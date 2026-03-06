# CI/CD and shipping readiness exploration
_Exported on 3/3/2026 at 18:55:39 GMT+8 from Cursor (2.5.25)_

---

**User**

Explore the CI/CD and shipping readiness of this repo. I need:

1. List all GitHub Actions workflows in .github/workflows/ — for each, note name, triggers, and whether it's required on main.
2. Check if there's any branch protection config or docs about it (search for "branch protection" in docs/).
3. Check if there's a CHANGELOG.md or release process docs.
4. Check git status — what files are currently modified/untracked that would need to be committed.
5. Look at docs/DOCS_INDEX.md around lines 488-560 to see the current V2 promotion gates and hybrid selector documentation sections.
6. Check if there's a pytest.ini or setup.cfg for test configuration.
7. Check if requirements-test.txt exists and what's in it.

Report everything you find.

---

**Cursor**


Exploring CI/CD and shipping readiness. Gathering the requested information.



Reading workflow files for triggers and required-status checks, and fetching branch-protection and test-config details.



Here’s the CI/CD and shipping readiness report:

---

## 1. GitHub Actions workflows

| Workflow | Triggers | Required on main? |
|----------|----------|-------------------|
| **Core tests** | `push` + `pull_request` on `main`/`master` (no path filter) | **Yes** — required in branch protection |
| **Release gates** | `push` to main (paths: phoenix_v4, scripts, config, atoms, workflow); `schedule` Sun 6am UTC; `workflow_dispatch` | **No** — not in branch protection |
| **Teacher gates** | `push` + `pull_request` on main (paths: teacher config, banks, teacher code, tests) | **Yes** — required when teacher paths change |
| **Brand guards** | `push` + `pull_request` on main (paths: brand registry, locale extension, catalog planning) | **Yes** — required when brand paths change |
| **Pearl News gates** | `push` + `pull_request` on main (paths: pearl_news, tests); `workflow_dispatch` | **Yes** — required when pearl_news paths change |
| **EI V2 gates** | `push` + `pull_request` on main (paths: quality, ei_v2 config/tests); `schedule` Mon 4am UTC; `workflow_dispatch` | **No** — not in branch protection |
| **Docs CI** | `push` + `pull_request` on main (paths: docs, specs, ONBOARDING, governance scripts) | **Optional** — mentioned in PEARL_NEWS_GO_NO_GO |
| **Simulation 10k** | `push` to main (paths: simulation, format_selector, run script); `schedule` Mon 6am UTC; `workflow_dispatch` | **No** |
| **Locale gate** | `push` + `pull_request` on main (paths: atoms locales, validate_translations, check_golden_translation) | **No** — new, untracked |
| **Translate Atoms (Qwen Matrix)** | `workflow_dispatch` (inputs: locale, shard_count, dry_run); `schedule` Sun 2am UTC | **No** — manual/scheduled only |
| **Production alerts** | `workflow_run` (completed) for Core tests, Release gates, Pearl News, Teacher, Brand, Docs CI, Simulation 10k, Production observability | **No** — downstream alerting |
| **Production observability** | `schedule` daily 7am UTC; `workflow_dispatch` | **No** — monitoring only |
| **Pages** | `push` to main; `workflow_dispatch` | **No** — deployment |
| **Pearl News scheduled** | `schedule` 6am + 6pm UTC daily; `workflow_dispatch` | **No** — feed ingest |

---

## 2. Branch protection config

**`docs/BRANCH_PROTECTION_REQUIREMENTS.md`** defines required status checks:

- **Core tests** — required (minimum)
- **Teacher gates** — required when teacher paths change
- **Brand guards** — required when brand paths change
- **Pearl News gates** — required when pearl_news paths change

Notes:

- Path-triggered workflows (Teacher, Brand, Pearl News) only run when their paths change; for core-only PRs, only Core tests runs.
- Docs mention `docs-ci` as optional for Pearl News.
- `locale-gate.yml` is untracked and not in branch protection.

---

## 3. CHANGELOG and release process

- **CHANGELOG.md** — not present at repo root.
- **`docs/SCHEMA_CHANGELOG.md`** — exists for schema version history.
- **Release process docs** — referenced but missing:
  - `docs/PRODUCTION_READINESS_GO_NO_GO.md` — not present
  - `docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md` — not present
- **Existing release-related docs:**
  - `docs/RELEASE_VELOCITY_AND_SCHEDULE.md` — brand & release schedule
  - `docs/DISASTER_RECOVERY_DRILL_CHECKLIST.md` — DR drill and rollback
  - `docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md` — Pearl News go/no-go
  - `docs/CONTROL_PLANE_GO_NO_GO.md` — control plane release checklist (mentions versioned release notes / CHANGELOG)

---

## 4. Git status — modified and untracked

**Modified (8 files):**

