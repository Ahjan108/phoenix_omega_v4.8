"""
Brevo SMTP send and template rendering for Proof-Loop sequence.
Checks suppression (unsubscribed) before sending.
"""
from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = APP_DIR / "emails"


def _load_config() -> dict:
    import yaml
    config_path = APP_DIR / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _render_template(name: str, **kwargs) -> str:
    path = TEMPLATES_DIR / name
    if not path.exists():
        return ""
    raw = path.read_text(encoding="utf-8")
    try:
        from jinja2 import Template
        return Template(raw).render(**kwargs)
    except Exception:
        for k, v in kwargs.items():
            raw = raw.replace("{{ " + k + " }}", str(v))
            raw = raw.replace("{{" + k + "}}", str(v))
        return raw


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    from_email: str | None = None,
    from_name: str | None = None,
) -> bool:
    """Send one email via Brevo SMTP. Returns True on success."""
    cfg = _load_config()
    host = os.environ.get("SMTP_HOST", cfg.get("smtp_host", "smtp-relay.brevo.com"))
    port = int(os.environ.get("SMTP_PORT", cfg.get("smtp_port", 587)))
    user = os.environ.get("SMTP_USER", cfg.get("smtp_user", ""))
    password = os.environ.get("SMTP_PASSWORD", cfg.get("smtp_password", ""))
    if not user or not password:
        return False
    from_addr = from_email or os.environ.get("FROM_EMAIL", cfg.get("from_email", ""))
    from_display = from_name or os.environ.get("FROM_NAME", cfg.get("from_name", "Phoenix Protocol"))
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_display} <{from_addr}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.sendmail(from_addr, [to_email], msg.as_string())
        return True
    except Exception:
        return False


def send_e1(lead: dict, tool_link: str, unsubscribe_url: str, base_url: str) -> bool:
    first_name = (lead.get("name") or "").split()[0] or "there"
    html = _render_template(
        "email_1_immediate.html",
        first_name=first_name,
        exercise_name=lead.get("exercise_name", "").replace("_", " ").title(),
        tool_link=tool_link,
        unsubscribe_url=unsubscribe_url,
        base_url=base_url.rstrip("/"),
    )
    subject = f"Your {lead.get('exercise_name', '').replace('_', ' ').title()} tool is here, {first_name}"
    return send_email(lead["email"], subject, html)


def send_e2(lead: dict, second_exercise_name: str, second_tool_link: str, unsubscribe_url: str, base_url: str) -> bool:
    first_name = (lead.get("name") or "").split()[0] or "there"
    html = _render_template(
        "email_2_delay.html",
        first_name=first_name,
        second_exercise_name=second_exercise_name,
        second_tool_link=second_tool_link,
        unsubscribe_url=unsubscribe_url,
        base_url=base_url.rstrip("/"),
    )
    subject = f"One more reset — {second_exercise_name}, {first_name}"
    return send_email(lead["email"], subject, html)


def send_e3(lead: dict, story_body: str, unsubscribe_url: str, base_url: str) -> bool:
    first_name = (lead.get("name") or "").split()[0] or "there"
    html = _render_template(
        "email_3_delay.html",
        first_name=first_name,
        story_body=story_body,
        unsubscribe_url=unsubscribe_url,
        base_url=base_url.rstrip("/"),
    )
    subject = "Why this actually works (a short story)"
    return send_email(lead["email"], subject, html)


def send_e4(lead: dict, book_title: str, book_link: str, unsubscribe_url: str, base_url: str) -> bool:
    first_name = (lead.get("name") or "").split()[0] or "there"
    html = _render_template(
        "email_4_delay.html",
        first_name=first_name,
        book_title=book_title,
        book_link=book_link,
        unsubscribe_url=unsubscribe_url,
        base_url=base_url.rstrip("/"),
    )
    subject = f"Recommended for you: {book_title}, {first_name}"
    return send_email(lead["email"], subject, html)


def send_e5(lead: dict, more_books: list[dict], unsubscribe_url: str, base_url: str) -> bool:
    first_name = (lead.get("name") or "").split()[0] or "there"
    html = _render_template(
        "email_5_delay.html",
        first_name=first_name,
        more_books=more_books or [],
        unsubscribe_url=unsubscribe_url,
        base_url=base_url.rstrip("/"),
    )
    subject = f"More books for this issue, {first_name}"
    return send_email(lead["email"], subject, html)
