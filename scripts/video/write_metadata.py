#!/usr/bin/env python3
"""
Metadata Writer: produces distribution_manifest.json with title, description, tags, telemetry (hook_type, etc.), primary_asset_ids.
Usage: python scripts/video/write_metadata.py --video-id <id> --plan-id <id> --title <t> --description <d> --provenance-path <path> --batch-id <id> -o distribution_manifest.json [--tags tag1,tag2] [--hook-type light_reveal] ...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import write_atomically, should_skip_output


def main() -> int:
    ap = argparse.ArgumentParser(description="Write distribution manifest with telemetry")
    ap.add_argument("--video-id", required=True)
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--description", required=True)
    ap.add_argument("--provenance-path", required=True, help="Path to video_provenance.json for partner")
    ap.add_argument("--batch-id", required=True)
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--format", default="landscape_16_9")
    ap.add_argument("--tags", default="", help="Comma-separated tags")
    ap.add_argument("--hook-type", default="light_reveal")
    ap.add_argument("--environment", default="forest_path")
    ap.add_argument("--motion-type", default="slow_zoom")
    ap.add_argument("--music-mood", default="calm")
    ap.add_argument("--caption-pattern", default="question_hook")
    ap.add_argument("--style-version", default="v1")
    ap.add_argument("--primary-asset-ids", default="", help="Comma-separated asset IDs (or from timeline)")
    ap.add_argument("--shot-plan", help="Path to shot_plan.json (to read config_hash for idempotent skip)")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists with same config_hash")
    args = ap.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    primary_asset_ids = [a.strip() for a in args.primary_asset_ids.split(",") if a.strip()] if args.primary_asset_ids else []

    config_hash = ""
    if args.shot_plan and Path(args.shot_plan).exists():
        config_hash = json.loads(Path(args.shot_plan).read_text(encoding="utf-8")).get("config_hash") or ""

    out_path = Path(args.out)
    if config_hash and should_skip_output(out_path, ["video_id", "plan_id", "config_hash"], args.force, config_hash):
        print(f"Skip (output exists with same config_hash, use --force to overwrite): {out_path}")
        return 0

    doc = {
        "video_id": args.video_id,
        "plan_id": args.plan_id,
        "config_hash": config_hash,
        "title": args.title,
        "description": args.description,
        "tags": tags,
        "video_provenance_path": args.provenance_path,
        "batch_id": args.batch_id,
        "format": args.format,
        "hook_type": args.hook_type,
        "environment": args.environment,
        "motion_type": args.motion_type,
        "music_mood": args.music_mood,
        "caption_pattern": args.caption_pattern,
        "style_version": args.style_version,
        "primary_asset_ids": primary_asset_ids,
    }
    write_atomically(out_path, doc)
    print(f"Wrote distribution manifest to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
