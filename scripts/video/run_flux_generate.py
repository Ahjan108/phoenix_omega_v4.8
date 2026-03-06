#!/usr/bin/env python3
"""
Generate one image via Cloudflare Workers AI FLUX. Uses master prompt template from
docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md: foreground → Background: → Overall lighting: → 9:16.
Loads palette and never_rules from config/video/brand_style_tokens.yaml and
config/video/prompt_constraints.yaml.

Credentials (pick one): env CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN; or .env at repo root;
or key file at repo root: cloudflare_workers_ai.txt or 11.txt with lines
CLOUDFLARE_ACCOUNT_ID=... and CLOUDFLARE_API_TOKEN=... (same pattern as author cover art / TTS).
"""
from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

# REPO_ROOT for config loading
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_yaml(rel_path: str) -> dict:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        raise RuntimeError("PyYAML required; pip install pyyaml")


def build_master_prompt(
    scene_description: str,
    palette_prompt_names: list[str],
    band_never_rules: list[str],
    no_adoration: list[str],
    shared_negatives: list[str],
) -> str:
    """Build positive prompt from template (foreground → Background: → Overall lighting:)."""
    palette_str = ", ".join(palette_prompt_names)
    foreground = (
        f"A soft hand-painted gouache illustration of {scene_description}, "
        f"in {palette_str}, soft brush texture, gentle paper-like grain, "
        "centered composition, generous negative space, no faces, contemplative mood."
    )
    background = (
        f"Background: an atmospheric abstract gradient of {palette_str}, "
        "with soft blur, no sharp edges, ethereal haze."
    )
    lighting = (
        "Overall lighting: soft diffused light from the window, quiet and undramatic, "
        "subtle volumetric haze, 9:16, highly detailed but soft."
    )
    return f"{foreground}\n\n{background}\n\n{lighting}"


def build_negative_block(
    band_never_rules: list[str],
    no_adoration: list[str],
    shared_negatives: list[str],
) -> str:
    """Combine band never_rules + no_adoration + shared_negatives for negative block."""
    parts = list(band_never_rules)
    parts.extend(no_adoration)
    parts.extend(shared_negatives)
    return ", ".join(parts)


def call_cloudflare_flux(
    account_id: str,
    api_token: str,
    prompt: str,
    negative_prompt: str,
    width: int = 576,
    height: int = 1024,
    steps: int = 25,
    guidance: float = 3.0,
    seed: int = 739204,
    model: str = "@cf/black-forest-labs/flux-2-dev",
) -> bytes:
    """POST to Cloudflare Workers AI FLUX (multipart/form-data); returns image bytes."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    # FLUX expects multipart form. Append negative as "Avoid: ..." if no separate field.
    full_prompt = prompt
    if negative_prompt:
        full_prompt = f"{prompt}\n\nAvoid: {negative_prompt}"

    try:
        import requests
    except ImportError:
        raise RuntimeError("requests required for multipart; pip install requests")

    payload = {
        "prompt": (None, full_prompt),
        "width": (None, str(width)),
        "height": (None, str(height)),
        "steps": (None, str(steps)),
        "guidance": (None, str(guidance)),
        "seed": (None, str(seed)),
    }
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_token}"},
        files=payload,
        timeout=120,
    )
    resp.raise_for_status()
    out = resp.content

    import json
    try:
        obj = json.loads(out.decode("utf-8"))
    except Exception:
        return out
    if not obj.get("success", True):
        errors = obj.get("errors", [])
        raise RuntimeError(f"API errors: {errors}")
    result = obj.get("result", obj)
    if isinstance(result, dict) and "image" in result:
        return base64.b64decode(result["image"])
    if isinstance(result, str):
        return base64.b64decode(result)
    raise RuntimeError(f"Unexpected API response: {list(result.keys()) if isinstance(result, dict) else type(result)}")


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

    # Optional: load .env from repo root for CLOUDFLARE_*
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass

    # Optional: load from key file (same pattern as TTS/cover art: 11.txt or cloudflare_workers_ai.txt at repo root)
    def _load_cloudflare_from_keyfile() -> None:
        for name in ("cloudflare_workers_ai.txt", "11.txt"):
            path = REPO_ROOT / name
            if not path.exists():
                continue
            raw = path.read_text(encoding="utf-8").strip()
            for line in raw.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                for key in ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_AI_API_TOKEN"):
                    if os.environ.get(key, "").strip():
                        continue
                    if (line.startswith(key + "=") or line.startswith(key + ":")):
                        sep = "=" if "=" in line else ":"
                        val = line.split(sep, 1)[-1].strip().strip('"').strip("'")
                        if val and not val.startswith("$"):
                            os.environ[key] = val
                            break
    _load_cloudflare_from_keyfile()

    tokens = load_yaml("config/video/brand_style_tokens.yaml")
    constraints = load_yaml("config/video/prompt_constraints.yaml")
    band_name = tokens.get("topic_to_band", {}).get(args.topic, "cool_calm")
    bands = tokens.get("bands", {})
    band = bands.get(band_name, {})
    topics = band.get("topics", {})
    topic_cfg = topics.get(args.topic, {})
    palette = topic_cfg.get("palette", [])
    palette_prompt_names = [p.get("prompt_name", "") for p in palette if p.get("prompt_name")]
    if not palette_prompt_names:
        # Fallback anxiety
        palette_prompt_names = ["slate blue grey", "pale mist blue", "pale mist"]

    band_never = band.get("never_rules", [])
    gen_spec = band.get("generation_spec", {})
    seed = int(gen_spec.get("shnell_seed", 739204))
    guidance = float(gen_spec.get("guidance", 3.0))

    no_adoration = constraints.get("no_adoration", [])
    shared_negatives = constraints.get("shared_negatives", [])

    prompt = build_master_prompt(
        args.scene,
        palette_prompt_names,
        band_never,
        no_adoration,
        shared_negatives,
    )
    negative = build_negative_block(band_never, no_adoration, shared_negatives)
    full_prompt = f"{prompt}\n\nAvoid: {negative}" if negative else prompt

    if args.dry_run:
        print("=== Positive prompt ===")
        print(prompt)
        print("\n=== Negative block ===")
        print(negative)
        print("\n=== Full prompt (positive + Avoid) ===")
        print(full_prompt[:2000] + ("..." if len(full_prompt) > 2000 else ""))
        return 0

    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN", os.environ.get("CLOUDFLARE_AI_API_TOKEN", "")).strip()
    if not account_id or not api_token:
        print("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN (env, .env, or cloudflare_workers_ai.txt / 11.txt at repo root).", file=sys.stderr)
        return 1

    print("Prompt (first 400 chars):", prompt[:400] + "..." if len(prompt) > 400 else prompt)
    print("Negative block length:", len(negative), "chars")

    image_bytes = call_cloudflare_flux(
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
