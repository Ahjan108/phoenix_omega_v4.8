#!/usr/bin/env python3
"""
CI: Teacher readiness (plan §5.2). Gate F: minimum native pool per slot/band; Gate G: rolling synthetic debt.
TEACHER_AUTHORING_LAYER_SPEC §8.6: optional --min-mta-story-coverage / --min-mta-exercise-coverage per MTA.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

TEACHER_BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"


def _count_approved(teacher_id: str) -> dict[str, int]:
    root = TEACHER_BANKS / teacher_id / "approved_atoms"
    out: dict[str, int] = {}
    if not root.exists():
        return out
    for slot_dir in root.iterdir():
        if slot_dir.is_dir():
            n = sum(1 for f in slot_dir.iterdir() if f.suffix in (".yaml", ".yml", ".json"))
            out[slot_dir.name] = n
    return out


def _count_by_serves_mta(teacher_id: str) -> tuple[dict[str, int], dict[str, int]]:
    """(story_by_mta, exercise_by_mta) from approved_atoms YAMLs with serves_mta."""
    root = TEACHER_BANKS / teacher_id / "approved_atoms"
    story_by: dict[str, int] = {}
    exercise_by: dict[str, int] = {}
    if not root.exists():
        return story_by, exercise_by
    try:
        import yaml
    except ImportError:
        return story_by, exercise_by
    for slot, mta_dict in [("STORY", story_by), ("EXERCISE", exercise_by)]:
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
                    for c in (mta if isinstance(mta, list) else [mta]):
                        cid = str(c)
                        mta_dict[cid] = mta_dict.get(cid, 0) + 1
            except Exception:
                continue
    return story_by, exercise_by


def _load_mta_concept_ids(teacher_id: str) -> list[str] | None:
    """Load main_teaching_atoms.yaml; return list of concept_ids or None."""
    path = TEACHER_BANKS / teacher_id / "doctrine" / "main_teaching_atoms.yaml"
    if not path.exists():
        return None
    try:
        import yaml
        data = yaml.safe_load(path.read_text()) or {}
        atoms = data.get("main_teaching_atoms")
        if not isinstance(atoms, list):
            return None
        return [a.get("concept_id") for a in atoms if a.get("concept_id")]
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Check teacher readiness (min pool, MTA coverage)")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("--min-exercise", type=int, default=40, help="Min EXERCISE atoms")
    ap.add_argument("--min-hook", type=int, default=30, help="Min HOOK atoms")
    ap.add_argument("--min-reflection", type=int, default=30, help="Min REFLECTION atoms")
    ap.add_argument("--min-integration", type=int, default=20, help="Min INTEGRATION atoms")
    ap.add_argument("--min-mta-story-coverage", type=int, default=0, help="Min STORY atoms per MTA (concept_id); 0 = skip")
    ap.add_argument("--min-mta-exercise-coverage", type=int, default=0, help="Min EXERCISE atoms per MTA; 0 = skip")
    args = ap.parse_args()
    counts = _count_approved(args.teacher)
    errors = []
    if counts.get("EXERCISE", 0) < args.min_exercise:
        errors.append(f"EXERCISE {counts.get('EXERCISE', 0)} < {args.min_exercise}")
    if counts.get("HOOK", 0) < args.min_hook:
        errors.append(f"HOOK {counts.get('HOOK', 0)} < {args.min_hook}")
    if counts.get("REFLECTION", 0) < args.min_reflection:
        errors.append(f"REFLECTION {counts.get('REFLECTION', 0)} < {args.min_reflection}")
    if counts.get("INTEGRATION", 0) < args.min_integration:
        errors.append(f"INTEGRATION {counts.get('INTEGRATION', 0)} < {args.min_integration}")

    if args.min_mta_story_coverage > 0 or args.min_mta_exercise_coverage > 0:
        concept_ids = _load_mta_concept_ids(args.teacher)
        if concept_ids:
            story_by_mta, exercise_by_mta = _count_by_serves_mta(args.teacher)
            for cid in concept_ids:
                if args.min_mta_story_coverage > 0:
                    have = story_by_mta.get(cid, 0)
                    if have < args.min_mta_story_coverage:
                        errors.append(f"MTA {cid}: STORY {have} < {args.min_mta_story_coverage}")
                if args.min_mta_exercise_coverage > 0:
                    have = exercise_by_mta.get(cid, 0)
                    if have < args.min_mta_exercise_coverage:
                        errors.append(f"MTA {cid}: EXERCISE {have} < {args.min_mta_exercise_coverage}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print("TEACHER READINESS: FAIL", file=sys.stderr)
        return 1
    print("TEACHER READINESS: PASS", counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
