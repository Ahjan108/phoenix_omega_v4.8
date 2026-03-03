#!/usr/bin/env python3
"""
Update the cross-catalog memorable line registry from a book_quality_bundle.

Pipeline hook: run after quality_bundle_builder.py writes the bundle.
  PYTHONPATH=. python3 -m phoenix_v4.ops.update_memorable_line_registry --bundle artifacts/ops/book_quality_bundle_book_001_20260225.json

Appends events to artifacts/ops/memorable_line_registry_v1.jsonl, then writes
artifacts/ops/memorable_line_registry_snapshot_v1.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from phoenix_v4.ops.memorable_line_registry import (
    REPO_ROOT,
    extract_lines_from_bundle,
    normalize_line,
    line_hash,
    load_registry_jsonl,
    append_record,
    build_snapshot,
)

EXIT_PASS = 0
EXIT_FAIL = 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Upsert bundle memorable lines into registry")
    ap.add_argument("--bundle", type=Path, required=True, help="Path to book_quality_bundle_*.json")
    ap.add_argument("--registry", type=Path, default=None, help="JSONL path (default artifacts/ops/memorable_line_registry_v1.jsonl)")
    ap.add_argument("--snapshot", type=Path, default=None, help="Snapshot path (default artifacts/ops/memorable_line_registry_snapshot_v1.json)")
    ap.add_argument("--ops-dir", type=Path, default=None, help="Ops dir (default artifacts/ops)")
    args = ap.parse_args()

    bundle_path = args.bundle
    if not bundle_path.exists():
        print(f"Error: bundle not found: {bundle_path}", file=sys.stderr)
        return EXIT_FAIL

    ops_dir = args.ops_dir or REPO_ROOT / "artifacts" / "ops"
    jsonl_path = args.registry or ops_dir / "memorable_line_registry_v1.jsonl"
    snapshot_path = args.snapshot or ops_dir / "memorable_line_registry_snapshot_v1.json"

    lines = extract_lines_from_bundle(bundle_path)
    appended = 0
    if not lines:
        print("No tracked memorable lines in bundle; nothing to append.")
    else:
        seen_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        for (norm, strength, book_id, brand_id) in lines:
            h = line_hash(norm)
            record = {
                "line_hash": h,
                "normalized_text": norm,
                "book_id": book_id,
                "brand_id": brand_id or "",
                "strength": strength,
                "seen_at": seen_at,
            }
            append_record(jsonl_path, record)
        appended = len(lines)
        index = load_registry_jsonl(jsonl_path)
        snapshot = build_snapshot(index)
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Appended {appended} line(s); snapshot written to {snapshot_path}")
    # Structured signal for callers (e.g. golden path script); do not key off prose.
    print(json.dumps({"appended": appended}))
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
