# Full Repo Test Suite Plan

**Purpose:** Analysis of all testing systems, gap identification, and a comprehensive plan for a full-repo test suite with all pipelines.  
**Authority:** Extends [DOCS_INDEX.md](./DOCS_INDEX.md), [RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md), [SYSTEMS_V4.md](./SYSTEMS_V4.md).  
**Last updated:** 2026-03-03

---

## 1. Current Testing Systems — Inventory

### 1.1 Pytest tests (34 files under `tests/`)

| Test file | Domain | CI coverage |
|-----------|--------|--------------|
| `teacher_arc_test.py` | Teacher Mode | teacher-gates.yml |
| `test_teacher_mode_e2e_smoke.py` | Teacher Mode | teacher-gates.yml |
| `test_pearl_news_quality_gates_minimal.py` | Pearl News | pearl_news_gates.yml |
| `test_pearl_news_pipeline_e2e.py` | Pearl News | pearl_news_gates.yml |
| `test_norcal_dharma_brand_smoke.py` | Church/brand | brand-guards.yml |
| `test_atoms_coverage_100_percent.py` | Atoms | **None** |
| `test_arc_loader.py` | Arc | **None** |
| `test_assembly_compiler.py` | Assembly | **None** |
| `test_atoms_model.py` | Atoms | **None** |
| `test_book_pass_gate.py` | Manuscript quality | **None** |
| `test_book_renderer.py` | Rendering | **None** |
| `test_brand_identity_stability.py` | Brand | **None** |
| `test_catalog_emotional_distribution.py` | Catalog | **None** |
| `test_chapter_flow_gate.py` | Chapter | **None** |
| `test_creative_quality_v1.py` | Quality | **None** |
| `test_cross_brand_divergence.py` | Brand | **None** |
| `test_emotional_curve_golden.py` | Arc/emotional | **None** |
| `test_format_selector.py` | Format | **None** |
| `test_intro_ending_variation.py` | Intro/ending | **None** |
| `test_narrative_gates.py` | Narrative | **None** |
| `test_platform_health_scorecard.py` | Platform | **None** |
| `test_prepublish_gates.py` | Pre-publish | **None** |
| `test_prepublish_series_wiring.py` | Series | **None** |
| `test_quality_regression.py` | Quality | **None** |
| `test_release_wave_controls.py` | Release | **None** |
| `test_series_mode_planner.py` | Series | **None** |
| `test_series_quality_gates.py` | Series | **None** |
| `test_slot_resolver.py` | Assembly | **None** |
| `test_template_selector.py` | Pearl News | **None** |
| `test_topic_sdg_classifier.py` | Pearl News | **None** |
| `test_validate_series_diversity.py` | Series | **None** |
| `test_validators.py` | Validators | **None** |
| `test_variation.py` | Variation | **None** |
| `test_wave_optimizer_constraint_solver.py` | Wave | **None** |

**Summary:** Only **5 test files** are run in CI (path-triggered). **29 tests** are never run automatically.

### 1.2 CI workflows (6 total)

