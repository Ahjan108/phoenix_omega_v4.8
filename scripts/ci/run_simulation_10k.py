#!/usr/bin/env python3
"""
Run 10k simulation for CI: format/structure at scale with Phase 2+3.
Output: artifacts/simulation_10k.json
Usage: python scripts/ci/run_simulation_10k.py [--out PATH] [--n N]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="Run 10k simulation for CI")
    ap.add_argument("--n", type=int, default=10000, help="Number of books (default 10000)")
    ap.add_argument("--out", default="", help="Output JSON path (default: artifacts/simulation_10k.json)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    args = ap.parse_args()

    out_path = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "simulation_10k.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(REPO_ROOT / "simulation" / "run_simulation.py"),
        "--n", str(args.n),
        "--seed", str(args.seed),
        "--use-format-selector",
        "--phase2",
        "--phase3",
        "--out", str(out_path),
    ]
    import os
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), env={**os.environ, "PYTHONPATH": str(REPO_ROOT)})
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
