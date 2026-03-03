# Phoenix Docs Index

**Purpose:** Canonical index for documentation authority and navigation.
**Last updated:** 2026-03-03

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

### Scripts

| Item | Location |
|------|----------|
| **Simulation CLI** | [simulation/run_simulation.py](../simulation/run_simulation.py) — `--n`, `--phase2`, `--phase3`, `--use-format-selector`, `--full-knobs`, `--out` |
| **Simulator core** | [simulation/simulator.py](../simulation/simulator.py) — Formats, validation matrix, BookRequest, run_simulation(), validate_plan() |
| **Phase 2** | [simulation/phase2.py](../simulation/phase2.py) — Waveform, arc, drift on Phase 1 results |
| **Phase 3 MVP** | [simulation/phase3_mvp.py](../simulation/phase3_mvp.py) — Volatility, cognitive, consequence, reassurance on synthetic text |
| **10k sim runner** | [scripts/ci/run_simulation_10k.py](../scripts/ci/run_simulation_10k.py) — n=10000, --use-format-selector, --phase2, --phase3 (CI) |
| **100k sim runner** | [scripts/ci/run_simulation_100k.py](../scripts/ci/run_simulation_100k.py) — n=100000, --full-knobs; optional --n, --out |
| **Analyzer** | [scripts/ci/analyze_pearl_prime_sim.py](../scripts/ci/analyze_pearl_prime_sim.py) — Pass rate by dimension; best/worst combos; --input, --out |
| **Rigorous suite runner** | [scripts/ci/run_rigorous_system_test.py](../scripts/ci/run_rigorous_system_test.py) — 10k sim + variation report + E2E smoke + atoms coverage |
| **Variation report** | [scripts/ci/report_variation_knobs.py](../scripts/ci/report_variation_knobs.py) — variation_knob_distribution, pearl_prime block from plans/index |
| **Monte Carlo CTSS** | [simulation/run_monte_carlo_ctss.py](../simulation/run_monte_carlo_ctss.py) — Duplication risk vs index |
| **Systems test** | [scripts/systems_test/run_systems_test.py](../scripts/systems_test/run_systems_test.py) — Phases 1–7; optional sim run |

### Config (simulation & knob coverage)

