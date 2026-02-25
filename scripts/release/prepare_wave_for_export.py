#!/usr/bin/env python3
"""
Release entrypoint: run all pre-publish gates for a wave before export.

Call this (or run_prepublish_gates.py directly) before any export to storefronts.
Do not export when this script exits non-zero.

Usage:
  python scripts/release/prepare_wave_for_export.py --wave-id my_wave --index artifacts/catalog_similarity/index.jsonl --report artifacts/ops/prepublish_my_wave.json
  python scripts/release/prepare_wave_for_export.py --plans-dir artifacts/waves/my_wave/plans --wave-rendered-dir artifacts/waves/my_wave/rendered --index artifacts/catalog_similarity/index.jsonl
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RUN_PREPUBLISH = REPO_ROOT / "scripts" / "ci" / "run_prepublish_gates.py"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run pre-publish gates for a wave; exit 1 on any gate failure so export must not proceed.",
    )
    ap.add_argument("--wave-id", default="", help="Wave ID: plans and rendered under artifacts/waves/<wave_id>/")
    ap.add_argument("--plans-dir", default="", help="Directory of compiled plan .json (overrides --wave-id when set)")
    ap.add_argument("--wave-rendered-dir", default="", help="Directory of rendered .txt for this wave (overrides --wave-id when set)")
    ap.add_argument("--index", required=True, help="Catalog similarity index.jsonl path")
    ap.add_argument("--catalog-rendered-dir", default="", help="Rendered .txt for existing catalog (optional)")
    ap.add_argument("--report", default="", help="Optional JSON report path (e.g. artifacts/ops/prepublish_<wave_id>.json)")
    ap.add_argument("--dry-run-index-update", action="store_true", help="Do not append to similarity index")
    args = ap.parse_args()

    if args.wave_id and not args.plans_dir and not args.wave_rendered_dir:
        plans_dir = REPO_ROOT / "artifacts" / "waves" / args.wave_id / "plans"
        wave_rendered_dir = REPO_ROOT / "artifacts" / "waves" / args.wave_id / "rendered"
    elif args.plans_dir and args.wave_rendered_dir:
        plans_dir = Path(args.plans_dir)
        wave_rendered_dir = Path(args.wave_rendered_dir)
    else:
        print("Either --wave-id or both --plans-dir and --wave-rendered-dir are required.", file=sys.stderr)
        return 1

    if not plans_dir.is_dir():
        print(f"Plans directory not found: {plans_dir}", file=sys.stderr)
        return 1
    if not wave_rendered_dir.is_dir():
        print(f"Wave rendered directory not found: {wave_rendered_dir}", file=sys.stderr)
        return 1

    index_path = Path(args.index)
    catalog_rendered = Path(args.catalog_rendered_dir) if args.catalog_rendered_dir else None

    cmd = [
        sys.executable,
        str(RUN_PREPUBLISH),
        "--plans-dir", str(plans_dir),
        "--index", str(index_path),
        "--wave-rendered-dir", str(wave_rendered_dir),
    ]
    if catalog_rendered is not None:
        cmd += ["--catalog-rendered-dir", str(catalog_rendered)]
    if args.report:
        cmd += ["--report", args.report]
    if args.dry_run_index_update:
        cmd += ["--dry-run-index-update"]

    r = subprocess.run(cmd, cwd=str(REPO_ROOT), timeout=600)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
