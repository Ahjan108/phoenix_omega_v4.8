#!/usr/bin/env python3
"""
Report teacher coverage gaps for a planned book (plan + arc + teacher).
Output: JSON with gaps by role (STORY bands, EXERCISE count) for gap_fill.py input.
Authority: specs/TEACHER_MODE_V4_CANONICAL_SPEC.md §9, TEACHER_MODE_AUTHORING_PLAYBOOK.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEACHER_BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"


def _approved_dir(teacher_id: str) -> Path:
    return TEACHER_BANKS / teacher_id / "approved_atoms"


def _count_teacher_atoms_by_slot_and_band(teacher_id: str) -> tuple[dict[str, int], dict[str, dict[str, int]]]:
    """Returns (slot_type -> count, slot_type -> band -> count for STORY)."""
    root = _approved_dir(teacher_id)
    if not root.exists():
        return {}, {}
    slot_totals: dict[str, int] = defaultdict(int)
    story_bands: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for slot_dir in root.iterdir():
        if not slot_dir.is_dir():
            continue
        slot = slot_dir.name
        for f in slot_dir.iterdir():
            if f.suffix not in (".yaml", ".yml", ".json"):
                continue
            slot_totals[slot] += 1
            if slot == "STORY":
                try:
                    import yaml
                    data = yaml.safe_load(f.read_text()) or {}
                    band = data.get("band") or data.get("BAND") or 3
                    story_bands[slot][str(band)] = story_bands[slot].get(str(band), 0) + 1
                except Exception:
                    story_bands[slot]["3"] = story_bands[slot].get("3", 0) + 1
    return dict(slot_totals), {k: dict(v) for k, v in story_bands.items()}


def run_report(plan_path: Path, arc_path: Path, teacher_id: str) -> dict:
    """Compute required vs available; return gaps dict for JSON output."""
    plan = json.loads(plan_path.read_text())
    try:
        import yaml
        arc = yaml.safe_load(arc_path.read_text()) or {}
    except Exception:
        arc = {}
    slot_definitions = plan.get("chapter_slot_sequence") or plan.get("slot_definitions") or []
    if not slot_definitions and plan.get("chapter_count"):
        ch = plan.get("chapter_count")
        slot_definitions = [["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]] * ch
    arc_curve = arc.get("emotional_curve") or arc.get("emotional_temperature_sequence") or []
    if not arc_curve and slot_definitions:
        arc_curve = ["3"] * len(slot_definitions)

    required_story_by_band: dict[str, int] = defaultdict(int)
    required_exercise = 0
    for ch_idx, row in enumerate(slot_definitions):
        if isinstance(row, list):
            for st in row:
                if str(st).upper() == "STORY":
                    band = arc_curve[ch_idx] if ch_idx < len(arc_curve) else "3"
                    required_story_by_band[str(band)] += 1
                elif str(st).upper() == "EXERCISE":
                    required_exercise += 1

    slot_totals, story_bands = _count_teacher_atoms_by_slot_and_band(teacher_id)
    have_story_by_band = story_bands.get("STORY", {})
    have_exercise = slot_totals.get("EXERCISE", 0)

    gaps_story = {}
    for band, need in required_story_by_band.items():
        have = have_story_by_band.get(band, 0)
        if need > have:
            gaps_story[f"band_{band}"] = need - have
    total_story_missing = sum(gaps_story.values())
    if total_story_missing > 0 and not gaps_story:
        gaps_story["total_missing"] = total_story_missing

    gaps_exercise = {}
    if required_exercise > have_exercise:
        gaps_exercise["total_missing"] = required_exercise - have_exercise

    return {
        "teacher_id": teacher_id,
        "topic": plan.get("topic_id") or plan.get("topic", ""),
        "persona": plan.get("persona_id") or plan.get("persona", ""),
        "format_id": plan.get("format_id") or "",
        "arc_id": plan.get("arc_id") or arc.get("arc_id") or "",
        "gaps": {
            "STORY": gaps_story if gaps_story else {"band_3": 0},
            "EXERCISE": gaps_exercise if gaps_exercise else {"total_missing": 0},
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Report teacher gaps for plan+arc (TEACHER_MODE §9)")
    ap.add_argument("--plan", required=True, help="Compiled plan JSON")
    ap.add_argument("--arc", required=True, help="Arc YAML path")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("--out", required=True, help="Output gaps JSON path")
    args = ap.parse_args()
    plan_path = Path(args.plan)
    arc_path = Path(args.arc)
    if not plan_path.exists():
        print(f"Plan not found: {plan_path}", file=sys.stderr)
        return 1
    if not arc_path.exists():
        print(f"Arc not found: {arc_path}", file=sys.stderr)
        return 1
    report = run_report(plan_path, arc_path, args.teacher)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
