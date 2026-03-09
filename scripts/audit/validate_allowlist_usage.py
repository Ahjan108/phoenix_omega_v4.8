#!/usr/bin/env python3
"""
Validate migration allowlist: file must exist, parse, and be the single source for drift audit.
CI fails if allowlist is missing, invalid, or if drift audit would use fallback instead.
Exit 0 if valid; exit 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ALLOWLIST_PATH = REPO_ROOT / "config" / "audit" / "qwen_migration_allowlist.yaml"


def main() -> int:
    if not ALLOWLIST_PATH.exists():
        print(f"  FAIL: Allowlist missing: {ALLOWLIST_PATH}", file=sys.stderr)
        return 1

    try:
        import yaml
    except ImportError:
        print("  FAIL: PyYAML required to validate allowlist", file=sys.stderr)
        return 1

    with open(ALLOWLIST_PATH, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"  FAIL: Allowlist invalid YAML: {e}", file=sys.stderr)
            return 1

    if not isinstance(data, dict):
        print("  FAIL: Allowlist must be a YAML object", file=sys.stderr)
        return 1

    expected_keys = ("workflows", "scripts", "config", "docs", "pearl_news_assets")
    for k in expected_keys:
        if k not in data:
            print(f"  FAIL: Allowlist missing key: {k}", file=sys.stderr)
            return 1
        v = data[k]
        if not isinstance(v, list):
            print(f"  FAIL: Allowlist.{k} must be a list", file=sys.stderr)
            return 1

    paths: list[str] = []
    for k in expected_keys:
        for x in data.get(k, []):
            s = str(x).strip()
            if s and not s.startswith("#"):
                paths.append(s)

    if not paths:
        print("  FAIL: Allowlist has no paths (all sections empty)", file=sys.stderr)
        return 1

    # Ensure drift_audit uses allowlist (not fallback)
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.ci.drift_audit import required_paths_from_allowlist  # noqa: E402

    required_list, source = required_paths_from_allowlist()
    if source != "allowlist":
        print(f"  FAIL: Drift audit must use allowlist (got source={source})", file=sys.stderr)
        return 1

    print("  PASS: Allowlist valid and single source for drift audit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
