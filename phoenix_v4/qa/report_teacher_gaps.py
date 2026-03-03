#!/usr/bin/env python3
"""
Report teacher coverage gaps for a planned book (plan + arc + teacher).
Output: JSON with gaps by role (STORY bands, EXERCISE count) and optional mta_coverage for gap_fill.py input.
Authority: specs/TEACHER_MODE_V4_CANONICAL_SPEC.md §9, TEACHER_AUTHORING_LAYER_SPEC.md §8.2.
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


def _doctrine_dir(teacher_id: str) -> Path:
    return TEACHER_BANKS / teacher_id / "doctrine"


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


def _count_teacher_atoms_by_serves_mta(teacher_id: str) -> tuple[dict[str, int], dict[str, int]]:
    """Count approved STORY and EXERCISE atoms per serves_mta (concept_id). Returns (story_by_mta, exercise_by_mta)."""
    root = _approved_dir(teacher_id)
    story_by_mta: dict[str, int] = defaultdict(int)
    exercise_by_mta: dict[str, int] = defaultdict(int)
    if not root.exists():
        return dict(story_by_mta), dict(exercise_by_mta)
    try:
        import yaml
    except ImportError:
        return dict(story_by_mta), dict(exercise_by_mta)
    for slot, mta_dict in [("STORY", story_by_mta), ("EXERCISE", exercise_by_mta)]:
        slot_dir = root / slot
        if not slot_dir.is_dir():
            continue
        for f in slot_dir.iterdir():
            if f.suffix not in (".yaml", ".yml", ".json"):
                continue
            try:
                data = yaml.safe_load(f.read_text()) or {}
                mta = data.get("serves_mta")
                if mta:
                    if isinstance(mta, list):
                        for c in mta:
                            mta_dict[str(c)] = mta_dict.get(str(c), 0) + 1
                    else:
                        mta_dict[str(mta)] = mta_dict.get(str(mta), 0) + 1
            except Exception:
                continue
    return dict(story_by_mta), dict(exercise_by_mta)


def _load_main_teaching_atoms(teacher_id: str) -> list[dict] | None:
    """Load main_teaching_atoms.yaml; return list of MTA dicts or None if missing."""
    path = _doctrine_dir(teacher_id) / "main_teaching_atoms.yaml"
    if not path.exists():
        return None
    try:
        import yaml
        data = yaml.safe_load(path.read_text()) or {}
        atoms = data.get("main_teaching_atoms")
        return atoms if isinstance(atoms, list) else None
    except Exception:
        return None


def _compute_mta_coverage(
    teacher_id: str,
    plan: dict,
    arc: dict,
    slot_definitions: list,
) -> dict[str, dict[str, int]] | None:
    """
    If arc has chapter_mta_assignments and main_teaching_atoms.yaml exists, compute per-MTA
    required/available/gap for STORY and EXERCISE. Otherwise return None.
    """
    mta_list = _load_main_teaching_atoms(teacher_id)
    chapter_assignments = arc.get("chapter_mta_assignments")
    if not mta_list or not chapter_assignments or not isinstance(chapter_assignments, dict):
        return None
    # Required per MTA: number of chapters assigned that primary_mta
    required_story: dict[str, int] = defaultdict(int)
    required_exercise: dict[str, int] = defaultdict(int)
    for ch_key, assign in chapter_assignments.items():
        if not isinstance(assign, dict):
            continue
        mta = assign.get("primary_mta")
        if not mta:
            continue
        required_story[mta] += 1
        required_exercise[mta] += 1
    story_by_mta, exercise_by_mta = _count_teacher_atoms_by_serves_mta(teacher_id)
    out: dict[str, dict[str, int]] = {}
    for cid in set(required_story) | set(required_exercise) | set(story_by_mta) | set(exercise_by_mta):
        req_s = required_story.get(cid, 0)
        req_e = required_exercise.get(cid, 0)
        have_s = story_by_mta.get(cid, 0)
        have_e = exercise_by_mta.get(cid, 0)
        out[cid] = {
            "required_stories": req_s,
            "available_stories": have_s,
            "gap_stories": max(0, req_s - have_s),
            "required_exercises": req_e,
            "available_exercises": have_e,
            "gap_exercises": max(0, req_e - have_e),
        }
    return out if out else None


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

    report = {
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
    mta_coverage = _compute_mta_coverage(teacher_id, plan, arc, slot_definitions)
    if mta_coverage is not None:
        report["mta_coverage"] = mta_coverage
    return report


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
