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
11. **Thumbnail Generator** — template card (hook text + brand palette); overwrites frame-extracted thumb when successful
12. **Distribution Writer** — pack and upload (e.g. R2)

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
| Distribution manifest | title, description, tags, video_provenance_path, batch_id, format, topic, persona; telemetry: hook_type, environment, motion_type, music_mood, caption_pattern, style_version, primary_asset_ids |

**Provenance policy:** Every rendered video records render_manifest_id and script_segments_id; QC summary and per-asset prompt reference are stored.

---

## 3. Config references

| Config | Path | Purpose |
|--------|------|---------|
| Pacing | `config/video/pacing_by_content_type.yaml` | min/max duration per content_type; hook_timing |
| Captions | `config/video/caption_policies.yaml` | max_chars_per_line, max_lines, strategy, hook_caption_max_words; **min_contrast_ratio** (≥ 4.5 for accessibility) |
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
| Thumbnail templates | `config/video/thumbnail_templates.yaml` | formats (resolution, thumb_filename), validation, typography; dimensions align with platform_seo_policies per platform |
| Thumbnail hook phrases | `config/video/thumbnail_hook_phrases.yaml` | topic_to_hook_phrase (2–4 word hook per topic) |
| Channel thumbnail styles | `config/video/channel_thumbnail_styles.yaml` | Per-channel thumbnail palette (bg, text, accent) for anti-spam visual diversity |
| Channel writing styles | `config/video/channel_writing_styles.yaml` | Per-channel voice, tone, CTA, emoji use, sentence style, hashtag pool |
| Platform SEO policies | `config/video/platform_seo_policies.yaml` | Per-platform title/description/hashtag rules (YouTube, TikTok, IG, YT Shorts) |
| Channel thumbnail styles | `config/video/channel_thumbnail_styles.yaml` | per-channel palette (bg_hex, text_hex, accent_hex) for anti-spam; fallback palette from brand_style_tokens bands.hook |

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

## 10. Thumbnail Generator

Single implementation: one script, one set of configs (templates, hook phrases, channel styles, brand default). No duplicate thumbnail generators in the pipeline.

**Script:** `scripts/video/generate_thumbnail.py`
**Config:** `config/video/thumbnail_templates.yaml` (formats, validation, typography), `config/video/thumbnail_hook_phrases.yaml` (topic_to_hook_phrase), `config/video/channel_thumbnail_styles.yaml` (per-channel palette when channel_id present; §15 anti-spam), `config/video/brand_style_tokens.yaml` (default palette from `bands.hook.spec`).

**Purpose:** Produce a designed template card (bold hook text + brand palette) for each video, replacing the renderer's FFmpeg frame-extract with a more scroll-stopping thumbnail.

**Inputs:** `distribution_manifest.json` (title, format, topic), optional topic/persona from metadata args.
**Output:** One thumbnail per plan in `artifacts/video/<plan_id>/`: either format-specific (`thumb_16x9.jpg` for long, `thumb_9x16.jpg` for shorts) or a single `thumb.jpg` at the correct aspect (1280×720 long, 1080×1920 shorts). Thumb is optional at handoff; Distribution Writer uses whatever thumb file exists.

