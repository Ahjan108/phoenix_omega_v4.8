#!/usr/bin/env python3
"""
Confirm Cloudflare API credentials for Workers AI (FLUX text-to-image).
Uses the same credential sources as run_flux_generate.py: env, .env, or
cloudflare_workers_ai.txt / 11.txt at repo root.

Checks:
  1. Token valid: GET .../user/tokens/verify
  2. Account ID valid and accessible: GET .../accounts/{account_id}

Used for: video image bank FLUX, and author cover art when using Cloudflare T2I.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_credentials() -> tuple[str, str]:
    """Load CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN (or CLOUDFLARE_AI_API_TOKEN)."""
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


def verify_token(api_token: str) -> dict | None:
    """GET .../user/tokens/verify; returns result dict on success, None on failure."""
    try:
        import requests
    except ImportError:
        print("pip install requests", file=sys.stderr)
        return None
    r = requests.get(
        "https://api.cloudflare.com/client/v4/user/tokens/verify",
        headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"},
        timeout=15,
    )
    if r.status_code != 200:
        return None
    data = r.json()
    if not data.get("success"):
        return None
    return data.get("result")


def verify_account(account_id: str, api_token: str) -> dict | None:
    """GET .../accounts/{id}; returns result dict on success, None on failure."""
    try:
        import requests
    except ImportError:
        return None
    r = requests.get(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}",
        headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"},
        timeout=15,
    )
    if r.status_code != 200:
        return None
    data = r.json()
    if not data.get("success"):
        return None
    return data.get("result")


def main() -> int:
    account_id, api_token = load_credentials()
    # Credentials loaded from: env → .env → cloudflare_workers_ai.txt / 11.txt at repo root

    if not account_id:
        print("Missing CLOUDFLARE_ACCOUNT_ID.", file=sys.stderr)
        print("Add it to .env or cloudflare_workers_ai.txt (or 11.txt) at repo root. See docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md.", file=sys.stderr)
        return 1
    if not api_token:
        print("Missing CLOUDFLARE_API_TOKEN (or CLOUDFLARE_AI_API_TOKEN).", file=sys.stderr)
        print("Add it to .env or cloudflare_workers_ai.txt (or 11.txt) at repo root. See docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md.", file=sys.stderr)
        return 1

    print("Verifying API token (Cloudflare user/tokens/verify)...")
    token_result = verify_token(api_token)
    if not token_result:
        print("Token verification failed. Check that CLOUDFLARE_API_TOKEN is correct and has not been revoked.", file=sys.stderr)
        return 1
    print("  Token valid:", token_result.get("status", "active"))

    print("Verifying account access...")
    account_result = verify_account(account_id, api_token)
    if not account_result:
        print("Account verification failed. Check that CLOUDFLARE_ACCOUNT_ID is the 32-char hex for your account.", file=sys.stderr)
        return 1
    name = account_result.get("name", "?")
    print("  Account:", name)

    print("Credentials confirmed. You can run scripts/video/run_flux_generate.py for FLUX image generation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
