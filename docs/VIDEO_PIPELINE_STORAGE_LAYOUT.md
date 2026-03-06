# Video pipeline storage layout

**Persistent vs ephemeral:** Separate paths so the nightly wipe never touches build outputs or the image bank.

---

## Persistent (never wiped)

These paths hold pipeline artifacts and assets. **Do not** put them under the staging root.

| Path | Contents |
|------|----------|
| `artifacts/video/<plan_id>/` | script_segments.json, shot_plan.json, resolved_assets.json, timeline.json, captions.json, distribution_manifest.json (per-plan outputs) |
| `artifacts/video/provenance/` | video_provenance.json per video_id |
| `config/video/` | Pacing, caption, motion, asset-selection config (versioned in repo; config_hash in artifacts identifies which version was used) |
| `image_bank/` | Image assets and index (when implemented) |
| `schemas/video/` | JSON schemas |

---

## Ephemeral staging (wiped after partner handoff)

Rendered videos and handoff manifests live here. **Wipe only after** partner writes `batch_acknowledged.json` (and optionally `failed_count == 0`).

| Path | Contents |
|------|----------|
| `staging/<YYYY-MM-DD>/long/<video_id>/` | video.mp4, thumb.jpg, distribution_manifest.json |
| `staging/<YYYY-MM-DD>/shorts/<video_id>/` | video.mp4, thumb.jpg, distribution_manifest.json |
| `staging/<YYYY-MM-DD>/daily_batch.json` | Index of all videos for that day |

**Wipe rule:** Delete `staging/<date>/` only when `staging/<date>/batch_acknowledged.json` exists (and optionally when the ack reports no failures).

---

## Idempotency and config hash

- Each stage writes output **atomically** (temp file then rename).
- Each stage **skips** if output already exists and is valid (unless `--force`).
- Artifacts that depend on `config/video/` include **config_hash** (hash of all `.yaml` under `config/video/`). Use it to see which config version produced a given shot_plan or timeline.
