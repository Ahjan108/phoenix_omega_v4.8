#!/usr/bin/env python3
"""
Ops smoke: brand_id -> church.short_name resolution across all church brands.
Run before payouts/storefront ops to verify church YAMLs load and display names resolve.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    from phoenix_v4.ops.church_loader import CHURCH_BRAND_MAP, get_church_display_name

    errors: list[str] = []
    for brand_id in sorted(CHURCH_BRAND_MAP.keys()):
        try:
            name = get_church_display_name(brand_id)
            print(f"{brand_id} -> {name}")
        except Exception as e:
            errors.append(f"{brand_id}: {e}")
            print(f"{brand_id} -> FAIL: {e}", file=sys.stderr)

    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
