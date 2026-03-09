#!/usr/bin/env python3
"""
Multi-hub funnel: 6-section landing page, form capture, Proof-Loop email sequence (E1–E5), GHL push.
Supports all 12 topic hubs (burnout, anxiety, overthinking, etc.) via dynamic routing.
Persistence: SQLite (leads + APScheduler jobstore). No JSONL. email_mode: "ghl" (GHL sends) or "smtp" (app sends via Brevo).
"""
from __future__ import annotations

import datetime
import os
import re
import uuid
from pathlib import Path

import yaml
from flask import Flask, redirect, render_template, request

from db import (
    get_lead,
    init_db,
    insert_lead,
    is_unsubscribed,
    mark_e1_sent,
    set_unsubscribed_by_token,
    update_ghl_pushed,
    get_database_url,
)
from email_send import send_e1, send_e2, send_e3, send_e4, send_e5

# Paths
APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent.parent if (APP_DIR.parent.parent / "config").exists() else APP_DIR
CONFIG_FREEBIES = REPO_ROOT / "config" / "freebies"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json(path: Path) -> dict | list:
    import json
    if not path.exists():
        return {} if "yaml" in str(path) else []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_funnel_config() -> dict:
    cfg_path = APP_DIR / "config.yaml"
    if not cfg_path.exists():
        return {}
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    # Env overrides
    for key in ("email_mode", "send_email_5", "database_path", "ghl_api_key", "ghl_location_id",
                "smtp_host", "smtp_port", "smtp_user", "smtp_password", "from_email", "from_name",
                "ga4_measurement_id", "base_url"):
        env_key = key.upper()
        if env_key in os.environ:
            cfg[key] = os.environ[env_key]
    return cfg


def get_exercises() -> list[dict]:
    p = CONFIG_FREEBIES / "exercises_landing.json"
    data = load_json(p)
    if isinstance(data, dict):
        return data.get("exercises", [])
    return []


def get_exercise_pairs() -> dict:
    """Returns pairing map. Supports both flat YAML and nested under exercise_pairs key."""
    raw = load_yaml(CONFIG_FREEBIES / "exercise_pairs.yaml")
    return raw.get("exercise_pairs", raw) if isinstance(raw, dict) else {}


def get_book_map() -> dict:
    return load_yaml(CONFIG_FREEBIES / "freebie_to_book_map.yaml")


def get_funnel_sections(hub: str = "burnout_reset") -> dict:
    sections = load_yaml(CONFIG_FREEBIES / "funnel_sections.yaml")
    return sections.get(hub, sections.get("burnout_reset", {}))


def get_proof_loop() -> dict:
    """Load all hub configs from funnel_proof_loop.yaml."""
    return load_yaml(CONFIG_FREEBIES / "funnel_proof_loop.yaml")


def resolve_hub(slug: str) -> tuple[str, dict] | tuple[None, None]:
    """Resolve a URL slug (e.g. 'burnout-reset') to (hub_key, hub_config).
    Returns (None, None) if not found."""
    proof_loop = get_proof_loop()
    # Direct match: slug matches hub key with hyphens→underscores
    hub_key = slug.replace("-", "_")
    if hub_key in proof_loop:
        return hub_key, proof_loop[hub_key]
    # Fallback: try adding _reset
    hub_key_with_reset = hub_key if hub_key.endswith("_reset") else f"{hub_key}_reset"
    if hub_key_with_reset in proof_loop:
        return hub_key_with_reset, proof_loop[hub_key_with_reset]
    return None, None


# Build valid hub slugs for routing
def _get_all_hub_slugs() -> list[str]:
    """Return all valid URL slugs for landing pages."""
    proof_loop = get_proof_loop()
    slugs = []
    for hub_key in proof_loop:
        slugs.append(hub_key.replace("_", "-"))
    return slugs


