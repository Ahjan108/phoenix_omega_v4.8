#!/usr/bin/env python3
"""
Rebuild artifacts/freebies/index.jsonl from a directory of blessed plan JSONs.

DoD: deterministic index source. Use for release waves or after cleaning test pollution.
Output contains only plan rows (release/catalog). One row per book_id (last wins).

Usage:
  python scripts/rebuild_freebie_index_from_plans.py --plans-dir artifacts/waves/my_wave/plans
  python scripts/rebuild_freebie_index_from_plans.py --plans-dir artifacts/systems_test/plans --out artifacts/freebies/index.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INDEX = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"


def main() -> int:
    ap = argparse.ArgumentParser(description="Rebuild freebie index from blessed plan JSONs")
    ap.add_argument("--plans-dir", required=True, help="Directory of compiled plan JSON files")
    ap.add_argument("--out", default=None, help=f"Output JSONL path (default: {DEFAULT_INDEX})")
    args = ap.parse_args()

    pdir = Path(args.plans_dir)
    if not pdir.is_dir():
        print(f"Not a directory: {pdir}", file=sys.stderr)
        return 1

    out_path = Path(args.out) if args.out else DEFAULT_INDEX
    rows: list[dict] = []
    for f in sorted(pdir.iterdir()):
        if f.suffix != ".json":
            continue
        try:
            with open(f, encoding="utf-8") as fp:
                plan = json.load(fp)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Skip {f.name}: {e}", file=sys.stderr)
            continue
        book_id = plan.get("plan_id") or plan.get("plan_hash") or f.stem
        freebie_bundle = plan.get("freebie_bundle") or []
        cta_template_id = plan.get("cta_template_id") or ""
        freebie_slug = plan.get("freebie_slug") or plan.get("slug") or ""
        row = {
            "book_id": book_id,
            "freebie_bundle": freebie_bundle,
            "cta_template_id": cta_template_id,
            "slug": freebie_slug,
            "freebie_slug": freebie_slug,
        }
        for key in ("brand_id", "release_week", "release_week_id", "book_structure_id", "journey_shape_id", "motif_id", "section_reorder_mode", "reframe_profile_id", "variation_signature", "chapter_archetypes"):
            if plan.get(key) is not None:
                row[key] = plan[key]
        rows.append(row)

    # Dedupe by book_id (last wins), preserving order
    seen: dict[str, dict] = {}
    for r in rows:
        bid = str(r.get("book_id") or "")
        seen[bid] = r
    ordered = list(seen.values())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in ordered:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(ordered)} plan row(s) to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
