#!/usr/bin/env python3
"""
Generate one image via Cloudflare Workers AI FLUX. Uses master prompt template from
docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md: foreground → Background: → Overall lighting: → 9:16.
Loads palette and never_rules from config/video/brand_style_tokens.yaml and
config/video/prompt_constraints.yaml.

Credentials (pick one): env CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN; or .env at repo root;
or key file at repo root: cloudflare_workers_ai.txt or 11.txt (same pattern as author cover art / TTS).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video.flux_client import (
    load_credentials,
    get_prompt_for_topic_scene,
    call_flux,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate one FLUX image via Cloudflare (master prompt test)")
    parser.add_argument("--scene", default="a person's hands holding a cup of tea by a window", help="Scene description for foreground")
    parser.add_argument("--topic", default="anxiety", help="Topic key (e.g. anxiety) for palette and band")
    parser.add_argument("--out", type=Path, default=None, help="Output image path (default: image_bank/master_prompt_test_<topic>.png)")
    parser.add_argument("--model", default="@cf/black-forest-labs/flux-2-dev", help="Cloudflare model id")
    parser.add_argument("--width", type=int, default=576, help="Width (9:16)")
    parser.add_argument("--height", type=int, default=1024, help="Height (9:16)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt and exit without calling API")
    args = parser.parse_args()

    prompt, negative, guidance, seed = get_prompt_for_topic_scene(args.topic, args.scene)

    if args.dry_run:
        print("=== Positive prompt ===")
        print(prompt)
        print("\n=== Negative block ===")
        print(negative)
        print("\n=== Full prompt (positive + Avoid) ===")
        full = f"{prompt}\n\nAvoid: {negative}" if negative else prompt
        print(full[:2000] + ("..." if len(full) > 2000 else ""))
        return 0

    account_id, api_token = load_credentials()
    if not account_id or not api_token:
        print("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN (env, .env, or cloudflare_workers_ai.txt / 11.txt at repo root).", file=sys.stderr)
        return 1

    print("Prompt (first 400 chars):", prompt[:400] + "..." if len(prompt) > 400 else prompt)
    print("Negative block length:", len(negative), "chars")

    image_bytes = call_flux(
        account_id=account_id,
        api_token=api_token,
        prompt=prompt,
        negative_prompt=negative,
        width=args.width,
        height=args.height,
        guidance=guidance,
        seed=seed,
        model=args.model,
    )

    out_path = args.out
    if out_path is None:
        image_bank = REPO_ROOT / "image_bank"
        image_bank.mkdir(parents=True, exist_ok=True)
        out_path = image_bank / f"master_prompt_test_{args.topic}.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)
    print("Saved:", out_path.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
