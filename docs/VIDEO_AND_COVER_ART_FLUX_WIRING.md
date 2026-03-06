# Wiring FLUX (Cloudflare Workers AI) into Video and Author Cover Art

**Purpose:** What’s already there vs what you need to connect so FLUX-generated images feed the **video** pipeline and **author cover art**.

**Credentials:** Already set. `cloudflare_workers_ai.txt` at repo root + `scripts/video/confirm_cloudflare_credentials.py` + `scripts/video/run_flux_generate.py` work for single-image tests.

---

## 1. Video pipeline — current state and gap

**Already in place:**
- **FLUX generator:** `scripts/video/run_flux_generate.py` — one image per run, writes to `image_bank/` (e.g. `master_prompt_test_anxiety.png`). Uses `config/video/brand_style_tokens.yaml` and `prompt_constraints.yaml`.
- **Asset resolver:** `scripts/video/run_asset_resolver.py` — takes a shot plan and optional `--bank <index.json>`. Resolves each shot’s `visual_intent` to an `asset_id` from the bank index.
- **Renderer:** `scripts/video/run_render.py` — takes `--assets-dir` and loads `{assets_dir}/{asset_id}.jpg` or `.png` per clip.

**Gap:** The resolver expects a **bank index** (JSON/JSONL) with entries like:
`{"visual_intent": "...", "composition_compat": {"16:9": 1.0}, "asset_id": "..."}`.  
FLUX currently only writes loose PNGs under `image_bank/`; nothing builds that index or names files by `asset_id` for the resolver/renderer.

**To wire FLUX into video you need to:**
1. **Batch FLUX:** A script (or loop) that generates many images from your shot plan / topic×intent list and writes them under `image_bank/` with **stable filenames** (e.g. `{topic}_{visual_intent}_{variant}.png` or same as `asset_id`).
2. **Index builder:** A step that scans `image_bank/` (or the batch output) and writes `image_bank/index.json` (or similar) with `visual_intent`, `asset_id` (= filename without extension), and `composition_compat` so the resolver can match shots to assets.
3. **Use the bank in the pipeline:** When running the video pipeline, pass `--bank image_bank/index.json` to the asset resolver and `--assets-dir image_bank` to the renderer so clips use your FLUX images.

Optional: define a convention (e.g. `asset_id` = filename without extension) so the renderer’s `assets_dir / f"{asset_id}.png"` finds the right file.

---

## 2. Author cover art — current state and gap

**Already in place:**
- **Cover art resolution:** `phoenix_v4/planning/author_cover_art_resolver.py` — used by `run_pipeline.py`. Resolves author/teacher to `cover_art_base` (path to PNG), `style_hint`, `palette_tokens` from `config/authoring/author_cover_art_registry.yaml`.
- **Base image generation:** `scripts/generate_author_cover_art_bases.py` — builds **gradient PNGs** only (hex palettes, no FLUX). Writes to `assets/authors/cover_art/{author_id}_base.png`.

**Gap:** There is no path that calls FLUX to generate author cover art. The registry points at static files (gradients or hand-made PNGs).

**To wire FLUX into author cover art you can:**
1. **Option A — Extend the generator:** Add an option to `scripts/generate_author_cover_art_bases.py` (e.g. `--use-flux`) that, per author in the registry, builds a FLUX prompt from `style_hint` and `palette_tokens` (and optional author-specific prompt), calls `run_flux_generate` or the same `call_cloudflare_flux` helper, and writes the result to `assets/authors/cover_art/{author_id}_base.png`. Keep the existing gradient path as fallback when FLUX is not used.
2. **Option B — Separate script:** New script (e.g. `scripts/generate_author_cover_art_flux.py`) that reads the registry, calls FLUX per author, writes PNGs to `assets/authors/cover_art/`, and optionally updates the registry. Pipeline and resolver stay unchanged; they keep pointing at `cover_art_base` paths.

In both cases, reuse the same Cloudflare credentials and the same FLUX call pattern as in `scripts/video/run_flux_generate.py` (and optionally the same prompt template / constraints).

---

## 3. Summary

| System            | FLUX status        | To wire FLUX |
|-------------------|--------------------|--------------|
| **Video**         | Generator only     | Batch FLUX → named images in `image_bank/`; build resolver index; pass `--bank` and `--assets-dir` in the video pipeline. |
| **Author cover art** | Not used (gradients only) | Add FLUX path to `generate_author_cover_art_bases.py` or a dedicated script that writes to `assets/authors/cover_art/` and keep registry paths. |

Credentials and single-image FLUX are done; the remaining work is **batch + index for video** and **FLUX-backed generation for author cover art**.
