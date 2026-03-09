#!/usr/bin/env python3
"""
Run the full video pipeline for a plan: preparer -> shot_planner -> asset_resolver -> timeline_builder -> caption_adapter -> qc -> provenance -> metadata -> thumbnail generator.
Writes pipeline_log.json with per-stage timing and pipeline_version for throughput tuning and debugging.
Usage: python scripts/video/run_pipeline.py --plan-id plan-therapeutic-001 [--fixtures-dir fixtures/video_pipeline] [--out-dir artifacts/video] [--topic anxiety]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import PIPELINE_VERSION, write_atomically


def run(cmd: list[str], cwd: Path) -> bool:
    r = subprocess.run(cmd, cwd=cwd)
    return r.returncode == 0


def has_audio_stream(video_path: Path) -> bool:
    if not video_path.exists():
        return False


def _evaluate_scene_alignment(script_segments_path: Path, segment_scenes_path: Path) -> tuple[float, list[tuple[str, float]]]:
    """
    Use EI V2 reranker heuristic as scene<->script alignment score.
    Returns (average_score, [(segment_id, score), ...]).
    """
    try:
        from phoenix_v4.quality.ei_v2.cross_encoder_reranker import rerank_candidates
    except Exception:
        return 0.0, []
    segs = json.loads(script_segments_path.read_text(encoding="utf-8")).get("segments", [])
    scenes = json.loads(segment_scenes_path.read_text(encoding="utf-8")).get("segments", [])
    scene_by_id = {s.get("segment_id"): s for s in scenes if s.get("segment_id")}
    per_seg: list[tuple[str, float]] = []
    for s in segs:
        sid = s.get("segment_id", "")
        text = (s.get("text") or "").strip()
        desc = (scene_by_id.get(sid) or {}).get("scene_description", "")
        if not text or not desc:
            per_seg.append((sid, 0.0))
            continue
        scored = rerank_candidates(text, [desc], [sid], cfg={"method": "heuristic", "top_n": 1})
        score = float(scored[0].get("score", 0.0)) if scored else 0.0
        per_seg.append((sid, score))
    if not per_seg:
        return 0.0, []
    avg = sum(v for _, v in per_seg) / len(per_seg)
    return avg, per_seg


def _log_ei_scene_learning(
    *,
    topic: str,
    persona: str,
    slot: str,
    success: bool,
    v1_id: str,
    v2_id: str,
    final_id: str,
) -> None:
    """Append EI learner feedback so retries contribute to learning telemetry."""
    try:
        from phoenix_v4.quality.ei_v2.learner import (
            FeedbackRecord,
            load_learned_params,
            log_feedback,
            save_learned_params,
        )
    except Exception:
        return
    repo = REPO_ROOT
    params_path = repo / "artifacts" / "ei_v2" / "learned_params.json"
    feedback_path = repo / "artifacts" / "ei_v2" / "learner_feedback.jsonl"
    params = load_learned_params(path=params_path)
    params.total_observations = int(getattr(params, "total_observations", 0)) + 1
    save_learned_params(params, params_path)
    rec = FeedbackRecord(
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        slot=slot,
        chapter_index=0,
        persona_id=persona or "",
        topic_id=topic or "",
        v1_chosen_id=v1_id,
        v2_chosen_id=v2_id,
        hybrid_chosen_id=final_id,
        override_applied=bool(success and final_id != v1_id),
    )
    log_feedback(rec, feedback_path)
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        for p in ("/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe"):
            if Path(p).exists():
                ffprobe = p
                break
    if not ffprobe:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            for p in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
                if Path(p).exists():
                    ffmpeg = p
                    break
        if ffmpeg and Path(ffmpeg).exists():
            try:
                r = subprocess.run([ffmpeg, "-i", str(video_path)], capture_output=True, text=True, timeout=8)
                return "Audio:" in ((r.stderr or "") + (r.stdout or ""))
            except Exception:
                return False
        return False
    try:
        r = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_type", "-of", "default=nw=1:nk=1", str(video_path)],
            capture_output=True,
            text=True,
            timeout=8,
        )
        return r.returncode == 0 and "audio" in (r.stdout or "").lower()
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Run full video pipeline for a plan")
    ap.add_argument("--plan-id", default="plan-therapeutic-001", help="Plan ID (used for naming)")
    ap.add_argument("--fixtures-dir", default=None, help="Dir with render_manifest.json etc (default: fixtures/video_pipeline)")
    ap.add_argument("--out-dir", default=None, help="Output dir (default: artifacts/video/<plan_id>)")
    ap.add_argument("--video-id", default=None, help="Video ID for provenance/manifest (default: video-<plan_id>)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing artifacts at every stage")
    ap.add_argument("--assets-dir", default=None, help="Assets directory for render (asset_id -> <assets_dir>/<asset_id>.jpg|.png)")
    ap.add_argument("--bank", default=None, help="Image bank index (e.g. image_bank/index.json) for asset resolver; if --assets-dir set but --bank unset, uses <assets-dir>/index.json when present")
    ap.add_argument("--segment-index", default=None, help="Segment asset index (segment_asset_index.json) for script-specific images; auto-used if out_dir/segment_asset_index.json exists")
    ap.add_argument("--skip-render", action="store_true", default=True, help="Skip render step (default: True)")
    ap.add_argument("--run-render", action="store_true", help="Run render step")
    ap.add_argument("--topic", default="", help="Content topic for metadata and thumbnail hook (e.g. anxiety, burnout)")
    ap.add_argument("--persona", default="", help="Persona identifier for metadata and thumbnail (reserved)")
    ap.add_argument("--platform", default="tiktok", help="Target platform (tiktok, youtube, instagram_reels, youtube_shorts)")
    ap.add_argument("--skip-thumbnail", action="store_true", help="Skip thumbnail generator (use renderer frame-extract only)")
    ap.add_argument("--content-type", default="therapeutic", help="Content type for pacing and QC (e.g. therapeutic, long_form for 90s)")
    ap.add_argument("--segment-scenes", dest="segment_scenes", action="store_true", help="Generate script-specific segment scenes and per-segment images (required; default: on)")
    ap.add_argument("--allow-placeholder-ratio", type=float, default=0.0, help="Maximum allowed placeholder asset ratio (0.0 = none allowed)")
    ap.add_argument("--allow-silent-video", action="store_true", help="Allow publish pipeline to continue when rendered video has no audio stream")
    ap.set_defaults(segment_scenes=True)
    args = ap.parse_args()

    content_type = args.content_type or "therapeutic"
    fixtures = Path(args.fixtures_dir or str(REPO_ROOT / "fixtures" / "video_pipeline"))
    out_root = Path(args.out_dir or str(REPO_ROOT / "artifacts" / "video" / args.plan_id))
    video_id = args.video_id or f"video-{args.plan_id}"
    out_root.mkdir(parents=True, exist_ok=True)

    manifest_path = fixtures / "render_manifest.json"
    if not manifest_path.exists():
        print(f"Error: render manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    # Optional: derive topic from script segments if not passed
    topic = (args.topic or "").strip()
    persona = (args.persona or "").strip()
    if not topic and (out_root / "script_segments.json").exists():
        try:
            segs = json.loads((out_root / "script_segments.json").read_text(encoding="utf-8"))
            for s in segs.get("segments", []):
                t = (s.get("metadata") or {}).get("topic", "").strip()
                if t:
                    topic = t
                    break
        except Exception:
            pass

    scripts = REPO_ROOT / "scripts" / "video"
    py = sys.executable
    force_flag = ["--force"] if args.force else []
    bank_path = args.bank
    segment_index_path = args.segment_index
    if not segment_index_path and (out_root / "segment_asset_index.json").exists():
        segment_index_path = str(out_root / "segment_asset_index.json")
    if not bank_path and args.assets_dir and not segment_index_path:
        ad = Path(args.assets_dir)
        default_index = (REPO_ROOT / ad) if not ad.is_absolute() else ad
        default_index = default_index / "index.json"
        if default_index.exists():
            bank_path = str(default_index)
    stages: list[dict] = []

    def run_stage(name: str, cmd: list[str]) -> bool:
        t0 = time.perf_counter()
        success = run(cmd, REPO_ROOT)
        t1 = time.perf_counter()
        stages.append({
            "name": name,
            "start_time": t0,
            "end_time": t1,
            "duration_ms": round((t1 - t0) * 1000),
            "success": success,
        })
        return success

    prepare_cmd = [py, str(scripts / "prepare_script_segments.py"), str(manifest_path), "-o", str(out_root / "script_segments.json"), "--content-type", content_type] + force_flag
    if not run_stage("prepare_script_segments", prepare_cmd):
        print("Failed: prepare_script_segments", file=sys.stderr)
        return 1
    print("OK: prepare_script_segments")

    # Script-aware scene/image generation is required for production coherence.
    if not args.segment_scenes:
        print("Failed: --segment-scenes is required in strict mode.", file=sys.stderr)
        return 1
    segment_topic = topic or "anxiety"
    repair_cfg_path = REPO_ROOT / "config" / "video" / "ei_v2_scene_repair.yaml"
    repair_cfg = {}
    if repair_cfg_path.exists():
        try:
            import yaml
            repair_cfg = yaml.safe_load(repair_cfg_path.read_text(encoding="utf-8")) or {}
        except Exception:
            repair_cfg = {}
    max_attempts = int(repair_cfg.get("max_attempts", 3))
    min_avg_alignment = float(repair_cfg.get("min_avg_alignment", 0.20))
    min_segment_alignment = float(repair_cfg.get("min_segment_alignment", 0.15))
    repair_note = ""
    scene_ok = False
    last_avg = 0.0
    last_per_seg: list[tuple[str, float]] = []
    for attempt in range(1, max_attempts + 1):
        scene_cmd = [
            py, str(scripts / "run_segment_scene_extraction.py"),
            str(out_root / "script_segments.json"),
            "-o", str(out_root / "segment_scenes.json"),
            "--topic", segment_topic,
            "--platform", args.platform,
        ]
        if repair_note:
            scene_cmd.extend(["--repair-note", repair_note])
        if run_stage(f"segment_scene_extraction_attempt_{attempt}", scene_cmd):
            last_avg, last_per_seg = _evaluate_scene_alignment(
                out_root / "script_segments.json",
                out_root / "segment_scenes.json",
            )
            weak = [sid for sid, sc in last_per_seg if sc < min_segment_alignment]
            if last_avg >= min_avg_alignment and not weak:
                scene_ok = True
                print(f"OK: segment_scene_extraction (attempt {attempt}, avg_alignment={last_avg:.3f})")
                _log_ei_scene_learning(
                    topic=segment_topic,
                    persona=persona,
                    slot="video_scene_generation",
                    success=True,
                    v1_id=f"attempt_1",
                    v2_id=f"attempt_{attempt}",
                    final_id=f"attempt_{attempt}",
                )
                break
            repair_note = (
                f"Prior attempt scene descriptions were too generic or weakly aligned. "
                f"Focus on concrete environment/action details for segments: {', '.join(weak[:6])}. "
                f"Use specific objects and actions from each segment."
            )
            print(
                f"Retrying scene extraction: avg_alignment={last_avg:.3f}, weak_segments={len(weak)}",
                file=sys.stderr,
            )
            continue
        repair_note = "Previous attempt failed. Return strict valid JSON for each segment and ensure concrete, filmable scenes."
    if not scene_ok:
        _log_ei_scene_learning(
            topic=segment_topic,
            persona=persona,
            slot="video_scene_generation",
            success=False,
            v1_id="attempt_1",
            v2_id=f"attempt_{max_attempts}",
            final_id="failed",
        )
        print(
            f"Failed: segment_scene_extraction after {max_attempts} attempts (avg_alignment={last_avg:.3f}).",
            file=sys.stderr,
        )
        return 1

    seg_img_cmd = [
        py, str(scripts / "run_flux_per_segment_build.py"),
        str(out_root / "segment_scenes.json"),
        "-o", str(out_root),
        "--topic", segment_topic,
    ] + force_flag
    if not run_stage("segment_image_build", seg_img_cmd):
        print("Failed: segment_image_build", file=sys.stderr)
        return 1
    print("OK: segment_image_build")
    segment_index_path = str(out_root / "segment_asset_index.json")
    try:
        idx = json.loads((out_root / "segment_asset_index.json").read_text(encoding="utf-8"))
        mapped = len((idx.get("segment_id_to_asset") or {}))
    except Exception:
        mapped = 0
    expected = 0
    try:
        segs = json.loads((out_root / "script_segments.json").read_text(encoding="utf-8"))
        expected = len(segs.get("segments", []))
    except Exception:
        expected = 0
    if mapped < max(1, expected):
        print(
            f"Failed: segment_image_build mapped {mapped}/{expected} segments in segment_asset_index.json",
            file=sys.stderr,
        )
        return 1

    resolver_cmd = [py, str(scripts / "run_asset_resolver.py"), str(out_root / "shot_plan.json"), "-o", str(out_root / "resolved_assets.json")] + force_flag
    if segment_index_path:
        resolver_cmd.extend(["--segment-index", str(segment_index_path)])
    elif bank_path:
        resolver_cmd.extend(["--bank", str(bank_path)])

    steps = [
        ([py, str(scripts / "run_shot_planner.py"), str(out_root / "script_segments.json"), "-o", str(out_root / "shot_plan.json"), "--content-type", content_type] + force_flag, "shot_planner"),
        (resolver_cmd, "asset_resolver"),
        ([py, str(scripts / "run_timeline_builder.py"), str(out_root / "shot_plan.json"), str(out_root / "resolved_assets.json"), "-o", str(out_root / "timeline.json")] + force_flag, "timeline_builder"),
        ([py, str(scripts / "run_caption_adapter.py"), str(out_root / "timeline.json"), str(out_root / "script_segments.json"), "-o", str(out_root / "captions.json")] + force_flag, "caption_adapter"),
        (
            [
                py, str(scripts / "run_qc.py"),
                str(out_root / "shot_plan.json"),
                str(out_root / "resolved_assets.json"),
                str(out_root / "timeline.json"),
                "-o", str(out_root / "qc_summary.json"),
                "--content-type", content_type,
                "--captions", str(out_root / "captions.json"),
                "--require-captions",
                "--max-placeholder-ratio", str(max(0.0, min(1.0, float(args.allow_placeholder_ratio)))),
                "--script-segments", str(out_root / "script_segments.json"),
                "--segment-scenes", str(out_root / "segment_scenes.json"),
            ],
            "qc",
        ),
    ]
    for cmd, name in steps:
        if not run_stage(name, cmd):
            print(f"Failed: {name}", file=sys.stderr)
            return 1
        print(f"OK: {name}")

    # --- Render step ---
    if args.run_render or not args.skip_render:
        render_cmd = [
            py, str(scripts / "run_render.py"),
            str(out_root / "timeline.json"),
            "-o", str(out_root),
            "--video-id", video_id,
            "--captions", str(out_root / "captions.json"),
            "--shot-plan", str(out_root / "shot_plan.json"),
            "--music-mood", "calm",
        ]
        render_assets = args.assets_dir
        if not render_assets and segment_index_path:
            # Segment index implies images in plan_dir/segment_images
            seg_index_dir = Path(segment_index_path).parent
            if (seg_index_dir / "segment_images").exists():
                render_assets = str(seg_index_dir / "segment_images")
        if not render_assets:
            print("Failed: no render assets available (segment_images missing and --assets-dir not set).", file=sys.stderr)
            return 1
        render_cmd.extend(["--assets-dir", str(render_assets)])
        if not run_stage("render", render_cmd):
            print("Failed: Render", file=sys.stderr)
            return 1
        print("OK: Render")
        rendered_video = out_root / "video.mp4"
        if not args.allow_silent_video and not has_audio_stream(rendered_video):
            print(f"Failed: render produced no audio stream ({rendered_video}).", file=sys.stderr)
            return 1

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
    if not run_stage("provenance", prov_cmd):
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
    if topic:
        meta_cmd.extend(["--topic", topic])
    if persona:
        meta_cmd.extend(["--persona", persona])
    if args.platform:
        meta_cmd.extend(["--platform", args.platform])
    if not run_stage("metadata", meta_cmd):
        print("Failed: Metadata Writer", file=sys.stderr)
        return 1
    print("OK: Metadata Writer")

    # Thumbnail generator (template card from title/topic; fallback: renderer frame-extract)
    if not args.skip_thumbnail:
        thumb_cmd = [
            py, str(scripts / "generate_thumbnail.py"),
            "--plan-id", args.plan_id,
        ]
        if force_flag:
            thumb_cmd.append("--force")
        if topic:
            thumb_cmd.extend(["--topic", topic])
        if persona:
            thumb_cmd.extend(["--persona", persona])
        if not run_stage("thumbnail", thumb_cmd):
            print("Warning: Thumbnail generator failed; distribution will use frame-extracted thumb if present", file=sys.stderr)
        else:
            print("OK: Thumbnail Generator")

    # Write pipeline_log.json (timing + pipeline_version)
    pipeline_log = {
        "pipeline_version": PIPELINE_VERSION,
        "plan_id": args.plan_id,
        "stages": stages,
    }
    write_atomically(out_root / "pipeline_log.json", pipeline_log)

    print(f"Pipeline complete. Outputs in {out_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