- `.github/workflows/ei-v2-gates.yml`
- `PhoenixControl/Services/ScriptRunner.swift`
- `PhoenixControl/Views/ContentView.swift`
- `PhoenixControl/Views/ObservabilityView.swift`
- `config/quality/ei_v2_config.yaml`
- `config/quality/ei_v2_promotion_criteria.yaml`
- `docs/DOCS_INDEX.md`
- `scripts/run_pipeline.py`

**Untracked (many files):**

- `.github/workflows/locale-gate.yml`
- `.github/workflows/translate-atoms-qwen-matrix.yml`
- `PhoenixControl.xcodeproj/`, `PhoenixControl/README.md`, `PhoenixControl/Services/KeychainService.swift`, `PhoenixControl/project.yml`, `PhoenixControlTests/`
- `QUALITY_CONTRACTS_INDEX.md`
- `atoms/de-DE/`, `atoms/es-ES/`, `atoms/es-US/`, `atoms/fr-FR/`, `atoms/hu-HU/`, `atoms/ja-JP/`, `atoms/ko-KR/`, `atoms/zh-CN/`, `atoms/zh-HK/`, `atoms/zh-SG/`, `atoms/zh-TW/`
- `config/localization/quality_contracts/`
- `docs/CONTROL_PLANE_GO_NO_GO.md`, `docs/CONTROL_PLANE_RUNBOOK.md`
- `phoenix_v4/quality/ei_v2/dimension_gates.py`, `hybrid_selector.py`, `learner.py`
- `scripts/TRANSLATE_ATOMS_README.md`, `check_golden_translation.py`, `merge_translation_shards.py`, `native_prompts_eval_learn.py`, `scaffold_locale_atom_stubs.py`, `translate_atoms_all_locales_cloud.py`, `validate_translations.py`
- `scripts/ci/run_ei_v2_catalog_calibration.py`
- `tests/test_ei_v2_hybrid.py`

---

## 5. DOCS_INDEX.md lines 488–560 — V2 promotion gates and hybrid selector

**V2 promotion gates (lines 493–513):**

- V2 cannot replace V1 until all five gates pass for 5 consecutive CI runs.
- `auto_promote` is OFF; manual approval required.
- Gates:
  1. **Quality** — composite ≥ 0.55, per-dimension floors, agreement rate ≥ 10% — PASS
  2. **Performance** — V2 per-slot ≤ 50ms, V2/V1 ratio ≤ 100x, per-book overhead ≤ 5000ms — PASS
  3. **Safety** — zero regressions, compliance ≥ 0.95 — FAIL (2 chapter-level regressions)
  4. **Dimension gates** — max 20% chapter fail rate, per-dimension pass rates — NEW
  5. **Hybrid override** — override success ≥ 60%, override rate ≤ 40%, block rate ≤ 20% — NEW
- Status: **BLOCKED** — 0/5 consecutive passes; V1 is authoritative.

**Hybrid V1+V2 selector (lines 515–552):**

- V1 picks winner; V2 scores and can override or block.
- Override rule: `v2_best - v2_v1_winner >= margin` (default 0.12), no safety violation, dedup risk &lt; 0.6, arc deviation &lt; 0.5.
- Dimension gates: uniqueness, engagement, somatic precision, listen experience, cohesion.
- Promotion plan: catalog calibration → per-book hybrid → scope expansion.
- Pipeline flag: `--ei-hybrid` on `run_pipeline.py`.

---

## 6. pytest.ini

**`pytest.ini`** exists:

```1:14:pytest.ini
[pytest]
# Phoenix test configuration — see docs/FULL_REPO_TEST_SUITE_PLAN.md
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
    ignore::UserWarning
markers =
    slow: marks tests as slow (excluded from fast CI run)
    integration: marks tests that need external resources or full pipeline
    e2e: end-to-end tests (compile, render, etc.)
```

---

## 7. requirements-test.txt

**`requirements-test.txt`** exists:

```1:6:requirements-test.txt
# Test dependencies — used by core-tests, teacher-gates, pearl_news_gates, brand-guards.
# Install: pip install -r requirements-test.txt
pyyaml>=5.0
pytest>=7.0
jsonschema>=4.0
feedparser>=6.0
```

---

## Summary

- **CI:** 14 workflows; Core tests, Teacher gates, Brand guards, Pearl News gates are required on main (path-dependent for the last three).
- **Branch protection:** Documented in `docs/BRANCH_PROTECTION_REQUIREMENTS.md`; actual GitHub settings are not in the repo.
- **Release:** No root `CHANGELOG.md`; `PRODUCTION_READINESS_GO_NO_GO.md` and `RELEASE_PRODUCTION_READINESS_CHECKLIST.md` are referenced but missing.
- **Tests:** `pytest.ini` and `requirements-test.txt` are present and used by core workflows.
- **Uncommitted work:** EI V2 changes, PhoenixControl updates, locale/translation workflows and atoms, and hybrid selector code are modified or untracked.