| Workflow | Triggers | What runs |
|----------|----------|-----------|
| `teacher-gates.yml` | Paths: teacher config, banks, teacher scripts, teacher tests | run_teacher_production_gates.py, teacher_arc_test, test_teacher_mode_e2e_smoke |
| `pearl_news_gates.yml` | Paths: pearl_news/**, pearl_news tests | test_pearl_news_quality_gates_minimal, test_pearl_news_pipeline_e2e |
| `brand-guards.yml` | Paths: brand_registry, locale, brand_teacher_*, guard scripts | check_norcal_dharma_brand_guards, check_church_yaml_no_sensitive_tokens, test_norcal_dharma_brand_smoke |
| `docs-ci.yml` | Paths: docs/**, specs/**, ONBOARDING | check_docs_governance, check_church_yaml_no_sensitive_tokens |
| `pearl_news_scheduled.yml` | Scheduled + manual | Pipeline run → drafts → optional WordPress dry-run |
| `pages.yml` | Pages build | Not a test workflow |

**Critical gap:** No workflow runs on **core pipeline changes** (run_pipeline.py, phoenix_v4/planning/, phoenix_v4/rendering/, atoms/, simulation/). Changes to these can merge with **zero CI**.

### 1.3 Script-based systems

| System | Entry point | CI? |
|--------|-------------|-----|
| **Systems test** | `scripts/systems_test/run_systems_test.py --all` | **None** |
| **Production readiness gates** | `scripts/run_production_readiness_gates.py` | **None** (only invoked inside systems test Phase 6) |
| **Simulation** | `simulation/run_simulation.py --n N` | **None** |
| **Pre-publish gates** | `scripts/ci/run_prepublish_gates.py` | **None** (release-time only) |
| **Variation report** | `scripts/ci/report_variation_knobs.py` | **None** |

### 1.4 Missing scripts (from DOCS_INDEX)

| Script | Purpose |
|--------|---------|
| `scripts/ci/run_simulation_10k.py` | 10k sim for CI |
| `scripts/ci/run_simulation_100k.py` | 100k full-knobs sim |
| `scripts/ci/analyze_pearl_prime_sim.py` | Pass rate by dimension, best/worst combos |
| `scripts/ci/run_rigorous_system_test.py` | 10k + variation + E2E smoke + atoms coverage |
| `scripts/ci/check_book_output_tier0_contract.py` | Manuscript Tier 0 contract |
| `scripts/ci/tier0_trend.py` | Violations over time (observability) |
| `scripts/ci/run_canary_100_books.py` | Real pipeline canary on 100 books |

### 1.5 Missing workflows

| Workflow | Purpose |
|----------|---------|
| `.github/workflows/simulation-10k.yml` | Simulation at scale in CI |
| `.github/workflows/release-gates.yml` | Release-path gates on main |

---

## 2. Gap Analysis

### 2.1 CI coverage gaps

1. **No full-pytest workflow** — 29/34 tests never run in CI.
2. **Path-only triggers** — Core pipeline changes (run_pipeline, assembly_compiler, book_renderer, atoms, simulation) do not trigger any workflow.
3. **No simulation in CI** — Simulation is readiness tooling but never runs automatically.
4. **No systems test in CI** — `run_systems_test.py --all` is manual only.
5. **No production readiness gates in CI** — 17 gates run only when systems test Phase 6 runs.
6. **No atoms coverage gate in CI** — `test_atoms_coverage_100_percent.py` is a blocker test but not wired to CI.

### 2.2 Production 100% gaps (per RIGOROUS_SYSTEM_TEST.md)

| Requirement | Status |
|-------------|--------|
| 1. Real pipeline canary runs on worst/best combos | **Missing** — no `run_canary_100_books.py` or equivalent |
| 2. CI gate on analyzer regression thresholds | **Missing** — no analyzer, no CI gate |
| 3. Evidence on main (green workflows + artifact links) | **Partial** — workflows exist but no simulation/release evidence |
| 4. Release-path smoke + rollback proof | **Missing** — no release-gates workflow, no rollback proof |

### 2.3 Domain coverage gaps

| Domain | Tests | CI | Gap |
|--------|-------|-----|-----|
| Arc-First pipeline (Stage 1–3) | test_assembly_compiler, test_slot_resolver, test_arc_loader | None | Core pipeline untested in CI |
| Rendering (Stage 6) | test_book_renderer | None | Delivery contract, word count gate not in CI |
| Format selection | test_format_selector | None | Stage 2 logic untested in CI |
| Atoms coverage | test_atoms_coverage_100_percent, test_atoms_model | None | 450/450 gate not in CI |
| Manuscript quality | test_book_pass_gate | None | Tier 0 contract scripts missing |
| Teacher Mode | teacher_arc_test, test_teacher_mode_e2e_smoke | teacher-gates | **Covered** |
| Pearl News | test_pearl_news_*, test_topic_sdg_classifier, test_template_selector | pearl_news_gates | **Covered** |
| Church/brand | test_norcal_dharma_brand_smoke | brand-guards | **Covered** |
| Series, wave, release | test_series_*, test_release_wave_controls, test_wave_optimizer | None | Release path untested |
| Quality gates | test_creative_quality_v1, test_quality_regression, test_prepublish_gates | None | Quality gates not in CI |
| Variation | test_variation | None | Knob distribution untested |

### 2.4 Best-practice gaps

1. **No conftest.py** — No shared fixtures, markers, or pytest config.
2. **No pyproject.toml pytest section** — No test discovery config, timeout, or markers.
3. **No test tiers** — No fast/slow split; all tests treated equally.
4. **No coverage reporting** — No pytest-cov or coverage gate.
5. **Dependency fragmentation** — teacher-gates: pyyaml, pytest; pearl_news: feedparser, pyyaml, pytest; brand-guards: pyyaml, pytest. No unified requirements-test.txt.

---

## 3. Full Repo Test Suite Plan

### 3.1 Phase 1 — Core CI (immediate)

**Goal:** Every push/PR to main runs a minimal fast suite so core regressions are caught.

| Item | Action |
|------|--------|
| **1.1** | Add `.github/workflows/core-tests.yml` — triggers on push/PR to main; paths: `phoenix_v4/**`, `scripts/run_pipeline.py`, `scripts/run_production_readiness_gates.py`, `atoms/**`, `config/**`, `simulation/**`, `tests/**` (exclude pearl_news, teacher, brand paths that have their own workflows). |
| **1.2** | Core workflow runs: `pytest tests/ -v --ignore=tests/test_pearl_news_*.py --ignore=tests/test_norcal_dharma_*.py -x` (or use markers to exclude). Actually: run a **fast subset** first: `test_arc_loader`, `test_assembly_compiler`, `test_atoms_model`, `test_format_selector`, `test_slot_resolver`, `test_validators`, `test_book_renderer`, `test_atoms_coverage_100_percent`. |
| **1.3** | Add `scripts/ci/run_fast_tests.sh` — runs ~10 fastest tests; target &lt;2 min. |
| **1.4** | Add `requirements-test.txt` — pytest, pyyaml, feedparser (for pearl_news), jsonschema. All workflows use this. |
| **1.5** | Wire `run_production_readiness_gates.py` into core workflow — run after pytest, fail PR if gates fail. |

**Deliverables:** One new workflow; core pipeline changes trigger CI; 17 production gates run on every relevant PR.

### 3.2 Phase 2 — Simulation pipeline

**Goal:** Simulation runs in CI; analyzer and evidence exist.

| Item | Action |
|------|--------|
| **2.1** | Create `scripts/ci/run_simulation_10k.py` — wrapper: `python simulation/run_simulation.py --n 10000 --use-format-selector --phase2 --phase3 --out artifacts/simulation_10k.json`. |
| **2.2** | Create `scripts/ci/analyze_pearl_prime_sim.py` — reads simulation output; computes pass rate by dimension; outputs `artifacts/reports/pearl_prime_sim_analysis.json` and `_SUMMARY.txt`. |
| **2.3** | Add `.github/workflows/simulation-10k.yml` — on push to main (or scheduled weekly); runs 10k sim; runs analyzer; uploads artifacts; fails if pass rate &lt; baseline (configurable). |
| **2.4** | Add baseline file `artifacts/reports/pearl_prime_sim_baseline.json` — commit when acceptable; CI compares against it. |

**Deliverables:** Simulation in CI; analyzer; regression gate.

### 3.3 Phase 3 — Rigorous system test + release gates

**Goal:** Systems test and release-path gates run in CI; production 100% requirements 1–4 move toward completion.

| Item | Action |
|------|--------|
| **3.1** | Create `scripts/ci/run_rigorous_system_test.py` — runs: (1) 10k sim (or skip if long), (2) `report_variation_knobs.py`, (3) systems test `--all`, (4) `test_atoms_coverage_100_percent`. Single entrypoint for "full rigorous" run. |
| **3.2** | Add `.github/workflows/release-gates.yml` — on push to main; runs: production readiness gates, systems test (phases 1–5 + 7; phase 6 includes prod gates), prepublish gates (if plans exist). |
| **3.3** | Create `scripts/ci/run_canary_100_books.py` — samples worst/best combos from analyzer (or fixed set); runs `run_pipeline.py` for each; fails if any compile/render fails. Fulfills RIGOROUS_SYSTEM_TEST requirement 1. |
| **3.4** | Document rollback procedure and add `scripts/release/rollback_smoke.sh` — placeholder that runs smoke and records evidence. |

**Deliverables:** Rigorous suite runner; release-gates workflow; canary script; rollback proof path.

### 3.4 Phase 4 — Manuscript quality (Tier 0)

**Goal:** Tier 0 contract and canary exist; manuscript quality is gateable.

| Item | Action |
|------|--------|
| **4.1** | Create `config/quality/tier0_book_output_contract.yaml` — forbidden patterns, min word count, etc. |
| **4.2** | Create `scripts/ci/check_book_output_tier0_contract.py` — validates rendered output against contract. |
| **4.3** | Wire into `run_prepublish_gates.py` (step 4a already has delivery gate; extend or add step 4b). |
| **4.4** | Optional: `scripts/ci/run_canary_100_books.py` can call Tier 0 checker on rendered output. |

**Deliverables:** Tier 0 config; checker script; integration with prepublish.

### 3.5 Phase 5 — Test infrastructure

**Goal:** Consistent pytest config, markers, fixtures; faster feedback.

| Item | Action |
|------|--------|
| **5.1** | Add `pyproject.toml` (or `pytest.ini`) — `[tool.pytest.ini_options]` with `testpaths = ["tests"]`, `markers = ["slow", "integration", "e2e"]`. |
| **5.2** | Add `tests/conftest.py` — shared fixtures (e.g. repo_root, sample_plan_path, sample_arc_path). |
| **5.3** | Mark slow tests: `@pytest.mark.slow` for test_atoms_coverage_100_percent, test_teacher_mode_e2e_smoke, etc. |
| **5.4** | Core workflow runs `pytest -m "not slow"`; full workflow runs `pytest` (all). |
| **5.5** | Add `scripts/ci/run_full_test_suite.sh` — `pytest tests/ -v`; used by release-gates. |

**Deliverables:** pytest config; conftest; markers; full-suite script.

### 3.6 Phase 6 — Observability (POLES alignment)

**Goal:** All production signals observable; evidence captured.

| Item | Action |
|------|--------|
| **6.1** | Create `config/observability_production_signals.yaml` — registry of all signals (per PRODUCTION_OBSERVABILITY_LEARNING_SPEC). |
| **6.2** | Extend `scripts/observability/collect_signals.py` — collect from workflows, gates, systems test, simulation. |
| **6.3** | Add scheduled workflow that runs collector and writes `artifacts/observability/signal_snapshot_<timestamp>.json`. |
| **6.4** | Document evidence links in README or docs — where to find green runs, artifacts. |

**Deliverables:** Signal registry; collector; scheduled snapshot.

---

## 4. Pipeline Test Matrix

| Pipeline | Unit tests | Integration | E2E | CI |
|----------|------------|-------------|-----|-----|
| **Arc-First (Stage 1–3)** | test_assembly_compiler, test_slot_resolver, test_arc_loader | systems test Phase 3 | run_pipeline golden | core-tests, release-gates |
| **Format selection (Stage 2)** | test_format_selector | — | — | core-tests |
| **Rendering (Stage 6)** | test_book_renderer | — | render_plan_to_txt | core-tests |
| **Atoms** | test_atoms_model | test_atoms_coverage_100_percent | — | core-tests |
| **Simulation** | — | run_simulation n=10 | run_simulation n=10k | simulation-10k |
| **Teacher Mode** | teacher_arc_test | run_teacher_production_gates | test_teacher_mode_e2e_smoke | teacher-gates |
| **Pearl News** | test_pearl_news_quality_gates_minimal, test_topic_sdg_classifier, test_template_selector | — | test_pearl_news_pipeline_e2e | pearl_news_gates |
| **Church/brand** | — | check_norcal_dharma_brand_guards | test_norcal_dharma_brand_smoke | brand-guards |
| **Pre-publish** | test_prepublish_gates | run_prepublish_gates | — | release-gates (when plans) |
| **Release** | test_release_wave_controls, test_wave_optimizer | — | — | release-gates |

---

## 5. Recommended Execution Order

1. **Phase 1** — Core CI (highest impact; unblocks everything).
2. **Phase 5** — Test infrastructure (enables Phase 1 to scale).
3. **Phase 2** — Simulation pipeline (readiness tooling in CI).
4. **Phase 3** — Rigorous + release gates (production 100% path).
5. **Phase 4** — Manuscript quality (when Tier 0 contract is defined).
6. **Phase 6** — Observability (continuous improvement).

---

## 6. Summary

| Metric | Current | After Phase 1 | After Phase 3 | **Implemented** |
|--------|---------|---------------|---------------|-----------------|
| Tests in CI | 5 | ~15 | 34 | core-tests runs fast set |
| Workflows | 5 (path-triggered) | 6 (+ core-tests) | 8 (+ simulation-10k, release-gates) | **9** (core-tests, simulation-10k, release-gates, production-observability) |
| Core pipeline changes trigger CI | No | Yes | Yes | **Yes** |
| Production gates in CI | No | Yes | Yes | **Yes** |
| Simulation in CI | No | No | Yes | **Yes** (simulation-10k.yml) |
| Release-path smoke | No | No | Yes | **Yes** (release-gates + rollback_smoke) |
| DR drill evidence | No | No | No | **Checklist + template** (docs/DISASTER_RECOVERY_DRILL_CHECKLIST.md) |

---

## 7. References

- [DOCS_INDEX.md](./DOCS_INDEX.md) — Full inventory
- [RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) — Production 100% requirements
- [SYSTEMS_V4.md](./SYSTEMS_V4.md) — §8 systems test
- [PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md](./PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md) — POLES
- [V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md) — 17 gates
