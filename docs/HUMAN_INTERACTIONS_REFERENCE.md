# Human Interactions Reference

**Purpose:** Single place for everything *you* (or a human operator) must do: UI actions, church/banking setup, checklists to complete, what to tell GoHighLevel admin for freebies, and other human-facing tasks.

**Authority:** This doc aggregates from existing specs and checklists; those remain the source of truth for detail.

---

## 1. What you do on the UI (Phoenix Control / Dashboard)

- **Prerequisites:** Phoenix Control app built and launched (Xcode: open `PhoenixControl.xcodeproj`, Cmd+R). Repo path set to phoenix_omega root. Python 3 and repo dependencies installed.

| Tab / area | Your action | Pass / evidence |
|------------|-------------|-----------------|
| **Dashboard** | Open Dashboard. After running collector at least once: check observability phase (P1–P4), snapshot summary, evidence/elevated counts, branch protection checklist. | Screenshot with non-empty snapshot and phase status. |
| **Observability** | Open Observability → click **Collect signals**. | Log streams; on completion snapshot and evidence/elevated tables update. Screenshot after collect. |
| **Pipeline / Simulation / Tests / Gates / Pearl News / Teacher / Docs** | For each tab: run the primary action (e.g. Run pipeline, Run sim, Run core tests, Run gates, Run article pipeline, Run teacher gates, Run docs check). | Log streams; completion or clear error. Log tail or screenshot. |
| **CI / Workflows** | Set owner/repo; with token, click Refresh. Click links to open workflow runs / production-alert issues. | Loads workflow runs and issues; links open correct URLs. |
| **Completeness** (when implemented) | Run validation; use scorecard and drill-down by locale/language/persona/topic/engine/teacher. | Screenshot of scorecard and one drill-down. |
| **Approvals** (when implemented) | Check required items and status. If any not approved: resolve (sign checklist, etc.); red blocker and launch actions stay disabled until approved. | Screenshot showing blocker when approval missing, or green when all approved. |
| **Missing/Blocked queue** (when implemented) | Review queue for severity, owner, source, fix action. Run the stated fix (next command) and verify. | Queue shows items with fix action; you run command and confirm fix. |

**Operator rule (from spec):** For every failed or blocked item the UI must show: **next command**, **owner**, **SLA**, **evidence path**. You use that to fix and verify.

**Safety checks you can run:** Cancel a long run; set invalid repo path (run disabled or validation message); force a failure and confirm error appears in log/alert.

---

## 2. Church contracts and banking — what you must complete

Governance: [docs/CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md](./CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md).  
Operational checklist: [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md).

### Church agreements (both required)

1. **Existing:** Church docs / Cooperative Church Compliance (canonical church record, compliance calendar). See [docs/church_docs/README.md](./church_docs/README.md).
2. **Additional:** Separate agreement covering: Google Play developer account setup and use, bank account control by treasurer, and VWM 90% payout terms (and, where applicable, letter to bank re low-activity intent).

**Church agreements = [existing Cooperative Church Compliance] + [VWM/Google Play/bank control/payout agreement].**

### Payout checklist — what you must give / do

| # | What | Where / action |
|---|------|----------------|
| 1 | **Plaid credentials** (from dashboard.plaid.com): `client_id`, `secret` | Put in `config/payouts/credentials.yaml` under `plaid:`. |
| 2 | **24 bank connections** (churches CHURCH_01–CHURCH_24) | Run `python -m payouts.link_server` → open http://localhost:5000 → connect each church Bluevine account via Plaid Link. |
| 3 | **Bluevine account last 4 digits** for all 24 churches | Put in `churches.yaml` (bluevine_account_last4) or `fill_template.csv` (bluevine_last4). |
| 4 | **Payee info** for 24 payees (who gets the 90%): name, bank_last4 | Put in `payees.yaml` (display_name, bank_last4) or `fill_template.csv` (payee_name, payee_bank_last4). |
| 5 | **International partner payees** (optional) | Choose payout method per payee (wise_usd, wise_direct, crypto, hk_clearing). Store only **vault_ref** in config; real details in vault/secrets. Set status, effective_from, effective_to, fallback_methods. **2-person approval** required for: (1) payout method changes for existing payee, (2) first payout to new payee. Document approvals. See [docs/PAYOUT_PARTNER_METHODS.md](./PAYOUT_PARTNER_METHODS.md). |

**Approval controls:** Treasurer + one other (e.g. board or ops lead). No single-person changes to payout method or account/vault_ref.

**Entities:** 24 churches/payees; 20 bank accounts (4 existing, 16 to set up). 1:1:1: one church = one Google Play developer account = one bank account.

---

## 3. Stuff you must complete (checklists and sign-offs)

### Production / release

- **Pre-publish (wave export):** Run `scripts/ci/run_prepublish_gates.py` with correct `--plans-dir`, `--wave-rendered-dir`, etc. Publish only when exit code 0. See [scripts/ci/PREPUBLISH_CHECKLIST.md](../scripts/ci/PREPUBLISH_CHECKLIST.md).
- **Production readiness:** Run `scripts/run_production_readiness_gates.py` + simulation. 15 conditions in [specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md).
- **Pearl News GO/NO-GO:** One real networked run, CI green on main, GO/NO-GO checklist signed with evidence links. [docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md).
- **Audiobook go-live:** 10-item sign-off gate before first production run. [docs/GO_LIVE_FINAL_CHECKLIST.md](./GO_LIVE_FINAL_CHECKLIST.md).

### Quality (human, not CI)

