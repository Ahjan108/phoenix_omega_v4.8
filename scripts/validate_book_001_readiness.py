#!/usr/bin/env python3
"""
Book_001 readiness validator.
Loads atom pool for persona/topic/engine; checks STORY count and BAND presence/diversity;
optionally slot_definitions vs chapter count.
Exit 0 = pass; non-zero = fail with clear messages.
See docs/BOOK_001_READINESS_CHECKLIST.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.assembly_compiler import (
    ATOMS_ROOT,
    _parse_canonical_txt,
    validate_canonical_atom_file,
)


def validate_emotional_curve(
    dominant_band_sequence: list[int | None],
    chapter_count: int,
) -> list[str]:
    """
    Enforce emotional curve when chapter_count >= 6:
    1. >= 3 distinct BAND values
    2. No more than 3 consecutive chapters with same BAND
    """
    errors: list[str] = []
    if chapter_count < 6:
        return errors

    # Use only non-None bands for diversity; sequence may contain None for chapters without STORY
    bands_in_sequence = [b for b in dominant_band_sequence if b is not None]

    # Rule 1: minimum diversity
    distinct_bands = set(bands_in_sequence)
    if len(distinct_bands) < 3:
        errors.append(
            f"Emotional curve invalid: only {len(distinct_bands)} distinct BAND values found "
            f"(minimum 3 required for books >= 6 chapters)."
        )

    # Rule 2: no more than 3 consecutive same band
    max_run = 1
    current_run = 1
    for i in range(1, len(dominant_band_sequence)):
        curr = dominant_band_sequence[i]
        prev = dominant_band_sequence[i - 1]
        if curr is not None and prev is not None and curr == prev:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1

    if max_run > 3:
        errors.append(
            f"Emotional curve invalid: {max_run} consecutive chapters "
            f"with same BAND detected (maximum allowed is 3)."
        )

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate Book_001 readiness for persona/topic/engine")
    ap.add_argument("--persona", required=True, help="Canonical persona (e.g. nyc_executives)")
    ap.add_argument("--topic", required=True, help="Canonical topic (e.g. self_worth)")
    ap.add_argument("--engine", required=True, help="Engine (e.g. shame)")
    ap.add_argument(
        "--chapter-count",
        type=int,
        default=None,
        help="Required STORY count (≥1 per chapter). If omitted, only checks pool exists and has ≥1 STORY.",
    )
    ap.add_argument(
        "--min-bands",
        type=int,
        default=2,
        help="Require at least this many distinct BAND values if chapter_count >= 3 (default 2)",
    )
    ap.add_argument(
        "--plan",
        type=str,
        default=None,
        help="Path to compiled plan JSON (e.g. artifacts/book_001.plan.json). When set, enforces emotional curve on dominant_band_sequence for books >= 6 chapters.",
    )
    args = ap.parse_args()

    path = ATOMS_ROOT / args.persona / args.topic / args.engine / "CANONICAL.txt"
    errors: list[str] = []

    if not path.exists():
        print(f"FAIL: CANONICAL.txt not found: {path}", file=sys.stderr)
        return 1

    errs = validate_canonical_atom_file(path)
    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    try:
        atoms = _parse_canonical_txt(path)
    except ValueError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    story_count = len(atoms)
    if story_count == 0:
        print("FAIL: No STORY atoms in CANONICAL.txt", file=sys.stderr)
        return 1

    required_stories = args.chapter_count if args.chapter_count is not None else 1
    if story_count < required_stories:
        print(
            f"FAIL: STORY count {story_count} < required {required_stories} (chapter_count)",
            file=sys.stderr,
        )
        return 1

    bands = {a["band"] for a in atoms}
    # Require band diversity only when chapter count is set and >= 3 (emotional curve contract).
    if args.chapter_count is not None and args.chapter_count >= 3 and len(bands) < args.min_bands:
        print(
            f"FAIL: Only {len(bands)} distinct BAND(s) {sorted(bands)}; need ≥ {args.min_bands} for emotional curve (≥3 chapters)",
            file=sys.stderr,
        )
        return 1

    # Optional: duplicate atom IDs (parser produces unique atom_id per block)
    atom_ids = [a["atom_id"] for a in atoms]
    if len(atom_ids) != len(set(atom_ids)):
        print("FAIL: Duplicate atom IDs in CANONICAL.txt", file=sys.stderr)
        return 1

    # Emotional curve enforcement (when compiled plan provided and >= 6 chapters)
    if args.plan:
        plan_path = Path(args.plan)
        if not plan_path.exists():
            print(f"FAIL: Plan file not found: {plan_path}", file=sys.stderr)
            return 1
        try:
            plan_data = json.loads(plan_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"FAIL: Could not load plan: {e}", file=sys.stderr)
            return 1
        dominant_band_sequence = plan_data.get("dominant_band_sequence") or []
        # Normalize None from JSON
        dominant_band_sequence = [b if b is not None else None for b in dominant_band_sequence]
        chapter_count = len(dominant_band_sequence)
        curve_errors = validate_emotional_curve(dominant_band_sequence, chapter_count)
        if curve_errors:
            for err in curve_errors:
                print(f"FAIL: {err}", file=sys.stderr)
            return 1
        print("PASS: Emotional curve (>= 3 distinct bands, no > 3 consecutive same)", file=sys.stderr)

    print(
        f"PASS: {path.name} story_count={story_count} bands={sorted(bands)}"
        + (f" (chapter_count={args.chapter_count})" if args.chapter_count else ""),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
