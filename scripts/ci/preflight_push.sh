#!/usr/bin/env bash
# Preflight before push: block direct push to main, block orphan branches.
# Run manually before git push or install as a pre-push hook.
set -e
branch=$(git rev-parse --abbrev-ref HEAD)
remote="${1:-origin}"
if [[ "$branch" == "main" || "$branch" == "master" ]]; then
  if git rev-parse --verify "$remote/main" &>/dev/null || git rev-parse --verify "$remote/master" &>/dev/null; then
    echo "Direct push to main is not allowed. Use a PR." >&2
    exit 1
  fi
fi
base=$(git merge-base HEAD "$remote/main" 2>/dev/null || git merge-base HEAD "$remote/master" 2>/dev/null || true)
if [[ -z "$base" ]]; then
  echo "Branch has no history in common with main. Create branch from origin/main." >&2
  exit 1
fi
echo "Preflight OK."
