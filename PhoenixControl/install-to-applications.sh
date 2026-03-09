#!/usr/bin/env bash
# Copy the built Phoenix Control.app to /Applications so you can launch from Finder and Dock.
# Run from phoenix_omega repo root after building in Xcode (Product → Build, ⌘B).

set -e
DERIVED="$HOME/Library/Developer/Xcode/DerivedData"
APP_NAME="Phoenix Control.app"

if [[ ! -d "$DERIVED" ]]; then
  echo "Xcode DerivedData not found at: $DERIVED"
  echo "Open phoenix_omega/PhoenixControl.xcodeproj in Xcode, then Product → Build (⌘B)."
  exit 1
fi

# Find real build (exclude Index.noindex — that can be incomplete and show "damaged")
SRC=$(find "$DERIVED" -name "$APP_NAME" -path "*/Build/Products/*" -type d ! -path "*Index.noindex*" 2>/dev/null | head -1)
if [[ -z "$SRC" ]]; then
  SRC=$(find "$DERIVED" -name "$APP_NAME" -path "*/Build/Products/*" -type d 2>/dev/null | head -1)
fi
if [[ -z "$SRC" ]]; then
  echo "No built app found in DerivedData."
  echo ""
  echo "Do this on this Mac:"
  echo "  1. Open Xcode"
  echo "  2. File → Open → choose: $(cd -P "$(dirname "$0")/.." && pwd)/PhoenixControl.xcodeproj"
  echo "  3. Product → Build (⌘B)"
  echo "  4. Run this script again: ./PhoenixControl/install-to-applications.sh"
  exit 1
fi

echo "Installing: $SRC → /Applications/"
rm -rf "/Applications/$APP_NAME"
cp -R "$SRC" "/Applications/$APP_NAME"
xattr -cr "/Applications/$APP_NAME"
# Ad-hoc sign so macOS doesn't show "damaged"
codesign --force --deep --sign - "/Applications/$APP_NAME" 2>/dev/null || true
echo "Done. Open: Finder → Applications → double-click Phoenix Control."
