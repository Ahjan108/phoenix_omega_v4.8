#!/usr/bin/env python3
"""
ML Editorial — Weekly orchestration: section scoring -> variant ranking -> reader fit -> rewrite recs -> market router.
Runs all five stages and writes audit log. See docs/ML_EDITORIAL_MARKET_LOOP_SPEC.md
Usage:
  python scripts/ml_editorial/run_weekly_ml_editorial.py
  python scripts/ml_editorial/run_weekly_ml_editorial.py --skip-section-scoring
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


def load_config() -> dict:
    path = REPO_ROOT / "config" / "ml_editorial" / "ml_editorial_config.yaml"
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def audit_log(artifacts_dir: Path, action: str, outcome: str, detail: str = "") -> None:
    cfg = load_config()
    log_path = Path((cfg.get("automation") or {}).get("audit_log_path", "artifacts/ml_editorial/audit_log.jsonl"))
    log_path = REPO_ROOT / log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    row = {"action": action, "outcome": outcome, "ts": ts, "detail": detail}
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="ML Editorial weekly run")
    ap.add_argument("--skip-section-scoring", action="store_true", help="Skip section scoring step")
    ap.add_argument("--artifacts-dir", default=None, help="Output dir (default from config)")
    args = ap.parse_args()
    config = load_config()
    if not config.get("ml_actions_enabled", False):
        print("ml_actions_enabled is false; running in read-only (artifacts still written).")
    paths = config.get("paths") or {}
    out_dir = Path(args.artifacts_dir) if args.artifacts_dir else REPO_ROOT / (paths.get("output_dir") or "artifacts/ml_editorial")
    out_dir.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    steps = []
    if not args.skip_section_scoring:
        steps.append(("run_section_scoring", [sys.executable, str(REPO_ROOT / "scripts/ml_editorial/run_section_scoring.py"), "--out", str(out_dir / "section_scores.jsonl")]))
    steps.extend([
        ("run_variant_ranking", [sys.executable, str(REPO_ROOT / "scripts/ml_editorial/run_variant_ranking.py"), "--out", str(out_dir / "variant_rankings.jsonl")]),
        ("run_reader_fit", [sys.executable, str(REPO_ROOT / "scripts/ml_editorial/run_reader_fit.py"), "--out", str(out_dir / "reader_fit_scores.jsonl")]),
        ("run_rewrite_recs", [sys.executable, str(REPO_ROOT / "scripts/ml_editorial/run_rewrite_recs.py"), "--section-scores", str(out_dir / "section_scores.jsonl"), "--out", str(out_dir / "rewrite_recs.jsonl")]),
        ("run_market_router", [sys.executable, str(REPO_ROOT / "scripts/ml_editorial/run_market_router.py"), "--artifacts-dir", str(out_dir), "--out", str(out_dir / "market_actions.jsonl")]),
    ])
    for name, cmd in steps:
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            audit_log(out_dir, name, "fail", r.stderr or r.stdout or "")
            print(f"{name}: failed", file=sys.stderr)
            return 1
        audit_log(out_dir, name, "ok", "")
        print(f"{name}: ok")
    audit_log(out_dir, "weekly_ml_editorial", "ok", "all steps completed")
    print(f"Weekly ML Editorial complete -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