def get_story(topic: str, story_id: str) -> str:
    stories_file = APP_DIR / "stories" / f"{topic}.md"
    if not stories_file.exists():
        return ""
    text = stories_file.read_text(encoding="utf-8")
    pattern = rf"##\s*{re.escape(story_id)}\s*\n(.*?)(?=\n##\s|\Z)"
    m = re.search(pattern, text, re.DOTALL)
    if m:
        block = m.group(1).strip()
        for para in block.split("\n\n"):
            if para.strip() and not para.strip().startswith("**"):
                return para.strip()[:500]
    return ""


def exercise_id_to_tool_path(exercise_id: str) -> str:
    kebab = (exercise_id or "").strip().lower().replace("_", "-")
    return f"/breathwork/tools/{kebab}.html"


def get_book_by_slug(slug: str) -> dict | None:
    """Resolve slug to book info. Prefer explicit slugs section for deterministic lookup and attribution."""
    book_map = get_book_map() or {}
    slugs = book_map.get("slugs") or {}
    if isinstance(slugs, dict) and slug in slugs:
        entry = dict(slugs[slug])
        entry.setdefault("book_url", f"{_base_url()}/books/{slug}")
        entry.setdefault("redirect_url", entry.get("book_url"))
        return entry
    base = _base_url()
    our_url = f"{base}/books/{slug}"
    for key, val in book_map.items():
        if key == "slugs" or not isinstance(val, dict):
            continue
        if val.get("slug") == slug:
            out = dict(val)
            out.setdefault("book_url", our_url)
            out.setdefault("redirect_url", out.get("book_url"))
            return out
    return {"book_url": our_url, "book_title": slug.replace("-", " ").title(), "redirect_url": our_url}


# App
app = Flask(__name__, template_folder=str(APP_DIR / "templates"))
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

# Config and DB init
FUNNEL_CFG = get_funnel_config()
DATABASE_PATH = APP_DIR / FUNNEL_CFG.get("database_path", "data/funnel.db")
if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = APP_DIR / DATABASE_PATH
init_db(DATABASE_PATH)

# Scheduler (smtp mode only)
_scheduler = None


def get_scheduler():
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    if FUNNEL_CFG.get("email_mode") != "smtp":
        return None
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
        jobstore_url = os.environ.get("DATABASE_URL") or get_database_url(DATABASE_PATH)
        store = SQLAlchemyJobStore(url=jobstore_url)
        _scheduler = BackgroundScheduler(jobstores={"default": store})
        _scheduler.job_defaults["coalesce"] = True
        _scheduler.job_defaults["max_instances"] = 1
        _scheduler.job_defaults["misfire_grace_time"] = 300
        _scheduler.start()
    except Exception:
        _scheduler = None
    return _scheduler


def _base_url() -> str:
    return (os.environ.get("BASE_URL") or FUNNEL_CFG.get("base_url", "https://phoenixprotocolbooks.com")).rstrip("/")


def _unsubscribe_url(token: str) -> str:
    return f"{_base_url()}/unsubscribe?token={token}"


def run_scheduled_email(lead_id: str, email_number: int, unsubscribe_token: str) -> None:
    lead = get_lead(lead_id, DATABASE_PATH)
    if not lead or lead.get("unsubscribed"):
        return
    base_url = _base_url()
    unsub_url = f"{base_url}/unsubscribe?token={unsubscribe_token}"
    ex_map = {e.get("id", ""): e for e in get_exercises()}
    book_map = get_book_map()
    book_info = book_map.get(lead["exercise_name"]) or book_map.get(lead.get("topic", "burnout"), {})
    tool_link = f"{base_url}{exercise_id_to_tool_path(lead['exercise_name'])}"
    second_tool_link = f"{base_url}{exercise_id_to_tool_path(lead['second_exercise'])}?utm_content=email2_practice"
    second_display = ""
    for e in get_exercises():
        if e.get("id") == lead["second_exercise"]:
            second_display = f"{e.get('h1_line1', '')} {e.get('h1_line2', '')}".strip() or lead["second_exercise"].replace("_", " ").title()
            break
    if not second_display:
        second_display = lead["second_exercise"].replace("_", " ").title()

    # Resolve hub config for this lead's topic
    proof_loop = get_proof_loop()
    hub_key = lead.get("hub", "burnout_reset")
    hub_config = proof_loop.get(hub_key, {})
    topic = hub_config.get("topic", lead.get("topic", "burnout"))
    story_id = hub_config.get("story_id", f"{topic}_nurse_story")
    book_slug = hub_config.get("book_slug", "burnout-reset")

    if email_number == 2:
        send_e2(lead, second_display, second_tool_link, unsub_url, base_url)
    elif email_number == 3:
        story_body = get_story(topic, story_id)
        send_e3(lead, story_body, unsub_url, base_url)
    elif email_number == 4:
        send_e4(lead, book_info.get("book_title", book_slug.replace("-", " ").title()), book_info.get("book_url", base_url + f"/books/{book_slug}"), unsub_url, base_url)
    elif email_number == 5:
        send_e5(lead, book_info.get("more_books", []), unsub_url, base_url)


