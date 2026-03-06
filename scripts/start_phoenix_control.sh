#!/usr/bin/env bash
# Start Phoenix Control (Pearl Prime / Simulation UI and control plane).
# From repo root: ./scripts/start_phoenix_control.sh
# Option 1: Opens Xcode with the project — press ⌘R to run.
# Option 2: If full Xcode is active, builds and launches the app.

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$REPO_ROOT/PhoenixControl/PhoenixControl.xcodeproj"
SCHEME="Phoenix Control"

# If xcodebuild is from full Xcode (not just Command Line Tools), build and open the app.
BUILD_DIR="$REPO_ROOT/build/PhoenixControl"
if xcode-select -p 2>/dev/null | grep -q "Xcode.app"; then
  echo "Building Phoenix Control..."
  if xcodebuild -project "$PROJECT" -scheme "$SCHEME" -destination "platform=macOS" -configuration Debug -derivedDataPath "$BUILD_DIR" build -quiet 2>/dev/null; then
    APP="$BUILD_DIR/Build/Products/Debug/Phoenix Control.app"
    if [ -d "$APP" ]; then
      echo "Launching Phoenix Control..."
      open "$APP"
      exit 0
    fi
  fi
fi

# Fallback: open project in Xcode so you can press ⌘R.
echo "Opening Phoenix Control in Xcode — press ⌘R to run."
open "$PROJECT"
