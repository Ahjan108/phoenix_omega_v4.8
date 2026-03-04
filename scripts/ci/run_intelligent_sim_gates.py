#!/usr/bin/env python3
"""
Robust intelligent simulation gates: run 10k sim (or use existing), analyze with
per-dimension + baseline regression, then bestseller/root-cause report. Single entry point.
Usage:
  python scripts/ci/run_intelligent_sim_gates.py
  python scripts/ci/run_intelligent_sim_gates.py --sim-artifact artifacts/simulation_10k.json
  python scripts/ci/run_intelligent_sim_gates.py --run-sim --n 10000 --min-pass-rate 0.95 --strict
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ARTIFACT = REPO_ROOT / "artifacts" / "simulation_10k.json"
REPORTS_DIR = REPO_ROOT / "artifacts" / "reports"


def run(cmd: list[str], cwd: Path) -> int:
    """Run command; return exit code."""
    r = subprocess.run(
        cmd,
        cwd=str(cwd),
        env={**__import__("os").environ, "PYTHONPATH": str(cwd)},
    )
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Robust intelligent sim gates: 10k → analyze → bestseller report")
    ap.add_argument("--sim-artifact", default="", help=f"Path to simulation JSON (default: {DEFAULT_ARTIFACT})")
    ap.add_argument("--run-sim", action="store_true", help="Run 10k simulation first (ignore --sim-artifact if set)")
    ap.add_argument("--n", type=int, default=10000, help="Number of books when --run-sim (default 10000)")
    ap.add_argument("--min-pass-rate", type=float, default=0.95, help="Min overall pass rate (default 0.95)")
    ap.add_argument("--min-format-rate", type=float, default=0.0, help="Min pass rate per format (0 = disabled)")
    ap.add_argument("--min-tier-rate", type=float, default=0.0, help="Min pass rate per tier (0 = disabled)")
    ap.add_argument("--baseline", default="", help="Baseline JSON for regression (optional)")
    ap.add_argument("--regress-tolerance", type=float, default=0.05, help="Max drop vs baseline (default 0.05)")
    ap.add_argument("--strict", action="store_true", help="Fail on high-risk format/tier (bestseller report)")
    ap.add_argument("--llm", action="store_true", help="Call LLM in bestseller report (optional)")
    ap.add_argument("--no-fail", action="store_true", help="Do not exit 1 on gate failure (report only)")
    args = ap.parse_args()

    sim_path = Path(args.sim_artifact) if args.sim_artifact else DEFAULT_ARTIFACT

    if args.run_sim:
        print("Running 10k simulation...")
        code = run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "ci" / "run_simulation_10k.py"),
                "--n", str(args.n),
                "--out", str(sim_path),
            ],
            REPO_ROOT,
        )
        if code != 0:
            print("Simulation failed.", file=sys.stderr)
            return code if not args.no_fail else 0
        print("Simulation done.")

    if not sim_path.exists():
        print(f"Error: simulation artifact not found: {sim_path}", file=sys.stderr)
        return 1

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    analysis_out = REPORTS_DIR / "pearl_prime_sim_analysis.json"

    print("Running analyzer (per-format, per-tier, optional baseline regression)...", flush=True)
    analyze_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "ci" / "analyze_pearl_prime_sim.py"),
        "--input", str(sim_path),
        "--out", str(analysis_out),
        "--min-pass-rate", str(args.min_pass_rate),
        "--min-format-rate", str(args.min_format_rate),
        "--min-tier-rate", str(args.min_tier_rate),
        "--regress-tolerance", str(args.regress_tolerance),
    ]
    if args.baseline:
        analyze_cmd += ["--baseline", args.baseline]
    if args.no_fail:
        analyze_cmd.append("--no-fail")
    code = run(analyze_cmd, REPO_ROOT)
    if code != 0 and not args.no_fail:
        return code

    print("Running bestseller/root-cause report (heuristic + optional LLM)...", flush=True)
    report_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "ci" / "llm_bestseller_error_report.py"),
        "--input", str(sim_path),
        "--out", str(REPORTS_DIR),
    ]
    if args.strict:
        report_cmd.append("--strict")
    if args.llm:
        report_cmd.append("--llm")
    if args.no_fail:
        # Bestseller report still exits 1 on bestseller failures; we don't have --no-fail there
        pass
    code = run(report_cmd, REPO_ROOT)
    if code != 0 and not args.no_fail:
        return code

    print("Intelligent gates complete. Reports:")
    print(f"  {analysis_out}")
    print(f"  {REPORTS_DIR / 'pearl_prime_sim_analysis_SUMMARY.txt'}")
    print(f"  {REPORTS_DIR / 'bestseller_error_report.json'}")
    print(f"  {REPORTS_DIR / 'bestseller_error_report_SUMMARY.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
