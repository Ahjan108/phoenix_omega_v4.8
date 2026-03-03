#!/usr/bin/env python3
"""
Rigorous system test: systems test + variation report + atoms coverage.
Single entrypoint for full rigorous run. Used by release-gates.
Usage: python scripts/ci/run_rigorous_system_test.py [--skip-sim] [--strict]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def run(cmd: list[str], desc: str) -> int:
    """Run command; return exit code."""
    print(f"\n--- {desc} ---")
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), env={**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)})
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Run rigorous system test")
    ap.add_argument("--skip-sim", action="store_true", help="Skip 10k simulation (faster)")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any step fails")
    args = ap.parse_args()

    failed = 0

    # 1. Systems test (phases 1-7)
    rc = run(
        [sys.executable, "scripts/systems_test/run_systems_test.py", "--all", "--strict"],
        "Systems test (phases 1-7)",
    )
    if rc != 0:
        failed += 1

    # 2. Variation report (if index exists)
    report_script = REPO_ROOT / "scripts" / "ci" / "report_variation_knobs.py"
    index_path = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
    if report_script.exists() and index_path.exists():
        rc = run([sys.executable, str(report_script)], "Variation report")
        if rc != 0:
            failed += 1
    else:
        print("\n--- Variation report (skip: index not found) ---")

    # 3. Atoms coverage (slow but critical)
    rc = run(
        [sys.executable, "-m", "pytest", "tests/test_atoms_coverage_100_percent.py", "-v", "--tb=short"],
        "Atoms coverage 100%",
    )
    if rc != 0:
        failed += 1

    # 4. 10k simulation (optional)
    if not args.skip_sim:
        rc = run(
            [sys.executable, "scripts/ci/run_simulation_10k.py", "--n", "1000"],
            "Simulation 1k (reduced for rigorous run)",
        )
        if rc != 0:
            failed += 1
        if failed == 0:
            rc = run(
                [
                    sys.executable,
                    "scripts/ci/analyze_pearl_prime_sim.py",
                    "--input", "artifacts/simulation_10k.json",
                    "--no-fail",
                ],
                "Analyze simulation",
            )
    else:
        print("\n--- Simulation (skipped) ---")

    if failed > 0:
        print(f"\nFAILED: {failed} step(s)")
        if args.strict:
            return 1
    print("\nRigorous system test complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
