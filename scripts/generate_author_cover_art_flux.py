#!/usr/bin/env python3
"""
Generate author cover art base images via Cloudflare Workers AI FLUX.
Reads config/authoring/author_cover_art_registry.yaml; for each author builds a prompt
from style_hint and writes assets/authors/cover_art/{author_id}_base.png.
Uses same credentials as video FLUX (cloudflare_workers_ai.txt).
Authority: docs/authoring/AUTHOR_COVER_ART_SYSTEM.md, docs/VIDEO_AND_COVER_ART_FLUX_WIRING.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video.flux_client import (
    load_credentials,
    get_prompt_for_topic_scene,
    call_flux,
    load_yaml,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate author cover art bases via FLUX")
    ap.add_argument("--authors", type=str, default=None, help="Comma-separated author_ids (default: all in registry)")
    ap.add_argument("--out-dir", type=Path, default=None, help="Output dir (default: assets/authors/cover_art)")
    ap.add_argument("--topic", type=str, default="anxiety", help="Topic for palette (default: anxiety / cool_calm)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing PNGs")
    ap.add_argument("--dry-run", action="store_true", help="Print plan only")
    args = ap.parse_args()

    reg_path = REPO_ROOT / "config" / "authoring" / "author_cover_art_registry.yaml"
    if not reg_path.exists():
        print(f"Registry not found: {reg_path}", file=sys.stderr)
        return 1
    reg = load_yaml(str(reg_path.relative_to(REPO_ROOT)))
    authors = reg.get("authors") or {}
    if not authors:
        print("No authors in registry.", file=sys.stderr)
        return 1

    out_dir = args.out_dir or (REPO_ROOT / "assets" / "authors" / "cover_art")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.authors:
        author_ids = [a.strip() for a in args.authors.split(",") if a.strip()]
        author_ids = [a for a in author_ids if a in authors]
    else:
        author_ids = list(authors.keys())

    if not author_ids:
        print("No authors to process.", file=sys.stderr)
        return 1

    account_id, api_token = load_credentials()
    if not args.dry_run and (not account_id or not api_token):
        print("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN. See docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md.", file=sys.stderr)
        return 1

    for i, author_id in enumerate(author_ids):
        entry = authors.get(author_id) or {}
        style_hint = entry.get("style_hint") or "contemplative"
        out_path = out_dir / f"{author_id}_base.png"
        if out_path.exists() and not args.force:
            print(f"Skip (exists): {out_path.relative_to(REPO_ROOT)}")
            continue
        scene = (
            f"abstract book cover base background, {style_hint} mood, no text no faces, "
            "soft gradient atmosphere, contemplative, portrait orientation"
        )
        if args.dry_run:
            print(f"  {author_id}: {scene[:60]}... -> {out_path.name}")
            continue
        print(f"[{i+1}/{len(author_ids)}] {author_id} ...")
        try:
            prompt, negative, guidance, seed = get_prompt_for_topic_scene(args.topic, scene)
            image_bytes = call_flux(
                account_id=account_id,
                api_token=api_token,
                prompt=prompt,
                negative_prompt=negative,
                width=576,
                height=1024,
                guidance=guidance,
                seed=seed + hash(author_id) % 100000,
            )
            out_path.write_bytes(image_bytes)
            print(f"  Wrote {out_path.relative_to(REPO_ROOT)}")
        except Exception as e:
            print(f"  Failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
