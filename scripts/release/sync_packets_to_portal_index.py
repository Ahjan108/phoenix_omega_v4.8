#!/usr/bin/env python3
"""
Sync packet metadata from pipeline output into portal DB (weekly_packets) and optionally
write download_index.json for R2 or local use.

Run after upload_brand_packets_r2.py. Reads artifacts/brand_packets/YYYY-WW/download_links.json
and release_day from each brand folder; upserts into services/admin_portal data DB.

Usage:
  python scripts/release/sync_packets_to_portal_index.py --packets-dir artifacts/brand_packets/2026-W11
  python scripts/release/sync_packets_to_portal_index.py --week-start 2026-03-10
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PORTAL_DIR = REPO_ROOT / "services" / "admin_portal"
sys.path.insert(0, str(REPO_ROOT))

from services.admin_portal.models import get_conn, init_db, upsert_packet

DEFAULT_DB = PORTAL_DIR / "data" / "portal.db"


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync packet metadata to portal DB.")
    ap.add_argument("--packets-dir", type=Path, default=None)
    ap.add_argument("--week-start", default=None)
    ap.add_argument("--db", type=Path, default=None, help="Portal DB path")
    ap.add_argument("--write-index", action="store_true", help="Also write download_index.json to packets-dir")
    args = ap.parse_args()

    if args.packets_dir:
        packets_dir = Path(args.packets_dir)
        if not packets_dir.is_absolute():
            packets_dir = REPO_ROOT / packets_dir
    elif args.week_start:
        from scripts.release.week_utils import iso_week_from_week_start
        week_key = iso_week_from_week_start(args.week_start)
        packets_dir = REPO_ROOT / "artifacts" / "brand_packets" / week_key
    else:
        print("Provide --packets-dir or --week-start", file=sys.stderr)
        return 1

    links_path = packets_dir / "download_links.json"
    if not links_path.exists():
        print(f"Not found: {links_path}", file=sys.stderr)
        return 1

    week_key = packets_dir.name
    data = json.loads(links_path.read_text())
    prefix = "weekly"
    brands_data = data.get("brands") or {}

    db_path = args.db or DEFAULT_DB
    conn = get_conn(db_path)
    init_db(conn)

    index_packets = []
    for brand_id, info in brands_data.items():
        r2_key = f"{prefix}/{week_key}/{brand_id}/packet.zip"
        release_day = ""
        release_file = packets_dir / brand_id / "release_day.txt"
        if release_file.exists():
            release_day = release_file.read_text().strip()
        bytes_ = info.get("size_bytes") or 0
        sha256 = info.get("sha256") or ""
        upsert_packet(conn, week_key, brand_id, r2_key, release_day, bytes_, sha256, "ready")
        index_packets.append({
            "brand_id": brand_id,
            "r2_key": r2_key,
            "release_day": release_day,
            "bytes": bytes_,
            "sha256": sha256,
            "status": "ready",
        })

    conn.close()

    if args.write_index:
        from datetime import datetime, timezone
        index = {
            "schema_version": "1.0",
            "week": week_key,
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "packets": index_packets,
        }
        index_path = packets_dir / "download_index.json"
        index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
        print(f"Wrote {index_path}")

    print(f"Synced {len(index_packets)} packets for {week_key} to {db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
