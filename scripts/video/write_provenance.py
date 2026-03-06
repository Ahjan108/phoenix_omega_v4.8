#!/usr/bin/env python3
"""
Provenance Writer: writes video_provenance.json for a rendered video (plan_id, assets, QC, telemetry).
Usage: python scripts/video/write_provenance.py --video-id <id> --plan-id <id> --shot-plan <path> --resolved <path> --timeline <path> -o provenance.json [--qc-passed] [--hook-type light_reveal] ...
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import write_atomically, should_skip_output


def main() -> int:
    ap = argparse.ArgumentParser(description="Write video provenance record")
    ap.add_argument("--video-id", required=True, help="Video identifier")
    ap.add_argument("--plan-id", required=True, help="Plan ID")
    ap.add_argument("--shot-plan", required=True, help="Path to shot_plan.json")
    ap.add_argument("--resolved", required=True, help="Path to resolved_assets.json")
    ap.add_argument("--timeline", required=True, help="Path to timeline.json")
    ap.add_argument("--script-segments", default="", help="Path to script_segments.json (for script_segments_id)")
    ap.add_argument("-o", "--out", required=True, help="Output provenance JSON path")
    ap.add_argument("--content-type", default="therapeutic")
    ap.add_argument("--duration-s", type=float, default=0.0, help="Duration seconds (default: from timeline)")
    ap.add_argument("--qc-passed", action="store_true", default=True)
    ap.add_argument("--hook-type", default="light_reveal")
    ap.add_argument("--environment", default="forest_path")
    ap.add_argument("--motion-type", default="slow_zoom")
    ap.add_argument("--music-mood", default="calm")
    ap.add_argument("--caption-pattern", default="question_hook")
    ap.add_argument("--style-version", default="v1")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists with same config_hash")
    args = ap.parse_args()

    plan_path = Path(args.shot_plan)
    res_path = Path(args.resolved)
    tl_path = Path(args.timeline)
    if not plan_path.exists() or not res_path.exists() or not tl_path.exists():
        print("Error: shot_plan, resolved, or timeline not found", file=sys.stderr)
        return 1
    shot_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    resolved = json.loads(res_path.read_text(encoding="utf-8"))
    timeline = json.loads(tl_path.read_text(encoding="utf-8"))

    duration_s = args.duration_s or timeline.get("duration_s", 0.0)
    primary_asset_ids = [c.get("asset_id") for c in timeline.get("clips", []) if c.get("asset_id")]

    config_hash = shot_plan.get("config_hash") or timeline.get("config_hash") or ""

    out_path = Path(args.out)
    if should_skip_output(out_path, ["video_id", "plan_id", "config_hash"], args.force, config_hash):
        print(f"Skip (output exists with same config_hash, use --force to overwrite): {out_path}")
        return 0

    doc = {
        "video_id": args.video_id,
        "plan_id": args.plan_id,
        "content_type": args.content_type,
        "config_hash": config_hash,
        "duration_s": duration_s,
        "render_manifest_id": args.plan_id,
        "script_segments_id": args.plan_id,
        "qc_summary": {"passed": args.qc_passed, "checks": ["duration", "resolution", "captions"]},
        "format_adaptations": [timeline.get("aspect_ratio", "16:9")],
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hook_type": args.hook_type,
        "environment": args.environment,
        "motion_type": args.motion_type,
        "music_mood": args.music_mood,
        "caption_pattern": args.caption_pattern,
        "style_version": args.style_version,
        "primary_asset_ids": primary_asset_ids,
    }
    write_atomically(out_path, doc)
    print(f"Wrote provenance to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
