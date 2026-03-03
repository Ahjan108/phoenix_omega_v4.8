# Phoenix Docs Index

**Purpose:** Canonical index for documentation authority and navigation.  
**Missing-file policy:** Only existing files are linked; planned or missing files are listed as backlog items (plain text or `path` with ⚠️ *file not present*).  
**Last updated:** 2026-03-04 (Production Observability, Learning & Self-Healing spec)

**Missing-file policy:** Only files that exist on disk are linked. Planned or referenced-but-missing files are listed as plain text backlog items and marked `⚠️ *file not present*`.

---

## Canonical authority

- **System owner vision (north star):** [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md) — What the system owner wants: technical, therapeutic, reader/listener experience, marketing and business. The whole story of success.
- **Docs index (this file):** [docs/DOCS_INDEX.md](./DOCS_INDEX.md)
- **System architecture (sole authority):** [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md)
- **Writer/content authority:** [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md)

**Docs vs production 100%:** Governance and documentation consolidation (this index, specs, runbooks) = **strong docs layer**. **Production 100%** is only reached when **operational proof gates** are green: CI on `main`, release path checks (no export bypass), smoke runs, rollback evidence, branch protection. Strong docs support but do not replace runtime/release evidence. **Simulation (10k/100k) is readiness tooling, not standalone production 100%** — see [docs/RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) for the four requirements still needed (real canaries, CI gate on analyzer, evidence on main, release smoke + rollback proof).

---

## Core system docs

- [docs/RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) — Simulation (10k/100k) as readiness tooling; **four requirements for production 100%**: real pipeline canaries, CI gate on analyzer, evidence on main, release smoke + rollback proof
- [docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md](./PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md) — **Production Observability, Learning & Self-Healing (POLES):** observe 100% repo live; document success; elevate, auto-fix, retest failures; learn and enhance over time
- [docs/SYSTEMS_V4.md](./SYSTEMS_V4.md) — V4 systems overview
- [docs/PLANNING_STATUS.md](./PLANNING_STATUS.md) — Planning status
- [docs/SYSTEMS_AUDIT.md](./SYSTEMS_AUDIT.md) — Systems audit
- [specs/README.md](../specs/README.md) — Specs overview
- [ONBOARDING.md](../ONBOARDING.md) — Onboarding

---

## Rigorous system test & simulation (document all)

Single index: every doc, script, config, and artifact for simulation, 10k/100k knob coverage, analyzer, and production 100% requirements. **Simulation = readiness tooling; production 100%** still requires real canaries, CI gate on analyzer, evidence on main, release smoke + rollback proof ([RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md)).

### Docs

| Item | Location |
|------|----------|
| **Rigorous test & production 100%** | [docs/RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) — Sim as readiness; four production requirements |
| **V4 features, scale, knobs** | [docs/V4_FEATURES_SCALE_AND_KNOBS.md](./V4_FEATURES_SCALE_AND_KNOBS.md) — All knobs, simulation bullet, observability |
| **Systems V4 (systems test)** | [docs/SYSTEMS_V4.md](./SYSTEMS_V4.md) — §8 systems test (rigorous) |
| **Simulation overview** | [simulation/README.md](../simulation/README.md) — Quick run, config, Phase 2/3 workflow |
| **Phase 2 scope** | [simulation/SIMULATION_PHASE2_SCOPE.md](../simulation/SIMULATION_PHASE2_SCOPE.md) — Waveform, arc, drift |
| **Phase 3 MVP** | [simulation/PHASE3_MVP.md](../simulation/PHASE3_MVP.md) — Content/emotional force |
| **Production readiness checklist** | [specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md) — Gate 12 simulation |
| **Production gates script** | [scripts/run_production_readiness_gates.py](../scripts/run_production_readiness_gates.py) — Gate 12 checks simulation script exists |
| **Production observability spec** | [docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md](./PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md) — Observe, document, elevate/fix, learn |

### Scripts

| Item | Location |
|------|----------|
| **Simulation CLI** | [simulation/run_simulation.py](../simulation/run_simulation.py) — `--n`, `--phase2`, `--phase3`, `--use-format-selector`, `--full-knobs`, `--out` |
| **Simulator core** | [simulation/simulator.py](../simulation/simulator.py) — Formats, validation matrix, BookRequest, run_simulation(), validate_plan() |
| **Phase 2** | [simulation/phase2.py](../simulation/phase2.py) — Waveform, arc, drift on Phase 1 results |
| **Phase 3 MVP** | [simulation/phase3_mvp.py](../simulation/phase3_mvp.py) — Volatility, cognitive, consequence, reassurance on synthetic text |
| **10k sim runner** | `scripts/ci/run_simulation_10k.py` — n=10000, --use-format-selector, --phase2, --phase3 (CI) ⚠️ *file not present* |
| **100k sim runner** | `scripts/ci/run_simulation_100k.py` — n=100000, --full-knobs; optional --n, --out ⚠️ *file not present* |
| **Analyzer** | `scripts/ci/analyze_pearl_prime_sim.py` — Pass rate by dimension; best/worst combos; --input, --out ⚠️ *file not present* |
| **Rigorous suite runner** | `scripts/ci/run_rigorous_system_test.py` — 10k sim + variation report + E2E smoke + atoms coverage ⚠️ *file not present* |
| **Variation report** | [scripts/ci/report_variation_knobs.py](../scripts/ci/report_variation_knobs.py) — variation_knob_distribution, pearl_prime block from plans/index |
| **Monte Carlo CTSS** | [simulation/run_monte_carlo_ctss.py](../simulation/run_monte_carlo_ctss.py) — Duplication risk vs index |
| **Systems test** | [scripts/systems_test/run_systems_test.py](../scripts/systems_test/run_systems_test.py) — Phases 1–7; optional sim run |
| **Observability collector** | [scripts/observability/collect_signals.py](../scripts/observability/collect_signals.py) — Collect production signals (Phase 1 POLES); `--signals`, `--out` |

### Config (simulation & knob coverage)

| Item | Location |
|------|----------|
| **Formats (V4.5)** | [simulation/config/v4_5_formats.yaml](../simulation/config/v4_5_formats.yaml) — 14 formats, tiers S–E |
| **Validation matrix** | [simulation/config/validation_matrix.yaml](../simulation/config/validation_matrix.yaml) — Tier rules (misfire, silence, integration_modes, etc.) |
| **Emotional temperature curves** | [simulation/config/emotional_temperature_curves.yaml](../simulation/config/emotional_temperature_curves.yaml) — Per-format temperature sequences |
| **Format selection** | [config/format_selection/format_registry.yaml](../config/format_selection/format_registry.yaml), [config/format_selection/selection_rules.yaml](../config/format_selection/selection_rules.yaml) — Stage 2 format selector; includes `deep_book_6h` runtime (360 min, 52k–58k words) |
| **Canonical personas/topics** | [config/catalog_planning/canonical_personas.yaml](../config/catalog_planning/canonical_personas.yaml), [config/catalog_planning/canonical_topics.yaml](../config/catalog_planning/canonical_topics.yaml) — Knob sampler / full-knobs source |
| **Angles** | [config/angles/angle_registry.yaml](../config/angles/angle_registry.yaml) — angle_id for sim |
| **Book structure / journey / motif / reframe** | [config/source_of_truth/book_structure_archetypes.yaml](../config/source_of_truth/book_structure_archetypes.yaml), [config/source_of_truth/journey_shapes.yaml](../config/source_of_truth/journey_shapes.yaml), [config/source_of_truth/recurring_motif_bank.yaml](../config/source_of_truth/recurring_motif_bank.yaml), [config/source_of_truth/reframe_line_bank.yaml](../config/source_of_truth/reframe_line_bank.yaml) |
| **Section / chapter order** | [config/source_of_truth/section_reorder_modes.yaml](../config/source_of_truth/section_reorder_modes.yaml) — `chapter_order_modes.yaml` ⚠️ *file not present* |

### Artifacts

| Item | Location |
|------|----------|
| **10k results** | `artifacts/simulation_10k.json` (optional --out from run_simulation_10k.py) |
| **100k results** | `artifacts/simulation_100k.json` (optional --out from run_simulation_100k.py) |
| **Analysis JSON** | `artifacts/reports/pearl_prime_sim_analysis.json` (from analyze_pearl_prime_sim.py --out) |
| **Analysis summary** | `artifacts/reports/pearl_prime_sim_analysis_SUMMARY.txt` |
| **Variation report** | `artifacts/reports/variation_report.json` (from report_variation_knobs.py) |
| **Drift dashboard** | `artifacts/drift/` (from build_structural_drift_dashboard.py) |

### CI / workflows

