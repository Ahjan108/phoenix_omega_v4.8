#!/usr/bin/env python3
"""
List book and series names and titles for the whole English catalog.

Runs the same allocation + BookSpec production as generate_full_catalog (catalog planner),
then runs the naming engine per BookSpec to get title/subtitle. Outputs series_id, series_name,
book_id, title, subtitle, brand_id, topic_id, persona_id.

English = brands with locale en-US. Use --use-24-brands to allocate across the 24 en-US brands
from brand_archetype_registry.yaml (default: 1008 books total across 24 brands).

Usage:
  python3 scripts/list_english_catalog_titles.py --max-books 1008 --use-24-brands --out artifacts/english_catalog_titles.json
  python3 scripts/list_english_catalog_titles.py --max-books 1008 --use-24-brands --out - --format text
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _load_24_brand_matrix(archetype_path: Path, default_teacher: str = "ahjan") -> tuple[dict, Path | None]:
    """
    Build a brand matrix with 24 brands from brand_archetype_registry.yaml.
    Returns (matrix_dict, path_to_temp_yaml). Caller must unlink temp file when done.
    """
    data = _load_yaml(archetype_path)
    archetypes = data.get("brand_archetypes") or []
    if not archetypes:
        return {}, None
    brands = {}
    for entry in archetypes:
        bid = entry.get("brand_id")
        if bid:
            brands[bid] = {"teachers": [default_teacher]}
    if not brands:
        return {}, None
    matrix = {"brands": brands, "defaults": {"max_books_per_wave": 50, "release_spacing_days": 14}}
    try:
        import yaml
        fd, path = tempfile.mkstemp(suffix=".yaml", prefix="brand_matrix_24_")
        with open(fd, "w", encoding="utf-8") as f:
            yaml.dump(matrix, f, default_flow_style=False, sort_keys=False)
        return matrix, Path(path)
    except Exception:
        return {}, None


def _en_us_brand_ids(extension_path: Path, matrix_brand_ids: list[str]) -> set[str] | None:
    """
    Brand IDs with locale en-US. If extension has no en-US brands listed, return None
    (treat all matrix brands as English). Otherwise return set of en-US brand IDs.
    """
    data = _load_yaml(extension_path)
    brands = data.get("brands") or {}
    out = set()
    for bid, cfg in brands.items():
        loc = (cfg or {}).get("locale")
        if loc == "en-US":
            out.add(bid)
    # Brands in matrix but not in extension = assume en-US (baseline catalog)
    if not out:
        return None
    for bid in matrix_brand_ids:
        if bid not in brands:
            out.add(bid)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="List book and series names/titles for English catalog")
    ap.add_argument("--max-books", type=int, default=1008, help="Max books to plan (default 1008)")
    ap.add_argument("--seed", default="catalog_seed_001", help="Seed for allocation")
    ap.add_argument("--out", default="-", help="Output path (- for stdout)")
    ap.add_argument("--format", choices=("json", "csv", "text"), default="json", help="Output format")
    ap.add_argument("--brand-matrix", type=Path, default=None, help="Brand matrix YAML (default: config)")
    ap.add_argument("--use-24-brands", action="store_true", help="Use 24 en-US brands from brand_archetype_registry.yaml")
    args = ap.parse_args()

    # --- Step 1: Allocation (same as generate_full_catalog) ---
    from phoenix_v4.planning.teacher_portfolio_planner import allocate_wave, load_brand_matrix, TeacherAllocation
    from phoenix_v4.planning.atoms_model_loader import get_allocation_personas_path

    matrix_path = args.brand_matrix
    temp_matrix_path: Path | None = None
    if args.use_24_brands:
        archetype_path = REPO_ROOT / "config" / "catalog_planning" / "brand_archetype_registry.yaml"
        _matrix, temp_matrix_path = _load_24_brand_matrix(archetype_path)
        if temp_matrix_path:
            matrix_path = temp_matrix_path
            print(f"Using 24 brands from brand_archetype_registry.yaml (temp matrix: {temp_matrix_path})", file=sys.stderr)
    if matrix_path is None:
        matrix_path = REPO_ROOT / "config" / "catalog_planning" / "brand_teacher_matrix.yaml"
    matrix = load_brand_matrix(matrix_path)
    brands = matrix.get("brands") or {}
    matrix_brand_ids = list(brands.keys())

    CONFIG_LOCALIZATION = REPO_ROOT / "config" / "localization"
    CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
    CONFIG_TEACHERS = REPO_ROOT / "config" / "teachers"
    extension_path = CONFIG_LOCALIZATION / "brand_registry_locale_extension.yaml"
    en_us_brands = _en_us_brand_ids(extension_path, matrix_brand_ids)
    all_teachers = []
    for b in brands.values():
        all_teachers.extend(b.get("teachers") or [])
    all_teachers = list(dict.fromkeys(all_teachers))

    if not all_teachers:
        print("No teachers in brand matrix.", file=sys.stderr)
        return 1

    # Topic and persona lists (for 24-brand round-robin or for filtering)
    registry = _load_yaml(CONFIG_TEACHERS / "teacher_registry.yaml")
    teachers_reg = registry.get("teachers", {})
    topic_pool = set()
    for t in all_teachers:
        topic_pool.update(teachers_reg.get(t, {}).get("allowed_topics", []))
    topic_list = sorted(topic_pool) or ["self_worth"]
    personas_cfg = _load_yaml(CONFIG_CATALOG / "canonical_personas.yaml")
    persona_list = list(personas_cfg.get("personas") or []) or ["tech_finance_burnout"]
    allocation_path = get_allocation_personas_path()
    if allocation_path and allocation_path.exists():
        data = _load_yaml(allocation_path)
        override = data.get("personas") or data.get("persona_ids") or []
        if isinstance(override, list) and override:
            persona_list = list(override)

    total_to_allocate = min(args.max_books + 200, 5000)  # overallocate then cap
    # When using 24 brands, round-robin by brand so each brand gets ~equal share (1008/24 = 42 per brand)
    if args.use_24_brands and len(matrix_brand_ids) >= 24:
        allocations = []
        for i in range(total_to_allocate):
            allocations.append(
                TeacherAllocation(
                    teacher_id=all_teachers[0],
                    topic_id=topic_list[i % len(topic_list)],
                    persona_id=persona_list[i % len(persona_list)],
                    brand_id=matrix_brand_ids[i % len(matrix_brand_ids)],
                    position_in_wave=i + 1,
                )
            )
    else:
        allocations = allocate_wave(
            wave_id="english_catalog",
            teachers=all_teachers,
            total_books=total_to_allocate,
            seed=args.seed,
            brand_matrix_path=matrix_path,
            personas_override=persona_list if persona_list else None,
        )

    # Filter to English brands only
    if en_us_brands is not None:
        allocations = [a for a in allocations if a.brand_id in en_us_brands]
    allocations = allocations[: args.max_books]

    if not allocations:
        print("No allocations (or none for en-US brands).", file=sys.stderr)
        return 1

    # --- Step 2: BookSpec per allocation (catalog planner) ---
    from phoenix_v4.planning.catalog_planner import CatalogPlanner, AtomsModel
    from phoenix_v4.planning.atoms_model_loader import atoms_model_for_persona

    planner = CatalogPlanner()
    specs: list[tuple[Any, Any]] = []
    for i, alloc in enumerate(allocations):
        try:
            atoms_model = atoms_model_for_persona(alloc.persona_id)
            spec = planner.produce_single(
                topic_id=alloc.topic_id,
                persona_id=alloc.persona_id,
                teacher_id=alloc.teacher_id,
                brand_id=alloc.brand_id,
                seed=f"{args.seed}:{i}:{alloc.position_in_wave}",
                teacher_mode=bool(alloc.teacher_id and alloc.teacher_id != "default_teacher"),
                atoms_model=atoms_model,
            )
            specs.append((alloc, spec))
        except Exception as e:
            print(f"BookSpec failed {alloc.teacher_id}/{alloc.topic_id}/{alloc.persona_id}: {e}", file=sys.stderr)
            continue

    if not specs:
        print("No BookSpecs produced.", file=sys.stderr)
        return 1

    # --- Series names from series_templates ---
    series_templates = _load_yaml(REPO_ROOT / "config" / "catalog_planning" / "series_templates.yaml")
    series_cfg = series_templates.get("series") or {}

    def series_name(series_id: str) -> str:
        s = series_cfg.get(series_id) or {}
        return s.get("description") or series_id.replace("_", " ").title()

    # --- Step 3: Naming engine per BookSpec ---
    from phoenix_v4.naming.cli import run as naming_run

    rows = []
    for alloc, spec in specs:
        try:
            out = naming_run(
                topic_id=spec.topic_id,
                persona_id=spec.persona_id,
                series_id=spec.series_id or "",
                angle_id=spec.angle_id or "",
                brand_id=spec.brand_id,
                domain_id=spec.domain_id or "",
                seed=spec.seed,
                installment_number=spec.installment_number or 1,
                existing_titles_path=None,
                include_trace=False,
            )
            rows.append({
                "series_id": spec.series_id or "",
                "series_name": series_name(spec.series_id or ""),
                "book_id": out.get("book_id") or "",
                "title": out.get("title") or "",
                "subtitle": out.get("subtitle") or "",
                "brand_id": spec.brand_id,
                "topic_id": spec.topic_id,
                "persona_id": spec.persona_id,
            })
        except Exception as e:
            print(f"Naming failed {spec.topic_id}/{spec.persona_id}: {e}", file=sys.stderr)
            rows.append({
                "series_id": spec.series_id or "",
                "series_name": series_name(spec.series_id or ""),
                "book_id": "",
                "title": "",
                "subtitle": "",
                "brand_id": spec.brand_id,
                "topic_id": spec.topic_id,
                "persona_id": spec.persona_id,
            })

    # --- Output ---
    if args.format == "json":
        text = json.dumps(rows, indent=2)
    elif args.format == "csv":
        import csv
        from io import StringIO
        buf = StringIO()
        w = csv.DictWriter(buf, fieldnames=["series_id", "series_name", "book_id", "title", "subtitle", "brand_id", "topic_id", "persona_id"])
        w.writeheader()
        w.writerows(rows)
        text = buf.getvalue()
    else:
        lines = ["series_id\tseries_name\tbook_id\ttitle\tsubtitle\tbrand_id\ttopic_id\tpersona_id"]
        for r in rows:
            lines.append(f"{r['series_id']}\t{r['series_name']}\t{r['book_id']}\t{r['title']}\t{r['subtitle']}\t{r['brand_id']}\t{r['topic_id']}\t{r['persona_id']}")
        text = "\n".join(lines)

    if args.out == "-":
        print(text)
    else:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {len(rows)} rows to {out_path}", file=sys.stderr)

    # Cleanup temp matrix if used
    if temp_matrix_path and temp_matrix_path.exists():
        try:
            temp_matrix_path.unlink()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
