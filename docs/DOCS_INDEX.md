# Phoenix Docs Index

**Purpose:** Canonical index for documentation authority and navigation.  
**Missing-file policy:** Only existing files are linked; planned or missing files are listed as backlog items (plain text or `path` with ⚠️ *file not present*).  
**Last updated:** 2026-03-04

---

## How to use this index

| Task | Where to go |
|------|-------------|
| **Document all (single source)** | This file: [Document all — complete inventory](#document-all--complete-inventory) lists every doc/spec/config/script; domain "(document all)" subsections list every asset per domain. |
| **Find a doc** | Browse sections below, or search [Document all — complete inventory](#document-all--complete-inventory). |
| **Add a doc** | Follow [Document all — usage](#document-all--usage): place in correct section, add to inventory, reference canonical anchors if authority doc. |
| **Check domain coverage** | Use "(document all)" subsections (e.g. [V4 features, scale & knobs](#v4-features-scale--knobs-document-all), [Marketing & deep research](#marketing--deep-research-document-all), [Teacher Mode](#teacher-mode--production-readiness-document-all)) — each lists every asset for that domain. |
| **Go/no-go decision** | [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md) §6 Hard NOs. |

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
- [docs/FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md) — Full test suite plan, gap analysis, pipeline matrix
- [docs/BRANCH_PROTECTION_REQUIREMENTS.md](./BRANCH_PROTECTION_REQUIREMENTS.md) — Required status checks for main
- [docs/DISASTER_RECOVERY_DRILL_CHECKLIST.md](./DISASTER_RECOVERY_DRILL_CHECKLIST.md) — DR drill steps, evidence template
- `docs/CONTROL_PLANE_GO_NO_GO.md` — Control Plane macOS app: pass/fail checks per tab; production-ready when all pass and evidenced
- `docs/CONTROL_PLANE_RUNBOOK.md` — Runbook proving each tab runs real repo commands and reads real artifacts
- `docs/PRODUCTION_100_PLAN.md` — **Production 100% handoff:** scope lock, source-of-truth files, quality system, V2 policy, CI baseline, evidence, release-week commands, hu-HU rules, docs governance, do-not-ship, start-now sequence, definition of 100%; **blockers** and **freeze policy**
- `docs/RELEASE_POLICY.md` — Freeze policy: release/* only, required checks on release branch, only tagged vX.Y.Z can ship
- [docs/PRODUCTION_READINESS_GO_NO_GO.md](./PRODUCTION_READINESS_GO_NO_GO.md) — Go/no-go gate for production readiness
- [docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md) — Step-by-step release checklist; block release on Tier 0 / gate fail
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
| **10k sim runner** | [scripts/ci/run_simulation_10k.py](../scripts/ci/run_simulation_10k.py) — n=10000, --use-format-selector, --phase2, --phase3 (CI) |
| **100k sim runner** | `scripts/ci/run_simulation_100k.py` — n=100000, --full-knobs; optional --n, --out ⚠️ *file not present* |
| **Analyzer** | [scripts/ci/analyze_pearl_prime_sim.py](../scripts/ci/analyze_pearl_prime_sim.py) — Pass rate by dimension; best/worst combos; --input, --out |
| **Rigorous suite runner** | [scripts/ci/run_rigorous_system_test.py](../scripts/ci/run_rigorous_system_test.py) — Systems test + variation + atoms coverage + optional sim |
| **Canary** | [scripts/ci/run_canary_100_books.py](../scripts/ci/run_canary_100_books.py) — Real pipeline on sampled arcs |
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
| **10k results** | `artifacts/simulation_10k.json` (from run_simulation_10k.py --out) |
| **100k results** | `artifacts/simulation_100k.json` (optional --out from run_simulation_100k.py) |
| **Analysis JSON** | `artifacts/reports/pearl_prime_sim_analysis.json` (from analyze_pearl_prime_sim.py --out) |
| **Analysis summary** | `artifacts/reports/pearl_prime_sim_analysis_SUMMARY.txt` |
| **Simulation baseline** | [artifacts/reports/pearl_prime_sim_baseline.json](../artifacts/reports/pearl_prime_sim_baseline.json) — min_pass_rate for CI threshold |
| **Variation report** | `artifacts/reports/variation_report.json` (from report_variation_knobs.py) |
| **Drift dashboard** | `artifacts/drift/` (from build_structural_drift_dashboard.py) |

### CI / workflows

| Item | Location |
|------|----------|
| **Core tests** | [.github/workflows/core-tests.yml](../.github/workflows/core-tests.yml) — Fast pytest + production readiness gates; required for branch protection |
| **Simulation 10k workflow** | [.github/workflows/simulation-10k.yml](../.github/workflows/simulation-10k.yml) — 10k sim + analyzer; fail on threshold |
| **Release gates** | [.github/workflows/release-gates.yml](../.github/workflows/release-gates.yml) — Production gates + rigorous test + canary + rollback smoke |
| **Production observability** | [.github/workflows/production-observability.yml](../.github/workflows/production-observability.yml) — Signal collection, trend tracking |
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
- [docs/GITHUB_SUPPORT_SYSTEM_SPEC.md](./GITHUB_SUPPORT_SYSTEM_SPEC.md) — GitHub support system spec (v1): branch/PR workflow, command delivery format, recovery runbooks, governance checks; dev instruction format and PR checklist

---

## Marketing & deep research (document all)

Single index: every doc, spec, script, and config that uses or is fed by marketing deep research (prompts, invisible scripts, title philosophy, belief flip, consumer language). Outputs feed brand registry, title engine, persona metadata, and content briefs.

### Docs

| Item | Location |
|------|----------|
| **Marketing deep research prompts** | [docs/MARKETING_DEEP_RESEARCH_PROMPTS.md](./MARKETING_DEEP_RESEARCH_PROMPTS.md) — One-to-many deep research prompts; master + 7 sub-prompts (per-brand GTM, emotional vocabulary, consumer vs clinical language, persona×topic invisible scripts, duration bands, cover design, pricing). **Use:** Run via deep research workflow; output feeds brand registry, title engine, persona metadata, content briefs. Downstream: [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md), HOOK atoms, title engine seeds. |
| **Title & catalog marketing system** | [docs/TITLE_AND_CATALOG_MARKETING_SYSTEM.md](./TITLE_AND_CATALOG_MARKETING_SYSTEM.md) — Title philosophy (search keyword, invisible script, brand voice); deep research integration; ops-manual dimensions (templates, imprints, validation); title engine v2→v4. Authority: [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md). |
| **Locale catalog marketing plan** | [docs/LOCALE_CATALOG_MARKETING_PLAN.md](./LOCALE_CATALOG_MARKETING_PLAN.md) — Per-locale positioning, go-live checklists, invisible script per locale; extends title philosophy; references deep research briefs. |
| **New language/location onboarding** | [docs/NEW_LANGUAGE_LOCATION_ONBOARDING.md](./NEW_LANGUAGE_LOCATION_ONBOARDING.md) — Market-driven process and deep research prompts for onboarding a new language, location, topic, or persona. Covers personas, topics (topic families), authors, platforms, metadata, marketing, writing spec, book titles, stories. Use when adding a new locale or expanding persona/topic in a locale. |
| **Release velocity and schedule** | [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md) — Release velocity and schedule |
| **Platform hardening phases** | [docs/PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md](./PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md) — Platform hardening phases 3–8 |

### Specs

| Item | Location |
|------|----------|
| **Deep research integration spec** | [specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) — Narrative Depth Layer v1.0: `invisible_script` HOOK subtype, `belief_flip` STORY pattern, SCENE micro-failure, INTEGRATION `milestone_type`, arc quality test. Subordinate to Arc-First Canonical. Feeds: title philosophy, HOOK atoms, marketing brief (invisible_script, belief flip). |
| **Title engine marketing config spec** | [specs/TITLE_ENGINE_MARKETING_CONFIG_SPEC.md](../specs/TITLE_ENGINE_MARKETING_CONFIG_SPEC.md) — Config layer authority: consumer_language_by_topic.yaml replaces COMPLIANCE_FILTER and topic-level vocabulary; invisible_scripts_by_persona_topic.yaml replaces TOPIC_VOCABULARY.invisible_scripts; config-driven loader with fallback; generate_invisible_script() persona×topic sourcing. **Implementation complete** (config, loader, compliance + invisible_script wiring, check_marketing_config.py, marketing-config-gate.yml). COMPLIANCE_FILTER is currently parallel; deprecation to single source of truth in spec §9. |

### Scripts / code (consumers of deep research outputs)

| Item | Location |
|------|----------|
| **Title engine (v3)** | [phoenix_title_engine_v3.py](../phoenix_title_engine_v3.py) — `generate_invisible_script()`; title = search keyword + invisible script; persona×topic invisible_scripts in topic vocab |
| **Title engine (v4)** | [phoenix_title_engine_v4.py](../phoenix_title_engine_v4.py) — Config-driven invisible_script + compliance; loads `MarketingConfigLoader` from `config/marketing/`; falls back to hardcoded TOPIC_VOCABULARY if config absent; generates persona×topic scripts deterministically |
| **Title engine (legacy)** | [phoenix_title_engine.py](../phoenix_title_engine.py) — `invisible_script` in title model; picks from topic invisible_scripts |

### Config (marketing layer)

| Item | Location |
|------|----------|
| **Consumer language by topic** | [config/marketing/consumer_language_by_topic.yaml](../config/marketing/consumer_language_by_topic.yaml) — 14 topics × consumer_phrases, banned_clinical_terms, bridge_language, search_clusters, platform_risk_terms, persona_subtitle_patterns. Feeds title engine compliance filter and CI gate. Authority: marketing_deep_research/ scaffold 03. |
| **Invisible scripts by persona×topic** | [config/marketing/invisible_scripts_by_persona_topic.yaml](../config/marketing/invisible_scripts_by_persona_topic.yaml) — 140 entries (10 personas × 14 topics), 2 persona-specific invisible scripts each. Feeds HOOK atom seeds and title engine `generate_invisible_script()`. Authority: marketing_deep_research/ scaffold 04. |

### CI / validation

| Item | Location |
|------|----------|
| **Marketing config gate** | [scripts/ci/check_marketing_config.py](../scripts/ci/check_marketing_config.py) — Validates consumer_language_by_topic.yaml and invisible_scripts_by_persona_topic.yaml: referential integrity vs canonical topics/personas, required fields, minimum content, cross-file consistency, brand allowed_tokens vs clinical terms. Exit 1 on ERROR. `--strict` promotes WARNs to ERRORs. |
| **Marketing config CI workflow** | [.github/workflows/marketing-config-gate.yml](../.github/workflows/marketing-config-gate.yml) — Runs check_marketing_config.py on PRs touching config/marketing/**. Uses --strict on main branch pushes. |

### Use flow

1. **Run prompts:** Use [MARKETING_DEEP_RESEARCH_PROMPTS.md](./MARKETING_DEEP_RESEARCH_PROMPTS.md) (master or sub-prompts) in your deep research workflow.
2. **Outputs:** Structured YAML/JSON (e.g. per-brand GTM, emotional vocabulary, consumer language, invisible scripts, duration bands, cover language, pricing).
3. **Ingestion:** Consumer language → [config/marketing/consumer_language_by_topic.yaml](../config/marketing/consumer_language_by_topic.yaml); Invisible scripts → [config/marketing/invisible_scripts_by_persona_topic.yaml](../config/marketing/invisible_scripts_by_persona_topic.yaml). Both are now populated and loaded by the title engine.
4. **Authority:** [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) defines how invisible_script and belief_flip integrate into atoms and title philosophy. Config layer (consumer language, invisible scripts, loader, fallback) is specified in [TITLE_ENGINE_MARKETING_CONFIG_SPEC](../specs/TITLE_ENGINE_MARKETING_CONFIG_SPEC.md).

---

## Church & payout (distribution-only brands)

Church brands (e.g. NorCal Dharma) are identity/distribution only: no teacher, no Teacher Mode, no wave allocation. Display name from church YAML at runtime. **NorCal Dharma brand integration** is production-ready when [Brand guards](../.github/workflows/brand-guards.yml) is green on `main`: CI guards (matrix exclusion + assignments → default_teacher), secret scan on brand config, and runtime smoke tests pass.

### Church docs

- [docs/church_docs/README.md](./church_docs/README.md) — Church–brand linkage: brand_id → church record mapping, display name source, Cooperative Church Compliance YAML Schema reference, ops smoke
- **docs/norcal_dharma.yaml** — Church #1 canonical record (Cooperative Church Compliance YAML Schema). ⚠️ *file not present*; when added, link here.
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
- [docs/authoring/AUTHOR_COVER_ART_SYSTEM.md](./authoring/AUTHOR_COVER_ART_SYSTEM.md) — Author signature cover art base backgrounds (first 10 authors per catalog)
- [docs/WRITER_BRIEF_BOOK_001.md](./WRITER_BRIEF_BOOK_001.md) — Writer brief for Book_001
- [docs/WRITER_COMMS_SYSTEMS_100.md](./WRITER_COMMS_SYSTEMS_100.md) — Writer comms systems
- [docs/WRITER_SPEC_MARKDOWN_AND_DOCX.md](./WRITER_SPEC_MARKDOWN_AND_DOCX.md) — Writer spec (Markdown and DOCX)
- [docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) — First 10 books evaluation protocol

### Author cover art (document all)

Author signature cover art base backgrounds for the first 10 authors of every catalog; runtime resolver, pipeline output, CI gate. Launchable = teachers in brand_teacher_matrix + author_registry; each must have registry entry, PNG, style_hint, palette_tokens.

| Item | Location |
|------|----------|
| **Doc** | [docs/authoring/AUTHOR_COVER_ART_SYSTEM.md](./authoring/AUTHOR_COVER_ART_SYSTEM.md) — Registry, assets, generation, runtime, CI |
| **Registry** | [config/authoring/author_cover_art_registry.yaml](../config/authoring/author_cover_art_registry.yaml) — author_id → cover_art_base, style_hint, palette_tokens |
| **Resolver** | [phoenix_v4/planning/author_cover_art_resolver.py](../phoenix_v4/planning/author_cover_art_resolver.py) — `resolve_author_cover_art(author_id_or_teacher_id)`; fallback default |
| **Generator** | [scripts/generate_author_cover_art_bases.py](../scripts/generate_author_cover_art_bases.py) — Pure Python PNG gradients → `assets/authors/cover_art/{author_id}_base.png` |
| **Pipeline output** | [scripts/run_pipeline.py](../scripts/run_pipeline.py) — Plan JSON: `cover_art_base`, `cover_art_style_hint`, `cover_art_palette_tokens`, `cover_variant_id` |
| **CI gate** | [scripts/ci/check_author_cover_art.py](../scripts/ci/check_author_cover_art.py) — Launchable authors: registry + PNG + style/palette; exit 0/1 |
| **Production gates** | [scripts/run_production_readiness_gates.py](../scripts/run_production_readiness_gates.py) — **Gate 18:** author cover art |
| **Assets** | `assets/authors/cover_art/` — `{author_id}_base.png` (1080×1920); see [assets/authors/README.md](../assets/authors/README.md) |

---

## Enlightened Intelligence (EI) — V1 & V2 (document all)

Single index: every doc, module, config, test, script, and artifact for the Enlightened Intelligence subsystem. EI V1 is the production candidate-selection pipeline (heuristic scoring, embedding thesis alignment, LLM tie-break, teacher integrity). EI V2 is a parallel enhancement layer with 6 new AI techniques (cross-encoder reranking, domain-tuned embeddings, few-shot safety classifiers, semantic dedup, emotion arc validation, TTS readability). V2 runs alongside V1 for A/B comparison and never overrides V1 in production.

EI V1 is 100% at **test slice** when the 4 targeted unit tests pass. It is **100% production-ready** only when all operational gates are confirmed on `main` with evidence links (see [ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md](./ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md)).

### Operational gates (production 100%)

1. Merge to `main`
2. CI green on `main`
3. Runtime/scheduled smoke passes
4. Secrets (embedding/LLM API keys if used) verified
5. Checklist doc completed with evidence links
6. Rollback procedure validated

### Architecture

| Layer | Purpose | Authority |
|-------|---------|-----------|
| **EI V1 (production)** | Per-slot candidate selection: heuristic scoring (somatic, concreteness, risk), embedding thesis alignment, teacher integrity penalties, deterministic hash or GA-best selector, optional LLM tie-break | `ei_adapter.py` |
| **EI V2 (parallel/advisory)** | 6 enhanced AI modules: cross-encoder reranking, domain-tuned embeddings, few-shot safety classifiers, semantic dedup, emotion arc validation, TTS readability scoring. Config-gated, fail-open, deterministic | `ei_v2/__init__.py` |
| **Parallel adapter** | Runs V1 + V2 on the same candidates, compares selections, produces comparison reports. V1 always wins; V2 is advisory only | `ei_parallel_adapter.py` |
| **Rigorous eval harness** | 10-dimension quality scoring (therapeutic, engagement, journey, listen experience, marketability, safety, uniqueness, somatic precision, emotional coherence, cohesion) + V1/V2 slot comparison + timing benchmarks | `run_ei_v2_rigorous_eval.py` |

### Docs

| Item | Location |
|------|----------|
| **Production checklist** | [docs/ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md](./ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md) — Test slice (4 tests) + 6 operational gates; pre-merge verification, rollback procedure |
| **EI registry** | `config/source_of_truth/enlightened_intelligence_registry.yaml` ⚠️ *file not present* — EI registry: slots, llm_judge, embeddings, teacher_integrity |

### EI / Release docs

| Item | Location |
|------|----------|
| **EI V2 rollout proof checklist** | `docs/EI_V2_ROLLOUT_PROOF_CHECKLIST.md` — Manual steps to confirm EI V2 gates green, 3 consecutive main runs, branch protection; includes proof template and branch-protection evidence link |

### EI V1 modules (production)

| Module | Location | Purpose |
|--------|----------|---------|
| **EI adapter (main entry)** | [phoenix_v4/quality/ei_adapter.py](../phoenix_v4/quality/ei_adapter.py) | `apply_ei_selection()`: threshold gates, heuristic scoring (somatic precision, concreteness, risk penalty), embedding thesis alignment, teacher integrity penalties, deterministic hash selector (`rule_best`) or score selector (`ga_best`), optional LLM tie-break. Composite: somatic 0.25 + concreteness 0.25 + thesis 0.35 − risk 0.25 − teacher_penalty 0.10 |
| **Embedding thesis alignment** | [phoenix_v4/quality/ei_embeddings.py](../phoenix_v4/quality/ei_embeddings.py) | `thesis_similarity()`: cosine similarity between thesis and candidate embeddings. `EmbeddingCache` with SQLite backend. `get_embedding()` with pluggable `embed_fn` |
| **LLM judge (tie-break)** | [phoenix_v4/quality/ei_llm_judge.py](../phoenix_v4/quality/ei_llm_judge.py) | `judge_tie_break()`: builds structured therapeutic rubric prompt, calls LLM, returns `LLMJudgeResult`. JSONL cache for determinism |
| **Teacher integrity** | [phoenix_v4/quality/teacher_integrity.py](../phoenix_v4/quality/teacher_integrity.py) | `compute_teacher_integrity_penalty()`: phrase-matching for promotional tone, miracle claims, sectarian superiority, endorsement implication. `TeacherIntegrityPenalty` dataclass with softening for allowlisted phrases |

### EI V2 modules (parallel/advisory)

| Module | Location | Purpose |
|--------|----------|---------|
| **V2 entry point** | [phoenix_v4/quality/ei_v2/\_\_init\_\_.py](../phoenix_v4/quality/ei_v2/__init__.py) | `run_ei_v2_analysis()`: orchestrates all enabled V2 modules based on config. Returns `EIV2AnalysisReport` with per-candidate scores and V2 recommendation. `_select_v2_best()` for composite V2 scoring |
| **Config loader** | [phoenix_v4/quality/ei_v2/config.py](../phoenix_v4/quality/ei_v2/config.py) | `load_ei_v2_config()`: loads defaults + merges from `config/quality/ei_v2_config.yaml`. All modules disabled by default; YAML enables them. Cached after first load |
| **Cross-encoder reranker** | [phoenix_v4/quality/ei_v2/cross_encoder_reranker.py](../phoenix_v4/quality/ei_v2/cross_encoder_reranker.py) | `rerank_candidates()`: scores thesis-candidate relevance via semantic field overlap, token overlap (Jaccard), positional bonuses. Default `heuristic` mode; pluggable model callback. `_SEMANTIC_FIELDS` for domain terms |
| **Safety classifier** | [phoenix_v4/quality/ei_v2/safety_classifier.py](../phoenix_v4/quality/ei_v2/safety_classifier.py) | `classify_safety()`: expanded pattern detection for medical claims, clinical language, promotional content, reassurance spam, pathologizing language. Negation handling. Default `heuristic_plus` mode; pluggable LLM |
| **Domain embeddings** | [phoenix_v4/quality/ei_v2/domain_embeddings.py](../phoenix_v4/quality/ei_v2/domain_embeddings.py) | `domain_thesis_similarity()`: combines thesis alignment (token/semantic overlap) with persona affinity (`_PERSONA_LEXICONS`) and topic coherence (`_TOPIC_LEXICONS`). Default `weighted` heuristic mode; pluggable `embed_fn` |
| **Semantic dedup** | [phoenix_v4/quality/ei_v2/semantic_dedup.py](../phoenix_v4/quality/ei_v2/semantic_dedup.py) | `detect_semantic_duplicates()`: word/char n-grams, paragraph shape similarity, narrative beat fingerprinting (`_BEAT_PATTERNS`). Default `ngram_plus_embedding` mode |
| **Emotion arc validator** | [phoenix_v4/quality/ei_v2/emotion_arc_validator.py](../phoenix_v4/quality/ei_v2/emotion_arc_validator.py) | `validate_emotion_arc()`: internal valence/arousal lexicons score paragraph emotional trajectory against expected BAND values and `emotional_role`. Returns PASS/WARN/FAIL with deviation details |
| **TTS readability** | [phoenix_v4/quality/ei_v2/tts_readability.py](../phoenix_v4/quality/ei_v2/tts_readability.py) | `score_tts_readability()`: sentence length distribution, rhythm variance, paragraph breaks, problematic TTS patterns (parenthetical, em-dash chains, all-caps), rhetorical questions. Composite 0–1 score |

### Parallel adapter

| Module | Location | Purpose |
|--------|----------|---------|
| **Parallel adapter** | [phoenix_v4/quality/ei_parallel_adapter.py](../phoenix_v4/quality/ei_parallel_adapter.py) | `compare_slot()`: runs V1 + V2 on identical candidates, returns `SlotComparisonResult`. `build_pipeline_comparison()`: aggregates into `PipelineComparisonReport`. `write_comparison_report()`: JSON + human-readable summary |

### Config

| Item | Location |
|------|----------|
| **EI V2 config** | [config/quality/ei_v2_config.yaml](../config/quality/ei_v2_config.yaml) — Enable/disable each V2 module, set modes (`heuristic`, `heuristic_plus`, `model`), thresholds, composite weights (rerank 0.35, safety 0.25, domain_similarity 0.20, tts_readability 0.20) |
| **EI registry** | `config/source_of_truth/enlightened_intelligence_registry.yaml` ⚠️ *file not present* |

### Tests

| Item | Location |
|------|----------|
| **EI V2 test suite** | [tests/test_ei_v2.py](../tests/test_ei_v2.py) — 28 tests: cross-encoder reranker, safety classifier, semantic dedup, emotion arc validator, TTS readability, domain embeddings, V2 orchestration, config loading, parallel adapter comparison, pipeline report generation |

### Scripts (evaluation)

| Item | Location |
|------|----------|
| **Rigorous eval harness** | [scripts/ci/run_ei_v2_rigorous_eval.py](../scripts/ci/run_ei_v2_rigorous_eval.py) — Compiles + renders books across persona × topic × engine matrix, evaluates each chapter on 10 quality dimensions (therapeutic value, emotional coherence, engagement, chapter journey, cohesion, listen experience, marketability, safety compliance, content uniqueness, somatic precision), runs V1/V2 slot comparison, benchmarks timing. Flags: `--full` (7 books), `--sample N`. Outputs: `artifacts/ei_v2/eval_rigorous_report.json`, `artifacts/ei_v2/eval_rigorous_summary.txt` |
| **Catalog calibrator** | `scripts/ci/run_ei_v2_catalog_calibration.py` — Runs V2 dimension gates across all compilable catalog combos, discovers optimal percentile thresholds, feeds learner. Flags: `--learn`, `--out`. Output: `artifacts/ei_v2/catalog_calibration.json` |

### Pipeline integration

| Item | Location | Purpose |
|------|----------|---------|
| **`--ei-v2-compare` flag** | [scripts/run_pipeline.py](../scripts/run_pipeline.py) | Post-render, runs `ei_parallel_adapter.compare_slot` for every atom in the book. Non-blocking try-except ensures V2 errors never halt the main pipeline. Outputs: `artifacts/ei_v2/ei_v1_v2_comparison.json`, `artifacts/ei_v2/ei_v1_v2_summary.txt` |
| **`--ei-hybrid` flag** | [scripts/run_pipeline.py](../scripts/run_pipeline.py) | Activates hybrid V1+V2 selector: V1 picks → V2 scores → risk blocks → margin override → dimension gates → learner feedback. Per-book enforcement with catalog-calibrated thresholds. |

### Artifacts

| Item | Location |
|------|----------|
| **V1/V2 comparison report** | `artifacts/ei_v2/ei_v1_v2_comparison.json` — Per-slot V1 vs V2 chosen candidate, scores, timing, agreement rate |
| **V1/V2 summary** | `artifacts/ei_v2/ei_v1_v2_summary.txt` — Human-readable executive summary: agreement rate, safety/dedup/TTS/arc flags, timing |
| **Rigorous eval report** | `artifacts/ei_v2/eval_rigorous_report.json` — Full 10-dimension quality data for all evaluated books + V1/V2 comparison per slot |
| **Rigorous eval summary** | `artifacts/ei_v2/eval_rigorous_summary.txt` — Dimension scorecard, per-book breakdown, performance benchmarks, weakest-to-strongest ranking |
| **Catalog calibration** | `artifacts/ei_v2/catalog_calibration.json` — Percentile thresholds per dimension from whole-catalog sweep |
| **Learned params** | `artifacts/ei_v2/learned_params.json` — Adaptive composite weights, override margin, per-persona/topic adjustments |
| **Learner feedback** | `artifacts/ei_v2/learner_feedback.jsonl` — Append-only log of every hybrid decision (override/keep) with full scores |

### V2 composite weights

The V2 best-candidate selector uses these weights (configurable in `ei_v2_config.yaml`):

| Dimension | Weight |
|-----------|--------|
| Cross-encoder rerank score | 0.35 |
| Safety compliance (1 − risk) | 0.25 |
| Domain thesis similarity | 0.20 |
| TTS readability composite | 0.20 |

### Rigorous eval quality dimensions

The 10-dimension audiobook quality rubric (scored per chapter, aggregated per book):

| # | Dimension | Weight | What it measures |
|---|-----------|--------|-----------------|
| 1 | Therapeutic Value | 0.15 | Recognition-first language, non-pathologizing, earned insight |
| 2 | Emotional Coherence | 0.12 | Chapter arc matches blueprint BAND + emotional_role |
| 3 | Engagement | 0.12 | Hook strength, narrative tension markers, forward momentum |
| 4 | Chapter Journey | 0.12 | Clear point per chapter, progression signals, actionable takeaway |
| 5 | Cohesion | 0.08 | Cross-chapter thread references, motif continuity |
| 6 | Listen Experience | 0.12 | TTS readability: rhythm, sentence length, breath points, pacing |
| 7 | Marketability | 0.10 | Invisible script feel, persona-specific language, concrete detail |
| 8 | Safety Compliance | 0.08 | No medical claims, clinical language, promotional content |
| 9 | Content Uniqueness | 0.05 | No duplicate atoms/structures across chapters |
| 10 | Somatic Precision | 0.06 | Body-grounded moments, concrete sensory detail |

### Latest eval results (baseline)

Evaluated 6 books (78 chapters, 33,007 words) across 3 personas. Key findings:

| Grade | Score | Dimension |
|-------|-------|-----------|
| A | 0.995 | Safety Compliance |
| A | 0.939 | Emotional Coherence |
| B | 0.710 | Therapeutic Value |
| B | 0.619 | Chapter Journey |
| C | 0.590 | Listen Experience |
| C | 0.424 | Cohesion |
| D | 0.362 | Somatic Precision |
| D | 0.298 | Marketability |
| D | 0.269 | Engagement |
| F | 0.021 | Content Uniqueness |

V1/V2 agreement rate: 20.4% across 431 slots. V2 flagged 698 dedup issues, 381 TTS problems, 65 arc concerns, 0 safety issues. V2 per-slot cost: 6.16ms (vs V1: 0.28ms). Total per-book: ~956ms avg.

### V2 promotion gates

V2 cannot replace V1 until **all five gates pass for 5 consecutive CI runs**. `auto_promote` is OFF; manual approval required even after criteria are met.

| Gate | Criteria | Current |
|------|----------|---------|
| **1. Quality** | Composite >= 0.55; per-dimension floors (safety >= 0.95, emotional_coherence >= 0.85, etc.); agreement rate >= 10% | PASS |
| **2. Performance** | V2 per-slot <= 50ms; V2/V1 ratio <= 100x; per-book overhead <= 5000ms | PASS |
| **3. Safety** | Zero safety regressions; compliance >= 0.95; V2 must catch everything V1 catches | FAIL (2 chapter-level regressions) |
| **4. Dimension gates** | Max 20% chapter fail rate; per-dimension pass rates (uniqueness >= 70%, engagement >= 60%, etc.); max 3 gate failures per book | NEW |
| **5. Hybrid override** | Override success rate >= 60%; override rate <= 40%; block rate <= 20% | NEW |

Current status: **BLOCKED** — 0/5 consecutive passes. V1 is authoritative.

| Item | Location |
|------|----------|
| **Promotion criteria config** | [config/quality/ei_v2_promotion_criteria.yaml](../config/quality/ei_v2_promotion_criteria.yaml) — Five gates (quality, performance, safety, dimension gates, hybrid override), consecutive pass requirement, auto_promote flag |
| **Promotion gate checker** | [scripts/ci/check_ei_v2_promotion_gate.py](../scripts/ci/check_ei_v2_promotion_gate.py) — Reads eval report + criteria, checks all gates, appends to history, writes `promotion_gate_result.json` |
| **CI workflow** | [.github/workflows/ei-v2-gates.yml](../.github/workflows/ei-v2-gates.yml) — Runs on EI code changes + weekly: unit tests → rigorous eval (3 books) → catalog calibration + learner → promotion gate check. Uploads evidence artifacts |
| **Promotion history** | `artifacts/ei_v2/promotion_history.jsonl` — Append-only log of gate results per run; used for consecutive-pass tracking |
| **Promotion result** | `artifacts/ei_v2/promotion_gate_result.json` — Latest gate check breakdown: pass/fail per gate, issues, consecutive count |

### Hybrid V1+V2 selector

Layered selection with override logic. V1 picks the winner; V2 scores the same candidates and can override or block when quality thresholds are met.

| Item | Location |
|------|----------|
| **Hybrid selector** | `phoenix_v4/quality/ei_v2/hybrid_selector.py` — V1 picks → V2 scores → risk blocks → margin override → log for learner |
| **Learning system** | `phoenix_v4/quality/ei_v2/learner.py` — EMA-based weight/threshold tuning from hybrid feedback; per-persona/topic adjustments |
| **Dimension gates** | `phoenix_v4/quality/ei_v2/dimension_gates.py` — Per-chapter enforcement: uniqueness, engagement, somatic precision, listen experience, cohesion |
| **Catalog calibrator** | `scripts/ci/run_ei_v2_catalog_calibration.py` — Catalog-level threshold discovery; feeds learner with whole-catalog observations |
| **Tests** | `tests/test_ei_v2_hybrid.py` — 25 tests: learner, dimension gates, hybrid selector, config, integration |
| **Learned params** | `artifacts/ei_v2/learned_params.json` — Latest learned composite weights, override margin, per-persona/topic adjustments |
| **Learner feedback** | `artifacts/ei_v2/learner_feedback.jsonl` — Append-only log of every hybrid decision (override/keep) with full scores |
| **Calibration report** | `artifacts/ei_v2/catalog_calibration.json` — Percentile thresholds per dimension from catalog sweep |

**Override rule (keeps V1 unless all true):**
1. `v2_best - v2_v1_winner >= margin` (default 0.12, learner-tunable)
2. No safety violation on V2 pick
3. Dedup risk below cap (0.6)
4. Arc deviation below cap (0.5)

**Dimension gate enforcement:**

| Dimension | Key checks | Fail = |
|-----------|-----------|--------|
| **Uniqueness** | Dedup similarity caps, banned repeated structures | Content too similar across chapters |
| **Engagement** | Hook density, tension markers, pull-forward lines | Flat, no narrative drive |
| **Somatic precision** | Body-signal atom count, somatic lexicon density | Generic, not embodied |
| **Listen experience** | TTS readability composite | Unlistenable as audiobook |
| **Cohesion** | Cross-chapter thread references | Disconnected chapters |

**Promotion plan (3-phase):**
1. **Catalog calibration** — Run V2 on whole catalog to set thresholds (global policy)
2. **Per-book hybrid** — Run hybrid override in production per book
3. **Scope expansion** — Gradually increase override scope by format/persona/topic once stable

**Pipeline flag:** `--ei-hybrid` on `run_pipeline.py` activates hybrid mode (V1 + V2 layered + dimension gates + learner)

---

## Manuscript quality (Tier 0 contract)

**Feature = complete.** Tier 0 contract, canary gate, and trend dashboard are implemented. **Production 100%** requires the full operational checklist: CI/release gates on `main`, branch protection, smoke runs, evidence, rollback proof. See [docs/PRODUCTION_READINESS_GO_NO_GO.md](./PRODUCTION_READINESS_GO_NO_GO.md), [docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md).

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

All test files under `tests/`. Core tests workflow runs fast set (`-m "not slow"`); slow tests (atoms coverage, teacher E2E) run in release-gates or separately.

### Test infrastructure

| Item | Location |
|------|----------|
| **Test dependencies** | [requirements-test.txt](../requirements-test.txt) — pytest, pyyaml, jsonschema, feedparser |
| **Pytest config** | [pytest.ini](../pytest.ini) — markers (slow, integration, e2e), testpaths |
| **Shared fixtures** | [tests/conftest.py](../tests/conftest.py) — repo_root, fixtures_dir, config_root, atoms_root |

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
| [tests/test_ei_v2.py](../tests/test_ei_v2.py) | EI V2 test suite: 28 tests — cross-encoder, safety, dedup, arc, TTS, domain embeddings, V2 orchestration, config, parallel adapter |

---

## Coverage & ops

- [docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md](./TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md) — Tuple viability and coverage health (preflight gate, weekly report)
- [docs/COVERAGE_HEALTH_JSON_SCHEMA.md](./COVERAGE_HEALTH_JSON_SCHEMA.md) — Coverage health JSON dashboard schema
- [docs/TITLE_AND_CATALOG_MARKETING_SYSTEM.md](./TITLE_AND_CATALOG_MARKETING_SYSTEM.md) — Title and catalog marketing system
- [docs/PHASE_13_C_WAVE_OPTIMIZER.md](./PHASE_13_C_WAVE_OPTIMIZER.md) — Phase 13 C wave optimizer
- [docs/V4_FEATURES_SCALE_AND_KNOBS.md](./V4_FEATURES_SCALE_AND_KNOBS.md) — V4 features, scale, and knobs

---

## V4 features, scale & knobs (document all)

**Single reference:** [docs/V4_FEATURES_SCALE_AND_KNOBS.md](./V4_FEATURES_SCALE_AND_KNOBS.md) — All V4 features (§1), scale parts and anti-spam assurance (§2), and every knob: pipeline CLI (§3.1), asset/observability CLI (§3.2), CI/QA flags (§3.3), full catalog and quality tools (§3.4), thresholds in code (§3.5), emotional governance (§3.6), config YAML (§3.7), Teacher Mode knobs (§3.8), CTSS weights (§3.9), systems test (§3.10). **Use:** To change behavior, adjust the relevant config or script constant; then run systems test and production gates. Full inventory below.

### Docs

| Item | Location |
|------|----------|
| **V4 features, scale, knobs** | [docs/V4_FEATURES_SCALE_AND_KNOBS.md](./V4_FEATURES_SCALE_AND_KNOBS.md) — Single reference (this domain) |
| **Systems V4** | [docs/SYSTEMS_V4.md](./SYSTEMS_V4.md) — V4 systems overview; §8 systems test |
| **Arc-First canonical spec** | [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) — Sole architecture authority |
| **Rigorous system test** | [docs/RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) — Simulation = readiness; production 100% requirements |
| **Practice library teacher fallback** | [docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md](./PRACTICE_LIBRARY_TEACHER_FALLBACK.md) — Doctrine wrapper for EXERCISE backstop |
| **Practice item schema** | [specs/PRACTICE_ITEM_SCHEMA.md](../specs/PRACTICE_ITEM_SCHEMA.md) — Practice item YAML schema |
| **Compiled plan schema contract** | [specs/COMPILED_PLAN_SCHEMA_CONTRACT.md](../specs/COMPILED_PLAN_SCHEMA_CONTRACT.md) — BookSpec, FormatPlan, CompiledBook |
| **Creative quality validation checklist** | [docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md](./CREATIVE_QUALITY_VALIDATION_CHECKLIST.md) — Human checkpoint |
| **First 10 books evaluation protocol** | [docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) — Human checkpoint |
| **Quality tools README** | [phoenix_v4/quality/README.md](../phoenix_v4/quality/README.md) — Story lint, heatmap, memorable lines, marketing assets |
| **Release velocity and schedule** | [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md) — Pacing; generate_weekly_schedule.py |
| **Unified personas** | [unified_personas.md](../unified_personas.md) — 10 active personas, 12 active topics (canonical source) |

### Scripts (pipeline, asset, CI/QA, quality)

| Item | Location |
|------|----------|
| **Run pipeline** | [scripts/run_pipeline.py](../scripts/run_pipeline.py) — Full 6-stage; --topic, --persona, --arc, --teacher, --author, --render-book, --generate-freebies, etc. |
| **Render plan to txt** | [scripts/render_plan_to_txt.py](../scripts/render_plan_to_txt.py) — Stage 6 standalone render |
| **Plan freebie assets** | [scripts/plan_freebie_assets.py](../scripts/plan_freebie_assets.py) — Catalog or canonical; manifest output |
| **Create freebie assets** | [scripts/create_freebie_assets.py](../scripts/create_freebie_assets.py) — HTML, PDF, EPUB, MP3 |
| **Validate asset store** | [scripts/validate_asset_store.py](../scripts/validate_asset_store.py) — Store vs manifest |
| **Update similarity index** | `scripts/update_similarity_index.py` — Append CTSS row |
| **Build structural drift dashboard** | `scripts/build_structural_drift_dashboard.py` — artifacts/drift/ |
| **Run simulation** | [simulation/run_simulation.py](../simulation/run_simulation.py) — --n, --phase2, --phase3 |
| **Pre-export check (Gate #49)** | [scripts/distribution/pre_export_check.py](../scripts/distribution/pre_export_check.py) — Locale/territory consistency |
| **Check structural entropy** | [scripts/ci/check_structural_entropy.py](../scripts/ci/check_structural_entropy.py) — Min words, family dominance, teacher-mode checks |
| **Check author positioning** | [scripts/ci/check_author_positioning.py](../scripts/ci/check_author_positioning.py) — Profile language bands |
| **Check platform similarity** | [scripts/ci/check_platform_similarity.py](../scripts/ci/check_platform_similarity.py) — CTSS block/review thresholds |
| **Check wave density** | [scripts/ci/check_wave_density.py](../scripts/ci/check_wave_density.py) — Arc/band/slot/ex/role share limits |
| **Validate freebie density** | [phoenix_v4/qa/validate_freebie_density.py](../phoenix_v4/qa/validate_freebie_density.py) — Bundle/CTA/slug thresholds |
| **CTA signature caps** | [phoenix_v4/qa/cta_signature_caps.py](../phoenix_v4/qa/cta_signature_caps.py) — Per brand/quarter cap |
| **Check book output no placeholders** | [scripts/ci/check_book_output_no_placeholders.py](../scripts/ci/check_book_output_no_placeholders.py) — Delivery gate (§10.6) |
| **Run production readiness gates** | [scripts/run_production_readiness_gates.py](../scripts/run_production_readiness_gates.py) — 15 + optional gate 16 |
| **Run systems test** | [scripts/systems_test/run_systems_test.py](../scripts/systems_test/run_systems_test.py) — Phases 1–7 |
| **Generate full catalog** | [scripts/generate_full_catalog.py](../scripts/generate_full_catalog.py) — Portfolio → BookSpec → compile → wave |
| **Story atom lint** | [phoenix_v4/quality/story_atom_lint.py](../phoenix_v4/quality/story_atom_lint.py) — STORY specificity, conflict, cost, pivot |
| **Transformation heatmap** | [phoenix_v4/quality/transformation_heatmap.py](../phoenix_v4/quality/transformation_heatmap.py) — Per-chapter recognition/reframe/challenge |
| **Memorable line detector** | [phoenix_v4/quality/memorable_line_detector.py](../phoenix_v4/quality/memorable_line_detector.py) — Highlight-density candidates |
| **Marketing assets from lines** | [phoenix_v4/quality/marketing_assets_from_lines.py](../phoenix_v4/quality/marketing_assets_from_lines.py) — Quotes, pin captions, trailer lines |
| **Practice library scripts** | `scripts/practice/` — Ingest, normalize, validate (practice_items store) |
| **Practice safety lint** | [phoenix_v4/qa/practice_safety_lint.py](../phoenix_v4/qa/practice_safety_lint.py) — EXERCISE backstop safety |
| **Teacher gap-fill / approve** | [tools/teacher_mining/gap_fill.py](../tools/teacher_mining/gap_fill.py); approve_atoms, report_teacher_gaps (see Teacher Mode section) |
| **Wave orchestrator** | [phoenix_v4/planning/wave_orchestrator.py](../phoenix_v4/planning/wave_orchestrator.py) — Balanced wave from candidates |
| **Monte Carlo CTSS** | [simulation/run_monte_carlo_ctss.py](../simulation/run_monte_carlo_ctss.py) — Duplication risk vs index |

### Config (knobs per V4_FEATURES §3.6, 3.7, 3.8)

| Item | Location |
|------|----------|
| **Topic/engine bindings** | [config/topic_engine_bindings.yaml](../config/topic_engine_bindings.yaml) — allowed_engines per topic |
| **Identity aliases** | [config/identity_aliases.yaml](../config/identity_aliases.yaml) — persona_aliases, topic_aliases |
| **Format registry** | [config/format_selection/format_registry.yaml](../config/format_selection/format_registry.yaml) — structural/runtime formats, tier |
| **Format selection rules** | [config/format_selection/selection_rules.yaml](../config/format_selection/selection_rules.yaml) — topic_complexity, installment_strategy |
| **Emotional role slot requirements** | [config/format_selection/emotional_role_slot_requirements.yaml](../config/format_selection/emotional_role_slot_requirements.yaml) — Role→slot |
| **Chapter planner policies** | [config/source_of_truth/chapter_planner_policies.yaml](../config/source_of_truth/chapter_planner_policies.yaml) — Arc-role, quotas, slot policy |
| **Master arcs / engines** | [config/source_of_truth/master_arcs/](../config/source_of_truth/master_arcs/), [config/source_of_truth/engines/](../config/source_of_truth/engines/) |
| **Capacity constraints** | [config/catalog_planning/capacity_constraints.yaml](../config/catalog_planning/capacity_constraints.yaml) |
| **Brand teacher matrix** | [config/catalog_planning/brand_teacher_matrix.yaml](../config/catalog_planning/brand_teacher_matrix.yaml) |
| **Teacher persona matrix** | [config/catalog_planning/teacher_persona_matrix.yaml](../config/catalog_planning/teacher_persona_matrix.yaml) |
| **Brand teacher assignments** | [config/catalog_planning/brand_teacher_assignments.yaml](../config/catalog_planning/brand_teacher_assignments.yaml) |
| **Teacher registry** | [config/teachers/teacher_registry.yaml](../config/teachers/teacher_registry.yaml) |
| **Brand archetype registry** | [config/catalog_planning/brand_archetype_registry.yaml](../config/catalog_planning/brand_archetype_registry.yaml) |
| **Author positioning profiles** | [config/authoring/author_positioning_profiles.yaml](../config/authoring/author_positioning_profiles.yaml) |
| **Freebie selection rules** | [config/freebies/freebie_selection_rules.yaml](../config/freebies/freebie_selection_rules.yaml) |
| **CTA anti-spam** | [config/freebies/cta_anti_spam.yaml](../config/freebies/cta_anti_spam.yaml) — density_thresholds, max_same_cta_signature |
| **Emotional governance rules** | [phoenix_v4/qa/emotional_governance_rules.yaml](../phoenix_v4/qa/emotional_governance_rules.yaml) — chapter, tts_rhythm, book, catalog |
| **Release wave controls** | [config/release_wave_controls.yaml](../config/release_wave_controls.yaml) — weekly_caps, anti_homogeneity |
| **Practice selection rules** | [config/practice/selection_rules.yaml](../config/practice/selection_rules.yaml) — EXERCISE_BACKSTOP |
| **Practice validation** | [config/practice/validation.yaml](../config/practice/validation.yaml) |
| **Angle registry** | [config/angles/angle_registry.yaml](../config/angles/angle_registry.yaml) |
| **Validation (assets)** | [config/validation.yaml](../config/validation.yaml) — duration, file_size (MP3) |
| **TTS engines** | [config/tts/engines.yaml](../config/tts/engines.yaml) |
| **Asset lifecycle** | [config/asset_lifecycle.yaml](../config/asset_lifecycle.yaml) — regenerate_when, auto_prune |
| **Canonical topics/personas** | [config/catalog_planning/canonical_topics.yaml](../config/catalog_planning/canonical_topics.yaml), [config/catalog_planning/canonical_personas.yaml](../config/catalog_planning/canonical_personas.yaml) |

### Artifacts

| Item | Location |
|------|----------|
| **Similarity index** | `artifacts/catalog_similarity/index.jsonl` — CTSS fingerprint per plan |
| **Drift dashboard** | `artifacts/drift/` — Role distribution, signatures (from build_structural_drift_dashboard.py) |
| **Freebies index** | `artifacts/freebies/index.jsonl` — Plan rows for freebie density gate |
| **CTA signature index** | `artifacts/freebies/cta_signature_index.jsonl` — Optional; CTA caps |
| **Rendered books** | `artifacts/rendered/<plan_id>/book.txt` — Stage 6 output |
| **Practice store** | `SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl` — EXERCISE backstop source |

### Pipeline modules (phoenix_v4)

| Item | Location |
|------|----------|
| **Chapter planner** | [phoenix_v4/planning/chapter_planner.py](../phoenix_v4/planning/chapter_planner.py) — Stage 3 policy layer |
| **Angle resolver / bias** | [phoenix_v4/planning/angle_resolver.py](../phoenix_v4/planning/angle_resolver.py), angle_bias.py |
| **Practice selector** | [phoenix_v4/planning/practice_selector.py](../phoenix_v4/planning/practice_selector.py) — get_backstop_pool() |
| **Prose resolver / book renderer** | phoenix_v4.rendering — atom_id → prose; TxtWriter, render_book |
| **Validate compiled plan / arc alignment** | phoenix_v4 validators |

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

Translation and validation pipeline: parallel sharded translation (atoms + exercises) to all locales (zh-CN, zh-TW, zh-HK, zh-SG, yue, ja-JP, ko-KR), deterministic validation (schema, locale script, coverage, meta/leakage, repetition), merge + global QA, golden regression. Infrastructure now complete: all scripts & CI workflows deployed.

### All-locale production readiness (verified state)

| Dimension | Status |
|-----------|--------|
| **Docs/planning readiness** | **High** — content_roots_by_locale.yaml, LOCALE_PERSONAS.md, LOCALE_CATALOG_MARKETING_PLAN.md, ZH_CN_DISTRIBUTION_PLAN.md exist |
| **All-locale runtime production readiness** | **Not 100% yet** |

**Remaining: Translation execution pending (infrastructure 100%):**

1. **Locale atom stubs created** — `atoms/zh-CN`, `atoms/zh-TW`, `atoms/ja-JP`, etc. now exist with TRANSLATION PENDING stubs via `scripts/scaffold_locale_atom_stubs.py`.
2. **Translation execution script deployed** — `scripts/translate_atoms_all_locales_cloud.py` now present; runs parallel sharded translation via OpenAI API.
3. **Translation pipeline ready** — CI workflows deployed (`.github/workflows/translate-atoms-qwen-matrix.yml`, `.github/workflows/locale-gate.yml`); infrastructure complete; execution pending API call.

### Docs

| Item | Location |
|------|----------|
| **Locale personas** | [docs/LOCALE_PERSONAS.md](./LOCALE_PERSONAS.md) — 40 persona definitions across 11 non-en-US locales (anxious_insomniac_tw, burned_out_professional_tw, etc.) |
| **All-locale catalog marketing plan** | [docs/LOCALE_CATALOG_MARKETING_PLAN.md](./LOCALE_CATALOG_MARKETING_PLAN.md) — Per-locale positioning, go-live checklists, readiness tracker for all 12 locales |
| **zh-CN distribution plan** | [docs/ZH_CN_DISTRIBUTION_PLAN.md](./ZH_CN_DISTRIBUTION_PLAN.md) — Local platform pipeline (Ximalaya, NetEase, WeChat Read, Dedao); Phase 5 prerequisite checklist |
| **Locale strategy (rollout phases)** | [del_location_plan/locale_strategy.md](../del_location_plan/locale_strategy.md) — One brand = one locale; Phase 1–5 rollout; distribution routing; CI gate #49 |
| **Locale prose & prompting** | `docs/LOCALE_PROSE_AND_PROMPTING.md` ⚠️ *file not present* |
| **Multilingual architecture** | `docs/MULTILINGUAL_ARCHITECTURE.md` ⚠️ *file not present* |
| **Korean market & prose** | `docs/KOREA_MARKET_AND_PROSE.md` ⚠️ *file not present* |
| **Japanese market self-help** | `docs/JAPANESE_MARKET_SELFHELP_GUIDE.md` ⚠️ *file not present* |

### Scripts

| Item | Location |
|------|----------|
| **Translate atoms/exercises (cloud)** | `scripts/translate_atoms_all_locales_cloud.py` — Parallel sharded translation to all locales; runs N shards in parallel, each shard translates atoms/exercises via OpenAI API |
| **Scaffold locale atom stubs** | `scripts/scaffold_locale_atom_stubs.py` — Create TRANSLATION PENDING stub files for all atom types in a locale directory |
| **Validate translations** | `scripts/validate_translations.py` — Structure check, script encoding check, glossary consistency, golden regression |
| **Merge translation shards** | `scripts/merge_translation_shards.py` — Merges parallel shard outputs into locale atom tree; conflict detection |
| **Golden translation regression** | `scripts/check_golden_translation.py` — Regression check against golden translation samples per locale |
| **Native prompts / eval / learn** | `scripts/native_prompts_eval_learn.py` — Generates native-speaker evaluation prompts (4 dimensions: Fluency, Register, Term Consistency, Structure); output: `artifacts/evaluations/{locale}/` |

### Config & quality contracts

| Item | Location |
|------|----------|
| **Content roots by locale** | [config/localization/content_roots_by_locale.yaml](../config/localization/content_roots_by_locale.yaml) — Maps all 12 locales to atoms_root, translation paths, TTS constraints, rollout phase, and distribution blockers. |
| **Locale registry** | [config/localization/locale_registry.yaml](../config/localization/locale_registry.yaml) — All 12 locale definitions: language, script, TTS provider, storefront IDs, distribution rules. |
| **Brand locale extension** | [config/localization/brand_registry_locale_extension.yaml](../config/localization/brand_registry_locale_extension.yaml) — Per-brand locale and territory. One brand = one locale. |

**Quality contracts** — `config/localization/quality_contracts/` — Present on disk. Contains: `glossary.yaml` (28 terms × 11 locales), `release_thresholds.yaml` (phase-based thresholds), `golden_translation_regression.yaml` (5 golden samples), `README.md`, `INTEGRATION_GUIDE.md`.

### CI / workflow

`.github/workflows/translate-atoms-qwen-matrix.yml` — Parallel sharded translation workflow; triggered manually or weekly; runs N shards in matrix, merges results, validates all locales.

### Artifacts

| Item | Location |
|------|----------|
| **Shard output** | `{out_root}/{locale}/shard_{n}/` — exercises/*.json, atoms/*.json, shard_manifest.json |
| **Merged translations** | `{input_root}/{locale}/exercises/`, `{input_root}/{locale}/atoms/`, manifest.json at input root |

---

## Locale atom stubs & translation status

**Status:** Locale atom stub infrastructure 100% complete; translation execution pending API run.

Atoms for non-en-US locales (`atoms/zh-CN/`, `atoms/zh-TW/`, `atoms/zh-HK/`, `atoms/zh-SG/`, `atoms/yue/`, `atoms/ja-JP/`, `atoms/ko-KR/`) now exist with TRANSLATION PENDING stubs created by `scripts/scaffold_locale_atom_stubs.py`. Each locale directory mirrors the en-US atoms/ structure with stub ATOM_<locale>.yaml files.

### Coverage by locale

| Locale | Stub files created | Infrastructure status | Translation status |
|--------|-------------------|----------------------|-------------------|
| zh-CN | Multiple (>100) | ✓ Ready | Pending API execution |
| zh-TW | Multiple (>100) | ✓ Ready | Pending API execution |
| zh-HK | Multiple (>100) | ✓ Ready | Pending API execution |
| zh-SG | Multiple (>100) | ✓ Ready | Pending API execution |
| yue | Multiple (>100) | ✓ Ready | Pending API execution |
| ja-JP | Multiple (>100) | ✓ Ready | Pending API execution |
| ko-KR | Multiple (>100) | ✓ Ready | Pending API execution |

### Related scripts

- `scripts/scaffold_locale_atom_stubs.py` — Create stub ATOM_<locale>.yaml files for all atom types in a locale
- `scripts/translate_atoms_all_locales_cloud.py` — Fills stubs via parallel sharded OpenAI API calls
- `.github/workflows/translate-atoms-qwen-matrix.yml` — Orchestrates translation; runs weekly or on manual trigger
- `.github/workflows/locale-gate.yml` — Validates translations per locale and reports coverage

---

## Scripts — authoring, catalog & validation

All root-level `scripts/*.py` files confirmed present on disk.

| Script | Purpose |
|--------|---------|
| [scripts/run_pipeline.py](../scripts/run_pipeline.py) | Full 6-stage pipeline CLI — see Delivery pipeline section |
| [scripts/run_production_readiness_gates.py](../scripts/run_production_readiness_gates.py) | Production readiness gate runner |
| [scripts/render_plan_to_txt.py](../scripts/render_plan_to_txt.py) | Standalone render from saved plan JSON |
| [scripts/release/rollback_smoke.sh](../scripts/release/rollback_smoke.sh) | Post-restore verification (gates + pytest); DR drill evidence |
| [scripts/build_proof_chapter.py](../scripts/build_proof_chapter.py) | Build a single proof chapter from atoms + plan |
| [scripts/check_spec_version_bump.py](../scripts/check_spec_version_bump.py) | Verify spec version is bumped on breaking changes |
| [scripts/clean_atom_prose.py](../scripts/clean_atom_prose.py) | Batch clean atom prose files (strip metadata artifacts) |
| [scripts/compose_cohesive_chapter_from_plan.py](../scripts/compose_cohesive_chapter_from_plan.py) | Compose a cohesive chapter from a compiled plan JSON |
| [scripts/create_freebie_assets.py](../scripts/create_freebie_assets.py) | Generate freebie assets (PDFs, landing copy) from plan |
| [scripts/fill_non_story_coverage_gaps.py](../scripts/fill_non_story_coverage_gaps.py) | Fill missing HOOK/SCENE/REFLECTION/INTEGRATION/EXERCISE CANONICAL.txt files |
| [scripts/generate_arcs_from_backlog.py](../scripts/generate_arcs_from_backlog.py) | Batch-generate arc YAMLs from arc backlog config |
| [scripts/generate_author_cover_art_bases.py](../scripts/generate_author_cover_art_bases.py) | Author cover art base PNGs → assets/authors/cover_art/{author_id}_base.png (see Author cover art §) |
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
| [scripts/ci/check_author_cover_art.py](../scripts/ci/check_author_cover_art.py) | Author cover art: every launchable author has registry + PNG + style/palette (Gate 18) |
| [scripts/ci/check_book_output_no_placeholders.py](../scripts/ci/check_book_output_no_placeholders.py) | Hard-fail if any placeholder pattern survives rendered output |
| [scripts/ci/check_book_output_tier0_contract.py](../scripts/ci/check_book_output_tier0_contract.py) | Tier 0 book output contract (config-driven forbidden patterns) |
| [scripts/ci/run_simulation_10k.py](../scripts/ci/run_simulation_10k.py) | 10k sim for CI |
| [scripts/ci/analyze_pearl_prime_sim.py](../scripts/ci/analyze_pearl_prime_sim.py) | Pass rate by dimension; best/worst combos; threshold gate |
| [scripts/ci/run_rigorous_system_test.py](../scripts/ci/run_rigorous_system_test.py) | Systems test + variation + atoms coverage + optional sim |
| [scripts/ci/run_canary_100_books.py](../scripts/ci/run_canary_100_books.py) | Real pipeline canary on sampled arcs |
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
| [config/quality/tier0_book_output_contract.yaml](../config/quality/tier0_book_output_contract.yaml) | Tier 0 book output contract (forbidden patterns, min word count) |
| [config/observability_production_signals.yaml](../config/observability_production_signals.yaml) | Production signal registry for POLES collector |
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

### When to add

| Trigger | Action |
|---------|--------|
| New doc that declares authority or is referenced by specs | Add to the appropriate section and to the complete inventory below |
| New script/config that is part of a documented system | Add to that section's Document all table |
| New workflow, artifact, or config file | Add to the domain subsection (e.g. Rigorous system test, Pearl News, Teacher Mode) |
| File is planned but not yet created | Add with ⚠️ *file not present* in the inventory |

### How to add

1. **Place in the correct section** — Match the domain (e.g. Pearl News, Teacher Mode, Translation, Rigorous system test).
2. **Add a row to the domain's Document all table** — If the section has a table (Docs, Scripts, Config, Artifacts, CI), add the item there.
3. **Add to "Document all — complete inventory"** — Use ✓ if file exists, ⚠️ if referenced but missing.
4. **Authority docs** — If the doc declares authority, ensure it references the three canonical anchors: [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md), [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md), [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md).

### Domain-specific subsections (document all)

| Section | Anchor | Purpose |
|---------|--------|---------|
| [Rigorous system test & simulation](#rigorous-system-test--simulation-document-all) | § Rigorous system test | Simulation, 10k/100k, analyzer, variation report, config, artifacts, CI |
| [Pearl News](#pearl-news-document-all) | § Pearl News | Pipeline, docs, scripts, config, tests, artifacts, workflows |
| [Marketing & deep research](#marketing--deep-research-document-all) | § Marketing | Deep research prompts, invisible script, marketing brief |
| [Church & payout](#church--payout-distribution-only-brands) | § Church | Church docs, brand config, scripts, tests, CI |
| [Teacher Mode & production readiness](#teacher-mode--production-readiness-document-all) | § Teacher Mode | Teacher gates, doctrine, config, tests, artifacts, workflows |
| [Mechanism alias system](#mechanism-alias-system-document-all) | § Mechanism alias | Schema, alias files, renderer integration |
| [Delivery pipeline](#delivery-pipeline-document-all) | § Delivery pipeline | Renderer, CLI, delivery contract, word-count gate, artifacts |
| [Enlightened Intelligence V1 & V2](#enlightened-intelligence-ei--v1--v2-document-all) | § EI | V1 modules, V2 modules (6 AI techniques), parallel adapter, eval harness, config, tests, artifacts |
| [Phoenix Churches Payout System](#phoenix-churches-payout-system-document-all) | § Payout | Spec, config, package (most files ⚠️ missing) |

### Governance

- **Link integrity:** [scripts/ci/check_docs_governance.py](../scripts/ci/check_docs_governance.py) — Fails if any linked file is missing; warns on stale date.
- **North star for go/no-go:** [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md) §6 Hard NOs.

---

## Document all — complete inventory

Single list of every **doc**, **spec**, **config**, and **script** referenced in this index. ⚠️ = referenced but file not found on disk.

### Docs (docs/)

| Doc | Section | Status |
|-----|---------|--------|
| [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md) | Canonical authority | ✓ |
| [DOCS_INDEX.md](./DOCS_INDEX.md) | Canonical authority | ✓ |
| [RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) | Core system docs | ✓ |
| [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md) | Core system docs | ✓ |
| [BRANCH_PROTECTION_REQUIREMENTS.md](./BRANCH_PROTECTION_REQUIREMENTS.md) | Core system docs | ✓ |
| [DISASTER_RECOVERY_DRILL_CHECKLIST.md](./DISASTER_RECOVERY_DRILL_CHECKLIST.md) | Core system docs | ✓ |
| [MARKETING_DEEP_RESEARCH_PROMPTS.md](./MARKETING_DEEP_RESEARCH_PROMPTS.md) | Marketing & deep research | ✓ |
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
| [GITHUB_SUPPORT_SYSTEM_SPEC.md](./GITHUB_SUPPORT_SYSTEM_SPEC.md) | Governance | ✓ |
| [RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md) | Brand & release | ✓ |
| [PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md](./PLATFORM_HARDENING_PHASES_3-8_OUTLINE.md) | Brand & release | ✓ |
| [church_docs/README.md](./church_docs/README.md) | Church & payout | ✓ |
| `docs/norcal_dharma.yaml` | Church & payout | ⚠️ missing |
| [adr/ADR-002-distribution-only-church-brand.md](./adr/ADR-002-distribution-only-church-brand.md) | Church & payout, ADRs | ✓ |
| [BOOK_001_ASSEMBLY_CONTRACT.md](./BOOK_001_ASSEMBLY_CONTRACT.md) | Book & authoring | ✓ |
| [BOOK_001_FREEZE.md](./BOOK_001_FREEZE.md) | Book & authoring | ✓ |
| [BOOK_001_READINESS_CHECKLIST.md](./BOOK_001_READINESS_CHECKLIST.md) | Book & authoring | ✓ |
| [BOOK_001_POST_MORTEM.md](./BOOK_001_POST_MORTEM.md) | Book & authoring | ✓ |
| [authoring/AUTHOR_ASSET_WORKBOOK.md](./authoring/AUTHOR_ASSET_WORKBOOK.md) | Book & authoring | ✓ |
| [authoring/AUTHOR_COVER_ART_SYSTEM.md](./authoring/AUTHOR_COVER_ART_SYSTEM.md) | Book & authoring | ✓ |
| [WRITER_BRIEF_BOOK_001.md](./WRITER_BRIEF_BOOK_001.md) | Book & authoring | ✓ |
| [WRITER_COMMS_SYSTEMS_100.md](./WRITER_COMMS_SYSTEMS_100.md) | Book & authoring | ✓ |
| [WRITER_SPEC_MARKDOWN_AND_DOCX.md](./WRITER_SPEC_MARKDOWN_AND_DOCX.md) | Book & authoring | ✓ |
| [FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) | Book & authoring | ✓ |
| [ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md](./ENLIGHTENED_INTELLIGENCE_PROD_CHECKLIST.md) | Enlightened Intelligence (V1/V2) | ✓ |
| `EI_V2_ROLLOUT_PROOF_CHECKLIST.md` | Enlightened Intelligence (V2 release) | ✓ |
| `docs/ei_v2_branch_protection_evidence.png` | Enlightened Intelligence (V2 release) | ⚠️ missing — add screenshot after completing branch protection step |
| [MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md](./MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md) | Manuscript quality | ✓ |
| [PRODUCTION_READINESS_GO_NO_GO.md](./PRODUCTION_READINESS_GO_NO_GO.md) | Manuscript quality / release | ✓ |
| [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md) | Manuscript quality / release | ✓ |
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
| [LOCALE_PERSONAS.md](./LOCALE_PERSONAS.md) | Locale personas | ✓ — 40 persona definitions across all 11 non-en-US locales (zh-TW, zh-HK, zh-CN, zh-SG, ja-JP, ko-KR, es-US, es-ES, fr-FR, de-DE, hu-HU) |
| [LOCALE_CATALOG_MARKETING_PLAN.md](./LOCALE_CATALOG_MARKETING_PLAN.md) | All-locale marketing plan | ✓ — Per-locale positioning, go-live checklists, readiness tracker for all 12 locales |
| [NEW_LANGUAGE_LOCATION_ONBOARDING.md](./NEW_LANGUAGE_LOCATION_ONBOARDING.md) | Marketing & deep research / Locale onboarding | ✓ — Process and deep research prompts for new language/location/topic/persona; market-driven; personas, topics, authors, platforms, metadata, stories, writing spec, book titles |
| [ZH_CN_DISTRIBUTION_PLAN.md](./ZH_CN_DISTRIBUTION_PLAN.md) | zh-CN distribution | ✓ — Local platform pipeline (Ximalaya, NetEase, WeChat Read, Dedao); Phase 5 prerequisite checklist |
| `LOCALE_PROSE_AND_PROMPTING.md` | Translation | ⚠️ missing |
| `MULTILINGUAL_ARCHITECTURE.md` | Translation | ⚠️ missing |
| `KOREA_MARKET_AND_PROSE.md` | Translation | ⚠️ missing (covered in LOCALE_PERSONAS.md + locale_strategy.md) |
| `JAPANESE_MARKET_SELFHELP_GUIDE.md` | Translation | ⚠️ missing (covered in LOCALE_PERSONAS.md + locale_strategy.md) |

### Specs (specs/)

| Spec | Section | Status |
|------|---------|--------|
| [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) | Canonical authority | ✓ |
| [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) | Canonical authority | ✓ |
| [specs/README.md](../specs/README.md) | Core system docs | ✓ |
| `specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md` | Phoenix Churches Payout | ⚠️ missing |
| [specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md) | Simulation | ✓ |
| [specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) | Marketing & deep research | ✓ |

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
| [requirements-test.txt](../requirements-test.txt) | Test infrastructure | ✓ |
| [pytest.ini](../pytest.ini) | Test infrastructure | ✓ |
| [tests/conftest.py](../tests/conftest.py) | Test infrastructure | ✓ |
| [artifacts/reports/pearl_prime_sim_baseline.json](../artifacts/reports/pearl_prime_sim_baseline.json) | Simulation | ✓ |
| [artifacts/dr_drill/](../artifacts/dr_drill/) | DR | ✓ |
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
| `config/source_of_truth/enlightened_intelligence_registry.yaml` | Enlightened Intelligence (V1/V2) | ⚠️ missing |
| [config/quality/ei_v2_config.yaml](../config/quality/ei_v2_config.yaml) | Enlightened Intelligence V2 | ✓ — Enable/disable V2 modules, modes, thresholds, composite weights |
| [config/quality/ei_v2_promotion_criteria.yaml](../config/quality/ei_v2_promotion_criteria.yaml) | Enlightened Intelligence V2 promotion | ✓ — Five gates (quality, performance, safety, dimension gates, hybrid override), consecutive passes, auto_promote |
| [config/quality/tier0_book_output_contract.yaml](../config/quality/tier0_book_output_contract.yaml) | Manuscript quality | ✓ |
| [config/observability_production_signals.yaml](../config/observability_production_signals.yaml) | Observability | ✓ |
| `config/quality/canary_config.yaml` | Manuscript quality | ⚠️ missing |
| `config/payouts/churches.yaml` | Phoenix Churches Payout | ⚠️ missing |
| `config/payouts/payees.yaml` | Phoenix Churches Payout | ⚠️ missing |
| `config/payouts/credentials.yaml.example` | Phoenix Churches Payout | ⚠️ missing |
| `config/payouts/fill_template.csv` | Phoenix Churches Payout | ⚠️ missing |
| [config/teachers/teacher_registry.yaml](../config/teachers/teacher_registry.yaml) | Teacher Mode | ✓ |
| [config/authoring/author_cover_art_registry.yaml](../config/authoring/author_cover_art_registry.yaml) | Book & authoring (Author cover art) | ✓ |
| [config/marketing/consumer_language_by_topic.yaml](../config/marketing/consumer_language_by_topic.yaml) | Marketing & deep research | ✓ — 14 topics, consumer phrases, banned clinical terms, bridge language, search clusters, platform risk terms |
| [config/marketing/invisible_scripts_by_persona_topic.yaml](../config/marketing/invisible_scripts_by_persona_topic.yaml) | Marketing & deep research | ✓ — 140 entries (10 personas × 14 topics), 2 scripts each; loaded by title engine |
| [scripts/ci/check_marketing_config.py](../scripts/ci/check_marketing_config.py) | Marketing & deep research | ✓ — CI gate: referential integrity, required fields, brand×clinical cross-check, strict mode |
| [.github/workflows/marketing-config-gate.yml](../.github/workflows/marketing-config-gate.yml) | Marketing & deep research | ✓ — PR gate for config/marketing/** changes |
| [.github/workflows/teacher-gates.yml](../.github/workflows/teacher-gates.yml) | Teacher Mode | ✓ |
| [.github/workflows/brand-guards.yml](../.github/workflows/brand-guards.yml) | Church & payout (NorCal Dharma brand guards) | ✓ |
| `config/localization/quality_contracts/README.md` | Translation | ✓ — Quality contract definitions and thresholds |
| `quality_contracts/glossary.yaml` | Translation | ⚠️ missing |
| `quality_contracts/release_thresholds.yaml` | Translation | ⚠️ missing |
| `quality_contracts/golden_translation_regression.yaml` | Translation | ⚠️ missing |
| [config/localization/content_roots_by_locale.yaml](../config/localization/content_roots_by_locale.yaml) | Translation | ✓ — all 12 locales mapped with atoms_root, TTS constraints, rollout phase, distribution blockers |
| `.github/workflows/translate-atoms-qwen-matrix.yml` | Translation | ✓ — Parallel sharded translation workflow |
| `.github/workflows/locale-gate.yml` | Translation | ✓ — Locale validation gate: validate translations per locale, golden regression check, coverage report |
| [.github/workflows/core-tests.yml](../.github/workflows/core-tests.yml) | Core CI | ✓ |
| [.github/workflows/simulation-10k.yml](../.github/workflows/simulation-10k.yml) | Simulation CI | ✓ |
| [.github/workflows/release-gates.yml](../.github/workflows/release-gates.yml) | Release CI | ✓ |
| [.github/workflows/production-observability.yml](../.github/workflows/production-observability.yml) | Observability | ✓ |
| [.github/workflows/ei-v2-gates.yml](../.github/workflows/ei-v2-gates.yml) | Enlightened Intelligence V2 CI | ✓ — Unit tests → rigorous eval → promotion gate check; weekly + on EI code changes |
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
| [phoenix_v4/quality/ei_adapter.py](../phoenix_v4/quality/ei_adapter.py) | Enlightened Intelligence V1 | ✓ — `apply_ei_selection()`: heuristic scoring, embedding thesis alignment, selector, LLM tie-break |
| [phoenix_v4/quality/ei_embeddings.py](../phoenix_v4/quality/ei_embeddings.py) | Enlightened Intelligence V1 | ✓ — `thesis_similarity()`: cosine similarity, SQLite cache |
| [phoenix_v4/quality/ei_llm_judge.py](../phoenix_v4/quality/ei_llm_judge.py) | Enlightened Intelligence V1 | ✓ — `judge_tie_break()`: LLM-based candidate comparison, JSONL cache |
| [phoenix_v4/quality/teacher_integrity.py](../phoenix_v4/quality/teacher_integrity.py) | Enlightened Intelligence V1 | ✓ — `compute_teacher_integrity_penalty()`: phrase-matching safety |
| [phoenix_v4/quality/ei_v2/\_\_init\_\_.py](../phoenix_v4/quality/ei_v2/__init__.py) | Enlightened Intelligence V2 | ✓ — `run_ei_v2_analysis()`: orchestrates all V2 modules |
| [phoenix_v4/quality/ei_v2/config.py](../phoenix_v4/quality/ei_v2/config.py) | Enlightened Intelligence V2 | ✓ — `load_ei_v2_config()`: YAML + defaults merge |
| [phoenix_v4/quality/ei_v2/cross_encoder_reranker.py](../phoenix_v4/quality/ei_v2/cross_encoder_reranker.py) | Enlightened Intelligence V2 | ✓ — `rerank_candidates()`: semantic + token overlap reranking |
| [phoenix_v4/quality/ei_v2/safety_classifier.py](../phoenix_v4/quality/ei_v2/safety_classifier.py) | Enlightened Intelligence V2 | ✓ — `classify_safety()`: expanded pattern detection + negation |
| [phoenix_v4/quality/ei_v2/domain_embeddings.py](../phoenix_v4/quality/ei_v2/domain_embeddings.py) | Enlightened Intelligence V2 | ✓ — `domain_thesis_similarity()`: persona + topic weighted |
| [phoenix_v4/quality/ei_v2/semantic_dedup.py](../phoenix_v4/quality/ei_v2/semantic_dedup.py) | Enlightened Intelligence V2 | ✓ — `detect_semantic_duplicates()`: n-gram + beat fingerprint |
| [phoenix_v4/quality/ei_v2/emotion_arc_validator.py](../phoenix_v4/quality/ei_v2/emotion_arc_validator.py) | Enlightened Intelligence V2 | ✓ — `validate_emotion_arc()`: valence/arousal lexicon scoring |
| [phoenix_v4/quality/ei_v2/tts_readability.py](../phoenix_v4/quality/ei_v2/tts_readability.py) | Enlightened Intelligence V2 | ✓ — `score_tts_readability()`: rhythm, sentence length, TTS patterns |
| [phoenix_v4/quality/ei_parallel_adapter.py](../phoenix_v4/quality/ei_parallel_adapter.py) | Enlightened Intelligence (parallel) | ✓ — `compare_slot()`, `build_pipeline_comparison()`, `write_comparison_report()` |
| [scripts/ci/run_ei_v2_rigorous_eval.py](../scripts/ci/run_ei_v2_rigorous_eval.py) | Enlightened Intelligence (eval) | ✓ — 10-dimension quality eval + V1/V2 comparison + timing benchmarks |
| [scripts/ci/check_ei_v2_promotion_gate.py](../scripts/ci/check_ei_v2_promotion_gate.py) | Enlightened Intelligence (promotion) | ✓ — Checks eval report against promotion criteria; tracks consecutive passes |
| `phoenix_v4/quality/ei_v2/hybrid_selector.py` | Enlightened Intelligence V2 (hybrid) | ✓ — `hybrid_select()`: V1 picks → V2 scores → risk blocks → margin override → learner feedback |
| `phoenix_v4/quality/ei_v2/learner.py` | Enlightened Intelligence V2 (learner) | ✓ — `learn()`: EMA-based weight/threshold tuning; `log_feedback()`, `load_learned_params()` |
| `phoenix_v4/quality/ei_v2/dimension_gates.py` | Enlightened Intelligence V2 (gates) | ✓ — `enforce_chapter_gates()`: uniqueness, engagement, somatic, listen, cohesion |
| `scripts/ci/run_ei_v2_catalog_calibration.py` | Enlightened Intelligence (calibration) | ✓ — Whole-catalog dimension gate sweep; percentile threshold discovery; learner integration |
| `tests/test_ei_v2_hybrid.py` | Enlightened Intelligence V2 (tests) | ✓ — 25 tests: learner, dimension gates, hybrid selector, config, integration |
| [phoenix_title_engine.py](../phoenix_title_engine.py) | Marketing & deep research | ✓ |
| [phoenix_title_engine_v3.py](../phoenix_title_engine_v3.py) | Marketing & deep research | ✓ |
| [phoenix_title_engine_v4.py](../phoenix_title_engine_v4.py) | Marketing & deep research | ✓ |
| [scripts/ci/run_teacher_production_gates.py](../scripts/ci/run_teacher_production_gates.py) | Teacher Mode | ✓ |
| [scripts/ci/check_doctrine_schema.py](../scripts/ci/check_doctrine_schema.py) | Teacher Mode | ✓ |
| [scripts/ci/check_teacher_readiness.py](../scripts/ci/check_teacher_readiness.py) | Teacher Mode | ✓ |
| [scripts/ci/check_teacher_synthetic_governance.py](../scripts/ci/check_teacher_synthetic_governance.py) | Teacher Mode | ✓ |
| [scripts/ci/check_author_cover_art.py](../scripts/ci/check_author_cover_art.py) | Book & authoring (Author cover art Gate 18) | ✓ |
| [scripts/teacher_stub_f006_slots.py](../scripts/teacher_stub_f006_slots.py) | Teacher Mode | ✓ |
| [scripts/generate_author_cover_art_bases.py](../scripts/generate_author_cover_art_bases.py) | Book & authoring (Author cover art) | ✓ |
| [phoenix_v4/planning/author_cover_art_resolver.py](../phoenix_v4/planning/author_cover_art_resolver.py) | Book & authoring (Author cover art; pipeline output) | ✓ |
| [scripts/ci/report_variation_knobs.py](../scripts/ci/report_variation_knobs.py) | Simulation | ✓ |
| [scripts/ci/run_simulation_10k.py](../scripts/ci/run_simulation_10k.py) | Simulation | ✓ |
| `scripts/ci/run_simulation_100k.py` | Simulation | ⚠️ missing |
| [scripts/ci/analyze_pearl_prime_sim.py](../scripts/ci/analyze_pearl_prime_sim.py) | Simulation | ✓ |
| [scripts/ci/run_rigorous_system_test.py](../scripts/ci/run_rigorous_system_test.py) | Simulation | ✓ |
| [scripts/ci/check_book_output_tier0_contract.py](../scripts/ci/check_book_output_tier0_contract.py) | Manuscript quality | ✓ |
| `scripts/ci/tier0_trend.py` | Manuscript quality | ⚠️ missing |
| [scripts/ci/run_canary_100_books.py](../scripts/ci/run_canary_100_books.py) | Simulation / Release | ✓ |
| [scripts/release/rollback_smoke.sh](../scripts/release/rollback_smoke.sh) | Release / DR | ✓ |
| [scripts/ci/check_norcal_dharma_brand_guards.py](../scripts/ci/check_norcal_dharma_brand_guards.py) | Church & payout | ✓ |
| [scripts/ci/check_church_yaml_no_sensitive_tokens.py](../scripts/ci/check_church_yaml_no_sensitive_tokens.py) | Church & payout | ✓ |
| [scripts/ops/smoke_church_brand_resolution.py](../scripts/ops/smoke_church_brand_resolution.py) | Church & payout | ✓ |
| [phoenix_v4/ops/church_loader.py](../phoenix_v4/ops/church_loader.py) | Church & payout | ✓ |
| `scripts/translate_atoms_all_locales_cloud.py` | Translation | ✓ — Parallel sharded translation to all locales |
| `scripts/validate_translations.py` | Translation | ✓ — Structure, encoding, glossary, golden regression |
| `scripts/merge_translation_shards.py` | Translation | ✓ — Merges parallel shard outputs; conflict detection |
| `scripts/check_golden_translation.py` | Translation | ✓ — Regression against golden samples |
| `scripts/native_prompts_eval_learn.py` | Translation | ✓ — Native-speaker eval prompts; 4 evaluation dimensions |
