#!/usr/bin/env python3
"""
EI V2 catalog calibration: run EI V2 analysis over a sample of catalog arcs
to produce calibration metrics (score distributions, thresholds).
Output: artifacts/ei_v2/catalog_calibration.json
Stub: writes minimal report; extend with real catalog scan when needed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="EI V2 catalog calibration")
    ap.add_argument("--out", default=None, help="Output JSON path")
    ap.add_argument("--sample", type=int, default=0, help="Max arcs to sample (0 = skip scan)")
    ap.add_argument("--learn", action="store_true", help="Enable learning mode (currently no-op placeholder)")
    args = ap.parse_args()

    out_path = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "ei_v2" / "catalog_calibration.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "run_at": datetime.utcnow().isoformat() + "Z",
        "sample_size": args.sample,
        "learn_enabled": bool(args.learn),
        "status": "stub",
        "message": "Calibration stub; add catalog scan and EI V2 batch run to produce metrics.",
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
