#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== Git repo =="
git rev-parse --is-inside-work-tree

echo "== Branch =="
git branch --show-current

echo "== Origin =="
git remote -v || true

echo "== launchd job =="
launchctl print gui/"$(id -u)"/com.ahjan.phoenix_omega.autobackup | head -n 30 || true

echo "== Recent autobackup log =="
tail -n 30 artifacts/backup_logs/autobackup.log 2>/dev/null || echo "No autobackup log yet"
