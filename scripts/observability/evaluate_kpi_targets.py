#!/usr/bin/env python3
"""
Evaluate KPI targets against latest signal snapshot; emit trigger list for enhancement jobs.
Reads config/observability_kpi_targets.yaml and artifacts/observability/signal_snapshot*.json (or --snapshot path).
Writes artifacts/observability/kpi_trigger_{timestamp}.json.
See docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md and config/observability_kpi_targets.yaml
Usage:
  python scripts/observability/evaluate_kpi_targets.py
  python scripts/observability/evaluate_kpi_targets.py --snapshot artifacts/observability/signal_snapshot.json
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_kpi_config() -> list[dict]:
    path = REPO_ROOT / "config" / "observability_kpi_targets.yaml"
    if not path.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(path.read_text()) or {}
        return data.get("kpis", [])
    except Exception:
        return []


def load_latest_snapshot(snapshot_path: Path | None) -> dict | None:
    if snapshot_path:
        path = snapshot_path if snapshot_path.is_absolute() else REPO_ROOT / snapshot_path
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                return None
    obs_dir = REPO_ROOT / "artifacts" / "observability"
    if not obs_dir.exists():
        return None
    candidates = list(obs_dir.glob("signal_snapshot*.json"))
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        return json.loads(latest.read_text())
    except Exception:
        return None


def evaluate_kpis(snapshot: dict | None, kpis: list[dict]) -> list[dict]:
    triggers: list[dict] = []
    if not snapshot:
        return triggers

    signals = snapshot.get("signals") or []
    passed = snapshot.get("passed", 0)
    failed = snapshot.get("failed", 0)
    total = passed + failed
    overall_rate = (passed / total) if total else 0.0

    # Per-signal pass map
    signal_pass: dict[str, bool] = {}
    for s in signals:
        sid = s.get("signal_id", "")
        signal_pass[sid] = s.get("status") == "pass"

    for kpi in kpis:
        kpi_id = kpi.get("id", "")
        threshold = kpi.get("threshold", 0)
        trigger_job = kpi.get("trigger_job")
        if not trigger_job:
            continue
        current: float | None = None
        if kpi_id == "gate_production_readiness_pass":
            current = 1.0 if signal_pass.get("gate_production_readiness", False) else 0.0
        elif kpi_id == "atoms_coverage_pass":
            current = 1.0 if signal_pass.get("atoms_coverage", False) else 0.0
        elif kpi_id == "systems_test_pass_rate":
            # From snapshot if systems_test was run; else skip or use overall
            if signal_pass.get("systems_test") is not None:
                current = 1.0 if signal_pass.get("systems_test") else 0.0
            else:
                current = overall_rate
        elif kpi_id == "overall_signal_pass_rate":
            current = overall_rate
        else:
            continue
        if current is not None and current < threshold:
            triggers.append({
                "job": trigger_job,
                "kpi_id": kpi_id,
                "reason": f"{kpi_id}={current} below threshold {threshold}",
                "current": current,
                "threshold": threshold,
            })
    return triggers


def main() -> int:
    ap = argparse.ArgumentParser(description="Evaluate KPI targets and emit trigger list")
    ap.add_argument("--snapshot", default=None, help="Path to signal snapshot JSON (default: latest in artifacts/observability)")
    ap.add_argument("--out", default=None, help="Output path (default: artifacts/observability/kpi_trigger_{ts}.json)")
    args = ap.parse_args()

    snapshot_path = Path(args.snapshot) if args.snapshot else None
    snapshot = load_latest_snapshot(snapshot_path)
    kpis = load_kpi_config()
    if not kpis:
        print("No KPIs in config/observability_kpi_targets.yaml")
        return 0

    triggers = evaluate_kpis(snapshot, kpis)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snap_path_str: str | None = None
    if snapshot_path:
        snap_path_str = str(snapshot_path if snapshot_path.is_absolute() else REPO_ROOT / snapshot_path)
    elif (REPO_ROOT / "artifacts" / "observability").exists():
        cands = list((REPO_ROOT / "artifacts" / "observability").glob("signal_snapshot*.json"))
        if cands:
            snap_path_str = str(max(cands, key=lambda p: p.stat().st_mtime))
    out_obj = {
        "evaluated_at": timestamp,
        "snapshot_path": snap_path_str,
        "triggers": triggers,
    }

    out_path = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "observability" / f"kpi_trigger_{timestamp}.json"
    out_path = out_path if out_path.is_absolute() else REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_obj, indent=2))

    if triggers:
        print(f"KPI triggers: {len(triggers)} jobs")
        for t in triggers:
            print(f"  - {t['job']}: {t['reason']}")
    else:
        print("KPI triggers: none (all above threshold)")
    print(f"Output: {out_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
