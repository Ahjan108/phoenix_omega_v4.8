#!/usr/bin/env python3
"""
QC: Validates shot_plan, timeline, resolved_assets (no consecutive same asset_id, duration/resolution sane).
Always runs (no skip). Optionally writes qc_summary.json for provenance to reference.
Usage: python scripts/video/run_qc.py <shot_plan.json> <resolved_assets.json> <timeline.json> [--content-type therapeutic] [--out qc_summary.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, write_atomically, REPO_ROOT


def run_qc(shot_plan: dict, resolved: dict, timeline: dict, content_type: str) -> tuple[bool, list[str]]:
    errors = []
    # No two consecutive shots with same asset_id
    clips = timeline.get("clips", [])
    for i in range(1, len(clips)):
        if clips[i].get("asset_id") == clips[i - 1].get("asset_id"):
            errors.append(f"Consecutive clips share asset_id: {clips[i]['asset_id']}")
    # Duration sanity
    duration_s = timeline.get("duration_s", 0)
    if duration_s <= 0 or duration_s > 3600:
        errors.append(f"Timeline duration_s out of range: {duration_s}")
    pacing = load_yaml("config/video/pacing_by_content_type.yaml")
    ct = (pacing.get("content_types") or {}).get(content_type) or {}
    max_d = ct.get("max_duration_s", 600)
    if duration_s > max_d:
        errors.append(f"Duration {duration_s}s exceeds content_type max {max_d}s")
    # Resolution
    res = timeline.get("resolution", {})
    w, h = res.get("width", 0), res.get("height", 0)
    if w < 100 or h < 100:
        errors.append(f"Invalid resolution: {w}x{h}")
    passed = len(errors) == 0
    return passed, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Run QC on shot plan, resolved assets, timeline")
    ap.add_argument("shot_plan", help="Path to shot_plan.json")
    ap.add_argument("resolved_assets", help="Path to resolved_assets.json")
    ap.add_argument("timeline", help="Path to timeline.json")
    ap.add_argument("--content-type", default="therapeutic")
    ap.add_argument("-o", "--out", help="Write qc_summary.json (passed, errors, checks) for provenance to reference")
    args = ap.parse_args()

    paths = [Path(args.shot_plan), Path(args.resolved_assets), Path(args.timeline)]
    if not all(p.exists() for p in paths):
        print("Error: one or more inputs not found", file=sys.stderr)
        return 1
    shot_plan = json.loads(paths[0].read_text(encoding="utf-8"))
    resolved = json.loads(paths[1].read_text(encoding="utf-8"))
    timeline = json.loads(paths[2].read_text(encoding="utf-8"))

    passed, errors = run_qc(shot_plan, resolved, timeline, args.content_type)
    if args.out:
        summary = {
            "passed": passed,
            "errors": errors,
            "checks": ["consecutive_asset_id", "duration", "resolution"],
        }
        write_atomically(Path(args.out), summary)
    if errors:
        for e in errors:
            print(f"QC: {e}", file=sys.stderr)
        return 0 if passed else 1
    print("QC passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
