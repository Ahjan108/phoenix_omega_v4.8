# Freebie index and generated assets

**Authority:** [specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md](../../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md).

## File contract (DoD)

- **`artifacts/freebies/index.jsonl`** = **release/catalog plan rows only.** Updated only by release or catalog pipeline runs (never by systems test). Use `--no-update-freebie-index` for test runs.
- **`artifacts/freebies/artifacts_index.jsonl`** = **generated file log only.** One row per generated HTML/PDF/etc.; written by `phoenix_v4.freebies.freebie_renderer`.

## index.jsonl

Plan rows only (one per book). The pipeline upserts one row per `book_id` when writing a plan with `--out`, unless `--no-update-freebie-index` is set. Used by density and CTA caps gates (same scope).

Example plan row:
```json
{"book_id": "...", "freebie_bundle": ["breath_timer_v1", "companion_core_v2"], "cta_template_id": "tool_forward", "slug": "self-worth-nyc-breath", "freebie_slug": "self-worth-nyc-breath"}
```

Density validation (`validate_freebie_density.py --index ...`) and CTA caps (`cta_signature_caps.py --index ...`) use this file.

**Curated index (governance evidence):** To satisfy Gate 16 + 16b (density + CTA caps), the index can be rebuilt from a blessed plans directory. **Blessed plans path:** `artifacts/freebies/blessed_plans` (curated subset from `artifacts/systems_test/plans` with diverse bundle/CTA/slug; max 5 per (brand, quarter, cta_signature)). Rebuild: `python3 scripts/rebuild_freebie_index_from_plans.py --plans-dir artifacts/freebies/blessed_plans --out artifacts/freebies/index.jsonl`. Then run both validators on the same index.

## artifacts_index.jsonl

Generated file log only (one row per rendered file). Written by `phoenix_v4.freebies.freebie_renderer` when generating HTML/PDF. Not used by density or CTA caps gates.

## Generated files

HTML (and optional PDF) outputs live under `artifacts/freebies/YYYY-MM-DD/` with names like `{slug}_{freebie_id}.html`.

---

## V4 Immersion Ecosystem: asset store and pipeline

**Asset store layout:** Pre-built assets live under a format-first store:

`store/{format}/{topic}/{persona}/{freebie_id}.{ext}`

- `format`: html, pdf, epub, mp3
- Fallback for missing topic/persona: `store/{format}/default/{persona}/` or per-renderer resolution
- Built by `scripts/create_freebie_assets.py` and consumed by `generate_freebies_for_book(..., asset_store_root=...)`

**Manifest:** `artifacts/asset_planning/manifest.jsonl` — one JSON object per line: `topic`, `persona`, `freebie_id`, `format` (and optional keys). Produced by `scripts/plan_freebie_assets.py` (catalog mode: `--catalog <yaml>`; canonical mode: `--topics` + `--personas` YAML paths).

**Scripts:**

- **plan_freebie_assets.py** — Builds manifest from a book catalog or from canonical topics × personas; runs freebie planner per (topic, persona).
- **create_freebie_assets.py** — Reads manifest; generates HTML (template + metadata), PDF (WeasyPrint), EPUB (if ebooklib present), MP3 (placeholder or TTS); writes to the store.
- **validate_asset_store.py** — Validates store against manifest (exists, non-empty; optional `--rules config/validation.yaml` for format-specific rules).

**Publish directory:** When `run_pipeline.py --publish-dir <dir>` (and optionally `--asset-store <store_root>`) is used, `generate_freebies_for_book` can write final freebie outputs to `publish_dir/{slug}/` for public or email-gated delivery. Assets are copied from the store when present, otherwise rendered on demand.
