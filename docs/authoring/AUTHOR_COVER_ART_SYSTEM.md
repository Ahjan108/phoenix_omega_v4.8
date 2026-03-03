# Author Signature Cover Art Base Background System

**Purpose:** Author signature cover art base backgrounds for the first 10 authors of every catalog.  
**Authority:** [config/authoring/author_cover_art_registry.yaml](../../config/authoring/author_cover_art_registry.yaml)  
**Last updated:** 2026-03-03

---

## 1. Overview

Each catalog (24 brands in [brand_archetype_registry.yaml](../../config/catalog_planning/brand_archetype_registry.yaml)) uses author signature base backgrounds when rendering book covers. The first 10 authors (teachers) each have a unique base background that serves as the visual signature for their books across catalogs.

**First 10 authors:** ahjan, master_feung, sai_ma, ra, junko, miki, master_wu, pamela_fellows, joshin, maat.

---

## 2. Registry

**Path:** `config/authoring/author_cover_art_registry.yaml`

Maps each author_id to:

- `cover_art_base`: path to PNG asset (e.g. `assets/authors/cover_art/ahjan_base.png`)
- `style_hint`: mood descriptor (contemplative, grounded, compassionate, etc.)
- `palette_tokens`: optional color tokens for blending with brand `cover_art_identity`

---

## 3. Asset location

```
assets/authors/cover_art/
  ahjan_base.png
  master_feung_base.png
  sai_ma_base.png
  ra_base.png
  junko_base.png
  miki_base.png
  master_wu_base.png
  pamela_fellows_base.png
  joshin_base.png
  maat_base.png
```

**Dimensions:** 1080×1920 (mobile/audiobook portrait).  
**Format:** PNG, no text, no faces — base layer only. Title and brand overlay applied at render time.

---

## 4. Generation

**Script:** [scripts/generate_author_cover_art_bases.py](../../scripts/generate_author_cover_art_bases.py)

Pure Python (zlib only); no Pillow required.

```bash
python3 scripts/generate_author_cover_art_bases.py
```

Outputs one gradient PNG per author into `assets/authors/cover_art/`. Palettes are taken from the registry `palette_tokens`.

---

## 5. Runtime and pipeline integration

**Resolver:** [phoenix_v4/planning/author_cover_art_resolver.py](../../phoenix_v4/planning/author_cover_art_resolver.py) — `resolve_author_cover_art(author_id_or_teacher_id, repo_root)` returns `cover_art_base`, `cover_art_style_hint`, `cover_art_palette_tokens`, `cover_variant_id`. Uses `author_id` when set, else `teacher_id` (Teacher Mode). Fallback: default author when missing from registry.

**Pipeline output:** [scripts/run_pipeline.py](../../scripts/run_pipeline.py) writes to every plan JSON: `cover_art_base`, `cover_art_style_hint`, `cover_art_palette_tokens`, `cover_variant_id` for export/storefront and CTR tracking by `cover_variant_id`.

**Cover renderer / freebie:** Use plan fields when compositing; see [TITLE_AND_CATALOG_MARKETING_SYSTEM.md](../TITLE_AND_CATALOG_MARKETING_SYSTEM.md) and [PHOENIX_FREEBIE_SYSTEM_SPEC.md](../../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md).

---

## 6. CI gate

**Script:** [scripts/ci/check_author_cover_art.py](../../scripts/ci/check_author_cover_art.py)

**Rule:** Every **launchable** author (teachers in [brand_teacher_matrix.yaml](../../config/catalog_planning/brand_teacher_matrix.yaml) + authors in [author_registry.yaml](../../config/author_registry.yaml)) must have:

- An entry in `author_cover_art_registry.yaml`
- Existing PNG at `cover_art_base`
- Non-empty `style_hint` and `palette_tokens`

**Wiring:** Gate **18** in [scripts/run_production_readiness_gates.py](../../scripts/run_production_readiness_gates.py). Run: `python scripts/run_production_readiness_gates.py`.
