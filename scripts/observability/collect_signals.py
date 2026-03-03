#!/usr/bin/env python3
"""
Production Observability — collect all production signals (Phase 1 MVP).
Observes 100% repo: runs local scripts, captures pass/fail, writes snapshot.
See docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md
Usage:
  python scripts/observability/collect_signals.py
  python scripts/observability/collect_signals.py --signals gate_production_readiness systems_test
  python scripts/observability/collect_signals.py --out artifacts/observability/snapshot.json
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


def load_signal_registry() -> list[dict]:
    path = REPO_ROOT / "config" / "observability_production_signals.yaml"
    if not path.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(path.read_text()) or {}
        return data.get("signals", [])
    except Exception:
        return []


def run_script_signal(sig: dict, timestamp: str) -> dict:
    """Run a script-based signal and return result."""
    script = sig.get("script")
    if not script or not (REPO_ROOT / script).exists():
        return {"status": "skip", "message": f"Script not found: {script}"}
    args = sig.get("args") or []
    timeout = sig.get("timeout_sec", 120)
    cmd = [sys.executable, str(REPO_ROOT / script)] + [str(a).replace("{timestamp}", timestamp) for a in args]
    try:
        r = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        )
        return {
            "status": "pass" if r.returncode == 0 else "fail",
            "exit_code": r.returncode,
            "stdout_tail": (r.stdout or "")[-500:] if r.stdout else None,
            "stderr_tail": (r.stderr or "")[-500:] if r.stderr else None,
        }
    except subprocess.TimeoutExpired:
        return {"status": "fail", "message": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}


def run_pytest_signal(sig: dict, timestamp: str) -> dict:
    """Run a pytest-based signal."""
    test = sig.get("test")
    if not test or not (REPO_ROOT / test).exists():
        return {"status": "skip", "message": f"Test not found: {test}"}
    timeout = sig.get("timeout_sec", 60)
    cmd = [sys.executable, "-m", "pytest", test, "-v", "--tb=short"]
    try:
        r = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        )
        return {
            "status": "pass" if r.returncode == 0 else "fail",
            "exit_code": r.returncode,
            "stdout_tail": (r.stdout or "")[-500:] if r.stdout else None,
            "stderr_tail": (r.stderr or "")[-500:] if r.stderr else None,
        }
    except subprocess.TimeoutExpired:
        return {"status": "fail", "message": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}


def run_workflow_signal(sig: dict, timestamp: str) -> dict:
    """Workflow signals: passive (no local run). Status from last run would need GitHub API."""
    return {"status": "passive", "message": f"Workflow {sig.get('workflow')} — check GitHub Actions"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Collect production signals")
    ap.add_argument("--signals", nargs="*", help="Limit to these signal IDs")
    ap.add_argument("--out", default=None, help="Output path (default: artifacts/observability/signal_snapshot_{ts}.json)")
    args = ap.parse_args()
    signals = load_signal_registry()
    if not signals:
        print("No signals in config/observability_production_signals.yaml")
        return 1
    if args.signals:
        signals = [s for s in signals if s.get("id") in args.signals]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = []
    for sig in signals:
        sid = sig.get("id", "unknown")
        source = sig.get("source", "script")
        if source == "script":
            out = run_script_signal(sig, timestamp)
        elif source == "pytest":
            out = run_pytest_signal(sig, timestamp)
        elif source == "workflow":
            out = run_workflow_signal(sig, timestamp)
        else:
            out = {"status": "skip", "message": f"Unknown source: {source}"}
        results.append({
            "signal_id": sid,
            "category": sig.get("category", ""),
            "timestamp": timestamp,
            **out,
        })
        status = out.get("status", "?")
        print(f"  {status:8} {sid}")
    snapshot = {
        "timestamp": timestamp,
        "signals": results,
        "passed": sum(1 for r in results if r.get("status") == "pass"),
        "failed": sum(1 for r in results if r.get("status") == "fail"),
        "skipped": sum(1 for r in results if r.get("status") in ("skip", "passive")),
    }
    out_path = args.out or f"artifacts/observability/signal_snapshot_{timestamp}.json"
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(snapshot, indent=2))
    print(f"\nSnapshot: {out_file}")
    return 0 if snapshot["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