| Item | Location |
|------|----------|
| **Formats (V4.5)** | [simulation/config/v4_5_formats.yaml](../simulation/config/v4_5_formats.yaml) — 14 formats, tiers S–E |
| **Validation matrix** | [simulation/config/validation_matrix.yaml](../simulation/config/validation_matrix.yaml) — Tier rules (misfire, silence, integration_modes, etc.) |
| **Emotional temperature curves** | [simulation/config/emotional_temperature_curves.yaml](../simulation/config/emotional_temperature_curves.yaml) — Per-format temperature sequences |
| **Format selection** | [config/format_selection/format_registry.yaml](../config/format_selection/format_registry.yaml), [config/format_selection/selection_rules.yaml](../config/format_selection/selection_rules.yaml) — Stage 2 format selector (topic/persona/installment) |
| **Canonical personas/topics** | [config/catalog_planning/canonical_personas.yaml](../config/catalog_planning/canonical_personas.yaml), [config/catalog_planning/canonical_topics.yaml](../config/catalog_planning/canonical_topics.yaml) — Knob sampler / full-knobs source |
| **Angles** | [config/angles/angle_registry.yaml](../config/angles/angle_registry.yaml) — angle_id for sim |
| **Book structure / journey / motif / reframe** | [config/source_of_truth/book_structure_archetypes.yaml](../config/source_of_truth/book_structure_archetypes.yaml), [config/source_of_truth/journey_shapes.yaml](../config/source_of_truth/journey_shapes.yaml), [config/source_of_truth/recurring_motif_bank.yaml](../config/source_of_truth/recurring_motif_bank.yaml), [config/source_of_truth/reframe_line_bank.yaml](../config/source_of_truth/reframe_line_bank.yaml) |
| **Section / chapter order** | [config/source_of_truth/section_reorder_modes.yaml](../config/source_of_truth/section_reorder_modes.yaml), [config/source_of_truth/chapter_order_modes.yaml](../config/source_of_truth/chapter_order_modes.yaml) |

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
| **Simulation 10k workflow** | [.github/workflows/simulation-10k.yml](../.github/workflows/simulation-10k.yml) — If present: 10k sim, variation report, E2E smoke, atoms coverage |
| **Release gates** | [.github/workflows/release-gates.yml](../.github/workflows/release-gates.yml) — Release gates; may reference sim |
| **Teacher gates** | [.github/workflows/teacher-gates.yml](../.github/workflows/teacher-gates.yml) — Teacher production gates + teacher arc tests + Teacher Mode E2E smoke (see [Teacher Mode & production readiness](#teacher-mode--production-readiness-document-all)) |

---

## Pearl News

Pearl News is 100% at **code/tests** when classifier, selector, quality gates, and e2e tests pass. It is **100% production-ready** only when all 6 operational gates are confirmed on `main` with evidence links (see [PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md](./PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md)).

### Operational gates (production 100%)

1. Merge to `main`
2. `pearl_news_gates.yml` green on `main`
3. Networked pipeline smoke run on `main` passes
4. Scheduled workflow run on GitHub passes
5. WordPress draft-post flow verified with real secrets
6. Checklist doc completed with evidence links

### Pearl News docs

- [docs/PEARL_NEWS_ARCHITECTURE_SPEC.md](./PEARL_NEWS_ARCHITECTURE_SPEC.md) — Architecture: pipeline, atoms, templates, config, governance
- [docs/PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md](./PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md) — Frozen metadata contract for `article_metadata.jsonl`; required keys, governance use
- [docs/PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md) — Scheduled pipeline runs, WordPress posting, GitHub Actions setup, secrets
- [docs/PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md](./PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md) — **Production checklist:** code/tests must-pass (4 criteria) + 6 operational gates. Pre-merge verification, incident ownership, evidence lock template, rollback procedure
- [docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md) — Go/no-go checklist for Pearl News releases
- [docs/PEARL_NEWS_HARDENING_100_PERCENT.md](./PEARL_NEWS_HARDENING_100_PERCENT.md) — Hardening slice: URL normalization, one-command runner, CI preflight, evidence bundle
- [docs/PEARL_NEWS_WRITER_SPEC.md](./PEARL_NEWS_WRITER_SPEC.md) — Writer spec: voice, atom types, 4-layer blend, quality gates, template guidance
- [pearl_news/README.md](../pearl_news/README.md) — Quick start, structure, one-command run
- [pearl_news/publish/README.md](../pearl_news/publish/README.md) — WordPress credentials, article format, posting script

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

Church brands (e.g. NorCal Dharma) are identity/distribution only: no teacher, no Teacher Mode, no wave allocation. Display name from church YAML at runtime.

### Church docs

- [docs/church_docs/README.md](./church_docs/README.md) — Church–brand linkage: brand_id → church record mapping, display name source, ops smoke
- [docs/norcal_dharma.yaml](./norcal_dharma.yaml) — Church #1 canonical record (Cooperative Church Compliance YAML Schema)
- [docs/adr/ADR-002-distribution-only-church-brand.md](./adr/ADR-002-distribution-only-church-brand.md) — Distribution-only church brand policy

### Scripts & CI

- `scripts/ci/check_norcal_dharma_no_matrix.py` — norcal_dharma must NOT appear in any brand_teacher_matrix_*.yaml
- `scripts/ci/check_norcal_dharma_export.py` — norcal_dharma rows must have teacher_id=default_teacher (plans + manifest)
- `scripts/ci/check_church_yaml_no_sensitive_tokens.py` — Church YAMLs must not contain ssn, account_number, etc.
- `scripts/ops/smoke_church_brand_resolution.py` — Ops smoke: brand_id → church.short_name across all church brands
- `phoenix_v4/ops/church_loader.py` — load_church(brand_id), get_church_display_name(brand_id); fail-fast when missing/invalid

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
- [config/source_of_truth/enlightened_intelligence_registry.yaml](../config/source_of_truth/enlightened_intelligence_registry.yaml) — EI registry: slots, llm_judge, embeddings, teacher_integrity

---

## Manuscript quality (Tier 0 contract)

**Feature = complete.** Tier 0 contract, canary gate, and trend dashboard are implemented. **Production 100%** requires the full operational checklist: CI/release gates on `main`, branch protection, smoke runs, evidence, rollback proof. See [PRODUCTION_READINESS_GO_NO_GO.md](./PRODUCTION_READINESS_GO_NO_GO.md), [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md).

### Document all

| Item | Location |
|------|----------|
| **Checklist (Tier 0–4, canary, verification)** | [docs/MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md](./MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md) |
| **Tier 0 contract config** | [config/quality/tier0_book_output_contract.yaml](../config/quality/tier0_book_output_contract.yaml) |
| **Canary config** | [config/quality/canary_config.yaml](../config/quality/canary_config.yaml) |
| **Tier 0 checker** | [scripts/ci/check_book_output_tier0_contract.py](../scripts/ci/check_book_output_tier0_contract.py) |
| **Trend dashboard** | [scripts/ci/tier0_trend.py](../scripts/ci/tier0_trend.py) — violations over time; observability add-on, not a production gate |
| **Canary script** | [scripts/ci/run_canary_100_books.py](../scripts/ci/run_canary_100_books.py) |
| **Tests** | [tests/test_tier0_contract.py](../tests/test_tier0_contract.py) |
| **Release checklist (item 12)** | [docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md) — block release on Tier 0 fail |

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

## Teacher Mode & production readiness (document all)

Teacher Mode is **100% production-ready** when: (1) strict validation and CI gates pass on `main`, (2) E2E Teacher Mode compile smoke tests pass for all teachers, (3) release path uses only approved assets (no fallback/missing-atom warnings), (4) evidence is archived, (5) branch protection requires Teacher gates. See [TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md).

### Docs

| Item | Location |
|------|----------|
| **Teacher production readiness** | [docs/TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md) — Gates, E2E smoke, release path, evidence, branch protection |
| **Teacher mode system reference** | [docs/TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md) — Coverage gate, doctrine, approved_atoms, config (see also [Atoms & formats](#atoms--formats)) |
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
| **Teacher Arc unit tests** | [tests/teacher_arc_test.py](../tests/teacher_arc_test.py) — Blueprint schema, planner determinism, golden teacher blueprint shape (skips if teacher_arc_planner/blueprint not present) |
| **Teacher Mode E2E smoke** | [tests/test_teacher_mode_e2e_smoke.py](../tests/test_teacher_mode_e2e_smoke.py) — One topic/persona/arc per teacher; coverage-gate or full compile |

### Config

| Item | Location |
|------|----------|
| **Teacher registry** | [config/teachers/teacher_registry.yaml](../config/teachers/teacher_registry.yaml) — Canonical list: display_name, kb_id, doctrine_profile, allowed_topics, allowed_engines, teacher_mode_defaults |
| **Per-teacher config** | [config/teachers/<teacher_id>.yaml](../config/teachers/) — Quality profile, exercise fallback, wrappers, teacher_conclusion |
| **Teacher banks** | [SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/](../SOURCE_OF_TRUTH/teacher_banks/) — raw/, doctrine/, kb/, candidate_atoms/, approved_atoms/, artifacts/ |

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

Biweekly payouts for 24 churches; Plaid sync, Bluevine, 90/10 split, human-in-the-loop execution.

### Spec & checklist

- [specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md](../specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md) — Tech spec: architecture, data model, workflow, compensating controls
- [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md) — **What you must give:** Plaid credentials, 24 bank connections, Bluevine last4, payee info

### Config

- [config/payouts/churches.yaml](../config/payouts/churches.yaml) — Church registry (24 churches; bluevine_account_last4, payee_id, rules)
- [config/payouts/payees.yaml](../config/payouts/payees.yaml) — Payee registry (24 payees; display_name, bank_last4)
- [config/payouts/credentials.yaml.example](../config/payouts/credentials.yaml.example) — Credentials template (plaid, access_tokens; copy to credentials.yaml)
- [config/payouts/fill_template.csv](../config/payouts/fill_template.csv) — CSV template for batch-filling church + payee info

### Package & CLI

- [payouts/README.md](../payouts/README.md) — Quick start, setup flow, Cloud Run
- [payouts/cli.py](../payouts/cli.py) — CLI: sync, batch, export, reconcile, fill, migrate
- [payouts/setup.py](../payouts/setup.py) — One-time setup (creates credentials, runs migrations)
- [payouts/credentials.py](../payouts/credentials.py) — Credentials loader (credentials.yaml, env)
- [payouts/plaid_sync.py](../payouts/plaid_sync.py) — Plaid sync (transactions/get)
- [payouts/link_server.py](../payouts/link_server.py) — Plaid Link server (connect banks via web UI)
- [payouts/reconciliation.py](../payouts/reconciliation.py) — Reconciliation engine (eligible deposits, reconcile_batch)
- [payouts/calculator.py](../payouts/calculator.py) — Payout calculator (Decimal, 90%)
- [payouts/batch.py](../payouts/batch.py) — Batch generator + anomaly flags
- [payouts/exporter.py](../payouts/exporter.py) — CSV export (BATCH_SUMMARY, PAYOUT_ITEMS)
- [payouts/ledger/](../payouts/ledger/) — Ledger (SQLite, migrations)
- [payouts/migrations/](../payouts/migrations/) — Schema migrations (001_initial_schema.sql)

### Deployment

- [payouts/Dockerfile](../payouts/Dockerfile) — Cloud Run image
- [payouts/cloudbuild.yaml](../payouts/cloudbuild.yaml) — Cloud Build config
- [payouts/requirements.txt](../payouts/requirements.txt) — Runtime deps (plaid-python, flask)

### Artifacts (gitignored)

- `payouts/ledger.db` — Ledger database
- `artifacts/payouts/` — Batch exports (BATCH_*_BATCH_SUMMARY.csv, BATCH_*_PAYOUT_ITEMS.csv)
- `config/payouts/credentials.yaml` — Secrets (not committed)

---

## Translation, validation & multilingual

Translation and validation pipeline: parallel sharded translation (atoms + exercises) to all locales (zh_CN, zh_TW, zh_HK, zh_SG, yue, ja_JP, ko_KR), deterministic validation (schema, locale script, coverage, meta/leakage, repetition), merge + global QA, golden regression. Native-language prompts and quality contracts drive prose; market guides inform style (reference only).

### Docs

| Item | Location |
|------|----------|
| **Locale prose & prompting** | [docs/LOCALE_PROSE_AND_PROMPTING.md](./LOCALE_PROSE_AND_PROMPTING.md) — Prose quality and prompting for CJK + Korean; native prompts, eval/fix/learn |
| **Multilingual architecture** | [docs/MULTILINGUAL_ARCHITECTURE.md](./MULTILINGUAL_ARCHITECTURE.md) — Locale codes, content roots, BCP-47 normalization |
| **Korean market & prose** | [docs/KOREA_MARKET_AND_PROSE.md](./KOREA_MARKET_AND_PROSE.md) — South Korea self-help credibility, author roster, positioning → ko_KR contract |
| **Japanese market self-help** | [docs/JAPANESE_MARKET_SELFHELP_GUIDE.md](./JAPANESE_MARKET_SELFHELP_GUIDE.md) — Japanese self-help principles, tone, reader segments, devices |

### Scripts

| Item | Location |
|------|----------|
| **Translate atoms/exercises (cloud)** | [scripts/translate_atoms_all_locales_cloud.py](../scripts/translate_atoms_all_locales_cloud.py) — `--total-shards`, `--shard-index`, `--locales`, `--rate-limit-delay`; retries with backoff |
| **Validate translations** | [scripts/validate_translations.py](../scripts/validate_translations.py) — Schema, locale script, coverage, meta/leakage, repetition; `--merge-qa` for post-merge global QA; exit codes 0–6 |
| **Merge translation shards** | [scripts/merge_translation_shards.py](../scripts/merge_translation_shards.py) — Collect shards per locale, dedupe IDs, write manifest |
| **Golden translation regression** | [scripts/check_golden_translation.py](../scripts/check_golden_translation.py) — Golden set regression; `--config`, `--translations-dir` |
| **Native prompts / eval / learn** | [scripts/native_prompts_eval_learn.py](../scripts/native_prompts_eval_learn.py) — Native-language reproduction prompts, style_examples from quality contracts, eval/fix/learn |

### Config & quality contracts

| Item | Location |
|------|----------|
| **Quality contracts (README)** | [quality_contracts/README.md](../quality_contracts/README.md) — Locales, script/tone/taboo/style_examples |
| **Per-locale contracts** | [quality_contracts/zh_CN.yaml](../quality_contracts/zh_CN.yaml), [quality_contracts/ja_JP.yaml](../quality_contracts/ja_JP.yaml), [quality_contracts/ko_KR.yaml](../quality_contracts/ko_KR.yaml), etc. |
| **Glossary (term-lock)** | [quality_contracts/glossary.yaml](../quality_contracts/glossary.yaml) — Bilingual term lock (e.g. grounding, somatic, mindfulness) per locale |
| **Release thresholds** | [quality_contracts/release_thresholds.yaml](../quality_contracts/release_thresholds.yaml) — min_first_pass_pct, min_post_fix_pct, min_gold_pass_pct per locale |
| **Golden regression config** | [quality_contracts/golden_translation_regression.yaml](../quality_contracts/golden_translation_regression.yaml) — golden_items (id, locale, expected_phrases, max_length_delta) |
| **Japanese anchor phrases** | [quality_contracts/ja_JP_anchor_phrases.yaml](../quality_contracts/ja_JP_anchor_phrases.yaml) — Curated Japanese self-help anchor phrases |
| **Content roots by locale** | [config/localization/content_roots_by_locale.yaml](../config/localization/content_roots_by_locale.yaml) — atoms_root, teacher_banks_root, exercises_v4_root per locale |

### CI / workflow

| Item | Location |
|------|----------|
| **Translate + validate + merge** | [.github/workflows/translate-atoms-qwen-matrix.yml](../.github/workflows/translate-atoms-qwen-matrix.yml) — Matrix locale × shard; translate → validate per shard → merge → global QA; workflow_dispatch |

### Artifacts

| Item | Location |
|------|----------|
| **Shard output** | `{out_root}/{locale}/shard_{n}/` — exercises/*.json, atoms/*.json, shard_manifest.json |
| **Merged translations** | `{input_root}/{locale}/exercises/`, `{input_root}/{locale}/atoms/`, manifest.json at input root |

---

## Operations & infra

- [docs/GITHUB_BACKUP_SETUP.md](./GITHUB_BACKUP_SETUP.md) — GitHub backup setup
- [docs/QWEN_FORKS_AND_BACKUP.md](./QWEN_FORKS_AND_BACKUP.md) — Qwen forks and backup

---

## ADRs

- [docs/adr/README.md](./adr/README.md) — ADR index
- [docs/adr/ADR-002-distribution-only-church-brand.md](./adr/ADR-002-distribution-only-church-brand.md) — Church brand policy (see also [Church & payout](#church--payout-distribution-only-brands))

---

## Schema & audit

- [docs/SCHEMA_CHANGELOG.md](./SCHEMA_CHANGELOG.md) — Schema changelog
- [docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md](./AUDIT_OLD_CHAT_SPECS_VS_V4.md) — Audit old chat specs vs V4

---

## Governance note

All docs that declare authority must reference the three canonical anchors above.

---

## Document all — complete inventory

Single list of every **doc**, **spec**, **config**, and **script** referenced in this index. Use for coverage checks and "is X anywhere in the index?"

### Docs (docs/)

| Doc | Section |
|-----|---------|
| [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md) | Canonical authority |
| [DOCS_INDEX.md](./DOCS_INDEX.md) | Canonical authority |
| [RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) | Core system docs |
| [SYSTEMS_V4.md](./SYSTEMS_V4.md) | Core system docs |
| [PLANNING_STATUS.md](./PLANNING_STATUS.md) | Core system docs |
| [SYSTEMS_AUDIT.md](./SYSTEMS_AUDIT.md) | Core system docs |
| [PEARL_NEWS_ARCHITECTURE_SPEC.md](./PEARL_NEWS_ARCHITECTURE_SPEC.md) | Pearl News |
| [PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md](./PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md) | Pearl News |
| [PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md) | Pearl News |
| [PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md](./PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md) | Pearl News |
| [PEARL_NEWS_GO_NO_GO_CHECKLIST.md](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md) | Pearl News |
| [PEARL_NEWS_HARDENING_100_PERCENT.md](./PEARL_NEWS_HARDENING_100_PERCENT.md) | Pearl News |
| [PEARL_NEWS_WRITER_SPEC.md](./PEARL_NEWS_WRITER_SPEC.md) | Pearl News |
| [PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md](./PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md) | Governance |
| [PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md](./PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md) | Governance |
| [GOVERNANCE_HARDENING_BLUEPRINT.md](./GOVERNANCE_HARDENING_BLUEPRINT.md) | Governance |
| [governance/registry_integrity_checker_v1.md](./governance/registry_integrity_checker_v1.md) | Governance |
| [RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md) | Brand & release |
| [PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md](./PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md) | Brand & release |
| [church_docs/README.md](./church_docs/README.md) | Church & payout |
| [norcal_dharma.yaml](./norcal_dharma.yaml) | Church & payout |
| [adr/ADR-002-distribution-only-church-brand.md](./adr/ADR-002-distribution-only-church-brand.md) | Church & payout, ADRs |
| [BOOK_001_ASSEMBLY_CONTRACT.md](./BOOK_001_ASSEMBLY_CONTRACT.md) | Book & authoring |
| [BOOK_001_FREEZE.md](./BOOK_001_FREEZE.md) | Book & authoring |
| [BOOK_001_READINESS_CHECKLIST.md](./BOOK_001_READINESS_CHECKLIST.md) | Book & authoring |
| [BOOK_001_POST_MORTEM.md](./BOOK_001_POST_MORTEM.md) | Book & authoring |
| [authoring/AUTHOR_ASSET_WORKBOOK.md](./authoring/AUTHOR_ASSET_WORKBOOK.md) | Book & authoring |
| [WRITER_BRIEF_BOOK_001.md](./WRITER_BRIEF_BOOK_001.md) | Book & authoring |
| [WRITER_COMMS_SYSTEMS_100.md](./WRITER_COMMS_SYSTEMS_100.md) | Book & authoring |
| [WRITER_SPEC_MARKDOWN_AND_DOCX.md](./WRITER_SPEC_MARKDOWN_AND_DOCX.md) | Book & authoring |
| [FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) | Book & authoring |
| [ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md](./ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md) | Enlightened Intelligence |
| [MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md](./MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md) | Manuscript quality |
| [PRODUCTION_READINESS_GO_NO_GO.md](./PRODUCTION_READINESS_GO_NO_GO.md) | Manuscript quality |
| [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md) | Manuscript quality |
| [writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md](./writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md) | Writing & content quality |
| [HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md](./HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md) | Writing & content quality |
| [CREATIVE_QUALITY_GATE_V1.md](./CREATIVE_QUALITY_GATE_V1.md) | Writing & content quality |
| [CREATIVE_QUALITY_VALIDATION_CHECKLIST.md](./CREATIVE_QUALITY_VALIDATION_CHECKLIST.md) | Writing & content quality |
| [INSIGHT_DENSITY_ANALYZER.md](./INSIGHT_DENSITY_ANALYZER.md) | Writing & content quality |
| [NARRATIVE_TENSION_VALIDATOR.md](./NARRATIVE_TENSION_VALIDATOR.md) | Writing & content quality |
| [SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md](./SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md) | Writing & content quality |
| [UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md](./UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md) | Writing & content quality |
| [ATOM_NATIVE_MODULAR_FORMATS.md](./ATOM_NATIVE_MODULAR_FORMATS.md) | Atoms & formats |
| [INTRO_AND_CONCLUSION_SYSTEM.md](./INTRO_AND_CONCLUSION_SYSTEM.md) | Atoms & formats |
| [PRACTICE_LIBRARY_TEACHER_FALLBACK.md](./PRACTICE_LIBRARY_TEACHER_FALLBACK.md) | Atoms & formats |
| [TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md) | Atoms & formats |
| [TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md) | Teacher Mode & production readiness |
| [TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md](./TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md) | Coverage & ops |
| [COVERAGE_HEALTH_JSON_SCHEMA.md](./COVERAGE_HEALTH_JSON_SCHEMA.md) | Coverage & ops |
| [TITLE_AND_CATALOG_MARKETING_SYSTEM.md](./TITLE_AND_CATALOG_MARKETING_SYSTEM.md) | Coverage & ops |
| [PHASE_13_C_WAVE_OPTIMIZER.md](./PHASE_13_C_WAVE_OPTIMIZER.md) | Coverage & ops |
| [V4_FEATURES_SCALE_AND_KNOBS.md](./V4_FEATURES_SCALE_AND_KNOBS.md) | Coverage & ops |
| [email_sequences/README.md](./email_sequences/README.md) | Email sequences |
| [email_sequences/5-email-welcome-sequence.md](./email_sequences/5-email-welcome-sequence.md) | Email sequences |
| [email_sequences/persona-variants.md](./email_sequences/persona-variants.md) | Email sequences |
| [email_sequences/exercise-one-liners.md](./email_sequences/exercise-one-liners.md) | Email sequences |
| [email_sequences/FORMSPREE_SETUP.md](./email_sequences/FORMSPREE_SETUP.md) | Email sequences |
| [GITHUB_BACKUP_SETUP.md](./GITHUB_BACKUP_SETUP.md) | Operations & infra |
| [QWEN_FORKS_AND_BACKUP.md](./QWEN_FORKS_AND_BACKUP.md) | Operations & infra |
| [adr/README.md](./adr/README.md) | ADRs |
| [SCHEMA_CHANGELOG.md](./SCHEMA_CHANGELOG.md) | Schema & audit |
| [AUDIT_OLD_CHAT_SPECS_VS_V4.md](./AUDIT_OLD_CHAT_SPECS_VS_V4.md) | Schema & audit |
| [LOCALE_PROSE_AND_PROMPTING.md](./LOCALE_PROSE_AND_PROMPTING.md) | Translation, validation & multilingual |
| [MULTILINGUAL_ARCHITECTURE.md](./MULTILINGUAL_ARCHITECTURE.md) | Translation, validation & multilingual |
| [KOREA_MARKET_AND_PROSE.md](./KOREA_MARKET_AND_PROSE.md) | Translation, validation & multilingual |
| [JAPANESE_MARKET_SELFHELP_GUIDE.md](./JAPANESE_MARKET_SELFHELP_GUIDE.md) | Translation, validation & multilingual |

### Specs (specs/)

| Spec | Section |
|------|---------|
| [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) | Canonical authority |
| [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) | Canonical authority |
| [specs/README.md](../specs/README.md) | Core system docs |
| [specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md](../specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md) | Phoenix Churches Payout |

### Root & other

| Item | Section |
|------|---------|
| [ONBOARDING.md](../ONBOARDING.md) | Core system docs |
| [pearl_news/README.md](../pearl_news/README.md) | Pearl News |
| [pearl_news/publish/README.md](../pearl_news/publish/README.md) | Pearl News |

### Config

| Config | Section |
|--------|---------|
| [config/source_of_truth/enlightened_intelligence_registry.yaml](../config/source_of_truth/enlightened_intelligence_registry.yaml) | Enlightened Intelligence |
| [config/quality/tier0_book_output_contract.yaml](../config/quality/tier0_book_output_contract.yaml) | Manuscript quality |
| [config/quality/canary_config.yaml](../config/quality/canary_config.yaml) | Manuscript quality |
| [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md) | Phoenix Churches Payout |
| [config/payouts/churches.yaml](../config/payouts/churches.yaml) | Phoenix Churches Payout |
| [config/payouts/payees.yaml](../config/payouts/payees.yaml) | Phoenix Churches Payout |
| [config/payouts/credentials.yaml.example](../config/payouts/credentials.yaml.example) | Phoenix Churches Payout |
| [config/payouts/fill_template.csv](../config/payouts/fill_template.csv) | Phoenix Churches Payout |
| [config/teachers/teacher_registry.yaml](../config/teachers/teacher_registry.yaml) | Teacher Mode & production readiness |
| [.github/workflows/teacher-gates.yml](../.github/workflows/teacher-gates.yml) | Teacher Mode & production readiness |
| [quality_contracts/README.md](../quality_contracts/README.md) | Translation, validation & multilingual |
| [quality_contracts/glossary.yaml](../quality_contracts/glossary.yaml) | Translation, validation & multilingual |
| [quality_contracts/release_thresholds.yaml](../quality_contracts/release_thresholds.yaml) | Translation, validation & multilingual |
| [quality_contracts/golden_translation_regression.yaml](../quality_contracts/golden_translation_regression.yaml) | Translation, validation & multilingual |
| [config/localization/content_roots_by_locale.yaml](../config/localization/content_roots_by_locale.yaml) | Translation, validation & multilingual |
| [.github/workflows/translate-atoms-qwen-matrix.yml](../.github/workflows/translate-atoms-qwen-matrix.yml) | Translation, validation & multilingual |

### Scripts & code

| Script / module | Section |
|-----------------|---------|
| `scripts/ci/check_norcal_dharma_no_matrix.py` | Church & payout |
| `scripts/ci/check_norcal_dharma_export.py` | Church & payout |
| `scripts/ci/check_church_yaml_no_sensitive_tokens.py` | Church & payout |
| `scripts/ops/smoke_church_brand_resolution.py` | Church & payout |
| `phoenix_v4/ops/church_loader.py` | Church & payout |
| `scripts/ci/run_teacher_production_gates.py` | Teacher Mode & production readiness |
| `scripts/ci/check_doctrine_schema.py` | Teacher Mode & production readiness |
| `scripts/ci/check_teacher_readiness.py` | Teacher Mode & production readiness |
| `scripts/ci/check_teacher_synthetic_governance.py` | Teacher Mode & production readiness |
| `scripts/teacher_stub_f006_slots.py` | Teacher Mode & production readiness |
| `scripts/ci/check_book_output_tier0_contract.py` | Manuscript quality |
| `scripts/ci/tier0_trend.py` | Manuscript quality |
| `scripts/ci/run_canary_100_books.py` | Manuscript quality |
| `tests/test_tier0_contract.py` | Manuscript quality |
| `tests/teacher_arc_test.py` | Teacher Mode & production readiness |
| `tests/test_teacher_mode_e2e_smoke.py` | Teacher Mode & production readiness |
| `payouts/README.md` | Phoenix Churches Payout |
| `payouts/cli.py` | Phoenix Churches Payout |
| `payouts/setup.py` | Phoenix Churches Payout |
| `payouts/credentials.py` | Phoenix Churches Payout |
| `payouts/plaid_sync.py` | Phoenix Churches Payout |
| `payouts/link_server.py` | Phoenix Churches Payout |
| `payouts/reconciliation.py` | Phoenix Churches Payout |
| `payouts/calculator.py` | Phoenix Churches Payout |
| `payouts/batch.py` | Phoenix Churches Payout |
| `payouts/exporter.py` | Phoenix Churches Payout |
| `payouts/ledger/` | Phoenix Churches Payout |
| `payouts/migrations/` | Phoenix Churches Payout |
| `payouts/Dockerfile` | Phoenix Churches Payout |
| `payouts/cloudbuild.yaml` | Phoenix Churches Payout |
| `payouts/requirements.txt` | Phoenix Churches Payout |
| `scripts/translate_atoms_all_locales_cloud.py` | Translation, validation & multilingual |
| `scripts/validate_translations.py` | Translation, validation & multilingual |
| `scripts/merge_translation_shards.py` | Translation, validation & multilingual |
| `scripts/check_golden_translation.py` | Translation, validation & multilingual |
| `scripts/native_prompts_eval_learn.py` | Translation, validation & multilingual |
