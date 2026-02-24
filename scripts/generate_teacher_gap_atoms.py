#!/usr/bin/env python3
"""
TDEL: Generate synthetic atoms for teacher gaps (plan §3.4, §3.9).
Input: doctrine.yaml, approved atoms, gap report. Output: synthetic_atoms/pending/<slot_type>/*.yaml.
This script is a stub: writes gap report and placeholder structure; actual LLM generation is a separate implementation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate teacher gap atoms (TDEL stub)")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("--gap-report", help="Path to teacher_gap_report.json (optional)")
    ap.add_argument("--out-dir", help="Output dir (default: SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/synthetic_atoms/pending)")
    args = ap.parse_args()
    teacher_id = args.teacher
    banks_root = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id
    out_dir = Path(args.out_dir) if args.out_dir else banks_root / "synthetic_atoms" / "pending"
    out_dir.mkdir(parents=True, exist_ok=True)
    gap_report_path = Path(args.gap_report) if args.gap_report else REPO_ROOT / "artifacts" / "teacher_coverage_report.json"
    if gap_report_path.exists():
        data = json.loads(gap_report_path.read_text(encoding="utf-8"))
        gaps = data.get("gaps") or {}
        for slot_type, slot_gaps in gaps.items():
            if slot_gaps and (isinstance(slot_gaps, dict) and any(v for v in slot_gaps.values())):
                (out_dir / slot_type).mkdir(parents=True, exist_ok=True)
        print(f"Gap report loaded; pending dirs created under {out_dir}. Run LLM generation separately.")
    else:
        print(f"No gap report at {gap_report_path}; create one via coverage gate first.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
