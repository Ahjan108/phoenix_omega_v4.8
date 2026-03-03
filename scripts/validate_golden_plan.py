#!/usr/bin/env python3
"""
Validate a compiled plan JSON against the Stage 3 golden-fixture contract.
Usage: python scripts/validate_golden_plan.py [path/to/plan.json]
       If no path given, checks artifacts/golden_plans/*.plan.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED = ["plan_hash", "chapter_slot_sequence", "atom_ids"]
OPTIONAL = ["dominant_band_sequence", "input_digest", "book_id"]


def validate_plan(data: dict) -> list[str]:
    errors = []
    for k in REQUIRED:
        if k not in data:
            errors.append(f"Missing required key: {k}")
            continue
        v = data[k]
        if k == "plan_hash" and not isinstance(v, str):
            errors.append("plan_hash must be a string")
        elif k == "chapter_slot_sequence" and not isinstance(v, list):
            errors.append("chapter_slot_sequence must be a list")
        elif k == "atom_ids" and not isinstance(v, list):
            errors.append("atom_ids must be a list")
    if "dominant_band_sequence" in data and data["dominant_band_sequence"] is not None:
        if not isinstance(data["dominant_band_sequence"], list):
            errors.append("dominant_band_sequence must be a list or null")
    return errors


def main() -> int:
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        paths = list((REPO_ROOT / "artifacts" / "golden_plans").glob("*.plan.json"))
    if not paths:
        print("No *.plan.json files in artifacts/golden_plans/ (or no path given).")
        print("Usage: python scripts/validate_golden_plan.py [path/to/plan.json]")
        return 0
    failed = 0
    for p in paths:
        if not p.exists():
            print(f"FAIL {p}: file not found")
            failed += 1
            continue
        try:
            data = json.loads(p.read_text())
        except Exception as e:
            print(f"FAIL {p}: {e}")
            failed += 1
            continue
        errs = validate_plan(data)
        if errs:
            print(f"FAIL {p}:")
            for e in errs:
                print(f"  - {e}")
            failed += 1
        else:
            print(f"PASS {p} (plan_hash={data.get('plan_hash', '')[:16]}... len(chapter_slot_sequence)={len(data.get('chapter_slot_sequence', []))} len(atom_ids)={len(data.get('atom_ids', []))})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
