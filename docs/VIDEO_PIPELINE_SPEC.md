# Video Pipeline Specification

**Purpose:** Single canonical spec for the metadata-driven visual storytelling engine.  
**Audience:** Engineers implementing or extending the pipeline.  
**Related:** [DOCS_INDEX.md](./DOCS_INDEX.md) § Video pipeline; `schemas/video/`, `config/video/`.

---

## 1. Pipeline stage order

1. **Script Generator** (content engine)
2. **Script Preparer** (content engine)
3. **Shot Planner** — consumes script segments + metadata → ShotPlan
4. **Asset Resolver** — ShotPlan + Image Bank → resolved assets (retrieval-first)
5. **Timeline Builder** — ShotPlan + assets → Timeline JSON (per aspect ratio via FormatAdapter)
6. **CaptionAdapter** — format/language-specific caption content
7. **Renderer** — Timeline + assets → video file(s)
8. **QC / Safety Gates**
9. **Provenance Writer** — audit trail
10. **Metadata Writer** — distribution manifest
11. **Distribution Writer** — pack and upload (e.g. R2)

---

## 2. Contracts and schemas

| Artifact | Schema / contract |
|----------|-------------------|
| Render manifest (input from content engine Stage 6) | `schemas/video/render_manifest_v1.schema.json` |
| Script segments (input to Shot Planner) | Contract: text, time range, metadata; segment_id, slot_id, primary_atom_id, atom_refs from render manifest |
| Shot plan | shot_id, visual_intent, aspect_ratio, thumbnail_candidate, prompt_bundle |
| Image bank asset | `schemas/video/image_bank_asset_v1.schema.json` — asset_id, layer_type, tags, composition_compat (per aspect), caption_safe_zone, safety_score, style_version, generation_batch |
| Timeline | fps, resolution, aspect_ratio, audio_tracks[], thumbnail_frame_ref, clips[] |
| Video provenance | video_id, plan_id, content_type, duration_s, render_manifest_id, script_segments_id, qc_summary, format_adaptations |
| Distribution manifest | title, description, tags, video_provenance_path, batch_id; telemetry: hook_type, environment, motion_type, music_mood, caption_pattern, style_version, primary_asset_ids |

**Provenance policy:** Every rendered video records render_manifest_id and script_segments_id; QC summary and per-asset prompt reference are stored.

---

## 3. Config references

| Config | Path | Purpose |
|--------|------|---------|
| Pacing | `config/video/pacing_by_content_type.yaml` | min/max duration per content_type; hook_timing |
| Captions | `config/video/caption_policies.yaml` | max_chars_per_line, max_lines, strategy, hook_caption_max_words |
| Degraded render | `config/video/degraded_render_policy.yaml` | allow_degraded, max count/ratio, placement constraints |
| Visual intent defaults | `config/video/visual_intent_defaults.yaml` | framing, face_visibility, camera_angle, motion per visual_intent |
| Emotion overrides | `config/video/emotion_to_camera_overrides.yaml` | emotional_band / arc_role → camera overrides |
| Motion | `config/video/motion_policy.yaml` | motion_distribution (70–80% static for therapeutic), speed limits |
| Hook selection | `config/video/hook_selection_rules.yaml` | topic/emotion → hook mapping; daily_batch_max_share_per_hook |
| Music | `config/video/music_policy.yaml` | arc/emotional_band → mood; segment-level override |
| Brand style | `config/video/brand_style_tokens.yaml` | palette per emotional_band |
| Aspect ratios | `config/video/aspect_ratio_presets.yaml` | presets for FormatAdapter |
| Visual metaphor library | `config/video/visual_metaphor_library.yaml` | human-reviewed metaphor cache |
| Cross-video dedup | `config/video/cross_video_dedup.yaml` | publishing window, max shared primary assets, require_primary_asset_ids_in_batch |
| Asset fallback priority | `config/video/asset_selection_priority.yaml` | deterministic fallback order; composition_compat_threshold; step 5 = degraded_render_fallback |
| Color grade presets | `config/video/color_grade_presets.yaml` | per-video eq presets (neutral, warm, cool, sunset, soft); one grade per video |
| Render params | `config/video/render_params.yaml` | crop_margin_pct (e.g. 6) — guardrail so seed-derived crop offsets don't clip subject |

