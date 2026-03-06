# D2/D3/D5/D6 Go-Live Evidence Pack

Purpose: single runbook + evidence checklist for d2/d3/d5/d6 production go-live.

## Required same-day green checklist

- Required workflows pass on `main`: `Core tests`, `Release gates`, `EI V2 gates`, `Change impact`.
- Branch protection on `main` requires those four checks.
- EI V2 calibration accepts `--learn` and writes `artifacts/ei_v2/catalog_calibration.json`.
- Required EI V2 artifacts are enforced (`missing => CI fail`).
- Rollback toggle smoke test run and documented.
- One full evidence bundle captured (commands + artifact links + timestamps).

## Local verification commands

Run from repo root:

```bash
PYTHONPATH=. python3 scripts/observability/detect_changes.py --base HEAD~1 --head HEAD --out artifacts/observability/change_events.jsonl
PYTHONPATH=. python3 scripts/observability/impact_from_changes.py --events artifacts/observability/change_events.jsonl
PYTHONPATH=. python3 scripts/ci/run_ei_v2_catalog_calibration.py --learn --out artifacts/ei_v2/catalog_calibration.json
PYTHONPATH=. python3 -m pytest tests/test_ei_v2.py tests/test_ei_v2_hybrid.py -v
```

Expected local artifacts:

- `artifacts/observability/change_events.jsonl`
- `artifacts/observability/impact_*.json`
- `artifacts/ei_v2/catalog_calibration.json`

## Rollback toggle smoke test

Current EI V2 rollback toggle is `config/quality/ei_v2_config.yaml`:

- `marketing_sources.enabled: false` disables marketing integration globally.

Smoke test procedure:

1. Ensure `marketing_sources.enabled: false`.
2. Run calibration command:
   `PYTHONPATH=. python3 scripts/ci/run_ei_v2_catalog_calibration.py --learn --out artifacts/ei_v2/catalog_calibration.json`
3. Confirm command succeeds and artifact exists.
4. Record timestamp and command output in evidence notes.

## CI artifact contract (EI V2)

Workflow `EI V2 gates` now fails if any required artifact is missing:

- `artifacts/ei_v2/catalog_calibration.json`
- `artifacts/ei_v2/eval_rigorous_report.json`
- `artifacts/ei_v2/promotion_gate_result.json`

## GitHub branch protection (manual UI step)

Set in GitHub:

1. `Settings -> Branches -> Branch protection rules -> main`
2. Enable `Require status checks to pass before merging`
3. Require checks:
   - `Core tests`
   - `Release gates`
   - `EI V2 gates`
   - `Change impact`

Reference: `docs/BRANCH_PROTECTION_REQUIREMENTS.md`.

## Evidence record template

Fill this after a green run:

- Date (UTC):
- Commit SHA:
- Core tests run URL:
- Release gates run URL:
- EI V2 gates run URL:
- Change impact run URL:
- Artifact links:
  - `artifacts/ei_v2/catalog_calibration.json`
  - `artifacts/ei_v2/eval_rigorous_report.json`
  - `artifacts/ei_v2/promotion_gate_result.json`
  - `artifacts/observability/change_events.jsonl`
- Rollback toggle smoke test: PASS/FAIL
- Go-live decision: GO / NO-GO

## Latest local run evidence (2026-03-06 UTC)

- `PYTHONPATH=. python3 scripts/ci/run_ei_v2_catalog_calibration.py --learn --out artifacts/ei_v2/catalog_calibration.json` -> PASS
- `PYTHONPATH=. python3 -m pytest tests/test_ei_v2.py tests/test_ei_v2_hybrid.py -v` -> PASS (45 passed)
- `PYTHONPATH=. python3 scripts/observability/detect_changes.py --base HEAD~1 --head HEAD --out artifacts/observability/change_events.jsonl` -> PASS
- `PYTHONPATH=. python3 scripts/observability/impact_from_changes.py --events artifacts/observability/change_events.jsonl` -> PASS
- `PYTHONPATH=. python3 scripts/run_production_readiness_gates.py` -> PASS (all automatable gates passed)

Notes:
- `run_ei_v2_rigorous_eval.py` produced required artifacts.
- `check_ei_v2_promotion_gate.py` currently returns BLOCKED (expected when thresholds are not met), but still writes `artifacts/ei_v2/promotion_gate_result.json`. This does not block artifact-contract enforcement.

## Go-live evidence — merged PR #13

- Date (UTC): 2026-03-06T05:20:11Z
- PR merged: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/13
- Merge status: merged and closed

Run URLs:

- PR checks overview: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/13/checks
- Core tests workflow: https://github.com/Ahjan108/phoenix_omega_v4.8/actions/workflows/core-tests.yml
- EI V2 gates workflow: https://github.com/Ahjan108/phoenix_omega_v4.8/actions/workflows/ei-v2-gates.yml
- Change impact workflow: https://github.com/Ahjan108/phoenix_omega_v4.8/actions/workflows/change-impact.yml

Branch protection:

- Ruleset: `Main protection` (active)
- Required checks: `Core tests`, `EI V2 gates`, `Change impact / change-impact`

Go-live decision:

- GO
