#!/usr/bin/env python3
"""
Build the video image bank: generate FLUX images per (topic, visual_intent) and write index.json
for the asset resolver. Uses config/video/flux_bank_scenes.yaml and canonical_topics.
Usage: python scripts/video/run_flux_bank_build.py [--bank-dir image_bank] [--topics anxiety,burnout] [--limit 4]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video.flux_client import (
    load_credentials,
    get_prompt_for_topic_scene,
    call_flux,
    load_yaml,
)


def _slug(s: str) -> str:
    return re.sub(r"[^\w]", "_", s).strip("_") or "default"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build FLUX image bank and index for video pipeline")
    ap.add_argument("--bank-dir", type=Path, default=None, help="Image bank directory (default: repo image_bank/)")
    ap.add_argument("--topics", type=str, default=None, help="Comma-separated topics (default: from canonical_topics.yaml)")
    ap.add_argument("--limit", type=int, default=None, help="Max number of (topic,intent) pairs to generate (for testing)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing images")
    ap.add_argument("--dry-run", action="store_true", help="Print plan only, no API calls")
    args = ap.parse_args()

    bank_dir = args.bank_dir or (REPO_ROOT / "image_bank")
    bank_dir = Path(bank_dir)
    bank_dir.mkdir(parents=True, exist_ok=True)

    # Topics
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    else:
        ct = load_yaml("config/catalog_planning/canonical_topics.yaml")
        topics = ct.get("topics") or ["anxiety", "burnout", "grief", "self_worth"]

    # Visual intents and scenes
    scenes_cfg = load_yaml("config/video/flux_bank_scenes.yaml")
    intent_map = scenes_cfg.get("visual_intent_scenes") or {}
    default_scene = scenes_cfg.get("default_scene") or "a contemplative moment, soft light, no faces"
    intents = list(intent_map.keys()) or ["HOOK_VISUAL", "CHARACTER_EMOTION", "SYMBOLIC_METAPHOR", "ENVIRONMENT_ATMOSPHERE"]

    account_id, api_token = load_credentials()
    if not args.dry_run and (not account_id or not api_token):
        print("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN. See docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md.", file=sys.stderr)
        return 1

    index_entries = []
    planned = []
    for topic in topics:
        for intent in intents:
            scene = (intent_map.get(intent) or {}).get("scene") or default_scene
            asset_id = f"{_slug(topic)}_{_slug(intent)}"
            out_path = bank_dir / f"{asset_id}.png"
            planned.append((topic, intent, scene, asset_id, out_path))

    if args.limit:
        planned = planned[: args.limit]

    if args.dry_run:
        print(f"Would generate {len(planned)} images into {bank_dir}")
        for topic, intent, scene, asset_id, out_path in planned:
            print(f"  {asset_id} <- {topic} / {intent}")
        print("Index would contain visual_intent + composition_compat 16:9/9:16 + asset_id per row.")
        return 0

    for i, (topic, intent, scene, asset_id, out_path) in enumerate(planned):
        if out_path.exists() and not args.force:
            print(f"Skip (exists): {out_path.name}")
            index_entries.append({
                "visual_intent": intent,
                "composition_compat": {"16:9": 1.0, "9:16": 1.0},
                "asset_id": asset_id,
            })
            continue
        print(f"[{i+1}/{len(planned)}] {asset_id} ...")
        try:
            prompt, negative, guidance, seed = get_prompt_for_topic_scene(topic, scene)
            image_bytes = call_flux(
                account_id=account_id,
                api_token=api_token,
                prompt=prompt,
                negative_prompt=negative,
                width=576,
                height=1024,
                guidance=guidance,
                seed=seed + i,
            )
            out_path.write_bytes(image_bytes)
            index_entries.append({
                "visual_intent": intent,
                "composition_compat": {"16:9": 1.0, "9:16": 1.0},
                "asset_id": asset_id,
            })
        except Exception as e:
            print(f"  Failed: {e}", file=sys.stderr)
            continue

    index_path = bank_dir / "index.json"
    index_path.write_text(json.dumps(index_entries, indent=2), encoding="utf-8")
    print(f"Wrote {len(index_entries)} entries to {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
