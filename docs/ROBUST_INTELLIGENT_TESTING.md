# Robust & Intelligent Testing — Plan and How to Fix

**Purpose:** Make the Phoenix test suite more robust (reliable, deterministic, well-covered) and more intelligent (smarter coverage, parametrization, contract and property-style tests).  
**Authority:** Complements [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md) and [DOCS_INDEX.md](./DOCS_INDEX.md) Test suite section.  
**Last updated:** 2026-03-04

---

## 1. What “robust” and “intelligent” mean here

| Term | Meaning | Examples |
|------|--------|----------|
| **Robust** | Tests are reliable, deterministic, and fail only for real regressions. | No silent skips when fixtures are missing; fail fast with clear errors; no flake from time/network; shared fixtures in conftest. |
| **Intelligent** | Tests exercise more behavior with less brittle, repetitive code. | Parametrize over inputs; property-based or fuzz for invariants; contract tests for boundaries; coverage of edge cases and error paths. |

---

## 2. Current gaps (summary)

- **Silent skips:** Some tests `return` or skip when a fixture path is missing, so missing fixtures go unnoticed.
- **No coverage gate:** No pytest-cov (or similar) in CI; coverage is not measured or enforced.
- **Little parametrization:** Only a couple of test files use `@pytest.mark.parametrize`; most tests are one-off cases.
- **Missing test module:** `tests/test_ei_v2_hybrid.py` was referenced in DOCS_INDEX and EI V2 gates workflow but did not exist (now added).
- **Slow tests never in CI:** Tests marked `@pytest.mark.slow` are excluded from core-tests; they only run in release-gates or manually.
- **No property-based tests:** No Hypothesis (or similar) for invariants (e.g. slot resolver always returns index in range, safety score in [0,1]).

---

## 3. How to fix — prioritized

### 3.1 Immediate (already done or quick wins)

| Fix | Action |
|-----|--------|
| **Add missing EI V2 hybrid tests** | **Done.** `tests/test_ei_v2_hybrid.py` exists with 17 tests: one always runs (EI V2 package + `run_ei_v2_analysis`); 16 require `learner`, `dimension_gates`, `hybrid_selector` and skip with a clear message until those modules exist in the repo. EI V2 gates workflow and DOCS_INDEX no longer reference a missing file. |
| **Fail fast on missing fixtures** | In `conftest.py`, add optional fixtures that raise a clear error if a required path is missing (e.g. `bindings_path`), and use them in tests that currently do `if not path.exists(): return`. |
| **Parametrize key behaviors** | In at least one high-value file (e.g. `test_ei_v2.py` or `test_book_renderer.py`), add `@pytest.mark.parametrize` for multiple inputs (safe/unsafe text, different slot types) so one test function covers several cases. |

### 3.2 Short term (robustness)

| Fix | Action |
|-----|--------|
| **Replace silent skips with explicit skip or fail** | Where tests do `if not bindings_path.exists(): return`, replace with `pytest.skip("Fixture missing: ...")` or `pytest.importorskip` / require fixture and `pytest.raise` so CI and developers see the reason. |
| **Add pytest-cov to CI** | Add `pytest-cov` to `requirements-test.txt`; in core-tests (or a separate job), run `pytest --cov=phoenix_v4 --cov-report=term-missing --cov-fail-under=50` (or a chosen threshold). Start low (e.g. 40%); raise over time. |
| **Mark and document slow tests** | Ensure every long-running test is marked `@pytest.mark.slow` and listed in FULL_REPO_TEST_SUITE_PLAN; add a weekly or release job that runs the full suite including slow. |

### 3.3 Medium term (intelligence)

| Fix | Action |
|-----|--------|
| **Property-based tests for resolvers and scoring** | Add Hypothesis for: `_selector_index(key, n)` always in `[0, n)`; safety classifier output risk in [0,1]; composite scores bounded. One new file e.g. `tests/test_property_resolvers.py`. |
| **Contract tests for renderer and delivery** | Encode “delivery contract” (no `---`, no `===CHAPTER`, no unresolved `{var}`) and word-count bounds in a small contract test that runs on a set of plan + rendered outputs (golden or generated). |
| **Golden / snapshot for critical outputs** | For Tier 0 manuscript output or EI V2 comparison report shape, add a golden file and a test that compares structure (and optionally key fields) so format regressions are caught. |

