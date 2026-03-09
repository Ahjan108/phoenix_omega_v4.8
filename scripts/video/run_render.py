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
import shutil
import subprocess
import sys
import tempfile
import textwrap
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
        # FFmpeg drawtext: escape backslash then single-quote (see drawtext doc)
        escaped = caption_text.replace("\\", "\\\\").replace("'", "\\'")
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


def _ffmpeg_has_drawtext() -> bool:
    """True if this FFmpeg build includes the drawtext filter (often missing without libfreetype)."""
    try:
        r = subprocess.run(
            [get_ffmpeg_bin(), "-filters"],
            capture_output=True,
            timeout=5,
            text=True,
        )
        return r.returncode == 0 and "drawtext" in (r.stdout or "")
    except Exception:
        return False


def _burn_caption_to_image(image_path: Path, out_path: Path, caption_text: str) -> bool:
    """Fallback caption path when FFmpeg drawtext is unavailable: burn caption onto source image with Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except ImportError:
        return False
    try:
        img = Image.open(image_path).convert("RGB")
        # Normalize to renderer working resolution so motion/crop stays stable.
        resampling = getattr(Image, "Resampling", Image)
        img = ImageOps.fit(img, (SCALE_W, SCALE_H), method=resampling.LANCZOS)
        canvas = img.convert("RGBA")
        draw = ImageDraw.Draw(canvas, "RGBA")
        box_h = int(SCALE_H * 0.24)
        draw.rectangle([(0, SCALE_H - box_h), (SCALE_W, SCALE_H)], fill=(0, 0, 0, 110))

        font_size = 52
        font = ImageFont.load_default()
        for font_path in (
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ):
            if Path(font_path).exists():
                try:
                    font = ImageFont.truetype(font_path, size=font_size)
                    break
                except Exception:
                    pass

        wrapped = "\n".join(textwrap.wrap(caption_text.strip(), width=34)[:3])
        text_x = int(SCALE_W * 0.08)
        text_y = SCALE_H - box_h + int(box_h * 0.22)
        # Stroke keeps readability over bright images.
        draw.text(
            (text_x, text_y),
            wrapped,
            fill=(255, 255, 255, 245),
            font=font,
            stroke_width=2,
            stroke_fill=(0, 0, 0, 220),
            spacing=8,
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out_path, "PNG")
        return out_path.exists()
    except Exception:
        return False


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


def _mix_background_music(
    video_in: Path,
    video_out: Path,
    duration_s: float,
    music_track: Path | None,
    music_mood: str,
) -> bool:
    """Attach background music/ambience track to rendered video."""
    ffmpeg = get_ffmpeg_bin()
    duration_s = max(0.1, float(duration_s))
    fade_d = max(0.5, min(2.5, duration_s * 0.05))
    fade_out_st = max(0.0, duration_s - fade_d)

    if music_track and music_track.exists():
        cmd = [
            ffmpeg, "-y",
            "-i", str(video_in),
            "-stream_loop", "-1", "-i", str(music_track),
            "-filter_complex",
            f"[1:a]volume=0.13,atrim=0:{duration_s},afade=t=in:st=0:d={fade_d},afade=t=out:st={fade_out_st}:d={fade_d}[bg]",
            "-map", "0:v", "-map", "[bg]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
            str(video_out),
        ]
    else:
        # Fallback ambient bed when no music file is provided.
        color = "pink"
        amp = "0.018"
        if music_mood.strip().lower() in {"tense", "urgent"}:
            amp = "0.024"
        cmd = [
            ffmpeg, "-y",
            "-i", str(video_in),
            "-f", "lavfi", "-t", str(duration_s), "-i", f"anoisesrc=color={color}:amplitude={amp}:sample_rate=48000",
            "-filter_complex",
            f"[1:a]lowpass=f=1300,highpass=f=80,volume=0.20,afade=t=in:st=0:d={fade_d},afade=t=out:st={fade_out_st}:d={fade_d}[bg]",
            "-map", "0:v", "-map", "[bg]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
            str(video_out),
        ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return video_out.exists()
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(e.stderr.decode("utf-8", errors="ignore"), file=sys.stderr)
        return False


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


def _write_placeholder_frame_image(frame_path: Path, width: int, height: int, duration_s: float) -> bool:
    """Draw one frame with visible 'PLACEHOLDER' label; used when FFmpeg has no drawtext. Returns True if Pillow succeeded."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    img = Image.new("RGB", (width, height), color=(0x33, 0x33, 0x44))  # dark blue-gray
    draw = ImageDraw.Draw(img)
    label = f"PLACEHOLDER  {duration_s:.0f}s  {width}x{height}"
    font_size = min(72, width // 20)
    font = ImageFont.load_default()
    for font_path in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        if Path(font_path).exists():
            try:
                font = ImageFont.truetype(font_path, size=font_size)
                break
            except Exception:
                pass
    try:
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        tw, th = draw.textsize(label, font=font)  # Pillow < 8
    x = (width - tw) // 2
    y = (height - th) // 2
    draw.text((x, y), label, fill="white", font=font)
    img.save(str(frame_path), "PNG")
    return frame_path.exists()


def _write_placeholder_video(
    video_path: Path,
    thumb_path: Path,
    width: int,
    height: int,
    duration_s: float,
    fps: int,
) -> bool:
    """Write a minimal playable MP4 (silent, visible frame with label) and one-frame thumb. Returns True if FFmpeg succeeded."""
    try:
        ffmpeg = get_ffmpeg_bin()
    except Exception:
        return False
    duration_s = max(0.1, min(float(duration_s), 600.0))
    width = max(1, int(width))
    height = max(1, int(height))
    fps = max(1, int(fps))
    tmp_frame = video_path.parent / "_place_frame.png"
    use_image = _write_placeholder_frame_image(tmp_frame, width, height, duration_s)

    try:
        if use_image and tmp_frame.exists():
            # Encode one image as video for full duration (loop frame)
            cmd_video = [
                ffmpeg, "-y", "-loop", "1", "-i", str(tmp_frame),
                "-t", str(duration_s), "-r", str(fps),
                "-pix_fmt", "yuv420p", "-c:v", "libx264", "-vf", f"scale={width}:{height}",
                str(video_path),
            ]
        else:
            # Fallback: visible gray (0x333344) so QA sees something even without Pillow
            cmd_video = [
                ffmpeg, "-y",
                "-f", "lavfi", "-i", f"color=c=0x333344:s={width}x{height}:d={duration_s}:r={fps}",
                "-t", str(duration_s),
                "-pix_fmt", "yuv420p", "-c:v", "libx264", "-r", str(fps),
                str(video_path),
            ]
        result = subprocess.run(cmd_video, capture_output=True, timeout=120, text=True)
        if tmp_frame.exists():
            tmp_frame.unlink(missing_ok=True)
        if result.returncode != 0 or not video_path.exists():
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return False
        cmd_thumb = [
            ffmpeg, "-y", "-ss", "0", "-i", str(video_path), "-frames:v", "1", str(thumb_path),
        ]
        thumb_result = subprocess.run(cmd_thumb, capture_output=True, timeout=10, text=True)
        if thumb_result.returncode != 0 and thumb_result.stderr:
            print(thumb_result.stderr, file=sys.stderr)
        return video_path.exists() and thumb_path.exists()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        if tmp_frame.exists():
            tmp_frame.unlink(missing_ok=True)
        print(f"Placeholder FFmpeg error: {e}", file=sys.stderr)
        return False


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
    ap.add_argument("--music-track", default=None, help="Optional music file path (.wav/.mp3) to mix under video")
    ap.add_argument("--music-mood", default="calm", help="Music mood label (used for fallback ambience profile)")
    ap.add_argument("--no-music", action="store_true", help="Disable music/ambience mix and keep silent video")
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
        video_path = out_dir / "video.mp4"
        thumb_path = out_dir / "thumb.jpg"
        duration_s = timeline.get("duration_s", 1.0)
        fps = timeline.get("fps", FPS_DEFAULT)
        if _write_placeholder_video(video_path, thumb_path, output_w, output_h, duration_s, fps):
            ref = {"timeline_path": str(tl_path), "video_path": str(video_path), "thumbnail_path": str(thumb_path)}
            (out_dir / "timeline_ref.json").write_text(json.dumps(ref, indent=2), encoding="utf-8")
            print(f"Placeholder: {video_path} (playable {duration_s}s silent video)")
            return 0
        # Do not write a text file as .mp4 — that produces a "blank" unplayable file. Fail visibly.
        print("Placeholder render failed: no playable video written. Install FFmpeg (e.g. brew install ffmpeg) and ensure libx264 is available.", file=sys.stderr)
        return 1

    assets_dir = Path(args.assets_dir)
    clips = timeline.get("clips", [])
    if not clips:
        print("No clips in timeline", file=sys.stderr)
        return 1

    use_captions = _ffmpeg_has_drawtext()
    if not use_captions and captions_by_ref:
        print("Note: FFmpeg has no drawtext filter; using Pillow caption-burn fallback.", file=sys.stderr)
    clip_files: list[Path] = []
    caption_burn_files: list[Path] = []
    for i, clip in enumerate(clips):
        asset_id = clip.get("asset_id")
        if not asset_id:
            continue
        start_s = clip.get("start_time_s", 0)
        end_s = clip.get("end_time_s", start_s + 5)  # end_time_s is end timestamp, not duration
        duration_s = end_s - start_s  # clip duration in seconds
        if duration_s <= 0:
            continue

        image_path = assets_dir / f"{asset_id}.jpg"
        if not image_path.exists():
            image_path = assets_dir / f"{asset_id}.png"
        if not image_path.exists():
            # Keep timeline continuity: if asset is missing, render a visible fallback frame for this clip.
            missing_path = out_dir / f"_missing_{i:04d}.png"
            ok = _write_placeholder_frame_image(missing_path, SCALE_W, SCALE_H, duration_s)
            if not ok:
                print(f"Warning: asset not found {asset_id}, skipping clip", file=sys.stderr)
                continue
            image_path = missing_path
            caption_burn_files.append(missing_path)

        motion_type = motion_by_shot.get(clip.get("shot_id", ""), clip.get("motion", "static"))
        caption_ref = clip.get("caption_ref", "")
        caption_text = (captions_by_ref.get(caption_ref) if caption_ref else None) if use_captions else None
        if not use_captions and captions_by_ref and caption_ref:
            raw_caption = captions_by_ref.get(caption_ref)
            if raw_caption:
                burn_path = out_dir / f"_capburn_{i:04d}.png"
                if _burn_caption_to_image(image_path, burn_path, raw_caption):
                    image_path = burn_path
                    caption_burn_files.append(burn_path)
                else:
                    print(f"Warning: caption fallback burn failed for {caption_ref}", file=sys.stderr)
        out_clip = out_dir / f"clip_{i:04d}.mp4"
        _render_clip(
            image_path, out_clip, video_id, i, duration_s, motion_type, grade,
            caption_text, caption_x, caption_y, fps, output_w, output_h, margin_pct,
        )
        clip_files.append(out_clip)

    if not clip_files:
        print("No clips rendered", file=sys.stderr)
        return 1

    video_silent_path = out_dir / "video_silent.mp4"
    video_path = out_dir / "video.mp4"
    _concat_clips(clip_files, video_silent_path)
    for f in clip_files:
        f.unlink(missing_ok=True)
    for f in caption_burn_files:
        f.unlink(missing_ok=True)

    if args.no_music:
        video_path.unlink(missing_ok=True)
        shutil.move(str(video_silent_path), str(video_path))
    else:
        music_track_path = Path(args.music_track) if args.music_track else None
        if not _mix_background_music(video_silent_path, video_path, timeline.get("duration_s", 1.0), music_track_path, args.music_mood):
            print("Warning: audio mix failed; using silent video", file=sys.stderr)
            video_path.unlink(missing_ok=True)
            shutil.move(str(video_silent_path), str(video_path))
        else:
            video_silent_path.unlink(missing_ok=True)

    thumb_ref = timeline.get("thumbnail_frame_ref")
    ts = _timestamp_from_thumbnail_ref(timeline, thumb_ref, fps)
    thumb_path = out_dir / "thumb.jpg"
    _extract_thumbnail(video_path, ts, thumb_path)

    ref = {"timeline_path": str(tl_path), "video_path": str(video_path), "thumbnail_path": str(thumb_path)}
    (out_dir / "timeline_ref.json").write_text(json.dumps(ref, indent=2), encoding="utf-8")
    print(f"Rendered: {video_path} (thumb: {thumb_path})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
