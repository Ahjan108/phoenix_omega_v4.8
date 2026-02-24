# Freebie index and generated assets

**Authority:** [specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md](../../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md).

## index.jsonl

Append-only log. The pipeline appends to this file when writing a plan (when freebie generation is enabled). Two row types:

**Plan rows** (one per book, from `run_pipeline.py`): used for density CI and wave-level anti-spam.
```json
{"book_id": "...", "freebie_bundle": ["breath_timer_v1", "companion_core_v2"], "freebie_bundle_with_formats": [{"freebie_id": "breath_timer_v1", "formats": ["html", "pdf"]}], "cta_template_id": "tool_forward", "slug": "self-worth-nyc-breath"}
```

**Artifact rows** (one per generated file, from `phoenix_v4.freebies.freebie_renderer`): audit trail of HTML/PDF outputs.
```json
{"freebie_id": "breath_timer_v1", "book_id": "...", "persona": "gen_z_professionals", "topic": "anxiety", "type": "somatic_html_tool", "format": "html", "file_path": "artifacts/freebies/2026-02-23/anxiety-gen_z-breath_timer_v1.html", "slug": "anxiety-gen_z-breath", "cta": "tool_forward", "generated_at": "2026-02-23T10:30:00Z", "hash": "sha256:abc..."}
```

Density validation (`validate_freebie_density.py --index ...`) uses only rows that have `freebie_bundle` (plan rows).

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
