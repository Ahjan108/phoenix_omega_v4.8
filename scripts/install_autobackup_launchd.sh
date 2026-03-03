#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_SRC="$REPO_ROOT/ops/launchd/com.ahjan.phoenix_omega.autobackup.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.ahjan.phoenix_omega.autobackup.plist"

mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"

launchctl bootout gui/"$(id -u)" com.ahjan.phoenix_omega.autobackup >/dev/null 2>&1 || true
launchctl bootstrap gui/"$(id -u)" "$PLIST_DST"
launchctl enable gui/"$(id -u)"/com.ahjan.phoenix_omega.autobackup

echo "Installed and enabled: com.ahjan.phoenix_omega.autobackup"
launchctl print gui/"$(id -u)"/com.ahjan.phoenix_omega.autobackup | head -n 40 || true
