#!/usr/bin/env python3
"""
Approval & promotion: move teacher candidate atoms to approved; add approval metadata.
Authority: specs/TEACHER_MODE_V4_CANONICAL_SPEC.md §11.
Usage: approve_atoms.py --teacher <id> list | approve_atoms.py --teacher <id> approve <atom_id>
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEACHER_BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"


def _candidate_dir(teacher_id: str) -> Path:
    return TEACHER_BANKS / teacher_id / "candidate_atoms"


def _approved_dir(teacher_id: str) -> Path:
    return TEACHER_BANKS / teacher_id / "approved_atoms"


def _approval_log_dir(teacher_id: str) -> Path:
    return TEACHER_BANKS / teacher_id / "artifacts" / "approval_logs"


def list_candidates(teacher_id: str) -> list[tuple[str, Path]]:
    """Return list of (atom_id, path) for all candidate atoms."""
    cand = _candidate_dir(teacher_id)
    if not cand.exists():
        return []
    out = []
    for slot_dir in cand.iterdir():
        if not slot_dir.is_dir():
            continue
        for f in slot_dir.iterdir():
            if f.suffix in (".yaml", ".yml", ".json"):
                atom_id = f.stem
                out.append((atom_id, f))
    return sorted(out)


def find_candidate(teacher_id: str, atom_id: str) -> Path | None:
    """Return path to candidate atom file or None."""
    cand = _candidate_dir(teacher_id)
    if not cand.exists():
        return None
    for slot_dir in cand.iterdir():
        if not slot_dir.is_dir():
            continue
        for f in slot_dir.iterdir():
            if f.stem == atom_id:
                return f
    return None


def approve_atom(teacher_id: str, atom_id: str) -> tuple[bool, str]:
    """
    Move candidate atom to approved_atoms; write approval log. Returns (success, message).
    """
    src = find_candidate(teacher_id, atom_id)
    if not src:
        return False, f"Candidate atom not found: {atom_id}"
    approved_root = _approved_dir(teacher_id)
    slot = src.parent.name
    dest_dir = approved_root / slot
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    src.unlink()
    log_dir = _approval_log_dir(teacher_id)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{atom_id}.yaml"
    log_content = {
        "atom_id": atom_id,
        "teacher_id": teacher_id,
        "approved_at": datetime.utcnow().isoformat() + "Z",
        "from_path": str(src),
        "to_path": str(dest),
    }
    try:
        import yaml
        log_file.write_text(yaml.dump(log_content, default_flow_style=False))
    except Exception:
        import json
        log_file.write_text(json.dumps(log_content, indent=2))
    return True, f"Approved {atom_id} -> {dest}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Teacher-scoped approval: list candidates, approve atom (TEACHER_MODE §11)")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("action", choices=["list", "approve"], help="list | approve")
    ap.add_argument("atom_id", nargs="?", default="", help="Atom ID (for approve)")
    args = ap.parse_args()

    if args.action == "list":
        pairs = list_candidates(args.teacher)
        if not pairs:
            print("No candidate atoms.")
            return 0
        for aid, _ in pairs:
            print(aid)
        return 0

    if args.action == "approve":
        if not args.atom_id:
            print("approve requires atom_id", file=sys.stderr)
            return 1
        ok, msg = approve_atom(args.teacher, args.atom_id)
        if not ok:
            print(msg, file=sys.stderr)
            return 1
        print(msg)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