---

## 4. Shot Planner

- **Input:** Script segments (with segment_id, text, slot_id, primary_atom_id, atom_refs) and content metadata (persona, topic, location, emotion, arc_role).
- **Output:** ShotPlan (one visual story per plan).
- **Rules:** Visual intent defaults + emotion/arc overrides; motion policy (static majority); pacing from pacing_by_content_type; hook rules from hook_selection_rules.

---

## 5. Asset Resolver

- **Strategy:** Retrieval-first from Image Bank; filter by metadata, rank by embedding similarity, then apply dedup. Generate only when no suitable asset exists.
- **Input:** ShotPlan, Image Bank index (asset_id, layer_type, tags, composition_compat, style_version).
- **Output:** Resolved asset references per shot (asset_id or prompt_bundle for generation).
- **Per-batch reuse cap:** No single asset may appear more than `max_asset_reuse_per_batch` times across the daily output (config: `config/video/cross_video_dedup.yaml`). When an asset hits the cap, it is unavailable for the rest of the batch; coverage gaps surface in the preflight report so you know which assets need more variants.

---

## 6. FormatAdapter and aspect ratio

**Scope:** FormatAdapter sits between ShotPlan + resolved assets and the Timeline Builder. It produces one timeline per target aspect ratio (16:9, 9:16, 1:1) from a single ShotPlan.

**Inputs:** ShotPlan, resolved assets per shot (asset_id from Asset Resolver), caption content per segment, target aspect ratio.

**Outputs:** Timeline JSON per format (layout, clip refs, caption placement, thumbnail_frame_ref). Same shot sequence and narrative; only layout and asset/caption choices may differ per format.

**What FormatAdapter may modify:**
- Caption safe zones and positioning per aspect ratio (e.g. lower third for 16:9, centered for 9:16).
- Caption content length per format (reflow or truncate per caption_policies; see §7).
- **Asset selection:** When the primary asset’s composition does not work for the target aspect (e.g. wide establishing shot unusable in 9:16), FormatAdapter may select an **alternate asset** from the Image Bank for that shot. It does not change the ShotPlan’s visual_intent or prompt_bundle; it only swaps the resolved asset when the primary fails the composition check.

**What FormatAdapter does not modify:**
- Shot count, order, or duration.
- Visual intent, arc_role, or segment boundaries.
- Prompt bundle or style; those stay from ShotPlan.

**Composition compatibility (composition_compat):** Each Image Bank asset carries a per-aspect **composition_compat** score (0–1). **Source (defined):** During bank generation, compute once per asset per aspect: **1.0** if the image was generated natively at that aspect ratio; **0.5** if it is croppable without losing the main subject; **0.0** if incompatible. Simple, automatable, no ML dependency. Schema: `schemas/video/image_bank_asset_v1.schema.json`. When composition_compat for the primary asset is below the threshold (see `config/video/asset_selection_priority.yaml`), FormatAdapter follows the **asset fallback priority** (see below) and only if all steps fail uses **degraded_render_fallback**.

**Asset substitution reason (provenance):** When FormatAdapter substitutes an asset, it records a reason from a closed enum: `COMPOSITION_INCOMPATIBLE`, `SUBJECT_CROPPED`, `CAPTION_OVERLAP`, `ASPECT_MISMATCH`. Provenance and QC use this enum (no freetext) for aggregation and debugging.

- One ShotPlan → FormatAdapter → per-format timelines (no cropping; generate or select assets at target aspect).
- Presets: `config/video/aspect_ratio_presets.yaml`.

