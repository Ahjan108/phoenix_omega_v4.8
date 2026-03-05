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

---

## Handoff / open items (no code changes)

Everything in the **GO** section above is built and in the repo. What’s left is human/operator work:

| Area | What’s open | Who |
|------|-------------|-----|
| **Go live** | Set SMTP or GHL credentials; run one test submission; confirm E1 arrives and (if smtp) E2–E5 schedule; confirm unsubscribe works. Then share URL. | You or operator |
| **Authority narrative** | Nihala’s paragraph (Section 2). Paste into `config/freebies/funnel_sections.yaml` → hub → `authority_narrative`. Scaffold/placeholder in that file. | Nihala drafts; copywriter one light edit |
| **Email 3 stories** | Raw from Nihala; copywriter shapes to 120–150 words, Before/Practice/After; add to `funnel/burnout_reset/stories/<topic>.md`. | Nihala sources; copywriter shapes; Nihala approves |
| **Headlines / CTA** | A/B variants (incl. “Nihala’s teaching language” option). Document in spec or config; test; Nihala approves. | Copywriter proposes + tests; Nihala approves |
| **E1 / E2 / E4 / Problem–Solution** | Drafts for all hubs, topics, personas. E2 can use approved mechanism lines (see `docs/email_sequences/e2_approved_mechanism_lines.md`). | Copywriter |
| **GHL custom field UUIDs** | If using GHL: in GHL Settings → Custom Fields, copy the real UUID for topic, exercise, persona; put them in app config so the payload maps correctly. | Operator |
| **CAN-SPAM** | Add physical address in footer (see CAN-SPAM section below); configure in Brevo account settings. | Operator |
| **Teacher Mode author story** | Preferred structure/length for key-turning-point story (e.g. before / encounter / after, N words). Optional: add to writer spec so copywriter has a template. | Nihala / expert |

**Prompt for Nihala (when ready):** Headline language in her teaching voice (1–2 example headlines); approved mechanism lines for E2 (nervous system / breath); CAN-SPAM address decision; preferred structure for the author story in Teacher Mode.

---

## Three things from Nihala (unblocks launch)

Everything is ready to ship **the moment these three come from Nihala** — no code changes required.

1. **Authority narrative (raw).** Sit down, dictate or type 150–200 words about the MIT-to-monastery path and what you learned about nervous systems from both directions. Don’t edit. Send the raw version to the copywriter. They’ll shape it to 100–150 words and paste it into `funnel_sections.yaml` → `authority_narrative`.
2. **One real burnout story (raw).** A specific person (anonymized), specific profession, specific moment you witnessed or they shared. Three sentences of raw detail is enough. Copywriter shapes it to the spec (Before/Practice/After, 120–150 words) and adds it to `stories/burnout.md`.
3. **Approve headline variants.** Once the copywriter proposes 2–3 options (including one in your teaching language), you approve. Give the copywriter one or two example phrases from your actual teaching so they can calibrate.

After that: copywriter delivers the rest; operator adds GHL UUIDs and tests the flow; you go live.

---

## Copywriter (after Nihala’s three)

- Shape the authority narrative into 100–150 words; paste into config.
- Write two headline variants in Nihala’s teaching voice (using her example phrases as benchmark).
- Draft Email 2 science content: one mechanism, one citation, plain language (or use approved lines from `docs/email_sequences/e2_approved_mechanism_lines.md`).
- Draft Email 1 and Email 4 copy per writer spec.
- Format the burnout story to spec (Before/Practice/After) and add to `stories/burnout.md`.

---

## Operator

- Add **real GHL custom field UUIDs** (GHL Settings → Custom Fields) into app config so the payload maps correctly.
- Run **one full test**: submit form → confirm E1 arrives → confirm E2–E5 schedule (if smtp) or GHL sequence (if ghl) → confirm unsubscribe works. Then the URL can be shared.

---

## CAN-SPAM (physical address)

**Add a physical address** in the email footer. For a California nonprofit, use your registered agent address. Wording: *You’re receiving this because you requested [exercise name] from PhoenixProtocolBooks.com. [Physical address]. Unsubscribe.* Brevo can insert this automatically if you configure it in Brevo account settings; no code change needed.
