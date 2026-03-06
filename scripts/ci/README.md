# CI scripts and requirements

Scripts in this directory are used by production readiness gates and CI. Run from **repo root** with `PYTHONPATH=.` when needed.

## Required dependency: jsonschema

**`jsonschema` is required in CI and for ops artifact validation.** It is not optional.

- `scripts/ci/validate_ops_artifacts.py` validates JSON in `artifacts/ops` and `artifacts/waves` against schemas in `config/ops_schema_registry.yaml`. If `jsonschema` is not installed, the script **exits 1** (no silent skip).
- `scripts/run_production_readiness_gates.py` **Gate 17** requires `import jsonschema` to succeed. If it fails, the gate fails.
- **Gate 17b** (when `artifacts/ops` or `artifacts/waves` exists): the gate script runs `validate_ops_artifacts.py`; a non-zero exit fails the gate.

So in CI:

1. Install jsonschema (e.g. `pip install -r requirements.txt` or `pip install jsonschema`).
2. Gate 17 and 17b must pass; ops validation cannot be skipped.

## Running production readiness gates

From repo root:

```bash
python scripts/run_production_readiness_gates.py
```

This runs 17 conditions including Gate 17 (jsonschema required) and Gate 17b (ops/waves schema validation when those dirs exist).

**Quality/registry regression tests:** `tests/test_quality_regression.py` — malformed CANONICAL.txt, missing chapter text in plan, duplicate memorable-line collision. Run: `python -m unittest tests.test_quality_regression -v`.

**100% atoms coverage sim test:** `tests/test_atoms_coverage_100_percent.py` — requires every (persona, topic, engine) in the catalog to have a non-empty STORY pool (`atoms/{persona}/{topic}/{engine}/CANONICAL.txt`). Exit 0 only when 100%; reports shallow pools (below `min_story_pool_size`) without failing. Run: `python3 tests/test_atoms_coverage_100_percent.py` or `pytest tests/test_atoms_coverage_100_percent.py -v`. See [docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md](../../docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md) §7.

## Running pre-publish anti-spam gates

From repo root:

```bash
python scripts/ci/run_prepublish_gates.py \
  --plans-dir artifacts/waves/<wave_id>/plans \
  --index artifacts/catalog_similarity/index.jsonl \
  --wave-rendered-dir artifacts/waves/<wave_id>/rendered \
  --catalog-rendered-dir artifacts/catalog_rendered \
  --report artifacts/ops/prepublish_<wave_id>.json
```

This enforces the gate order:
1. structural entropy
2. platform similarity
3. prose duplication
4. wave density
4a. **delivery gate** — book output no placeholders (PHOENIX_FREEBIE_SYSTEM_SPEC §10.6; `check_book_output_no_placeholders.py`)
4b. series diversity
5. similarity index append (only after gates pass)

Checklist: `scripts/ci/PREPUBLISH_CHECKLIST.md`.

## No-bypass export check

**`scripts/ci/check_export_no_bypass.py`** fails if any script in `scripts/ci/export_scripts_registry.yaml` does not reference `prepare_wave_for_export`. Ensures no export path bypasses the release entrypoint. Run from repo root: `python scripts/ci/check_export_no_bypass.py`. Add any new export-triggering script to the registry; it must call the release layer.

## AI/LLM cohesive bestseller tester (10k Pearl Prime + 10k teacher-mode + v2 EI)

**`scripts/ci/llm_cohesive_bestseller_tester.py`** tests 10k Pearl Prime CLI books and 10k teacher-mode books (all personas × topics) with v2 EI to report what is 100% and cohesive bestseller quality.

- **Test read all:** `--read-all` loads and prints all config (canonical personas, topics, teacher persona matrix, format registry, EI v2).
- **Pearl Prime 10k:** use `--pearl-prime-input artifacts/simulation_10k.json` (or `--run-pearl-10k` to run the sim first).
- **Teacher matrix:** `--teacher-matrix` builds the full teacher-mode test matrix (personas × topics × teachers); cap with `--teacher-matrix-cap 10000`.
- **EI v2:** `--ei-v2-report` includes `artifacts/ei_v2/eval_rigorous_report.json` if present.
- **LLM:** `--llm` calls the model to classify cohesive bestseller gaps and what is 100%; use `--require-100` to exit 1 on any bestseller-tier failure.
- **Robust/intelligent:** Validates simulation JSON; dimension-aware analysis (pass rate by format/tier, phase2/3, EI v2 ten dimensions); severity levels (CRITICAL/HIGH/MEDIUM/LOW); health score 0–100; coverage from results; optional `--baseline` for regression; LLM response validation and retry; `--run-pearl-timeout` and `--ei-v2-threshold`.

Example (from repo root):

```bash
# Read all config only
PYTHONPATH=. python scripts/ci/llm_cohesive_bestseller_tester.py --read-all

# Full run: Pearl 10k + teacher matrix + EI v2 report + LLM
PYTHONPATH=. python scripts/ci/llm_cohesive_bestseller_tester.py \
  --pearl-prime-input artifacts/simulation_10k.json \
  --teacher-matrix --ei-v2-report --llm --out artifacts/reports
```

Outputs: `artifacts/reports/cohesive_bestseller_tester_report.json` and `cohesive_bestseller_tester_SUMMARY.txt`. For strict 100% gating, combine with `analyze_pearl_prime_sim.py --min-pass-rate 1.0`.
