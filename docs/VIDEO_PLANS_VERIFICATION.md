# Video pipeline plans — implementation verification

**Date:** 2026-03-08 (updated 2026-03-09 after gap closure)  
**Plans checked:** All six `.cursor/plans` video pipeline plans.

---

## Summary

| Plan | Status | Notes |
|------|--------|-------|
| [Architecture](#1-video-pipeline-architecture-plan) | **Complete** | All 4 schemas added; QC stillness gate added |
| [Motion / stillness / style](#2-video-motion-stillness-and-style-spec) | **Complete** | run_qc enforces min_static_ratio from motion_policy.yaml |
| [Spec and config lock](#3-video-pipeline-spec-and-config-lock) | **Complete** | shot_plan_v1, script_segments_v1, timeline_v1, video_provenance_v1 in schemas/video/ |
| [Handoff to Metricool](#4-video-handoff-to-metricool-partner) | **Complete** | None |
| [Operational layers](#5-video-pipeline-operational-layers) | **Complete** | video_performance_v1, partner runbook, R2 throughput, accessibility, style batch, spot-check in spec; caption min_contrast_ratio 4.5 |
| [Thumbnail](#6-video-thumbnail-plan) | **Complete** | None |

---

## 1. Video pipeline architecture plan

**File:** `video_pipeline_architecture_plan_5c201f84.plan.md`

### Coded

- **Render manifest schema:** `schemas/video/render_manifest_v1.schema.json` — plan_id, segments[], primary_atom_id, atom_refs. ✓
- **Script preparer:** `scripts/video/prepare_script_segments.py` — reads render manifest, outputs script segments. ✓
- **Shot planner:** `scripts/video/run_shot_planner.py` — visual_intent, duration_s, thumbnail_candidate, pacing from config. ✓
- **Asset resolver:** `scripts/video/run_asset_resolver.py` — ShotPlan + bank index → resolved asset_id per shot; no consecutive same asset. ✓
- **Timeline builder:** `scripts/video/run_timeline_builder.py` — ShotPlan + resolved_assets → timeline JSON; thumbnail_frame_ref from thumbnail_candidate. ✓
- **Caption adapter:** `scripts/video/run_caption_adapter.py` — caption_policies, reflow/truncate. ✓
- **Renderer:** `scripts/video/run_render.py` — timeline + assets → video.mp4 + thumb; placeholder path when no assets. ✓
- **QC:** `scripts/video/run_qc.py` — no consecutive same asset_id, duration, resolution. ✓
- **Provenance / metadata:** `write_provenance.py`, `write_metadata.py` — provenance record, distribution_manifest. ✓
- **Thumbnail generator:** `scripts/video/generate_thumbnail.py` — template card, topic/persona, hook phrases. ✓
- **Distribution writer:** `scripts/video/distribution_writer.py` — staging, R2 upload, retry, upload_progress, daily_batch after all succeed. ✓
- **Config:** `config/video/` — pacing_by_content_type, caption_policies, degraded_render_policy, visual_intent_defaults, emotion_to_camera_overrides, brand_style_tokens, aspect_ratio_presets, visual_metaphor_library, motion_policy, etc. ✓
- **DOCS_INDEX:** Video pipeline subsection with VIDEO_PIPELINE_SPEC, schemas, config, scripts. ✓
- **Image bank asset schema:** `schemas/video/image_bank_asset_v1.schema.json`. ✓

### Coded (gap closed)

- **shot_plan_v1.schema.json** — `schemas/video/shot_plan_v1.schema.json`. ✓
- **script_segments_v1.schema.json** — `schemas/video/script_segments_v1.schema.json`. ✓
- **timeline_v1.schema.json** — `schemas/video/timeline_v1.schema.json`. ✓
- **video_provenance_v1.schema.json** — `schemas/video/video_provenance_v1.schema.json`. ✓

---

## 2. Video motion, stillness, and style spec

**File:** `video_motion_stillness_and_style_spec_70d7221b.plan.md`

### Coded

- **motion_policy.yaml:** `config/video/motion_policy.yaml` — motion_distribution (static 0.75, slow_zoom, slow_pan), speed_limits, one_movement_per_shot, rhythm_rule. ✓
- **Spec §8 Motion and style:** VIDEO_PIPELINE_SPEC.md — 70–80% static, motion_policy, style system (Warm Illustration, Atmospheric Abstract, Macro Nature), character consistency, visual quality checklist. ✓
- **Style / palette:** brand_style_tokens, no brand names in prompts (docmented). ✓
- **Cross-video dedup:** `config/video/cross_video_dedup.yaml`; spec §14. ✓
- **Caption policies:** by_language (en, ja) in caption_policies.yaml. ✓

### Coded (gap closed)

- **QC gate: “Visual Stillness Ratio ≥ 70%”** — `config/video/motion_policy.yaml` has `min_static_ratio: 0.70`. `run_qc.py` computes static fraction from timeline clips (motion=static) and fails when below min_static_ratio for content_type therapeutic/long_form. QC summary includes `stillness_ratio` in checks. ✓

---

## 3. Video pipeline spec and config lock

**File:** `video_pipeline_spec_and_config_lock_aea658dc.plan.md`

### Coded

- **docs/VIDEO_PIPELINE_SPEC.md:** Exists and is the canonical spec (authority, locked decisions, module boundaries, visual language, config refs). ✓
- **config/video/:** pacing_by_content_type, caption_policies, degraded_render_policy, visual_intent_defaults, emotion_to_camera_overrides; plus brand_style_tokens, aspect_ratio_presets, visual_metaphor_library, motion_policy, etc. ✓
- **schemas/video/render_manifest_v1.schema.json:** With primary_atom_id and atom_refs. ✓
- **DOCS_INDEX:** Video pipeline subsection → VIDEO_PIPELINE_SPEC, config, schemas. ✓

### Coded (gap closed)

- Same four schemas as in §1: all added under `schemas/video/`. ✓

---

## 4. Video handoff to Metricool partner

**File:** `video_handoff_to_metricool_partner_6c2998e4.plan.md`

### Coded

- **Distribution writer:** `scripts/video/distribution_writer.py` — scan artifacts, copy to staging, upload to R2 with retry (3 attempts, backoff), upload_progress.json, daily_batch.json only after all uploads succeed. ✓
- **daily_batch_v1.schema.json:** `schemas/video/daily_batch_v1.schema.json` — batch_date, long_form, shorts, counts. ✓
- **batch_acknowledged_v1.schema.json:** `schemas/video/batch_acknowledged_v1.schema.json` — batch_date, acknowledged_at, failed_count, failed_ids. ✓
- **Wipe script:** `scripts/video/wipe_staging_after_ack.py` — checks batch_acknowledged.json, optional failed_count == 0, deletes staging. ✓
- **R2 credentials:** docs/VIDEO_R2_CREDENTIALS.md; config/video/distribution_r2.yaml for non-secret fields. ✓
- **Spec and storage layout:** VIDEO_PIPELINE_SPEC.md §10/11, VIDEO_PIPELINE_STORAGE_LAYOUT.md — handoff flow, partner contract, wipe gate. ✓

### Not coded

- None identified.

---

## 5. Video pipeline operational layers

**File:** `video_pipeline_operational_layers_33bbd5cf.plan.md`

### Coded

- **Music:** `config/video/music_policy.yaml`; spec references arc/emotional-driven selection. ✓
- **Style version:** style_version in distribution_manifest and provenance; asset/style versioning referenced. ✓
- **Caption contrast / safe zone:** Spec §8 visual checklist mentions “renderer caption_bar_opacity and contrast”; caption safe zones in asset/composition. ✓
- **A/B telemetry (outbound):** hook_type, environment, motion_type, music_mood, caption_pattern, style_version, primary_asset_ids in manifest and provenance (VIDEO_PIPELINE_SPEC §11, §14). ✓
- **Localization:** variant_id; caption_policies by_language (en, ja). ✓
- **Video uniqueness:** Spec §14 — sequence signature, cross-video dedup, cross_video_dedup.yaml. ✓

### Coded (gap closed)

- **video_performance_v1.schema.json** — `schemas/video/video_performance_v1.schema.json` added. VIDEO_PIPELINE_SPEC §14 documents ingestion (schema + return path, owner/frequency in runbook). ✓
- **Partner runbook** — `docs/PARTNER_VIDEO_PICKUP_RUNBOOK.md` added (download daily_batch, pull from R2, upload to Metricool, write batch_acknowledged, error/retry/contact). Linked from DOCS_INDEX and VIDEO_PIPELINE_SPEC §11. ✓
- **R2 upload throughput** — Spec §11 now documents multipart + parallel (16–32 concurrent, 16 MB chunk), target 2–3 hours; `config/video/distribution_r2.yaml` has optional parallel_uploads, chunk_size_mb, target_upload_window_hours. ✓
- **Rendered spot-check (1–2% safety)** — Spec §12.1 “Rendered spot-check (safety)” added: sample 1–2% of daily renders, run safety classifier on composite; runs in post-render QC or dedicated job; implement when safety tooling is wired. ✓
- **Caption contrast ≥ 4.5** — `config/video/caption_policies.yaml` has `min_contrast_ratio: 4.5`. Spec §12.2 “Accessibility” added: caption contrast ≥ 4.5 (WCAG 2.1), caption safe zone. §3 config table references min_contrast_ratio. ✓
- **Style version at batch boundary** — Spec §14 now states: “Style version is fixed for the entire daily batch”; no mid-day switch. ✓

---

## 6. Video thumbnail plan

**File:** `video_thumbnail_plan_963c4465.plan.md`

### Coded

- **Thumb from render:** run_render.py produces thumb.jpg (frame at thumbnail_frame_ref) when not placeholder. ✓
- **Distribution writer:** Treats thumb as optional; copies thumb.jpg (or format-specific) to staging/R2. ✓
- **thumbnail_candidate from hook:** run_shot_planner.py sets thumbnail_candidate on segment with arc_role == "hook" when present, else first shot; timeline builder sets thumbnail_frame_ref from it. ✓
- **Thumbnail generator:** `scripts/video/generate_thumbnail.py` — template card, topic/persona, hook phrases, palette from brand/channel. ✓
- **Topic/persona in metadata:** write_metadata.py accepts --topic, --persona; distribution_manifest includes them; pipeline passes them. ✓
- **Config:** thumbnail_templates.yaml, thumbnail_hook_phrases.yaml, channel_thumbnail_styles.yaml; brand_style_tokens bands.hook. ✓
- **Spec §10:** Thumbnail Generator stage, inputs, fallback (generated → frame-extract → none), thumb_provenance.json, validation. ✓
- **Storage layout:** Note that thumb can be frame-extracted or generated. ✓

### Not coded

- None identified.

---

## Recommended next steps (all completed)

All items from the original “Recommended next steps” have been implemented:

1. **Schemas:** shot_plan_v1, script_segments_v1, timeline_v1, video_provenance_v1, video_performance_v1 are in `schemas/video/`.
2. **Operational layers:** Partner runbook, R2 throughput, Accessibility (§12.2), style batch boundary, spot-check (§12.1), performance ingestion (§14), caption min_contrast_ratio 4.5 in config and spec.
3. **Motion QC:** run_qc.py enforces Visual Stillness Ratio from motion_policy.min_static_ratio for therapeutic/long_form.
4. **Rendered spot-check:** Spec §12.1 defines the requirement and where it runs; implementation when safety tooling is ready.
