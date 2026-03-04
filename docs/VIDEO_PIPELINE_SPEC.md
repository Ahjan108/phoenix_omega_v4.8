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
| Image bank asset | asset_id, layer_type, tags, composition_compat, generation_batch, style_version |
| Timeline | fps, resolution, aspect_ratio, audio_tracks[], thumbnail_frame_ref, clips[] |
| Video provenance | video_id, plan_id, content_type, duration_s, render_manifest_id, script_segments_id, qc_summary, format_adaptations |
| Distribution manifest | title, description, tags, video_provenance_path, batch_id |

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

---

## 4. Shot Planner

- **Input:** Script segments (with segment_id, text, slot_id, primary_atom_id, atom_refs) and content metadata (persona, topic, location, emotion, arc_role).
- **Output:** ShotPlan (one visual story per plan).
- **Rules:** Visual intent defaults + emotion/arc overrides; motion policy (static majority); pacing from pacing_by_content_type; hook rules from hook_selection_rules.

---

## 5. Asset Resolver

- **Strategy:** Retrieval-first from Image Bank; generate only when no suitable asset exists.
- **Input:** ShotPlan, Image Bank index (asset_id, layer_type, tags, composition_compat, style_version).
- **Output:** Resolved asset references per shot (asset_id or prompt_bundle for generation).

---

## 6. FormatAdapter and aspect ratio

- One ShotPlan → FormatAdapter → per-format timelines (no cropping; generate or select assets at target aspect).
- Presets: `config/video/aspect_ratio_presets.yaml`.

---

## 7. CaptionAdapter

- Consumes caption_policies (max_chars_per_line, max_lines, strategy, hook_caption_max_words).
- Produces format- and language-specific caption content (reflow/truncate per policy).

---

## 8. Motion and style

- **Visual stillness ratio:** 70–80% static shots for therapeutic content (motion_policy.yaml).
- **Style system:** Warm Illustration (primary), Atmospheric Abstract (secondary), Macro Nature (subcategory); unified palette; no brand-name references in prompts.
- **Character consistency:** Sprite-sheet approach (pre-rendered pose/emotion sets per character_id); faces discouraged by default.

---

## 9. Degraded render policy

- Fallbacks when assets are missing; strict placement constraints (no degraded in first two shots or hook window).
- Config: `config/video/degraded_render_policy.yaml`.

---

## 10. Distribution handoff

- **Target:** Cloudflare R2 (or equivalent); batch packs for shorts; manifests; ack-before-wipe.
- **Artifacts:** distribution_manifest (title, description, tags, video_provenance_path, batch_id); daily_batch index; batch_acknowledged for partner confirmation.

---

## 11. QC gates

- Pre-render: ShotPlan and Timeline validation.
- Post-render: duration, resolution, caption presence; safety checks as defined by governance.

---

## 12. Localization

- CaptionAdapter and metadata support multi-locale (e.g. en, ja); caption_policies has by_language rules.

---

## 13. Operational notes

- **Scale target:** Thousands of therapeutic videos daily (e.g. 100 long-form, 5,000 shorts).
- **Video uniqueness:** Sequence hash + cross-video dedup + bank variety to avoid duplicate content.
- **A/B testing:** Outbound telemetry + inbound performance feedback schema (video_performance_v1).
- **Persistent storage:** Image Bank and artifacts separate from ephemeral R2 handoff.

---

## 14. References

- Render manifest schema: `../schemas/video/render_manifest_v1.schema.json`
- Video config: `../config/video/`
- Golden fixtures: `../fixtures/video_pipeline/` (render_manifest, script_segments, shot_plan, timeline, distribution_manifest, video_provenance)
