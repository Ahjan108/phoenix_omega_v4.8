#!/usr/bin/env python3
"""
TDEL: Promote approved synthetic atoms from staging to approved_atoms (plan §3.9).
Requires approval_manifest.json (approved atom_ids, approved_by, approved_at). Only manifest-listed atoms are moved.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote approved synthetic atoms to approved_atoms")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("--staging-dir", default="approved_staging", help="Staging dir under synthetic_atoms")
    ap.add_argument("--manifest", required=True, help="Path to approval_manifest.json")
    ap.add_argument("--approved-dir", default="approved_atoms", help="Target dir under teacher_banks/<id>")
    args = ap.parse_args()
    teacher_id = args.teacher
    banks_root = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id
    staging = banks_root / "synthetic_atoms" / args.staging_dir
    manifest_path = Path(args.manifest)
    approved_root = banks_root / args.approved_dir
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    approved_ids = set(manifest.get("approved_atom_ids") or manifest.get("approved_ids") or [])
    if not approved_ids:
        print("No approved_atom_ids in manifest.", file=sys.stderr)
        return 1
    promoted = 0
    for slot_dir in staging.iterdir():
        if not slot_dir.is_dir():
            continue
        slot_type = slot_dir.name
        target_dir = approved_root / slot_type
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in slot_dir.iterdir():
            if f.suffix not in (".yaml", ".yml", ".json"):
                continue
            atom_id = f.stem
            if atom_id in approved_ids or f.name in approved_ids:
                dest = target_dir / f.name
                shutil.copy2(f, dest)
                promoted += 1
    print(f"Promoted {promoted} atoms to {approved_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