### 3.4 Optional (further intelligence)

| Fix | Action |
|-----|--------|
| **Mutation testing** | Use `mutmut` or similar on a subset of modules (e.g. slot_resolver, safety_classifier) to find tests that don’t actually detect changes. |
| **Fuzz safety classifier** | Feed random or mutated text into the safety classifier and assert it never crashes and risk stays in [0,1]. |
| **Structured coverage** | Use coverage to find untested branches in `phoenix_v4/quality/` and `phoenix_v4/rendering/` and add targeted tests. |

---

## 4. Conftest improvements (fail fast)

**Current:** `conftest.py` provides `repo_root`, `fixtures_dir`, `config_root`, `atoms_root`.

**Add (optional):**

- **`require_fixtures_dir`** — fixture that fails the test with a clear message if `fixtures_dir` is missing or empty for required subdirs (e.g. `fixtures/atoms`, `fixtures/bindings`). Tests that need these request `require_fixtures_dir` instead of silently returning.
- **`golden_bindings_path`** — returns `fixtures_dir / "bindings" / "golden_test_bindings.yaml"` and uses `pytest.skip("...")` if missing, so the skip is visible in the run.

Example pattern for tests that currently do silent return:

```python
def test_used_ids_excluded(golden_bindings_path):
    if golden_bindings_path is None:
        pytest.skip("golden_test_bindings.yaml not found")
    # ... rest of test
```

Or a strict fixture that fails:

```python
@pytest.fixture
def require_golden_bindings(fixtures_dir):
    p = fixtures_dir / "bindings" / "golden_test_bindings.yaml"
    if not p.exists():
        raise FileNotFoundError(f"Required fixture missing: {p}")
    return p
```

---

## 5. Coverage in CI

1. Add to `requirements-test.txt`: `pytest-cov>=4.0`
2. In `.github/workflows/core-tests.yml`, add an optional step (or a separate job) after “Run fast/core pytest”:
   - Run: `PYTHONPATH=. python -m pytest tests/ -m "not slow" --cov=phoenix_v4 --cov-report=term-missing --cov-fail-under=40 -v --tb=short`
   - Start with `--cov-fail-under=40`; once green, raise to 50 and then 60 as you add tests.
3. Optionally upload `coverage.xml` and use a coverage badge or status check.

---

## 6. Parametrization examples

**Safety classifier (test_ei_v2.py):**

```python
@pytest.mark.parametrize("text,expect_high_risk", [
    (SAMPLE_STORY_SAFE, False),
    (SAMPLE_STORY_UNSAFE, True),
    ("Sign up now for my exclusive program.", True),
    ("", False),
])
def test_safety_classifier_parametrized(text, expect_high_risk):
    from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
    r = classify_safety(text)
    if expect_high_risk:
        assert r["risk_score"] > 0.3
    else:
        assert r["risk_score"] <= 0.5
```

**Placeholder / silence (test_book_renderer.py):**

```python
@pytest.mark.parametrize("atom_id,is_placeholder,slot_type", [
    ("placeholder:STORY:ch0:slot2", True, "STORY"),
    ("silence:REFLECTION:ch1:slot3", True, "REFLECTION"),
    ("nyc_executives_self_worth_shame_EMBODIMENT_v04", False, None),
])
def test_placeholder_silence_helpers_parametrized(atom_id, is_placeholder, slot_type):
    assert _is_placeholder_or_silence(atom_id) == is_placeholder
    if slot_type:
        assert _slot_type_from_placeholder_or_silence(atom_id) == slot_type
```

---

## 7. Property-based example (Hypothesis)

Optional dependency: `hypothesis` in `requirements-test.txt`.

```python
# tests/test_property_resolvers.py
from hypothesis import given, strategies as st

@given(key=st.text(min_size=1, max_size=200), n=st.integers(min_value=1, max_value=1000))
def test_selector_index_in_range(key, n):
    from phoenix_v4.planning.slot_resolver import _selector_index
    idx = _selector_index(key, n)
    assert 0 <= idx < n
```

---

## 8. References

- [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md) — Test inventory, CI matrix, phases
- [DOCS_INDEX.md](./DOCS_INDEX.md) — Test suite (document all) section
- [RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md) — Production 100% and simulation vs real canaries
