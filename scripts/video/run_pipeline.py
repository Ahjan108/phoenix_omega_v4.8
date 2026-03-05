#!/usr/bin/env python3
"""
Run the full video pipeline for a plan: preparer -> shot_planner -> asset_resolver -> timeline_builder -> caption_adapter -> qc -> provenance -> metadata.
Uses fixtures or artifacts; writes to artifacts/video/ by default.
Usage: python scripts/video/run_pipeline.py --plan-id plan-therapeutic-001 [--fixtures-dir fixtures/video_pipeline] [--out-dir artifacts/video]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def run(cmd: list[str], cwd: Path) -> bool:
    r = subprocess.run(cmd, cwd=cwd)
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Run full video pipeline for a plan")
    ap.add_argument("--plan-id", default="plan-therapeutic-001", help="Plan ID (used for naming)")
    ap.add_argument("--fixtures-dir", default=None, help="Dir with render_manifest.json etc (default: fixtures/video_pipeline)")
    ap.add_argument("--out-dir", default=None, help="Output dir (default: artifacts/video/<plan_id>)")
    ap.add_argument("--video-id", default=None, help="Video ID for provenance/manifest (default: video-<plan_id>)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing artifacts at every stage")
    ap.add_argument("--skip-render", action="store_true", default=True, help="Skip render step (default: True until FFmpeg integration; set False when run_render.py is wired)")
    args = ap.parse_args()

    fixtures = Path(args.fixtures_dir or str(REPO_ROOT / "fixtures" / "video_pipeline"))
    out_root = Path(args.out_dir or str(REPO_ROOT / "artifacts" / "video" / args.plan_id))
    video_id = args.video_id or f"video-{args.plan_id}"
    out_root.mkdir(parents=True, exist_ok=True)

    manifest_path = fixtures / "render_manifest.json"
    if not manifest_path.exists():
        print(f"Error: render manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    scripts = REPO_ROOT / "scripts" / "video"
    py = sys.executable
    force_flag = ["--force"] if args.force else []
    steps = [
        ([py, str(scripts / "prepare_script_segments.py"), str(manifest_path), "-o", str(out_root / "script_segments.json")] + force_flag, "Script Preparer"),
        ([py, str(scripts / "run_shot_planner.py"), str(out_root / "script_segments.json"), "-o", str(out_root / "shot_plan.json")] + force_flag, "Shot Planner"),
        ([py, str(scripts / "run_asset_resolver.py"), str(out_root / "shot_plan.json"), "-o", str(out_root / "resolved_assets.json")] + force_flag, "Asset Resolver"),
        ([py, str(scripts / "run_timeline_builder.py"), str(out_root / "shot_plan.json"), str(out_root / "resolved_assets.json"), "-o", str(out_root / "timeline.json")] + force_flag, "Timeline Builder"),
        ([py, str(scripts / "run_caption_adapter.py"), str(out_root / "timeline.json"), str(out_root / "script_segments.json"), "-o", str(out_root / "captions.json")] + force_flag, "Caption Adapter"),
        ([py, str(scripts / "run_qc.py"), str(out_root / "shot_plan.json"), str(out_root / "resolved_assets.json"), str(out_root / "timeline.json"), "-o", str(out_root / "qc_summary.json")], "QC"),
    ]
    for cmd, name in steps:
        if not run(cmd, REPO_ROOT):
            print(f"Failed: {name}", file=sys.stderr)
            return 1
        print(f"OK: {name}")

    # --- Render step (insert here when FFmpeg integration is ready) ---
    # run_render.py: timeline.json + assets -> staging/<date>/<video_id>/video.mp4, thumb.jpg
    # Example: run( [py, str(scripts / "run_render.py"), str(out_root / "timeline.json"), "-o", str(staging_dir)], REPO_ROOT )
    if not args.skip_render:
        # Placeholder: run_render.py when implemented
        pass

    timeline = json.loads((out_root / "timeline.json").read_text(encoding="utf-8"))
    duration_s = timeline.get("duration_s", 0)
    primary_asset_ids = [c.get("asset_id") for c in timeline.get("clips", []) if c.get("asset_id")]
    provenance_path = f"artifacts/video/provenance/{video_id}.json"
    prov_out = REPO_ROOT / "artifacts" / "video" / "provenance"
    prov_out.mkdir(parents=True, exist_ok=True)

    prov_cmd = [
        py, str(scripts / "write_provenance.py"),
        "--video-id", video_id, "--plan-id", args.plan_id,
        "--shot-plan", str(out_root / "shot_plan.json"),
        "--resolved", str(out_root / "resolved_assets.json"),
        "--timeline", str(out_root / "timeline.json"),
        "-o", str(prov_out / f"{video_id}.json"),
        "--duration-s", str(duration_s),
        "--hook-type", "light_reveal", "--environment", "forest_path", "--motion-type", "slow_zoom",
        "--music-mood", "calm", "--caption-pattern", "question_hook", "--style-version", "v1",
    ] + force_flag
    if not run(prov_cmd, REPO_ROOT):
        print("Failed: Provenance Writer", file=sys.stderr)
        return 1
    print("OK: Provenance Writer")

    meta_cmd = [
        py, str(scripts / "write_metadata.py"),
        "--video-id", video_id, "--plan-id", args.plan_id,
        "--shot-plan", str(out_root / "shot_plan.json"),
        "--title", "When anxiety shows up",
        "--description", "A short on noticing anxiety without fighting it.",
        "--provenance-path", provenance_path, "--batch-id", "batch-2026-03-04-001",
        "-o", str(out_root / "distribution_manifest.json"),
        "--tags", "anxiety,mindfulness,therapeutic",
        "--primary-asset-ids", ",".join(primary_asset_ids),
        "--hook-type", "light_reveal", "--environment", "forest_path", "--motion-type", "slow_zoom",
        "--music-mood", "calm", "--caption-pattern", "question_hook", "--style-version", "v1",
    ] + force_flag
    if not run(meta_cmd, REPO_ROOT):
        print("Failed: Metadata Writer", file=sys.stderr)
        return 1
    print("OK: Metadata Writer")

    print(f"Pipeline complete. Outputs in {out_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
