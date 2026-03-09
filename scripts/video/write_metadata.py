#!/usr/bin/env python3
"""
Metadata Writer: produces distribution_manifest.json with title, description, tags,
telemetry (hook_type, etc.), primary_asset_ids, and platform-specific SEO metadata.

Channel-aware: when --channel-id is given, loads per-channel writing style
(config/video/channel_writing_styles.yaml) and platform SEO policies
(config/video/platform_seo_policies.yaml) to produce unique, anti-spam metadata.

Usage:
  python scripts/video/write_metadata.py --video-id <id> --plan-id <id> --title <t> --description <d> \
    --provenance-path <path> --batch-id <id> -o distribution_manifest.json \
    [--channel-id ch_001] [--platform youtube] [--tags tag1,tag2] [--topic anxiety] ...

Authority: docs/VIDEO_PIPELINE_SPEC.md §10 (metadata), §15 (anti-spam).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.video._config import load_yaml, write_atomically, should_skip_output, PIPELINE_VERSION

WRITING_STYLES_PATH = "config/video/channel_writing_styles.yaml"
PLATFORM_SEO_PATH = "config/video/platform_seo_policies.yaml"


def _load_channel_style(channel_id: str | None) -> dict:
    """Load writing style for a channel. Returns empty dict if not found."""
    if not channel_id:
        return {}
    styles = load_yaml(WRITING_STYLES_PATH)
    return styles.get("styles", {}).get(channel_id, {})


def _load_platform_policy(platform: str | None) -> dict:
    """Load SEO policy for a platform. Returns empty dict if not found."""
    if not platform:
        return {}
    policies = load_yaml(PLATFORM_SEO_PATH)
    return policies.get("platforms", {}).get(platform, {})


def _select_hashtags(channel_style: dict, platform_policy: dict, topic: str) -> list[str]:
    """Pick hashtags from channel pool, respecting platform max count."""
    pool = channel_style.get("hashtag_pool", [])
    max_count = platform_policy.get("hashtags", {}).get("max_count", 5)
    # Return up to max_count from channel pool
    return pool[:max_count]


def _build_platform_metadata(
    channel_id: str | None,
    platform: str | None,
    title: str,
    description: str,
    topic: str,
) -> dict:
    """Build platform-specific SEO metadata section for the manifest."""
    channel_style = _load_channel_style(channel_id)
    platform_policy = _load_platform_policy(platform)

    if not channel_style and not platform_policy:
        return {}

    meta = {}

    # Channel writing style fields
    if channel_style:
        meta["channel_voice"] = channel_style.get("voice", "")
        meta["channel_tone"] = channel_style.get("tone", "")
        meta["description_opener_style"] = channel_style.get("description_opener", "")
        meta["sentence_style"] = channel_style.get("sentence_style", "")
        meta["emoji_use"] = channel_style.get("emoji_use", "none")
        meta["cta_style"] = channel_style.get("cta_style", "")
        meta["signature_phrase"] = channel_style.get("signature_phrase", "")

    # Platform SEO fields
    if platform_policy:
        title_policy = platform_policy.get("title", {})
        desc_policy = platform_policy.get("description", {})
        hashtag_policy = platform_policy.get("hashtags", {})

        meta["platform"] = platform
        meta["title_max_chars"] = title_policy.get("max_chars", 100)
        meta["title_recommended_chars"] = title_policy.get("recommended_chars", 60)
        meta["description_max_chars"] = desc_policy.get("max_chars", 5000)
        meta["description_recommended_chars"] = desc_policy.get("recommended_chars", 150)
        meta["hashtag_placement"] = hashtag_policy.get("placement", "end_of_caption")
        meta["hashtag_max_count"] = hashtag_policy.get("max_count", 5)

        # Title length warning
        if len(title) > title_policy.get("max_chars", 100):
            meta["title_warning"] = f"title exceeds {title_policy.get('max_chars', 100)} char limit"

        # Description length warning
        if len(description) > desc_policy.get("max_chars", 5000):
            meta["description_warning"] = f"description exceeds {desc_policy.get('max_chars', 5000)} char limit"

    # Hashtags (channel pool + platform count limit)
    if channel_style or platform_policy:
        meta["hashtags"] = _select_hashtags(channel_style, platform_policy, topic)

    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description="Write distribution manifest with telemetry + platform SEO")
    ap.add_argument("--video-id", required=True)
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--description", required=True)
    ap.add_argument("--provenance-path", required=True, help="Path to video_provenance.json for partner")
    ap.add_argument("--batch-id", required=True)
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--format", default="landscape_16_9")
    ap.add_argument("--tags", default="", help="Comma-separated tags")
    ap.add_argument("--hook-type", default="light_reveal")
    ap.add_argument("--environment", default="forest_path")
    ap.add_argument("--motion-type", default="slow_zoom")
    ap.add_argument("--music-mood", default="calm")
    ap.add_argument("--caption-pattern", default="question_hook")
    ap.add_argument("--style-version", default="v1")
    ap.add_argument("--topic", default="", help="Content topic (e.g. anxiety, burnout) for thumbnail generator")
    ap.add_argument("--persona", default="", help="Persona identifier (reserved for template variants)")
    ap.add_argument("--channel-id", default="", help="Channel ID (e.g. ch_001) for per-brand writing style")
    ap.add_argument("--platform", default="", help="Target platform (youtube, tiktok, instagram_reels, youtube_shorts)")
    ap.add_argument("--primary-asset-ids", default="", help="Comma-separated asset IDs (or from timeline)")
    ap.add_argument("--shot-plan", help="Path to shot_plan.json (to read config_hash for idempotent skip)")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists with same config_hash")
    args = ap.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    primary_asset_ids = [a.strip() for a in args.primary_asset_ids.split(",") if a.strip()] if args.primary_asset_ids else []

    config_hash = ""
    if args.shot_plan and Path(args.shot_plan).exists():
        config_hash = json.loads(Path(args.shot_plan).read_text(encoding="utf-8")).get("config_hash") or ""

    out_path = Path(args.out)
    if config_hash and should_skip_output(out_path, ["video_id", "plan_id", "config_hash"], args.force, config_hash):
        print(f"Skip (output exists with same config_hash, use --force to overwrite): {out_path}")
        return 0

    doc = {
        "pipeline_version": PIPELINE_VERSION,
        "video_id": args.video_id,
        "plan_id": args.plan_id,
        "config_hash": config_hash,
        "title": args.title,
        "description": args.description,
        "tags": tags,
        "video_provenance_path": args.provenance_path,
        "batch_id": args.batch_id,
        "format": args.format,
        "topic": args.topic or "",
        "persona": args.persona or "",
        "channel_id": args.channel_id or "",
        "platform": args.platform or "",
        "hook_type": args.hook_type,
        "environment": args.environment,
        "motion_type": args.motion_type,
        "music_mood": args.music_mood,
        "caption_pattern": args.caption_pattern,
        "style_version": args.style_version,
        "primary_asset_ids": primary_asset_ids,
    }

    # Build platform-specific SEO metadata
    platform_seo = _build_platform_metadata(
        channel_id=args.channel_id or None,
        platform=args.platform or None,
        title=args.title,
        description=args.description,
        topic=args.topic or "",
    )
    if platform_seo:
        doc["platform_seo"] = platform_seo

    write_atomically(out_path, doc)
    print(f"Wrote distribution manifest to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
