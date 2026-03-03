#!/usr/bin/env python3
"""
Generate all 27 breathwork landing pages from config/freebies/exercises_landing.json.
Output: public/breathwork/lp-{exercise_id}.html (one per exercise).
Email capture: set "formspree_form_id" in the JSON (one free form at formspree.io) and re-run;
  no MailerLite needed — you get submissions by email + CSV export; optional Zapier to MailerLite later.
Usage: from repo root, python3 scripts/generate_landing_pages.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG = REPO_ROOT / "config" / "freebies" / "exercises_landing.json"
OUT_DIR = REPO_ROOT / "public" / "breathwork"


def _id_to_kebab(s: str) -> str:
    return re.sub(r"_", "-", (s or "").strip().lower())


def _html_esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def one_page(ex: dict, base_url: str, formspree_form_id: str) -> str:
    ex_id = ex.get("id", "")
    kebab = _id_to_kebab(ex_id)
    title = _html_esc((ex.get("h1_line1", "") + " " + ex.get("h1_line2", "")).strip() or ex_id)
    h1_1 = _html_esc(ex.get("h1_line1", ""))
    h1_2 = _html_esc(ex.get("h1_line2", ""))
    benefit = _html_esc(ex.get("benefit", ""))
    duration = _html_esc(ex.get("duration", ""))
    ml_tag = ex.get("ml_tag", ex_id)
    tool_url = f"tools/{kebab}.html"
    tool_url_js = tool_url.replace("\\", "\\\\").replace("'", "\\'")

    if formspree_form_id:
        formspree_esc = _html_esc(formspree_form_id)
        ml_tag_js = ml_tag.replace("\\", "\\\\").replace("'", "\\'")
        script_block = f"""<script>
const TOOL_URL = '{tool_url_js}';
const FORMSPREE_ENDPOINT = 'https://formspree.io/f/{formspree_esc}';
const EXERCISE_TAG = '{ml_tag_js}';

function handleSubmit(e) {{
  e.preventDefault();
  const email = document.getElementById('email').value.trim();
  var body = new URLSearchParams();
  body.append('email', email);
  body.append('exercise', EXERCISE_TAG);
  fetch(FORMSPREE_ENDPOINT, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
    body: body
  }}).then(function() {{
    document.getElementById('toolLink').href = TOOL_URL;
    document.getElementById('formView').style.display = 'none';
    document.getElementById('successView').style.display = 'block';
  }}).catch(function() {{
    document.getElementById('toolLink').href = TOOL_URL;
    document.getElementById('formView').style.display = 'none';
    document.getElementById('successView').style.display = 'block';
  }});
}}
</script>"""
    else:
        script_block = f"""<script>
const ML_API_KEY   = 'YOUR_MAILERLITE_API_KEY';
const ML_GROUP_ID  = 'YOUR_GROUP_ID';
const EXERCISE_TAG = '{ml_tag}';
const TOOL_URL     = '{tool_url_js}';

