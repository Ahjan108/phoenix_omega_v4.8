#!/usr/bin/env python3
"""
Operations board — append rows from evidence_log + elevated_failures into a single feed.
Feed links: signal_id / issue → suggested_fix → pr_url → merged → impact.
See docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md and plan: Autonomous Improvement Loop.
Usage:
  python scripts/observability/write_operations_board.py
  python scripts/observability/write_operations_board.py --out artifacts/observability/operations_board.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(REPO_ROOT)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def evidence_to_board_row(row: dict, status: str = "detected") -> dict:
    """Convert evidence_log or elevated_failures row to operations board row."""
    out = {
        "timestamp": row.get("timestamp"),
        "signal_id": row.get("signal_id"),
        "category": row.get("category"),
        "status": status,
        "artifact_path": row.get("snapshot_path"),
        "run_url": row.get("run_url"),
    }
    if row.get("message"):
        out["suggested_fix"] = row["message"]
    # elevated_failures may have suggested_fix from systems test
    if row.get("suggested_fix"):
        out["suggested_fix"] = row["suggested_fix"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Write operations board feed from evidence + elevated failures")
    ap.add_argument(
        "--out",
        default=None,
        help="Output path (default: artifacts/observability/operations_board.jsonl)",
    )
    ap.add_argument(
        "--max-rows",
        type=int,
        default=500,
        help="Max rows to keep in feed (default 500)",
    )
    args = ap.parse_args()

    artifacts = REPO_ROOT / "artifacts" / "observability"
    evidence_log = artifacts / "evidence_log.jsonl"
    elevated_log = artifacts / "elevated_failures.jsonl"
    out_path = Path(args.out) if args.out else artifacts / "operations_board.jsonl"
    out_path = out_path if out_path.is_absolute() else REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing board rows (so we can merge / dedupe by issue if we add that later)
    existing = load_jsonl(out_path)

    # New rows from evidence (pass → impact_recorded for recent successes; we keep it simple: append failures as detected)
    new_rows: list[dict] = []
    for row in load_jsonl(elevated_log):
        board_row = evidence_to_board_row(row, status="detected")
        # Avoid duplicate signal_id+timestamp
        key = (board_row.get("signal_id"), board_row.get("timestamp"))
        if not any(
            (r.get("signal_id"), r.get("timestamp")) == key for r in existing + new_rows
        ):
            new_rows.append(board_row)
    for row in load_jsonl(evidence_log):
        if row.get("status") == "pass":
            board_row = evidence_to_board_row(row, status="impact_recorded")
            board_row["impact"] = "pass"
            key = (board_row.get("signal_id"), board_row.get("timestamp"))
            if not any(
                (r.get("signal_id"), r.get("timestamp")) == key for r in existing + new_rows
            ):
                new_rows.append(board_row)

    combined = existing + new_rows
    # Keep last max_rows, most recent first (assume timestamp order)
    combined.sort(key=lambda r: (r.get("timestamp") or ""), reverse=True)
    combined = combined[: args.max_rows]

    with out_path.open("w", encoding="utf-8") as f:
        for r in combined:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Operations board: {out_path} ({len(combined)} rows)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
