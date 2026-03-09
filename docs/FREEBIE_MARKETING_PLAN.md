# Freebie Marketing Plan

**Purpose:** Single doc tying freebies to funnel, Proof Loop, email, upsell, and GHL. Authority for future hubs and variants.

---

## Objectives

- **Lead capture** — Form on landing page; name, email, exercise choice.
- **List building** — Contacts stored in-app and pushed to GoHighLevel (GHL).
- **Nurture** — Proof-Loop email sequence (4–5 emails); two micro-reliefs before any offer.
- **Upsell** — First book in Email 4; optional “more books” in Email 5. Sell nervous system *change*, not information.

---

## Conversion psychology: Proof Loop (mandatory)

The funnel must **demonstrate the mechanism twice** before the offer.

1. **Micro-relief 1** — First free exercise (landing + Email 1).
2. **Micro-relief 2** — Second short practice, different technique (Email 2). Not philosophy; another felt shift.
3. **Story of relief** — Transformation story (Email 3). Builds relatability, authority, trust.
4. **Offer** — Book recommendation (Email 4). Only after two micro-reliefs + story. Minimum 48h after story.
5. **Optional LTV** — “More books for this issue” (Email 5).

**Wrong:** Freebie → insight → story → book.  
**Right:** Exercise → Exercise → Story → Book (→ More books).

---

## Funnel stages

| Stage   | What happens |
|--------|----------------|
| Awareness | Book CTA, social, paid; link to hub URL (e.g. `/burnout-reset`) |
| Landing   | 6-section page: hero, problem, solution, form, soft CTA, GA4. No heavy book push. |
| Capture   | Form submit → thank-you; lead stored; Email 1 sent. |
| Nurture   | Proof-Loop emails 1–5 (E1 immediate, E2 +24h, E3 +72h, E4 +48h after E3, E5 +168h). |
| Upsell    | Book in E4; more books in E5. |

---

## Funnel architecture at scale

- **Hubs:** `/burnout-reset`, `/anxiety-reset`, `/sleep-reset`, etc. Each topic is its own funnel with the **same Proof Loop structure**.
- **Config:** One entry per hub in `config/freebies/funnel_proof_loop.yaml` (topic, first_exercise, story_id, book_slug). Second exercise from `exercise_pairs.yaml`; story from story bank; book from `freebie_to_book_map.yaml`.
- **Content:** Only topic, exercise ids, story_id, and book_slug change per hub; layout and email logic stay the same.

---

## Channels

- **In-book CTA** — Existing; can point to `yoursite.com/burnout-reset?exercise=cyclic_sighing`.
- **Hub URLs** — `/burnout-reset` (and future hubs); GA4 for form and page views.
- **Email** — Proof-Loop sequence; source in repo (`docs/email_sequences/proof_loop_sequence.md`); delivery via Python app + Brevo SMTP (MVP).

---

## Email

- **Sequence:** 4–5 emails (Proof Loop). Canonical copy in `docs/email_sequences/proof_loop_sequence.md`.
- **Delivery (MVP):** Python funnel app + Brevo SMTP. From: `nihala@phoenixprotocolbooks.com`. Brevo: SPF/DKIM, unsubscribe, open/click. Sequence in Python for version control; GHL automation Phase 2 after conversion proven.
- **Timing:** E1 0, E2 +24h, E3 +72h, E4 +48h after E3, E5 +168h. Do not compress story→book; min 48h gap.

---

## Upsell

- **Config:** `freebie_to_book_map.yaml` (exercise/topic → book_title, book_url, more_books); `funnel_proof_loop.yaml` (book_slug per hub).
- **Email 4:** First book recommendation.
- **Email 5:** Optional list from `more_books` for multi-book buyers.
- **Future:** Topic/persona-based recs and series upsell.

---

## GHL (GoHighLevel)

- **Role:** Single CRM for contacts. Funnel app pushes each lead to GHL Contacts API (create/update).
- **Setup:** API Key 2.0 + Location ID in env; see `funnel/burnout_reset/GHL_HANDBOFF.md` for payload and tags.
- **Automations:** Operator can add GHL workflows on “contact created” (e.g. tags, internal follow-up). MVP does not use GHL to send the 5-email sequence.

---

## Locale

- **First:** en-US. CTA URL pattern: `PhoenixProtocolBooks.com/burnout-reset` (and `/free/{slug}` where applicable).
- **Multi-locale:** Deferred; document when needed.

---

## Analytics

- **lead_submit** — GA4 event on form submit.
- **second_tool_click** — UTM on Email 2 second-tool link (`utm_content=email2_practice`). GA4 auto-parses UTM parameters; no custom event code needed. Filter by `utm_content = email2_practice` in GA4 reports.
- **book_intent** — GA4 event on book page (e.g. `/books/{slug}`). Use for conversion tuning after 200+ sends.

---

## Governance

- Existing freebie index, Gate 16/16b, and CTA caps unchanged.
- Funnel is an additional path; freebie_to_landing and freebie_renderer behavior unchanged.

## MVP scope (4 vs 5 emails)

- **4-email MVP:** E1 (immediate) → E2 (+24h) → E3 (+72h) → E4 (+48h after E3). Set `send_email_5: false` in funnel config to validate funnel faster.
- **E5 (more books):** Phase 2 / optional; enable with `send_email_5: true` when ready for LTV step.

## Persistence and reliability

- **Leads:** Stored in SQLite (`data/funnel.db`), not JSONL. Concurrent-write safe (WAL mode). Use Postgres (`DATABASE_URL`) for production scale.
- **Scheduled emails (smtp mode):** APScheduler uses same DB as jobstore; jobs survive restarts. Do not go live until E1–E5 are verified sending and unsubscribe is working.
