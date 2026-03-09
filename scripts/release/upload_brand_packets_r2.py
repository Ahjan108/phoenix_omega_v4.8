#!/usr/bin/env python3
"""
Upload brand packet zips to Cloudflare R2 and write download_links.json with
presigned URLs (24–72h), sha256, and size_bytes per zip.

Idempotent: overwrites same keys and download_links.json.
Prefix-scoped keys only: weekly/YYYY-WW/<brand_id>/packet.zip.
Secrets: R2 credentials from env only.

Usage:
  python scripts/release/upload_brand_packets_r2.py --packets-dir artifacts/brand_packets/2026-W11
  python scripts/release/upload_brand_packets_r2.py --week-start 2026-03-10 --expiry-hours 48 --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _get_r2_client():
    try:
        import boto3
    except ImportError:
        raise RuntimeError("boto3 required for R2: pip install boto3")
    cfg = _load_yaml(REPO_ROOT / "config" / "release" / "brand_packets_r2.yaml")
    account_id = os.environ.get("R2_ACCOUNT_ID") or cfg.get("account_id", "")
    access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    endpoint = os.environ.get("R2_ENDPOINT") or cfg.get(
        "endpoint", f"https://{account_id}.r2.cloudflarestorage.com"
    )
    if not access_key or not secret_key:
        raise RuntimeError("Set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY")
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def _get_bucket_and_prefix() -> tuple[str, str]:
    cfg = _load_yaml(REPO_ROOT / "config" / "release" / "brand_packets_r2.yaml")
    bucket = os.environ.get("R2_BUCKET_NAME") or cfg.get("bucket_name", "")
    if not bucket:
        bucket = os.environ.get("R2_BUCKET_NAME") or _load_yaml(REPO_ROOT / "config" / "video" / "distribution_r2.yaml").get("bucket_name", "pearl-video-handoff")
    prefix = cfg.get("prefix", "weekly")
    return bucket, prefix


def _sha256_and_size(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    return h.hexdigest(), n


def main() -> int:
    ap = argparse.ArgumentParser(description="Upload brand packet zips to R2; write download_links.json.")
    ap.add_argument("--packets-dir", type=Path, default=None)
    ap.add_argument("--week-start", default=None, help="Derive packets-dir as artifacts/brand_packets/YYYY-WW")
    ap.add_argument("--expiry-hours", type=int, default=72, help="Presigned URL TTL (24–72h)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.packets_dir:
        packets_dir = Path(args.packets_dir)
        if not packets_dir.is_absolute():
            packets_dir = REPO_ROOT / packets_dir
    elif args.week_start:
        import sys
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from scripts.release.week_utils import iso_week_from_week_start
        week_key = iso_week_from_week_start(args.week_start)
        packets_dir = REPO_ROOT / "artifacts" / "brand_packets" / week_key
    else:
        print("Provide --packets-dir or --week-start", file=sys.stderr)
        return 1

    if not packets_dir.exists():
        print(f"Packets dir not found: {packets_dir}", file=sys.stderr)
        return 1

    week_key = packets_dir.name
    if not week_key or week_key.startswith("."):
        print("Packets dir name must be YYYY-WW", file=sys.stderr)
        return 1

    expiry = max(24, min(72, args.expiry_hours))
    expiry_sec = expiry * 3600

    zips = sorted(packets_dir.glob("*.zip"))
    if not zips:
        print(f"No *.zip in {packets_dir}", file=sys.stderr)
        return 1

    bucket, prefix = _get_bucket_and_prefix()
    base_key = f"{prefix}/{week_key}"

    download_links: dict = {
        "week": week_key,
        "brands": {},
        "expiry_hours": expiry,
    }

    if args.dry_run:
        for z in zips:
            brand_id = z.stem.replace(f"{week_key}_", "").replace("_packet", "")
            sha, size = _sha256_and_size(z)
            r2_key = f"{base_key}/{brand_id}/packet.zip"
            download_links["brands"][brand_id] = {
                "url": "(dry-run)",
                "expires_at": "",
                "sha256": sha,
                "size_bytes": size,
            }
            print(f"  [dry-run] would upload {z.name} -> s3://{bucket}/{r2_key}")
    else:
        client = _get_r2_client()
        for z in zips:
            # YYYY-WW_<brand_id>_packet.zip -> brand_id
            stem = z.stem
            if stem.startswith(f"{week_key}_") and stem.endswith("_packet"):
                brand_id = stem[len(week_key) + 1 : -len("_packet")]
            else:
                brand_id = stem.replace("_packet", "")
            sha, size = _sha256_and_size(z)
            r2_key = f"{base_key}/{brand_id}/packet.zip"
            try:
                client.upload_file(str(z), bucket, r2_key)
            except Exception as e:
                print(f"Upload failed {z.name}: {e}", file=sys.stderr)
                report_path = packets_dir / "packet_delivery_report.json"
                existing = {}
                if report_path.exists():
                    try:
                        existing = json.loads(report_path.read_text())
                    except (json.JSONDecodeError, OSError):
                        pass
                existing["upload"] = {
                    "success": False,
                    "uploaded_brands": list(download_links["brands"]),
                    "errors": existing.get("upload", {}).get("errors", []) + [f"{brand_id}: {e}"],
                }
                existing["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                report_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
                return 1
            expires_at = datetime.now(timezone.utc).timestamp() + expiry_sec
            expires_iso = datetime.fromtimestamp(expires_at, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            presigned = client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": r2_key},
                ExpiresIn=expiry_sec,
            )
            download_links["brands"][brand_id] = {
                "url": presigned,
                "expires_at": expires_iso,
                "sha256": sha,
                "size_bytes": size,
            }
            print(f"  uploaded {z.name} -> {r2_key}")

    links_path = packets_dir / "download_links.json"
    links_path.write_text(json.dumps(download_links, indent=2), encoding="utf-8")
    print(f"Wrote {links_path}")

    report_path = packets_dir / "packet_delivery_report.json"
    existing = {}
    if report_path.exists():
        try:
            existing = json.loads(report_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    existing["run_id"] = existing.get("run_id", "")
    existing["week"] = week_key
    existing["upload"] = {
        "success": True,
        "uploaded_brands": list(download_links["brands"]),
        "errors": [],
    }
    existing["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