**Asset fallback priority (deterministic):** When the primary asset fails composition_compat for the target aspect, FormatAdapter and Asset Resolver use this order (config: `config/video/asset_selection_priority.yaml`): (1) primary_asset, (2) alternate_same_environment, (3) alternate_same_visual_intent, (4) alternate_same_emotional_band, (5) **degraded_render_fallback**. Step 5 is not a bank lookup — it triggers the degraded render policy (e.g. branded background + caption). Do not select a random low-confidence asset; explicit fallback only.

---

## 7. CaptionAdapter

- Consumes caption_policies (max_chars_per_line, max_lines, strategy, hook_caption_max_words).
- Produces format- and language-specific caption content (reflow/truncate per policy).
- **Truncation rule:** When strategy is truncate (or reflow-then-truncate when space is insufficient), truncate at the **last complete clause boundary** that fits (sentence or clause end). If no clause boundary fits within the limit, truncate at the **last word boundary**. Any segment where the displayed caption is **truncated by more than 50%** of the original text must be **flagged for human review** (e.g. in QC or an audit log). This avoids cutting mid-thought and surfaces heavy truncation for therapeutic content. See `config/video/caption_policies.yaml` for the rule and flag threshold.

---

## 8. Motion and style

- **Visual stillness ratio:** 70–80% static shots for therapeutic content (motion_policy.yaml).
- **Style system:** Warm Illustration (primary), Atmospheric Abstract (secondary), Macro Nature (subcategory); unified palette; no brand-name references in prompts.
- **Character consistency:** Sprite-sheet approach (pre-rendered pose/emotion sets per character_id); faces discouraged by default.
- **Hook motion mapping:** Only use motion types the renderer supports. Light reveal / hands close-up / walking path → slow_zoom_in (walking path uses zoom-in for “forward” illusion). Ripple/breathing → slow_zoom_out. Do not add slow_expand or slow_pan_forward until the renderer implements them.

**Visual quality checklist (avoid “cheap” look):** (1) Low visual noise — subject_count ≤ 2, low background detail, negative space. (2) No direct faces by default — face_visibility partial_or_none; back of head, profile, silhouette, hands. (3) Slow motion only — per motion_policy speed limits; one motion per shot; no zoom+pan. (4) Lighting consistency — max_lighting_changes_per_video from style; image bank lighting families. (5) Caption-safe zones — assets with caption_safe_zone; renderer caption_bar_opacity and contrast. (6) Emotion–image alignment — use emotion_to_camera_overrides; no sunny beach for “overwhelmed.” QC and asset metadata should enforce these where applicable.

---

## 9. Degraded render policy

- Fallbacks when assets are missing; strict placement constraints (no degraded in first two shots or hook window).
- Config: `config/video/degraded_render_policy.yaml`.

---

## 10. Distribution handoff

- **Target:** Cloudflare R2 (or equivalent); batch packs for shorts; manifests; ack-before-wipe.
- **Artifacts:** distribution_manifest (title, description, tags, video_provenance_path, batch_id); daily_batch index; batch_acknowledged for partner confirmation.

**Telemetry fields (A/B and performance):** The distribution manifest and the provenance record both include the same visual/audio telemetry so you can correlate platform metrics with pipeline decisions: **hook_type**, **environment**, **motion_type**, **music_mood**, **caption_pattern**, **style_version**. Also include **primary_asset_ids** (or primary_environment_asset_ids) per video for cross-video dedup and usage analysis. Duplication in both artifacts is intentional: distribution for partner and performance joins; provenance for debugging and replay.

---

## 11. Renderer parameters (no separate mutation stage)

Motion, caption placement, and pacing already come from the pipeline (timeline, caption adapter, TTS). **Do not add a scene_mutation or mutation_engine stage.** The following are **render-time parameters** consumed by `run_render.py` (FFmpeg).

**Crop offset variation:** Same image can be rendered with a slight crop/zoom for variety. Per clip, the renderer may set `crop_zoom` (e.g. 0.92–1.0), `crop_offset_x`, `crop_offset_y` — **deterministic** from `hash(video_id + shot_index)` so builds are reproducible. Implement as crop/zoompan parameters in the FFmpeg filter chain, not a new pipeline artifact.

