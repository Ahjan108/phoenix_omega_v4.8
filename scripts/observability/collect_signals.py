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
import re
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


def _tail(text: str | None, n: int = 500) -> str | None:
    if not text:
        return None
    return text[-n:]


def _extract_missing_module(stderr_or_stdout: str | None) -> str | None:
    if not stderr_or_stdout:
        return None
    m = re.search(r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]", stderr_or_stdout)
    return m.group(1) if m else None


def _append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _run_cmd(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )


def _attempt_dependency_autofix(module_name: str) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", module_name],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=180,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        )
    except Exception as e:
        return False, f"pip install exception: {e}"
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    return r.returncode == 0, _tail(out, n=800) or ""


def run_script_signal(sig: dict, timestamp: str) -> dict:
    """Run a script-based signal and return result."""
    script = sig.get("script")
    if not script or not (REPO_ROOT / script).exists():
        return {"status": "skip", "message": f"Script not found: {script}"}
    args = sig.get("args") or []
    timeout = sig.get("timeout_sec", 120)
    auto_fix = sig.get("auto_fix_dependency", True)
    cmd = [sys.executable, str(REPO_ROOT / script)] + [str(a).replace("{timestamp}", timestamp) for a in args]
    try:
        r = _run_cmd(cmd, timeout=timeout)
        stdout = r.stdout or ""
        stderr = r.stderr or ""
        missing = _extract_missing_module(stderr) or _extract_missing_module(stdout)
        if r.returncode != 0 and auto_fix and missing:
            ok, fix_tail = _attempt_dependency_autofix(missing)
            if ok:
                r = _run_cmd(cmd, timeout=timeout)
                stdout = r.stdout or ""
                stderr = r.stderr or ""
            return {
                "status": "pass" if r.returncode == 0 else "fail",
                "exit_code": r.returncode,
                "stdout_tail": _tail(stdout),
                "stderr_tail": _tail(stderr),
                "auto_fix_attempted": True,
                "auto_fix_module": missing,
                "auto_fix_result_tail": fix_tail,
            }
        return {
            "status": "pass" if r.returncode == 0 else "fail",
            "exit_code": r.returncode,
            "stdout_tail": _tail(r.stdout),
            "stderr_tail": _tail(r.stderr),
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
    auto_fix = sig.get("auto_fix_dependency", True)
    cmd = [sys.executable, "-m", "pytest", test, "-v", "--tb=short"]
    try:
        r = _run_cmd(cmd, timeout=timeout)
        stdout = r.stdout or ""
        stderr = r.stderr or ""
        missing = _extract_missing_module(stderr) or _extract_missing_module(stdout)
        if r.returncode != 0 and auto_fix and missing:
            ok, fix_tail = _attempt_dependency_autofix(missing)
            if ok:
                r = _run_cmd(cmd, timeout=timeout)
                stdout = r.stdout or ""
                stderr = r.stderr or ""
            return {
                "status": "pass" if r.returncode == 0 else "fail",
                "exit_code": r.returncode,
                "stdout_tail": _tail(stdout),
                "stderr_tail": _tail(stderr),
                "auto_fix_attempted": True,
                "auto_fix_module": missing,
                "auto_fix_result_tail": fix_tail,
            }
        return {
            "status": "pass" if r.returncode == 0 else "fail",
            "exit_code": r.returncode,
            "stdout_tail": _tail(r.stdout),
            "stderr_tail": _tail(r.stderr),
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

    evidence_log = REPO_ROOT / "artifacts" / "observability" / "evidence_log.jsonl"
    elevated_log = REPO_ROOT / "artifacts" / "observability" / "elevated_failures.jsonl"
    for r in results:
        row = {
            "timestamp": timestamp,
            "signal_id": r.get("signal_id"),
            "category": r.get("category"),
            "status": r.get("status"),
            "exit_code": r.get("exit_code"),
            "auto_fix_attempted": r.get("auto_fix_attempted", False),
            "auto_fix_module": r.get("auto_fix_module"),
            "message": r.get("message"),
            "stdout_tail": r.get("stdout_tail"),
            "stderr_tail": r.get("stderr_tail"),
            "snapshot_path": str(out_file),
        }
        _append_jsonl(evidence_log, row)
        if r.get("status") == "fail":
            _append_jsonl(elevated_log, row)

    # Update operations board feed (issue → fix → PR → merged → impact)
    try:
        write_board = REPO_ROOT / "scripts" / "observability" / "write_operations_board.py"
        if write_board.exists():
            subprocess.run(
                [sys.executable, str(write_board), "--out", str(REPO_ROOT / "artifacts" / "observability" / "operations_board.jsonl")],
                cwd=str(REPO_ROOT),
                env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
                timeout=30,
                check=False,
            )
    except Exception:
        pass  # Do not fail collection if board write fails

    return 0 if snapshot["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
