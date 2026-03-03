#!/usr/bin/env python3
"""
Pre-export check: run Gate #49 (locale/territory consistency) before platform export.
Call this in the distribution/upload pipeline before exporting to storefronts.
Authority: PLANNING_STATUS.md, SYSTEMS_V4.md — Gate #49 in distribution pipeline.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate #49: locale/territory consistency before export")
    ap.add_argument("--plan", required=True, help="Compiled plan JSON (must include locale, territory)")
    args = ap.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"Plan not found: {plan_path}", file=sys.stderr)
        return 1

    plan = json.loads(plan_path.read_text())
    locale = plan.get("locale", "en-US")
    territory = plan.get("territory", "US")
    book_spec = SimpleNamespace(locale=locale, territory=territory)

    from phoenix_v4.qa.locale_territory_gate import gate_49_locale_territory_consistency
    passed, msg = gate_49_locale_territory_consistency(book_spec)
    if not passed:
        print(f"GATE #49 FAIL: {msg}", file=sys.stderr)
        return 1
    print("GATE #49 PASS: locale/territory consistent for distribution")
    return 0


if __name__ == "__main__":
    sys.exit(main())
