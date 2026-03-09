#!/usr/bin/env bash
set -euo pipefail

# Installs pre-push guard in one or more repos.
# Usage:
#   scripts/git/install_push_guard.sh
#   scripts/git/install_push_guard.sh /path/to/repo1 /path/to/repo2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD_PY="${SCRIPT_DIR}/push_guard.py"

if [ ! -f "$GUARD_PY" ]; then
  echo "Missing guard script: $GUARD_PY"
  exit 1
fi

install_one() {
  local repo="$1"
  echo "[install] repo=$repo"
  cd "$repo"
  git rev-parse --is-inside-work-tree >/dev/null

  mkdir -p .githooks
  cat > .githooks/pre-push <<HOOK
#!/usr/bin/env bash
set -euo pipefail
python3 "$GUARD_PY"
HOOK
  chmod +x .githooks/pre-push

  git config core.hooksPath .githooks
  # Conservative transport settings for stability on slower links.
  git config --local http.lowSpeedLimit 1000
  git config --local http.lowSpeedTime 60

  echo "[install] done core.hooksPath=.githooks"
}

if [ "$#" -eq 0 ]; then
  install_one "$(pwd)"
else
  for repo in "$@"; do
    install_one "$repo"
  done
fi

echo "[install] complete"
