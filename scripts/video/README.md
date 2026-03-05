# Video pipeline scripts

Sequential stages per [docs/VIDEO_PIPELINE_SPEC.md](../../docs/VIDEO_PIPELINE_SPEC.md). Run against golden fixtures first.

**Idempotent:** Each stage skips if output already exists (and is valid). Use `--force` to overwrite. Outputs are written atomically (temp file then rename). **Config hash:** Shot plan, resolved assets, timeline, and captions include `config_hash` (hash of `config/video/*.yaml`) so you can see which config version produced each artifact.

**Storage:** Persistent artifacts go under `artifacts/video/`; ephemeral handoff (mp4s, daily_batch) goes under `staging/<date>/` and is wiped after partner ack. See [docs/VIDEO_PIPELINE_STORAGE_LAYOUT.md](../../docs/VIDEO_PIPELINE_STORAGE_LAYOUT.md).

## Order (implementation order)

1. **prepare_script_segments.py** — Render manifest → script_segments (timing via WPM; optional metadata).
2. **run_shot_planner.py** — Script segments → ShotPlan (visual_intent, duration_s, thumbnail_candidate, prompt_bundle).
3. **run_asset_resolver.py** — ShotPlan + optional Image Bank → resolved asset_id per shot.
4. **run_timeline_builder.py** — ShotPlan + resolved_assets → Timeline JSON (per aspect).
5. **run_caption_adapter.py** — Timeline + script_segments → captions (reflow/truncate per caption_policies).
6. **run_qc.py** — Validates shot_plan, resolved_assets, timeline (no consecutive same asset; duration/resolution).
7. **write_provenance.py** — Writes video_provenance.json (telemetry: hook_type, environment, etc.).
8. **write_metadata.py** — Writes distribution_manifest.json with telemetry and primary_asset_ids.
9. **run_render.py** — Timeline (plan_id, clips with asset_id, start_time_s, end_time_s, caption_ref) → video + thumb. Reads color presets from `config/video/color_grade_presets.yaml`, crop margin from `config/video/render_params.yaml`. Optional --shot-plan for motion per clip, --captions for caption text. Renders per-clip then concat (hard cuts); extracts thumbnail from thumbnail_frame_ref. **Audio:** timeline.audio_tracks (narration + music with duck_under) mixing is a follow-up; Phase 1 is video-only (silent).

## Run full pipeline

```bash
python3 scripts/video/run_pipeline.py --plan-id plan-therapeutic-001
```

Use `--force` to overwrite existing artifacts. Outputs under `artifacts/video/<plan_id>/` and `artifacts/video/provenance/` (persistent; never in wipe path).

## Run single stage

```bash
python3 scripts/video/prepare_script_segments.py fixtures/video_pipeline/render_manifest.json -o artifacts/video/plan-therapeutic-001/script_segments.json
python3 scripts/video/run_shot_planner.py artifacts/video/plan-therapeutic-001/script_segments.json -o artifacts/video/plan-therapeutic-001/shot_plan.json
# ... etc
```

Config is loaded from `config/video/*.yaml` (pacing, caption_policies, asset_selection_priority, aspect_ratio_presets, etc.).

## Render smoke test (one real image)

Create test assets matching the golden timeline fixture, then run the renderer:

```bash
python scripts/video/create_test_assets.py --dir /tmp/test_assets
python scripts/video/run_render.py fixtures/video_pipeline/timeline.json -o /tmp/test_render --assets-dir /tmp/test_assets --video-id test-001
```

Optional: pass `--captions` and `--shot-plan` (e.g. from a pipeline run) for caption text and motion. If the output is a valid MP4 with visible zoompan motion, drawbox, and captions, the renderer works. Benchmark per-clip time; then move to audio mixing.

**Finding ffmpeg:** Scripts use `_config.get_ffmpeg_bin()`: `FFMPEG` env (if set) → `which ffmpeg` → `/opt/homebrew/bin/ffmpeg` → `/usr/local/bin/ffmpeg` → `ffmpeg`. Set `FFMPEG=/path/to/ffmpeg` to override.