| Item | Location |
|------|----------|
| **Simulation 10k workflow** | `.github/workflows/simulation-10k.yml` ⚠️ *file not present* |
| **Release gates** | `.github/workflows/release-gates.yml` ⚠️ *file not present* |
| **Teacher gates** | [.github/workflows/teacher-gates.yml](../.github/workflows/teacher-gates.yml) — Teacher production gates + teacher arc tests + Teacher Mode E2E smoke (see [Teacher Mode & production readiness](#teacher-mode--production-readiness-document-all)) |
| **Brand guards** | [.github/workflows/brand-guards.yml](../.github/workflows/brand-guards.yml) — NorCal Dharma brand-only invariants: matrix exclusion, assignments → default_teacher, secret scan, smoke tests (see [Church & payout](#church--payout-distribution-only-brands)) |

---

## Pearl News (document all)

Pearl News is 100% at **code/tests** when classifier, selector, quality gates, and e2e tests pass. It is **100% production-ready** only when all operational gates are confirmed on `main` with evidence links (see [PEARL_NEWS_GO_NO_GO_CHECKLIST.md](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md) and [PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md](./PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md)).

### Operational gates (production 100%)

1. Merge to `main`
2. `pearl_news_gates.yml` green on `main`
3. Networked pipeline smoke run on `main` passes
4. Scheduled workflow run on GitHub passes
5. WordPress draft-post flow verified with real secrets
6. Checklist doc completed with evidence links

### Docs

| Item | Location |
|------|----------|
| **Architecture spec** | [docs/PEARL_NEWS_ARCHITECTURE_SPEC.md](./PEARL_NEWS_ARCHITECTURE_SPEC.md) — Pipeline, atoms, templates, config, governance |
| **Article metadata schema (doc)** | [docs/PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md](./PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md) — Frozen metadata contract for `article_metadata.jsonl`; required keys, governance use |
| **GitHub scheduling** | [docs/PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md) — Scheduled pipeline runs, WordPress posting, GitHub Actions, secrets |
| **Minimal prod checklist** | [docs/PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md](./PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md) — Code/tests must-pass + 6 operational gates; pre-merge verification, rollback procedure |
| **GO/NO-GO checklist** | [docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md) — Production 100% gates: networked run, CI green, signed checklist with evidence |
| **Hardening 100%** | [docs/PEARL_NEWS_HARDENING_100_PERCENT.md](./PEARL_NEWS_HARDENING_100_PERCENT.md) — URL normalization, one-command runner, CI preflight, evidence bundle |
| **Writer spec** | `docs/PEARL_NEWS_WRITER_SPEC.md` ⚠️ *file not present* — Voice, atom types, 4-layer blend, quality gates, template guidance |
| **Pearl News README** | [pearl_news/README.md](../pearl_news/README.md) — Quick start, structure, one-command run |
| **Publish README** | [pearl_news/publish/README.md](../pearl_news/publish/README.md) — WordPress credentials, article format, posting script |
| **Pipeline README** | [pearl_news/pipeline/README.md](../pearl_news/pipeline/README.md) — Pipeline stages, usage |
| **Atoms README** | [pearl_news/atoms/README.md](../pearl_news/atoms/README.md), [pearl_news/atoms/youth_impact/README.md](../pearl_news/atoms/youth_impact/README.md), [pearl_news/atoms/sdg_un_refs/README.md](../pearl_news/atoms/sdg_un_refs/README.md) |
| **Governance README** | [pearl_news/governance/README.md](../pearl_news/governance/README.md) |
| **WordPress env example** | `docs/pearl_news_wordpress_env.example` — Placeholder env var names for WordPress (create from repo template if missing) |

### Scripts

| Item | Location |
|------|----------|
| **Run article pipeline** | [pearl_news/pipeline/run_article_pipeline.py](../pearl_news/pipeline/run_article_pipeline.py) — `python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts`; `--limit`, `--per-feed-limit`, `--no-filter-qc` |
| **Networked run + evidence** | [scripts/pearl_news_networked_run_and_evidence.sh](../scripts/pearl_news_networked_run_and_evidence.sh) — Live feed run; writes `artifacts/pearl_news/evaluation/networked_run_evidence.json` |
| **Post to WordPress** | [scripts/pearl_news_post_to_wp.py](../scripts/pearl_news_post_to_wp.py) — `--article <path>`, `--status draft|publish`, `--dry-run` |
| **Do-it script** | [scripts/pearl_news_do_it.sh](../scripts/pearl_news_do_it.sh) — Convenience runner; optional `--post` |

### Pipeline modules

| Item | Location |
|------|----------|
| **Feed ingest** | [pearl_news/pipeline/feed_ingest.py](../pearl_news/pipeline/feed_ingest.py) — Ingest RSS/Atom from feeds.yaml |
| **Topic/SDG classifier** | [pearl_news/pipeline/topic_sdg_classifier.py](../pearl_news/pipeline/topic_sdg_classifier.py) — topic, primary_sdg, sdg_labels, un_body from sdg_news_topic_mapping.yaml |
| **Template selector** | [pearl_news/pipeline/template_selector.py](../pearl_news/pipeline/template_selector.py) — template_id per item from article_templates_index |
| **Article assembler** | [pearl_news/pipeline/article_assembler.py](../pearl_news/pipeline/article_assembler.py) — Fills template slots (news + teacher + youth + SDG); appends disclaimer |
| **Quality gates** | [pearl_news/pipeline/quality_gates.py](../pearl_news/pipeline/quality_gates.py) — 5 fail-hard gates: fact_check, youth_specificity, sdg_accuracy, promotional, un_endorsement |
| **QC checklist** | [pearl_news/pipeline/qc_checklist.py](../pearl_news/pipeline/qc_checklist.py) — Runs gates; optionally filter to passed-only |
| **WordPress client** | [pearl_news/publish/wordpress_client.py](../pearl_news/publish/wordpress_client.py) — REST API client; env-based credentials; appends legal disclaimer |

### Config

| Item | Location |
|------|----------|
| **Feeds** | [pearl_news/config/feeds.yaml](../pearl_news/config/feeds.yaml) — UN News RSS URLs, refresh_minutes |
| **SDG/news topic mapping** | [pearl_news/config/sdg_news_topic_mapping.yaml](../pearl_news/config/sdg_news_topic_mapping.yaml) — topic → primary_sdg, sdg_labels, un_body |
| **Article templates index** | [pearl_news/config/article_templates_index.yaml](../pearl_news/config/article_templates_index.yaml) — template_id → template file |
| **Legal boundary** | [pearl_news/config/legal_boundary.yaml](../pearl_news/config/legal_boundary.yaml) — Mandatory disclaimers, UN-affiliation blocklist |
| **Editorial firewall** | [pearl_news/config/editorial_firewall.yaml](../pearl_news/config/editorial_firewall.yaml) — Labeling (news vs commentary), source requirements |
| **Template diversity** | [pearl_news/config/template_diversity.yaml](../pearl_news/config/template_diversity.yaml) — Content signatures, caps on repeated patterns |
| **Quality gates** | [pearl_news/config/quality_gates.yaml](../pearl_news/config/quality_gates.yaml) — 5 gate definitions |
| **LLM safety** | [pearl_news/config/llm_safety.yaml](../pearl_news/config/llm_safety.yaml) — Allowed tasks, gating for full article generation |
| **Teacher topic expertise** | [pearl_news/config/teacher_topic_expertise.yaml](../pearl_news/config/teacher_topic_expertise.yaml) — Teacher–topic mapping for assembly |

### Article templates

| Item | Location |
|------|----------|
| **Hard news + spiritual response** | [pearl_news/article_templates/hard_news_spiritual_response.yaml](../pearl_news/article_templates/hard_news_spiritual_response.yaml) |
| **Youth feature** | [pearl_news/article_templates/youth_feature.yaml](../pearl_news/article_templates/youth_feature.yaml) |
| **Interfaith dialogue report** | [pearl_news/article_templates/interfaith_dialogue_report.yaml](../pearl_news/article_templates/interfaith_dialogue_report.yaml) |
| **Explainer/context** | [pearl_news/article_templates/explainer_context.yaml](../pearl_news/article_templates/explainer_context.yaml) |
| **Commentary** | [pearl_news/article_templates/commentary.yaml](../pearl_news/article_templates/commentary.yaml) |

### Governance (pearl_news)

| Item | Location |
|------|----------|
| **Governance page** | [pearl_news/governance/GOVERNANCE_PAGE.md](../pearl_news/governance/GOVERNANCE_PAGE.md) |
| **Editorial standards** | [pearl_news/governance/EDITORIAL_STANDARDS.md](../pearl_news/governance/EDITORIAL_STANDARDS.md) |
| **Corrections policy** | [pearl_news/governance/CORRECTIONS_POLICY.md](../pearl_news/governance/CORRECTIONS_POLICY.md) |
| **Conflict of interest** | [pearl_news/governance/CONFLICT_OF_INTEREST_POLICY.md](../pearl_news/governance/CONFLICT_OF_INTEREST_POLICY.md) |

### Tests

| Item | Location |
|------|----------|
| **Pipeline E2E** | [tests/test_pearl_news_pipeline_e2e.py](../tests/test_pearl_news_pipeline_e2e.py) — Classify, select, assemble, gates, QC with fake items |
| **Quality gates minimal** | [tests/test_pearl_news_quality_gates_minimal.py](../tests/test_pearl_news_quality_gates_minimal.py) — run_quality_gates unit tests |

### Artifacts

| Item | Location |
|------|----------|
| **Drafts** | `artifacts/pearl_news/drafts/` — article_<id>.json, ingest_manifest.json, build_manifests.json, feed_item_<id>.json |
| **Networked run evidence** | `artifacts/pearl_news/evaluation/networked_run_evidence.json` — Evidence for production 100% (from pearl_news_networked_run_and_evidence.sh) |

### CI / workflows

| Item | Location |
|------|----------|
| **Pearl News gates** | [.github/workflows/pearl_news_gates.yml](../.github/workflows/pearl_news_gates.yml) — On push/PR to main (pearl_news/**, test files); runs pytest for test_pearl_news_quality_gates_minimal, test_pearl_news_pipeline_e2e |
| **Pearl News scheduled** | [.github/workflows/pearl_news_scheduled.yml](../.github/workflows/pearl_news_scheduled.yml) — Scheduled/manual run: pipeline → drafts → optional WordPress dry-run; uploads artifact pearl_news_drafts |

---

## Governance

- [docs/PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md](./PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md) — North-star governance at 24-brand scale
- [docs/PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md](./PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md) — Minimum governance core
- [docs/GOVERNANCE_HARDENING_BLUEPRINT.md](./GOVERNANCE_HARDENING_BLUEPRINT.md) — Candidate controls backlog (reference only, non-authoritative)
- [docs/governance/registry_integrity_checker_v1.md](./governance/registry_integrity_checker_v1.md) — Registry integrity checker

---

## Brand & release

- [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md) — Release velocity and schedule
- [docs/PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md](./PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md) — Platform hardening phases

---

## Church & payout (distribution-only brands)

Church brands (e.g. NorCal Dharma) are identity/distribution only: no teacher, no Teacher Mode, no wave allocation. Display name from church YAML at runtime. **NorCal Dharma brand integration** is production-ready when [Brand guards](../.github/workflows/brand-guards.yml) is green on `main`: CI guards (matrix exclusion + assignments → default_teacher), secret scan on brand config, and runtime smoke tests pass.

### Church docs

- [docs/church_docs/README.md](./church_docs/README.md) — Church–brand linkage: brand_id → church record mapping, display name source, Cooperative Church Compliance YAML Schema reference, ops smoke
- `docs/norcal_dharma.yaml` ⚠️ *file not present* — Church #1 canonical record (Cooperative Church Compliance YAML Schema)
- [docs/adr/ADR-002-distribution-only-church-brand.md](./adr/ADR-002-distribution-only-church-brand.md) — Distribution-only church brand policy

### Config (church / brand-only)

| Item | Location |
|------|----------|
| **Brand registry (norcal_dharma)** | [config/brand_registry.yaml](../config/brand_registry.yaml) — `norcal_dharma` entry: lifecycle, catalog_id, locale, family_allowlist; no teacher |
| **Locale extension (norcal_dharma)** | [config/localization/brand_registry_locale_extension.yaml](../config/localization/brand_registry_locale_extension.yaml) — `norcal_dharma`: locale en-US, territory US |
| **Brand–teacher assignments** | [config/catalog_planning/brand_teacher_assignments.yaml](../config/catalog_planning/brand_teacher_assignments.yaml) — `norcal_dharma` → `teacher_id: default_teacher` only; never in brand_teacher_matrix |

### Scripts & CI

- [scripts/ci/check_norcal_dharma_brand_guards.py](../scripts/ci/check_norcal_dharma_brand_guards.py) — **Dual guard:** (1) `norcal_dharma` must NOT appear in any `brand_teacher_matrix_*.yaml`; (2) in brand_teacher_assignments.yaml every row with `brand_id: norcal_dharma` must have `teacher_id: default_teacher`
- [scripts/ci/check_church_yaml_no_sensitive_tokens.py](../scripts/ci/check_church_yaml_no_sensitive_tokens.py) — Church YAMLs (and brand config when passed via `--files`) must not contain ssn, account_number, etc.; used in brand-guards workflow for secret scan on brand_registry, locale_extension, brand_teacher_assignments
- [scripts/ops/smoke_church_brand_resolution.py](../scripts/ops/smoke_church_brand_resolution.py) — Ops smoke: brand_id → church.short_name across all church brands
- [phoenix_v4/ops/church_loader.py](../phoenix_v4/ops/church_loader.py) — `load_church(brand_id)`, `get_church_display_name(brand_id)`; fail-fast when missing/invalid

### Tests

- [tests/test_norcal_dharma_brand_smoke.py](../tests/test_norcal_dharma_brand_smoke.py) — Runtime smoke: wave allocation does not allocate norcal_dharma; `--brand norcal_dharma` resolves to default_teacher and does not enter Teacher Mode

### CI / workflow

- [.github/workflows/brand-guards.yml](../.github/workflows/brand-guards.yml) — **Brand guards:** on push/PR to main when brand registry, locale extension, or catalog_planning brand_teacher_* change. Runs: check_norcal_dharma_brand_guards.py, check_church_yaml_no_sensitive_tokens.py (on brand config files), pytest test_norcal_dharma_brand_smoke.py

---

## Book & authoring

- [docs/BOOK_001_ASSEMBLY_CONTRACT.md](./BOOK_001_ASSEMBLY_CONTRACT.md) — V4.5 locked assembly contract for Book_001
- [docs/BOOK_001_FREEZE.md](./BOOK_001_FREEZE.md) — Book_001 freeze
- [docs/BOOK_001_READINESS_CHECKLIST.md](./BOOK_001_READINESS_CHECKLIST.md) — Book_001 readiness checklist
- [docs/BOOK_001_POST_MORTEM.md](./BOOK_001_POST_MORTEM.md) — Book_001 post-mortem
- [docs/authoring/AUTHOR_ASSET_WORKBOOK.md](./authoring/AUTHOR_ASSET_WORKBOOK.md) — Author asset workbook
- [docs/WRITER_BRIEF_BOOK_001.md](./WRITER_BRIEF_BOOK_001.md) — Writer brief for Book_001
- [docs/WRITER_COMMS_SYSTEMS_100.md](./WRITER_COMMS_SYSTEMS_100.md) — Writer comms systems
- [docs/WRITER_SPEC_MARKDOWN_AND_DOCX.md](./WRITER_SPEC_MARKDOWN_AND_DOCX.md) — Writer spec (Markdown and DOCX)
- [docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) — First 10 books evaluation protocol

---

## Enlightened Intelligence (EI)

EI is 100% at **test slice** when the 4 targeted unit tests pass. It is **100% production-ready** only when all operational gates are confirmed on `main` with evidence links (see [ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md](./ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md)).

### Operational gates (production 100%)

1. Merge to `main`
2. CI green on `main`
3. Runtime/scheduled smoke passes
4. Secrets (embedding/LLM API keys if used) verified
5. Checklist doc completed with evidence links
6. Rollback procedure validated

### EI docs

- [docs/ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md](./ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md) — **Production checklist:** test slice (4 tests) + 6 operational gates. Pre-merge verification, rollback procedure
- `config/source_of_truth/enlightened_intelligence_registry.yaml` ⚠️ *file not present* — EI registry: slots, llm_judge, embeddings, teacher_integrity

---

## Manuscript quality (Tier 0 contract)

**Feature = complete.** Tier 0 contract, canary gate, and trend dashboard are implemented. **Production 100%** requires the full operational checklist: CI/release gates on `main`, branch protection, smoke runs, evidence, rollback proof. See `docs/PRODUCTION_READINESS_GO_NO_GO.md` ⚠️ *file not present*, `docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md` ⚠️ *file not present*.

### Document all

| Item | Location |
|------|----------|
| **Checklist (Tier 0–4, canary, verification)** | [docs/MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md](./MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md) |
| **Tier 0 contract config** | `config/quality/tier0_book_output_contract.yaml` ⚠️ *file not present* |
| **Canary config** | `config/quality/canary_config.yaml` ⚠️ *file not present* |
| **Tier 0 checker** | `scripts/ci/check_book_output_tier0_contract.py` ⚠️ *file not present* |
| **Trend dashboard** | `scripts/ci/tier0_trend.py` ⚠️ *file not present* — violations over time; observability add-on, not a production gate |
| **Canary script** | `scripts/ci/run_canary_100_books.py` ⚠️ *file not present* |
| **Tests** | [tests/test_book_pass_gate.py](../tests/test_book_pass_gate.py) |
| **Release checklist (item 12)** | `docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md` ⚠️ *file not present* — block release on Tier 0 fail |

---

## Writing & content quality

- [docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md](./writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md) — Golden Phoenix atom upgrade guide
- [docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md](./HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md) — High-impact story atom upgrade rubric
- [docs/CREATIVE_QUALITY_GATE_V1.md](./CREATIVE_QUALITY_GATE_V1.md) — Creative quality gate v1
- [docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md](./CREATIVE_QUALITY_VALIDATION_CHECKLIST.md) — Creative quality validation checklist
- [docs/INSIGHT_DENSITY_ANALYZER.md](./INSIGHT_DENSITY_ANALYZER.md) — Insight density analyzer (prevents generic prose)
- [docs/NARRATIVE_TENSION_VALIDATOR.md](./NARRATIVE_TENSION_VALIDATOR.md) — Narrative tension validator (prevents flat arcs)
- [docs/SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md](./SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md) — Simplified emotional impact scoring
- [docs/UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md](./UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md) — Unified personas book readiness analysis

---

## Atoms & formats

- [docs/ATOM_NATIVE_MODULAR_FORMATS.md](./ATOM_NATIVE_MODULAR_FORMATS.md) — Atom-native modular formats (no long-form cohesion required)
- [docs/INTRO_AND_CONCLUSION_SYSTEM.md](./INTRO_AND_CONCLUSION_SYSTEM.md) — Intro and conclusion system
- [docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md](./PRACTICE_LIBRARY_TEACHER_FALLBACK.md) — Practice library teacher fallback
- [docs/TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md) — Teacher mode system reference

---

## Mechanism alias system (document all)

Persona × topic–specific metaphor aliases that replace the generic "the mechanism" throughout rendered prose. Introduced once per book in a NAMING beat (Chapter 1, after HOOK); resolved automatically at render time via `{{MA}}` token substitution. Covers 12 personas × up to 16 topics = 176 alias files.

### Config

| Item | Location |
|------|----------|
| **Schema** | [config/source_of_truth/mechanism_aliases/_schema.yaml](../config/source_of_truth/mechanism_aliases/_schema.yaml) — Fields: `short_form`, `descriptor`, `naming_moment`, `forms` |
| **Naming template** | [config/source_of_truth/mechanism_aliases/_naming_template.md](../config/source_of_truth/mechanism_aliases/_naming_template.md) — Chapter 1 NAMING beat structure; bridge sentence format |
| **Alias files (all personas)** | `config/source_of_truth/mechanism_aliases/{persona}/{topic}.yaml` — 176 files across gen_alpha_students, gen_z_professionals, gen_x_sandwich, corporate_managers, healthcare_rns, tech_finance_burnout, entrepreneurs, millennial_women_professionals, nyc_executives, working_parents, first_responders, educators |

### Renderer integration

| Item | Location |
|------|----------|
| **Book renderer** | [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py) — `_load_mechanism_alias()`, `_resolve_mechanism_alias_tokens()`, `_build_naming_moment_block()`; auto-substitutes "the mechanism" → alias short_form for all existing atoms |
| **Token reference** | `{{MA}}` = short_form, `{{MA_DEF}}` = descriptor, `{{MA_FULL}}` = full naming_moment paragraph |

### Alias short-forms reference (selected)

| Persona × Topic | Alias |
|-----------------|-------|
| gen_alpha_students × anxiety | the notification spiral |
| gen_alpha_students × overthinking | the draft that never sends |
| gen_z_professionals × anxiety | the twenty apps open |
| gen_z_professionals × burnout | the side hustle that became everything |
| gen_x_sandwich × burnout | the second shift |
| corporate_managers × imposter_syndrome | the board meeting you didn't call |
| healthcare_rns × compassion_fatigue | the chart that stopped being a person |
| tech_finance_burnout × depression | the dashboard with no green |
| entrepreneurs × imposter_syndrome | the doubt investor |
| first_responders × compassion_fatigue | the numbering |

---

## Delivery pipeline (document all)

Clean epub/TTS-ready output pipeline with delivery contract gate, word-count gate, and slot-level budget telemetry.

### Renderer

| Item | Location |
|------|----------|
| **Book renderer** | [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py) — `clean_for_delivery()`, `delivery_contract_gate()`, `word_count_gate()`, `_build_deficit_report()`, mechanism alias injection |
| **Prose resolver** | [phoenix_v4/rendering/prose_resolver.py](../phoenix_v4/rendering/prose_resolver.py) — Atom prose lookup, placeholder/silence handling |
| **Renderer init** | [phoenix_v4/rendering/__init__.py](../phoenix_v4/rendering/__init__.py) — Public API: `render_book()` |

### Pipeline CLI

| Item | Location |
|------|----------|
| **Run pipeline** | [scripts/run_pipeline.py](../scripts/run_pipeline.py) — Full 6-stage pipeline: BookSpec → FormatPlan → CompiledBook → render. Flags: `--topic`, `--persona`, `--arc`, `--structural-format`, `--runtime-format`, `--render-book`, `--render-formats`, `--skip-word-count-gate`, `--generate-freebies` |
| **Render plan to txt** | [scripts/render_plan_to_txt.py](../scripts/render_plan_to_txt.py) — Standalone render from saved plan JSON |

### Delivery contract gate (forbidden patterns)

Patterns that must never survive into output (hard-fail on `delivery_contract_gate()`): `---` dividers, `===CHAPTER` scaffolds, `mode:`, `reframe_type:`, `weight:`, `family:`, `voice_mode:`, `carry_line:`, unresolved `{variable}` placeholders.

### Word-count gate & budget telemetry

| Item | Notes |
|------|-------|
| **Gate** | `word_count_gate()` in book_renderer.py — fails build if word count < `word_range` min for runtime format. Bypass with `--skip-word-count-gate` |
| **Budget report** | `budget.json` written alongside every rendered book — per-chapter, per-slot word counts, deficit vs. target, slot_totals |
| **Runtime formats** | Defined in [config/format_selection/format_registry.yaml](../config/format_selection/format_registry.yaml) — includes `deep_book_6h`: 360 min, 24 chapters default, 52,000–58,000 words |

### Artifacts (rendered books)

| Item | Location |
|------|----------|
| **gen_alpha × anxiety 6hr book (with alias)** | `artifacts/gen_alpha_anxiety_6hr_book_with_alias.txt` |
| **gen_alpha × anxiety 6hr book** | `artifacts/gen_alpha_anxiety_6hr_book.txt` |
| **gen_alpha × anxiety budget** | `artifacts/gen_alpha_anxiety_6hr_budget.json` |
| **gen_alpha × anxiety plan** | `artifacts/gen_alpha_anxiety_6hr_plan.json` |
| **Rendered book directory** | `artifacts/rendered/{hash}/book.txt` + `budget.json` |

---

## Master arcs

Pre-authored chapter-level emotional arcs that drive the Arc-First pipeline. `chapter_count` in the arc overrides the format plan default.

| Item | Location |
|------|----------|
| **Arc README** | [config/source_of_truth/master_arcs/README.md](../config/source_of_truth/master_arcs/README.md) |
| **Arc files** | `config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__{format}.yaml` — 24-chapter arcs; BAND values 2–4 only; max 3 consecutive same BAND; emotional_role_sequence constraints |
| **gen_alpha × anxiety × spiral × F013** | `config/source_of_truth/master_arcs/gen_alpha_students__anxiety__spiral__F013.yaml` — 24-chapter Before/During/After arc; `arc_id: gen_alpha_students_anxiety_spiral_F013_6h` |

### Arc validation rules

- BAND values: RECOGNITION 2,2,3,3,4 | MECHANISM_PROOF 3,3,4,4,3 | TURNING_POINT all 3 | EMBODIMENT 2,1,2,1,1
- No BAND 1 or 5 in atom pools; arc must use only 2–4
- Max 3 consecutive same BAND value
- Max 2 consecutive same emotional_role in sequence

---

## Atom coverage

| Item | Location |
|------|----------|
| **Coverage test (450/450)** | [tests/test_atoms_coverage_100_percent.py](../tests/test_atoms_coverage_100_percent.py) — Verifies all persona × topic × pool combos have CANONICAL.txt files; EXIT:0 = 100% |
| **Atoms root** | `atoms/{persona}/{topic}/{POOL}/CANONICAL.txt` — Pools: STORY (per engine), HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION, COMPRESSION |
| **Atoms index** | [atoms/INDEX.md](../atoms/INDEX.md) |
| **Identity aliases** | `config/identity_aliases.yaml` — maps topic aliases to canonical directories |
| **Intro/ending variation** | [config/source_of_truth/intro_ending_variation.yaml](../config/source_of_truth/intro_ending_variation.yaml) — `intro_ending_variation_enabled: true` |

---

## Teacher Mode & production readiness (document all)

Teacher Mode is **100% production-ready** when: (1) strict validation and CI gates pass on `main`, (2) E2E Teacher Mode compile smoke tests pass for all teachers, (3) release path uses only approved assets (no fallback/missing-atom warnings), (4) evidence is archived, (5) branch protection requires Teacher gates. See [TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md).

### Docs

| Item | Location |
|------|----------|
| **Teacher production readiness** | [docs/TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md) — Gates, E2E smoke, release path, evidence, branch protection |
| **Teacher mode system reference** | [docs/TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md) — Coverage gate, doctrine, approved_atoms, config |
| **Practice library teacher fallback** | [docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md](./PRACTICE_LIBRARY_TEACHER_FALLBACK.md) — EXERCISE fallback when teacher pool is non-empty but smaller than required |

### Scripts

| Item | Location |
|------|----------|
| **Teacher production gates** | [scripts/ci/run_teacher_production_gates.py](../scripts/ci/run_teacher_production_gates.py) — Doctrine schema + teacher readiness (+ optional synthetic governance with `--plan`) |
| **Doctrine schema check** | [scripts/ci/check_doctrine_schema.py](../scripts/ci/check_doctrine_schema.py) — Gate N: doctrine.yaml allowlist/required keys; `--teacher <id>` |
| **Teacher readiness** | [scripts/ci/check_teacher_readiness.py](../scripts/ci/check_teacher_readiness.py) — Min EXERCISE/STORY (and optional HOOK/REFLECTION/INTEGRATION); `--teacher <id>`, `--min-exercise`, etc. |
| **Teacher synthetic governance** | [scripts/ci/check_teacher_synthetic_governance.py](../scripts/ci/check_teacher_synthetic_governance.py) — No placeholders; synthetic ratio caps; teacher_sourced ratio min; `--out` |
| **F006 slot stubs** | [scripts/teacher_stub_f006_slots.py](../scripts/teacher_stub_f006_slots.py) — Generate candidate HOOK, SCENE, REFLECTION, INTEGRATION, COMPRESSION stubs (20 per slot) for teachers missing F006 coverage |

### Tests

| Item | Location |
|------|----------|
| **Teacher Arc unit tests** | [tests/teacher_arc_test.py](../tests/teacher_arc_test.py) — Blueprint schema, planner determinism, golden teacher blueprint shape |
| **Teacher Mode E2E smoke** | [tests/test_teacher_mode_e2e_smoke.py](../tests/test_teacher_mode_e2e_smoke.py) — One topic/persona/arc per teacher; coverage-gate or full compile |

### Config

| Item | Location |
|------|----------|
| **Teacher registry** | [config/teachers/teacher_registry.yaml](../config/teachers/teacher_registry.yaml) — Canonical list: display_name, kb_id, doctrine_profile, allowed_topics, allowed_engines, teacher_mode_defaults |
| **Per-teacher config** | `config/teachers/<teacher_id>.yaml` — Quality profile, exercise fallback, wrappers, teacher_conclusion |
| **Teacher banks** | `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/` — raw/, doctrine/, kb/, candidate_atoms/, approved_atoms/, artifacts/ |

### CI / workflow

| Item | Location |
|------|----------|
| **Teacher gates workflow** | [.github/workflows/teacher-gates.yml](../.github/workflows/teacher-gates.yml) — On teacher-related path changes: run_teacher_production_gates.py, pytest teacher_arc_test, pytest test_teacher_mode_e2e_smoke. **Required status check for branch protection.** |

### Artifacts

| Item | Location |
|------|----------|
| **Teacher coverage report** | `artifacts/teacher_coverage_report.json` — Gap report when coverage gate fails |
| **Teacher synthetic report** | `artifacts/teacher_synthetic_report.json` — From check_teacher_synthetic_governance.py when `--plan` used |
| **Gates / E2E logs** | `artifacts/logs/teacher_production_gates.log`, `artifacts/logs/teacher_e2e_smoke.log` — Archive for evidence |

---

## Tests (full inventory)

All test files under `tests/`. Two are required status checks; remainder are available for CI expansion.

| Test file | Purpose |
|-----------|---------|
| [tests/teacher_arc_test.py](../tests/teacher_arc_test.py) | Teacher arc blueprint schema, planner determinism (**required**) |
| [tests/test_teacher_mode_e2e_smoke.py](../tests/test_teacher_mode_e2e_smoke.py) | Teacher Mode E2E compile per teacher (**required**) |
| [tests/test_atoms_coverage_100_percent.py](../tests/test_atoms_coverage_100_percent.py) | 450/450 atom pool coverage gate — EXIT:0 = 100% |
| [tests/test_arc_loader.py](../tests/test_arc_loader.py) | Arc YAML loading and validation |
| [tests/test_assembly_compiler.py](../tests/test_assembly_compiler.py) | Assembly compiler unit tests |
| [tests/test_atoms_model.py](../tests/test_atoms_model.py) | Atom data model and pool indexing |
| [tests/test_book_pass_gate.py](../tests/test_book_pass_gate.py) | Book-level pass gate (Tier 0 contract) |
| [tests/test_book_renderer.py](../tests/test_book_renderer.py) | Renderer: clean_for_delivery, delivery_contract_gate, word_count_gate |
| [tests/test_brand_identity_stability.py](../tests/test_brand_identity_stability.py) | Brand identity stability across builds |
| [tests/test_catalog_emotional_distribution.py](../tests/test_catalog_emotional_distribution.py) | Emotional distribution across catalog |
| [tests/test_chapter_flow_gate.py](../tests/test_chapter_flow_gate.py) | Chapter-level flow gate |
| [tests/test_creative_quality_v1.py](../tests/test_creative_quality_v1.py) | Creative quality gate v1 |
| [tests/test_cross_brand_divergence.py](../tests/test_cross_brand_divergence.py) | Cross-brand divergence validation |
| [tests/test_emotional_curve_golden.py](../tests/test_emotional_curve_golden.py) | Emotional curve golden regression |
| [tests/test_format_selector.py](../tests/test_format_selector.py) | Format selector Stage 2 logic |
| [tests/test_intro_ending_variation.py](../tests/test_intro_ending_variation.py) | Intro/ending variation feature flag |
| [tests/test_narrative_gates.py](../tests/test_narrative_gates.py) | Narrative gate checks |
| [tests/test_norcal_dharma_brand_smoke.py](../tests/test_norcal_dharma_brand_smoke.py) | NorCal Dharma church brand smoke |
| [tests/test_pearl_news_pipeline_e2e.py](../tests/test_pearl_news_pipeline_e2e.py) | Pearl News E2E pipeline |
| [tests/test_pearl_news_quality_gates_minimal.py](../tests/test_pearl_news_quality_gates_minimal.py) | Pearl News quality gates minimal |
| [tests/test_platform_health_scorecard.py](../tests/test_platform_health_scorecard.py) | Platform health scorecard |
| [tests/test_prepublish_gates.py](../tests/test_prepublish_gates.py) | Pre-publish gate checks |
| [tests/test_prepublish_series_wiring.py](../tests/test_prepublish_series_wiring.py) | Pre-publish series wiring validation |
| [tests/test_quality_regression.py](../tests/test_quality_regression.py) | Quality regression golden set |
| [tests/test_release_wave_controls.py](../tests/test_release_wave_controls.py) | Release wave controls |
| [tests/test_series_mode_planner.py](../tests/test_series_mode_planner.py) | Series mode planner |
| [tests/test_series_quality_gates.py](../tests/test_series_quality_gates.py) | Series quality gates |
| [tests/test_slot_resolver.py](../tests/test_slot_resolver.py) | Slot resolver unit tests |
| [tests/test_template_selector.py](../tests/test_template_selector.py) | Template selector |
| [tests/test_topic_sdg_classifier.py](../tests/test_topic_sdg_classifier.py) | Topic SDG classifier |
| [tests/test_validate_series_diversity.py](../tests/test_validate_series_diversity.py) | Series diversity validation |
| [tests/test_validators.py](../tests/test_validators.py) | Core validators |
| [tests/test_variation.py](../tests/test_variation.py) | Variation knob distribution |
| [tests/test_wave_optimizer_constraint_solver.py](../tests/test_wave_optimizer_constraint_solver.py) | Wave optimizer constraint solver |

---

## Coverage & ops

- [docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md](./TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md) — Tuple viability and coverage health (preflight gate, weekly report)
- [docs/COVERAGE_HEALTH_JSON_SCHEMA.md](./COVERAGE_HEALTH_JSON_SCHEMA.md) — Coverage health JSON dashboard schema
- [docs/TITLE_AND_CATALOG_MARKETING_SYSTEM.md](./TITLE_AND_CATALOG_MARKETING_SYSTEM.md) — Title and catalog marketing system
- [docs/PHASE_13_C_WAVE_OPTIMIZER.md](./PHASE_13_C_WAVE_OPTIMIZER.md) — Phase 13 C wave optimizer
- [docs/V4_FEATURES_SCALE_AND_KNOBS.md](./V4_FEATURES_SCALE_AND_KNOBS.md) — V4 features, scale, and knobs

---

## Email sequences

- [docs/email_sequences/README.md](./email_sequences/README.md) — Email sequences overview (Formspree, MailerLite, freebie landing pages)
- [docs/email_sequences/5-email-welcome-sequence.md](./email_sequences/5-email-welcome-sequence.md) — 5-email welcome sequence master
- [docs/email_sequences/persona-variants.md](./email_sequences/persona-variants.md) — Persona variants (Executive / Gen Z / Healthcare)
- [docs/email_sequences/exercise-one-liners.md](./email_sequences/exercise-one-liners.md) — Per-exercise copy (subject lines, opening lines)
- [docs/email_sequences/FORMSPREE_SETUP.md](./email_sequences/FORMSPREE_SETUP.md) — Formspree setup

---

## Phoenix Churches Payout System (document all)

Biweekly payouts for 24 churches; Plaid sync, Bluevine, 90/10 split, human-in-the-loop execution. ⚠️ **Most payout files not present in repo** — spec and config referenced below, implementation files missing.

### Spec & checklist

- `specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md` ⚠️ *file not present* — Tech spec: architecture, data model, workflow, compensating controls
- [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md) — What you must give: Plaid credentials, 24 bank connections, Bluevine last4, payee info

### Config

- `config/payouts/churches.yaml` ⚠️ *file not present* — Church registry (24 churches; bluevine_account_last4, payee_id, rules)
- `config/payouts/payees.yaml` ⚠️ *file not present* — Payee registry (24 payees; display_name, bank_last4)
- `config/payouts/credentials.yaml.example` ⚠️ *file not present* — Credentials template (plaid, access_tokens; copy to credentials.yaml)
- `config/payouts/fill_template.csv` ⚠️ *file not present* — CSV template for batch-filling church + payee info

### Package & CLI

All payout package files (`payouts/cli.py`, `payouts/setup.py`, `payouts/plaid_sync.py`, etc.) ⚠️ *not present in repo* — see spec for planned structure.

### Artifacts (gitignored)

- `payouts/ledger.db` — Ledger database
- `artifacts/payouts/` — Batch exports (BATCH_*_BATCH_SUMMARY.csv, BATCH_*_PAYOUT_ITEMS.csv)
- `config/payouts/credentials.yaml` — Secrets (not committed)

---

## Translation, validation & multilingual

Translation and validation pipeline: parallel sharded translation (atoms + exercises) to all locales (zh_CN, zh_TW, zh_HK, zh_SG, yue, ja_JP, ko_KR), deterministic validation (schema, locale script, coverage, meta/leakage, repetition), merge + global QA, golden regression. ⚠️ **Several translation files not present** — see ⚠️ markers.

### Docs

| Item | Location |
|------|----------|
| **Locale prose & prompting** | `docs/LOCALE_PROSE_AND_PROMPTING.md` ⚠️ *file not present* |
| **Multilingual architecture** | `docs/MULTILINGUAL_ARCHITECTURE.md` ⚠️ *file not present* |
| **Korean market & prose** | `docs/KOREA_MARKET_AND_PROSE.md` ⚠️ *file not present* |
| **Japanese market self-help** | `docs/JAPANESE_MARKET_SELFHELP_GUIDE.md` ⚠️ *file not present* |

### Scripts

| Item | Location |
|------|----------|
| **Translate atoms/exercises (cloud)** | `scripts/translate_atoms_all_locales_cloud.py` ⚠️ *file not present* |
| **Validate translations** | `scripts/validate_translations.py` ⚠️ *file not present* |
| **Merge translation shards** | `scripts/merge_translation_shards.py` ⚠️ *file not present* |
| **Golden translation regression** | `scripts/check_golden_translation.py` ⚠️ *file not present* |
| **Native prompts / eval / learn** | `scripts/native_prompts_eval_learn.py` ⚠️ *file not present* |

### Config & quality contracts

All quality_contracts/ files and `config/localization/content_roots_by_locale.yaml` ⚠️ *not present in repo*.

### CI / workflow

`github/workflows/translate-atoms-qwen-matrix.yml` ⚠️ *file not present*.

### Artifacts

| Item | Location |
|------|----------|
| **Shard output** | `{out_root}/{locale}/shard_{n}/` — exercises/*.json, atoms/*.json, shard_manifest.json |
| **Merged translations** | `{input_root}/{locale}/exercises/`, `{input_root}/{locale}/atoms/`, manifest.json at input root |

---

## Scripts — authoring, catalog & validation

All root-level `scripts/*.py` files confirmed present on disk.

| Script | Purpose |
|--------|---------|
| [scripts/run_pipeline.py](../scripts/run_pipeline.py) | Full 6-stage pipeline CLI — see Delivery pipeline section |
| [scripts/run_production_readiness_gates.py](../scripts/run_production_readiness_gates.py) | Production readiness gate runner |
| [scripts/render_plan_to_txt.py](../scripts/render_plan_to_txt.py) | Standalone render from saved plan JSON |
| [scripts/build_proof_chapter.py](../scripts/build_proof_chapter.py) | Build a single proof chapter from atoms + plan |
| [scripts/check_spec_version_bump.py](../scripts/check_spec_version_bump.py) | Verify spec version is bumped on breaking changes |
| [scripts/clean_atom_prose.py](../scripts/clean_atom_prose.py) | Batch clean atom prose files (strip metadata artifacts) |
| [scripts/compose_cohesive_chapter_from_plan.py](../scripts/compose_cohesive_chapter_from_plan.py) | Compose a cohesive chapter from a compiled plan JSON |
| [scripts/create_freebie_assets.py](../scripts/create_freebie_assets.py) | Generate freebie assets (PDFs, landing copy) from plan |
| [scripts/fill_non_story_coverage_gaps.py](../scripts/fill_non_story_coverage_gaps.py) | Fill missing HOOK/SCENE/REFLECTION/INTEGRATION/EXERCISE CANONICAL.txt files |
| [scripts/generate_arcs_from_backlog.py](../scripts/generate_arcs_from_backlog.py) | Batch-generate arc YAMLs from arc backlog config |
| [scripts/generate_full_catalog.py](../scripts/generate_full_catalog.py) | Generate full 1,008-title US catalog plan JSON |
| [scripts/generate_landing_pages.py](../scripts/generate_landing_pages.py) | Generate landing page HTML for each freebie |
| [scripts/generate_teacher_gap_atoms.py](../scripts/generate_teacher_gap_atoms.py) | Generate candidate atoms for teachers with pool gaps |
| [scripts/intake_teacher_ahjan.py](../scripts/intake_teacher_ahjan.py) | One-time intake: ingest Ahjan teacher KB and doctrine |
| [scripts/list_english_catalog_titles.py](../scripts/list_english_catalog_titles.py) | List all en-US catalog titles with topic/persona/engine |
| [scripts/pearl_news_post_to_wp.py](../scripts/pearl_news_post_to_wp.py) | Post Pearl News articles to WordPress via REST API |
| [scripts/plan_freebie_assets.py](../scripts/plan_freebie_assets.py) | Plan freebie asset set for a given book plan |
| [scripts/promote_approved_synthetic_atoms.py](../scripts/promote_approved_synthetic_atoms.py) | Promote reviewed synthetic atoms to approved_atoms/ |
| [scripts/run_golden_quality_path.py](../scripts/run_golden_quality_path.py) | Run the golden quality path: compile + render + gate |
| [scripts/teacher_integrity_dashboard.py](../scripts/teacher_integrity_dashboard.py) | Teacher integrity dashboard: doctrine drift, synthetic ratios |
| [scripts/teacher_integrity_report.py](../scripts/teacher_integrity_report.py) | Teacher integrity report: per-teacher compliance summary |
| [scripts/validate_and_stage_synthetic_atoms.py](../scripts/validate_and_stage_synthetic_atoms.py) | Validate synthetic atoms and stage approved ones |
| [scripts/validate_asset_store.py](../scripts/validate_asset_store.py) | Validate asset store structure and manifests |
| [scripts/validate_book_001_readiness.py](../scripts/validate_book_001_readiness.py) | Validate Book_001 readiness against assembly contract |
| [scripts/validate_canonical_sources.py](../scripts/validate_canonical_sources.py) | Validate canonical source YAML files for schema correctness |
| [scripts/validate_golden_plan.py](../scripts/validate_golden_plan.py) | Validate a golden plan JSON against compiled plan schema |

---

## Scripts/CI — content quality gates

All `scripts/ci/` files confirmed present on disk.

| Script | Purpose |
|--------|---------|
| [scripts/ci/check_docs_governance.py](../scripts/ci/check_docs_governance.py) | **DOCS_INDEX link integrity + Last updated staleness** — fails if any linked file is missing; warns on stale date |
| [scripts/ci/check_author_positioning.py](../scripts/ci/check_author_positioning.py) | Author positioning validation: pen name, bio, positioning consistency |
| [scripts/ci/check_book_output_no_placeholders.py](../scripts/ci/check_book_output_no_placeholders.py) | Hard-fail if any placeholder pattern survives rendered output |
| [scripts/ci/check_doctrine_drift.py](../scripts/ci/check_doctrine_drift.py) | Detect teacher doctrine drift vs approved baseline |
| [scripts/ci/check_doctrine_schema.py](../scripts/ci/check_doctrine_schema.py) | Doctrine YAML schema validation per teacher |
| [scripts/ci/check_export_no_bypass.py](../scripts/ci/check_export_no_bypass.py) | Verify export path cannot bypass release gates |
| [scripts/ci/check_platform_similarity.py](../scripts/ci/check_platform_similarity.py) | Cross-platform similarity: prevent near-duplicate titles across brands |
| [scripts/ci/check_prose_duplication.py](../scripts/ci/check_prose_duplication.py) | Prose duplication detector: flag atom-level repetition |
| [scripts/ci/check_series_content_uniqueness.py](../scripts/ci/check_series_content_uniqueness.py) | Series content uniqueness: no two books in a series share atoms |
| [scripts/ci/check_series_metadata_intent.py](../scripts/ci/check_series_metadata_intent.py) | Series metadata intent validation |
| [scripts/ci/check_series_open_close_collision.py](../scripts/ci/check_series_open_close_collision.py) | Series open/close collision: prevent reused intros/conclusions |
| [scripts/ci/check_structural_entropy.py](../scripts/ci/check_structural_entropy.py) | Structural entropy: detect low-variation chapter sequences |
| [scripts/ci/check_wave_density.py](../scripts/ci/check_wave_density.py) | Wave density: enforce release spacing and catalog balance |
| [scripts/ci/check_church_yaml_no_sensitive_tokens.py](../scripts/ci/check_church_yaml_no_sensitive_tokens.py) | Church YAML must not contain sensitive tokens (ssn, account_number, etc.) |
| [scripts/ci/check_norcal_dharma_brand_guards.py](../scripts/ci/check_norcal_dharma_brand_guards.py) | NorCal Dharma: (1) not in any brand_teacher_matrix; (2) assignments map only to default_teacher |
| [scripts/ci/check_teacher_readiness.py](../scripts/ci/check_teacher_readiness.py) | Teacher atom pool readiness: min EXERCISE/STORY counts |
| [scripts/ci/check_teacher_synthetic_governance.py](../scripts/ci/check_teacher_synthetic_governance.py) | Teacher synthetic governance: ratio caps, sourcing minimums |
| [scripts/ci/report_variation_knobs.py](../scripts/ci/report_variation_knobs.py) | Variation knob distribution report |
| [scripts/ci/run_prepublish_gates.py](../scripts/ci/run_prepublish_gates.py) | Run full pre-publish gate suite before any release |
| [scripts/ci/run_teacher_production_gates.py](../scripts/ci/run_teacher_production_gates.py) | Teacher production gate runner |
| [scripts/ci/update_similarity_index.py](../scripts/ci/update_similarity_index.py) | Rebuild cross-book similarity index after new releases |
| [scripts/ci/validate_ops_artifacts.py](../scripts/ci/validate_ops_artifacts.py) | Validate ops artifacts (plans, manifests) for schema compliance |
| [scripts/ci/validate_ops_registry_consistency.py](../scripts/ci/validate_ops_registry_consistency.py) | Ops registry consistency: wave, brand, teacher cross-checks |
| [scripts/ci/PREPUBLISH_CHECKLIST.md](../scripts/ci/PREPUBLISH_CHECKLIST.md) | Pre-publish human checklist: steps before running gates |
| [scripts/ci/export_scripts_registry.yaml](../scripts/ci/export_scripts_registry.yaml) | Registry of export scripts and their gate requirements |
| [scripts/systems_test/run_systems_test.py](../scripts/systems_test/run_systems_test.py) | Systems test phases 1–7 |

---

## Source of truth — style & composition configs

Config files in `config/source_of_truth/` that control prose style, chapter composition, and carry-line behavior.

| Config | Purpose |
|--------|---------|
| [config/source_of_truth/carry_line_styles.yaml](../config/source_of_truth/carry_line_styles.yaml) | Carry-line style variants per engine/tone |
| [config/source_of_truth/chapter_archetypes.yaml](../config/source_of_truth/chapter_archetypes.yaml) | Chapter archetype definitions (revelation, confrontation, turn, etc.) |
| [config/source_of_truth/chapter_planner_policies.yaml](../config/source_of_truth/chapter_planner_policies.yaml) | Chapter planner policies: slot assignment rules, budget constraints |
| [config/source_of_truth/integration_ending_styles.yaml](../config/source_of_truth/integration_ending_styles.yaml) | INTEGRATION slot ending style variants |
| [config/source_of_truth/opening_recognition_styles.yaml](../config/source_of_truth/opening_recognition_styles.yaml) | Opening recognition style variants for HOOK/SCENE |
| [config/source_of_truth/book_structure_archetypes.yaml](../config/source_of_truth/book_structure_archetypes.yaml) | Book-level structure archetypes |
| [config/source_of_truth/journey_shapes.yaml](../config/source_of_truth/journey_shapes.yaml) | Journey shape definitions |
| [config/source_of_truth/recurring_motif_bank.yaml](../config/source_of_truth/recurring_motif_bank.yaml) | Recurring motif bank |
| [config/source_of_truth/reframe_line_bank.yaml](../config/source_of_truth/reframe_line_bank.yaml) | Reframe line bank |
| [config/source_of_truth/section_reorder_modes.yaml](../config/source_of_truth/section_reorder_modes.yaml) | Section reorder modes |
| [config/source_of_truth/intro_ending_variation.yaml](../config/source_of_truth/intro_ending_variation.yaml) | Intro/ending variation feature flag (`intro_ending_variation_enabled: true`) |
| [config/source_of_truth/mechanism_aliases/_schema.yaml](../config/source_of_truth/mechanism_aliases/_schema.yaml) | Mechanism alias schema |
| [config/source_of_truth/mechanism_aliases/_naming_template.md](../config/source_of_truth/mechanism_aliases/_naming_template.md) | Mechanism alias naming template |

---

## Operations & infra

- [docs/GITHUB_BACKUP_SETUP.md](./GITHUB_BACKUP_SETUP.md) — GitHub backup setup
- [docs/QWEN_FORKS_AND_BACKUP.md](./QWEN_FORKS_AND_BACKUP.md) — Qwen forks and backup

---

## ADRs

- [docs/adr/README.md](./adr/README.md) — ADR index
- [docs/adr/ADR-002-distribution-only-church-brand.md](./adr/ADR-002-distribution-only-church-brand.md) — Church brand policy

---

## Schema & audit

- [docs/SCHEMA_CHANGELOG.md](./SCHEMA_CHANGELOG.md) — Schema changelog
- [docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md](./AUDIT_OLD_CHAT_SPECS_VS_V4.md) — Audit old chat specs vs V4

---

## Governance note

All docs that declare authority must reference the three canonical anchors: `SYSTEM_OWNER_VISION.md`, `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`, `specs/PHOENIX_V4_5_WRITER_SPEC.md`.

---

## Document all — usage

**What "document all" means:** Subsections titled "Document all" or "(document all)" list every doc, script, config, and artifact for that domain. Use them for coverage checks and "is X anywhere in the index?"

**When to add a doc:**
- New doc that declares authority or is referenced by specs → add to the appropriate section and to the complete inventory below.
- New script/config that is part of a documented system → add to that section's Document all table.

**How to add:**
1. Place in the correct section (e.g. Pearl News, Teacher Mode, Translation).
2. Add a row to the "Document all — complete inventory" below. Use ✓ if file exists, ⚠️ if referenced but missing.
3. If the doc declares authority, ensure it references the three canonical anchors: [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md), [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md), [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md).

**North star for go/no-go:** [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md) §6 Hard NOs.

---

## Document all — complete inventory

Single list of every **doc**, **spec**, **config**, and **script** referenced in this index. ⚠️ = referenced but file not found on disk.

### Docs (docs/)

| Doc | Section | Status |
|-----|---------|--------|
| [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md) | Canonical authority | ✓ |
| [DOCS_INDEX.md](./DOCS_INDEX.md) | Canonical authority | ✓ |
| [RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) | Core system docs | ✓ |
| [PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md](./PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md) | Core system docs | ✓ |
| [SYSTEMS_V4.md](./SYSTEMS_V4.md) | Core system docs | ✓ |
| [PLANNING_STATUS.md](./PLANNING_STATUS.md) | Core system docs | ✓ |
| [SYSTEMS_AUDIT.md](./SYSTEMS_AUDIT.md) | Core system docs | ✓ |
| [PEARL_NEWS_ARCHITECTURE_SPEC.md](./PEARL_NEWS_ARCHITECTURE_SPEC.md) | Pearl News | ✓ |
| [PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md](./PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md) | Pearl News | ✓ |
| [PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md) | Pearl News | ✓ |
| [PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md](./PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md) | Pearl News | ✓ |
| [PEARL_NEWS_GO_NO_GO_CHECKLIST.md](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md) | Pearl News | ✓ |
| [PEARL_NEWS_HARDENING_100_PERCENT.md](./PEARL_NEWS_HARDENING_100_PERCENT.md) | Pearl News | ✓ |
| `PEARL_NEWS_WRITER_SPEC.md` | Pearl News | ⚠️ missing |
| [PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md](./PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md) | Governance | ✓ |
| [PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md](./PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md) | Governance | ✓ |
| [GOVERNANCE_HARDENING_BLUEPRINT.md](./GOVERNANCE_HARDENING_BLUEPRINT.md) | Governance | ✓ |
| [governance/registry_integrity_checker_v1.md](./governance/registry_integrity_checker_v1.md) | Governance | ✓ |
| [RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md) | Brand & release | ✓ |
| [PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md](./PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md) | Brand & release | ✓ |
| [church_docs/README.md](./church_docs/README.md) | Church & payout | ✓ |
| `norcal_dharma.yaml` | Church & payout | ⚠️ missing |
| [adr/ADR-002-distribution-only-church-brand.md](./adr/ADR-002-distribution-only-church-brand.md) | Church & payout, ADRs | ✓ |
| [BOOK_001_ASSEMBLY_CONTRACT.md](./BOOK_001_ASSEMBLY_CONTRACT.md) | Book & authoring | ✓ |
| [BOOK_001_FREEZE.md](./BOOK_001_FREEZE.md) | Book & authoring | ✓ |
| [BOOK_001_READINESS_CHECKLIST.md](./BOOK_001_READINESS_CHECKLIST.md) | Book & authoring | ✓ |
| [BOOK_001_POST_MORTEM.md](./BOOK_001_POST_MORTEM.md) | Book & authoring | ✓ |
| [authoring/AUTHOR_ASSET_WORKBOOK.md](./authoring/AUTHOR_ASSET_WORKBOOK.md) | Book & authoring | ✓ |
| [WRITER_BRIEF_BOOK_001.md](./WRITER_BRIEF_BOOK_001.md) | Book & authoring | ✓ |
| [WRITER_COMMS_SYSTEMS_100.md](./WRITER_COMMS_SYSTEMS_100.md) | Book & authoring | ✓ |
| [WRITER_SPEC_MARKDOWN_AND_DOCX.md](./WRITER_SPEC_MARKDOWN_AND_DOCX.md) | Book & authoring | ✓ |
| [FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) | Book & authoring | ✓ |
| [ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md](./ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md) | Enlightened Intelligence | ✓ |
| [MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md](./MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md) | Manuscript quality | ✓ |
| `PRODUCTION_READINESS_GO_NO_GO.md` | Manuscript quality | ⚠️ missing |
| `RELEASE_PRODUCTION_READINESS_CHECKLIST.md` | Manuscript quality | ⚠️ missing |
| [writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md](./writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md) | Writing & content quality | ✓ |
| [HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md](./HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md) | Writing & content quality | ✓ |
| [CREATIVE_QUALITY_GATE_V1.md](./CREATIVE_QUALITY_GATE_V1.md) | Writing & content quality | ✓ |
| [CREATIVE_QUALITY_VALIDATION_CHECKLIST.md](./CREATIVE_QUALITY_VALIDATION_CHECKLIST.md) | Writing & content quality | ✓ |
| [INSIGHT_DENSITY_ANALYZER.md](./INSIGHT_DENSITY_ANALYZER.md) | Writing & content quality | ✓ |
| [NARRATIVE_TENSION_VALIDATOR.md](./NARRATIVE_TENSION_VALIDATOR.md) | Writing & content quality | ✓ |
| [SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md](./SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md) | Writing & content quality | ✓ |
| [UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md](./UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md) | Writing & content quality | ✓ |
| [ATOM_NATIVE_MODULAR_FORMATS.md](./ATOM_NATIVE_MODULAR_FORMATS.md) | Atoms & formats | ✓ |
| [INTRO_AND_CONCLUSION_SYSTEM.md](./INTRO_AND_CONCLUSION_SYSTEM.md) | Atoms & formats | ✓ |
| [PRACTICE_LIBRARY_TEACHER_FALLBACK.md](./PRACTICE_LIBRARY_TEACHER_FALLBACK.md) | Atoms & formats | ✓ |
| [TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md) | Atoms & formats | ✓ |
| [TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md) | Teacher Mode | ✓ |
| [TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md](./TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md) | Coverage & ops | ✓ |
| [COVERAGE_HEALTH_JSON_SCHEMA.md](./COVERAGE_HEALTH_JSON_SCHEMA.md) | Coverage & ops | ✓ |
| [TITLE_AND_CATALOG_MARKETING_SYSTEM.md](./TITLE_AND_CATALOG_MARKETING_SYSTEM.md) | Coverage & ops | ✓ |
| [PHASE_13_C_WAVE_OPTIMIZER.md](./PHASE_13_C_WAVE_OPTIMIZER.md) | Coverage & ops | ✓ |
| [V4_FEATURES_SCALE_AND_KNOBS.md](./V4_FEATURES_SCALE_AND_KNOBS.md) | Coverage & ops | ✓ |
| [email_sequences/README.md](./email_sequences/README.md) | Email sequences | ✓ |
| [email_sequences/5-email-welcome-sequence.md](./email_sequences/5-email-welcome-sequence.md) | Email sequences | ✓ |
| [email_sequences/persona-variants.md](./email_sequences/persona-variants.md) | Email sequences | ✓ |
| [email_sequences/exercise-one-liners.md](./email_sequences/exercise-one-liners.md) | Email sequences | ✓ |
| [email_sequences/FORMSPREE_SETUP.md](./email_sequences/FORMSPREE_SETUP.md) | Email sequences | ✓ |
| [GITHUB_BACKUP_SETUP.md](./GITHUB_BACKUP_SETUP.md) | Operations & infra | ✓ |
| [QWEN_FORKS_AND_BACKUP.md](./QWEN_FORKS_AND_BACKUP.md) | Operations & infra | ✓ |
| [adr/README.md](./adr/README.md) | ADRs | ✓ |
| [SCHEMA_CHANGELOG.md](./SCHEMA_CHANGELOG.md) | Schema & audit | ✓ |
| [AUDIT_OLD_CHAT_SPECS_VS_V4.md](./AUDIT_OLD_CHAT_SPECS_VS_V4.md) | Schema & audit | ✓ |
| `LOCALE_PROSE_AND_PROMPTING.md` | Translation | ⚠️ missing |
| `MULTILINGUAL_ARCHITECTURE.md` | Translation | ⚠️ missing |
| `KOREA_MARKET_AND_PROSE.md` | Translation | ⚠️ missing |
| `JAPANESE_MARKET_SELFHELP_GUIDE.md` | Translation | ⚠️ missing |

### Specs (specs/)

| Spec | Section | Status |
|------|---------|--------|
| [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) | Canonical authority | ✓ |
| [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) | Canonical authority | ✓ |
| [specs/README.md](../specs/README.md) | Core system docs | ✓ |
| `specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md` | Phoenix Churches Payout | ⚠️ missing |
| [specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md) | Simulation | ✓ |

### Specs — full index

All `.md` files under `specs/` confirmed present on disk. Additional `.txt` and `.js` spec files listed as plain text (unusual filenames or non-markdown format; present on disk, not linked to avoid path-encoding issues in governance check).

| Spec | Purpose |
|------|---------|
| [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) | Arc-First pipeline: sole architecture authority |
| [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) | Writer/content authority |
| [specs/README.md](../specs/README.md) | Specs overview |
| [specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md) | Gate 12 production readiness |
| [specs/ARC_AUTHORING_PLAYBOOK.md](../specs/ARC_AUTHORING_PLAYBOOK.md) | Arc authoring: constraints, BAND rules, validation |
| [specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md](../specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md) | Brand archetype validation rules |
| [specs/COMPILED_PLAN_SCHEMA_CONTRACT.md](../specs/COMPILED_PLAN_SCHEMA_CONTRACT.md) | CompiledBook JSON schema contract |
| [specs/DUPE_EVAL_SPEC.md](../specs/DUPE_EVAL_SPEC.md) | Duplication evaluation: prose, atom, structural |
| [specs/ENGINE_DEFINITION_SCHEMA.md](../specs/ENGINE_DEFINITION_SCHEMA.md) | Engine YAML schema (spiral, watcher, false_alarm, etc.) |
| [specs/INTRO_CONCLUSION_VARIATION_SPEC.md](../specs/INTRO_CONCLUSION_VARIATION_SPEC.md) | Intro/conclusion variation: flag, pools, injection rules |
| [specs/OMEGA_LAYER_CONTRACTS.md](../specs/OMEGA_LAYER_CONTRACTS.md) | Omega layer interface contracts |
| [specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) | Deep research: invisible script, belief flip, marketing brief |
| [specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md) | Freebie system: asset types, planner, CTA injection |
| [specs/PHOENIX_V4_CANONICAL_SPEC.md](../specs/PHOENIX_V4_CANONICAL_SPEC.md) | V4 canonical spec (predecessor to V4.5) |
| [specs/PRACTICE_ITEM_SCHEMA.md](../specs/PRACTICE_ITEM_SCHEMA.md) | Practice item YAML schema for EXERCISE slot |
| [specs/TEACHER_AUTHORING_LAYER_SPEC.md](../specs/TEACHER_AUTHORING_LAYER_SPEC.md) | Teacher authoring layer: workflow, approval, staging |
| [specs/TEACHER_INTEGRITY_SPEC.md](../specs/TEACHER_INTEGRITY_SPEC.md) | Teacher integrity: doctrine, synthetic ratio, governance |
| [specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md](../specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md) | Teacher Mode authoring playbook |
| [specs/TEACHER_MODE_MASTER_SPEC.md](../specs/TEACHER_MODE_MASTER_SPEC.md) | Teacher Mode master spec |
| [specs/TEACHER_MODE_NORMALIZATION_SPEC.md](../specs/TEACHER_MODE_NORMALIZATION_SPEC.md) | Teacher Mode normalization: consistent voice, format |
| [specs/TEACHER_MODE_STRUCTURAL_SPEC.md](../specs/TEACHER_MODE_STRUCTURAL_SPEC.md) | Teacher Mode structural rules |
| [specs/TEACHER_MODE_V4_CANONICAL_SPEC.md](../specs/TEACHER_MODE_V4_CANONICAL_SPEC.md) | Teacher Mode V4 canonical spec |
| [specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md](../specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md) | Teacher portfolio planning: topic/persona coverage targets |
| [specs/V4_6_BINGE_OPTIMIZATION_LAYER.md](../specs/V4_6_BINGE_OPTIMIZATION_LAYER.md) | V4.6 binge optimization: serialized listening, continuity |
| [specs/WRITER_DEV_SPEC_PHASE_2.md](../specs/WRITER_DEV_SPEC_PHASE_2.md) | Writer dev spec phase 2 |

**Additional specs files (non-.md or unusual filename — present on disk, plain-text references):**

| File | Purpose |
|------|---------|
| `specs/PHOENIX_OMEGA_V4_COMPLETE_SPEC (1).md` | Full V4 system spec (2358 lines); claims canonical status; predecessor to current Arc-First canonical. Filename has parens — cannot be safely linked. |
| `specs/PHOENIX_V4_NARRATIVE_GATES_DEV_SPEC.js` | JavaScript doc-generation script (1082 lines) for narrative gates spec; produces a formatted .docx. Non-markdown — indexed as plain text. |
| `specs/phoenix_rebuild_spec.txt` | V4 exercise system dev spec (610 lines); covers slot-compatible, template-safe exercise pipeline design. |
| `specs/v4_system_up_spec.txt` | V4 Narrative Amplification Addendum (403 lines); covers escalation, cost, and resonance amplification layer. |

### Root & other

| Item | Section | Status |
|------|---------|--------|
| [ONBOARDING.md](../ONBOARDING.md) | Core system docs | ✓ |
| [pearl_news/README.md](../pearl_news/README.md) | Pearl News | ✓ |
| [pearl_news/publish/README.md](../pearl_news/publish/README.md) | Pearl News | ✓ |
| [pearl_news/pipeline/README.md](../pearl_news/pipeline/README.md) | Pearl News | ✓ |
| [pearl_news/atoms/README.md](../pearl_news/atoms/README.md) | Pearl News | ✓ |
| [pearl_news/governance/README.md](../pearl_news/governance/README.md) | Pearl News | ✓ |
| [config/source_of_truth/mechanism_aliases/_schema.yaml](../config/source_of_truth/mechanism_aliases/_schema.yaml) | Mechanism alias | ✓ |
| [config/source_of_truth/mechanism_aliases/_naming_template.md](../config/source_of_truth/mechanism_aliases/_naming_template.md) | Mechanism alias | ✓ |
| [config/source_of_truth/intro_ending_variation.yaml](../config/source_of_truth/intro_ending_variation.yaml) | Atom coverage | ✓ |
| [config/source_of_truth/master_arcs/README.md](../config/source_of_truth/master_arcs/README.md) | Master arcs | ✓ |
| [atoms/INDEX.md](../atoms/INDEX.md) | Atom coverage | ✓ |

### Config

| Config | Section | Status |
|--------|---------|--------|
| `config/source_of_truth/enlightened_intelligence_registry.yaml` | Enlightened Intelligence | ⚠️ missing |
| `config/quality/tier0_book_output_contract.yaml` | Manuscript quality | ⚠️ missing |
| `config/quality/canary_config.yaml` | Manuscript quality | ⚠️ missing |
| `config/payouts/churches.yaml` | Phoenix Churches Payout | ⚠️ missing |
| `config/payouts/payees.yaml` | Phoenix Churches Payout | ⚠️ missing |
| `config/payouts/credentials.yaml.example` | Phoenix Churches Payout | ⚠️ missing |
| `config/payouts/fill_template.csv` | Phoenix Churches Payout | ⚠️ missing |
| [config/teachers/teacher_registry.yaml](../config/teachers/teacher_registry.yaml) | Teacher Mode | ✓ |
| [.github/workflows/teacher-gates.yml](../.github/workflows/teacher-gates.yml) | Teacher Mode | ✓ |
| [.github/workflows/brand-guards.yml](../.github/workflows/brand-guards.yml) | Church & payout (NorCal Dharma brand guards) | ✓ |
| `quality_contracts/README.md` | Translation | ⚠️ missing |
| `quality_contracts/glossary.yaml` | Translation | ⚠️ missing |
| `quality_contracts/release_thresholds.yaml` | Translation | ⚠️ missing |
| `quality_contracts/golden_translation_regression.yaml` | Translation | ⚠️ missing |
| `config/localization/content_roots_by_locale.yaml` | Translation | ⚠️ missing |
| `.github/workflows/translate-atoms-qwen-matrix.yml` | Translation | ⚠️ missing |
| `.github/workflows/simulation-10k.yml` | Simulation CI | ⚠️ missing |
| `.github/workflows/release-gates.yml` | Simulation CI | ⚠️ missing |
| [config/format_selection/format_registry.yaml](../config/format_selection/format_registry.yaml) | Simulation / Delivery | ✓ |
| [config/format_selection/selection_rules.yaml](../config/format_selection/selection_rules.yaml) | Simulation | ✓ |
| `config/source_of_truth/chapter_order_modes.yaml` | Simulation | ⚠️ missing |

### Scripts & code

| Script / module | Section | Status |
|-----------------|---------|--------|
| [scripts/run_pipeline.py](../scripts/run_pipeline.py) | Delivery pipeline | ✓ |
| [scripts/run_production_readiness_gates.py](../scripts/run_production_readiness_gates.py) | Simulation | ✓ |
| [scripts/render_plan_to_txt.py](../scripts/render_plan_to_txt.py) | Delivery pipeline | ✓ |
| [scripts/pearl_news_networked_run_and_evidence.sh](../scripts/pearl_news_networked_run_and_evidence.sh) | Pearl News | ✓ |
| [scripts/pearl_news_post_to_wp.py](../scripts/pearl_news_post_to_wp.py) | Pearl News | ✓ |
| [scripts/pearl_news_do_it.sh](../scripts/pearl_news_do_it.sh) | Pearl News | ✓ |
| [pearl_news/pipeline/run_article_pipeline.py](../pearl_news/pipeline/run_article_pipeline.py) | Pearl News | ✓ |
| [pearl_news/pipeline/feed_ingest.py](../pearl_news/pipeline/feed_ingest.py) | Pearl News | ✓ |
| [pearl_news/pipeline/topic_sdg_classifier.py](../pearl_news/pipeline/topic_sdg_classifier.py) | Pearl News | ✓ |
| [pearl_news/pipeline/template_selector.py](../pearl_news/pipeline/template_selector.py) | Pearl News | ✓ |
| [pearl_news/pipeline/article_assembler.py](../pearl_news/pipeline/article_assembler.py) | Pearl News | ✓ |
| [pearl_news/pipeline/quality_gates.py](../pearl_news/pipeline/quality_gates.py) | Pearl News | ✓ |
| [pearl_news/pipeline/qc_checklist.py](../pearl_news/pipeline/qc_checklist.py) | Pearl News | ✓ |
| [pearl_news/publish/wordpress_client.py](../pearl_news/publish/wordpress_client.py) | Pearl News | ✓ |
| [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py) | Delivery pipeline / Mechanism alias | ✓ |
| [phoenix_v4/rendering/prose_resolver.py](../phoenix_v4/rendering/prose_resolver.py) | Delivery pipeline | ✓ |
| [phoenix_v4/rendering/__init__.py](../phoenix_v4/rendering/__init__.py) | Delivery pipeline | ✓ |
| [scripts/ci/run_teacher_production_gates.py](../scripts/ci/run_teacher_production_gates.py) | Teacher Mode | ✓ |
| [scripts/ci/check_doctrine_schema.py](../scripts/ci/check_doctrine_schema.py) | Teacher Mode | ✓ |
| [scripts/ci/check_teacher_readiness.py](../scripts/ci/check_teacher_readiness.py) | Teacher Mode | ✓ |
| [scripts/ci/check_teacher_synthetic_governance.py](../scripts/ci/check_teacher_synthetic_governance.py) | Teacher Mode | ✓ |
| [scripts/teacher_stub_f006_slots.py](../scripts/teacher_stub_f006_slots.py) | Teacher Mode | ✓ |
| [scripts/ci/report_variation_knobs.py](../scripts/ci/report_variation_knobs.py) | Simulation | ✓ |
| `scripts/ci/run_simulation_10k.py` | Simulation | ⚠️ missing |
| `scripts/ci/run_simulation_100k.py` | Simulation | ⚠️ missing |
| `scripts/ci/analyze_pearl_prime_sim.py` | Simulation | ⚠️ missing |
| `scripts/ci/run_rigorous_system_test.py` | Simulation | ⚠️ missing |
| `scripts/ci/check_book_output_tier0_contract.py` | Manuscript quality | ⚠️ missing |
| `scripts/ci/tier0_trend.py` | Manuscript quality | ⚠️ missing |
| `scripts/ci/run_canary_100_books.py` | Manuscript quality | ⚠️ missing |
| [scripts/ci/check_norcal_dharma_brand_guards.py](../scripts/ci/check_norcal_dharma_brand_guards.py) | Church & payout | ✓ |
| [scripts/ci/check_church_yaml_no_sensitive_tokens.py](../scripts/ci/check_church_yaml_no_sensitive_tokens.py) | Church & payout | ✓ |
| `scripts/ci/check_norcal_dharma_export.py` | Church & payout | ⚠️ missing |
| [scripts/ops/smoke_church_brand_resolution.py](../scripts/ops/smoke_church_brand_resolution.py) | Church & payout | ✓ |
| [phoenix_v4/ops/church_loader.py](../phoenix_v4/ops/church_loader.py) | Church & payout | ✓ |
| `scripts/translate_atoms_all_locales_cloud.py` | Translation | ⚠️ missing |
| `scripts/validate_translations.py` | Translation | ⚠️ missing |
| `scripts/merge_translation_shards.py` | Translation | ⚠️ missing |
| `scripts/check_golden_translation.py` | Translation | ⚠️ missing |
| `scripts/native_prompts_eval_learn.py` | Translation | ⚠️ missing |
