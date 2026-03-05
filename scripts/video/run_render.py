#!/usr/bin/env python3
"""
Renderer stub: accepts timeline + assets and writes a placeholder or invokes FFmpeg/Remotion.
Phase 1: writes a small placeholder file and timeline_ref.json so downstream can assume a video path exists.
Usage: python scripts/video/run_render.py <timeline.json> -o <output_dir> [--placeholder]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="Render timeline to video (stub or FFmpeg)")
    ap.add_argument("timeline", help="Path to timeline.json")
    ap.add_argument("-o", "--out-dir", required=True, help="Output directory for video and ref")
    ap.add_argument("--placeholder", action="store_true", default=True, help="Write placeholder only (default)")
    args = ap.parse_args()

    tl_path = Path(args.timeline)
    if not tl_path.exists():
        print(f"Error: not found: {tl_path}", file=sys.stderr)
        return 1
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timeline = json.loads(tl_path.read_text(encoding="utf-8"))
    plan_id = timeline.get("plan_id", "unknown")
    video_path = out_dir / f"{plan_id}.mp4"
    ref_path = out_dir / "timeline_ref.json"
    if args.placeholder:
        video_path.write_text("placeholder\n", encoding="utf-8")
    ref_path.write_text(json.dumps({"timeline_path": str(tl_path), "video_path": str(video_path)}, indent=2), encoding="utf-8")
    print(f"Render output: {video_path} (ref: {ref_path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
