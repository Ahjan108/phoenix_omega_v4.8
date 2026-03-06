"""
Shared Cloudflare Workers AI FLUX client for video image bank and author cover art.
Load credentials, build prompts from config, call FLUX API.
Used by: run_flux_generate.py, run_flux_bank_build.py, generate_author_cover_art_flux.py.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path

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


def load_credentials() -> tuple[str, str]:
    """Load CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN from env, .env, or key file."""
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass
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
                if line.startswith(key + "=") or line.startswith(key + ":"):
                    sep = "=" if "=" in line else ":"
                    val = line.split(sep, 1)[-1].strip().strip('"').strip("'")
                    if val and not val.startswith("$"):
                        os.environ[key] = val
                        break
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN", os.environ.get("CLOUDFLARE_AI_API_TOKEN", "")).strip()
    return account_id, api_token


def build_master_prompt(
    scene_description: str,
    palette_prompt_names: list[str],
    band_never_rules: list[str],
    no_adoration: list[str],
    shared_negatives: list[str],
) -> str:
    """Build positive prompt (foreground → Background: → Overall lighting:)."""
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
    """Combine never_rules + no_adoration + shared_negatives."""
    parts = list(band_never_rules)
    parts.extend(no_adoration)
    parts.extend(shared_negatives)
    return ", ".join(parts)


def get_prompt_for_topic_scene(topic: str, scene_description: str) -> tuple[str, str, float, int]:
    """
    Load config for topic, build prompt and negative block. Returns (prompt, negative, guidance, seed).
    """
    tokens = load_yaml("config/video/brand_style_tokens.yaml")
    constraints = load_yaml("config/video/prompt_constraints.yaml")
    band_name = tokens.get("topic_to_band", {}).get(topic, "cool_calm")
    bands = tokens.get("bands", {})
    band = bands.get(band_name, {})
    topics_cfg = band.get("topics", {})
    topic_cfg = topics_cfg.get(topic, {})
    palette = topic_cfg.get("palette", [])
    palette_prompt_names = [p.get("prompt_name", "") for p in palette if p.get("prompt_name")]
    if not palette_prompt_names:
        palette_prompt_names = ["slate blue grey", "pale mist blue", "pale mist"]
    band_never = band.get("never_rules", [])
    gen_spec = band.get("generation_spec", {})
    seed = int(gen_spec.get("shnell_seed", 739204))
    guidance = float(gen_spec.get("guidance", 3.0))
    no_adoration = constraints.get("no_adoration", [])
    shared_negatives = constraints.get("shared_negatives", [])
    prompt = build_master_prompt(
        scene_description,
        palette_prompt_names,
        band_never,
        no_adoration,
        shared_negatives,
    )
    negative = build_negative_block(band_never, no_adoration, shared_negatives)
    return prompt, negative, guidance, seed


def call_flux(
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
    """POST to Cloudflare Workers AI FLUX; returns image bytes."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    full_prompt = f"{prompt}\n\nAvoid: {negative_prompt}" if negative_prompt else prompt
    try:
        import requests
    except ImportError:
        raise RuntimeError("requests required; pip install requests")
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
    try:
        obj = json.loads(out.decode("utf-8"))
    except Exception:
        return out
    if not obj.get("success", True):
        raise RuntimeError(f"API errors: {obj.get('errors', [])}")
    result = obj.get("result", obj)
    if isinstance(result, dict) and "image" in result:
        return base64.b64decode(result["image"])
    if isinstance(result, str):
        return base64.b64decode(result)
    raise RuntimeError(f"Unexpected API response: {type(result)}")
