#!/usr/bin/env python3
"""
Weekly pipeline build orchestrator: pull marketing feedback signals, run canary + systems test, write to observability.
Inputs: optional EI V2 / marketing_integration.log or KPI file to decide segment or parameters.
Outputs: artifacts/observability/weekly_pipeline_result_{date}.json, optional operations board row.
See docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md and plan: Autonomous Improvement Loop.
Usage:
  python scripts/release/weekly_pipeline_with_marketing.py
  python scripts/release/weekly_pipeline_with_marketing.py --skip-canary --skip-systems-test
  python scripts/release/weekly_pipeline_with_marketing.py --marketing-signal artifacts/ei_v2/marketing_integration.log
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


def load_marketing_signal(path: Path | None) -> dict:
    """Load optional marketing/EI V2 signal (e.g. last log tail or KPI summary)."""
    if not path or not path.exists():
        return {"used": False, "path": None, "events_count": 0}
    try:
        lines = path.read_text().strip().splitlines()
        events = [json.loads(ln) for ln in lines if ln.strip() and _is_json_line(ln)]
        return {
            "used": True,
            "path": str(path),
            "events_count": len(events),
            "last_event": events[-1] if events else None,
        }
    except Exception:
        return {"used": False, "path": str(path), "error": "read_failed"}


def _is_json_line(line: str) -> bool:
    try:
        json.loads(line)
        return True
    except json.JSONDecodeError:
        return False


def run_canary(n: int = 10) -> dict:
    """Run pipeline canary (n books). Returns pass/fail and summary."""
    script = REPO_ROOT / "scripts" / "ci" / "run_canary_100_books.py"
    if not script.exists():
        return {"status": "skip", "message": "run_canary_100_books.py not found"}
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--n", str(n)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        )
        return {
            "status": "pass" if r.returncode == 0 else "fail",
            "exit_code": r.returncode,
            "stdout_tail": (r.stdout or "")[-500:] if r.stdout else None,
        }
    except subprocess.TimeoutExpired:
        return {"status": "fail", "message": "canary timeout"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}


def run_systems_test() -> dict:
    """Run systems test --all. Returns pass/fail and summary."""
    script = REPO_ROOT / "scripts" / "systems_test" / "run_systems_test.py"
    if not script.exists():
        return {"status": "skip", "message": "run_systems_test.py not found"}
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--all"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        )
        return {
            "status": "pass" if r.returncode == 0 else "fail",
            "exit_code": r.returncode,
            "stdout_tail": (r.stdout or "")[-500:] if r.stdout else None,
        }
    except subprocess.TimeoutExpired:
        return {"status": "fail", "message": "systems_test timeout"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}


def append_operations_board_row(row: dict) -> None:
    path = REPO_ROOT / "artifacts" / "observability" / "operations_board.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly pipeline with marketing feedback")
    ap.add_argument("--marketing-signal", default=None, help="Path to marketing/EI V2 log or KPI file (optional)")
    ap.add_argument("--skip-canary", action="store_true", help="Do not run canary")
    ap.add_argument("--skip-systems-test", action="store_true", help="Do not run systems test")
    ap.add_argument("--canary-n", type=int, default=10, help="Canary book count (default 10)")
    ap.add_argument("--out", default=None, help="Output JSON path (default: artifacts/observability/weekly_pipeline_result_{date}.json)")
    args = ap.parse_args()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_slug = datetime.now(timezone.utc).strftime("%Y%m%d")

    marketing_path = Path(args.marketing_signal) if args.marketing_signal else REPO_ROOT / "artifacts" / "ei_v2" / "marketing_integration.log"
    marketing = load_marketing_signal(marketing_path)

    canary_result = run_canary(args.canary_n) if not args.skip_canary else {"status": "skip"}
    systems_result = run_systems_test() if not args.skip_systems_test else {"status": "skip"}

    passed = sum(1 for r in (canary_result, systems_result) if r.get("status") == "pass")
    failed = sum(1 for r in (canary_result, systems_result) if r.get("status") == "fail")

    out_obj = {
        "timestamp": timestamp,
        "date_slug": date_slug,
        "marketing_signal": marketing,
        "canary": canary_result,
        "systems_test": systems_result,
        "passed": passed,
        "failed": failed,
        "overall": "pass" if failed == 0 else "fail",
    }

    out_path = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "observability" / f"weekly_pipeline_result_{date_slug}.json"
    out_path = out_path if out_path.is_absolute() else REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_obj, indent=2))

    append_operations_board_row({
        "timestamp": timestamp,
        "signal_id": "weekly_pipeline",
        "category": "core",
        "status": "impact_recorded",
        "impact": f"weekly_pipeline: {out_obj['overall']} (canary={canary_result.get('status')}, systems_test={systems_result.get('status')})",
        "artifact_path": str(out_path),
    })

    print(f"Weekly pipeline: {out_obj['overall']} (canary={canary_result.get('status')}, systems_test={systems_result.get('status')})")
    print(f"Result: {out_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
