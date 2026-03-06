#!/usr/bin/env python3
"""
Renderer: timeline + assets + captions -> video file (FFmpeg).
Reads real timeline schema: plan_id, clips[] (asset_id, start_time_s, end_time_s, caption_ref).
video_id comes from args (provenance/distribution); plan_id used for output naming and seed when video_id not set.
Loads color presets from config/video/color_grade_presets.yaml and crop margin from config/video/render_params.yaml.
Optional: --shot-plan for motion per clip, --captions for caption text. Concat demuxer (hard cuts). Thumbnail from thumbnail_frame_ref.
Usage: python scripts/video/run_render.py <timeline.json> -o <output_dir> [--assets-dir DIR] [--captions captions.json] [--shot-plan shot_plan.json] [--video-id ID] [--placeholder]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import get_ffmpeg_bin, load_yaml, load_json, REPO_ROOT

# Default output size for 9:16 shorts; override from timeline resolution if present
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
FPS_DEFAULT = 24
# Scale before crop (slightly larger so crop has headroom)
SCALE_W = 1200
SCALE_H = 2133


def _deterministic_seed(video_id: str, shot_index: int) -> int:
    key = f"{video_id}_{shot_index}".encode()
    return int(hashlib.sha256(key).hexdigest(), 16)


def _crop_params(seed: int, width: int, height: int, margin_pct: float) -> tuple[float, int, int]:
    """Crop zoom and offsets; offsets bounded by crop_margin_pct so we don't clip the subject."""
    zoom = 0.92 + (seed % 80) / 1000.0
    margin = margin_pct / 100.0
    max_off_x = int(width * (1 - zoom) * margin)
    max_off_y = int(height * (1 - zoom) * margin)
    crop_x = seed % max(1, max_off_x)
    crop_y = (seed // 10) % max(1, max_off_y)
    return zoom, crop_x, crop_y


def _motion_expr(motion_type: str) -> tuple[str, str | None, str | None]:
    """zoompan z (and optionally x,y for pan). Always init zoom on frame 0 to avoid undefined state.
    Returns (z_expr, x_expr or None, y_expr or None). For slow_pan, x/y are full key=value e.g. x='...'.
    FFmpeg zoompan is picky about quoting and parameter order — verify with a real slow_pan render if needed."""
    motion = (motion_type or "static").strip().lower()
    if motion == "static":
        return "z='1'", None, None
    if motion in ("slow_zoom_in", "slow_zoom"):
        return "z='if(eq(on,0),1.0,min(zoom+0.00023,1.08))'", None, None
    if motion == "slow_zoom_out":
        return "z='if(eq(on,0),1.0,max(zoom-0.00023,0.92))'", None, None
    if motion == "slow_pan":
        return "z='1'", "x='iw/2-(iw/zoom/2)+sin(on/50)*10'", "y='ih/2-(ih/zoom/2)'"
    return "z='1'", None, None


def _build_filter_chain(
    zoom: float,
    crop_x: int,
    crop_y: int,
    frames: int,
    motion_z: str,
    motion_x: str | None,
    motion_y: str | None,
    eq_preset: dict,
    output_w: int,
    output_h: int,
    caption_text: str | None,
    caption_x: str,
    caption_y: str,
    drawbox: bool = True,
) -> str:
    crop = f"crop=iw*{zoom}:ih*{zoom}:{crop_x}:{crop_y}"
    zoompan = f"zoompan={motion_z}:d={frames}:s={output_w}x{output_h}"
    if motion_x is not None and motion_y is not None:
        zoompan = f"zoompan={motion_z}:{motion_x}:{motion_y}:d={frames}:s={output_w}x{output_h}"
    eq = f"eq=contrast={eq_preset.get('contrast', 1.0)}:brightness={eq_preset.get('brightness', 0)}:saturation={eq_preset.get('saturation', 1.0)}"
    filters = [
        f"scale={SCALE_W}:{SCALE_H}",
        crop,
        zoompan,
        eq,
        "format=yuv420p",
    ]
    if drawbox and caption_text:
        filters.append("drawbox=x=0:y=h*0.75:w=iw:h=h*0.25:color=black@0.35:t=fill")
    if caption_text:
        escaped = caption_text.replace("\\", "\\\\").replace("'", "'\\\\''")
        filters.append(
            f"drawtext=text='{escaped}':fontsize=64:fontcolor=white:x={caption_x}:y={caption_y}:"
            "shadowcolor=black:shadowx=2:shadowy=2:line_spacing=8"
        )
    return ",".join(filters)


def _render_clip(
    image_path: Path,
    output_path: Path,
    video_id: str,
    shot_index: int,
    duration_s: float,
    motion_type: str,
    grade: dict,
    caption_text: str | None,
    caption_x: str,
    caption_y: str,
    fps: int,
    output_w: int,
    output_h: int,
    margin_pct: float,
) -> None:
    seed = _deterministic_seed(video_id, shot_index)
    zoom, crop_x, crop_y = _crop_params(seed, SCALE_W, SCALE_H, margin_pct)
    frames = int(round(duration_s * fps))
    motion_z, motion_x, motion_y = _motion_expr(motion_type)
    filter_complex = _build_filter_chain(
        zoom, crop_x, crop_y, frames, motion_z, motion_x, motion_y,
        grade, output_w, output_h, caption_text, caption_x, caption_y, drawbox=True,
    )
    cmd = [
        get_ffmpeg_bin(), "-y", "-loop", "1", "-i", str(image_path),
        "-filter_complex", filter_complex,
        "-t", str(duration_s), "-r", str(fps),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _concat_clips(clip_paths: list[Path], out_path: Path) -> None:
    """Concat demuxer (hard cuts, no re-encode)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in clip_paths:
            f.write(f"file '{p.absolute()}'\n")
        list_path = Path(f.name)
    try:
        subprocess.run(
            [get_ffmpeg_bin(), "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(out_path)],
            check=True, capture_output=True,
        )
    finally:
        list_path.unlink(missing_ok=True)


def _extract_thumbnail(video_path: Path, timestamp_s: float, thumb_path: Path) -> None:
    subprocess.run(
        [get_ffmpeg_bin(), "-y", "-ss", str(timestamp_s), "-i", str(video_path), "-frames:v", "1", str(thumb_path)],
        check=True, capture_output=True,
    )


def _timestamp_from_thumbnail_ref(timeline: dict, thumbnail_ref: dict | None, fps: int) -> float:
    """Map thumbnail_frame_ref (shot_id, frame_offset) to seconds into the video."""
    if not thumbnail_ref:
        return 0.0
    shot_id = thumbnail_ref.get("shot_id")
    frame_offset = thumbnail_ref.get("frame_offset", 0)
    for clip in timeline.get("clips", []):
        if clip.get("shot_id") == shot_id:
            start_s = clip.get("start_time_s", 0)
            return start_s + (frame_offset / fps)
    return 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description="Render timeline to video (FFmpeg) or placeholder")
    ap.add_argument("timeline", help="Path to timeline.json")
    ap.add_argument("-o", "--out-dir", required=True, help="Output directory for video, thumb, timeline_ref")
    ap.add_argument("--assets-dir", default=None, help="Directory with image assets; asset_id maps to <assets_dir>/<asset_id>.jpg")
    ap.add_argument("--captions", default=None, help="Path to captions.json (segment_id -> text)")
    ap.add_argument("--shot-plan", default=None, help="Path to shot_plan.json for motion per shot_id (prompt_bundle.motion)")
    ap.add_argument("--video-id", default=None, help="Video ID for deterministic seed and provenance (default: plan_id)")
    ap.add_argument("--color-grade", default=None, help="Color preset name (default: from config default_preset)")
    ap.add_argument("--placeholder", action="store_true", help="Write placeholder only, no FFmpeg")
    args = ap.parse_args()

    tl_path = Path(args.timeline)
    if not tl_path.exists():
        print(f"Error: not found: {tl_path}", file=sys.stderr)
        return 1
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timeline = load_json(tl_path)
    plan_id = timeline.get("plan_id", "unknown")
    video_id = args.video_id or plan_id

    # Config: color presets and crop margin
    color_cfg = load_yaml("config/video/color_grade_presets.yaml")
    presets = (color_cfg.get("presets") or {})
    default_preset_name = color_cfg.get("default_preset", "neutral")
    grade_name = args.color_grade or default_preset_name
    grade = presets.get(grade_name) or presets.get("neutral") or {"contrast": 1.0, "brightness": 0.0, "saturation": 1.0}

    render_cfg = load_yaml("config/video/render_params.yaml")
    margin_pct = float(render_cfg.get("crop_margin_pct", 6))

    resolution = timeline.get("resolution") or {}
    output_w = resolution.get("width", DEFAULT_WIDTH)
    output_h = resolution.get("height", DEFAULT_HEIGHT)
    fps = timeline.get("fps", FPS_DEFAULT)

    # Motion per shot_id from shot_plan if provided
    motion_by_shot: dict[str, str] = {}
    if args.shot_plan and Path(args.shot_plan).exists():
        shot_plan = load_json(Path(args.shot_plan))
        for shot in shot_plan.get("shots", []):
            pb = shot.get("prompt_bundle") or {}
            motion_by_shot[shot["shot_id"]] = pb.get("motion", "static")

    # Caption text per segment from captions.json if provided
    captions_by_ref: dict[str, str] = {}
    if args.captions and Path(args.captions).exists():
        captions_data = load_json(Path(args.captions))
        for seg_id, obj in (captions_data.get("captions") or {}).items():
            if isinstance(obj, dict) and "text" in obj:
                captions_by_ref[seg_id] = obj["text"]
            elif isinstance(obj, str):
                captions_by_ref[seg_id] = obj

    # Default caption position (bottom center; spec contrast >= 4.5 with drawbox)
    caption_x, caption_y = "(w-text_w)/2", "h*0.82"

    if args.placeholder or not args.assets_dir:
        video_path = out_dir / f"{plan_id}.mp4"
        thumb_path = out_dir / "thumb.jpg"
        video_path.write_text("placeholder\n", encoding="utf-8")
        thumb_path.write_text("placeholder\n", encoding="utf-8")
        ref = {"timeline_path": str(tl_path), "video_path": str(video_path), "thumbnail_path": str(thumb_path)}
        (out_dir / "timeline_ref.json").write_text(json.dumps(ref, indent=2), encoding="utf-8")
        print(f"Placeholder: {video_path} (no FFmpeg)")
        return 0

    assets_dir = Path(args.assets_dir)
    clips = timeline.get("clips", [])
    if not clips:
        print("No clips in timeline", file=sys.stderr)
        return 1

    clip_files: list[Path] = []
    for i, clip in enumerate(clips):
        asset_id = clip.get("asset_id")
        if not asset_id:
            continue
        image_path = assets_dir / f"{asset_id}.jpg"
        if not image_path.exists():
            image_path = assets_dir / f"{asset_id}.png"
        if not image_path.exists():
            print(f"Warning: asset not found {asset_id}, skipping clip", file=sys.stderr)
            continue
        start_s = clip.get("start_time_s", 0)
        end_s = clip.get("end_time_s", start_s + 5)  # end_time_s is end timestamp, not duration
        duration_s = end_s - start_s  # clip duration in seconds
        if duration_s <= 0:
            continue
        motion_type = motion_by_shot.get(clip.get("shot_id", ""), clip.get("motion", "static"))
        caption_ref = clip.get("caption_ref", "")
        caption_text = captions_by_ref.get(caption_ref) if caption_ref else None
        out_clip = out_dir / f"clip_{i:04d}.mp4"
        _render_clip(
            image_path, out_clip, video_id, i, duration_s, motion_type, grade,
            caption_text, caption_x, caption_y, fps, output_w, output_h, margin_pct,
        )
        clip_files.append(out_clip)

    if not clip_files:
        print("No clips rendered", file=sys.stderr)
        return 1

    video_path = out_dir / f"{plan_id}.mp4"
    _concat_clips(clip_files, video_path)
    for f in clip_files:
        f.unlink(missing_ok=True)

    thumb_ref = timeline.get("thumbnail_frame_ref")
    ts = _timestamp_from_thumbnail_ref(timeline, thumb_ref, fps)
    thumb_path = out_dir / "thumb.jpg"
    _extract_thumbnail(video_path, ts, thumb_path)

    ref = {"timeline_path": str(tl_path), "video_path": str(video_path), "thumbnail_path": str(thumb_path)}
    (out_dir / "timeline_ref.json").write_text(json.dumps(ref, indent=2), encoding="utf-8")
    print(f"Rendered: {video_path} (thumb: {thumb_path})")

    # TODO: Audio — timeline.audio_tracks has narration and music with duck_under. After concat,
    # mix narration + music (ducking) with the video in a separate FFmpeg pass or filter graph.
    # This is the hardest part of the renderer; Phase 1 is video-only (silent).

    return 0


if __name__ == "__main__":
    sys.exit(main())
