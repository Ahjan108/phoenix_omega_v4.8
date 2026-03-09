# Video pipeline storage layout

**Persistent vs ephemeral:** Separate paths so the nightly wipe never touches build outputs or the image bank.

---

## Persistent (never wiped)

These paths hold pipeline artifacts and assets. **Do not** put them under the staging root.

| Path | Contents |
|------|----------|
| `artifacts/video/<plan_id>/` | script_segments.json, shot_plan.json, resolved_assets.json, timeline.json, captions.json, **video.mp4** (the rendered video — open this to view), distribution_manifest.json, thumb.jpg (frame-extracted or generated), thumb_16x9.jpg / thumb_9x16.jpg (optional), thumb_provenance.json, qc_summary.json (per-plan outputs) |

**How to view the video (QA)**  
The file you open to watch the video is always **`artifacts/video/<plan_id>/video.mp4`** (e.g. `open artifacts/video/depression-genz-nyc-90s/video.mp4` on macOS).  
- **Real video (images + captions matching the script):** Run the pipeline with an image bank so the renderer has assets: use `--run-render` and `--assets-dir <path_to_image_bank>`. The resolver expects assets named by `asset_id` (e.g. `asset-shot-1.jpg`). Without `--assets-dir`, the render step produces a **placeholder** (playable silent file) so the path still exists.  
- **After distribution:** The same video is copied to `staging/<date>/long/` or `staging/<date>/shorts/` per `<video_id>` and uploaded to R2; the partner (Metricool) reads from R2. To watch from R2 you need a public URL or S3-compatible download (see VIDEO_R2_CREDENTIALS).
| `artifacts/video/provenance/` | video_provenance.json per video_id |
| `config/video/` | Pacing, caption, motion, asset-selection config (versioned in repo; config_hash in artifacts identifies which version was used) |
| `image_bank/` | Image assets and index (when implemented) |
| `schemas/video/` | JSON schemas |

---

## Ephemeral staging (wiped after partner handoff)

Rendered videos and handoff manifests live here. Created by `scripts/video/distribution_writer.py` (pipeline stage 12). **Wipe only after** partner writes `batch_acknowledged.json` AND `failed_count == 0`.

| Path | Contents |
|------|----------|
| `staging/<YYYY-MM-DD>/long/<video_id>/` | video.mp4, thumb.jpg, distribution_manifest.json |
| `staging/<YYYY-MM-DD>/shorts/<video_id>/` | video.mp4, thumb.jpg, distribution_manifest.json |
| `staging/<YYYY-MM-DD>/upload_progress.json` | Per-video upload status (pending/uploaded/failed); resume-safe |
| `staging/<YYYY-MM-DD>/daily_batch.json` | Index of all videos for that day (written ONLY after all uploads succeed) |
| `staging/<YYYY-MM-DD>/batch_acknowledged.json` | Partner writes this after Metricool ingest |

**Wipe rule:** `scripts/video/wipe_staging_after_ack.py` deletes `staging/<date>/` only when `batch_acknowledged.json` exists AND `failed_count == 0`. Hard rule: no ack → no wipe. Use `--allow-failures` to override (not recommended).

**Thumbnail fallback (deterministic precedence):** `generated card > frame-extracted > none`. Distribution Writer selects format-aware thumb (`thumb_16x9.jpg` for long, `thumb_9x16.jpg` for shorts), falls back to `thumb.jpg` (legacy frame-extract), then proceeds without thumb if none exist. Uploaded to R2 as `thumb.jpg` (canonical handoff name). Source recorded in `thumb_provenance.json`.

---

## R2 bucket layout (mirrors staging)

The Distribution Writer uploads staging content to Cloudflare R2. Partner reads from R2, not local staging.

| R2 key | Contents |
|--------|----------|
| `<YYYY-MM-DD>/long/<video_id>/video.mp4` | Long-form video |
| `<YYYY-MM-DD>/long/<video_id>/thumb.jpg` | Thumbnail |
| `<YYYY-MM-DD>/long/<video_id>/distribution_manifest.json` | Per-video metadata |
| `<YYYY-MM-DD>/shorts/<video_id>/video.mp4` | Short-form video |
| `<YYYY-MM-DD>/shorts/<video_id>/thumb.jpg` | Thumbnail |
| `<YYYY-MM-DD>/shorts/<video_id>/distribution_manifest.json` | Per-video metadata |
| `<YYYY-MM-DD>/daily_batch.json` | Batch index (partner entry point) |
| `<YYYY-MM-DD>/batch_acknowledged.json` | Partner writes after ingest |

**Partner contract:** Read ONLY `<date>/daily_batch.json` and follow paths therein. Do not scan/list the bucket. After ingest to Metricool, write `batch_acknowledged.json` with `failed_count` and optional `failed_ids`. Schema: `schemas/video/batch_acknowledged_v1.schema.json`.

---

## JSON schemas

| Schema | Path | Written by |
|--------|------|------------|
| daily_batch_v1 | `schemas/video/daily_batch_v1.schema.json` | Distribution Writer |
| batch_acknowledged_v1 | `schemas/video/batch_acknowledged_v1.schema.json` | Partner (Metricool) |
| render_manifest_v1 | `schemas/video/render_manifest_v1.schema.json` | Pipeline input |
| image_bank_asset_v1 | `schemas/video/image_bank_asset_v1.schema.json` | Asset bank |

---

## Idempotency and config hash

- Each stage writes output **atomically** (temp file then rename).
- Each stage **skips** if output already exists and is valid (unless `--force`).
- Artifacts that depend on `config/video/` include **config_hash** (hash of all `.yaml` under `config/video/`). Use it to see which config version produced a given shot_plan or timeline.
