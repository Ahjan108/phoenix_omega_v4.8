#!/usr/bin/env python3
"""
Autonomous loop — daily promotion: evaluate queue, apply drift/confidence rules, auto-PR for safe scope.
See docs/ML_AUTONOMOUS_LOOP_SPEC.md §7.
Usage:
  python scripts/ml_loop/run_daily_promotion.py
  python scripts/ml_loop/run_daily_promotion.py --dry-run
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


def load_jsonl(path: Path, limit: int = 500) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
                if len(out) >= limit:
                    break
            except json.JSONDecodeError:
                continue
    return out


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Daily promotion: queue -> gates -> auto-PR")
    ap.add_argument("--dry-run", action="store_true", help="Do not call agent_open_fix_pr")
    ap.add_argument("--queue", default=None, help="Promotion queue JSONL path")
    args = ap.parse_args()
    policy = load_yaml(REPO_ROOT / "config" / "ml_loop" / "promotion_policy.yaml")
    drift_cfg = load_yaml(REPO_ROOT / "config" / "ml_loop" / "drift_thresholds.yaml")
    if not policy.get("autonomy_enabled", False):
        print("autonomy_enabled is false; skipping promotion.")
        return 0
    queue_path = Path(args.queue) if args.queue else REPO_ROOT / (policy.get("promotion_queue_path") or "artifacts/ml_loop/promotion_queue.jsonl")
    board_path = REPO_ROOT / (policy.get("operations_board_path") or "artifacts/observability/operations_board.jsonl")
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    confidence_floor = policy.get("confidence_floor_ranker", 0.7)
    candidates = load_jsonl(queue_path)
    promoted = 0
    for c in candidates:
        if c.get("decision") != "promote":
            continue
        if (c.get("confidence") or 0) < confidence_floor:
            append_jsonl(board_path, {"ts": ts, "book_id": c.get("book_id"), "source": "promotion_engine", "decision": "hold", "confidence": c.get("confidence"), "evidence_path": c.get("evidence_path"), "reason": "below_confidence_floor"})
            continue
        if args.dry_run:
            promoted += 1
            continue
        script = policy.get("agent_open_fix_pr_script") or "scripts/observability/agent_open_fix_pr.py"
        script_path = REPO_ROOT / script
        if script_path.exists():
            r = subprocess.run([sys.executable, str(script_path)], cwd=str(REPO_ROOT), env={**os.environ, "PYTHONPATH": str(REPO_ROOT)}, capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                promoted += 1
                append_jsonl(board_path, {"ts": ts, "book_id": c.get("book_id"), "source": "pr_agent", "decision": "pr_opened", "confidence": c.get("confidence"), "evidence_path": c.get("evidence_path")})
            else:
                append_jsonl(board_path, {"ts": ts, "book_id": c.get("book_id"), "source": "pr_agent", "decision": "fail", "confidence": c.get("confidence"), "evidence_path": c.get("evidence_path"), "suggested_fix": r.stderr or r.stdout})
    print(f"Daily promotion: {promoted} promoted (dry_run={args.dry_run})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
