# Go / No-Go checklist (MVP launch)

**Do not share the funnel URL for real testing until the items below are satisfied.**

---

## GO (ready to ship as scaffold)

- Config layout (proof loop YAMLs, pairs, book map, sections)
- Story bank + composite disclaimer
- Landing + thank-you pages
- GHL handoff doc and optional push
- Local run instructions
- **Persistence:** SQLite (`data/funnel.db`), no JSONL. WAL mode, concurrent-write safe.
- **email_mode:** `ghl` or `smtp` in `config.yaml`; GHL push in both modes.
- **4-email MVP:** `send_email_5: false` in config; E5 is Phase 2.
- **Unsubscribe:** `GET /unsubscribe?token=...`; link in every email template; suppression checked before send.
- **Persona:** Optional “I work as…” dropdown on form; stored and sent to GHL.
- **Book routing:** `/books/<slug>` logs intent and 301 redirects; emails use our URL for attribution.

---

## NO-GO until fixed (real MVP test)

- **E1 must actually send** on form submit when `email_mode: smtp`. Set `SMTP_USER` and `SMTP_PASSWORD` (or config) and verify one submission receives E1.
- **E2–E5 must schedule and send** when `email_mode: smtp`. Scheduler uses SQLAlchemy jobstore (same DB); jobs survive restarts. Verify with test lead and shortened delays.
- **Unsubscribe + compliance:** Every email includes unsubscribe link and “You received this because you requested the free practice.” Physical address line optional but recommended for CAN-SPAM.
- **Do not go live** with a form that accepts submissions but sends no emails (misleading conversion data; leads never get the sequence).

---

## If using GHL for email (email_mode: ghl)

- App only persists lead and pushes to GHL. Operator configures the 4-email (or 5) sequence in GHL automation.
- No APScheduler; no Brevo SMTP required in app. Leads still stored in SQLite for backup/audit.

---

## If using SMTP (email_mode: smtp)

- Brevo SMTP credentials in config or env.
- APScheduler runs in-process; jobstore = same SQLite DB. Restart-safe.
- E5 is optional: set `send_email_5: true` when you want the “more books” email.
