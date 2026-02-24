#!/usr/bin/env python3
"""
Doctrine drift detector (plan §3.11). If doctrine fingerprint changed, doctrine_version must be incremented.
Compares current doctrine.yaml fingerprint to SOURCE_OF_TRUTH/teacher_banks/<id>/reports/doctrine_registry.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    ap = argparse.ArgumentParser(description="Check doctrine drift (fingerprint vs registry)")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    args = ap.parse_args()
    teacher_id = args.teacher
    banks = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id
    doctrine_path = banks / "doctrine" / "doctrine.yaml"
    if not doctrine_path.exists():
        doctrine_path = banks / "doctrine.yaml"
    if not doctrine_path.exists():
        print(f"Doctrine not found for {teacher_id}", file=sys.stderr)
        return 1
    from phoenix_v4.teacher.doctrine_fingerprint import load_doctrine_yaml, fingerprint_doctrine
    data = load_doctrine_yaml(doctrine_path)
    if not data:
        print("Doctrine empty or failed to load", file=sys.stderr)
        return 1
    fp = fingerprint_doctrine(data)
    version = data.get("doctrine_version")
    registry_path = banks / "reports" / "doctrine_registry.json"
    if not registry_path.exists():
        print(f"No registry at {registry_path}; run update_doctrine_registry first or accept.", file=sys.stderr)
        return 0  # no registry = no drift check
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    current_fp = reg.get("current_fingerprint")
    current_ver = reg.get("current_doctrine_version")
    if current_fp is None:
        return 0
    if fp != current_fp:
        if version is None or int(version) <= int(current_ver or 0):
            print("Doctrine changed but doctrine_version not incremented (drift). FAIL.", file=sys.stderr)
            return 1
    if version is not None and current_ver is not None and int(version) > int(current_ver) and fp == current_fp:
        print("doctrine_version bumped but fingerprint identical (no content change). FAIL.", file=sys.stderr)
        return 1
    print("DOCTRINE DRIFT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
