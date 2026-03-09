"""
API: /api/me, /api/packets, POST /api/packets/{week_key}/{brand_id}/signed-url, /api/audit/recent.
Mint short-lived R2 URL (15 min); audit every request.
"""
from __future__ import annotations

import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from .auth import get_request_email
from .models import get_conn, init_db, insert_audit, packets_for_week, recent_audit, user_by_email, user_grants

router = APIRouter(prefix="/api", tags=["packets"])

# Rate limit: max 10 mints per user per 15 minutes (in-memory, resets on restart)
_MINT_TIMES: defaultdict[str, list[float]] = defaultdict(list)
MINT_WINDOW_SEC = 15 * 60
MINT_MAX_PER_WINDOW = 10


def _get_db_path() -> Path:
    return Path(os.environ.get("PORTAL_DB_PATH", "") or (Path(__file__).resolve().parent / "data" / "portal.db"))


def _get_user(request: Request):
    email = get_request_email(request.headers)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated (missing CF Access email or OVERRIDE_EMAIL)")
    conn = get_conn(_get_db_path())
    try:
        init_db(conn)
        user = user_by_email(conn, email)
        if not user:
            insert_audit(conn, None, None, None, "list", request.client.host if request.client else None, request.headers.get("user-agent"), "denied")
            raise HTTPException(status_code=403, detail="No portal access for this user")
        return conn, user
    finally:
        conn.close()


def _get_user_conn(request: Request):
    conn = get_conn(_get_db_path())
    init_db(conn)
    return conn


@router.get("/me")
def api_me(request: Request):
    """Return user profile + granted brands."""
    conn = _get_user_conn(request)
    try:
        email = get_request_email(request.headers)
        if not email:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = user_by_email(conn, email)
        if not user:
            raise HTTPException(status_code=403, detail="No portal access")
        brands = user_grants(conn, user["id"])
        insert_audit(conn, user["id"], None, None, "list", request.client.host if request.client else None, request.headers.get("user-agent"))
        return {"email": user["email"], "display_name": user["display_name"], "brand_ids": brands}
    finally:
        conn.close()


@router.get("/packets")
def api_packets(request: Request, week: str | None = None):
    """List packets for user's brands. week=YYYY-WW; default current ISO week."""
    conn = _get_user_conn(request)
    try:
        email = get_request_email(request.headers)
        if not email:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = user_by_email(conn, email)
        if not user:
            raise HTTPException(status_code=403, detail="No portal access")
        brands = user_grants(conn, user["id"])
        if not week:
            now = datetime.now(timezone.utc)
            y, w, _ = now.isocalendar()
            week = f"{y}-W{w:02d}"
        rows = packets_for_week(conn, week, brand_ids=brands if brands else None)
        insert_audit(conn, user["id"], None, week, "list", request.client.host if request.client else None, request.headers.get("user-agent"))
        return {"week": week, "packets": rows}
    finally:
        conn.close()


def _mint_signed_url(r2_key: str, expiry_sec: int = 15 * 60) -> tuple[str, str]:
    """Return (url, expires_at_iso). Uses env R2_*."""
    try:
        import boto3
    except ImportError:
        raise HTTPException(status_code=500, detail="boto3 required for R2")
    bucket = os.environ.get("R2_BUCKET_NAME", "")
    if not bucket:
        raise HTTPException(status_code=500, detail="R2_BUCKET_NAME not set")
    account_id = os.environ.get("R2_ACCOUNT_ID", "")
    access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    if not access_key or not secret_key:
        raise HTTPException(status_code=500, detail="R2 credentials not set")
    endpoint = os.environ.get("R2_ENDPOINT") or f"https://{account_id}.r2.cloudflarestorage.com"
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )
    url = client.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": r2_key}, ExpiresIn=expiry_sec)
    expires_at = datetime.now(timezone.utc).timestamp() + expiry_sec
    expires_iso = datetime.fromtimestamp(expires_at, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return url, expires_iso


@router.post("/packets/{week_key}/{brand_id}/signed-url")
def api_mint_signed_url(request: Request, week_key: str, brand_id: str):
    """Mint 15-min R2 signed URL; audit; rate-limit."""
    conn = _get_user_conn(request)
    try:
        email = get_request_email(request.headers)
        if not email:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = user_by_email(conn, email)
        if not user:
            insert_audit(conn, None, brand_id, week_key, "mint_link", request.client.host if request.client else None, request.headers.get("user-agent"), "denied")
            raise HTTPException(status_code=403, detail="No portal access")
        brands = user_grants(conn, user["id"])
        if brand_id not in brands:
            insert_audit(conn, user["id"], brand_id, week_key, "mint_link", request.client.host if request.client else None, request.headers.get("user-agent"), "denied")
            raise HTTPException(status_code=403, detail="Not allowed for this brand")

        now = time.time()
        key = user["id"]
        _MINT_TIMES[key] = [t for t in _MINT_TIMES[key] if now - t < MINT_WINDOW_SEC]
        if len(_MINT_TIMES[key]) >= MINT_MAX_PER_WINDOW:
            insert_audit(conn, user["id"], brand_id, week_key, "mint_link", request.client.host if request.client else None, request.headers.get("user-agent"), "denied")
            raise HTTPException(status_code=429, detail="Too many download links; try again later")

        rows = packets_for_week(conn, week_key, brand_ids=[brand_id])
        if not rows:
            insert_audit(conn, user["id"], brand_id, week_key, "mint_link", request.client.host if request.client else None, request.headers.get("user-agent"), "error")
            raise HTTPException(status_code=404, detail="Packet not found")
        r2_key = rows[0]["r2_key"]
        url, expires_at = _mint_signed_url(r2_key, expiry_sec=15 * 60)
        _MINT_TIMES[key].append(now)
        insert_audit(conn, user["id"], brand_id, week_key, "mint_link", request.client.host if request.client else None, request.headers.get("user-agent"))
        return {"url": url, "expires_at": expires_at}
    finally:
        conn.close()


@router.get("/audit/recent")
def api_audit_recent(request: Request, limit: int = 100):
    """Recent access events (admin use)."""
    conn = _get_user_conn(request)
    try:
        email = get_request_email(request.headers)
        if not email:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = user_by_email(conn, email)
        if not user:
            raise HTTPException(status_code=403, detail="No portal access")
        events = recent_audit(conn, limit=min(limit, 500))
        return {"events": events}
    finally:
        conn.close()
