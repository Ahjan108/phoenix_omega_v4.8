#!/usr/bin/env python3
"""
Render a compiled plan JSON to a single .txt file for QA.
Uses Stage 6 prose resolution and TxtWriter (phoenix_v4.rendering).
Resolves all slot types from atoms/, compression_atoms, teacher_banks; placeholders written as
[Placeholder: TYPE] or script exits 1 when plan contains placeholders unless --allow-placeholders.
Usage: python scripts/render_plan_to_txt.py artifacts/book_001.plan.json -o artifacts/books_qa/book_001.txt [--allow-placeholders]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="Render plan JSON to book .txt for QA (Stage 6)")
    ap.add_argument("plan", help="Path to plan JSON (e.g. artifacts/book_001.plan.json)")
    ap.add_argument("-o", "--out", required=True, help="Output .txt path")
    ap.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="If set, output [Placeholder: TYPE] / [Silence: TYPE] for unresolved slots. Otherwise exit 1 when plan contains placeholders.",
    )
    ap.add_argument(
        "--on-missing",
        choices=("fail", "placeholder"),
        default="fail",
        help="If an atom_id has no prose: fail (exit 1) or emit [Missing: atom_id]. Default: fail.",
    )
    ap.add_argument("--no-title-page", action="store_true", help="Omit title/credits block at top")
    ap.add_argument("--atoms-root", type=Path, default=None, help="Atoms root (default: repo atoms/)")
    args = ap.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"Error: plan not found: {plan_path}", file=sys.stderr)
        return 1

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    atom_ids = plan.get("atom_ids") or []
    chapter_slot_sequence = plan.get("chapter_slot_sequence") or []
    if not chapter_slot_sequence or not atom_ids:
        print("Error: plan missing atom_ids or chapter_slot_sequence", file=sys.stderr)
        return 1

    from phoenix_v4.rendering import resolve_prose_for_plan, RenderOptions, TxtWriter

    render_result = resolve_prose_for_plan(
        plan,
        atoms_root=(Path(args.atoms_root) if args.atoms_root else None),
    )

    if not args.allow_placeholders and render_result.placeholder_or_silence_ids:
        print(
            "Error: Plan contains placeholders; resolve upstream first. Use --allow-placeholders for QA output.",
            file=sys.stderr,
        )
        return 1
    if args.on_missing == "fail" and render_result.missing_ids:
        print(
            "Error: Missing prose for atom_ids: "
            + ", ".join(render_result.missing_ids[:5])
            + (f" ... and {len(render_result.missing_ids) - 5} more" if len(render_result.missing_ids) > 5 else ""),
            file=sys.stderr,
        )
        return 1

    options = RenderOptions(
        allow_placeholders=args.allow_placeholders,
        on_missing=args.on_missing,
        title_page=not args.no_title_page,
        include_slot_labels_qa=True,
    )
    writer = TxtWriter(plan, render_result.prose_map, render_result, options)
    out_path = Path(args.out)
    writer.write(out_path)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