**Deterministic fallback rule (precedence):**
1. **Generated thumb** (template card from this stage) — preferred when run and passes validation.
2. **Frame-extracted thumb** (renderer's FFmpeg grab at `thumbnail_frame_ref`) — used when generator is not run or fails validation.
3. **No thumb** — Distribution Writer proceeds without thumbnail; partner handles missing thumb.

Fallback is logged in `artifacts/video/<plan_id>/thumb_provenance.json` with `source` (`generated` | `frame_extracted` | `none`) and `reason` if fallback occurred.

**Thumbnail validation (quality gate):**
Before accepting a generated thumbnail, `_validate_thumbnail()` checks:
- Resolution matches target format (1280×720 or 1080×1920 ±1px)
- Text contrast: luminance ratio between text color and background ≥ 3.0
- Hook text length: 2–6 words (target 2–4; hard cap 6)

If validation fails, auto-fallback to frame-extracted thumb and record failure reason in `thumb_provenance.json`.

**Design formula (self-help):**
- 2–4 word hook text derived from topic → hook phrase map (config) or truncated title
- Per-channel palette from `channel_thumbnail_styles.yaml` (unique bg + text + accent per channel for anti-spam); falls back to `brand_style_tokens.yaml → bands.hook.spec` when no channel_id
- Bold sans-serif text (Bebas Neue / Montserrat Bold or system fallback)
- Optional symbol from topic → symbol map (brain, spiral, breath icon)
- No faces; type-only or type + icon

**Metadata extension:** `write_metadata.py` accepts `--topic` and `--persona` args. These propagate into `distribution_manifest.json` and are consumed by the thumbnail generator for hook phrase selection and template variant.

---

## 11. Distribution handoff

- **Target:** Cloudflare R2 bucket (`pearl-video-handoff` or per-environment name).
- **Script:** `scripts/video/distribution_writer.py` (Stage 10).
- **Config:** `config/video/distribution_r2.yaml` (non-secret fields); secrets via env (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET_NAME`).

**Flow:**
1. Distribution Writer scans `artifacts/video/<plan_id>/` for completed renders (video.mp4 + distribution_manifest.json).
2. Classifies each as long-form or shorts by format field.
3. Stages locally to `staging/<date>/{long|shorts}/<video_id>/`.
4. Uploads to R2 at `<date>/{long|shorts}/<video_id>/{video.mp4, thumb.jpg, distribution_manifest.json}` with per-file retry (3 attempts, exponential backoff). Thumb selection is format-aware: Distribution Writer picks `thumb_16x9.jpg` for long-form, `thumb_9x16.jpg` for shorts, falling back to legacy `thumb.jpg` if format-specific files don't exist. Uploaded as `thumb.jpg` in R2 (canonical name at handoff).
5. Tracks progress in `staging/<date>/upload_progress.json` (resume-safe on restart).
6. Writes `daily_batch.json` (locally and to R2 at `<date>/daily_batch.json`) ONLY after all uploads succeed. Schema: `schemas/video/daily_batch_v1.schema.json`.

**Partner handoff contract:**
- Partner reads ONLY `<date>/daily_batch.json` from R2 — no bucket scan/list.
- Partner follows `r2_prefix` and `distribution_manifest_key` paths for each video.
- After ingest to Metricool, partner writes `<date>/batch_acknowledged.json` to R2 (schema: `schemas/video/batch_acknowledged_v1.schema.json`).
- `batch_acknowledged.json` MUST include `failed_count` (0 = all succeeded) and optionally `failed_ids`.

**Wipe gate:** `scripts/video/wipe_staging_after_ack.py` deletes `staging/<date>/` (and optionally R2 prefix) ONLY when `batch_acknowledged.json` exists AND `failed_count == 0`. Hard rule: no ack → no wipe. See storage layout doc for directory structure.

**Telemetry fields (A/B and performance):** The distribution manifest and the provenance record both include the same visual/audio telemetry so you can correlate platform metrics with pipeline decisions: **hook_type**, **environment**, **motion_type**, **music_mood**, **caption_pattern**, **style_version**. Also include **primary_asset_ids** (or primary_environment_asset_ids) per video for cross-video dedup and usage analysis. Duplication in both artifacts is intentional: distribution for partner and performance joins; provenance for debugging and replay.

**R2 credentials setup:**
1. Create a Cloudflare R2 bucket (e.g. `pearl-video-handoff`).
2. Create an R2 API token with Object Read & Write on that bucket.
3. Set env vars: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`.
4. Non-secret fields (account_id, bucket_name, endpoint) can also go in `config/video/distribution_r2.yaml`.

**R2 upload throughput:** For large daily batches, use **multipart upload** and **parallelism** (e.g. 16–32 concurrent uploads, chunk size 16 MB). Target: daily batch upload completes in **2–3 hours** max. Config or env may specify `parallel_uploads`, `chunk_size_mb`, `target_upload_window_hours`. See `scripts/video/distribution_writer.py` and `config/video/distribution_r2.yaml` for overrides.

**Partner runbook:** [docs/PARTNER_VIDEO_PICKUP_RUNBOOK.md](./PARTNER_VIDEO_PICKUP_RUNBOOK.md) — 1-page runbook for partner: download daily_batch, pull from R2, upload to Metricool, write batch_acknowledged; error/retry/contact.

---

## 11. Renderer parameters (no separate mutation stage)

Motion, caption placement, and pacing already come from the pipeline (timeline, caption adapter, TTS). **Do not add a scene_mutation or mutation_engine stage.** The following are **render-time parameters** consumed by `run_render.py` (FFmpeg).

**Crop offset variation:** Same image can be rendered with a slight crop/zoom for variety. Per clip, the renderer may set `crop_zoom` (e.g. 0.92–1.0), `crop_offset_x`, `crop_offset_y` — **deterministic** from `hash(video_id + shot_index)` so builds are reproducible. Implement as crop/zoompan parameters in the FFmpeg filter chain, not a new pipeline artifact.

**Per-video color grading:** One color grade per video (not per-shot) for coherence. Use `config/video/color_grade_presets.yaml` (neutral, warm, cool, sunset, soft); select preset by emotional arc or content_type. Apply as FFmpeg `eq=contrast=...:brightness=...:saturation=...` (or colorbalance/curves) on the final output.

**Encoding:** Use `-preset veryfast -crf 23` as the default. Do not use `-preset ultrafast` for production therapeutic content — text and caption edges show compression artifacts. Benchmark before lowering quality for throughput.

**Thumbnail:** The renderer produces `thumb.jpg` (frame extraction at `thumbnail_frame_ref`). The optional Thumbnail Generator stage (after Metadata Writer) may produce format-specific template cards (`thumb_16x9.jpg` / `thumb_9x16.jpg`); Distribution Writer uses generated thumb when present, else frame-extract, else no thumb. See §10.

See `docs/VIDEO_PIPELINE_FFMPEG_REFERENCE.md` for zoompan, eq, and drawtext/drawbox filter reference.

---

## 12. QC gates

- Pre-render: ShotPlan and Timeline validation (including **Visual Stillness Ratio** for therapeutic/long_form: fraction of clips with motion=static must be ≥ `config/video/motion_policy.yaml` → `min_static_ratio`, default 0.70).
- Post-render: duration, resolution, caption presence; safety checks as defined by governance.

### 12.1 Rendered spot-check (safety)

Sample **1–2% of daily rendered videos** (e.g. by final frame or key frames) and run the same safety classifier used at image-bank ingest (NSFW, violence, symbol detection) on the **composite** (image + caption). Catches unintended meaning from image+caption combination. This runs in **post-render QC** or a dedicated spot-check job; failures are logged and escalated. Implement when safety tooling is wired; spec defines the requirement and where it runs.

---

## 12.2 Accessibility

- **Caption contrast:** Caption text vs background must meet **contrast ratio ≥ 4.5** (WCAG 2.1). Config: `config/video/caption_policies.yaml` → `min_contrast_ratio: 4.5`. Renderer applies semi-transparent caption bar and/or text outline/shadow to satisfy this.
- **Caption safe zone:** Lower 30% of frame reserved for captions; composition prompts and assets support caption_safe_zone.

---

## 13. Localization

- CaptionAdapter and metadata support multi-locale (e.g. en, ja); caption_policies has by_language rules.

---

## 14. Operational notes

- **Scale target:** Thousands of therapeutic videos daily (e.g. 100 long-form, 5,000 shorts).
- **Video uniqueness:** **Sequence signature (lock):** `sequence_signature = hash( variant_id + ordered_concat( [ shot.visual_intent, shot.environment, shot.motion_type, shot.hook_type ] for each shot ) )`. Include variant_id so male_realistic and female_illustration of the same script do not collide. Use for duplicate detection and replay. **Cross-video dedup** + bank variety. **Cross-video dedup constraint:** Within a daily batch, no two videos scheduled in the same publishing window (e.g. same 2-hour slot on a given platform) may share more than one primary environment asset. The daily_batch index (or distribution manifests) should include primary asset_ids per video so the partner or scheduler can enforce this before publish. Rule and window: `config/video/cross_video_dedup.yaml`. This prevents “same forest path three times in a row” in a viewer’s feed.
- **Style version at batch boundary:** Style version is **fixed for the entire daily batch**. Do not switch style_version mid-day: the next full daily batch uses the new version so the partner never receives a batch mixing v1 and v2 assets. Pipeline default is set per batch, not per video.
- **A/B testing:** Outbound telemetry (hook_type, environment, motion_type, music_mood, caption_pattern, style_version in manifest and provenance) + **inbound performance feedback**. Schema: `schemas/video/video_performance_v1.schema.json` (video_id, platform, impressions, views, watch_time_median_s, completion_rate, engagement_rate, date_range, etc.). **Ingestion:** A separate process (e.g. analytics job or Metricool export) pulls from platform APIs (YouTube, TikTok, etc.) on a schedule, normalizes to video_performance_v1, and writes to the analytics store or artifact location. Document owner and frequency in runbook; spec defines the schema and that the return path exists so outbound telemetry can be joined to performance.
- **Persistent storage:** Image Bank and artifacts separate from ephemeral R2 handoff.
- **Image bank size (per channel/brand):** Pre-rendered single-image bank only (no compositing). Launch target **~400 images per brand** (360–405); **hook bank 35–40** (hooks are highest-frequency). Breakdown: 15 topics × ~24–27 images per topic. Run the coverage study (sample scripts → shot planner → unique combinations) for exact breakdown. Generation priority: environments first, then symbolic visuals, then character scenes. Grow when preflight or reuse cap surfaces gaps.
- **24-channel total image target:** 24 brands × ~400 images = **~9,600 images total** (range: 8,640–9,720). See §17 for multi-channel architecture and spam avoidance rules.

---

## 15. Multi-channel architecture and platform spam avoidance

### 15.1 Architecture

The pipeline supports **24 channels (brands)**, each with its own isolated image bank, style identity, and assembly configuration. No two channels share an image bank. This is the primary defense against platform spam detection.

| Layer | Per-channel isolation | Why it matters |
|---|---|---|
| **Image bank** | Separate bank per channel; visually distinct styles | Breaks visual fingerprint linking channels as a farm |
| **Thumbnails** | Unique palette (bg + text + accent) per channel (config: `channel_thumbnail_styles.yaml`) | Thumbnail is the most visible fingerprint in feeds and search |
| **Assembly method** | Different pacing (image interval 3–5s varies by brand), transition style, motion type, aspect ratio composition | Different sequence signatures even for same topic |
| **TTS voice** | Different voice ID per channel (config: `config/video/channel_registry.yaml → tts_voice_id`) | Audio fingerprint must differ between channels |
| **Writing voice** | 24 distinct copywriting styles (tone, CTA, sentence style, emoji use) (config: `channel_writing_styles.yaml`) | Description text pattern matching is a primary spam signal |
| **Metadata templates** | Different title formats, description structures, tag sets per channel | Metadata fingerprint must differ |
| **Platform SEO** | Per-platform rules (title length, hashtag count, description structure) (config: `platform_seo_policies.yaml`) | Each platform has unique algorithm; one-size-fits-all metadata underperforms |
| **Upload timing** | Staggered — no two channels upload in the same 2-hour window on the same platform | Upload pattern must look independent |
| **Background music** | Different music mood assignment per channel (config: `config/video/music_policy.yaml → channel_overrides`) | Same mood but different track pool per channel |

### 15.2 Image bank style differentiation

Each of the 24 channels gets a distinct visual style. Style must be **visually distinct at a glance** — not just palette-shifted versions of the same style. Examples:

| Channel group | Style family | Notes |
|---|---|---|
| 1–4 | Warm illustration (hand-drawn feel) | Soft lines, muted earth tones |
| 5–8 | Atmospheric photography (real-world) | Low-light, bokeh, natural environments |
| 9–12 | Minimal geometric / abstract | Clean shapes, high negative space |
| 13–16 | Watercolor + texture | Painterly, loose, organic |
| 17–20 | Cinematic / film-grain | Cooler tones, dramatic light |
| 21–24 | Botanical / nature macro | Close-up natural world; no faces |

Style definition lives in `config/video/channel_registry.yaml` under `image_style_family`. The image generation prompt prefix for each channel comes from `config/video/brand_style_tokens.yaml` keyed by `channel_id`.

### 15.3 Image bank sizing (per channel)

**Target: ~400 images per channel.** Minimum viable: 360; scale up to 450 when topic gap analysis shows reuse cap exceeded.

Coverage formula:
```
15 topics × 24 images per topic = 360 images base
+ hook bank: 35–40 images (shared within channel; never shared across channels)
= ~395–400 images per channel
```

Topic breakdown within each channel (all in the channel's visual style):
- Environments / scene-setting: ~8 images per topic
- Symbolic / metaphoric: ~8 images per topic
- Character / human presence (no faces): ~8 images per topic

### 15.4 Assembly method differentiation

Each channel should differ on at least 3 of these 5 assembly dimensions. Config: `config/video/channel_registry.yaml → assembly_profile`.

| Dimension | Example variation |
|---|---|
| Image hold duration | 3.0s vs 3.5s vs 4.0s vs 5.0s |
| Transition type | cut / crossfade / dip-to-black / zoom-dissolve |
| Caption style | lower-third / full-overlay / word-by-word / none |
| Aspect ratio emphasis | 9:16-first vs 16:9-first vs 1:1-first |
| Hook type pool | topic-specific hooks; each channel draws from different hook subset |

### 15.5 Platform spam avoidance rules (YouTube / Instagram / TikTok)

These rules are non-negotiable and must be enforced by the pipeline. Violations risk channel termination across the entire network.

**What YouTube/IG/TikTok detect:**
- Identical visual sequences across channels (visual fingerprint matching)
- Same audio track or TTS voice across channels (audio fingerprint)
- Same metadata structure repeated at scale (metadata pattern matching)
- Coordinated upload bursts from the same IP or account cluster

**Hard rules (config-enforced, CI-gated):**

1. **No shared image assets across channels.** `cross_channel_asset_share_ratio` = 0.0 (config: `config/video/cross_video_dedup.yaml → cross_channel`). A single image used in two different channels' banks is a violation.

2. **No two channels upload within the same 2-hour window on the same platform.** Scheduler must enforce. Config: `config/video/channel_registry.yaml → upload_window_offset_hours` (0–23, unique per channel).

3. **TTS voice must differ between all 24 channels.** Each channel gets one assigned voice ID. Voice ID is locked in `channel_registry.yaml → tts_voice_id`. No two entries may share a voice ID.

4. **Metadata template diversity.** Title format strings must differ: at least 6 distinct title templates across 24 channels (4 channels share a template maximum). Config: `config/video/channel_registry.yaml → title_template_id`.

5. **Sequence signature diversity within a channel.** Existing cross-video dedup rule (§14) applies within each channel. No two videos on the same channel share more than one primary environment asset in the same publishing window.

6. **Upload rate cap.** Max 3 uploads per channel per day at launch. Scale after 90 days of clean channel health. Config: `config/video/channel_registry.yaml → daily_upload_cap`.

7. **Thumbnail visual fingerprint diversity.** Each channel MUST use a unique thumbnail palette (bg, text, accent color triple). No two channels share the same palette. Config: `config/video/channel_thumbnail_styles.yaml`. The thumbnail generator (`generate_thumbnail.py`) resolves `--channel-id` → per-channel palette, overriding the shared hook band. This prevents platform detection of identical thumbnail visual patterns across channels.

8. **Writing voice diversity.** Each channel has a unique copywriting voice (tone, sentence style, emoji usage, CTA style, signature phrase). Config: `config/video/channel_writing_styles.yaml`. The metadata writer (`write_metadata.py`) loads the channel style via `--channel-id` and includes it in the distribution manifest's `platform_seo` section. Metricool or the publishing layer uses this to generate platform-native descriptions. No two channels may produce descriptions that follow the same structural pattern.

9. **Platform-specific SEO compliance.** Each platform has distinct metadata rules (title length, description structure, hashtag count/placement). Config: `config/video/platform_seo_policies.yaml`. The metadata writer loads platform policy via `--platform` flag and validates title/description lengths, selects hashtags from the channel's pool respecting platform max count, and flags violations. Supported platforms: `youtube`, `tiktok`, `instagram_reels`, `youtube_shorts`.

### 15.6 Anti-spam fingerprint isolation summary

| Fingerprint layer | Isolation mechanism | Config |
|---|---|---|
| Visual (video) | Isolated image bank per channel; distinct style families | `channel_registry.yaml → image_bank_path, style_id` |
| Visual (thumbnail) | Unique palette per channel (bg + text + accent) | `channel_thumbnail_styles.yaml` |
| Audio (TTS) | Unique voice ID per channel | `channel_registry.yaml → tts_voice_id` |
| Audio (music) | Different mood/track pool per channel | `music_policy.yaml → channel_overrides` |
| Metadata (title) | 6 distinct title templates, max 4 channels each | `channel_registry.yaml → title_template_id` |
| Metadata (description) | 24 unique writing voices (tone, CTA, emoji, sentence style) | `channel_writing_styles.yaml` |
| Metadata (hashtags) | Per-channel hashtag pool, platform count limits | `channel_writing_styles.yaml → hashtag_pool`, `platform_seo_policies.yaml` |
| Timing (upload) | Staggered upload windows (unique hour per channel) | `channel_registry.yaml → upload_window_offset_hours` |
| Sequence (dedup) | Cross-video primary asset cap within publishing window | `cross_video_dedup.yaml` |

### 15.7 channel_registry.yaml structure

New config file: `config/video/channel_registry.yaml`. Each channel entry:

```yaml
channels:
  ch_001:
    brand_id: phoenix_protocol
    channel_platform: youtube
    image_style_family: warm_illustration
    assembly_profile: profile_a   # refs config/video/assembly_profiles.yaml
    tts_voice_id: en-US-Journey-F  # unique across all 24 channels
    title_template_id: tmpl_01
    upload_window_offset_hours: 0  # unique; no two channels share same hour
    daily_upload_cap: 3
    image_bank_path: assets/image_banks/ch_001/
  ch_002:
    ...
```

---

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
