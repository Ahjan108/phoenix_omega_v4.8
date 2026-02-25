"""
Series Diversity Validator (P0).

Hard-fail: adjacent installments cannot share (primary_mechanism_id + journey_shape_id);
           adjacent installments cannot share band_curve_id.
Soft-warn: repeated combo (book_structure_id, journey_shape_id, motif_id, reframe_profile_id)
           density above threshold in series.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_RULES = REPO_ROOT / "config" / "catalog_planning" / "series_quality_rules.yaml"


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_plan(plan_path: Path) -> Optional[dict]:
    if not plan_path.exists():
        return None
    try:
        return json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _get_plan_series_key(plan: dict) -> tuple[Optional[str], int]:
    """Return (series_id, installment_number). Non-series plans return (None, 0)."""
    sid = plan.get("series_id")
    if not sid:
        return (None, 0)
    inst = plan.get("installment_number")
    if inst is None:
        inst = 0
    return (sid, int(inst))


def _combo_key(plan: dict) -> str:
    bs = plan.get("book_structure_id") or ""
    js = plan.get("journey_shape_id") or ""
    mot = plan.get("motif_id") or ""
    ref = plan.get("reframe_profile_id") or ""
    return f"{bs}|{js}|{mot}|{ref}"


def validate_series_diversity(
    plans_dir: Path,
    rules_path: Optional[Path] = None,
) -> tuple[list[dict], list[dict]]:
    """
    Validate all plans in plans_dir that share a series_id. Return (hard_violations, soft_warnings).
    Plans are grouped by series_id and sorted by installment_number.
    """
    rules_path = rules_path or CONFIG_RULES
    rules = _load_yaml(rules_path)
    hard_adj_mech_journey = rules.get("hard_rules", {}).get("adjacent_mech_journey_unique", True)
    hard_adj_band_curve = rules.get("hard_rules", {}).get("adjacent_band_curve_unique", True)
    max_combo_share = float(rules.get("soft_rules", {}).get("max_combo_share_warn", 0.40))

    plan_files = sorted([p for p in plans_dir.glob("*.json") if p.is_file() and "spec" not in p.name.lower()])
    plans_with_meta: list[tuple[Path, dict]] = []
    for p in plan_files:
        data = _load_plan(p)
        if not data:
            continue
        sid, inst = _get_plan_series_key(data)
        if sid is None:
            continue
        plans_with_meta.append((p, data))

    # Group by series_id
    by_series: dict[str, list[tuple[Path, dict]]] = {}
    for path, plan in plans_with_meta:
        sid = plan.get("series_id") or ""
        if sid not in by_series:
            by_series[sid] = []
        by_series[sid].append((path, plan))

    hard_violations: list[dict] = []
    soft_warnings: list[dict] = []

    for series_id, group in by_series.items():
        # Sort by installment_number
        group.sort(key=lambda x: (x[1].get("installment_number") or 0))
        ordered = [p[1] for p in group]
        paths = [p[0] for p in group]

        # Hard: adjacent (primary_mechanism_id + journey_shape_id) unique
        if hard_adj_mech_journey:
            for i in range(len(ordered) - 1):
                a, b = ordered[i], ordered[i + 1]
                mech_a = a.get("primary_mechanism_id") or ""
                mech_b = b.get("primary_mechanism_id") or ""
                jour_a = a.get("journey_shape_id") or ""
                jour_b = b.get("journey_shape_id") or ""
                if mech_a and jour_a and mech_a == mech_b and jour_a == jour_b:
                    hard_violations.append({
                        "rule": "adjacent_mech_journey_unique",
                        "series_id": series_id,
                        "installment_pair": (ordered[i].get("installment_number"), ordered[i + 1].get("installment_number")),
                        "plan_paths": [str(paths[i]), str(paths[i + 1])],
                        "primary_mechanism_id": mech_a,
                        "journey_shape_id": jour_a,
                    })

        # Hard: adjacent band_curve_id unique
        if hard_adj_band_curve:
            for i in range(len(ordered) - 1):
                a, b = ordered[i], ordered[i + 1]
                bc_a = a.get("band_curve_id") or ""
                bc_b = b.get("band_curve_id") or ""
                if bc_a and bc_a == bc_b:
                    hard_violations.append({
                        "rule": "adjacent_band_curve_unique",
                        "series_id": series_id,
                        "installment_pair": (ordered[i].get("installment_number"), ordered[i + 1].get("installment_number")),
                        "plan_paths": [str(paths[i]), str(paths[i + 1])],
                        "band_curve_id": bc_a,
                    })

        # Soft: combo density
        combo_counts: Counter[str] = Counter()
        for plan in ordered:
            combo_counts[_combo_key(plan)] += 1
        n = len(ordered)
        for combo, count in combo_counts.items():
            if n > 0 and (count / n) > max_combo_share:
                soft_warnings.append({
                    "rule": "max_combo_share_warn",
                    "series_id": series_id,
                    "combo_share": round(count / n, 2),
                    "threshold": max_combo_share,
                    "count": count,
                    "series_size": n,
                })
                break

    return (hard_violations, soft_warnings)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Validate series diversity (P0 hard + soft)")
    ap.add_argument("--plans-dir", type=Path, required=True, help="Directory of compiled plan JSONs")
    ap.add_argument("--rules", type=Path, default=None, help="series_quality_rules.yaml path")
    args = ap.parse_args()

    hard, soft = validate_series_diversity(args.plans_dir, args.rules)
    if hard:
        print("VALIDATE_SERIES_DIVERSITY: FAIL (hard violations)")
        for v in hard:
            print(f"  {v}")
        return 1
    if soft:
        print("VALIDATE_SERIES_DIVERSITY: PASS (soft warnings)")
        for w in soft:
            print(f"  WARN: {w}")
        return 0
    print("VALIDATE_SERIES_DIVERSITY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
