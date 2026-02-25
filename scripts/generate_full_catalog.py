#!/usr/bin/env python3
"""
Full catalog orchestrator: one command to run the full 24-brand catalog pipeline.

Sequence:
  1. Brand/teacher portfolio allocation (teacher_portfolio_planner)
  2. BookSpec planning per allocation (catalog_planner)
  3. Per-book compile Stage 1→2→3 (run_pipeline)
  4. Wave selection from compiled candidates (wave_orchestrator)

Use --brand and --max-books for "First 10 Books" evaluation (one brand, 10 books, no wave selection).
See docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md and docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md.

Usage:
  python3 scripts/generate_full_catalog.py --max-books 10 --brand stillness_press --skip-wave-selection
  python3 scripts/generate_full_catalog.py --max-books 120 --candidates-dir artifacts/full_catalog/candidates --out-wave artifacts/waves/wave_selected.txt
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
RUN_PIPELINE = REPO_ROOT / "scripts" / "run_pipeline.py"
WAVE_ORCHESTRATOR = REPO_ROOT / "phoenix_v4" / "planning" / "wave_orchestrator.py"


def _resolve_arc_for_book(persona_id: str, topic_id: str) -> Path | None:
    """Return path to an existing master arc for (persona, topic), or None."""
    if not ARCS_ROOT.exists():
        return None
    pattern = f"{persona_id}__{topic_id}__*.yaml"
    matches = sorted(ARCS_ROOT.glob(pattern))
    return matches[0] if matches else None


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Orchestrate full catalog: portfolio → BookSpec → compile → wave selection",
    )
    ap.add_argument(
        "--max-books",
        type=int,
        default=60,
        help="Max books to plan and compile (default 60). Use 10 for First-10 evaluation.",
    )
    ap.add_argument(
        "--brand",
        default=None,
        help="Restrict to one brand (e.g. stillness_press). Omit for all brands.",
    )
    ap.add_argument(
        "--seed",
        default="catalog_seed_001",
        help="Seed for allocation and determinism.",
    )
    ap.add_argument(
        "--candidates-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "full_catalog" / "candidates",
        help="Directory to write compiled plan JSONs (default: artifacts/full_catalog/candidates).",
    )
    ap.add_argument(
        "--skip-wave-selection",
        action="store_true",
        help="Do not run wave_orchestrator (e.g. for First 10 Books evaluation).",
    )
    ap.add_argument(
        "--wave-size",
        type=int,
        default=60,
        help="Target wave size when running wave selection (default 60).",
    )
    ap.add_argument(
        "--out-wave",
        type=Path,
        default=REPO_ROOT / "artifacts" / "waves" / "wave_selected.txt",
        help="Output path for wave selection (one plan path per line).",
    )
    ap.add_argument(
        "--generate-freebies",
        action="store_true",
        help="Generate freebie HTML during compile (default: off for catalog speed).",
    )
    ap.add_argument(
        "--plan-only",
        action="store_true",
        help="Only allocate and produce BookSpecs; do not run compile/assembly or wave selection.",
    )
    args = ap.parse_args()

    # --- Step 1: Teacher portfolio allocation ---
    from phoenix_v4.planning.teacher_portfolio_planner import (
        allocate_wave,
        load_brand_matrix,
    )

    matrix = load_brand_matrix()
    brands = matrix.get("brands") or {}
    all_teachers = []
    for b in brands.values():
        all_teachers.extend(b.get("teachers") or [])
    all_teachers = list(dict.fromkeys(all_teachers))  # preserve order, dedupe

    if not all_teachers:
        print("No teachers found in brand matrix. Check config/catalog_planning/brand_teacher_matrix.yaml.", file=sys.stderr)
        return 1

    wave_id = "full_catalog"
    total_to_allocate = args.max_books
    if args.brand:
        # Allocate extra so we have enough after filtering to one brand
        total_to_allocate = max(args.max_books * 4, 50)
    allocations = allocate_wave(
        wave_id=wave_id,
        teachers=all_teachers,
        total_books=total_to_allocate,
        seed=args.seed,
    )

    if args.brand:
        allocations = [a for a in allocations if a.brand_id == args.brand][: args.max_books]
        if not allocations:
            print(f"No allocations for brand '{args.brand}'.", file=sys.stderr)
            return 1
        print(f"Filtered to brand {args.brand}: {len(allocations)} books.")
    else:
        print(f"Portfolio allocated: {len(allocations)} books across brands.")

    # --- Step 2: BookSpec per allocation ---
    from phoenix_v4.planning.catalog_planner import CatalogPlanner

    planner = CatalogPlanner()
    specs = []
    for i, alloc in enumerate(allocations):
        try:
            spec = planner.produce_single(
                topic_id=alloc.topic_id,
                persona_id=alloc.persona_id,
                teacher_id=alloc.teacher_id,
                brand_id=alloc.brand_id,
                seed=f"{args.seed}:{i}:{alloc.position_in_wave}",
                teacher_mode=(alloc.teacher_id and alloc.teacher_id != "default_teacher"),
            )
            specs.append((alloc, spec))
        except Exception as e:
            print(f"BookSpec failed for {alloc.teacher_id}/{alloc.topic_id}/{alloc.persona_id}: {e}", file=sys.stderr)
            continue

    if not specs:
        print("No BookSpecs produced.", file=sys.stderr)
        return 1

    # Cap to requested max_books (e.g. 108)
    if len(specs) > args.max_books:
        specs = specs[: args.max_books]
    print(f"BookSpecs produced: {len(specs)}.")

    if args.plan_only:
        args.candidates_dir.mkdir(parents=True, exist_ok=True)
        for i, (alloc, spec) in enumerate(specs):
            out_path = args.candidates_dir / f"book_{i:04d}_{spec.topic_id}_{spec.persona_id}.spec.json"
            out_path.write_text(
                json.dumps(spec.to_dict(), indent=2),
                encoding="utf-8",
            )
        print(f"Wrote {len(specs)} BookSpecs to {args.candidates_dir} (plan-only; no assemble).")
        return 0

    # --- Step 3: Compile each book via run_pipeline ---
    args.candidates_dir.mkdir(parents=True, exist_ok=True)
    freebies_flag = "--generate-freebies" if args.generate_freebies else "--no-generate-freebies"

    failed = 0
    for i, (alloc, spec) in enumerate(specs):
        arc_path = _resolve_arc_for_book(spec.persona_id, spec.topic_id)
        if not arc_path or not arc_path.exists():
            print(f"Skip (no arc): {spec.persona_id} / {spec.topic_id}", file=sys.stderr)
            failed += 1
            continue

        out_path = args.candidates_dir / f"book_{i:04d}_{spec.topic_id}_{spec.persona_id}.json"
        cmd = [
            sys.executable,
            str(RUN_PIPELINE),
            "--topic", spec.topic_id,
            "--persona", spec.persona_id,
            "--arc", str(arc_path),
            "--teacher", spec.teacher_id or "default_teacher",
            "--seed", spec.seed,
            "--out", str(out_path),
            freebies_flag,
        ]
        if spec.series_id:
            cmd += ["--series", spec.series_id]
        if spec.installment_number is not None:
            cmd += ["--installment", str(spec.installment_number)]
        if spec.angle_id:
            cmd += ["--angle", spec.angle_id]

        print(f"Compile {i+1}/{len(specs)}: {spec.topic_id} × {spec.persona_id} → {out_path.name}")
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            print(f"  FAILED: {r.stderr or r.stdout or 'non-zero exit'}", file=sys.stderr)
            failed += 1

    compiled_count = len(specs) - failed
    print(f"Compiled: {compiled_count} books ({failed} failed).")

    if args.skip_wave_selection:
        print("Wave selection skipped (--skip-wave-selection).")
        return 0 if failed == 0 else 1

    if compiled_count == 0:
        print("No compiled plans; cannot run wave selection.", file=sys.stderr)
        return 1

    # --- Step 4: Wave selection ---
    out_wave = Path(args.out_wave)
    out_wave.parent.mkdir(parents=True, exist_ok=True)
    cmd_wave = [
        sys.executable,
        str(WAVE_ORCHESTRATOR),
        "--candidates-dir", str(args.candidates_dir),
        "--wave-size", str(min(args.wave_size, compiled_count)),
        "--seed", str(hash(args.seed) % (2**31)),
        "--out", str(out_wave),
    ]
    print("Running wave orchestrator...")
    r = subprocess.run(cmd_wave, cwd=str(REPO_ROOT), timeout=120)
    if r.returncode != 0:
        print("Wave orchestrator failed.", file=sys.stderr)
        return 1
    print(f"Wave written: {out_wave}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
