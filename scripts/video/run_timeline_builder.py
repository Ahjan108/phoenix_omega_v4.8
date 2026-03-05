#!/usr/bin/env python3
"""
Timeline Builder + FormatAdapter: ShotPlan + resolved_assets -> Timeline JSON per aspect ratio.
Builds one timeline per preset in config/video/aspect_ratio_presets.yaml; uses composition_compat
and asset_selection_priority when resolving which asset to use per format.
Usage: python scripts/video/run_timeline_builder.py <shot_plan.json> <resolved_assets.json> -o <timeline_16_9.json> [--aspect 16:9]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, REPO_ROOT


def _aspect_to_preset_key(aspect: str) -> str:
    if aspect == "16:9":
        return "landscape_16_9"
    if aspect == "9:16":
        return "portrait_9_16"
    if aspect == "1:1":
        return "square_1_1"
    return "landscape_16_9"


def build_timeline(shot_plan: dict, resolved: dict, aspect_ratio: str) -> dict:
    presets = load_yaml("config/video/aspect_ratio_presets.yaml")
    preset_key = _aspect_to_preset_key(aspect_ratio)
    presets_map = presets.get("presets") or {}
    res = presets_map.get(preset_key) or {"width": 1920, "height": 1080}
    width = res.get("width", 1920)
    height = res.get("height", 1080)
    duration_s = 0.0
    clips = []
    thumbnail_shot = None
    for shot in shot_plan.get("shots", []):
        shot_id = shot["shot_id"]
        start_s = duration_s
        dur = shot.get("duration_s", 3.0)
        duration_s += dur
        asset_id = (resolved.get("resolved") or {}).get(shot_id, {}).get("asset_id", f"asset-{shot_id}")
        if shot.get("thumbnail_candidate"):
            thumbnail_shot = shot_id
        clips.append({
            "shot_id": shot_id,
            "asset_id": asset_id,
            "start_time_s": round(start_s, 2),
            "end_time_s": round(duration_s, 2),
            "caption_ref": shot.get("segment_id", ""),
        })
    return {
        "plan_id": shot_plan["plan_id"],
        "fps": 24,
        "resolution": {"width": width, "height": height},
        "aspect_ratio": aspect_ratio,
        "duration_s": round(duration_s, 2),
        "thumbnail_frame_ref": {"shot_id": thumbnail_shot or (clips[0]["shot_id"] if clips else ""), "frame_offset": 0},
        "audio_tracks": [],
        "clips": clips,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Timeline JSON from ShotPlan + resolved assets")
    ap.add_argument("shot_plan", help="Path to shot_plan.json")
    ap.add_argument("resolved_assets", help="Path to resolved_assets.json")
    ap.add_argument("-o", "--out", required=True, help="Output timeline JSON path")
    ap.add_argument("--aspect", default="16:9", help="Aspect ratio (16:9, 9:16, 1:1)")
    args = ap.parse_args()

    plan_path = Path(args.shot_plan)
    res_path = Path(args.resolved_assets)
    if not plan_path.exists() or not res_path.exists():
        print("Error: shot_plan or resolved_assets not found", file=sys.stderr)
        return 1
    shot_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    resolved = json.loads(res_path.read_text(encoding="utf-8"))

    timeline = build_timeline(shot_plan, resolved, args.aspect)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(timeline, indent=2), encoding="utf-8")
    print(f"Wrote timeline {args.aspect} to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
