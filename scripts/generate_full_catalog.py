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
CONFIG_LOCALIZATION = REPO_ROOT / "config" / "localization"
RUN_PIPELINE = REPO_ROOT / "scripts" / "run_pipeline.py"
WAVE_ORCHESTRATOR = REPO_ROOT / "phoenix_v4" / "planning" / "wave_orchestrator.py"


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _validate_brand_locale_matrix(
    brand_matrix_path: Path,
    extension_path: Path,
    locale_registry_path: Path,
) -> list[str]:
    """Ensure every brand in the matrix has valid locale/territory in extension and registry. Returns list of errors."""
    errors = []
    matrix = _load_yaml(brand_matrix_path)
    extension = _load_yaml(extension_path)
    locale_reg = _load_yaml(locale_registry_path)
    brands_matrix = set((matrix.get("brands") or {}).keys())
    brands_ext = (extension.get("brands") or {})
    locales_valid = set((locale_reg.get("locales") or {}).keys())

    for bid in brands_matrix:
        ext_cfg = brands_ext.get(bid)
        if not ext_cfg:
            errors.append(f"Brand '{bid}' in matrix not found in brand_registry_locale_extension.yaml")
            continue
        loc = ext_cfg.get("locale")
        territory = ext_cfg.get("territory")
        if not loc:
            errors.append(f"Brand '{bid}' has no 'locale' in locale extension")
        elif loc not in locales_valid:
            errors.append(f"Brand '{bid}' locale '{loc}' not in locale_registry.yaml")
        if territory is None or territory == "":
            errors.append(f"Brand '{bid}' has no 'territory' in locale extension")
    return errors


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
    ap.add_argument(
        "--locale-group",
        default=None,
        help="Locale group name from locale_registry.yaml (e.g. chinese_all). Resolves to list of locales; atoms root per book = atoms/<locale>.",
    )
    ap.add_argument(
        "--brand-matrix",
        type=Path,
        default=None,
        help="Path to brand/teacher matrix YAML (default: config/catalog_planning/brand_teacher_matrix.yaml).",
    )
    ap.add_argument(
        "--atoms-root",
        default=None,
        help="Atoms root for single-locale run (e.g. atoms/zh-TW). For --locale-group, derived per book from spec.locale.",
    )
    args = ap.parse_args()

    brand_matrix_path = args.brand_matrix
    if args.locale_group or brand_matrix_path:
        ext_path = CONFIG_LOCALIZATION / "brand_registry_locale_extension.yaml"
        loc_reg_path = CONFIG_LOCALIZATION / "locale_registry.yaml"
        matrix_path_for_val = brand_matrix_path or (REPO_ROOT / "config" / "catalog_planning" / "brand_teacher_matrix.yaml")
        if matrix_path_for_val.exists():
            errs = _validate_brand_locale_matrix(matrix_path_for_val, ext_path, loc_reg_path)
            if errs:
                for e in errs:
                    print(e, file=sys.stderr)
                print("Fix brand_registry_locale_extension and locale_registry so every matrix brand has valid locale/territory.", file=sys.stderr)
                return 1

    # --- Step 1: Teacher portfolio allocation ---
    from phoenix_v4.planning.teacher_portfolio_planner import (
        allocate_wave,
        load_brand_matrix,
    )

    matrix = load_brand_matrix(brand_matrix_path)
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
        brand_matrix_path=brand_matrix_path,
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

    # Diversity guard: max share per topic/persona when using locale-group or custom brand matrix
    if (args.locale_group or brand_matrix_path) and specs:
        guard_path = REPO_ROOT / "config" / "catalog_planning" / "diversity_guards.yaml"
        if guard_path.exists():
            guard_cfg = _load_yaml(guard_path)
            max_topic = guard_cfg.get("max_share_per_topic")
            max_persona = guard_cfg.get("max_share_per_persona")
            fail_on = guard_cfg.get("fail_on_violation", True)
            n = len(specs)
            if n and (max_topic is not None or max_persona is not None):
                from collections import Counter
                topic_ct = Counter(spec.topic_id for _, spec in specs)
                persona_ct = Counter(spec.persona_id for _, spec in specs)
                violations = []
                for tid, c in topic_ct.items():
                    if max_topic is not None and c / n > max_topic:
                        violations.append(f"topic {tid}: {c}/{n} ({100*c/n:.0f}%) > {100*max_topic:.0f}%")
                for pid, c in persona_ct.items():
                    if max_persona is not None and c / n > max_persona:
                        violations.append(f"persona {pid}: {c}/{n} ({100*c/n:.0f}%) > {100*max_persona:.0f}%")
                if violations:
                    for v in violations:
                        print(v, file=sys.stderr)
                    if fail_on:
                        print("Diversity guard failed. Adjust allocation or config/catalog_planning/diversity_guards.yaml", file=sys.stderr)
                        return 1
                    print("Diversity guard warning (fail_on_violation=false).", file=sys.stderr)

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
        atoms_root = None
        if args.locale_group and getattr(spec, "locale", None):
            atoms_root = str(REPO_ROOT / "atoms" / spec.locale)
        elif args.atoms_root:
            atoms_root = args.atoms_root
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
        if atoms_root:
            cmd += ["--atoms-root", atoms_root]
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
