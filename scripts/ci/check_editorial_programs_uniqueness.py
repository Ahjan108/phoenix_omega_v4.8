#!/usr/bin/env python3
"""
CI check: editorial_programs.yaml uniqueness.
- Strict mode (--strict): unique (brand_id, worldview_id) per program.
- Default: unique (brand_id, worldview_id, metadata_style_family) per program.
Exit 0 if pass, 1 if fail.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="Check editorial_programs uniqueness (strict or triple).")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Require unique (brand_id, worldview_id) per program. Default: unique (brand_id, worldview_id, metadata_style_family).",
    )
    ap.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "config" / "catalog_planning" / "editorial_programs.yaml",
        help="Path to editorial_programs.yaml",
    )
    args = ap.parse_args()

    if not args.config.exists():
        print(f"Config not found: {args.config}", file=sys.stderr)
        return 1

    try:
        import yaml
        cfg = yaml.safe_load(args.config.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"Failed to load config: {e}", file=sys.stderr)
        return 1

    programs = cfg.get("programs") or {}
    if not programs:
        return 0

    seen: set[tuple[str, ...]] = set()
    key_desc = "(brand_id, worldview_id)" if args.strict else "(brand_id, worldview_id, metadata_style_family)"
    for pid, p in programs.items():
        brand = (p.get("brand_id") or "").strip()
        worldview = (p.get("worldview_id") or "").strip()
        family = (p.get("metadata_style_family") or "").strip()
        key = (brand, worldview) if args.strict else (brand, worldview, family)
        if key in seen:
            print(
                f"editorial_programs: duplicate {key_desc} for program {pid}: {key}. Each program must be distinct.",
                file=sys.stderr,
            )
            return 1
        seen.add(key)

    print(f"OK: all programs have unique {key_desc} ({len(programs)} programs).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
