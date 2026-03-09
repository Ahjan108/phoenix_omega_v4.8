"""
Resolve current user from Cloudflare Access. No permanent public links.
Behind CF Access: trust Cf-Access-Authenticated-User-Email (or JWT).
Local dev: OVERRIDE_EMAIL env.
"""
from __future__ import annotations

import os
from typing import Any

# Cloudflare Access sets these when MFA etc. pass
CF_EMAIL_HEADER = "Cf-Access-Authenticated-User-Email"
CF_JWT_HEADER = "Cf-Access-Jwt-Assertion"


def get_request_email(headers: dict[str, str] | Any) -> str | None:
    """Return authenticated user email or None. Prefer CF header; fallback OVERRIDE_EMAIL."""
    if hasattr(headers, "get"):
        email = (headers.get(CF_EMAIL_HEADER) or "").strip()
        if email:
            return email.lower()
    override = os.environ.get("OVERRIDE_EMAIL", "").strip()
    if override:
        return override.lower()
    return None
