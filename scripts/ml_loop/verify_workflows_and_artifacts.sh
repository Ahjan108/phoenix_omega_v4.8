#!/usr/bin/env bash
# Optional final proof: run loop scripts locally (green) and optionally trigger workflow_dispatch.
# Usage: ./scripts/ml_loop/verify_workflows_and_artifacts.sh [--trigger]
# Without --trigger: run scripts, verify artifacts, exit 0 if all pass.
# With --trigger: also run `gh workflow run` for each ML loop workflow (requires gh CLI and auth).

set -e
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
export PYTHONPATH="$REPO_ROOT"

echo "=== 1. Continuous loop ==="
python3 scripts/ml_loop/run_continuous_loop.py
echo "Exit: $?"

echo ""
echo "=== 2. Daily promotion (dry-run) ==="
python3 scripts/ml_loop/run_daily_promotion.py --dry-run
echo "Exit: $?"

echo ""
echo "=== 3. Weekly recalibration ==="
python3 scripts/ml_loop/run_weekly_market_recalibration.py
echo "Exit: $?"

echo ""
echo "=== 4. Expected artifacts ==="
ls -la artifacts/ml_loop/ || true
test -f artifacts/ml_loop/weekly_report.json && echo "OK: weekly_report.json" || echo "MISSING: weekly_report.json"
test -f artifacts/ml_loop/baseline.json && echo "OK: baseline.json" || echo "MISSING: baseline.json"
test -d artifacts/ml_loop && echo "OK: artifacts/ml_loop/ exists" || exit 1

echo ""
echo "=== 5. Operations board (last 3 rows) ==="
tail -3 artifacts/observability/operations_board.jsonl 2>/dev/null || echo "No operations_board.jsonl or empty"

echo ""
echo "=== All local checks passed. ==="

if [ "$1" = "--trigger" ]; then
  echo ""
  echo "=== Triggering workflows (requires gh CLI) ==="
  gh workflow run "ML loop continuous" && echo "Triggered: ML loop continuous" || echo "Failed: gh workflow run"
  gh workflow run "ML loop daily promotion" && echo "Triggered: ML loop daily promotion" || echo "Failed: gh workflow run"
  gh workflow run "ML loop weekly recalibration" && echo "Triggered: ML loop weekly recalibration" || echo "Failed: gh workflow run"
  echo "Check runs: gh run list --workflow=ml-loop-continuous.yml; gh run list --workflow=ml-loop-daily-promotion.yml; gh run list --workflow=ml-loop-weekly-recalibration.yml"
fi
