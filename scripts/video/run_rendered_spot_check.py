#!/usr/bin/env python3
"""
Rendered spot-check: sample 1–2% of daily renders, extract frame(s), optionally run safety classifier.
Writes artifacts/video/spot_check/<date>.json with sample plan_ids, frame paths, and optional command results.
Usage:
  python scripts/video/run_rendered_spot_check.py --date 2026-03-08
  python scripts/video/run_rendered_spot_check.py --date 2026-03-08 --sample-pct 2 --safety-cmd 'python scripts/safety/classify_frame.py'
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import write_atomically, get_ffmpeg_bin


def _discover_renders_for_date(artifacts_video: Path, batch_date: str) -> list[Path]:
    """Plan dirs that have video.mp4 (and optionally distribution_manifest.json)."""
    out = []
    if not artifacts_video.exists():
        return out
    for plan_dir in sorted(artifacts_video.iterdir()):
        if not plan_dir.is_dir() or plan_dir.name == "provenance" or plan_dir.name == "spot_check":
            continue
        if (plan_dir / "video.mp4").exists():
            out.append(plan_dir)
    return out


def _extract_frame(video_path: Path, out_frame_path: Path, ffmpeg_bin: str = "ffmpeg", time_s: float = 1.0) -> bool:
    """Extract one frame at time_s seconds. Returns True on success."""
    try:
        subprocess.run(
            [ffmpeg_bin, "-y", "-ss", str(time_s), "-i", str(video_path), "-vframes", "1", str(out_frame_path)],
            capture_output=True,
            timeout=30,
            check=True,
        )
        return out_frame_path.exists()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Spot-check daily renders: sample N%%, extract frame, optional safety command")
    ap.add_argument("--date", default=None, help="Batch date YYYY-MM-DD (default: discover from artifacts)")
    ap.add_argument("--artifacts-dir", default=None, help="artifacts/video dir (default: REPO_ROOT/artifacts/video)")
    ap.add_argument("--sample-pct", type=float, default=1.5, help="Sample this percentage of renders (1–2 typical)")
    ap.add_argument("--safety-cmd", default="", help="Command to run on extracted frame path (e.g. classifier); receives one arg: frame path")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    ap.add_argument("--min-sample", type=int, default=1, help="At least this many videos sampled if any exist")
    args = ap.parse_args()

    artifacts_video = Path(args.artifacts_dir or str(REPO_ROOT / "artifacts" / "video"))
    batch_date = args.date
    if not batch_date:
        # Default: use latest date from staging or a single global pool
        plan_dirs = _discover_renders_for_date(artifacts_video, "")
        if not plan_dirs:
            print("No renders found; use --date or ensure artifacts/video/<plan_id>/video.mp4 exist", file=sys.stderr)
            return 0
    else:
        plan_dirs = _discover_renders_for_date(artifacts_video, batch_date)

    if not plan_dirs:
        print("No renders found", file=sys.stderr)
        return 0

    n = max(args.min_sample, max(1, int(len(plan_dirs) * args.sample_pct / 100.0)))
    rng = random.Random(args.seed)
    sampled = rng.sample(plan_dirs, min(n, len(plan_dirs)))
    ffmpeg_bin = get_ffmpeg_bin()
    spot_dir = artifacts_video / "spot_check"
    spot_dir.mkdir(parents=True, exist_ok=True)
    date_key = batch_date or "latest"
    frames_dir = spot_dir / date_key
    frames_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for plan_dir in sampled:
        video_path = plan_dir / "video.mp4"
        plan_id = plan_dir.name
        frame_path = frames_dir / f"{plan_id}_frame.jpg"
        ok = _extract_frame(str(video_path), frame_path, ffmpeg_bin)
        entry = {"plan_id": plan_id, "video_path": str(video_path), "frame_path": str(frame_path), "frame_extracted": ok}
        if args.safety_cmd and frame_path.exists():
            try:
                r = subprocess.run(
                    [*args.safety_cmd.split(), str(frame_path)],
                    capture_output=True,
                    timeout=60,
                    text=True,
                )
                entry["safety_exit_code"] = r.returncode
                entry["safety_stdout"] = (r.stdout or "")[:500]
                entry["safety_stderr"] = (r.stderr or "")[:500]
            except Exception as e:
                entry["safety_error"] = str(e)
        results.append(entry)

    log_data = {
        "date": date_key,
        "sample_pct": args.sample_pct,
        "total_renders": len(plan_dirs),
        "sampled": len(sampled),
        "results": results,
    }
    out_path = spot_dir / f"{date_key}.json"
    write_atomically(out_path, log_data)
    print(f"Wrote spot-check log: {out_path} ({len(results)} sampled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
