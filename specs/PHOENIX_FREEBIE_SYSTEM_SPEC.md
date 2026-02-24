# Phoenix Freebie System — Canonical Dev Spec

**Purpose:** A **Freebie Planning & Attachment Layer** that is deterministic, pipeline-aligned, and extendable. Build the pipe first; add scale guards later.

**Authority:** This spec. Implementation: `config/freebies/`, `phoenix_v4/planning/freebie_planner.py`, `phoenix_v4/tools/generate_html_freebie.py`.

---

## Phase 1 (build now) vs Phase 3 (scale hardening)

| Phase 1 — Build now | Phase 3 — Add at scale |
|---------------------|-------------------------|
| Registry + selection rules | Density wave enforcement |
| Deterministic freebie_planner.py | Entropy / anti-spam CI gate |
| CompiledBook extension (freebie_bundle, cta_template_id, freebie_slug) | CTSS-level similarity tracking |
| CTA template system | Reseed logic / multi-wave diversity |
| Slug: `{topic}-{persona}-{primary_freebie}` | Cross-book slug uniqueness enforcement |

Phase 1 = architecture alignment. Phase 3 = when you have 300+ books, marketplace scrutiny, SEO collision risk. This spec describes both; **implement Phase 1 first**.

---

## 1. Architecture position

Freebies live **between Layer 2 (Omega) and the distribution layer**. They attach **post-compile** (after Stage 3).

They **do not** affect: Arc, Engine, atom selection, emotional band logic.

---

## 2. Structure

```
config/freebies/
    freebie_registry.yaml
    freebie_selection_rules.yaml
    cta_templates.yaml
    tier_bundles.yaml          (V4 Immersion: Good/Better/Best)
    audio_scripts.yaml         (V4 Immersion: templated/fixed scripts for MP3)
    freebie_to_landing.yaml
config/catalog_planning/
    canonical_topics.yaml     (V4 Immersion: single source for asset planning)
    canonical_personas.yaml
config/tts/
    engines.yaml               (V4 Immersion: TTS engine + voice mapping)
config/validation.yaml         (V4 Immersion: asset validation rules)
config/asset_lifecycle.yaml    (V4 Immersion: regenerate_when, auto_prune)

phoenix_v4/planning/
    freebie_planner.py        (plan_freebies, get_freebie_bundle_with_formats)
phoenix_v4/freebies/
    freebie_renderer.py       (render_freebie, generate_freebies_for_book)
phoenix_v4/tools/
    generate_html_freebie.py   (legacy CLI)

scripts/
    validate_canonical_sources.py   (V4 Immersion: canonical vs runtime config)
    plan_freebie_assets.py         (V4 Immersion: manifest from catalog or canonical)
    create_freebie_assets.py       (V4 Immersion: HTML/PDF/EPUB/MP3 to store)
    validate_asset_store.py        (V4 Immersion: manifest vs store)
    run_pipeline.py               (--formats, --skip-audio, --publish-dir, --asset-store)

artifacts/freebies/
    index.jsonl                (plan rows only; one row per book_id)
    artifacts_index.jsonl      (per-file artifact generation log)
artifacts/asset_planning/
    manifest.jsonl             (V4 Immersion: one row per topic, persona, freebie_id, format)
artifacts/freebie_assets/store/   (V4 Immersion: format-first store)
    {format}/{topic}/{persona}/{freebie_id}.{ext}
```

Phase 3 only: `phoenix_v4/qa/validate_freebie_density.py`, CTSS extension in `scripts/ci/`.

---

## 3. Freebie registry (source of truth)

**Path:** `config/freebies/freebie_registry.yaml`

Each freebie declares: `freebie_id`, `type`, `topics`, `personas`, `engines`, `book_types`, `arc_intensity_max`, optional `file_template`, `output_formats` (e.g. `[html, pdf]`, `[mp3]`), `email_required`, `cta_style`, `spam_weight`. For Phase 1 persona prioritization: optional `tool_style` (`structured` \| `interactive`) on somatic/assessment freebies.

---

## 4. Freebie types (enum)

`companion_workbook_pdf`, `somatic_html_tool`, `assessment_html`, `mini_audio`, `checklist_pdf`, `journal_pdf`, `identity_sheet_pdf`. V4 Immersion Ecosystem (all in registry; video/MP4 deferred): `guided_audio`, `thirty_day_tracker_pdf`, `environment_guide_pdf`, `affirmations_audio`, `audio_journal_prompts`, `emergency_kit_html`, `conversation_scripts_pdf`, `resistance_mapping_html`, `accountability_partner_pdf`. Registry entries declare `output_formats` (e.g. `[html, pdf]`, `[mp3]`); audio types use pre-created assets (no file_template).

---

