#!/usr/bin/env bash
set -euo pipefail

# Installs a LaunchAgent that runs the runner watchdog every 5 minutes.
# When run from phoenix_omega: WATCHDOG_SCRIPT defaults to this repo's scripts/runner/runner_watchdog.sh.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_DIR="${RUNNER_DIR:-${HOME}/actions-runner}"
WATCHDOG_SCRIPT="${WATCHDOG_SCRIPT:-$SCRIPT_DIR/runner_watchdog.sh}"
PLIST_ID="${PLIST_ID:-com.ahjan.phoenix.runner.watchdog}"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_ID}.plist"
LOG_DIR="$RUNNER_DIR/_diag/watchdog"

mkdir -p "$LOG_DIR"

cat >"$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_ID}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${WATCHDOG_SCRIPT}</string>
  </array>
  <key>StartInterval</key>
  <integer>300</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/launchd_watchdog.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/launchd_watchdog.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)/${PLIST_ID}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl kickstart -k "gui/$(id -u)/${PLIST_ID}"

echo "Installed watchdog LaunchAgent:"
echo "  ${PLIST_PATH}"
echo "Status:"
launchctl print "gui/$(id -u)/${PLIST_ID}" | head -n 40 || true
