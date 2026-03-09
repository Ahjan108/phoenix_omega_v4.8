#!/usr/bin/env bash
# Full pipeline test: 15-segment render manifest (strict, no fallback).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

PLAN_ID="overthinking-genz-nyc-15seg"
FIXTURES="$REPO_ROOT/fixtures/video_pipeline_15_segment_demo"
OUT_DIR="$REPO_ROOT/artifacts/video/$PLAN_ID"

if [[ ! -f "$FIXTURES/render_manifest.json" ]]; then
  echo "Error: $FIXTURES/render_manifest.json not found." >&2
  exit 1
fi

python3 scripts/video/run_pipeline.py \
  --plan-id "$PLAN_ID" \
  --fixtures-dir "$FIXTURES" \
  --out-dir "$OUT_DIR" \
  --content-type long_form \
  --topic overthinking \
  --persona gen_z \
  --platform tiktok \
  --run-render \
  --force

echo "Video: $OUT_DIR/video.mp4"
echo "Open: open $OUT_DIR/video.mp4"
