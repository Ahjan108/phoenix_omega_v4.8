# Robust, intelligent testing

**Purpose:** Strategy and inventory for robust, intelligent testing — fast sanity checks, data-driven parametrized tests over configs and locales, timeouts to avoid hung CI, and consistent fixtures. Catches regressions early without slowing the fast CI run.

**Authority:** Complements [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md). Core CI runs `pytest -m "not slow"` (includes sanity and intelligent tests).

**Last updated:** 2026-03-04

---

## 1. Goals

- **Robust:** Config and registry consistency validated on every run; no silent breakage from YAML or schema drift.
- **Intelligent:** Data-driven tests parametrized over all locales and critical configs; one test definition, many assertions.
- **Fast:** Sanity and intelligent tests are not marked `slow`; they run in core-tests and complete in seconds.
- **Bounded:** Default per-test timeout (e.g. 120s) so a hung test does not block CI.

---

## 2. Markers

| Marker         | Use | CI (core-tests) |
|----------------|-----|------------------|
| `slow`         | Long-running (atoms coverage, E2E smoke) | Excluded (`-m "not slow"`) |
| `integration`  | Needs external resources or full pipeline | Excluded if not run | 
| `e2e`          | End-to-end (compile, render) | Excluded if not run |
| `sanity`       | Fast sanity (config load, registry consistency) | **Included** |
| `intelligent`  | Data-driven / parametrized over configs and locales | **Included** |

Run only sanity tests for quick feedback:  
`pytest -m sanity -v`

Run sanity + intelligent (no slow):  
`pytest -m "sanity or intelligent" -v`

---

## 3. Test inventory (robust / intelligent)

| Test file | What it does |
|-----------|---------------|
| **tests/test_robust_intelligent.py** | Locale-registry ↔ content_roots consistency; required fields per locale; EU catalogue presence; no duplicate IDs; locale_groups subset; critical YAML load; marketing config structure; tts_locale_code vs locale ID. |

All tests in this file are fast and run in core-tests.

---

## 4. Fixtures (conftest.py)

| Fixture | Scope | Purpose |
|---------|--------|---------|
| `repo_root` | function | Repo root path |
| `fixtures_dir` | function | tests/fixtures |
| `config_root` | function | config/ |
| `atoms_root` | function | atoms/ (or ATOMS_ROOT env) |
| `locale_registry_path` | session | Path to locale_registry.yaml |
| `locale_registry` | session | Loaded locale_registry.yaml |
| `content_roots_path` | session | Path to content_roots_by_locale.yaml |
| `content_roots` | session | Loaded content_roots_by_locale.yaml |
| `all_locale_ids` | session | List of all locale IDs (for parametrization) |

Session-scoped config fixtures avoid reloading the same YAML for every test.

---

## 5. Timeout

- **pytest-timeout** is in `requirements-test.txt`.
- **pytest.ini** sets `timeout = 120` (seconds per test) by default.
- Override per test: `@pytest.mark.timeout(30)`.
- Prevents a single hung test from blocking CI; on timeout pytest reports the test and continues (or fails the run, depending on config).

---

## 6. Adding more robust / intelligent tests

1. **New sanity check:** Validate a critical config or contract; use `@pytest.mark.sanity`; keep it fast (no I/O beyond config load).
2. **New data-driven check:** Parametrize over `all_locale_ids` or over a list of config paths; use `locale_registry` / `content_roots` fixtures; use `@pytest.mark.intelligent`.
3. **Required keys:** If the schema gains new required keys, update `LOCALE_REGISTRY_REQUIRED_KEYS` or `CONTENT_ROOTS_REQUIRED_KEYS` in `test_robust_intelligent.py` and extend the assertion.

---

## 7. References

- [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md) — Full test suite plan, CI coverage, phases
- [DOCS_INDEX.md](./DOCS_INDEX.md) — Test suite (document all) section
- [.github/workflows/core-tests.yml](../.github/workflows/core-tests.yml) — Core CI: `pytest -m "not slow"`, production gates
- [tests/conftest.py](../tests/conftest.py) — Shared fixtures
- [pytest.ini](../pytest.ini) — Markers, timeout, testpaths
