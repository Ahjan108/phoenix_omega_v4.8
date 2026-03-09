#!/usr/bin/env python3
"""
Notify each brand admin with their download link and release_day.
Per-brand retry; failures logged to notify_failures.json; does not fail whole run.
SMTP and Slack webhook URLs/credentials from env only.

Usage:
  python scripts/release/notify_brand_admins.py --download-links artifacts/brand_packets/2026-W11/download_links.json
  python scripts/release/notify_brand_admins.py --week-start 2026-03-10 --channel email --channel slack
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTACTS_CONFIG = REPO_ROOT / "config" / "release" / "brand_admin_contacts.yaml"
MAX_RETRIES = 2
RETRY_BACKOFF_SEC = 2.0


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _release_day_for_brand(packets_dir: Path, brand_id: str) -> str:
    release_file = packets_dir / brand_id / "release_day.txt"
    if release_file.exists():
        return release_file.read_text().strip()
    return ""


def _send_email(brand_id: str, to_addr: str, link: str, release_day: str, portal_url: str | None = None) -> str | None:
    """Return None on success, error string on failure. Uses env SMTP_*. If portal_url set, message points to portal instead of direct link."""
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    from_addr = os.environ.get("NOTIFY_FROM_EMAIL", smtp_user or "noreply@example.com")
    if not smtp_host:
        return "SMTP_HOST not set"
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    subject = f"Brand packet ready: {brand_id}"
    if portal_url:
        body = f"Your weekly packet is ready.\n\nLog in to the portal to download: {portal_url}\n\nRelease day: {release_day}\n\nUpload to Google Play on the assigned day."
    else:
        body = f"Your weekly packet is ready.\n\nDownload link (expires soon): {link}\n\nRelease day: {release_day}\n\nUpload to Google Play on the assigned day."
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            if smtp_user and smtp_pass:
                s.starttls()
                s.login(smtp_user, smtp_pass)
            s.sendmail(from_addr, [to_addr], msg.as_string())
    except Exception as e:
        return str(e)
    return None


def _send_slack(brand_id: str, webhook_url: str, link: str, release_day: str, portal_url: str | None = None) -> str | None:
    """Return None on success, error string on failure. If portal_url set, message points to portal."""
    try:
        import urllib.request
        if portal_url:
            text = f"Brand packet ready: *{brand_id}*\nLog in to download: <{portal_url}>\nRelease day: {release_day}\nUpload to Google Play on the assigned day."
        else:
            text = f"Brand packet ready: *{brand_id}*\nDownload: <{link}>\nRelease day: {release_day}\nUpload to Google Play on the assigned day."
        payload = {"text": text}
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status >= 400:
                return f"HTTP {resp.status}"
    except Exception as e:
        return str(e)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Notify brand admins (email/Slack); per-brand retry, dead-letter log.")
    ap.add_argument("--download-links", type=Path, default=None)
    ap.add_argument("--week-start", default=None)
    ap.add_argument("--channel", action="append", choices=["email", "slack"], help="Can repeat")
    ap.add_argument("--portal-url", default=None, help="When set, notify with 'log in to portal' link instead of direct download URL")
    args = ap.parse_args()

    if args.download_links:
        links_path = Path(args.download_links)
        if not links_path.is_absolute():
            links_path = REPO_ROOT / links_path
    elif args.week_start:
        import sys
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from scripts.release.week_utils import iso_week_from_week_start
        week_key = iso_week_from_week_start(args.week_start)
        links_path = REPO_ROOT / "artifacts" / "brand_packets" / week_key / "download_links.json"
    else:
        print("Provide --download-links or --week-start", file=sys.stderr)
        return 1

    if not links_path.exists():
        print(f"Download links not found: {links_path}", file=sys.stderr)
        return 1

    packets_dir = links_path.parent
    week_key = packets_dir.name
    data = json.loads(links_path.read_text())
    brands_data = data.get("brands") or {}

    contacts = _load_yaml(CONTACTS_CONFIG)
    contacts_map = (contacts.get("brands") if isinstance(contacts, dict) else None) or (contacts if isinstance(contacts, dict) else {})

    channels = args.channel or ["email", "slack"]
    failures: list[dict] = []
    success_per_brand: dict[str, list[str]] = {}
    failed_brands: list[str] = []

    for brand_id, info in brands_data.items():
        brand_contacts = contacts_map.get(brand_id) if isinstance(contacts_map, dict) else {}
        if not brand_contacts:
            continue
        url = info.get("url", "")
        if not url or url == "(dry-run)":
            continue
        release_day = _release_day_for_brand(packets_dir, brand_id)
        success_per_brand[brand_id] = []
        for channel in channels:
            err = None
            for attempt in range(1, MAX_RETRIES + 1):
                if channel == "email":
                    to = brand_contacts.get("email")
                    if not to:
                        err = "no email in config"
                        break
                    err = _send_email(brand_id, to, url, release_day, portal_url=args.portal_url)
                else:
                    webhook = brand_contacts.get("slack_webhook") or os.environ.get(f"SLACK_WEBHOOK_{brand_id.upper().replace('-', '_')}")
                    if not webhook:
                        err = "no slack_webhook in config or env"
                        break
                    err = _send_slack(brand_id, webhook, url, release_day, portal_url=args.portal_url)
                if err is None:
                    success_per_brand[brand_id].append(channel)
                    break
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SEC ** attempt)
            if err is not None:
                failures.append({
                    "brand_id": brand_id,
                    "channel": channel,
                    "error": err,
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                })
                if brand_id not in failed_brands:
                    failed_brands.append(brand_id)

    run_id = str(uuid.uuid4())
    notify_failures_path = packets_dir / "notify_failures.json"
    if failures:
        payload = {"run_id": run_id, "week_key": week_key, "failures": failures}
        notify_failures_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Notify failures written to {notify_failures_path}", file=sys.stderr)

    report_path = packets_dir / "packet_delivery_report.json"
    existing = {}
    if report_path.exists():
        try:
            existing = json.loads(report_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    existing["run_id"] = existing.get("run_id") or run_id
    existing["week"] = week_key
    existing["notify"] = {
        "run_id": run_id,
        "week_key": week_key,
        "success_per_brand": success_per_brand,
        "failed_brands": failed_brands,
        "notify_failures_path": str(notify_failures_path) if failures else "",
    }
    existing["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    for bid, chs in success_per_brand.items():
        if chs:
            print(f"  notified {bid}: {', '.join(chs)}")
    for f in failures:
        print(f"  FAIL {f['brand_id']} {f['channel']}: {f['error']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
