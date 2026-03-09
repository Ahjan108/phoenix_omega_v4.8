#!/usr/bin/env bash
set -euo pipefail

# Guarded push with retry for transient network failures.
# Uses push_guard.py to block oversized pushes before upload starts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/push_guard.py"

attempt=1
max_attempts=3
while [ "$attempt" -le "$max_attempts" ]; do
  echo "[safe-push] attempt=$attempt"
  if git push "$@"; then
    echo "[safe-push] push succeeded"
    exit 0
  fi
  if [ "$attempt" -eq "$max_attempts" ]; then
    echo "[safe-push] push failed after ${max_attempts} attempts"
    exit 1
  fi
  sleep $((attempt * 5))
  attempt=$((attempt + 1))
done