@app.route("/")
def landing_default():
    return hub_landing("burnout_reset")


@app.route("/<hub_slug>")
def landing(hub_slug: str):
    hub_key, hub_config = resolve_hub(hub_slug)
    if hub_key is None:
        # Not a valid hub slug — could be another route; 404
        return f"Hub not found: {hub_slug}", 404
    return hub_landing(hub_key)


def hub_landing(hub_key: str):
    """Render the landing page for any topic hub."""
    exercises = get_exercises()
    sections = get_funnel_sections(hub_key)
    proof_loop = get_proof_loop()
    hub_config = proof_loop.get(hub_key, {})
    exercise_name = request.args.get("exercise", "").strip() or None
    ga4_id = os.environ.get("GA4_MEASUREMENT_ID", FUNNEL_CFG.get("ga4_measurement_id", ""))
    base_url = _base_url()
    personas = ["unknown", "professional", "healthcare", "first_responder", "entrepreneur", "corporate_manager", "working_parent", "other"]
    # Use dynamic template: hub_landing.html (generic) or fall back to burnout_reset.html
    template = "hub_landing.html" if (APP_DIR / "templates" / "hub_landing.html").exists() else "burnout_reset.html"
    return render_template(
        template,
        exercises=exercises,
        sections=sections,
        hub_key=hub_key,
        hub_config=hub_config,
        pre_selected_exercise=exercise_name or hub_config.get("first_exercise"),
        ga4_measurement_id=ga4_id,
        base_url=base_url,
        personas=personas,
    )


def _valid_email(email: str) -> bool:
    """Simple validation: one @, dot in domain, reasonable length."""
    if not email or len(email) > 254:
        return False
    if email.count("@") != 1:
        return False
    local, domain = email.split("@", 1)
    return bool(local and "." in domain and len(domain) >= 4)


