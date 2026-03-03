#!/usr/bin/env python3
"""
CI gate: verify only approved exercises are runtime-visible (registry runtime_source: approved_only)
and that approved/ contains only valid approved exercises.
Usage: python -m tools.ci.check_approved_exercises_status
Exit 0 if OK; 1 if registry wrong or approved/ has invalid entries.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXERCISES_V4 = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4"
REGISTRY = EXERCISES_V4 / "registry.yaml"
APPROVED_DIR = EXERCISES_V4 / "approved"


def main() -> int:
    if not REGISTRY.exists():
        print("OK: no registry (exercises_v4 not present)", file=sys.stderr)
        return 0
    try:
        import yaml
        with open(REGISTRY) as f:
            reg = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"ERROR: Failed to load registry: {e}", file=sys.stderr)
        return 1
    runtime = (reg.get("global_rules") or {}).get("runtime_source", "")
    if runtime != "approved_only":
        print(f"ERROR: registry global_rules.runtime_source must be 'approved_only', got {runtime!r}", file=sys.stderr)
        return 1
    if not APPROVED_DIR.exists():
        print("OK: approved/ missing (no approved exercises yet)", file=sys.stderr)
        return 0
    errors = []
    for path in APPROVED_DIR.rglob("*.yaml"):
        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            status = (data.get("approval") or {}).get("status", "")
            if status != "approved":
                errors.append(f"{path}: approval.status is {status!r}, expected 'approved'")
        except Exception as e:
            errors.append(f"{path}: {e}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    print("OK: only approved exercises in approved/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
