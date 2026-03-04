#!/usr/bin/env python3
"""
Autonomous loop — continuous (24/7): score, fast gates, queue pass candidates, send failures to operations board.
Trigger: hourly or on artifact/commit. See docs/ML_AUTONOMOUS_LOOP_SPEC.md §6.
Usage:
  python scripts/ml_loop/run_continuous_loop.py
  python scripts/ml_loop/run_continuous_loop.py --skip-scoring --skip-gates
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


def load_policy() -> dict:
    return load_yaml(REPO_ROOT / "config" / "ml_loop" / "promotion_policy.yaml")


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Continuous loop: score, fast gates, queue, operations board")
    ap.add_argument("--skip-scoring", action="store_true", help="Skip ML section scoring")
    ap.add_argument("--skip-gates", action="store_true", help="Skip fast gates")
    ap.add_argument("--out-dir", default=None, help="Artifacts dir (default artifacts/ml_loop)")
    args = ap.parse_args()
    policy = load_policy()
    if not policy.get("autonomy_enabled", False):
        print("autonomy_enabled is false; running in read-only.")
    out_dir = Path(args.out_dir) if args.out_dir else REPO_ROOT / "artifacts" / "ml_loop"
    out_dir.mkdir(parents=True, exist_ok=True)
    candidates_path = REPO_ROOT / (policy.get("continuous_candidates_path") or "artifacts/ml_loop/continuous_candidates.jsonl")
    queue_path = REPO_ROOT / (policy.get("promotion_queue_path") or "artifacts/ml_loop/promotion_queue.jsonl")
    board_path = REPO_ROOT / (policy.get("operations_board_path") or "artifacts/observability/operations_board.jsonl")
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}

    # 1. Run fast ML scoring (section only for speed)
    if not args.skip_scoring:
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts/ml_editorial/run_section_scoring.py"), "--out", str(REPO_ROOT / "artifacts/ml_editorial/section_scores.jsonl")],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=300,
        )
        if r.returncode != 0:
            append_jsonl(board_path, {"ts": ts, "issue_id": "continuous_loop", "source": "detector_agent", "decision": "fail", "confidence": 0, "evidence_path": None, "suggested_fix": r.stderr or r.stdout})
            print("Section scoring failed.", file=sys.stderr)
            return 1

    # 2. Run fast gates (production readiness is the main gate; optional: schema/safety)
    if not args.skip_gates:
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts/run_production_readiness_gates.py")],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            append_jsonl(board_path, {"ts": ts, "issue_id": "continuous_loop_gates", "source": "governance_agent", "decision": "fail", "confidence": 0, "evidence_path": None, "suggested_fix": r.stderr or "Run production readiness gates and fix reported issues."})
            print("Fast gates failed.", file=sys.stderr)
            return 1

    # 3. Read section_scores, filter by confidence/threshold, write candidates
    section_path = REPO_ROOT / "artifacts" / "ml_editorial" / "section_scores.jsonl"
    confidence_floor = policy.get("confidence_floor_ranker", 0.7)
    count_candidates = 0
    if section_path.exists():
        with section_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    book_id = row.get("book_id", "")
                    clarity = row.get("clarity_score", 0)
                    pacing = row.get("pacing_score", 0)
                    weak = row.get("weak_flags") or []
                    confidence = min(clarity, pacing) if (clarity and pacing) else 0.5
                    if confidence >= confidence_floor and not weak:
                        cand = {"ts": ts, "book_id": book_id, "source": "section_scoring", "decision": "promote", "confidence": confidence, "evidence_path": str(section_path)}
                        append_jsonl(candidates_path, cand)
                        append_jsonl(queue_path, cand)
                        count_candidates += 1
                    elif weak:
                        append_jsonl(board_path, {"ts": ts, "book_id": book_id, "source": "detector_agent", "decision": "fix", "confidence": confidence, "evidence_path": str(section_path), "suggested_fix": f"Address weak_flags: {weak}"})
                except json.JSONDecodeError:
                    continue
    print(f"Continuous loop: gates pass, {count_candidates} candidates queued -> {queue_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
