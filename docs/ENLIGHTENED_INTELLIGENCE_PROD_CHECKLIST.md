# Enlightened Intelligence — Production Checklist

**Definition of Done:** Test slice is **PASS** when all 4 targeted unit tests pass. **Production-go-live is 100%** only when all operational gates are confirmed on `main` with evidence links.

---

## Test Slice (Code/Tests — PASS)

The following 4 tests validate the hardened EI behaviors. All must pass before declaring the test slice complete.

| Test | Validates |
|------|-----------|
| `test_ei_adapter_llm_override_skipped_for_rule_best_when_disallowed` | `rule_best` + `allow_override_for_rule_best=false` → LLM never overrides; hash choice stands |
| `test_ei_llm_judge_cache_returns_last_match` | JSONL cache returns last matching entry (last write wins) |
| `test_ei_adapter_thesis_similarity_uses_config_floor_ceiling` | Thesis alignment uses config-driven floor/ceiling from registry |
| `test_teacher_integrity_softening_scoped_to_configured_categories` | Softening applies only to `soften_categories`; promo/miracle/endorsement stay full penalty |

### Run test slice

```bash
PYTHONPATH=. python -m pytest tests/test_enlightened_intelligence.py -v -k "llm_override or cache or thesis or softening"
```

Or run all EI tests:

```bash
PYTHONPATH=. python -m pytest tests/test_enlightened_intelligence.py -v
```

---

## Operational Gates (Production 100%)

These gates must be confirmed **on `main`** with evidence links before declaring EI production-ready. Rollback validation is recommended before go-live.

| # | Gate | Evidence link |
|---|------|---------------|
| 1 | **Merge to `main`** | PR URL: _______________ |
| 2 | **CI green on `main`** | EI tests (or full suite) in CI workflow run URL: _______________ |
| 3 | **Runtime/scheduled smoke** | Pipeline smoke run on `main` with EI path exercised: _______________ |
| 4 | **Secrets** | Embedding/LLM API keys (if used) configured and verified: _______________ |
| 5 | **Checklist evidence** | All above cells filled; Evidence Lock (below) signed |
| 6 | **Rollback proof** | Rollback procedure validated at least once: _______________ |

---

## Pre-Merge Verification

1. [ ] Run `pytest tests/test_enlightened_intelligence.py -v`
2. [ ] Confirm all 4 targeted tests pass
3. [ ] Push branch and verify CI workflow passes

---

## Rollback Procedure (recommended before go-live)

Validate **at least once** before go-live. Document date and outcome.

1. **Disable EI features** — Set `enlightened_intelligence.enabled: false` in registry config; or `slots.*.enabled: false` per slot.
2. **Disable embedding/LLM** — Set `embeddings.enabled: false` and `llm_judge.enabled: false` in registry.
3. **Fallback to rule_best** — Set `selector: rule_best` for affected slots.

| Step | Validated | Date | Owner |
|------|-----------|------|-------|
| Disable EI features | [ ] | | |
| Disable embedding/LLM | [ ] | | |
| Fallback to rule_best | [ ] | | |

---

## Related docs

- [config/source_of_truth/enlightened_intelligence_registry.yaml](../config/source_of_truth/enlightened_intelligence_registry.yaml) — EI registry config
- [phoenix_v4/quality/ei_adapter.py](../phoenix_v4/quality/ei_adapter.py) — Adapter, selection logic
- [phoenix_v4/quality/ei_llm_judge.py](../phoenix_v4/quality/ei_llm_judge.py) — LLM tie-break
- [phoenix_v4/quality/ei_embeddings.py](../phoenix_v4/quality/ei_embeddings.py) — Embedding thesis alignment
- [phoenix_v4/quality/teacher_integrity.py](../phoenix_v4/quality/teacher_integrity.py) — Teacher integrity scoring
