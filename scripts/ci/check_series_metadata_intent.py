#!/usr/bin/env python3
"""
Metadata Intent Gate (P1).

Blocking: unique search_intent_id per installment in series; title similarity below threshold (simple lexical/cosine).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

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


def _token_set(s: str) -> set[str]:
    """Lowercased word tokens for simple lexical similarity."""
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def check_series_metadata_intent(
    plans_dir: Path,
    rules_path: Optional[Path] = None,
) -> list[dict]:
    """
    Per series: unique search_intent_id; title similarity below max_title_similarity.
    Return list of violations.
    """
    rules_path = rules_path or CONFIG_RULES
    rules = _load_yaml(rules_path)
    max_sim = float(rules.get("metadata", {}).get("max_title_similarity", 0.85))

    plan_files = sorted([p for p in plans_dir.glob("*.json") if p.is_file() and "spec" not in p.name.lower()])
    by_series: dict[str, list[tuple[Path, dict]]] = {}
    for p in plan_files:
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        if not data.get("series_id"):
            continue
        by_series.setdefault(data["series_id"], []).append((p, data))

    violations: list[dict] = []
    for series_id, group in by_series.items():
        group.sort(key=lambda x: (x[1].get("installment_number") or 0))
        seen_intent: set[str] = set()
        for path, plan in group:
            intent = plan.get("search_intent_id") or ""
            if intent and intent in seen_intent:
                violations.append({
                    "rule": "unique_search_intent_id",
                    "series_id": series_id,
                    "plan_path": str(path),
                    "search_intent_id": intent,
                })
            if intent:
                seen_intent.add(intent)

        # Title similarity: pairwise within series
        titles = []
        paths_for_title = []
        for path, plan in group:
            t = (plan.get("title") or plan.get("book_title") or "").strip()
            titles.append(t)
            paths_for_title.append(path)
        for i in range(len(titles)):
            for j in range(i + 1, len(titles)):
                if not titles[i] or not titles[j]:
                    continue
                a, b = _token_set(titles[i]), _token_set(titles[j])
                sim = _jaccard(a, b)
                if sim >= max_sim:
                    violations.append({
                        "rule": "max_title_similarity",
                        "series_id": series_id,
                        "plan_paths": [str(paths_for_title[i]), str(paths_for_title[j])],
                        "similarity": round(sim, 2),
                        "threshold": max_sim,
                    })
    return violations


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Series metadata intent (P1): unique search_intent_id, title similarity below threshold")
    ap.add_argument("--plans-dir", type=Path, required=True, help="Directory of compiled plan JSONs")
    ap.add_argument("--rules", type=Path, default=None, help="series_quality_rules.yaml path")
    args = ap.parse_args()

    violations = check_series_metadata_intent(args.plans_dir, args.rules)
    if violations:
        print("CHECK_SERIES_METADATA_INTENT: FAIL")
        for v in violations:
            print(f"  {v}")
        return 1
    print("CHECK_SERIES_METADATA_INTENT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
