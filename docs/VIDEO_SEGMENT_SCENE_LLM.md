# Video: Segment-scene extraction (LLM) and script-specific prompts

Visuals must be **specific to what the script is saying** — not generic "hands" or abstract symbols. This is done by having an LLM read each segment and output **metadata to prompt the image**.

## Flow

1. **Script segments** (`script_segments.json`) — one segment per section of the script (e.g. 7 for a 90s video).
2. **LLM step** — For each segment, the LLM reads the full script context + segment metadata and outputs:
   - `scene_description`: one short sentence for the image (specific to the script; no faces).
   - `mood`: one word.
   - `avoid`: list of things to avoid in the image.
3. **Per-segment image build** — One FLUX image per segment using that `scene_description` (plus topic palette and constraints). Result: one image per segment, indexed by `segment_id`.
4. **Pipeline** — Shot planner and asset resolver use **segment_id**: each shot gets the asset for its segment, so the visual matches the script.

**Hard-fail policy:** No fallback scene generation and no local placeholder image generation in production path. If LLM or FLUX fails for any segment, pipeline fails.
The pipeline runs an EI V2-assisted retry loop (`config/video/ei_v2_scene_repair.yaml`) that retries scene generation with repair guidance and alignment scoring before final failure.

## Commands

```bash
# 1. Extract segment → scene metadata (LLM). Use Enlightened Intelligence V2 or any OpenAI-compatible API.
python scripts/video/run_segment_scene_extraction.py \
  artifacts/video/<plan_id>/script_segments.json \
  -o artifacts/video/<plan_id>/segment_scenes.json \
  --topic depression \
  --platform tiktok

# 2. Generate one FLUX image per segment from those scenes.
python scripts/video/run_flux_per_segment_build.py \
  artifacts/video/<plan_id>/segment_scenes.json \
  -o artifacts/video/<plan_id> \
  --topic depression

# 3. Run pipeline with segment index (and assets-dir = plan segment_images).
python scripts/video/run_pipeline.py \
  --plan-id <plan_id> \
  --out-dir artifacts/video/<plan_id> \
  --run-render \
  --assets-dir artifacts/video/<plan_id>/segment_images \
  ... # and pass segment index into asset resolver step
```

The pipeline (or a wrapper script) must pass `--segment-index artifacts/video/<plan_id>/segment_asset_index.json` to the asset resolver and `--assets-dir artifacts/video/<plan_id>/segment_images` to the render step when using segment-driven images.

## LLM config

- **Config:** `config/video/segment_scene_llm.yaml` (system hint, output schema hint, timeouts).
- **Env (preferred):** `QWEN_BASE_URL`, `QWEN_API_KEY`, optional `QWEN_MODEL` (default `qwen2.5:latest`).
- **Alias env supported:** `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`.
- Point `QWEN_BASE_URL` (or `OPENAI_BASE_URL`) at your Qwen Agent / Enlightened Intelligence V2 OpenAI-compatible endpoint.

## Outputs

| File | Purpose |
|------|--------|
| `segment_scenes.json` | Per-segment `scene_description`, `mood`, `avoid` from LLM. |
| `segment_images/<plan_id>_seg_N.png` | One FLUX image per segment. |
| `segment_asset_index.json` | Maps `segment_id` → `asset_id` for the resolver. |

Authority: game plan of N sections → N prompts that make sense for the script; LLM understands first, then we draw.
