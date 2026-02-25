#!/usr/bin/env python3
"""
Run the quality pipeline golden path end-to-end and keep artifacts.

Order: quality_bundle_builder → update_memorable_line_registry → wave_candidates_enricher
       → wave_optimizer_constraint_solver → check_memorable_line_registry.

Uses artifacts/rendered/book_001/book.txt and artifacts/book_001.plan.json.
Writes: artifacts/ops/book_quality_bundle_*.json; artifacts/waves/golden_candidates*.json;
        artifacts/ops/wave_optimizer/wave_optimizer_solution_*.
Registry artifacts (memorable_line_registry_v1.jsonl, memorable_line_registry_snapshot_v1.json)
are created or updated only when the bundle has tracked memorable lines (strength good/great);
otherwise the updater no-ops and registry is unchanged.

Run from repo root: PYTHONPATH=. python scripts/run_golden_quality_path.py
Requires: jsonschema (pip install jsonschema).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

WAVE_ID = "golden_quality_path"
DATE = "20260226"


def run(cmd: list[str], name: str, allow_exit: tuple[int, ...] = (0,)) -> bool:
    r = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env={**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode not in allow_exit:
        print(f"FAIL {name}: {r.stderr or r.stdout or 'non-zero exit'}", file=sys.stderr)
        return False
    print(f"OK   {name}")
    return True


def main() -> int:
    rendered = REPO_ROOT / "artifacts" / "rendered" / "book_001" / "book.txt"
    plan = REPO_ROOT / "artifacts" / "book_001.plan.json"
    ops_dir = REPO_ROOT / "artifacts" / "ops"
    waves_dir = REPO_ROOT / "artifacts" / "waves"

    if not rendered.exists() or not plan.exists():
        print("Missing rendered text or plan. Create artifacts/rendered/book_001/book.txt and artifacts/book_001.plan.json", file=sys.stderr)
        return 1

    # 1. Quality bundle builder (0 pass, 2 warn, 1 fail with bundle written — all OK to continue)
    bundle_path = ops_dir / f"book_quality_bundle_book_001_{DATE}.json"
    if not run([
        sys.executable, "-m", "phoenix_v4.quality.quality_bundle_builder",
        "--rendered-text", str(rendered),
        "--compiled-plan", str(plan),
        "--out-dir", str(ops_dir),
        "--date", DATE,
        "--overwrite",
    ], "quality_bundle_builder", allow_exit=(0, 1, 2)):
        return 1

    if not bundle_path.exists():
        print("Bundle not found after build.", file=sys.stderr)
        return 1

    # 2. Update memorable line registry (only appends when bundle has good/great memorable lines)
    r_registry = subprocess.run(
        [
            sys.executable, "-m", "phoenix_v4.ops.update_memorable_line_registry",
            "--bundle", str(bundle_path),
            "--ops-dir", str(ops_dir),
        ],
        cwd=str(REPO_ROOT),
        env={**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=60,
    )
    if r_registry.returncode != 0:
        print(f"FAIL update_memorable_line_registry: {r_registry.stderr or r_registry.stdout or 'non-zero exit'}", file=sys.stderr)
        return 1
    print("OK   update_memorable_line_registry")
    registry_unchanged = "No tracked memorable lines" in (r_registry.stdout or "")
    if registry_unchanged:
        print("     (no tracked lines; registry unchanged)")

    # 3. Wave candidates (minimal: one candidate book_001)
    candidates_path = waves_dir / "golden_candidates.json"
    waves_dir.mkdir(parents=True, exist_ok=True)
    candidates = {
        "candidates": [
            {
                "candidate_id": "book_001",
                "book_id": "book_001",
                "candidate_sort_key": "book_001",
                "tuple_id": "persona|topic|E1|F006",
                "brand_id": "phoenix",
                "persona_id": "gen_z",
                "topic_id": "overthinking",
                "engine_id": "E1",
                "arc_id": "arc1",
                "slot_sig": "sig1",
                "band_sig": "3-3-4",
                "variation_signature": "V1",
                "teacher_mode": False,
                "risk": "GREEN",
                "volatility": 0.5,
            },
        ],
    }
    candidates_path.write_text(json.dumps(candidates, indent=2), encoding="utf-8")

    enriched_path = waves_dir / "golden_candidates_enriched.json"
    if not run([
        sys.executable, "-m", "phoenix_v4.ops.wave_candidates_enricher",
        "--wave-candidates", str(candidates_path),
        "--quality-bundles-dir", str(ops_dir),
        "--out", str(enriched_path),
        "--warn-on-missing",
    ], "wave_candidates_enricher"):
        return 1

    # 4. Solver (target 1; golden config relaxes quality so single candidate is eligible)
    config_path = REPO_ROOT / "config" / "wave_optimizer_constraint_solver_golden.yaml"
    out_wo = ops_dir / "wave_optimizer"
    if not run([
        sys.executable, "-m", "phoenix_v4.ops.wave_optimizer_constraint_solver",
        "--wave-id", WAVE_ID,
        "--target-size", "1",
        "--candidates-json", str(enriched_path),
        "--ops-dir", str(ops_dir),
        "--config", str(config_path),
        "--out-dir", str(out_wo),
    ], "wave_optimizer_constraint_solver"):
        return 1

    solution_path = out_wo / f"wave_optimizer_solution_{WAVE_ID}.json"
    if not solution_path.exists():
        print("Solver did not produce solution file.", file=sys.stderr)
        return 1

    # 5. Check memorable line registry (pre-export gate)
    exit_check = subprocess.run(
        [
            sys.executable, "-m", "phoenix_v4.ops.check_memorable_line_registry",
            "--wave", str(solution_path),
            "--ops-dir", str(ops_dir),
        ],
        cwd=str(REPO_ROOT),
        env={**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    # 0 pass, 1 fail, 2 warn — any is acceptable for golden path (we may have no collisions)
    if exit_check.returncode not in (0, 2):
        print(f"check_memorable_line_registry exit {exit_check.returncode}: {exit_check.stderr or exit_check.stdout}", file=sys.stderr)
    else:
        print("OK   check_memorable_line_registry (pass or warn)")

    print("\nGolden path complete. Artifacts kept:")
    print(f"  {bundle_path}")
    if registry_unchanged:
        print("  Registry: no tracked lines; registry unchanged (JSONL/snapshot not written this run).")
    else:
        print(f"  {ops_dir / 'memorable_line_registry_v1.jsonl'}")
        print(f"  {ops_dir / 'memorable_line_registry_snapshot_v1.json'}")
    print(f"  {enriched_path}")
    print(f"  {solution_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
