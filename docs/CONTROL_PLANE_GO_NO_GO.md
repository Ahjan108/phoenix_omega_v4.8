# Control Plane Go/No-Go Checklist

**Purpose:** Pass/fail checks per tab before declaring the Phoenix Control macOS app production-ready.  
**Authority:** Design spec and [CONTROL_PLANE_SPEC_PATCH_V1.1.md](./CONTROL_PLANE_SPEC_PATCH_V1.1.md).  
**Related:** [CONTROL_PLANE_RUNBOOK.md](./CONTROL_PLANE_RUNBOOK.md) (evidence), [PRODUCTION_100_PLAN.md](./PRODUCTION_100_PLAN.md).

---

## 1. Build + run proof

| Check | Pass criteria |
|-------|----------------|
| Xcode project compiles | `xcodebuild -project PhoenixControl.xcodeproj -scheme PhoenixControl build` succeeds (or Cmd+B in Xcode). |
| App launches | App runs on macOS 13+ without crash on launch. |
| All tabs load | Dashboard, Pipeline, Simulation, Tests, Observability, Gates, Pearl News, Teacher, CI, Docs (and any new tabs from Spec Patch v1.1) each show content. |

---

## 2. End-to-end wiring (real commands + artifacts)

Each tab executes **real** repo commands and reads **real** artifacts (no mock data). Evidence per tab: screenshot or log excerpt proving that tab works on real repo data.

| Tab | Pass criteria |
|-----|----------------|
| Dashboard | Repo path set; observability phase/snapshot/evidence summary; approvals summary; Missing/Blocked summary. |
| Observability | Collect signals runs; snapshot + evidence/elevated tables update from real JSONL. |
| Pipeline / Simulation / Tests / Gates / Pearl News / Teacher / Docs / CI | Run buttons execute real scripts; log streams; completion or clear error. |
| Completeness (when implemented) | Scorecard from `book_script_content_validation.py`; drill-down works. |
| Approvals (when implemented) | Required approvals list; status; blocker when not approved; launch actions disabled. |
| Missing/Blocked | Queue shows items from completeness, approvals, checks; severity, owner, fix action. |

---

## 3. Safety controls

| Check | Pass criteria |
|-------|----------------|
| Cancel | Running script can be cancelled; log shows termination. |
| Timeout | Long run terminates after timeout; error shown. |
| Path validation | Invalid repo path shows validation message; run disabled until valid. |
| Command allowlist | Only allowlisted scripts run. |
| Clear errors | Failure shows in log and/or global error alert. |

---

## 4. Observability truth UI

Dashboard and Observability show **real** P1/P2/P3/P4 status derived from repo (collector, evidence_log, elevated_failures), not static text.

---

## 5. Secrets

GitHub token and WP creds in Keychain only; script output redacted (no secrets in logs).

---

## 6. GitHub integration

When token set: workflow status and production-alert issues load; rate-limit/offline show graceful message.

---

## 7. QA + release

Manual QA matrix per tab; unit tests (ScriptRunner, ArtifactReader); integration test (run → artifact refresh → UI). Signed app; crash logging strategy; versioned release notes; rollback plan.

---

## 8. Definition-of-done evidence (required per tab)

- **Evidence per tab:** Screenshot or log excerpt proving that tab works on real repo data.
- **Runbook:** [CONTROL_PLANE_RUNBOOK.md](./CONTROL_PLANE_RUNBOOK.md) executed; evidence recorded.

---

## 9. Pilot then scale

Before broad use: 1-week internal pilot; designated on-call owner and SLA; then scale.

---

## Go

When all sections above are **pass** and evidenced, the control plane is **production-ready**.

## No-Go

If any required check fails or is not evidenced, do not declare production-ready.
