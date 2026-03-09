#!/usr/bin/env python3
"""
Wipe staging after partner acknowledgement.

Hard rule: NO wipe unless batch_acknowledged.json exists AND failed_count == 0.

Flow:
  1. For each staging/<date>/ directory, check for batch_acknowledged.json.
  2. If missing → skip (partner hasn't ingested yet).
  3. If present but failed_count > 0 → skip and warn (some videos failed partner ingest).
  4. If present and failed_count == 0 → delete staging/<date>/ and optionally R2 prefix.

Usage:
  python scripts/video/wipe_staging_after_ack.py                    # check all staging dates
  python scripts/video/wipe_staging_after_ack.py --date 2026-03-08  # check specific date
  python scripts/video/wipe_staging_after_ack.py --dry-run           # log only, no deletion
  python scripts/video/wipe_staging_after_ack.py --wipe-r2           # also delete R2 date prefix
  python scripts/video/wipe_staging_after_ack.py --allow-failures    # wipe even if failed_count > 0

Authority: docs/VIDEO_PIPELINE_SPEC.md §10, docs/VIDEO_PIPELINE_STORAGE_LAYOUT.md.
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import REPO_ROOT

logger = logging.getLogger("wipe_staging")

STAGING_ROOT = REPO_ROOT / "staging"


def _check_ack(staging_date_dir: Path, allow_failures: bool) -> tuple[bool, str]:
    """Check if batch_acknowledged.json exists and meets wipe criteria.
    Returns (ok_to_wipe, reason).
    """
    ack_file = staging_date_dir / "batch_acknowledged.json"

    if not ack_file.exists():
        # Also check R2 (partner may write directly there)
        return False, "batch_acknowledged.json not found — partner has not acknowledged"

    try:
        ack = json.loads(ack_file.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"batch_acknowledged.json unreadable: {e}"

    failed_count = ack.get("failed_count", -1)
    if failed_count < 0:
        return False, "batch_acknowledged.json missing failed_count"

    if failed_count > 0 and not allow_failures:
        failed_ids = ack.get("failed_ids", [])
        return False, (
            f"failed_count={failed_count} (not 0) — partner reported failures: "
            f"{failed_ids[:5]}{'...' if len(failed_ids) > 5 else ''}"
        )

    return True, f"acknowledged at {ack.get('acknowledged_at', '?')}, failed_count={failed_count}"


def _wipe_local(staging_date_dir: Path, dry_run: bool) -> bool:
    """Delete the staging/<date>/ directory."""
    if dry_run:
        logger.info("  [dry-run] would delete %s", staging_date_dir)
        return True
    try:
        shutil.rmtree(staging_date_dir)
        logger.info("  deleted %s", staging_date_dir)
        return True
    except Exception as e:
        logger.error("  failed to delete %s: %s", staging_date_dir, e)
        return False


def _wipe_r2(batch_date: str, dry_run: bool) -> bool:
    """Delete all R2 objects under <date>/ prefix."""
    try:
        import os
        import boto3
        from _config import load_yaml

        r2_cfg = load_yaml("config/video/distribution_r2.yaml")
        account_id = os.environ.get("R2_ACCOUNT_ID") or r2_cfg.get("account_id", "")
        endpoint = os.environ.get("R2_ENDPOINT") or r2_cfg.get(
            "endpoint", f"https://{account_id}.r2.cloudflarestorage.com"
        )
        bucket = os.environ.get("R2_BUCKET_NAME") or r2_cfg.get("bucket_name", "pearl-video-handoff")

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=os.environ.get("R2_ACCESS_KEY_ID", ""),
            aws_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY", ""),
            region_name="auto",
        )

        prefix = f"{batch_date}/"
        paginator = client.get_paginator("list_objects_v2")
        keys_to_delete = []
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys_to_delete.append({"Key": obj["Key"]})

        if not keys_to_delete:
            logger.info("  R2 prefix %s is empty or already deleted", prefix)
            return True

        if dry_run:
            logger.info("  [dry-run] would delete %d R2 objects under %s", len(keys_to_delete), prefix)
            return True

        # Delete in batches of 1000 (S3 limit)
        for i in range(0, len(keys_to_delete), 1000):
            batch = keys_to_delete[i : i + 1000]
            client.delete_objects(Bucket=bucket, Delete={"Objects": batch})

        logger.info("  deleted %d R2 objects under %s", len(keys_to_delete), prefix)
        return True

    except ImportError:
        logger.warning("  boto3 not installed — skipping R2 wipe")
        return False
    except Exception as e:
        logger.error("  R2 wipe failed: %s", e)
        return False


def main():
    parser = argparse.ArgumentParser(description="Wipe staging after partner ack (no ack = no wipe)")
    parser.add_argument("--date", default=None, help="Specific date to check (YYYY-MM-DD). Default: all.")
    parser.add_argument("--dry-run", action="store_true", help="Log only, no deletions.")
    parser.add_argument("--wipe-r2", action="store_true", help="Also delete R2 date prefix.")
    parser.add_argument("--allow-failures", action="store_true",
                        help="Wipe even if failed_count > 0 (use with caution).")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if not STAGING_ROOT.exists():
        logger.info("No staging directory at %s — nothing to wipe", STAGING_ROOT)
        sys.exit(0)

    # Determine which dates to check
    if args.date:
        dates = [STAGING_ROOT / args.date]
    else:
        dates = sorted(d for d in STAGING_ROOT.iterdir() if d.is_dir())

    if not dates:
        logger.info("No staging date directories found")
        sys.exit(0)

    wiped = 0
    skipped = 0
    for date_dir in dates:
        batch_date = date_dir.name
        logger.info("checking staging/%s ...", batch_date)

        ok, reason = _check_ack(date_dir, allow_failures=args.allow_failures)
        if not ok:
            logger.info("  SKIP: %s", reason)
            skipped += 1
            continue

        logger.info("  ACK OK: %s", reason)

        # Wipe local staging
        if _wipe_local(date_dir, dry_run=args.dry_run):
            wiped += 1

        # Optionally wipe R2
        if args.wipe_r2:
            _wipe_r2(batch_date, dry_run=args.dry_run)

    logger.info("=== Done: %d wiped, %d skipped ===", wiped, skipped)


if __name__ == "__main__":
    main()
