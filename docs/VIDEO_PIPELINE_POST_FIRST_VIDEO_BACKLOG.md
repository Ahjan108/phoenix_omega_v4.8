# Video pipeline: post–first-video backlog

**When to do this:** After the first real video renders successfully (FFmpeg or stub replaced). These items improve operability and diagnostics; they do not block the first render.

---

## Cleanup / quality (tagged, not blocking)

| Item | Description |
|------|-------------|
| **pipeline_version** | Add `pipeline_version: "video-pipeline-v1"` (or similar) to artifacts so code changes are visible when config is unchanged. |
| **Input artifact refs** | Record upstream paths in outputs (e.g. timeline: `input_shot_plan`, `input_resolved_assets`) for easier provenance debugging. |
| **Placeholder asset naming** | Structure placeholder IDs (e.g. `placeholder_env_forest_001`, `placeholder_symbol_door_003`) so render stage can map them to image bank later. |
| **Pipeline timing log** | Write `artifacts/video/<plan_id>/pipeline_log.json` with per-stage start_time, end_time, duration_ms for throughput tuning. |

---

## QC expansion (after renderer exists)

| Item | Description |
|------|-------------|
| **Caption overflow** | Check that caption content fits safe zone for target aspect (requires renderer/frame dimensions and caption placement). |
| **Visual rhythm** | Enforce max N consecutive shots with same visual_intent (e.g. 3); add to run_qc.py and optionally to shot planner. |

---

## FFmpeg / render params

- First renderer can be trial-and-error tuning. For a later spec, add `config/video/ffmpeg_render_params.yaml` with: zoompan parameters per motion type, drawtext font/size/position per caption policy, audio ducking (e.g. sidechaincompress), xfade duration between clips.
- Throughput: measure both **render time** and **upload time**; at 5,100 videos/day upload bandwidth can be the bottleneck.
