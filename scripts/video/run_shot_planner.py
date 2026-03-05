#!/usr/bin/env python3
"""
Shot Planner: script_segments -> ShotPlan (shot_id, visual_intent, duration_s, thumbnail_candidate, prompt_bundle).
Uses config/video/pacing_by_content_type.yaml, visual_intent_defaults.yaml, hook_selection_rules.
Usage: python scripts/video/run_shot_planner.py <script_segments.json> -o <shot_plan.json> [--content-type therapeutic]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, config_snapshot_hash, write_atomically, should_skip_output, REPO_ROOT


def _visual_intent_for_segment(seg: dict, index: int, hook_rules: dict) -> str:
    meta = seg.get("metadata") or {}
    arc_role = meta.get("arc_role", "")
    if arc_role == "hook" or index == 0:
        topic_or_emotion = meta.get("emotional_band") or meta.get("topic") or "default"
        mapping = (hook_rules.get("topic_or_emotion_to_hook") or {}).get(topic_or_emotion) or hook_rules.get("topic_or_emotion_to_hook", {}).get("default", "emotional_mirror")
        if mapping == "calm_curiosity" or mapping == "slow_reveal":
            return "HOOK_VISUAL"
        return "HOOK_VISUAL"
    return "CHARACTER_EMOTION"


def _motion_for_intent(visual_intent: str, defaults: dict) -> str:
    d = (defaults.get("defaults") or {}).get(visual_intent) or {}
    return d.get("motion", "static")


def run_shot_planner(script_segments: dict, content_type: str) -> dict:
    pacing = load_yaml("config/video/pacing_by_content_type.yaml")
    intent_defaults = load_yaml("config/video/visual_intent_defaults.yaml")
    hook_rules = load_yaml("config/video/hook_selection_rules.yaml")
    ct = (pacing.get("content_types") or {}).get(content_type) or pacing.get("content_types", {}).get("default", {})
    aspect_ratio = "16:9"
    shots = []
    for i, seg in enumerate(script_segments["segments"]):
        start_s = seg["start_time_s"]
        end_s = seg["end_time_s"]
        duration_s = round(end_s - start_s, 2)
        visual_intent = _visual_intent_for_segment(seg, i, hook_rules)
        motion = _motion_for_intent(visual_intent, intent_defaults)
        shots.append({
            "shot_id": f"shot-{i + 1}",
            "segment_id": seg["segment_id"],
            "visual_intent": visual_intent,
            "aspect_ratio": aspect_ratio,
            "duration_s": duration_s,
            "thumbnail_candidate": i == 0,
            "prompt_bundle": {"style": "warm_illustration", "motion": motion},
        })
    config_hash = config_snapshot_hash()
    return {
        "plan_id": script_segments["plan_id"],
        "content_type": content_type,
        "config_hash": config_hash,
        "shots": shots,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Produce ShotPlan from script segments")
    ap.add_argument("script_segments", help="Path to script_segments.json")
    ap.add_argument("-o", "--out", required=True, help="Output shot_plan.json path")
    ap.add_argument("--content-type", default=None, help="Override content_type (default: from script_segments)")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists")
    args = ap.parse_args()

    path = Path(args.script_segments)
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1
    script_segments = json.loads(path.read_text(encoding="utf-8"))
    content_type = args.content_type or script_segments.get("content_type", "therapeutic")

    out_path = Path(args.out)
    if should_skip_output(out_path, ["plan_id", "shots", "config_hash"], args.force, config_snapshot_hash()):
        print(f"Skip (output exists, use --force to overwrite): {out_path}")
        return 0
    plan = run_shot_planner(script_segments, content_type)
    write_atomically(out_path, plan)
    print(f"Wrote ShotPlan with {len(plan['shots'])} shots to {out_path} (config_hash={plan['config_hash']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
