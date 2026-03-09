#!/usr/bin/env bash
# Full pipeline test: 90s script, Gen Z, NYC, depression.
# Run from repo root. Uses placeholder render (no FFmpeg assets) unless --assets-dir is set.
set -e
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
PLAN_ID="depression-genz-nyc-90s"
FIXTURES="$REPO_ROOT/fixtures/video_pipeline_90s_depression"
OUT_DIR="$REPO_ROOT/artifacts/video/$PLAN_ID"

if [[ ! -f "$FIXTURES/render_manifest.json" ]]; then
  echo "Error: $FIXTURES/render_manifest.json not found. Create the fixture first." >&2
  exit 1
fi

echo "=== Full video pipeline test: 90s, Gen Z, NYC, depression ==="
python3 scripts/video/run_pipeline.py \
  --plan-id "$PLAN_ID" \
  --fixtures-dir "$FIXTURES" \
  --out-dir "$OUT_DIR" \
  --content-type long_form \
  --topic depression \
  --persona gen_z \
  --run-render \
  --force

echo ""
echo "=== QA: Where to find the video ==="
# Render step always writes video.mp4 (placeholder or full render)
if [[ -f "$OUT_DIR/video.mp4" ]]; then
  echo "  Video:   $OUT_DIR/video.mp4"
  echo "  Open:    open $OUT_DIR/video.mp4"
fi
echo "  Artifacts: $OUT_DIR/"
echo "  Thumbnail: $OUT_DIR/thumb.jpg"
echo "  Manifest:  $OUT_DIR/distribution_manifest.json"
