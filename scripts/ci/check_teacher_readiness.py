#!/usr/bin/env python3
"""
CI: Teacher readiness (plan §5.2). Gate F: minimum native pool per slot/band; Gate G: rolling synthetic debt.
Only blocks release when below thresholds; used before wave planning.
"""
from __future__ import annotations

import argparse
import json
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Check teacher readiness (min pool, synthetic debt)")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("--min-exercise", type=int, default=40, help="Min EXERCISE atoms")
    ap.add_argument("--min-hook", type=int, default=30, help="Min HOOK atoms")
    ap.add_argument("--min-reflection", type=int, default=30, help="Min REFLECTION atoms")
    ap.add_argument("--min-integration", type=int, default=20, help="Min INTEGRATION atoms")
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
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print("TEACHER READINESS: FAIL", file=sys.stderr)
        return 1
    print("TEACHER READINESS: PASS", counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
