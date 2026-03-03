#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not a git repository: $REPO_ROOT" >&2
  exit 1
fi

if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "ERROR: Git user.name/user.email not configured." >&2
  echo "Run: git config --global user.name 'Your Name'" >&2
  echo "     git config --global user.email 'you@example.com'" >&2
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "ERROR: No 'origin' remote configured." >&2
  echo "Run: git remote add origin <github_repo_url>" >&2
  exit 1
fi

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  BRANCH="main"
fi

MSG="${1:-chore(backup): manual backup $(date '+%Y-%m-%d %H:%M:%S')}"

git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

git commit -m "$MSG"
git push -u origin "$BRANCH"
echo "Manual backup pushed to origin/$BRANCH"
