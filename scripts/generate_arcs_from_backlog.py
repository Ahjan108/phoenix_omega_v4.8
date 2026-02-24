#!/usr/bin/env python3
"""
Generate missing arc YAMLs for (persona, topic, engine, format) tuples.
Driven by topic_engine_bindings.yaml and a persona list (unified scope).
Single canonical format (e.g. F006) for coverage run.
Content coverage unblock sequence Step 2.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        raise SystemExit("Required: pip install pyyaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate missing arcs for bound persona×topic×engine tuples (single format)."
    )
    ap.add_argument(
        "--bindings",
        type=Path,
        default=REPO_ROOT / "config" / "topic_engine_bindings.yaml",
        help="topic_engine_bindings.yaml path",
    )
    ap.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Optional: backlog CSV; if set, only generate for NO_ARC rows (persona,topic,engine). Otherwise derive from bindings + personas.",
    )
    ap.add_argument(
        "--format-id",
        default="F006",
        help="Canonical format for this coverage run (default F006)",
    )
    ap.add_argument(
        "--chapter-count",
        type=int,
        default=20,
        help="Chapter count for generated arcs (default 20)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print tuples that would be generated, do not write",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate even if arc file already exists",
    )
    ap.add_argument(
        "--personas",
        nargs="*",
        default=None,
        help="Persona IDs (default: 10 unified from unified_personas.md Part 1)",
    )
    args = ap.parse_args()

    # 10 canonical production personas per unified_personas.md Part 1
    default_personas = [
        "millennial_women_professionals",
        "tech_finance_burnout",
        "entrepreneurs",
        "working_parents",
        "gen_x_sandwich",
        "corporate_managers",
        "gen_z_professionals",
        "healthcare_rns",
        "gen_alpha_students",
        "first_responders",
    ]
    personas = args.personas if args.personas else default_personas

    bindings = load_yaml(args.bindings)
    if not bindings:
        print("No bindings loaded.", file=sys.stderr)
        return 1

    # Topics = top-level keys with allowed_engines
    topics = {
        k for k in bindings
        if isinstance(bindings.get(k), dict) and "allowed_engines" in bindings[k]
    }

    arcs_dir = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
    format_id = args.format_id
    chapter_count = args.chapter_count
    arc_generator = REPO_ROOT / "tools" / "arc_generator.py"
    template = "standard_escalation"

    to_generate: list[tuple[str, str, str]] = []

    if args.csv and args.csv.exists():
        with open(args.csv, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                status = (row.get("status") or "").strip()
                if status != "NO_ARC":
                    continue
                persona = (row.get("persona") or "").strip()
                topic = (row.get("topic") or "").strip()
                engine = (row.get("engine") or "").strip()
                if not (persona and topic and engine):
                    continue
                out_path = arcs_dir / f"{persona}__{topic}__{engine}__{format_id}.yaml"
                if args.overwrite or not out_path.exists():
                    to_generate.append((persona, topic, engine))
    else:
        for persona in personas:
            for topic in topics:
                engines = bindings[topic].get("allowed_engines") or []
                for engine in engines:
                    out_path = arcs_dir / f"{persona}__{topic}__{engine}__{format_id}.yaml"
                    if args.overwrite or not out_path.exists():
                        to_generate.append((persona, topic, engine))

    if not to_generate:
        print("No missing arcs to generate.")
        return 0

    print(f"Missing arcs for format {format_id}: {len(to_generate)}")
    if args.dry_run:
        for p, t, e in to_generate[:20]:
            print(f"  {p} __ {t} __ {e} __ {format_id}")
        if len(to_generate) > 20:
            print(f"  ... and {len(to_generate) - 20} more")
        return 0

    failed = 0
    for i, (persona, topic, engine) in enumerate(to_generate):
        out_path = arcs_dir / f"{persona}__{topic}__{engine}__{format_id}.yaml"
        cmd = [
            sys.executable,
            str(arc_generator),
            "--template",
            template,
            "--persona",
            persona,
            "--topic",
            topic,
            "--engine",
            engine,
            "--format",
            format_id,
            "--chapter-count",
            str(chapter_count),
            "--out",
            str(out_path),
        ]
        rc = subprocess.call(cmd, cwd=REPO_ROOT)
        if rc != 0:
            failed += 1
            print(f"Failed: {' '.join(cmd)}", file=sys.stderr)
        elif (i + 1) % 50 == 0:
            print(f"Generated {i + 1}/{len(to_generate)}...")
    print(f"Done. Generated {len(to_generate) - failed}, failed {failed}.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
