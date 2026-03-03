#!/usr/bin/env python3
"""
Real pipeline canary: run run_pipeline.py on sampled (topic, persona, arc) combos.
Proves actual compile + render succeeds for worst/best combos or a fixed diverse set.
Usage: python scripts/ci/run_canary_100_books.py [--n N] [--out-dir DIR]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ARCS_DIR = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"


def _parse_arc_filename(name: str) -> tuple[str, str] | None:
    """Parse persona__topic__engine__format.yaml -> (persona, topic)."""
    stem = name.replace(".yaml", "")
    parts = stem.split("__")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None


def _sample_arcs(n: int, seed: int = 42) -> list[tuple[Path, str, str]]:
    """Sample n arcs with diverse persona/topic coverage. Returns [(arc_path, persona, topic), ...]."""
    if not ARCS_DIR.exists():
        return []
    arc_files = sorted(ARCS_DIR.glob("*.yaml"))
    parsed: list[tuple[Path, str, str]] = []
    for ap in arc_files:
        p = _parse_arc_filename(ap.name)
        if p:
            parsed.append((ap, p[0], p[1]))
    if not parsed:
        return []
    # Deterministic sample
    import random
    rng = random.Random(seed)
    k = min(n, len(parsed))
    return rng.sample(parsed, k)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run pipeline canary on sampled arcs")
    ap.add_argument("--n", type=int, default=20, help="Number of books (default 20 for CI speed)")
    ap.add_argument("--out-dir", default="", help="Output dir for plans (default: artifacts/canary_plans)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else REPO_ROOT / "artifacts" / "canary_plans"
    out_dir.mkdir(parents=True, exist_ok=True)

    samples = _sample_arcs(args.n, args.seed)
    if not samples:
        print("No arcs found", file=sys.stderr)
        return 1

    pipeline_script = REPO_ROOT / "scripts" / "run_pipeline.py"
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
    failures: list[dict] = []

    for i, (arc_path, persona, topic) in enumerate(samples):
        plan_path = out_dir / f"canary_{i:03d}_{arc_path.stem}.json"
        cmd = [
            sys.executable,
            str(pipeline_script),
            "--topic", topic,
            "--persona", persona,
            "--arc", str(arc_path),
            "--out", str(plan_path),
            "--no-generate-freebies",
        ]
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            failures.append({
                "arc": arc_path.name,
                "persona": persona,
                "topic": topic,
                "stderr": (r.stderr or "")[:500],
            })
            print(f"FAIL: {arc_path.name} ({persona}/{topic})", file=sys.stderr)
        elif not plan_path.exists():
            failures.append({"arc": arc_path.name, "persona": persona, "topic": topic, "error": "output not created"})
            print(f"FAIL: {arc_path.name} output missing", file=sys.stderr)

    if failures:
        report_path = out_dir / "canary_failures.json"
        report_path.write_text(json.dumps({"failures": failures, "total": len(samples), "failed": len(failures)}, indent=2))
        print(f"Canary: {len(failures)}/{len(samples)} failed. Report: {report_path}", file=sys.stderr)
        return 1
    print(f"Canary: {len(samples)}/{len(samples)} passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
