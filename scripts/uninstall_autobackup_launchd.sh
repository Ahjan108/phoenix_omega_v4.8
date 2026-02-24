#!/usr/bin/env bash
set -euo pipefail

PLIST_DST="$HOME/Library/LaunchAgents/com.ahjan.phoenix_omega.autobackup.plist"
launchctl bootout gui/"$(id -u)" com.ahjan.phoenix_omega.autobackup >/dev/null 2>&1 || true
rm -f "$PLIST_DST"
echo "Uninstalled: com.ahjan.phoenix_omega.autobackup"
