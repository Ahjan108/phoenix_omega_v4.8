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
    args = ap.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    primary_asset_ids = [a.strip() for a in args.primary_asset_ids.split(",") if a.strip()] if args.primary_asset_ids else []

    doc = {
        "video_id": args.video_id,
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
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"Wrote distribution manifest to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