function handleSubmit(e) {{
  e.preventDefault();
  const email = document.getElementById('email').value.trim();
  if (ML_API_KEY && ML_API_KEY !== 'YOUR_MAILERLITE_API_KEY') {{
    fetch('https://api.mailerlite.com/api/v2/subscribers', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'X-MailerLite-ApiKey': ML_API_KEY }},
      body: JSON.stringify({{ email, groups: [parseInt(ML_GROUP_ID, 10)], fields: {{ exercise: EXERCISE_TAG }} }})
    }}).catch(function() {{}});
  }}
  document.getElementById('toolLink').href = TOOL_URL;
  document.getElementById('formView').style.display = 'none';
  document.getElementById('successView').style.display = 'block';
}}
</script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Free Tool</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  :root {{ --bg: #080a0f; --text: #f0ece4; --gold: #c8a84b; --muted: rgba(240,236,228,0.4); --border: rgba(200,168,75,0.2); }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Georgia', serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }}
  body::before {{ content: ''; position: fixed; inset: 0; background: radial-gradient(ellipse 60% 60% at 50% 40%, rgba(200,168,75,0.06) 0%, transparent 70%); pointer-events: none; }}
  .card {{ position: relative; z-index: 2; max-width: 420px; width: 100%; text-align: center; }}
  .label {{ font-family: 'Courier New', monospace; font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase; color: var(--gold); opacity: 0.7; margin-bottom: 40px; }}
  h1 {{ font-size: clamp(2.2rem, 6vw, 3.2rem); font-weight: normal; line-height: 1.15; color: var(--text); margin-bottom: 12px; }}
  .benefit {{ font-size: 1.1rem; color: var(--muted); font-style: italic; margin-bottom: 8px; line-height: 1.5; }}
  .duration {{ font-family: 'Courier New', monospace; font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); opacity: 0.6; margin-bottom: 48px; }}
  .rule {{ width: 40px; height: 1px; background: var(--gold); opacity: 0.3; margin: 0 auto 40px; }}
  .form {{ display: flex; flex-direction: column; gap: 12px; }}
  input[type="email"] {{ background: rgba(255,255,255,0.04); border: 1px solid var(--border); color: var(--text); font-family: 'Georgia', serif; font-size: 1rem; padding: 16px 20px; text-align: center; outline: none; transition: border-color 0.25s; -webkit-appearance: none; border-radius: 0; }}
  input[type="email"]::placeholder {{ color: rgba(240,236,228,0.25); }}
  input[type="email"]:focus {{ border-color: rgba(200,168,75,0.5); }}
  button {{ background: var(--gold); border: none; color: var(--bg); font-family: 'Courier New', monospace; font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase; padding: 18px 24px; cursor: pointer; transition: background 0.25s; border-radius: 0; }}
  button:hover {{ background: #dfc06a; }}
  .privacy {{ font-family: 'Courier New', monospace; font-size: 9px; letter-spacing: 0.1em; color: rgba(240,236,228,0.2); margin-top: 8px; }}
  .success {{ display: none; animation: fade 0.6s ease forwards; }}
  .success h2 {{ font-size: 1.8rem; font-weight: normal; color: var(--gold); margin-bottom: 16px; }}
  .success p {{ font-size: 1rem; color: var(--muted); line-height: 1.65; font-style: italic; margin-bottom: 28px; }}
  .go-btn {{ display: inline-block; font-family: 'Courier New', monospace; font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase; padding: 16px 36px; background: var(--gold); color: var(--bg); text-decoration: none; transition: background 0.25s; }}
  .go-btn:hover {{ background: #dfc06a; }}
  @keyframes fade {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
</head>
<body>
<div class="card">
  <div id="formView">
    <p class="label">Phoenix Protocol · Free Tool</p>
    <h1>{h1_1}<br>{h1_2}</h1>
    <p class="benefit">{benefit}</p>
    <p class="duration">{duration}</p>
    <div class="rule"></div>
    <form class="form" onsubmit="handleSubmit(event)">
      <input type="email" id="email" placeholder="your@email.com" required autocomplete="email">
      <button type="submit">Get Free Access →</button>
      <p class="privacy">No spam. Unsubscribe anytime.</p>
    </form>
  </div>
  <div class="success" id="successView">
    <h2>It's yours.</h2>
    <p>Check your inbox for a confirmation.<br>Your tool is one click away.</p>
    <a class="go-btn" href="#" id="toolLink">Open the Tool →</a>
  </div>
</div>
{script_block}
</body>
</html>
"""


def main() -> int:
    if not CONFIG.exists():
        print(f"Missing {CONFIG}")
        return 1
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    exercises = data.get("exercises") or []
    base_url = (data.get("base_url") or "").strip()
    formspree_form_id = (data.get("formspree_form_id") or "").strip()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ex in exercises:
        ex_id = ex.get("id", "")
        if not ex_id:
            continue
        kebab = _id_to_kebab(ex_id)
        html = one_page(ex, base_url, formspree_form_id)
        out_path = OUT_DIR / f"lp-{kebab}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"Wrote {out_path.relative_to(REPO_ROOT)}")
    print(f"Done. {len(exercises)} pages in {OUT_DIR.relative_to(REPO_ROOT)}")
    if formspree_form_id:
        print("Email capture: Formspree (form ID set in config)")
    else:
        print("Email capture: MailerLite placeholders (set formspree_form_id in config for Formspree)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
