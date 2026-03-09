#!/usr/bin/env python3
"""
Distribution Writer (Stage 10) — Upload rendered videos to Cloudflare R2 and write daily_batch.json.

Flow:
  1. Scan artifacts/video/<plan_id>/ for completed renders (video.mp4 + distribution_manifest.json).
  2. Classify each as long-form or shorts based on distribution_manifest.json format field.
  3. Copy to local staging: staging/<date>/{long|shorts}/<video_id>/
  4. Upload each video dir to R2: <date>/{long|shorts}/<video_id>/{video.mp4, thumb.jpg, distribution_manifest.json}
  5. Track progress in staging/<date>/upload_progress.json (resume-safe).
  6. After ALL uploads succeed, write staging/<date>/daily_batch.json with verifiable counts.

Usage:
  python scripts/video/distribution_writer.py --date 2026-03-08
  python scripts/video/distribution_writer.py --date 2026-03-08 --force   # re-upload all
  python scripts/video/distribution_writer.py --date 2026-03-08 --dry-run # no uploads

R2 credentials: env vars R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME
  or config/video/distribution_r2.yaml (non-secret fields only; secrets always from env).

Authority: docs/VIDEO_PIPELINE_SPEC.md §10, docs/VIDEO_PIPELINE_STORAGE_LAYOUT.md.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# -- repo-relative imports --
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import REPO_ROOT, load_json, load_yaml, write_atomically

logger = logging.getLogger("distribution_writer")

ARTIFACTS_VIDEO = REPO_ROOT / "artifacts" / "video"
STAGING_ROOT = REPO_ROOT / "staging"
SCHEMAS_DIR = REPO_ROOT / "schemas" / "video"

# R2 config defaults (non-secret)
R2_CONFIG_PATH = "config/video/distribution_r2.yaml"

# Retry settings
MAX_UPLOAD_RETRIES = 3
RETRY_BACKOFF_BASE = 2.0  # seconds


# ─── R2 Client ────────────────────────────────────────────────────────────────

def _get_r2_client():
    """Return a boto3 S3 client configured for Cloudflare R2."""
    try:
        import boto3
    except ImportError:
        raise RuntimeError("boto3 required for R2 uploads: pip install boto3")

    r2_cfg = load_yaml(R2_CONFIG_PATH)
    account_id = os.environ.get("R2_ACCOUNT_ID") or r2_cfg.get("account_id", "")
    access_key = os.environ.get("R2_ACCESS_KEY_ID") or ""
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY") or ""
    endpoint = os.environ.get("R2_ENDPOINT") or r2_cfg.get(
        "endpoint", f"https://{account_id}.r2.cloudflarestorage.com"
    )

    if not access_key or not secret_key:
        raise RuntimeError(
            "R2 credentials required: set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY env vars"
        )

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def _get_r2_bucket() -> str:
    r2_cfg = load_yaml(R2_CONFIG_PATH)
    return os.environ.get("R2_BUCKET_NAME") or r2_cfg.get("bucket_name", "pearl-video-handoff")


# ─── Upload with retry ────────────────────────────────────────────────────────

def _upload_file(
    client,
    bucket: str,
    local_path: Path,
    r2_key: str,
    dry_run: bool = False,
    chunk_size_mb: int | None = None,
) -> bool:
    """Upload a single file to R2 with retry. Uses multipart for large files when chunk_size_mb is set. Returns True on success."""
    for attempt in range(1, MAX_UPLOAD_RETRIES + 1):
        try:
            if dry_run:
                logger.info("  [dry-run] would upload %s → s3://%s/%s", local_path, bucket, r2_key)
                return True
            extra = {}
            if chunk_size_mb and local_path.stat().st_size > (chunk_size_mb * 1024 * 1024):
                try:
                    from boto3.s3.transfer import TransferConfig
                    extra["Config"] = TransferConfig(multipart_chunksize=chunk_size_mb * 1024 * 1024)
                except Exception:
                    pass
            client.upload_file(str(local_path), bucket, r2_key, **extra)
            logger.info("  uploaded %s → %s (attempt %d)", local_path.name, r2_key, attempt)
            return True
        except Exception as e:
            logger.warning("  upload failed (attempt %d/%d): %s", attempt, MAX_UPLOAD_RETRIES, e)
            if attempt < MAX_UPLOAD_RETRIES:
                time.sleep(RETRY_BACKOFF_BASE ** attempt)
    return False


def _upload_one_entry(
    entry: dict,
    client,
    bucket: str,
    dry_run: bool,
    chunk_size_mb: int | None,
) -> tuple[str, bool, float]:
    """Upload all files for one staged entry. Returns (video_id, success, duration_s)."""
    t0 = time.perf_counter()
    prefix = entry["r2_prefix"]
    staged_dir = entry["staged_dir"]
    vid_id = entry["video_id"]
    all_ok = True
    for filename in ("video.mp4", "thumb.jpg", "distribution_manifest.json"):
        local_file = staged_dir / filename
        if not local_file.exists():
            if filename == "thumb.jpg":
                continue
            logger.error("  missing required file: %s", local_file)
            all_ok = False
            break
        r2_key = prefix + filename
        if not _upload_file(client, bucket, local_file, r2_key, dry_run=dry_run, chunk_size_mb=chunk_size_mb):
            all_ok = False
            break
    duration_s = time.perf_counter() - t0
    return vid_id, all_ok, duration_s


# ─── Discover renders ─────────────────────────────────────────────────────────

def _discover_renders(batch_date: str) -> list[dict]:
    """Find all plan dirs that have both video.mp4 and distribution_manifest.json."""
    renders = []
    if not ARTIFACTS_VIDEO.exists():
        return renders
    for plan_dir in sorted(ARTIFACTS_VIDEO.iterdir()):
        if not plan_dir.is_dir() or plan_dir.name == "provenance":
            continue
        video_file = plan_dir / "video.mp4"
        manifest_file = plan_dir / "distribution_manifest.json"
        if not video_file.exists() or not manifest_file.exists():
            continue
        manifest = load_json(manifest_file)
        # Filter by batch_id or batch_date if present
        manifest_batch = manifest.get("batch_id", "")
        if batch_date and batch_date not in manifest_batch and manifest.get("batch_date", "") != batch_date:
            # Accept if no batch_date filter or if manifest has no batch filtering
            pass  # include all for now; filter can be tightened
        fmt = manifest.get("format", "landscape_16_9")
        category = _classify_format(fmt)
        resolved_thumb = _resolve_thumb(plan_dir, category)
        renders.append({
            "plan_id": plan_dir.name,
            "video_id": manifest.get("video_id", plan_dir.name),
            "format": fmt,
            "manifest": manifest,
            "video_path": video_file,
            "thumb_path": resolved_thumb,
            "thumb_source": ("generated" if resolved_thumb and "16x9" in resolved_thumb.name or resolved_thumb and "9x16" in resolved_thumb.name else "frame_extracted") if resolved_thumb else "none",
            "manifest_path": manifest_file,
        })
    return renders


def _classify_format(fmt: str) -> str:
    """Map format string to 'long' or 'shorts'."""
    shorts_formats = {"portrait_9_16", "square_1_1", "9:16", "1:1"}
    return "shorts" if fmt in shorts_formats else "long"


def _resolve_thumb(plan_dir: Path, category: str) -> Path | None:
    """Format-aware thumb selection: generated card > frame-extracted > none.

    Precedence:
      1. thumb_16x9.jpg (long) or thumb_9x16.jpg (shorts) — generated card
      2. thumb.jpg — legacy frame-extracted
      3. None — no thumb available
    """
    format_thumb = "thumb_16x9.jpg" if category == "long" else "thumb_9x16.jpg"
    candidates = [plan_dir / format_thumb, plan_dir / "thumb.jpg"]
    for c in candidates:
        if c.exists() and c.stat().st_size > 100:  # >100 bytes rules out placeholder stubs
            return c
    return None


# ─── Stage to local ──────────────────────────────────────────────────────────

def _stage_locally(renders: list[dict], batch_date: str) -> list[dict]:
    """Copy renders into staging/<date>/{long|shorts}/<video_id>/. Returns staged entries."""
    staging_date = STAGING_ROOT / batch_date
    staged = []
    for r in renders:
        category = _classify_format(r["format"])
        vid_dir = staging_date / category / r["video_id"]
        vid_dir.mkdir(parents=True, exist_ok=True)

        # Copy video
        dest_video = vid_dir / "video.mp4"
        if not dest_video.exists():
            shutil.copy2(r["video_path"], dest_video)

        # Copy thumb (if exists)
        dest_thumb = vid_dir / "thumb.jpg"
        if r["thumb_path"] and not dest_thumb.exists():
            shutil.copy2(r["thumb_path"], dest_thumb)

        # Copy manifest
        dest_manifest = vid_dir / "distribution_manifest.json"
        if not dest_manifest.exists():
            shutil.copy2(r["manifest_path"], dest_manifest)

        staged.append({
            **r,
            "category": category,
            "staged_dir": vid_dir,
            "r2_prefix": f"{batch_date}/{category}/{r['video_id']}/",
        })
    return staged


# ─── Upload progress tracking ────────────────────────────────────────────────

def _load_progress(batch_date: str) -> dict:
    progress_file = STAGING_ROOT / batch_date / "upload_progress.json"
    if progress_file.exists():
        return load_json(progress_file)
    return {"batch_date": batch_date, "videos": {}}


def _save_progress(batch_date: str, progress: dict):
    progress_file = STAGING_ROOT / batch_date / "upload_progress.json"
    write_atomically(progress_file, progress)


# ─── Upload batch to R2 ──────────────────────────────────────────────────────

def _upload_batch(staged: list[dict], batch_date: str, force: bool, dry_run: bool) -> tuple[int, int]:
    """Upload all staged videos to R2 (parallel when configured). Returns (success_count, fail_count)."""
    r2_cfg = load_yaml(R2_CONFIG_PATH)
    parallel = int(r2_cfg.get("parallel_uploads", 1))
    chunk_mb = r2_cfg.get("chunk_size_mb")
    chunk_size_mb = int(chunk_mb) if chunk_mb is not None else None

    if dry_run:
        client = None
        bucket = _get_r2_bucket()
    else:
        client = _get_r2_client()
        bucket = _get_r2_bucket()

    progress = _load_progress(batch_date)
    to_upload = []
    for entry in staged:
        vid_id = entry["video_id"]
        if progress.get("videos", {}).get(vid_id) == "uploaded" and not force:
            logger.info("  skip %s (already uploaded)", vid_id)
            progress.setdefault("videos", {})[vid_id] = "uploaded"
            continue
        to_upload.append(entry)

    success = len(staged) - len(to_upload)
    failed = 0

    if not to_upload:
        return success, failed

    if parallel <= 1:
        for entry in to_upload:
            vid_id, all_ok, dur = _upload_one_entry(entry, client, bucket, dry_run, chunk_size_mb)
            if all_ok:
                progress.setdefault("videos", {})[vid_id] = "uploaded"
                success += 1
                logger.info("  %s uploaded in %.1fs", vid_id, dur)
            else:
                progress.setdefault("videos", {})[vid_id] = "failed"
                failed += 1
            _save_progress(batch_date, progress)
    else:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(_upload_one_entry, entry, client, bucket, dry_run, chunk_size_mb): entry
                for entry in to_upload
            }
            for fut in as_completed(futures):
                vid_id, all_ok, dur = fut.result()
                if all_ok:
                    progress.setdefault("videos", {})[vid_id] = "uploaded"
                    success += 1
                    logger.info("  %s uploaded in %.1fs", vid_id, dur)
                else:
                    progress.setdefault("videos", {})[vid_id] = "failed"
                    failed += 1
                _save_progress(batch_date, progress)

    return success, failed


# ─── Write daily_batch.json ───────────────────────────────────────────────────

def _write_daily_batch(staged: list[dict], batch_date: str, dry_run: bool) -> Path:
    """Write daily_batch.json after all uploads succeed."""
    long_form = []
    shorts = []

    for entry in staged:
        video_entry = {
            "video_id": entry["video_id"],
            "plan_id": entry["plan_id"],
            "r2_prefix": entry["r2_prefix"],
            "distribution_manifest_key": entry["r2_prefix"] + "distribution_manifest.json",
            "title": entry["manifest"].get("title", ""),
            "primary_asset_ids": entry["manifest"].get("primary_asset_ids", []),
        }
        if entry["category"] == "long":
            long_form.append(video_entry)
        else:
            shorts.append(video_entry)

    batch = {
        "schema_version": "1.0",
        "batch_date": batch_date,
        "batch_id": f"batch-{batch_date}-001",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "long_form": long_form,
        "shorts": shorts,
        "long_form_count": len(long_form),
        "shorts_count": len(shorts),
    }

    out_path = STAGING_ROOT / batch_date / "daily_batch.json"
    if dry_run:
        logger.info("[dry-run] would write %s (%d long, %d shorts)", out_path, len(long_form), len(shorts))
    else:
        write_atomically(out_path, batch)
        logger.info("wrote %s (%d long, %d shorts)", out_path, len(long_form), len(shorts))

    # Also upload daily_batch.json to R2 at <date>/daily_batch.json
    if not dry_run:
        try:
            client = _get_r2_client()
            bucket = _get_r2_bucket()
            _upload_file(client, bucket, out_path, f"{batch_date}/daily_batch.json")
        except Exception as e:
            logger.error("failed to upload daily_batch.json to R2: %s", e)

    return out_path


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Distribution Writer — Stage 10: upload to R2 + daily_batch.json")
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        help="Batch date (YYYY-MM-DD). Default: today UTC.")
    parser.add_argument("--force", action="store_true", help="Re-upload even if already uploaded.")
    parser.add_argument("--dry-run", action="store_true", help="Log what would happen without uploading.")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    batch_date = args.date
    logger.info("=== Distribution Writer: batch_date=%s ===", batch_date)

    # 1. Discover completed renders
    renders = _discover_renders(batch_date)
    if not renders:
        logger.warning("No completed renders found in %s", ARTIFACTS_VIDEO)
        sys.exit(0)
    logger.info("found %d completed renders", len(renders))

    # Log thumbnail resolution per render
    for r in renders:
        logger.info("  %s: thumb_source=%s thumb=%s", r["video_id"], r["thumb_source"],
                     r["thumb_path"].name if r["thumb_path"] else "none")

    # 2. Stage locally
    staged = _stage_locally(renders, batch_date)
    logger.info("staged %d videos to %s", len(staged), STAGING_ROOT / batch_date)

    # 3. Upload to R2
    success, failed = _upload_batch(staged, batch_date, force=args.force, dry_run=args.dry_run)
    logger.info("upload results: %d succeeded, %d failed", success, failed)

    if failed > 0:
        logger.error("%d videos failed to upload — daily_batch.json NOT written", failed)
        sys.exit(1)

    # 4. Write daily_batch.json (only if all uploads succeeded)
    _write_daily_batch(staged, batch_date, dry_run=args.dry_run)
    logger.info("=== Distribution Writer complete ===")


if __name__ == "__main__":
    main()
