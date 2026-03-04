#!/usr/bin/env python3
"""
Autonomous loop — weekly market recalibration: ingest marketing, recompute weights, update positioning, publish report.
See docs/ML_AUTONOMOUS_LOOP_SPEC.md §8.
Usage:
  python scripts/ml_loop/run_weekly_market_recalibration.py
  python scripts/ml_loop/run_weekly_market_recalibration.py --report-only
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly market recalibration")
    ap.add_argument("--report-only", action="store_true", help="Only write weekly report from existing artifacts")
    ap.add_argument("--out-dir", default=None, help="Artifacts dir")
    args = ap.parse_args()
    kpi_cfg = load_yaml(REPO_ROOT / "config" / "ml_loop" / "kpi_targets.yaml")
    out_dir = Path(args.out_dir) if args.out_dir else REPO_ROOT / "artifacts" / "ml_loop"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / (kpi_cfg.get("weekly_report_path", "weekly_report.json").replace("artifacts/ml_loop/", ""))
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}

    if not args.report_only:
        # Ingest: run full ML editorial weekly (section, variant, fit, rewrite, market_router)
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts/ml_editorial/run_weekly_ml_editorial.py")],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=900,
        )
        if r.returncode != 0:
            print("ML editorial weekly failed.", file=sys.stderr)
            return 1

    # Build weekly report and baseline from artifacts
    section_path = REPO_ROOT / "artifacts" / "ml_editorial" / "section_scores.jsonl"
    market_path = REPO_ROOT / "artifacts" / "ml_editorial" / "market_actions.jsonl"
    weak_count = 0
    total_sections = 0
    if section_path.exists():
        with section_path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    total_sections += 1
                    try:
                        row = json.loads(line)
                        if row.get("weak_flags"):
                            weak_count += 1
                    except json.JSONDecodeError:
                        pass
    weak_rate = (weak_count / total_sections) if total_sections else 0
    report = {
        "ts": ts,
        "source": "market_intelligence_integrator",
        "decision": "recalibration",
        "weak_section_rate": weak_rate,
        "weak_section_count": weak_count,
        "total_sections": total_sections,
        "baseline": {"weak_section_rate_baseline": weak_rate},
        "kpi_targets": [k.get("id") for k in (kpi_cfg.get("kpis") or [])],
    }
    report_path.write_text(json.dumps(report, indent=2))
    baseline_path = out_dir / "baseline.json"
    baseline_path.write_text(json.dumps(report.get("baseline", {}), indent=2))
    print(f"Weekly recalibration: report -> {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
