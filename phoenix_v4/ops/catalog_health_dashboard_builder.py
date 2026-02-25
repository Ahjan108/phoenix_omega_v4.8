#!/usr/bin/env python3
"""
Build catalog health summary from validated Ops artifacts.

Reads artifacts/ops and artifacts/waves to produce:
  artifacts/ops/catalog_health_summary_<YYYYMMDD>.json
  (optional) artifacts/ops/catalog_health_summary_<YYYYMMDD>.md

Usage:
  PYTHONPATH=. python3 -m phoenix_v4.ops.catalog_health_dashboard_builder \
    --ops-dir artifacts/ops --waves-dir artifacts/waves
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _glob_bundles(ops_dir: Path) -> List[Path]:
    return list(ops_dir.glob("book_quality_bundle_*.json"))


def _glob_solutions(ops_dir: Path) -> List[Path]:
    wo = ops_dir / "wave_optimizer"
    if wo.exists():
        return list(wo.glob("wave_optimizer_solution_*.json"))
    return []


def _glob_infeasible(ops_dir: Path) -> List[Path]:
    wo = ops_dir / "wave_optimizer"
    if wo.exists():
        return list(wo.glob("wave_optimizer_infeasible_*.json"))
    return []


def _glob_violations(ops_dir: Path) -> List[Path]:
    return list(ops_dir.glob("memorable_line_registry_violations_*.json"))


def _glob_coverage(ops_dir: Path) -> List[Path]:
    return list(ops_dir.glob("coverage_health_weekly_*.json"))


def build_quality_metrics(ops_dir: Path) -> Dict[str, Any]:
    bundles = _glob_bundles(ops_dir)
    by_brand: Dict[str, List[float]] = defaultdict(list)
    by_persona: Dict[str, List[float]] = defaultdict(list)
    by_topic: Dict[str, List[float]] = defaultdict(list)
    pass_c, warn_c, fail_c = 0, 0, 0
    ending_strengths: List[float] = []

    for path in bundles:
        data = _load_json(path)
        if not data or not isinstance(data, dict):
            continue
        csi = data.get("csi") or {}
        score = csi.get("score")
        if score is not None:
            brand = data.get("brand_id") or "unknown"
            persona = data.get("persona_id") or "unknown"
            topic = data.get("topic_id") or "unknown"
            by_brand[brand].append(float(score))
            by_persona[persona].append(float(score))
            by_topic[topic].append(float(score))
        status = (data.get("status") or "").lower()
        if status == "pass":
            pass_c += 1
        elif status == "warn":
            warn_c += 1
        else:
            fail_c += 1
        comp = csi.get("components") or {}
        es = comp.get("ending_strength")
        if es is not None:
            ending_strengths.append(float(es))

    mean = lambda xs: sum(xs) / len(xs) if xs else 0
    return {
        "mean_csi_per_brand": {k: round(mean(v), 1) for k, v in by_brand.items()},
        "mean_csi_per_persona": {k: round(mean(v), 1) for k, v in by_persona.items()},
        "mean_csi_per_topic": {k: round(mean(v), 1) for k, v in by_topic.items()},
        "pass_count": pass_c,
        "warn_count": warn_c,
        "fail_count": fail_c,
        "ending_strength_distribution": {
            "min": min(ending_strengths) if ending_strengths else 0,
            "max": max(ending_strengths) if ending_strengths else 0,
            "mean": round(mean(ending_strengths), 1),
        },
        "low_ending_ratio_per_wave": {},
    }


def build_duplication_risk(ops_dir: Path) -> Dict[str, Any]:
    snapshot_path = ops_dir / "memorable_line_registry_snapshot_v1.json"
    data = _load_json(snapshot_path) if snapshot_path.exists() else None
    if not data:
        return {
            "memorable_line_collision_count": 0,
            "top_repeated_great_lines": [],
            "wave_collision_hotspots": [],
        }
    lines = data.get("lines") or []
    collisions = [l for l in lines if int(l.get("occurrence_count", 0)) > 1]
    great_repeated = [l for l in lines if (l.get("strength_max") == "great") and int(l.get("occurrence_count", 0)) > 1]
    great_repeated.sort(key=lambda x: -int(x.get("occurrence_count", 0)))
    return {
        "memorable_line_collision_count": len(collisions),
        "top_repeated_great_lines": great_repeated[:10],
        "wave_collision_hotspots": [],
    }


def build_coverage(ops_dir: Path) -> Dict[str, Any]:
    coverage_files = _glob_coverage(ops_dir)
    if not coverage_files:
        return {"tuple_risk_trend": "", "deficits_by_code_delta": {}}
    latest = max(coverage_files, key=lambda p: p.stat().st_mtime)
    data = _load_json(latest)
    if not data:
        return {"tuple_risk_trend": "", "deficits_by_code_delta": {}}
    return {
        "tuple_risk_trend": data.get("summary", {}).get("tuple_risk_trend") or "",
        "deficits_by_code_delta": data.get("deficits_by_code_delta") or {},
    }


def build_release_readiness(ops_dir: Path) -> Dict[str, Any]:
    infeasible = _glob_infeasible(ops_dir)
    blocked = 0
    infeasible_quality = 0
    for path in infeasible:
        data = _load_json(path)
        if not data:
            continue
        reasons = data.get("blocking_reasons") or []
        for r in reasons:
            bd = r.get("exclusion_breakdown") or {}
            blocked += bd.get("filtered_fail", 0) + bd.get("filtered_ending", 0) + bd.get("filtered_csi", 0) + bd.get("filtered_missing", 0)
            if bd.get("filtered_fail") or bd.get("filtered_ending") or bd.get("filtered_csi"):
                infeasible_quality += 1
    return {
        "candidates_blocked_by_quality": blocked,
        "infeasible_waves_due_to_quality": infeasible_quality,
    }


def build_low_ending_ratio_per_wave(ops_dir: Path) -> Dict[str, float]:
    out = {}
    for path in _glob_solutions(ops_dir):
        data = _load_json(path)
        if not data:
            continue
        wave_id = data.get("wave_id", path.stem)
        qs = data.get("quality_summary") or {}
        ratio = qs.get("low_ending_ratio")
        if ratio is not None:
            out[wave_id] = round(float(ratio), 2)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Build catalog health summary from ops artifacts")
    ap.add_argument("--ops-dir", type=Path, default=None, help="Default artifacts/ops")
    ap.add_argument("--waves-dir", type=Path, default=None, help="Default artifacts/waves")
    ap.add_argument("--out", type=Path, default=None, help="Output JSON path")
    ap.add_argument("--md", action="store_true", help="Also write .md summary")
    args = ap.parse_args()

    ops_dir = args.ops_dir or REPO_ROOT / "artifacts" / "ops"
    waves_dir = args.waves_dir or REPO_ROOT / "artifacts" / "waves"
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = args.out or ops_dir / f"catalog_health_summary_{date_str}.json"

    quality = build_quality_metrics(ops_dir)
    quality["low_ending_ratio_per_wave"] = build_low_ending_ratio_per_wave(ops_dir)
    duplication_risk = build_duplication_risk(ops_dir)
    coverage = build_coverage(ops_dir)
    release_readiness = build_release_readiness(ops_dir)

    summary = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ"),
        "quality": quality,
        "duplication_risk": duplication_risk,
        "coverage": coverage,
        "release_readiness": release_readiness,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written: {out_path}")

    if args.md:
        md_path = out_path.with_suffix(".md")
        lines = [
            "# Catalog Health Summary",
            "",
            f"**Generated:** {summary['generated_at']}",
            "",
            "## Quality",
            f"- Pass: {quality['pass_count']}  Warn: {quality['warn_count']}  Fail: {quality['fail_count']}",
            f"- Ending strength: min={quality['ending_strength_distribution'].get('min')} max={quality['ending_strength_distribution'].get('max')} mean={quality['ending_strength_distribution'].get('mean')}",
            "",
            "## Duplication risk",
            f"- Memorable line collisions: {duplication_risk['memorable_line_collision_count']}",
            "",
            "## Release readiness",
            f"- Candidates blocked by quality: {release_readiness['candidates_blocked_by_quality']}",
            f"- Infeasible waves (quality): {release_readiness['infeasible_waves_due_to_quality']}",
        ]
        md_path.write_text("\n".join(lines))
        print(f"Written: {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