@app.route("/submit", methods=["POST"])
def submit():
    # Hub context: which hub did this form come from?
    hub_key = (request.form.get("hub") or "burnout_reset").strip()
    hub_slug = hub_key.replace("_", "-")
    proof_loop = get_proof_loop()
    hub_config = proof_loop.get(hub_key, proof_loop.get("burnout_reset", {}))
    topic = hub_config.get("topic", "burnout")

    # Honeypot: reject if filled
    if request.form.get("website_url"):
        return redirect(f"/{hub_slug}")
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    exercise_name = (request.form.get("exercise_name") or "").strip()
    persona = (request.form.get("persona") or "").strip() or "unknown"
    if not email or not exercise_name:
        return redirect(f"/{hub_slug}?error=missing")
    if not _valid_email(email):
        return redirect(f"/{hub_slug}?error=invalid")
    exercises = get_exercises()
    ex_map = {e.get("id", ""): e for e in exercises}
    if exercise_name not in ex_map:
        return redirect(f"/{hub_slug}?error=invalid")
    pairs = get_exercise_pairs()
    second = (pairs.get(exercise_name) or pairs.get("default") or {}).get("second", "box_breathing")
    book_map = get_book_map()
    book_slug = hub_config.get("book_slug", "burnout-reset")
    book_info = book_map.get(exercise_name) or book_map.get(topic, {})
    book_title = book_info.get("book_title", book_slug.replace("-", " ").title())
    book_url = book_info.get("book_url", _base_url() + f"/books/{book_slug}")
    more_books = book_info.get("more_books", [])
    tool_link = f"{_base_url()}{exercise_id_to_tool_path(exercise_name)}"
    second_tool_link = f"{_base_url()}{exercise_id_to_tool_path(second)}?utm_content=email2_practice"
    second_display = ex_map.get(second, {})
    second_display = f"{second_display.get('h1_line1', '')} {second_display.get('h1_line2', '')}".strip() or second.replace("_", " ").title()
    story_id = hub_config.get("story_id", f"{topic}_nurse_story")
    story_body = get_story(topic, story_id)

    unsubscribe_token = str(uuid.uuid4())
    lead_id = insert_lead(
        email=email,
        exercise_name=exercise_name,
        second_exercise=second,
        hub=hub_key,
        topic=topic,
        name=name,
        persona=persona,
        unsubscribe_token=unsubscribe_token,
        db_path=DATABASE_PATH,
    )
    lead = get_lead(lead_id, DATABASE_PATH)
    if not lead:
        return redirect(f"/{hub_slug}?error=save")

    email_mode = FUNNEL_CFG.get("email_mode", "ghl")
    send_e5_cfg = FUNNEL_CFG.get("send_email_5", False)

    if email_mode == "smtp" and not is_unsubscribed(email, DATABASE_PATH):
        unsub_url = _unsubscribe_url(unsubscribe_token)
        if send_e1(lead, tool_link, unsub_url, _base_url()):
            mark_e1_sent(lead_id, DATABASE_PATH)
        sch = get_scheduler()
        if sch:
            d2 = FUNNEL_CFG.get("email_2_delay_hours", 24)
            d3 = FUNNEL_CFG.get("email_3_delay_hours", 72)
            d4 = FUNNEL_CFG.get("email_4_delay_hours", 48)
            d5 = FUNNEL_CFG.get("email_5_delay_hours", 168)
            now = datetime.datetime.utcnow()
            sch.add_job(run_scheduled_email, "date", run_date=now + datetime.timedelta(hours=d2), id=f"{lead_id}:e2", args=[lead_id, 2, unsubscribe_token], replace_existing=True)
            sch.add_job(run_scheduled_email, "date", run_date=now + datetime.timedelta(hours=d2 + d3), id=f"{lead_id}:e3", args=[lead_id, 3, unsubscribe_token], replace_existing=True)
            sch.add_job(run_scheduled_email, "date", run_date=now + datetime.timedelta(hours=d2 + d3 + d4), id=f"{lead_id}:e4", args=[lead_id, 4, unsubscribe_token], replace_existing=True)
            if send_e5_cfg:
                sch.add_job(run_scheduled_email, "date", run_date=now + datetime.timedelta(hours=d2 + d3 + d4 + d5), id=f"{lead_id}:e5", args=[lead_id, 5, unsubscribe_token], replace_existing=True)

    # GHL push (both modes)
    ghl_lead = {"email": email, "name": name, "exercise_name": exercise_name, "topic": topic, "source_page": hub_key, "persona": persona}
    ghl_ok = _push_ghl(ghl_lead)
    update_ghl_pushed(lead_id, ghl_ok, DATABASE_PATH)

    exercise_display = ex_map.get(exercise_name, {})
    exercise_display = f"{exercise_display.get('h1_line1', '')} {exercise_display.get('h1_line2', '')}".strip() or exercise_name.replace("_", " ").title()
    return render_template(
        "thank_you.html",
        first_name=name.split()[0] if name else "",
        exercise_name=exercise_display,
        tool_link=tool_link,
    )


