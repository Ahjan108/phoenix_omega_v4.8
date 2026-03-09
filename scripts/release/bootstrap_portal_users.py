#!/usr/bin/env python3
"""
Bootstrap portal DB: create users and grants from config/release/brand_admin_contacts.yaml.
Maps email -> allowed_brand_ids and upserts brand_admin_users + brand_admin_grants.

Usage:
  python scripts/release/bootstrap_portal_users.py
  python scripts/release/bootstrap_portal_users.py --config config/release/brand_admin_contacts.yaml
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Bootstrap portal users from contacts config.")
    ap.add_argument("--config", type=Path, default=REPO_ROOT / "config" / "release" / "brand_admin_contacts.yaml")
    ap.add_argument("--db", type=Path, default=None)
    args = ap.parse_args()

    cfg = _load_yaml(args.config)
    brands_block = (cfg.get("brands") or {}) if isinstance(cfg, dict) else {}
    if not brands_block:
        print("No brands in config.", file=sys.stderr)
        return 0

    # email -> list of brand_ids
    email_to_brands: dict[str, list[str]] = {}
    for brand_id, data in brands_block.items():
        if not isinstance(data, dict):
            continue
        email = (data.get("email") or "").strip()
        if not email:
            continue
        email = email.lower()
        email_to_brands.setdefault(email, []).append(brand_id)

    if not email_to_brands:
        print("No emails in config (add email per brand).", file=sys.stderr)
        return 0

    from services.admin_portal.models import get_conn, init_db, ensure_user_and_grants

    db_path = args.db or (REPO_ROOT / "services" / "admin_portal" / "data" / "portal.db")
    conn = get_conn(db_path)
    init_db(conn)

    for email, brand_ids in email_to_brands.items():
        uid = ensure_user_and_grants(conn, email, None, brand_ids)
        print(f"  {email} -> {brand_ids} (user_id={uid})")

    conn.close()
    print("Bootstrap done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
