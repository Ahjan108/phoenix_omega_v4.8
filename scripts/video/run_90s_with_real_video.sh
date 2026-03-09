#!/usr/bin/env bash
# Build FLUX image bank for depression, then run the 90s pipeline with real assets.
# Result: video.mp4 with images + captions (no black placeholder).
# Requires: CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN (see docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md).
# Run from repo root.
set -e
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
BANK_DIR="${BANK_DIR:-$REPO_ROOT/image_bank}"
PLAN_ID="depression-genz-nyc-90s"
OUT_DIR="$REPO_ROOT/artifacts/video/$PLAN_ID"
FIXTURES="$REPO_ROOT/fixtures/video_pipeline_90s_depression"

echo "=== 1. Build FLUX image bank (depression, 6 variants per intent = 1 hook + 6 character for 7 unique clips) ==="
python3 scripts/video/run_flux_bank_build.py --topics depression --bank-dir "$BANK_DIR" --variants 6
echo ""

echo "=== 2. Run 90s pipeline with image bank ==="
python3 scripts/video/run_pipeline.py \
  --plan-id "$PLAN_ID" \
  --fixtures-dir "$FIXTURES" \
  --out-dir "$OUT_DIR" \
  --content-type long_form \
  --topic depression \
  --persona gen_z \
  --run-render \
  --assets-dir "$BANK_DIR" \
  --force

echo ""
echo "=== Video (real images + captions) ==="
echo "  $OUT_DIR/video.mp4"
echo "  Open: open $OUT_DIR/video.mp4"
