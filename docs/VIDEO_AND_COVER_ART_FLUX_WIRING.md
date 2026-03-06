# Wiring FLUX (Cloudflare Workers AI) into Video and Author Cover Art

**Purpose:** FLUX-generated images feed the **video** pipeline and **author cover art**. Wiring is implemented; use the scripts below.

**Credentials:** `cloudflare_workers_ai.txt` at repo root. Confirm with `python3 scripts/video/confirm_cloudflare_credentials.py`.

---

## 1. Video pipeline — wired

**Shared client:** `scripts/video/flux_client.py` — `load_credentials()`, `get_prompt_for_topic_scene(topic, scene)`, `call_flux(...)`.

**Build the image bank and index:**
```bash
# Generate FLUX images for (topic × visual_intent) and write image_bank/index.json
python3 scripts/video/run_flux_bank_build.py

# Optional: limit topics or number of images for testing
python3 scripts/video/run_flux_bank_build.py --topics anxiety,burnout,grief --limit 8
python3 scripts/video/run_flux_bank_build.py --dry-run   # plan only
```

**If you already have PNGs in image_bank/** (e.g. from a previous run or manual add):
```bash
python3 scripts/video/build_image_bank_index.py
# Writes image_bank/index.json from existing *.png (expects names like topic_HOOK_VISUAL.png)
```

**Use the bank in the video pipeline:**
- Run the asset resolver with the bank: `--bank image_bank/index.json`
- Run the renderer with the assets dir: `--assets-dir image_bank`

Example (after you have a shot_plan.json):
```bash
python3 scripts/video/run_asset_resolver.py artifacts/video/<plan_id>/shot_plan.json -o artifacts/video/<plan_id>/resolved_assets.json --bank image_bank/index.json
python3 scripts/video/run_render.py ... --assets-dir image_bank
```

**Config:** `config/video/flux_bank_scenes.yaml` — maps each `visual_intent` (HOOK_VISUAL, CHARACTER_EMOTION, etc.) to a scene description for the FLUX prompt.

---

## 2. Author cover art — wired

**Generate FLUX cover art bases** (one per author in the registry):
```bash
python3 scripts/generate_author_cover_art_flux.py

# Optional: specific authors, or dry-run
python3 scripts/generate_author_cover_art_flux.py --authors ahjan,master_feung
python3 scripts/generate_author_cover_art_flux.py --dry-run
```

Output: `assets/authors/cover_art/{author_id}_base.png`. The pipeline and `author_cover_art_resolver` already use `cover_art_base` from the registry; point the registry at these paths (they already match: `assets/authors/cover_art/ahjan_base.png` etc.).

**Gradient fallback:** `scripts/generate_author_cover_art_bases.py` still generates gradient PNGs without FLUX; use it when you don’t want to call the API.

---

## 3. Summary

| System            | Script / step |
|-------------------|----------------|
| **Video**         | `run_flux_bank_build.py` → `image_bank/*.png` + `image_bank/index.json`. Then `run_asset_resolver.py --bank image_bank/index.json` and `run_render.py --assets-dir image_bank`. |
| **Author cover art** | `generate_author_cover_art_flux.py` → `assets/authors/cover_art/{id}_base.png`. Registry paths unchanged. |
