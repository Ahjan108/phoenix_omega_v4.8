#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_ROOT/artifacts/backup_logs"
LOG_FILE="$LOG_DIR/autobackup.log"
mkdir -p "$LOG_DIR"

{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] auto-backup start"
  cd "$REPO_ROOT"

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "skip: not a git repo"
    exit 0
  fi

  if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
    echo "skip: git user.name/user.email not configured"
    exit 0
  fi

  if ! git remote get-url origin >/dev/null 2>&1; then
    echo "skip: no origin remote configured"
    exit 0
  fi

  BRANCH="$(git branch --show-current)"
  if [[ -z "$BRANCH" ]]; then
    BRANCH="main"
  fi

  git add -A
  if git diff --cached --quiet; then
    echo "no changes"
    exit 0
  fi

  COMMIT_MSG="chore(backup): auto backup $(date '+%Y-%m-%d %H:%M:%S')"
  git commit -m "$COMMIT_MSG"
  git push origin "$BRANCH"
  echo "pushed: $BRANCH"
} >> "$LOG_FILE" 2>&1
