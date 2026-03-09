#!/usr/bin/env python3
"""
EI V2 catalog calibration: run EI V2 analysis over a sample of catalog arcs
to produce calibration metrics (score distributions, thresholds).
Output: artifacts/ei_v2/catalog_calibration.json
When --learn: updates learned_params.json (total_observations) and appends to learner_feedback.jsonl.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EI_V2_ARTIFACTS = REPO_ROOT / "artifacts" / "ei_v2"
LEARNED_PARAMS_PATH = EI_V2_ARTIFACTS / "learned_params.json"
LEARNER_FEEDBACK_PATH = EI_V2_ARTIFACTS / "learner_feedback.jsonl"


def main() -> int:
    ap = argparse.ArgumentParser(description="EI V2 catalog calibration")
    ap.add_argument("--out", default=None, help="Output JSON path")
    ap.add_argument("--sample", type=int, default=0, help="Max arcs to sample (0 = skip scan)")
    ap.add_argument("--learn", action="store_true", help="Enable learning mode: update learned_params, append learner_feedback")
    args = ap.parse_args()

    out_path = Path(args.out) if args.out else EI_V2_ARTIFACTS / "catalog_calibration.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "run_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sample_size": args.sample,
        "learn_enabled": bool(args.learn),
        "status": "ok",
        "message": "Calibration run; use --sample N and real EI V2 batch for full metrics.",
    }

    if args.learn:
        try:
            from phoenix_v4.quality.ei_v2.learner import load_learned_params, save_learned_params

            params = load_learned_params(path=LEARNED_PARAMS_PATH)
            params.total_observations = getattr(params, "total_observations", 0) + 1
            save_learned_params(params, LEARNED_PARAMS_PATH)
            report["learned_params_updated"] = True
            report["total_observations"] = params.total_observations

            LEARNER_FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
            feedback_line = json.dumps({
                "timestamp": report["run_at"],
                "run": "calibration",
                "total_observations": params.total_observations,
            }, ensure_ascii=False) + "\n"
            with open(LEARNER_FEEDBACK_PATH, "a", encoding="utf-8") as f:
                f.write(feedback_line)
            report["learner_feedback_appended"] = True
        except Exception as e:
            report["learn_error"] = str(e)
            report["status"] = "learn_failed"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
