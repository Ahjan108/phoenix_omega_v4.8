#!/usr/bin/env python3
"""
Check wave solution against the memorable line registry for threshold violations.

Pipeline hook: before export (e.g. Gate #49 / pre_export_check), run:
  PYTHONPATH=. python3 -m phoenix_v4.ops.check_memorable_line_registry --wave artifacts/ops/wave_optimizer/wave_optimizer_solution_2026-W10.json

Exit: 0 pass, 1 fail (blocking), 2 warn (non-blocking).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from phoenix_v4.ops.memorable_line_registry import load_policy

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_WARN = 2


def load_wave_book_ids(wave_path: Path) -> tuple[List[str], str]:
    """Return (list of selected book_ids, wave_id)."""
    if not wave_path.exists():
        return [], ""
    try:
        data = json.loads(wave_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return [], ""
    wave_id = data.get("wave_id", "")
    items = data.get("selected_items") or data.get("selected_candidates")
    if isinstance(items, list):
        return [str(c.get("book_id") or c.get("candidate_id") or "") for c in items if c.get("book_id") or c.get("candidate_id")], wave_id
    ids = data.get("selected") or data.get("selected_candidates") or []
    return [str(i) for i in ids], wave_id


def check_violations(
    snapshot: Dict[str, Any],
    wave_book_ids: List[str],
    policy: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Return list of violations: { line_hash, normalized_text, reason, severity, occurrence_count, max_allowed, scope }.
    severity: blocking | warning. scope: global | per_wave.
    """
    violations: List[Dict[str, Any]] = []
    max_global = int(policy.get("max_occurrences_global", 2))
    max_per_wave = int(policy.get("max_occurrences_per_wave", 1))
    block_on = policy.get("block_on_violation", True)
    strength_tracked = set(policy.get("strength_levels_tracked") or ["good", "great"])
    wave_set = set(wave_book_ids)

    for ent in (snapshot.get("lines") or []):
        h = ent.get("line_hash")
        norm = ent.get("normalized_text", "")
        strength = (ent.get("strength_max") or "ok").lower()
        if strength not in strength_tracked:
            continue
        occ = int(ent.get("occurrence_count", 0))
        books = list(ent.get("books") or [])
        wave_count = sum(1 for b in books if b in wave_set)

        if occ > max_global:
            violations.append({
                "line_hash": h,
                "normalized_text": norm[:80] + ("..." if len(norm) > 80 else ""),
                "reason": f"global occurrence count {occ} exceeds max {max_global}",
                "severity": "blocking" if block_on else "warning",
                "book_id": books[0] if books else "",
                "occurrence_count": occ,
                "max_allowed": max_global,
                "scope": "global",
            })
        if wave_count > max_per_wave:
            violations.append({
                "line_hash": h,
                "normalized_text": norm[:80] + ("..." if len(norm) > 80 else ""),
                "reason": f"wave uses this line in {wave_count} books, max {max_per_wave}",
                "severity": "blocking" if block_on and strength == "great" else "warning",
                "book_id": books[0] if books else "",
                "occurrence_count": wave_count,
                "max_allowed": max_per_wave,
                "scope": "per_wave",
            })

    return violations


def main() -> int:
    ap = argparse.ArgumentParser(description="Check wave against memorable line registry")
    ap.add_argument("--wave", type=Path, required=True, help="Wave optimizer solution JSON")
    ap.add_argument("--snapshot", type=Path, default=None, help="Registry snapshot (default artifacts/ops/memorable_line_registry_snapshot_v1.json)")
    ap.add_argument("--ops-dir", type=Path, default=None, help="Ops dir")
    ap.add_argument("--out", type=Path, default=None, help="Write violations report here")
    ap.add_argument("--policy", type=Path, default=None, help="Policy YAML")
    args = ap.parse_args()

    ops_dir = args.ops_dir or REPO_ROOT / "artifacts" / "ops"
    snapshot_path = args.snapshot or ops_dir / "memorable_line_registry_snapshot_v1.json"
    if not snapshot_path.exists():
        print("No registry snapshot found; skipping check (no violations).", file=sys.stderr)
        return EXIT_PASS

    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading snapshot: {e}", file=sys.stderr)
        return EXIT_FAIL

    wave_book_ids, wave_id = load_wave_book_ids(args.wave)
    if not wave_book_ids:
        print("No selected books in wave; skipping check.", file=sys.stderr)
        return EXIT_PASS

    policy = load_policy(args.policy)
    violations = check_violations(snapshot, wave_book_ids, policy)
    blocking = [v for v in violations if v.get("severity") == "blocking"]
    warning = [v for v in violations if v.get("severity") == "warning"]

    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ"),
        "wave_id": wave_id,
        "status": "fail" if blocking else ("warn" if warning else "pass"),
        "violations": violations,
        "summary": {
            "total_violations": len(violations),
            "blocking_count": len(blocking),
            "warning_count": len(warning),
        },
    }

    out_path = args.out or ops_dir / f"memorable_line_registry_violations_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if blocking:
        print(f"FAIL: {len(blocking)} blocking violation(s). Report: {out_path}", file=sys.stderr)
        for v in blocking[:5]:
            print(f"  - {v.get('reason')} ({v.get('scope')})", file=sys.stderr)
        return EXIT_FAIL
    if warning:
        print(f"WARN: {len(warning)} warning(s). Report: {out_path}", file=sys.stderr)
        return EXIT_WARN
    print(f"PASS: no violations. Report: {out_path}")
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
