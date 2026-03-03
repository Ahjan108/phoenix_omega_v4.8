#!/usr/bin/env python3
"""
Single export path: run pre-publish gates then (optionally) upload.

No code path allows upload without gates. Automation must call this script
(or prepare_wave_for_export only) — never an upload path that skips gates.

Wave path contract: plans at artifacts/waves/<wave_id>/plans,
rendered at artifacts/waves/<wave_id>/rendered (see PREPUBLISH_CHECKLIST.md).

Usage:
  python scripts/release/export_wave.py --wave-id my_wave --index artifacts/catalog_similarity/index.jsonl
  python scripts/release/export_wave.py --wave-id my_wave --index artifacts/catalog_similarity/index.jsonl --upload-cmd "echo Upload would run"
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PREPARE_WAVE = REPO_ROOT / "scripts" / "release" / "prepare_wave_for_export.py"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run pre-publish gates for a wave; on success, optionally run upload command. No upload without gates.",
    )
    ap.add_argument("--wave-id", required=True, help="Wave ID (resolves to artifacts/waves/<wave_id>/plans and .../rendered)")
    ap.add_argument("--index", required=True, help="Catalog similarity index.jsonl path")
    ap.add_argument("--catalog-rendered-dir", default="", help="Rendered .txt for existing catalog (optional)")
    ap.add_argument("--report", default="", help="Optional JSON report path (e.g. artifacts/ops/prepublish_<wave_id>.json)")
    ap.add_argument("--dry-run-index-update", action="store_true", help="Do not append to similarity index")
    ap.add_argument("--upload-cmd", default="", help="Command to run after gates pass (e.g. script or 'echo done'). If empty, only gates run.")
    args = ap.parse_args()

    cmd = [
        sys.executable,
        str(PREPARE_WAVE),
        "--wave-id", args.wave_id,
        "--index", args.index,
    ]
    if args.catalog_rendered_dir:
        cmd += ["--catalog-rendered-dir", args.catalog_rendered_dir]
    if args.report:
        cmd += ["--report", args.report]
    if args.dry_run_index_update:
        cmd += ["--dry-run-index-update"]

    r = subprocess.run(cmd, cwd=str(REPO_ROOT), timeout=600)
    if r.returncode != 0:
        return r.returncode

    if args.upload_cmd:
        r2 = subprocess.run(args.upload_cmd, shell=True, cwd=str(REPO_ROOT))
        return r2.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