## 5. Planner logic — Phase 1 (hard rules only)

**File:** `phoenix_v4/planning/freebie_planner.py`

**Input:** BookSpec (or dict), FormatPlan (dict), CompiledBook (or dict), Arc. Optional: `wave_index` (for density/reseed), `series_context` (series_id, installment_number, total_in_series, previous_primary_freebies) for series-aware selection.

**Output:** `freebie_bundle` (list[str]), `cta_template_id` (str), `freebie_slug` (str). Pipeline also attaches `freebie_bundle_with_formats` via `get_freebie_bundle_with_formats()`.

### Rule layer (Phase 1)

1. **EXERCISE slots** → attach one compatible `somatic_html_tool`.
2. **Engine** in anxiety \| burnout \| shame → attach one `assessment_html`.
3. **Duration ≥ 60 min** → attach `companion_workbook_pdf`.
4. **Persona executive** → prefer freebie with `tool_style: structured`.
5. **Persona gen_z** → prefer freebie with `tool_style: interactive`.

No density logic, no wave math, no reseed. Just deterministic selection.

**Slug formula:** `{topic}-{persona}-{primary_freebie}` (e.g. `burnout-gen_z_professional-breath_reset`).

---

## 6. Freebie URL structure

Deterministic: `/free/{topic}/{persona}/{freebie_id}/`. Example: `/free/self-worth/nyc-executives/breath_timer_v1/`.

---

## 7. CTA template layer

**Path:** `config/freebies/cta_templates.yaml`

Templates: no hype, no promise, brand-aligned, persona-aware. Planner injects `{topic}`, `{freebie_name}`, `{slug}`. No creative generation.

---

## 8. Freebie generation engine

**Unified renderer:** `phoenix_v4/freebies/freebie_renderer.py` — single entry point `render_freebie(freebie_config, book_metadata, output_format)`. Loads template by registry `file_template` from `SOURCE_OF_TRUTH/freebies/templates/` (fallback `config/freebies/templates/`), injects metadata (topic, persona, slug, CTA), writes to `artifacts/freebies/YYYY-MM-DD/`, appends per-file rows to `artifacts/freebies/artifacts_index.jsonl`. Optional PDF via WeasyPrint (HTML → PDF).

**Templates:** Registry `file_template` (e.g. `breath_timer_template.html`, `companion_workbook_template.md`) must exist under the template root. Placeholders: `{{topic}}`, `{{persona}}`, `{{slug}}`, `{{cta_text}}`, `{{freebie_name}}`, `{{title}}`. Metadata-only MVP; exercise content injection can be added later.

**Pipeline:** After Stage 3, `run_pipeline.py` calls `generate_freebies_for_book(plan, book_spec)` to render HTML for each freebie in the bundle. Plan JSON includes `topic_id`, `persona_id` for standalone re-render via `python3 -m phoenix_v4.freebies.freebie_renderer <plan.json> [--pdf]`.

**V4 Immersion Ecosystem:** Planner output includes `freebie_bundle_with_formats` (formats per freebie). Multi-format export: `generate_freebies_for_book(..., formats=..., skip_audio=..., asset_store_root=..., publish_dir=...)` can copy from a format-first asset store (`store/{format}/{topic}/{persona}/{freebie_id}.{ext}`) and/or publish to `publish_dir/{slug}/` for email-gated delivery. CLI: `--formats html,pdf,epub,mp3`, `--skip-audio`, `--publish-dir`, `--asset-store`. Asset pipeline: `scripts/plan_freebie_assets.py` (manifest from catalog or canonical topics×personas), `scripts/create_freebie_assets.py` (generate store), `scripts/validate_asset_store.py` (validate).

**Legacy:** `phoenix_v4/tools/generate_html_freebie.py` remains for backward compatibility (e.g. direct CLI); new pipeline path uses the renderer.

---

## 9. Planner contract (CompiledBook extension)

CompiledBook (and plan JSON) is extended with:

- `freebie_bundle`: list[str]
- `cta_template_id`: str
- `freebie_slug`: str
- `freebie_bundle_with_formats`: list[{freebie_id, formats}] (V4 Immersion Ecosystem; set when registry and planner support it)

Set **after** Stage 3 by the freebie planner. Arc unchanged. Planner may receive optional `series_context` (series_id, installment_number, total_in_series, previous_primary_freebies) for series-aware selection.

---

## 10. Phase 3 — Anti-spam / density / CTSS (implemented)

