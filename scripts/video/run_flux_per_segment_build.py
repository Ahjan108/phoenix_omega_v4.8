#!/usr/bin/env python3
"""
Build one FLUX image per script segment using LLM-derived scene descriptions (segment_scenes.json).
Output: plan_dir/segment_images/<asset_id>.png and plan_dir/segment_asset_index.json.
Use with run_asset_resolver.py --segment-index plan_dir/segment_asset_index.json so each
shot gets the image that matches its segment’s script.
Requires: segment_scenes.json from run_segment_scene_extraction.py; FLUX credentials.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import shutil
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
    return re.sub(r"[^a-zA-Z0-9_-]", "_", s).strip("_") or "seg"


def _register_in_image_bank(asset_id: str, image_path: Path, topic: str, visual_intent: str = "CHARACTER_EMOTION") -> None:
    """Ensure every generated image is also available in image_bank/ with index.json entry."""
    bank_dir = REPO_ROOT / "image_bank"
    bank_dir.mkdir(parents=True, exist_ok=True)
    bank_image = bank_dir / f"{asset_id}.png"
    if not bank_image.exists():
        shutil.copy2(str(image_path), str(bank_image))
    index_path = bank_dir / "index.json"
    rows = []
    if index_path.exists():
        try:
            rows = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            rows = []
    existing = {r.get("asset_id") for r in rows if isinstance(r, dict)}
    if asset_id not in existing:
        rows.append({
            "asset_id": asset_id,
            "topic": topic,
            "visual_intent": visual_intent,
            "composition_compat": {"16:9": 1.0, "9:16": 1.0, "1:1": 1.0},
            "path": str(bank_image),
        })
        index_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate one FLUX image per segment from segment_scenes.json")
    ap.add_argument("segment_scenes", help="Path to segment_scenes.json (from run_segment_scene_extraction)")
    ap.add_argument("-o", "--out-dir", required=True, help="Output dir (e.g. artifacts/video/<plan_id>)")
    ap.add_argument("--topic", default=None, help="Topic for palette (default: from segment_scenes)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing images")
    ap.add_argument("--dry-run", action="store_true", help="Print plan only, no API calls")
    args = ap.parse_args()

    sc_path = Path(args.segment_scenes)
    if not sc_path.exists():
        print(f"Error: not found {sc_path}", file=sys.stderr)
        return 1
    data = json.loads(sc_path.read_text(encoding="utf-8"))
    plan_id = data.get("plan_id", "plan")
    topic = args.topic or data.get("topic", "depression")
    segments = data.get("segments") or []

    if not segments:
        print("No segments in segment_scenes.json", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    images_dir = out_dir / "segment_images"
    images_dir.mkdir(parents=True, exist_ok=True)

    account_id, api_token = load_credentials()
    flux_available = bool(account_id and api_token and not args.dry_run)
    if not flux_available and not args.dry_run:
        print("Error: FLUX credentials missing (CLOUDFLARE_ACCOUNT_ID/CLOUDFLARE_API_TOKEN). Hard fail mode.", file=sys.stderr)
        return 1

    segment_id_to_asset: dict[str, str] = {}
    failures: list[str] = []
    for i, seg in enumerate(segments):
        segment_id = seg.get("segment_id") or f"seg-{i+1}"
        scene_description = (seg.get("scene_description") or "").strip()
        if not scene_description or scene_description == "(dry-run)":
            if args.dry_run:
                asset_id = f"{_slug(plan_id)}_seg_{i+1}"
                segment_id_to_asset[segment_id] = asset_id
                print(f"[dry-run] {segment_id} -> {asset_id}")
            else:
                failures.append(f"{segment_id}: missing scene_description")
                print(f"  Missing scene_description for {segment_id} (hard fail mode)", file=sys.stderr)
            continue
        asset_id = f"{_slug(plan_id)}_seg_{i+1}"
        out_path = images_dir / f"{asset_id}.png"
        if out_path.exists() and not args.force:
            print(f"Skip (exists): {out_path.name}")
            segment_id_to_asset[segment_id] = asset_id
            continue
        if args.dry_run:
            print(f"Would generate: {asset_id} <- {scene_description[:60]}...")
            segment_id_to_asset[segment_id] = asset_id
            continue
        print(f"[{i+1}/{len(segments)}] {segment_id} -> {asset_id} ...")
        try:
            prompt, negative, guidance, seed = get_prompt_for_topic_scene(topic, scene_description)
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
            segment_id_to_asset[segment_id] = asset_id
            _register_in_image_bank(asset_id, out_path, topic=topic)
        except Exception as e:
            failures.append(f"{segment_id}: {e}")
            print(f"  FLUX failed for {segment_id} (hard fail mode)", file=sys.stderr)

    if failures:
        print("Error: segment image generation failed for one or more segments:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    index = {
        "plan_id": plan_id,
        "topic": topic,
        "segment_id_to_asset": segment_id_to_asset,
        "assets_dir": str(images_dir),
    }
    index_path = out_dir / "segment_asset_index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Wrote segment_asset_index.json ({len(segment_id_to_asset)} segments) to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
