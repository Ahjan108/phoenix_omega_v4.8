#!/usr/bin/env python3
"""
Create test images for render smoke test. Asset IDs match fixtures/video_pipeline/timeline.json
(asset-hook-001, asset-body-001). Images are 1200x2133 JPEG (suitable for scale step in run_render).
Usage:
  python scripts/video/create_test_assets.py [--dir /tmp/test_assets]
  python scripts/video/run_render.py fixtures/video_pipeline/timeline.json -o /tmp/test_render --assets-dir /tmp/test_assets --video-id test-001
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import get_ffmpeg_bin

# Asset IDs from fixtures/video_pipeline/timeline.json
ASSET_IDS = ("asset-hook-001", "asset-body-001")
W, H = 1200, 2133


def main() -> int:
    ap = argparse.ArgumentParser(description="Create test JPEGs for render smoke test")
    ap.add_argument("--dir", default="/tmp/test_assets", help="Output directory for asset images")
    args = ap.parse_args()
    out_dir = Path(args.dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, asset_id in enumerate(ASSET_IDS):
        # Different solid color per asset so motion/zoompan is visible
        color = "blue" if i == 0 else "navy"
        path = out_dir / f"{asset_id}.jpg"
        r = subprocess.run(
            [
                get_ffmpeg_bin(), "-y", "-f", "lavfi", "-i", f"color=c={color}:s={W}x{H}:d=1",
                "-frames:v", "1", str(path),
            ],
            capture_output=True,
        )
        if r.returncode != 0:
            print(f"ffmpeg failed: {r.stderr.decode()}", file=sys.stderr)
            return 1
        print(f"Created {path}")
    print(f"Run: python scripts/video/run_render.py {REPO_ROOT}/fixtures/video_pipeline/timeline.json -o /tmp/test_render --assets-dir {out_dir} --video-id test-001")
    return 0


if __name__ == "__main__":
    sys.exit(main())
