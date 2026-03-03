#!/usr/bin/env python3
"""
Series Content Freshness Gate (P1).

Fixed-count rules vs immediate previous installment only:
- min_new_story_atoms_vs_prev (integer): minimum new STORY atom IDs vs previous installment.
- require_distinct_integration_atom_vs_prev (boolean): final INTEGRATION atom must differ from previous.
No full-series cumulative comparisons.
"""
from __future__ import annotations

import json
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


def _story_atom_ids(plan: dict) -> set[str]:
    """Extract all STORY atom IDs from chapter_slot_sequence."""
    out: set[str] = set()
    ch_seq = plan.get("chapter_slot_sequence") or []
    for ch in ch_seq:
        slots = ch.get("slots") or []
        for s in slots:
            if (s.get("slot_type") or "").upper() == "STORY":
                aid = s.get("atom_id")
                if aid:
                    out.add(aid)
    return out


def _final_integration_atom_id(plan: dict) -> Optional[str]:
    """Last INTEGRATION slot atom_id in the plan (last chapter, last INTEGRATION)."""
    ch_seq = plan.get("chapter_slot_sequence") or []
    last_id = None
    for ch in ch_seq:
        slots = ch.get("slots") or []
        for s in slots:
            if (s.get("slot_type") or "").upper() == "INTEGRATION":
                last_id = s.get("atom_id")
    return last_id


def check_series_content_uniqueness(
    plans_dir: Path,
    rules_path: Optional[Path] = None,
) -> list[dict]:
    """
    For each series: compare each installment only to immediate previous.
    Return list of violations (empty if pass).
    """
    rules_path = rules_path or CONFIG_RULES
    rules = _load_yaml(rules_path)
    freshness = rules.get("freshness") or {}
    min_new_story = int(freshness.get("min_new_story_atoms_vs_prev", 2))
    require_distinct_integration = bool(freshness.get("require_distinct_integration_atom_vs_prev", True))

    plan_files = sorted([p for p in plans_dir.glob("*.json") if p.is_file() and "spec" not in p.name.lower()])
    by_series: dict[str, list[tuple[Path, dict]]] = {}
    for p in plan_files:
        data = _load_plan(p)
        if not data or not data.get("series_id"):
            continue
        sid = data.get("series_id")
        by_series.setdefault(sid, []).append((p, data))

    violations: list[dict] = []
    for series_id, group in by_series.items():
        group.sort(key=lambda x: (x[1].get("installment_number") or 0))
        for i in range(1, len(group)):
            prev_path, prev_plan = group[i - 1]
            curr_path, curr_plan = group[i]
            prev_story = _story_atom_ids(prev_plan)
            curr_story = _story_atom_ids(curr_plan)
            new_in_curr = curr_story - prev_story
            if len(new_in_curr) < min_new_story:
                violations.append({
                    "rule": "min_new_story_atoms_vs_prev",
                    "series_id": series_id,
                    "installment_number": curr_plan.get("installment_number"),
                    "plan_path": str(curr_path),
                    "new_story_count": len(new_in_curr),
                    "required": min_new_story,
                })
            if require_distinct_integration:
                prev_int = _final_integration_atom_id(prev_plan)
                curr_int = _final_integration_atom_id(curr_plan)
                if prev_int is not None and curr_int is not None and prev_int == curr_int:
                    violations.append({
                        "rule": "require_distinct_integration_atom_vs_prev",
                        "series_id": series_id,
                        "installment_number": curr_plan.get("installment_number"),
                        "plan_path": str(curr_path),
                        "repeated_atom_id": curr_int,
                    })
    return violations


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Series content freshness (P1): min new STORY vs prev, distinct INTEGRATION vs prev")
    ap.add_argument("--plans-dir", type=Path, required=True, help="Directory of compiled plan JSONs")
    ap.add_argument("--rules", type=Path, default=None, help="series_quality_rules.yaml path")
    args = ap.parse_args()

    violations = check_series_content_uniqueness(args.plans_dir, args.rules)
    if violations:
        print("CHECK_SERIES_CONTENT_UNIQUENESS: FAIL")
        for v in violations:
            print(f"  {v}")
        return 1
    print("CHECK_SERIES_CONTENT_UNIQUENESS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
