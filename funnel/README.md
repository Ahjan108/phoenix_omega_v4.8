# Funnel service — Freebie → Proof Loop → GHL

Self-contained Flask app for the burnout-reset (and future topic) funnels: 6-section landing page, form capture, Proof-Loop email sequence (E1–E5), and push to GoHighLevel.

**Persistence:** SQLite only (`data/funnel.db`). No JSONL. Leads table + APScheduler jobstore in same DB so jobs survive restarts. Use Postgres (set `DATABASE_URL`) for production scale if needed.

## Structure

- **burnout_reset/** — First hub. Run from repo root so `config/freebies/*` is found.
  - `app.py` — Routes: `GET /`, `GET /burnout-reset`, `POST /submit`, `GET /unsubscribe?token=...`, `GET /books/<slug>`. Persists to SQLite; `email_mode` ghl or smtp.
  - `config.yaml` — `email_mode` (ghl | smtp), `send_email_5` (4-email MVP when false), GHL, Brevo, GA4, base URL, `database_path`.
  - `db.py` — SQLite leads table; init_db, insert_lead, get_lead, mark_e1_sent, set_unsubscribed_by_token, is_unsubscribed.
  - `email_send.py` — Brevo SMTP; send_e1–e5 with unsubscribe link; used when `email_mode: smtp`.
  - `templates/` — `burnout_reset.html` (6 sections, form + optional persona, GA4), `thank_you.html`, `unsubscribed.html`.
  - `emails/` — 5 Jinja2 HTML templates; each includes unsubscribe link and compliance line.
  - `stories/` — Story bank for Email 3.
  - `GHL_HANDBOFF.md` — API key, payload, tags, who sends email.
  - `GO_NO_GO.md` — Launch checklist: do not share URL until E1–E5 send and unsubscribe work.

## Run locally

```bash
cd funnel/burnout_reset
pip install -r requirements.txt
export FLASK_APP=app.py
# For smtp mode: SMTP_USER, SMTP_PASSWORD, BASE_URL
# Optional: GHL_API_KEY, GHL_LOCATION_ID, GA4_MEASUREMENT_ID
flask run
# or: python app.py
```

Open `http://127.0.0.1:5000/burnout-reset`.

## Config (repo)

- `config/freebies/funnel_proof_loop.yaml` — Per-hub: topic, first_exercise, story_id, book_slug.
- `config/freebies/exercise_pairs.yaml` — Second-exercise pairing (activation_down vs grounding).
- `config/freebies/freebie_to_book_map.yaml` — exercise/topic → book_title, book_url, more_books. Use our domain in book_url; add `redirect_url` for final Amazon if needed.
- `config/freebies/funnel_sections.yaml` — Optional hero/problem/solution/CTA per hub.
- `config/freebies/exercises_landing.json` — Exercise list.

## Email mode

- **email_mode: ghl** — App persists lead and pushes to GHL. GHL sends the sequence (operator configures automation).
- **email_mode: smtp** — App sends E1 immediately and schedules E2–E5 via APScheduler (SQLAlchemy jobstore). Set `SMTP_USER`, `SMTP_PASSWORD`. 4-email MVP: `send_email_5: false`.

## Unsubscribe and compliance

- Every email template includes an unsubscribe link (`{{ unsubscribe_url }}`) and “You received this because you requested the free practice.”
- `GET /unsubscribe?token=...` marks lead unsubscribed; suppression checked before any send.

## Book routing

- Emails use `base_url/books/<slug>` for attribution. `GET /books/<slug>` logs intent and 301 redirects to `redirect_url` or `book_url` from `freebie_to_book_map.yaml`.

## Deploy

- Env: `EMAIL_MODE`, `GHL_API_KEY`, `GHL_LOCATION_ID`, `GA4_MEASUREMENT_ID`, `BASE_URL`, `SECRET_KEY`. For smtp: `SMTP_USER`, `SMTP_PASSWORD`. Optional: `DATABASE_URL` (Postgres) or `DATABASE_PATH` (SQLite path).
- Do not go live until E1–E5 are verified and unsubscribe works (see GO_NO_GO.md).
