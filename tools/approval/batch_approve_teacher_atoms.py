#!/usr/bin/env python3
"""
Batch approval for teacher candidate atoms: list candidates (optional filter), optionally validate, then approve/skip per atom.
Usage:
  python -m tools.approval.batch_approve_teacher_atoms --teacher ahjan [--slot STORY] [--persona X] [--topic Y] [--yes-all]
  --yes-all: approve all without prompting (use with caution).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.approval.approve_atoms import approve_atom, list_candidates


def _load_atom(path: Path) -> dict | None:
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return None


def _quick_validate(data: dict) -> list[str]:
    """Return list of validation errors; empty if OK."""
    errs = []
    if not data.get("atom_id") and not data.get("id"):
        errs.append("missing atom_id or id")
    if "body" not in data and "content" not in data:
        if not any(k in data for k in ("intro", "guided_practice")):
            errs.append("missing body/content or exercise sections")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch approve teacher candidate atoms")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("--slot", default=None, help="Filter by slot type (STORY, EXERCISE, etc.)")
    ap.add_argument("--persona", default=None, help="Filter by metadata.persona (if present)")
    ap.add_argument("--topic", default=None, help="Filter by metadata.topic (if present)")
    ap.add_argument("--yes-all", action="store_true", help="Approve all listed without prompting")
    ap.add_argument("--dry-run", action="store_true", help="List only; do not approve")
    args = ap.parse_args()

    pairs = list_candidates(args.teacher)
    if not pairs:
        print("No candidate atoms.")
        return 0

    # Filter by slot
    if args.slot:
        pairs = [(aid, p) for aid, p in pairs if p.parent.name == args.slot]
    if args.persona or args.topic:
        filtered = []
        for aid, p in pairs:
            data = _load_atom(p)
            if not data:
                continue
            meta = data.get("metadata") or {}
            if args.persona and meta.get("persona") != args.persona:
                continue
            if args.topic and meta.get("topic") != args.topic:
                continue
            filtered.append((aid, p))
        pairs = filtered

    if not pairs:
        print("No candidates match filters.")
        return 0

    print(f"Found {len(pairs)} candidate(s).")
    if args.dry_run:
        for aid, _ in pairs:
            print(" ", aid)
        return 0

    approved_count = 0
    for aid, path in pairs:
        if args.yes_all:
            ok, msg = approve_atom(args.teacher, aid)
            if ok:
                print(msg)
                approved_count += 1
            else:
                print("Skip:", msg, file=sys.stderr)
            continue
        data = _load_atom(path)
        val_errs = _quick_validate(data) if data else ["failed to load"]
        if val_errs:
            print(f"  {aid}: validation: {val_errs}")
        try:
            r = input(f"Approve {aid}? [y/N/q]: ").strip().lower()
        except EOFError:
            break
        if r == "q":
            break
        if r == "y" or r == "yes":
            ok, msg = approve_atom(args.teacher, aid)
            if ok:
                print(" ", msg)
                approved_count += 1
            else:
                print(" ", msg, file=sys.stderr)
    print(f"Approved {approved_count} atom(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
