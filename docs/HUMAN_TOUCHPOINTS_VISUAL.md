# Required Human Touchpoints — System-Wide

**Purpose:** Every place a human must touch the system for it to work. Optional steps are omitted.

---

## Visual: Where the human touches the system

```mermaid
flowchart TB
    subgraph HUMAN["👤 Human (required actions only)"]
        direction TB
    end

    subgraph CONTROL["Control plane & repo"]
        H1["Build Phoenix Control (Xcode, Cmd+R)"]
        H2["Set repo path to phoenix_omega root"]
        H3["Install Python 3 + repo dependencies"]
        H4["Run Observability → Collect signals"]
        H5["Run pipeline/tests/gates when needed"]
        H6["Fix blockers using next command + evidence"]
    end

    subgraph AUDIO["Audiobook pipeline"]
        A1["Start LM Studio with Qwen at http://127.0.0.1:1234"]
        A2["Put source content in artifacts/audiobook/source/"]
        A3["Run comparator loop (or trigger from UI)"]
        A4["Work Manual Review queue: triage & fix sections that failed gates"]
        A5["Sign 10-item go-live checklist before first production run"]
    end

    subgraph VIDEO["Video pipeline"]
        V1["Run run_pipeline.py with --plan-id (or UI)"]
        V2["Provide render manifest / fixtures"]
        V3["Set R2 env: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME (for distribution)"]
        V4["Provide Flux credentials (cloudflare_workers_ai.txt) if using image gen"]
        V5["Review caption truncation flags when QC flags >50% truncation"]
    end

    subgraph PAYOUT["Church / payout"]
        P1["Complete both church agreements (existing + VWM/Google Play/bank)"]
        P2["Put Plaid client_id + secret in config/payouts/credentials.yaml"]
        P3["Run link_server → connect 24 church bank accounts via Plaid Link"]
        P4["Provide Bluevine last4 for 24 churches → churches.yaml"]
        P5["Provide 24 payee names + bank_last4 → payees.yaml"]
        P6["2-person approval for payout method changes and first payout to new payee"]
    end

    subgraph GHL["GHL / freebie funnel"]
        G1["Create GHL API Key 2.0 → set GHL_API_KEY"]
        G2["Set GHL_LOCATION_ID"]
        G3["Create custom fields in GHL; put field UUIDs in app config (or contact push fails)"]
    end

    subgraph RELEASE["Release & production"]
        R1["Run prepublish gates before publish (exit 0 only)"]
        R2["Run production readiness gates + simulation"]
        R3["Sign Pearl News GO/NO-GO checklist with evidence"]
        R4["Sign approvals that block release (Pearl News, church, governance)"]
        R5["No production sign-off without run URLs + artifacts + digest evidence"]
    end

    subgraph QUALITY["Content quality"]
        Q1["Creative quality validation after each book compile (arc, story, exercise, voice, ending)"]
        Q2["First 10 books: blind listen, 5-axis score, pattern analysis"]
        Q3["Approve teacher atoms: approve_atoms.py / batch_approve_teacher_atoms.py"]
        Q4["Approve exercises: exercise_approve.py"]
    end

    HUMAN --> CONTROL
    HUMAN --> AUDIO
    HUMAN --> VIDEO
    HUMAN --> PAYOUT
    HUMAN --> GHL
    HUMAN --> RELEASE
    HUMAN --> QUALITY
```

---

## One-page table: Required human actions only

| Area | What the human must do |
|------|-------------------------|
| **Control plane** | Build Phoenix Control; set repo path; install Python + deps. Run Collect signals; run pipeline/tests/gates as needed; fix blockers using next command and evidence path. |
| **Audiobook** | Start LM Studio with Qwen at `http://127.0.0.1:1234`; put source content in `artifacts/audiobook/source/`; run pipeline (or UI); work Manual Review queue for failed sections; sign 10-item go-live checklist before first production run. |
| **Video** | Run `run_pipeline.py` with plan-id; provide render manifest/fixtures; set R2 env vars for distribution; provide Flux credentials if using image gen; review caption truncation when QC flags >50%. |
| **Church / payout** | Complete both church agreements; put Plaid credentials in `config/payouts/credentials.yaml`; run link_server and connect 24 bank accounts; provide 24 churches’ Bluevine last4 and 24 payees’ name + bank_last4; 2-person approval for payout method changes and first payout to new payee. |
| **GHL / freebies** | Set `GHL_API_KEY` and `GHL_LOCATION_ID`; create custom fields in GHL and put their UUIDs in app config so contact push works. |
| **Release** | Run prepublish gates (publish only when exit 0); run production readiness; sign Pearl News GO/NO-GO; sign all approvals that block release; retain run URLs + artifacts + digest for sign-off. |
| **Content quality** | Creative quality checklist after each compile; first 10 books evaluation; approve teacher atoms and exercises so content is eligible for use. |

---

## Authority

- Aggregated from [HUMAN_INTERACTIONS_REFERENCE.md](./HUMAN_INTERACTIONS_REFERENCE.md), [audiobook_operator_runbook.md](./audiobook_operator_runbook.md), [VIDEO_PIPELINE_SPEC.md](./VIDEO_PIPELINE_SPEC.md), [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md), [GO_LIVE_FINAL_CHECKLIST.md](./GO_LIVE_FINAL_CHECKLIST.md). Optional items (e.g. international partner payees, “when implemented” tabs, recommended tags) are omitted.
