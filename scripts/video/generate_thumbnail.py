#!/usr/bin/env python3
"""
Thumbnail Generator (Stage 11) — Produce template-card thumbnails for video handoff.

Design: Bold 2–4 word hook text + brand palette from hook band. No AI generation;
pure template rendering via Pillow. One thumb per format (16:9 / 9:16).

Fallback rule (deterministic precedence):
  1. Generated card (this script) — if run and passes validation
  2. Frame-extracted thumb (renderer FFmpeg grab) — if generator not run or fails
  3. No thumb — distribution writer proceeds without

Usage:
  python scripts/video/generate_thumbnail.py --plan-id <id>
  python scripts/video/generate_thumbnail.py --plan-id <id> --topic anxiety
  python scripts/video/generate_thumbnail.py --plan-id <id> --force --verbose

Authority: docs/VIDEO_PIPELINE_SPEC.md §10; config/video/thumbnail_templates.yaml, config/video/thumbnail_hook_phrases.yaml.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import load_json, load_yaml, write_atomically

logger = logging.getLogger("generate_thumbnail")

ARTIFACTS_VIDEO = REPO_ROOT / "artifacts" / "video"
THUMB_CONFIG_PATH = "config/video/thumbnail_templates.yaml"
THUMB_HOOK_PHRASES_PATH = "config/video/thumbnail_hook_phrases.yaml"
BRAND_TOKENS_PATH = "config/video/brand_style_tokens.yaml"
CHANNEL_THUMB_STYLES_PATH = "config/video/channel_thumbnail_styles.yaml"


# ─── Color utilities ──────────────────────────────────────────────────────────

def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' to (R, G, B)."""
    h = hex_str.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _relative_luminance(r: int, g: int, b: int) -> float:
    """WCAG relative luminance (0–1)."""
    def _linearize(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def _contrast_ratio(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    """WCAG contrast ratio between two colors."""
    l1 = _relative_luminance(*rgb1)
    l2 = _relative_luminance(*rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ─── Validation ───────────────────────────────────────────────────────────────

def _validate_thumbnail(
    img_path: Path,
    target_w: int,
    target_h: int,
    text_rgb: tuple[int, int, int],
    bg_rgb: tuple[int, int, int],
    hook_text: str,
    config: dict,
) -> tuple[bool, str]:
    """Validate generated thumbnail. Returns (ok, reason)."""
    try:
        from PIL import Image
    except ImportError:
        return False, "Pillow not installed"

    if not img_path.exists():
        return False, "thumbnail file not found"

    img = Image.open(img_path)
    w, h = img.size
    tol = config.get("validation", {}).get("resolution_tolerance_px", 1)
    if abs(w - target_w) > tol or abs(h - target_h) > tol:
        return False, f"resolution mismatch: got {w}x{h}, expected {target_w}x{target_h}"

    # Contrast check
    min_contrast = config.get("validation", {}).get("min_contrast_ratio", 3.0)
    cr = _contrast_ratio(text_rgb, bg_rgb)
    if cr < min_contrast:
        return False, f"contrast ratio {cr:.2f} below minimum {min_contrast}"

    # Word count check
    words = hook_text.strip().split()
    min_words = config.get("validation", {}).get("min_words", 2)
    max_words = config.get("validation", {}).get("max_words", 6)
    if len(words) < min_words:
        return False, f"hook text too short: {len(words)} words (min {min_words})"
    if len(words) > max_words:
        return False, f"hook text too long: {len(words)} words (max {max_words})"

    return True, "ok"


# ─── Thumbnail rendering ─────────────────────────────────────────────────────

def _resolve_font(font_families: list[str], font_size: int):
    """Try each font family until one loads. Returns a Pillow ImageFont."""
    from PIL import ImageFont

    for family in font_families:
        # Try as truetype path first
        for path_pattern in (
            f"/usr/share/fonts/truetype/**/{family.replace(' ', '')}*.ttf",
            f"/usr/share/fonts/truetype/**/{family.replace(' ', '').lower()}*.ttf",
            f"/usr/local/share/fonts/{family.replace(' ', '')}*.ttf",
            f"/System/Library/Fonts/{family.replace(' ', '')}*.ttf",
        ):
            import glob
            matches = glob.glob(path_pattern, recursive=True)
            if matches:
                try:
                    return ImageFont.truetype(matches[0], font_size)
                except Exception:
                    continue
        # Try as system name
        try:
            return ImageFont.truetype(family, font_size)
        except Exception:
            continue

    # Final fallback: default bitmap font (Pillow built-in)
    logger.warning("No custom fonts found; using Pillow default")
    return ImageFont.load_default()


def _render_card(
    width: int,
    height: int,
    hook_text: str,
    bg_hex: str,
    text_hex: str,
    accent_hex: str,
    config: dict,
    out_path: Path,
) -> Path:
    """Render a template-card thumbnail to out_path using Pillow."""
    from PIL import Image, ImageDraw

    bg_rgb = _hex_to_rgb(bg_hex)
    text_rgb = _hex_to_rgb(text_hex)
    accent_rgb = _hex_to_rgb(accent_hex)

    img = Image.new("RGB", (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)

    # Typography config
    typo = config.get("typography", {})
    font_size_ratio = typo.get("font_size_ratio", 0.08)
    font_size = int(height * font_size_ratio)
    line_spacing = typo.get("line_spacing", 1.2)
    text_y_frac = typo.get("text_position_y", 0.45)
    font_families = typo.get("font_families", ["DejaVu Sans Bold"])

    font = _resolve_font(font_families, font_size)

    # Accent bar (top stripe)
    bar_height = max(int(height * 0.015), 4)
    draw.rectangle([0, 0, width, bar_height], fill=accent_rgb)

    # Bottom accent bar
    draw.rectangle([0, height - bar_height, width, height], fill=accent_rgb)

    # Draw hook text centered
    lines = hook_text.upper().strip().split("\n")
    # If single line, split into 2 lines if > 3 words for visual impact
    if len(lines) == 1:
        words = lines[0].split()
        if len(words) > 3:
            mid = len(words) // 2
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    total_text_height = len(lines) * font_size * line_spacing
    start_y = int(height * text_y_frac - total_text_height / 2)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2
        y = start_y + int(i * font_size * line_spacing)
        draw.text((x, y), line, fill=text_rgb, font=font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), "JPEG", quality=92)
    return out_path


# ─── Main logic ───────────────────────────────────────────────────────────────

def _resolve_hook_text(topic: str | None, title: str, config: dict) -> str:
    """Pick hook phrase from thumbnail_hook_phrases.yaml (topic_to_hook_phrase), fall back to title truncation."""
    phrases_cfg = load_yaml(THUMB_HOOK_PHRASES_PATH)
    topic_map = phrases_cfg.get("topic_to_hook_phrase", {})
    if topic and topic in topic_map:
        return topic_map[topic]
    if "default" in topic_map:
        return topic_map["default"]
    # Truncate title to max_words
    max_words = config.get("validation", {}).get("max_words", 6)
    words = title.split()[:max_words]
    return " ".join(words) if words else "Feel Better Now"


def _get_palette(brand_tokens: dict, channel_id: str | None = None) -> dict:
    """Get thumbnail palette. Per-channel palette if channel_id given (anti-spam); else shared hook band."""
    # Per-channel palette takes priority (anti-spam: each channel MUST look different)
    if channel_id:
        ch_styles = load_yaml(CHANNEL_THUMB_STYLES_PATH)
        ch = ch_styles.get(channel_id)
        if ch:
            return {
                "bg": ch.get("bg_hex", "#1A1714"),
                "text": ch.get("text_hex", "#F5C842"),
                "accent": ch.get("accent_hex", "#F0A500"),
            }
        logger.warning("channel_id=%s not in channel_thumbnail_styles; falling back to hook band", channel_id)

    # Fallback: shared hook band palette
    hook_spec = brand_tokens.get("bands", {}).get("hook", {}).get("spec", {})
    return {
        "bg": hook_spec.get("thumbnail_bg", "#1A1714"),
        "text": hook_spec.get("title_color", "#F5C842"),
        "accent": hook_spec.get("accent", "#F0A500"),
    }


def _format_to_config_key(fmt: str) -> str:
    """Map distribution_manifest format to config key."""
    mapping = {
        "landscape_16_9": "landscape_16_9",
        "16:9": "landscape_16_9",
        "portrait_9_16": "portrait_9_16",
        "9:16": "portrait_9_16",
        "square_1_1": "square_1_1",
        "1:1": "square_1_1",
    }
    return mapping.get(fmt, "landscape_16_9")


def generate_for_plan(
    plan_id: str,
    topic: str | None = None,
    persona: str | None = None,
    channel_id: str | None = None,
    force: bool = False,
) -> dict:
    """Generate thumbnails for a plan. Returns thumb_provenance dict."""
    config = load_yaml(THUMB_CONFIG_PATH)
    brand_tokens = load_yaml(BRAND_TOKENS_PATH)
    palette = _get_palette(brand_tokens, channel_id=channel_id)

    plan_dir = ARTIFACTS_VIDEO / plan_id
    manifest_path = plan_dir / "distribution_manifest.json"

    if not manifest_path.exists():
        logger.warning("No distribution_manifest.json for plan %s — skipping", plan_id)
        return {"plan_id": plan_id, "source": "none", "reason": "no manifest"}

    manifest = load_json(manifest_path)
    title = manifest.get("title", "")
    fmt = manifest.get("format", "landscape_16_9")
    manifest_topic = manifest.get("topic", topic)

    # Resolve hook text
    hook_text = _resolve_hook_text(manifest_topic, title, config)
    logger.info("plan=%s topic=%s hook='%s'", plan_id, manifest_topic, hook_text)

    # Resolve format → dimensions
    fmt_key = _format_to_config_key(fmt)
    fmt_config = config.get("formats", {}).get(fmt_key, {})
    width = fmt_config.get("width", 1280)
    height = fmt_config.get("height", 720)
    thumb_filename = fmt_config.get("thumb_filename", "thumb_16x9.jpg")

    out_path = plan_dir / thumb_filename

    if out_path.exists() and not force:
        logger.info("  thumb already exists: %s (use --force to regenerate)", out_path)
        return {"plan_id": plan_id, "source": "generated", "thumb_file": thumb_filename, "reason": "already exists"}

    # Render
    try:
        _render_card(
            width=width,
            height=height,
            hook_text=hook_text,
            bg_hex=palette["bg"],
            text_hex=palette["text"],
            accent_hex=palette["accent"],
            config=config,
            out_path=out_path,
        )
    except ImportError:
        logger.error("Pillow not installed — falling back to frame-extracted thumb")
        return {"plan_id": plan_id, "source": "frame_extracted", "reason": "pillow_not_installed"}
    except Exception as e:
        logger.error("Render failed: %s — falling back to frame-extracted thumb", e)
        return {"plan_id": plan_id, "source": "frame_extracted", "reason": f"render_error: {e}"}

    # Validate
    bg_rgb = _hex_to_rgb(palette["bg"])
    text_rgb = _hex_to_rgb(palette["text"])
    ok, reason = _validate_thumbnail(out_path, width, height, text_rgb, bg_rgb, hook_text, config)
    if not ok:
        logger.warning("  validation failed: %s — falling back to frame-extracted thumb", reason)
        # Remove the bad generated thumb so frame-extract is used
        out_path.unlink(missing_ok=True)
        return {
            "plan_id": plan_id,
            "source": "frame_extracted",
            "reason": f"validation_failed: {reason}",
            "attempted_hook": hook_text,
        }

    logger.info("  generated %s (%dx%d) channel=%s", out_path.name, width, height, channel_id or "shared")
    return {
        "plan_id": plan_id,
        "channel_id": channel_id or "shared_hook_band",
        "source": "generated",
        "thumb_file": thumb_filename,
        "hook_text": hook_text,
        "resolution": f"{width}x{height}",
        "palette_bg": palette["bg"],
        "palette_text": palette["text"],
        "palette_accent": palette["accent"],
    }


def main():
    parser = argparse.ArgumentParser(description="Thumbnail Generator — template card for video handoff")
    parser.add_argument("--plan-id", required=True, help="Plan ID (directory under artifacts/video/)")
    parser.add_argument("--channel-id", default=None, help="Channel ID (e.g. ch_001) for per-brand thumbnail palette")
    parser.add_argument("--topic", default=None, help="Topic for hook phrase selection (e.g. anxiety, burnout)")
    parser.add_argument("--persona", default=None, help="Persona (reserved for future template variants)")
    parser.add_argument("--force", action="store_true", help="Regenerate even if thumb already exists")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    provenance = generate_for_plan(
        plan_id=args.plan_id,
        topic=args.topic,
        persona=args.persona,
        channel_id=args.channel_id,
        force=args.force,
    )

    # Write thumb provenance
    prov_path = ARTIFACTS_VIDEO / args.plan_id / "thumb_provenance.json"
    write_atomically(prov_path, provenance)
    logger.info("Wrote %s", prov_path)

    if provenance.get("source") == "generated":
        logger.info("=== Thumbnail generated successfully ===")
    else:
        logger.info("=== Fallback to %s: %s ===", provenance.get("source"), provenance.get("reason"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