- **Density gate:** `phoenix_v4/qa/validate_freebie_density.py` — FAIL wave if identical_bundle ≥40%, identical CTA ≥50%, identical slug pattern ≥60%. Wired in V4_5_PRODUCTION_READINESS_CHECKLIST §16 and `run_production_readiness_gates.py`; runs when `artifacts/freebies/index.jsonl` has ≥2 plan rows (full Phase 3). Gate normalizes to unique `book_id` (last row wins).
- **CTSS:** Catalog similarity index row includes `freebie_bundle_signature`, `cta_signature`; CTSS weight 0.08 total (0.04 each). `scripts/ci/update_similarity_index.py` and `check_platform_similarity.py`; Monte Carlo uses same weights.
- **Reseed:** `plan_freebies(..., wave_index=...)` — when wave_index (rows from `artifacts/freebies/index.jsonl`) is provided and density would exceed thresholds, slug is deterministically varied with a seed suffix. Wave normalization is plan-row-only and deduped by `book_id`.
- **Pipeline:** On each run with `--out`, the pipeline upserts one plan row per `book_id` into `artifacts/freebies/index.jsonl`, passes existing index rows as `wave_index` to the planner, and by default generates HTML freebie artifacts (`public/free/<slug>/`). Use `--no-generate-freebies` to skip HTML generation.

**27 exercise landing pages (email capture):** `config/freebies/exercises_landing.json` is the source of truth for 27 breathwork/somatic exercises. Run `python3 scripts/generate_landing_pages.py` to output `public/breathwork/lp-{id}.html` (one per exercise). Each page is minimal: title, benefit, duration, email field, MailerLite placeholders. When the planner assigns a somatic freebie that appears in `config/freebies/freebie_to_landing.yaml`, `public/free/{slug}/index.html` is generated as a redirect to the corresponding `public/breathwork/lp-{id}.html` so book CTAs send traffic to the right email-capture page. Email sequences (5-email welcome + persona variants) live in `docs/email_sequences/`.

---

---

## 11. V4 Immersion Ecosystem (implemented)

**Canonical sources:** `config/catalog_planning/canonical_topics.yaml` and `canonical_personas.yaml` are the single source of truth for asset planning. Validated by `scripts/validate_canonical_sources.py` against `topic_engine_bindings.yaml` and `identity_aliases.yaml`.

**Asset pipeline (two modes):**  
- **Catalog mode:** `scripts/plan_freebie_assets.py --catalog <yaml>` — manifest from a list of books (topic_id, persona_id, optional arc_path).  
- **Canonical mode:** `--topics canonical_topics.yaml --personas canonical_personas.yaml` — manifest from cross-product; planner run per (topic, persona) with mock arc.

**Asset creation:** `scripts/create_freebie_assets.py --manifest manifest.jsonl --format html,pdf,epub,mp3 --store <dir>`. Writes to format-first store `store/{format}/{topic}/{persona}/{freebie_id}.{ext}`. MP3 uses TTS config (`--tts-config config/tts/engines.yaml`); audio scripts from `config/freebies/audio_scripts.yaml` (templated or fixed + overrides).

**Asset validation:** `scripts/validate_asset_store.py --store <dir> --manifest manifest.jsonl [--rules config/validation.yaml]`. Per-format rules: exists, non-empty; optional duration/size for MP3.

**Book pipeline:** `generate_freebies_for_book(..., formats=..., skip_audio=..., asset_store_root=..., publish_dir=...)` resolves assets from store (with fallback `store/{format}/default/{persona}/`), renders when not in store, and can copy to `publish_dir/{slug}/` for public/free email-gated delivery. CLI: `run_pipeline.py --formats html,pdf,epub,mp3 --skip-audio --publish-dir public/free --asset-store artifacts/freebie_assets/store`.

**Tier bundles:** `config/freebies/tier_bundles.yaml` maps Good / Better / Best to freebie types (packaging and marketing).

**Asset lifecycle:** `config/asset_lifecycle.yaml` — `regenerate_when` (template_modified, tts_engine_upgraded, canonical_topics_changed), `auto_prune` for topics no longer in canonical.

---

## Implementation status

- **Freebie index:** Pipeline maintains `artifacts/freebies/index.jsonl` as plan rows only (one row per `book_id`), and renderer writes per-file artifact logs to `artifacts/freebies/artifacts_index.jsonl`. See docs/PLANNING_STATUS.md §5.
- **V4 Immersion types:** All immersion freebie types are in the registry with `output_formats`; document types have templates in SOURCE_OF_TRUTH/freebies/templates/; audio types (guided_audio, affirmations_audio, audio_journal_prompts) use pre-created assets only (no file_template). Video (MP4) deferred.
- **Narrator support** and **KB-driven gap-fill** are documented in OMEGA_LAYER_CONTRACTS.md, docs/SYSTEMS_V4.md, and docs/PLANNING_STATUS.md §5.

---

## References

- [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md) — BookSpec, FormatPlan, CompiledBook (freebie fields optional).
- [docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md) — Freebie pipeline status.
