#!/usr/bin/env bash
# Rollback smoke: verify rollback path works.
# Run after restore-from-backup in DR drill.
# Exit 0 = rollback path OK; exit 1 = failure.
# Evidence: writes artifacts/release/rollback_smoke_evidence.json
set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
EVIDENCE_DIR="${REPO_ROOT}/artifacts/release"
mkdir -p "$EVIDENCE_DIR"
EVIDENCE="${EVIDENCE_DIR}/rollback_smoke_evidence.json"

# Resolve Python interpreter deterministically.
if [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "{\"step\":\"python\",\"passed\":false,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"error\":\"python_not_found\"}" > "$EVIDENCE"
  echo "No Python interpreter found."
  exit 1
fi

# 1. Run production gates after "restore"
echo "Running production readiness gates (post-restore)..."
if ! PYTHONPATH=. "$PYTHON_BIN" scripts/run_production_readiness_gates.py; then
  echo "{\"step\":\"gates\",\"passed\":false,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$EVIDENCE"
  exit 1
fi

# 2. Run fast pytest
echo "Running fast pytest..."
if ! PYTHONPATH=. "$PYTHON_BIN" -m pytest tests/ -m "not slow" -v --tb=short -x; then
  echo "{\"step\":\"pytest\",\"passed\":false,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$EVIDENCE"
  exit 1
fi

# 3. Write evidence
echo "{\"step\":\"rollback_smoke\",\"passed\":true,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$EVIDENCE"
echo "Rollback smoke complete. Evidence: $EVIDENCE"
