#!/usr/bin/env python3
"""
Autonomous loop — delegate to observability agent for opening fix PRs.
Low-risk dependency/config fixes only; allowlist in promotion_policy.
See docs/ML_AUTONOMOUS_LOOP_SPEC.md and scripts/observability/agent_open_fix_pr.py
Usage:
  python scripts/ml_loop/agent_open_fix_pr.py
  python scripts/ml_loop/agent_open_fix_pr.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="Delegate to observability agent_open_fix_pr")
    ap.add_argument("--dry-run", action="store_true", help="Pass through to agent")
    args = ap.parse_args()
    script = REPO_ROOT / "scripts" / "observability" / "agent_open_fix_pr.py"
    if not script.exists():
        print("Observability agent_open_fix_pr.py not found.", file=sys.stderr)
        return 1
    cmd = [sys.executable, str(script)]
    if args.dry_run:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), env={**os.environ, "PYTHONPATH": str(REPO_ROOT)}, timeout=120)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
