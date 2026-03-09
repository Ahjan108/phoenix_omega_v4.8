"""
Brand Admin Portal: login-required packet downloads.
Auth: Cloudflare Access (email header). No permanent public links; mint 15-min signed URL on click.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .routes_packets import router as packets_router

app = FastAPI(
    title="Brand Admin Portal",
    description="Packet downloads for brand admins (CF Access + short-lived links).",
    version="1.0",
)
app.include_router(packets_router)

STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/admin/packets", response_class=HTMLResponse)
def admin_packets_page(request: Request):
    """Serve the packets table UI. Login handled by Cloudflare Access."""
    html = (Path(__file__).resolve().parent / "templates" / "packets.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/admin/login")
def admin_login_redirect():
    """Cloudflare Access handles /admin/login; this is a fallback message."""
    return {"message": "Protect this path with Cloudflare Access (Google/Microsoft + MFA)."}


@app.get("/")
def root():
    return {"service": "admin_portal", "docs": "/docs", "packets": "/admin/packets"}