def _push_ghl(lead: dict) -> bool:
    """Push lead to GHL with custom field UUIDs and tags. Returns True on success."""
    api_key = os.environ.get("GHL_API_KEY", FUNNEL_CFG.get("ghl_api_key"))
    location_id = os.environ.get("GHL_LOCATION_ID", FUNNEL_CFG.get("ghl_location_id"))
    if not api_key or not location_id:
        return False

    # Custom field UUIDs — MUST be real GHL UUIDs, not string names.
    cf_topic = os.environ.get("GHL_CUSTOM_FIELD_TOPIC", FUNNEL_CFG.get("ghl_custom_field_topic", ""))
    cf_exercise = os.environ.get("GHL_CUSTOM_FIELD_EXERCISE", FUNNEL_CFG.get("ghl_custom_field_exercise", ""))
    cf_persona = os.environ.get("GHL_CUSTOM_FIELD_PERSONA", FUNNEL_CFG.get("ghl_custom_field_persona", ""))

    if not cf_topic or not cf_exercise:
        app.logger.warning("GHL push skipped: custom field UUIDs not configured (ghl_custom_field_topic / ghl_custom_field_exercise)")
        return False

    try:
        import requests
        url = os.environ.get("GHL_CONTACTS_URL", FUNNEL_CFG.get("ghl_contacts_url", "https://services.leadconnectorhq.com/contacts/"))
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28",
        }
        name = lead.get("name", "")
        first = name.split()[0] if name else ""
        last = " ".join(name.split()[1:]) if name and len(name.split()) > 1 else ""

        # Build custom fields with real UUIDs
        custom_fields = [
            {"id": cf_topic, "value": lead.get("topic", "burnout")},
            {"id": cf_exercise, "value": lead.get("exercise_name", "")},
        ]
        if cf_persona:
            custom_fields.append({"id": cf_persona, "value": lead.get("persona", "unknown")})

        # Build tags dynamically: funnel_{hub}, topic_{topic}, exercise_{exercise}, persona_{persona}
        hub = lead.get("source_page", "burnout_reset")
        topic = lead.get("topic", "burnout")
        exercise = lead.get("exercise_name", "")
        persona = lead.get("persona", "")
        tags = [f"funnel_{hub}", f"topic_{topic}"]
        if exercise:
            tags.append(f"exercise_{exercise}")
        if persona and persona != "unknown":
            tags.append(f"persona_{persona}")

        payload = {
            "locationId": location_id,
            "email": lead.get("email"),
            "firstName": first,
            "lastName": last,
            "phone": "",
            "source": hub,
            "tags": tags,
            "customFields": custom_fields,
        }
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code in (200, 201):
            return True
        app.logger.warning("GHL push failed: %s %s", r.status_code, r.text[:200])
        return False
    except Exception as e:
        app.logger.warning("GHL push error: %s", e)
        return False


@app.route("/unsubscribe")
def unsubscribe():
    token = (request.args.get("token") or "").strip()
    if not token:
        return render_template("unsubscribed.html", success=False)
    if set_unsubscribed_by_token(token, DATABASE_PATH):
        return render_template("unsubscribed.html", success=True)
    return render_template("unsubscribed.html", success=False)


@app.route("/books/<slug>")
def book_redirect(slug: str):
    """Log book intent (GA4) and redirect with UTM passthrough. Emails use base_url/books/slug for attribution."""
    info = get_book_by_slug(slug)
    if not info:
        return redirect(_base_url(), code=302)
    target = (info.get("redirect_url") or info.get("book_url") or f"{_base_url()}/books/{slug}").strip()
    if not target:
        target = f"{_base_url()}/books/{slug}"
    qs = request.query_string.decode("utf-8") if request.query_string else ""
    if qs:
        target = target + ("&" if "?" in target else "?") + qs
    app.logger.info("book_intent slug=%s", slug)
    ga4_id = os.environ.get("GA4_MEASUREMENT_ID", FUNNEL_CFG.get("ga4_measurement_id", ""))
    return render_template("book_intent.html", slug=slug, target_url=target, ga4_measurement_id=ga4_id)


if __name__ == "__main__":
    if app.config["SECRET_KEY"] == "dev-secret-change-in-prod" and os.environ.get("FLASK_DEBUG", "0") != "1":
        raise RuntimeError("SECRET_KEY must be set in production (set env SECRET_KEY or FLASK_DEBUG=1 for dev)")
    get_scheduler()  # start if smtp
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG", "0") == "1")
