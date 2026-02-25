"""
Phase 11 — Brand Identity Stability Index (BISI).

Tracks structural drift of a single brand over time by comparing
current window (last 90 days) vs previous window (90 days before that).
Ensures brand personality and emotional signature stay within intended bounds.

Uses same dimensions as CBDI: arc, slot, band, engine, volatility.
BISI_drift(B) = weighted JSD(P_current, P_previous) per dimension.

Input: history index or plans-dir (same as Phase 10).
Output: artifacts/ops/brand_identity_stability_{report_date}.json

Exit: 0 PASS, 2 WARN (drift high), 1 FAIL (drift critical).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

from phoenix_v4.ops.cross_brand_divergence import (
    load_releases_in_window,
    build_brand_distributions,
    cbdi_pair,
)


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run(
    report_date: str,
    window_days: int,
    history_index_path: Optional[Path],
    plans_dir: Optional[Path],
    config: dict,
) -> dict[str, Any]:
    """Compute brand identity stability (drift per brand). Returns full output dict."""
    cfg = config.get("brand_identity_stability") or {}
    min_books = int(cfg.get("minimum_books_per_brand", 20))
    th = cfg.get("thresholds") or {}
    warn_above = float(th.get("warn_above", 0.18))
    fail_above = float(th.get("fail_above", 0.25))
    weights = cfg.get("weights") or {
        "arc": 0.30, "slot": 0.20, "band": 0.20, "engine": 0.15, "volatility": 0.15,
    }
    recommendations = cfg.get("recommendations") or {}
    _fallback = "Execute remediation per ops playbook."

    end_dt = datetime.strptime(report_date, "%Y-%m-%d")
    # Current window: [report_date - window_days + 1, report_date]
    start_current = (end_dt - timedelta(days=window_days - 1)).strftime("%Y-%m-%d")
    end_current = report_date
    # Previous window: [report_date - 2*window_days + 1, report_date - window_days]
    end_prev_dt = end_dt - timedelta(days=window_days)
    start_prev = (end_prev_dt - timedelta(days=window_days - 1)).strftime("%Y-%m-%d")
    end_prev = end_prev_dt.strftime("%Y-%m-%d")

    current_releases = load_releases_in_window(start_current, end_current, history_index_path, plans_dir)
    prev_releases = load_releases_in_window(start_prev, end_prev, history_index_path, plans_dir)

    dist_current = build_brand_distributions(current_releases, 0)
    dist_prev = build_brand_distributions(prev_releases, 0)

    current_counts = defaultdict(int)
    for r in current_releases:
        current_counts[r["brand_id"]] += 1
    prev_counts = defaultdict(int)
    for r in prev_releases:
        prev_counts[r["brand_id"]] += 1

    brands_evaluated = [
        b for b in dist_current
        if b in dist_prev and current_counts[b] >= min_books and prev_counts[b] >= min_books
    ]
    brands_evaluated.sort()

    results: list[dict[str, Any]] = []
    alerts: list[dict[str, Any]] = []

    for brand_id in brands_evaluated:
        drift_score, components = cbdi_pair(dist_current[brand_id], dist_prev[brand_id], weights)
        results.append({
            "brand_id": brand_id,
            "drift_score": drift_score,
            "components": components,
        })
        rec_high = (recommendations.get("BRAND_IDENTITY_DRIFT_HIGH") or _fallback).strip()
        rec_crit = (recommendations.get("BRAND_IDENTITY_DRIFT_CRITICAL") or _fallback).strip()
        if drift_score > fail_above:
            alerts.append({
                "severity": "FAIL",
                "code": "BRAND_IDENTITY_DRIFT_CRITICAL",
                "brand_id": brand_id,
                "score": drift_score,
                "threshold": fail_above,
                "recommendation": rec_crit,
            })
        elif drift_score > warn_above:
            alerts.append({
                "severity": "WARN",
                "code": "BRAND_IDENTITY_DRIFT_HIGH",
                "brand_id": brand_id,
                "score": drift_score,
                "threshold": warn_above,
                "recommendation": rec_high,
            })

    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_date": report_date,
        "window_days": window_days,
        "brands_evaluated": brands_evaluated,
        "results": results,
        "alerts": alerts,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 11: Brand Identity Stability Index (BISI)")
    ap.add_argument("--report-date", default=None, help="Report date YYYY-MM-DD; default today UTC")
    ap.add_argument("--window-days", type=int, default=90, help="Rolling window days (each of current and previous)")
    ap.add_argument("--history-index", type=Path, default=None, help="JSONL with publish_date, brand_id, arc_id, slot_sig, band_sig, engine_id")
    ap.add_argument("--plans-dir", type=Path, default=None, help="Plans directory (file mtime = date)")
    ap.add_argument("--out-dir", type=Path, default=None, help="Output dir (default artifacts/ops)")
    ap.add_argument("--config", type=Path, default=None, help="Config YAML (default config/brand_identity_stability.yaml)")
    args = ap.parse_args()

    repo_root = REPO_ROOT
    report_date = args.report_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = args.out_dir or repo_root / "artifacts" / "ops"
    config_path = args.config or repo_root / "config" / "brand_identity_stability.yaml"
    config = _load_yaml(config_path)
    if not config:
        config = {"brand_identity_stability": {"window_days": args.window_days}}

    bis = config.get("brand_identity_stability") or {}
    window_days = int(bis.get("window_days", args.window_days))

    result = run(
        report_date=report_date,
        window_days=window_days,
        history_index_path=args.history_index,
        plans_dir=args.plans_dir,
        config=config,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"brand_identity_stability_{report_date}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    has_fail = any(a.get("severity") == "FAIL" for a in result.get("alerts") or [])
    has_warn = any(a.get("severity") == "WARN" for a in result.get("alerts") or [])

    print(f"Written: {json_path}")
    print(f"Brands evaluated: {len(result.get('brands_evaluated') or [])}  Alerts: {len(result.get('alerts') or [])}")
    if has_fail:
        return 1
    if has_warn:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