**Per-video color grading:** One color grade per video (not per-shot) for coherence. Use `config/video/color_grade_presets.yaml` (neutral, warm, cool, sunset, soft); select preset by emotional arc or content_type. Apply as FFmpeg `eq=contrast=...:brightness=...:saturation=...` (or colorbalance/curves) on the final output.

**Encoding:** Use `-preset veryfast -crf 23` as the default. Do not use `-preset ultrafast` for production therapeutic content — text and caption edges show compression artifacts. Benchmark before lowering quality for throughput.

See `docs/VIDEO_PIPELINE_FFMPEG_REFERENCE.md` for zoompan, eq, and drawtext/drawbox filter reference.

---

## 12. QC gates

- Pre-render: ShotPlan and Timeline validation.
- Post-render: duration, resolution, caption presence; safety checks as defined by governance.

---

## 13. Localization

- CaptionAdapter and metadata support multi-locale (e.g. en, ja); caption_policies has by_language rules.

---

## 14. Operational notes

- **Scale target:** Thousands of therapeutic videos daily (e.g. 100 long-form, 5,000 shorts).
- **Video uniqueness:** **Sequence signature (lock):** `sequence_signature = hash( variant_id + ordered_concat( [ shot.visual_intent, shot.environment, shot.motion_type, shot.hook_type ] for each shot ) )`. Include variant_id so male_realistic and female_illustration of the same script do not collide. Use for duplicate detection and replay. **Cross-video dedup** + bank variety. **Cross-video dedup constraint:** Within a daily batch, no two videos scheduled in the same publishing window (e.g. same 2-hour slot on a given platform) may share more than one primary environment asset. The daily_batch index (or distribution manifests) should include primary asset_ids per video so the partner or scheduler can enforce this before publish. Rule and window: `config/video/cross_video_dedup.yaml`. This prevents “same forest path three times in a row” in a viewer’s feed.
- **A/B testing:** Outbound telemetry (hook_type, environment, motion_type, music_mood, caption_pattern, style_version in manifest and provenance) + inbound performance feedback schema (video_performance_v1).
- **Persistent storage:** Image Bank and artifacts separate from ephemeral R2 handoff.
- **Image bank size (locked):** Pre-rendered single-image bank only (no compositing). Launch target **~400 images** (350–500); **hook bank 35–40** (hooks are highest-frequency). Run the coverage study (sample scripts → shot planner → unique combinations) for exact breakdown. Generation priority: environments first, then symbolic visuals, then character scenes. Grow when preflight or reuse cap surfaces gaps.

---

## 15. Implementation order

- **Build Script Preparer first.** It has the clearest input (render manifest fixture) and output (script segments fixture) and validates that the render manifest schema works with real data. If the preparer runs cleanly against the fixture, every downstream stage has a proven input contract. Do not start with Shot Planner on an untested input.
- **Phase 1: sequential scripts.** Implement the pipeline as sequential steps (script_preparer → shot_planner → asset_resolver → timeline_builder → renderer), each reading the previous stage’s output from disk. Get the logic right against the golden fixtures.
- **Scale later with job queues.** When throughput demands it, wrap each stage as a queue worker (planner_queue, asset_resolver_queue, format_adapter_queue, render_queue, qc_queue, upload_queue). Starting with queues makes debugging pipeline logic and infrastructure issues simultaneously much harder.

---

## 16. References

- Render manifest schema: `../schemas/video/render_manifest_v1.schema.json`
- Image bank asset schema: `../schemas/video/image_bank_asset_v1.schema.json`
- Video config: `../config/video/`
- Golden fixtures: `../fixtures/video_pipeline/` (render_manifest, script_segments, shot_plan, timeline, distribution_manifest, video_provenance, image_bank_asset_example)
- Pipeline scripts: `../scripts/video/` (prepare_script_segments, run_shot_planner, run_asset_resolver, run_timeline_builder, run_caption_adapter, run_qc, write_provenance, write_metadata, run_render, run_pipeline)
