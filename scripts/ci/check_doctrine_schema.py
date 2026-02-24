#!/usr/bin/env python3
"""
Gate N: Doctrine schema freeze — validate doctrine.yaml against allowlist only (plan §3.10).
Allowed top-level keys only; required: teacher_id, doctrine_version, tradition, primary_methods, core_principles, tone_profile.
Unknown or missing keys → hard fail in CI.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOCTRINE_SCHEMA_VERSION = 1

ALLOWED_TOP_LEVEL = frozenset({
    "teacher_id", "doctrine_version", "tradition", "primary_methods", "core_principles", "tone_profile",
    "signature_metaphors", "signature_practices", "transformation_model", "forbidden_language", "avoid_claims",
    "fallback_alignment", "constraints", "doctrine_schema_version",
})

REQUIRED_TOP_LEVEL = frozenset({
    "teacher_id", "doctrine_version", "tradition", "primary_methods", "core_principles", "tone_profile",
})

# Nested allowlist: fallback_alignment → only these keys
ALLOWED_FALLBACK_ALIGNMENT = frozenset({"base_tradition", "allowed_sources"})
# constraints → only these keys
ALLOWED_CONSTRAINTS = frozenset({"story_style", "exercise_style", "reflection_style"})


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        return {"__load_error": str(e)}


def validate_doctrine_schema(doctrine_path: Path) -> tuple[bool, list[str]]:
    """Validate doctrine dict. Return (passed, list of error messages)."""
    errors: list[str] = []
    data = _load_yaml(doctrine_path)
    if data.get("__load_error"):
        return False, [f"Load error: {data['__load_error']}"]

    # Top-level: only allowed keys
    for key in data:
        if key not in ALLOWED_TOP_LEVEL:
            errors.append(f"Disallowed top-level key: {key}")

    # Required keys
    for key in REQUIRED_TOP_LEVEL:
        if key not in data or data[key] is None:
            errors.append(f"Missing required key: {key}")

    # Nested allowlist: fallback_alignment
    fa = data.get("fallback_alignment")
    if fa is not None and isinstance(fa, dict):
        for k in fa:
            if k not in ALLOWED_FALLBACK_ALIGNMENT:
                errors.append(f"fallback_alignment: disallowed key: {k}")

    # Nested allowlist: constraints
    constraints = data.get("constraints")
    if constraints is not None and isinstance(constraints, dict):
        for k in constraints:
            if k not in ALLOWED_CONSTRAINTS:
                errors.append(f"constraints: disallowed key: {k}")

    return len(errors) == 0, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Check doctrine.yaml schema (Gate N)")
    ap.add_argument("doctrine", nargs="?", default=None, help="Path to doctrine.yaml (default: SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine.yaml)")
    ap.add_argument("--teacher", default=None, help="Teacher ID (used if doctrine path not given)")
    args = ap.parse_args()
    if args.doctrine:
        path = Path(args.doctrine)
    elif args.teacher:
        path = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / args.teacher / "doctrine" / "doctrine.yaml"
        if not path.exists():
            path = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / args.teacher / "doctrine.yaml"
    else:
        print("Provide doctrine path or --teacher", file=sys.stderr)
        return 1
    if not path.exists():
        print(f"Doctrine file not found: {path}", file=sys.stderr)
        return 1
    passed, errors = validate_doctrine_schema(path)
    if not passed:
        for e in errors:
            print(e, file=sys.stderr)
        print("DOCTRINE SCHEMA: FAIL", file=sys.stderr)
        return 1
    print("DOCTRINE SCHEMA: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