- **Creative quality (after compiling each book):** Use [docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md](./CREATIVE_QUALITY_VALIDATION_CHECKLIST.md) — arc, story, exercise, voice, ending.
- **First 10 books:** [docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) — compile 10 from one brand → blind listen → 5-axis score → pattern analysis.
- **Approvals that block release:** Sign checklists/approval records for: Pearl News church/governance; Church/brand (e.g. NorCal Dharma); any governance evidence marked “blocks release”. UI shows these; release/go-live disabled until approved.

### GitHub / ops

- **No production sign-off** without run URLs + artifacts + digest evidence (per [docs/GITHUB_NO_FAILURE_FRAMEWORK.md](./GITHUB_NO_FAILURE_FRAMEWORK.md)).

---

## 4. What to tell GoHighLevel (GHL) admin for freebies

Funnel/lead flow: [docs/FREEBIE_MARKETING_PLAN.md](./FREEBIE_MARKETING_PLAN.md).  
Technical handoff: [funnel/burnout_reset/GHL_HANDBOFF.md](../funnel/burnout_reset/GHL_HANDBOFF.md).

### Setup (you or GHL admin)

1. **GHL API Key 2.0** — Create in GHL (Settings → API → Create Key). Put in env: `GHL_API_KEY`.
2. **Location ID** — GHL location/sub-account ID. Put in env: `GHL_LOCATION_ID`.

### What to tell GHL admin

- **Contacts:** The app pushes leads to GHL on form submit (Contacts API). Fields: `locationId`, `email`, `firstName`, `lastName`, `source` (e.g. `burnout_reset`), plus custom fields.
- **Custom fields:** In GHL, custom field **ids are UUIDs** (Settings → Custom Fields). Create or find each field and copy its **ID (UUID)**. Give those UUIDs to the app config. Using human-readable strings like `"topic"` or `"exercise"` will cause push to fail or not map — most common GHL integration failure.
- **Recommended tags** (GHL admin can add on “contact created”): e.g. `topic_burnout`, `funnel_burnout_reset`, `exercise_cyclic_sighing` (or chosen exercise), and `persona_*` if you add persona later.
- **Automations:** Operator can add GHL workflows on “contact created” (tags, internal follow-up). MVP does **not** use GHL to send the 5-email Proof Loop; that’s either this app (Brevo SMTP) or built later in GHL.
- **Email mode:** If `email_mode: ghl` — app only pushes contact + tags; GHL admin builds the email sequence in GHL automation. If `email_mode: smtp` — this app sends E1–E5 via Brevo; do not go live until E1–E5 verified and unsubscribe working.

**Summary for GHL admin:** “We push contacts to GHL with source, topic, exercise, and tags. You need to create custom fields in GHL, copy their UUIDs for our config, and optionally add automations on contact created. Our MVP sends the Proof Loop emails ourselves (Brevo); you can take over sequences in Phase 2 if desired.”

---

## 5. Other human-related items

- **Writer/copy:** Funnel and book copy live in repo; see [FUNNEL_AND_BOOK_COPY_WRITER_SPEC.md](../FUNNEL_AND_BOOK_COPY_WRITER_SPEC.md) and [docs/FREEBIE_MARKETING_PLAN.md](./FREEBIE_MARKETING_PLAN.md). Personas on form (“I work as…”) used for segmentation and GHL.
- **Teacher / author approvals:** Teacher atoms and gap-fill approval via `tools/approval/approve_atoms.py`, `tools/approval/batch_approve_teacher_atoms.py`; exercise approval via `tools/exercise_approval/exercise_approve.py`. See [docs/SYSTEMS_AUDIT.md](./SYSTEMS_AUDIT.md).
- **New locale/language:** Sign-off and marketing + ops approval per [docs/NEW_LANGUAGE_LOCATION_ONBOARDING.md](./NEW_LANGUAGE_LOCATION_ONBOARDING.md).
- **Disputes (payouts):** Contact treasurer with transaction ID, amount expected, date, and any provider error; report within 30 days of expected payout date. See dispute policy in [docs/CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md](./CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md).
- **Record retention:** Payout logs, approval records, method-change audit trail, dispute/correction records — retain per jurisdiction (e.g. 7 years for financial records).

---

## Quick reference table

| Area | Key doc | Main human action |
|------|---------|-------------------|
| UI / Control Plane | [CONTROL_PLANE_RUNBOOK.md](./CONTROL_PLANE_RUNBOOK.md), [EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md](./EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md) | Run tabs, collect signals, fix blockers using next command/owner/SLA/evidence |
| Church / banking | [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md), [CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md](./CHURCH_PAYOUT_AND_BANK_GOVERNANCE.md) | Plaid, 24 bank links, last4, payees, agreements, 2-person approval for method/first payout |
| GHL / freebies | [funnel/burnout_reset/GHL_HANDBOFF.md](../funnel/burnout_reset/GHL_HANDBOFF.md), [FREEBIE_MARKETING_PLAN.md](./FREEBIE_MARKETING_PLAN.md) | Give GHL admin: API key + Location ID; custom field UUIDs; tags/automations as desired |
| Pre-publish / release | [scripts/ci/PREPUBLISH_CHECKLIST.md](../scripts/ci/PREPUBLISH_CHECKLIST.md) | Run prepublish gates; only export when exit 0 |
| Pearl News | [PEARL_NEWS_GO_NO_GO_CHECKLIST.md](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md) | Networked run + CI green + signed checklist with evidence |
| Audiobook pipeline | [GO_LIVE_FINAL_CHECKLIST.md](./GO_LIVE_FINAL_CHECKLIST.md) | 10-item sign-off before first production run |
| Creative quality | [CREATIVE_QUALITY_VALIDATION_CHECKLIST.md](./CREATIVE_QUALITY_VALIDATION_CHECKLIST.md) | After each compile: arc, story, exercise, voice, ending |
| Approvals (block release) | [EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md](./EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md) § Approval Blockers | Sign Pearl News, church, governance checklists; UI blocks release until approved |
