#!/usr/bin/env bash
# Download and unzip a brand packet from a signed URL.
# Usage: fetch_brand_packet.sh <signed_url> [output_dir]
# Requires: curl, unzip
set -euo pipefail
URL="${1:?Usage: fetch_brand_packet.sh <signed_url> [output_dir]}"
OUT_DIR="${2:-.}"
mkdir -p "$OUT_DIR"
ZIP="$OUT_DIR/packet.zip"
echo "Downloading to $ZIP ..."
curl -fSL -o "$ZIP" "$URL"
echo "Unzipping ..."
unzip -o "$ZIP" -d "$OUT_DIR"
echo "Done. Contents in $OUT_DIR"
