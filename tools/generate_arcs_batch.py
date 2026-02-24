#!/usr/bin/env python3
"""
Generate concrete arcs from templates for persona×topic×format matrix.
Run with PyYAML installed: pip install pyyaml
Usage: python tools/generate_arcs_batch.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Matrix: (template_id, persona, topic, format_id, chapter_count, engine)
ARC_MATRIX = [
    ("standard_escalation", "nyc_executives", "anxiety", "F006", 8, "overwhelm"),
    ("standard_escalation", "nyc_executives", "depression", "F006", 8, "overwhelm"),
    ("standard_escalation", "educators", "anxiety", "F002", 12, "overwhelm"),
    ("standard_escalation", "educators", "boundaries", "F006", 8, "shame"),
    ("standard_escalation", "gen_z_professionals", "financial_stress", "F002", 30, "overwhelm"),
    ("slow_burn", "nyc_executives", "grief", "F006", 10, "shame"),
    ("slow_burn", "educators", "compassion_fatigue", "F006", 10, "overwhelm"),
    ("wave_cycle", "nyc_executives", "courage", "F002", 12, "overwhelm"),
    ("wave_cycle", "educators", "self_worth", "F006", 8, "shame"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print commands only")
    args = ap.parse_args()
    try:
        from tools.arc_generator import generate_arc
    except ImportError:
        print("Run from repo root with: python tools/generate_arcs_batch.py", file=sys.stderr)
        return 1
    templates_dir = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "templates"
    out_root = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
    for template_id, persona, topic, format_id, chapter_count, engine in ARC_MATRIX:
        template_path = templates_dir / f"{template_id}.yaml"
        if not template_path.exists():
            print(f"Skip: template {template_id} not found", file=sys.stderr)
            continue
        out_path = out_root / f"{persona}__{topic}__{engine}__{format_id}.yaml"
        if args.dry_run:
            print(f"Would generate: {out_path}")
            continue
        try:
            generate_arc(
                template_path,
                persona=persona,
                topic=topic,
                format_id=format_id,
                chapter_count=chapter_count,
                engine=engine,
                out_path=out_path,
            )
            print("Wrote", out_path)
        except Exception as e:
            print(f"ERROR {out_path}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
