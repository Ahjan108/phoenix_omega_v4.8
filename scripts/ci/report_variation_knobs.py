#!/usr/bin/env python3
"""
Structural Variation V4: report variation_knob_distribution and optional collision slices.
Reads artifacts/freebies/index.jsonl (or --index) and writes artifacts/reports/variation_report.json.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Variation knob distribution and collision report")
    ap.add_argument("--index", default=None, help="JSONL index path (default: artifacts/freebies/index.jsonl)")
    ap.add_argument("--out", default=None, help="Output JSON path (default: artifacts/reports/variation_report.json)")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    index_path = Path(args.index) if args.index else repo / "artifacts" / "freebies" / "index.jsonl"
    out_path = Path(args.out) if args.out else repo / "artifacts" / "reports" / "variation_report.json"

    rows: list[dict] = []
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8").strip().splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Only plan rows (have variation knobs or freebie_bundle)
    plan_rows = [r for r in rows if isinstance(r, dict) and (r.get("variation_signature") is not None or r.get("freebie_bundle") is not None)]

    # variation_knob_distribution
    book_structure_counts = Counter(r.get("book_structure_id") or "" for r in plan_rows)
    journey_shape_counts = Counter(r.get("journey_shape_id") or "" for r in plan_rows)
    motif_counts = Counter(r.get("motif_id") or "" for r in plan_rows)
    reframe_counts = Counter(r.get("reframe_profile_id") or "" for r in plan_rows)
    reorder_counts = Counter(r.get("section_reorder_mode") or "" for r in plan_rows)

    # Top combo share: (book_structure_id, journey_shape_id, motif_id, reframe_profile_id)
    combo_counts: Counter = Counter()
    for r in plan_rows:
        key = (
            r.get("book_structure_id") or "",
            r.get("journey_shape_id") or "",
            r.get("motif_id") or "",
            r.get("reframe_profile_id") or "",
        )
        combo_counts[key] += 1

    total = len(plan_rows)
    variation_knob_distribution = {
        "total_plans": total,
        "book_structure_id": dict(book_structure_counts),
        "journey_shape_id": dict(journey_shape_counts),
        "motif_id": dict(motif_counts),
        "reframe_profile_id": dict(reframe_counts),
        "section_reorder_mode": dict(reorder_counts),
        "top_combos": [{"combo": list(k), "count": c} for k, c in combo_counts.most_common(10)],
    }

    # Placeholders for collision (filled when first-sentence/section data available)
    collision_heatmap_by_section_id: dict = {}
    first_sentence_collision_by_section_type: dict = {}

    report = {
        "variation_knob_distribution": variation_knob_distribution,
        "collision_heatmap_by_section_id": collision_heatmap_by_section_id,
        "first_sentence_collision_by_section_type": first_sentence_collision_by_section_type,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
