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
