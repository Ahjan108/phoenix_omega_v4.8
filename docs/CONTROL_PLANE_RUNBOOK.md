# Control Plane Runbook — Proof that each tab works on real repo data

**Purpose:** Demonstrate that every core function runs real repo commands and reads real artifacts. Satisfies definition-of-done evidence in [CONTROL_PLANE_GO_NO_GO.md](./CONTROL_PLANE_GO_NO_GO.md).  
**Authority:** [CONTROL_PLANE_SPEC_PATCH_V1.1.md](./CONTROL_PLANE_SPEC_PATCH_V1.1.md).

---

## Prerequisites

- Phoenix Control app built and launched (Xcode: open `PhoenixControl.xcodeproj`, Cmd+R).
- Repo path set to phoenix_omega root.
- Python 3 and repo dependencies installed.

---

## 1. Dashboard

1. Open **Dashboard**.
2. **Pass:** With repo path set and after running the collector at least once: observability phase (P1–P4), snapshot summary, evidence/elevated counts, branch protection checklist.
3. **Evidence:** Screenshot of Dashboard with non-empty snapshot and phase status.

---

## 2. Observability

1. Open **Observability**.
2. Click **Collect signals**.
3. **Pass:** Log streams; on completion, snapshot and evidence/elevated tables update from real JSONL.
4. **Evidence:** Screenshot after successful collect with at least one evidence row (or note “no failures” if elevated empty).

---

## 3. Pipeline / Simulation / Tests / Gates / Pearl News / Teacher / Docs

For each tab: run the primary action (e.g. Run pipeline, Run sim, Run core tests, Run gates, Run article pipeline, Run teacher gates, Run docs check). **Pass:** Log streams; completion or clear error. **Evidence:** Log tail or screenshot.

---

## 4. CI / Workflows

**Pass:** Owner/repo set; with token, Refresh loads workflow runs and production-alert issues; links open correct URLs. **Evidence:** Screenshot of CI tab with runs or issues.

---

## 5. Completeness (when implemented)

Run validation; scorecard shows global % and by locale/language/persona/topic/engine/teacher; drill-down works. **Evidence:** Screenshot of scorecard and one drill-down.

---

## 6. Approvals (when implemented)

Approvals tab shows required items and status; if any not approved, red blocker and launch actions disabled. **Evidence:** Screenshot showing blocker when approval missing.

---

## 7. Missing/Blocked queue (when implemented)

Queue lists items with severity, owner, source, fix action. **Evidence:** Screenshot of queue with at least one item or “No blockers.”

---

## Safety checks

- **Cancel:** Start a long run, click Cancel; process stops.
- **Invalid path:** Set invalid repo path; run disabled or validation message shown.
- **Error display:** Force a failure; error in log and/or alert.

When all sections are executed and evidence (screenshots/log tails) recorded, the runbook satisfies definition-of-done evidence for production readiness.
