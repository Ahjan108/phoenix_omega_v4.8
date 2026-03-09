# Video pipeline scripts

Sequential stages per [docs/VIDEO_PIPELINE_SPEC.md](../../docs/VIDEO_PIPELINE_SPEC.md). Run against golden fixtures first.

**Idempotent:** Each stage skips if output already exists (and is valid). Use `--force` to overwrite. Outputs are written atomically (temp file then rename). **Config hash:** Shot plan, resolved assets, timeline, and captions include `config_hash` (hash of `config/video/*.yaml`) so you can see which config version produced each artifact.

**Storage:** Persistent artifacts go under `artifacts/video/`; ephemeral handoff (mp4s, daily_batch) goes under `staging/<date>/` and is wiped after partner ack. See [docs/VIDEO_PIPELINE_STORAGE_LAYOUT.md](../../docs/VIDEO_PIPELINE_STORAGE_LAYOUT.md).

## Order (implementation order)

1. **prepare_script_segments.py** — Render manifest → script_segments (timing via WPM; optional metadata).
2. **run_shot_planner.py** — Script segments → ShotPlan (visual_intent, duration_s, thumbnail_candidate, prompt_bundle).
3. **run_asset_resolver.py** — ShotPlan + optional Image Bank → resolved asset_id per shot. To use FLUX-generated images: build the bank with `run_flux_bank_build.py`, then pass `--bank image_bank/index.json` and use `--assets-dir image_bank` in the render step. See [docs/VIDEO_AND_COVER_ART_FLUX_WIRING.md](../../docs/VIDEO_AND_COVER_ART_FLUX_WIRING.md).
4. **run_timeline_builder.py** — ShotPlan + resolved_assets → Timeline JSON (per aspect).
5. **run_caption_adapter.py** — Timeline + script_segments → captions (reflow/truncate per caption_policies).
6. **run_qc.py** — Validates shot_plan, resolved_assets, timeline (no consecutive same asset; duration/resolution).
7. **write_provenance.py** — Writes video_provenance.json (telemetry: hook_type, environment, etc.).
8. **write_metadata.py** — Writes distribution_manifest.json with telemetry and primary_asset_ids.
9. **run_render.py** — Timeline (plan_id, clips with asset_id, start_time_s, end_time_s, caption_ref) → video + thumb. Reads color presets from `config/video/color_grade_presets.yaml`, crop margin from `config/video/render_params.yaml`. Optional --shot-plan for motion per clip, --captions for caption text. Renders per-clip then concat (hard cuts); extracts thumbnail from thumbnail_frame_ref. Captions use FFmpeg drawtext when available, otherwise Pillow caption-burn fallback. Renderer now mixes background audio by default (music track if provided, otherwise generated ambient bed); use `--no-music` for silent output.

## Run full pipeline

```bash
python3 scripts/video/run_pipeline.py --plan-id plan-therapeutic-001
```

Use `--force` to overwrite existing artifacts. Outputs under `artifacts/video/<plan_id>/` and `artifacts/video/provenance/` (persistent; never in wipe path).

By default, pipeline publish gates are strict and fail-hard:
- segment-scene/image generation must produce usable `segment_asset_index.json`,
- captions are required,
- placeholder assets are not allowed (`max placeholder ratio = 0.0`),
- rendered `video.mp4` must contain an audio stream.
- scene extraction uses LLM context + metadata and fails if any segment scene is missing.
- FLUX image generation fails if any segment image fails.

## Full test: 90s script (Gen Z, NYC, depression)

End-to-end test from a 90-second depression script with Gen Z / NYC angle. Uses fixture `fixtures/video_pipeline_90s_depression/render_manifest.json` (~217 words ≈ 93 s at 140 WPM).

**One command (from repo root):**

```bash
./scripts/video/run_full_test_90s_depression.sh
```

**Or run the pipeline explicitly:**

```bash
python3 scripts/video/run_pipeline.py \
  --plan-id depression-genz-nyc-90s \
  --fixtures-dir fixtures/video_pipeline_90s_depression \
  --out-dir artifacts/video/depression-genz-nyc-90s \
  --content-type long_form \
  --topic depression \
  --persona gen_z \
  --force
```

**QA: where to find the video**

The file to open is always **`artifacts/video/<plan_id>/video.mp4`**.
Render requires real assets; placeholder mode is not used in strict pipeline runs.

Open (macOS): `open artifacts/video/depression-genz-nyc-90s/video.mp4`  
Open (Linux): `xdg-open artifacts/video/depression-genz-nyc-90s/video.mp4` or VLC.

**Get the real video**

1. **Credentials:** Set Cloudflare Workers AI credentials so FLUX can run. See [docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md](../../docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md) (env or `cloudflare_workers_ai.txt` at repo root).
2. **Build image bank** for the topic your script uses (e.g. depression for the 90s test). Wait for it to finish — images must exist before the render step.
   ```bash
   python3 scripts/video/run_flux_bank_build.py --topics depression --bank-dir image_bank
   ```
3. **Run the pipeline with the bank** so the resolver uses real assets and the renderer composites them. If `image_bank/index.json` exists, you can omit `--bank`.
   ```bash
   python3 scripts/video/run_pipeline.py \
     --plan-id depression-genz-nyc-90s \
     --fixtures-dir fixtures/video_pipeline_90s_depression \
     --out-dir artifacts/video/depression-genz-nyc-90s \
     --content-type long_form --topic depression --persona gen_z \
     --run-render --assets-dir image_bank --force
   ```
   Then open `artifacts/video/depression-genz-nyc-90s/video.mp4` — you’ll see FLUX-generated images and captions, not the black placeholder.

   **One script (after credentials are set):** `./scripts/video/run_90s_with_real_video.sh` builds the depression bank and runs the 90s pipeline with it.

Other artifacts in the plan dir: `script_segments.json`, `shot_plan.json`, `timeline.json`, `captions.json`, `thumb.jpg`, `distribution_manifest.json`, `thumb_provenance.json`, `qc_summary.json` (and when enabled: `segment_scenes.json`, `segment_images/`, `segment_asset_index.json`).

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
