# Executive Dashboard + PhoenixControl: recommended setup

**Purpose:** Two-tier operator UI: native Mac app for actions and quick status; Python dashboard for charts and cross-artifact views. Implementation-ready with explicit acceptance criteria.

---

## Current state

- **PhoenixControl (Swift/SwiftUI):** Dashboard, Pipeline, Observability, Gates, Pearl News, Teacher, CI, etc., with status cards, evidence/snapshot tables, and live logs.
- **Observability:** evidence_log.jsonl, elevated_failures.jsonl, signal_snapshot*.json, config/observability_production_signals.yaml.
- **Ops/reports:** artifacts/ops/platform_health_scorecard_*.json, artifacts/ops/coverage_health_weekly_*.json, artifacts/governance/system_governance_report.json, artifacts/reports/pearl_prime_sim_analysis.json, scripts/obs/build_structural_drift_dashboard.py → artifacts/drift/report.html.
- **No** existing Streamlit/Dash app or “sales/marketing” metrics in the traditional sense; “sales” and “marketing” here are pipeline/catalog and Pearl News / deep research.

---

## Two-tier approach

| Layer | Role | Tech |
|------|------|------|
| **1. Native Mac app** | Control plane: run scripts, view evidence/snapshot, branch checklist, workflows, and “Open Executive Dashboard” | PhoenixControl (existing) |
| **2. Executive dashboard** | Tabs: System operations, Sales (catalog/pipeline), Marketing (Pearl News / deep research), All system; advanced charts; same repo path as Mac app | Python: Streamlit + Plotly (or Dash) |

Use the Mac app for actions and quick status; use the Python dashboard for charts and cross-artifact views. The Mac app launches the dashboard (with repo path) and opens it in the browser; no need to embed a WebView for MVP.

---

## Data sources (already in repo)

**System operations**

- artifacts/observability/signal_snapshot*.json — pass/fail/skip, per-signal status (e.g. ObservabilitySnapshot in PhoenixControl).
- artifacts/observability/evidence_log.jsonl, elevated_failures.jsonl — same schema the Mac app uses (EvidenceLogRow).
- artifacts/ops/platform_health_scorecard_*.json — composite_score, tier, components, alerts_summary.
- artifacts/ops/coverage_health_weekly_*.json — summary (total_tuples, risk_counts, velocity_by_persona, top_10_risk_tuples), previous_report for deltas.
- artifacts/governance/system_governance_report.json — from scripts/ci/check_system_governance_status.py.
- artifacts/reports/pearl_prime_sim_analysis.json — sim pass rate, dimensions.

**Sales (catalog / pipeline output)**

- Same coverage_health_weekly_*.json: viable_tuples, total_story_atoms, velocity_by_persona, story_growth_rate, top_10_risk_tuples.
- Counts: artifacts/systems_test/plans/*.json, artifacts/full_catalog/candidates*, artifacts/compiled/*, artifacts/freebies/artifacts_index.jsonl (and any book-pass reports).

**Marketing**

- Pearl News: pipeline evidence, drafts, networked_run_evidence.json (see DOCS_INDEX / PEARL_NEWS_).
- marketing_deep_research/, artifacts/freebies/ (e.g. artifacts_index.jsonl), locale/catalog marketing docs.

All paths are relative to repo root; the dashboard takes REPO_PATH (env or --repo) so it uses the same root as PhoenixControl.

---

## Tech choice: Streamlit + Plotly

- **Streamlit:** quick tabs, file-based data, no backend DB. Run with `streamlit run dashboard.py`; optional `--server.headless true` when launched from the Mac app.
- **Plotly:** line/bar/pie/drill-down and time series; works well with pandas DataFrames built from the JSON/JSONL above.
- **Pandas:** load JSON/JSONL, aggregate for charts.
- No new backend: read from REPO_PATH/artifacts/... and optional GitHub API (env token) for workflow status.

---

## Dashboard layout (conceptual)

**Tabs:** System operations, Sales, Marketing, All system.

- **Operations:** Snapshot pass/fail/skip over time (from multiple snapshot files), platform_health composite_score, coverage_health summary. Charts: time series of pass rate, pie of risk_counts (BLOCKER/RED/YELLOW/GREEN), bar of velocity_by_persona.
- **Sales:** viable_tuples, total_story_atoms, velocity_by_persona, plan counts. Charts: bar by persona, trend from previous_report if present.
- **Marketing:** Pearl News runs, freebies count, deep-research status. Tables + simple charts.
- **All system:** Combined summary + links to key artifacts (same as DOCS_INDEX).

---

## Integrating with the native Mac app

- **PhoenixControl** gets one action: **“Executive Dashboard”** (toolbar or menu).
- Set REPO_PATH (or equivalent) to the app’s repo path (e.g. from UserDefaults / @AppStorage).
- **Launch:** ScriptRunner (or Process) runs `streamlit run /path/to/dashboard.py --server.headless true` with cwd = repo path and env REPO_PATH=&lt;repo path&gt;.
- **Open:** NSWorkspace.shared.open(URL(string: "http://localhost:8501")!).
- Optional later: embed in a WKWebView (same URL) for “dashboard inside the app”; start with external browser to avoid WebView quirks.

So “integrate with native Mac OS window app” = Mac app launches the Python dashboard with the correct repo path and opens it in the browser (or, later, in an embedded WebView).

### App distribution: Dock and Applications

- **PhoenixControl** must be built as a proper **macOS .app bundle** so it can be **docked with other apps** and **appear in the Applications folder** in Finder.
- **Install target:** The app shall be installable to `/Applications` (or the user’s `~/Applications`) and appear in **Finder → Applications** like any other Mac app.
- **Dock:** When the user adds the app to the Dock or runs it from Applications, it behaves like a normal docked app (icon in Dock when running, optional “Keep in Dock”).
- **Delivery:** Provide a signed .app (or .dmg) and install instructions (e.g. “Drag PhoenixControl.app to Applications”); no requirement to ship via the Mac App Store for this spec.

---

## Suggested dashboard file layout

- **Repo root (or e.g. dashboard/):**
  - **dashboard.py** — Streamlit entry; reads `os.environ.get("REPO_PATH", ".")` or `--repo`; builds tabs from artifacts.
  - **dashboard_data.py** (or inline) — functions that load: latest snapshot(s), evidence/elevated JSONL; latest platform_health_scorecard_*.json and coverage_health_weekly_*.json; system_governance_report.json, pearl_prime_sim_analysis.json; Pearl News / freebies indexes as needed.
- **requirements-dashboard.txt:** streamlit, plotly, pandas (and any existing deps if run from repo venv). **Pinned versions** (see Acceptance criteria below).

PhoenixControl already has the exact artifact paths in ArtifactReader and the observability snapshot model; the Python dashboard can mirror those paths (see PhoenixControl/Services/ArtifactReader.swift and ObservabilitySnapshot).

---

## “Sales” and “marketing” in this system

- **Sales:** Pipeline and catalog health — coverage_health (viable_tuples, story counts, velocity by persona), plan/compiled/freebie counts. No CRM; all from artifacts/.
- **Marketing:** Pearl News (articles, pipeline runs, evidence), freebies index, marketing deep research and locale/catalog docs. Again file-based.
- If you later add real sales (e.g. store or distribution) or marketing (e.g. GA), add a small adapter that writes JSON/CSV into artifacts/ or a dedicated path and point the dashboard at it.

---

## Minimal UI additions

Only these additions are required; no major UI redesign.

### 1. Governance blockers card

Show **3 blockers explicitly** (pass/fail and, when failed, next-action text per §4 below):

| Blocker | Description |
|---------|-------------|
| **DOCS_INDEX link integrity** | Links in docs/DOCS_INDEX.md resolve; no broken file refs. |
| **Gate 17 jsonschema runtime** | Gate 17 (jsonschema runtime check) passes. |
| **Gate 16b CTA caps** | Gate 16b (CTA caps) passes. |

Card shows each of the three with status (e.g. ✓ pass / ✗ fail). When failed, show exact fix command/path per “Clear next-action text” below.

### 2. One-click verify actions

Buttons that run the following scripts (e.g. via ScriptRunner or subprocess; repo path = REPO_PATH):

| Button label | Command |
|--------------|---------|
| **Check docs governance** | `check_docs_governance.py` (or `scripts/ci/check_docs_governance.py`) |
| **Run production readiness gates** | `run_production_readiness_gates.py` (or `scripts/run_production_readiness_gates.py`) |
| **Check system governance status** | `check_system_governance_status.py` (or `scripts/ci/check_system_governance_status.py`) |

Each button runs the script with cwd = repo root; output visible in log or inline. No need for extra UI beyond these three actions.

### 3. Freebies index health panel

Display in one panel:

| Field | Description |
|-------|-------------|
| **Current index source** | Path to the index file in use (e.g. `artifacts/freebies/index.jsonl` or equivalent). |
| **Row count** | Number of rows in the index. |
| **Gate 16 result** | Pass/fail (and optional detail) for Gate 16. |
| **Gate 16b result** | Pass/fail (and optional detail) for Gate 16b (CTA caps). |
| **Last rebuild timestamp** | When the index was last built or updated (mtime or from report). |

Single panel; no extra decoration.

### 4. Clear next-action text

For **each failed blocker** (Governance blockers card or any top-row blocker), show **exact fix command or path** (e.g. “Run: `python scripts/ci/check_docs_governance.py`”, “Fix link at docs/DOCS_INDEX.md line 852”). So the operator knows the precise next step without searching.

### 5. Evidence links

Direct links (clickable file path or “Open” button) to:

- `artifacts/governance/system_governance_report.json`
- `artifacts/freebies/index.jsonl`
- `docs/DOCS_INDEX.md`

Links open the file in the default app (e.g. editor or browser) or copy path to clipboard; implementation choice. These three links must be available from the dashboard and/or PhoenixControl (e.g. in a sidebar or “Evidence” section).

---

## Acceptance criteria (implementation-ready)

The following 6 bullets must be satisfied before handoff is “done.” Execution must be unambiguous.

### 1. Top-row blockers

- The Executive Dashboard **must** show **hard blockers first** (top of the first tab or a dedicated “Blockers” strip).
- Hard blockers include: gates fail, approvals missing, freebies caps fail.
- No scrolling required to see blocker count and at least the first N items (e.g. top 5).

### 2. Freshness policy

- **Every widget** must display **last_updated** (timestamp of the data used).
- **Stale data threshold** must be clearly marked (e.g. “Stale if older than 60 min” or configurable value in UI/config).
- When data is stale, widget shows a “Stale” indicator or badge in addition to last_updated.

### 3. Data-contract table

- For **each tab / card**: document in the spec (or in-app help) the **data contract**:
  - **Source file(s):** exact path(s) under REPO_PATH (e.g. artifacts/ops/platform_health_scorecard_*.json).
  - **Fallback if missing:** what the widget shows when the file is absent (e.g. “No data”, last known snapshot, or error message).
  - **Refresh cadence:** when data is re-read (e.g. on tab focus, on manual Refresh, every N minutes).
- Implement so each card’s behavior matches the contract.

### 4. Launch contract (PhoenixControl ↔ Streamlit)

- **PhoenixControl** starts Streamlit with **REPO_PATH** set (env or arg) so the dashboard reads from the same repo as the app.
- **Port:** Confirm dashboard is reachable on **8501** (or document alternate port and use it consistently).
- **Browser:** On success, open browser to http://localhost:8501 (or the chosen port).
- **Launch error:** If Streamlit fails to start (process exit non-zero or port not listening within timeout), PhoenixControl **must** show a clear launch error (e.g. alert or inline message: “Executive Dashboard failed to start: &lt;reason&gt;”). No silent failure.

### 5. Dependency pinning

- **requirements-dashboard.txt** must list **pinned versions** for Streamlit, Plotly, and Pandas (e.g. streamlit==1.28.0, plotly==5.18.0, pandas==2.1.0).
- Optional: pin other deps used only by the dashboard. Document that install is `pip install -r requirements-dashboard.txt`.

### 6. Done criteria (test checklist)

A short **test checklist** must be run to confirm handoff:

| # | Check | Pass criterion |
|---|--------|----------------|
| 1 | **Tab loads** | Each tab (System operations, Sales, Marketing, All system) loads without crash and shows at least one section. |
| 2 | **Artifact parsing** | For each documented source file, if the file exists and is valid, the dashboard parses it and displays data (no parse error). |
| 3 | **Stale/missing behavior** | If a source file is missing or empty, the widget shows the documented fallback (e.g. “No data”, “File not found”) and does not crash. |
| 4 | **Blocker rendering** | When at least one hard blocker exists (e.g. gate fail, approval missing), the dashboard shows it in the top-row blockers area with correct count and at least one item visible. |
| 5 | **Launch from Mac app** | From PhoenixControl, “Executive Dashboard” starts Streamlit with REPO_PATH, and browser opens to the dashboard; if start fails, user sees launch error. |
| 6 | **Last_updated on widgets** | Every widget displays last_updated; stale threshold is visible or documented. |
| 7 | **Minimal UI additions** | Governance blockers card (3 blockers: DOCS_INDEX link integrity, Gate 17 jsonschema runtime, Gate 16b CTA caps); 3 one-click verify buttons; Freebies index health panel (source, row count, Gate 16/16b result, last rebuild); next-action text per failed blocker; evidence links to system_governance_report.json, freebies index.jsonl, DOCS_INDEX.md. |
| 8 | **Autonomous loop UI** | Loop Status panel; Agent Queue view (pending/active/completed, safe-fix reason, scope); PR Automation panel (bot PRs, auto-merge eligibility, blocked reason); KPI Trigger board; Weekly Orchestrator run page; Operations Board tab (signal_id, suggested_fix, PR link, merge status, before/after impact); Manual override controls (pause/resume, disable auto-merge, rerun one stage). |
| 9 | **App distribution** | PhoenixControl built as .app bundle; installable to /Applications or ~/Applications; appears in Finder → Applications and can be docked with other apps. |
| 10 | **Safety Kill Switch visibility** | Top-level “Autonomy OFF/ON” state visible in UI; immutable audit log for every state change (who, when, why); no autonomous loop activity when OFF. |
| 11 | **Autonomous loop dashboard (minimal set)** | Loop Health card (Continuous/Daily/Weekly status + last run time); Operations Board table (operations_board.jsonl with filters: source, decision, severity); Promotion Queue panel (queue size, top candidates, why held/skipped); Autonomy toggle state (ON/OFF + policy file source); Artifact freshness (last-updated for weekly_report, baseline, loop logs); Run-now actions (buttons for continuous/daily/weekly scripts + links to workflow runs). |

When all 6 acceptance criteria, the test checklist (including minimal UI, autonomous loop UI, autonomous loop dashboard minimal set, app distribution, Safety Kill Switch), the 5 operator-completeness requirements plus 2 final items, and the 7 autonomous loop UI items pass, the implementation is ready for handoff. With Dock/Applications and Safety Kill Switch visibility, the spec is **complete**.

---

## Operator completeness (100% handoff)

For true 100% operator-complete handoff, the following must be **explicit** and implemented. The **5 operator-completeness requirements** are: (1) Completeness Board, (2) Approval Blockers, (3) Governance Blockers Panel, (4) Action Mapping, (5) Acceptance Matrix. Plus **2 final items**: (6) Weekly Loop Automation Contract, (7) Decision Log. Freeze scope after these are added.

---

### 1. Completeness Board (operator requirement 1)

**Required cards** with exact formulas and **red / yellow / green thresholds** for locale, language, persona, topic, and catalog completion %.

| Dimension | Formula | Green (pass) | Yellow (warning) | Red (fail) |
|-----------|---------|--------------|-------------------|------------|
| **Locale** | `(locales_with_required_content / locales_in_scope) * 100` | ≥ 100% | &lt; 100% and ≥ 90% | &lt; 90% |
| **Language** | `(languages_with_required_content / languages_in_scope) * 100` | ≥ 100% | &lt; 100% and ≥ 90% | &lt; 90% |
| **Persona** | `(personas_with_min_atoms / personas_in_scope) * 100` | ≥ 100% | &lt; 100% and ≥ 90% | &lt; 90% |
| **Topic** | `(topics_with_min_atoms / topics_in_scope) * 100` | ≥ 100% | &lt; 100% and ≥ 90% | &lt; 90% |
| **Catalog** | `(books_meeting_quality_gates / books_in_catalog_scope) * 100` | ≥ 95% (or config) | &lt; 95% and ≥ 85% | &lt; 85% |

**UI:** Completeness Board shows one card per dimension with completion % and color (red/yellow/green). **Source:** Coverage/validation scripts (e.g. `book_script_content_validation.py`, coverage_report). Document the script and config keys used; thresholds may be overridden in config.

### 2. Approval Blockers (operator requirement 2)

**Formal states** and **hard stop rules** for release. Any approval in a blocking state prevents release/go-live; UI must show them.

| State | Definition | Release blocked? |
|-------|------------|------------------|
| **missing** | Source-of-truth file or checklist row absent. | Yes. |
| **pending** | File/row present but not yet submitted or signed. | Yes. |
| **approved** | Checklist signed with name/date; not past expiry. | No. |
| **expired** | Approval date older than policy; re-approval required. | Yes. |

**Hard stop rules:** (1) **Pearl** — Pearl News church/governance approvals must be `approved` before Pearl News launch or post. (2) **Church** — Church/brand approvals (e.g. NorCal Dharma, governance evidence) must be `approved` for that domain’s release. (3) **Governance evidence** — Any approval marked “blocks release” in config (e.g. signed GO/NO-GO, evidence bundle) must be `approved` before release. **UI:** Show approval id, name, state, SOT path; if state ≠ `approved`, show red blocker and disable release/go-live actions.

### 3. Governance Blockers Panel (operator requirement 3)

**Must show and run** in one panel (or card):

| Item | Show | Run (one-click) |
|------|------|-----------------|
| **DOCS link integrity** | Pass/fail; broken links if any | `check_docs_governance.py` |
| **Gate 16** | Pass/fail (freebies density) | Via production readiness or system governance |
| **Gate 16b** | Pass/fail (CTA caps) | Via production readiness or system governance |
| **Gate 17** | Pass/fail (jsonschema runtime) | Via production readiness or system governance |
| **Freebies index health** | Source path, row count, last rebuild; Gate 16/16b result | — |
| **Next fix command** | For each failed item: exact fix command or path | — |

**Rule:** The Governance Blockers Panel displays all of the above and provides run actions for DOCS governance and gates where applicable. Every failed blocker shows the exact next fix command (see Action Mapping below).

### 4. Action Mapping (operator requirement 4)

Every **failed** status must include:

| Field | Required | Description |
|-------|----------|-------------|
| **Exact next command** | Yes | CLI command or UI action to fix (e.g. `python scripts/ci/check_docs_governance.py`, “Sign checklist at docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md”). |
| **Owner** | Yes | Team or person responsible (e.g. “platform”, “content”, “on-call”). |
| **Due / SLA** | Yes | Time expectation (e.g. “Fix within 24h”, “Before release”) or “Document exception”. |
| **Evidence path** | Yes | Path to artifact or doc that proves fix (e.g. `artifacts/governance/system_governance_report.json`, `docs/DOCS_INDEX.md`). |

**Rule:** For every item in the top-row blockers or Action queue, all four (next command, owner, due/SLA, evidence path) must be populated. No failed status without a defined next command, owner, due/SLA, and evidence path.

---

### 5. Freebies governance panel

First-class UI state for freebies in the Executive Dashboard and/or PhoenixControl.

| Element | Description |
|---------|-------------|
| **Density** | Pass/fail vs configured density thresholds (e.g. identical_bundle, identical_cta, identical_slug_pattern). |
| **CTA caps** | CTA signature caps per brand/quarter; max_same_cta_signature status. |
| **Scope source** | Label: “wave” vs “global” (index scope). |
| **Pollution status** | Warnings for over-reuse (bundle/CTA/slug); index health. |
| **Pass/fail gate state** | Single pass/fail for the freebies gate (e.g. density + caps); red if fail. |

**Source:** `validate_freebie_density`, `artifacts/freebies/index.jsonl`, config `cta_anti_spam.yaml`, `check_wave_density`. Panel must show all five elements; data contract per §6.

### 6. Agent change/learning feed

“What changed, why, impact, rollback link.” Required for operator visibility.

| Field | Description |
|-------|-------------|
| **What changed** | Short summary (e.g. “PR #123: updated persona lexicons”, “Workflow: EI V2 calibration”). |
| **Why** | Reason or trigger (e.g. “Scheduled run”, “Config change”). |
| **Impact** | Test/score delta or affected scope. |
| **Rollback link** | URL or exact command to revert (e.g. PR revert, “Set marketing_sources.enabled=false”). |

**Source:** GitHub API (PRs, workflow runs), EI/learning artifacts. **UI:** Dedicated feed or section; each row has the four fields. Data contract per §6.

### 7. Data contract table (per widget)

For each widget/panel, the following must be defined and implemented.

| Widget / panel | Source | Refresh cadence | Stale policy | Fallback behavior |
|----------------|--------|------------------|--------------|-------------------|
| **Completeness** | e.g. `book_script_content_validation.py --json` or artifact | On load / manual; optional scheduled | If older than X min, show “Stale” + last_updated | Last known scorecard + error message; red banner |
| **Approvals** | SOT files + checklist paths | On load / manual | If file mtime older than X, show “Stale” | “Unknown”; treat as blocking (red) |
| **Top-row blockers** | Aggregation from gates, approvals, freebies, etc. | On Dashboard open / after any source refresh | Re-aggregate when any source refreshes | Partial list; errors as queue items |
| **Freebies governance** | validate_freebie_density + index.jsonl + config | On load / after pipeline run | Show last run time; “Stale” if older than X | Last run result + error |
| **Agent change feed** | GitHub API + workflow/agent artifacts | On load / manual; rate-limit aware | Show last fetch time | Offline/rate-limit message; last cached data |
| **System operations / Sales / Marketing tabs** | Per Data sources section above | On tab focus / manual | Same: last_updated + stale threshold | Per-artifact fallback (e.g. “No data”, last snapshot) |

**Rule:** Before shipping a widget, document its row (source, refresh cadence, stale policy, fallback behavior). No widget without a contract.

### 8. Acceptance Matrix (operator requirement 5)

Testable checklist proving: **“UI shows what is missing, why it blocks, and how to fix.”**

| Scenario | UI must show | Pass criterion |
|----------|--------------|----------------|
| Something is missing | What is missing (e.g. locale gap, approval, gate fail) | Operator sees the missing item explicitly |
| Why it blocks | Why it blocks (e.g. “Blocks release”, “Gate 16b fail”) | Operator sees the blocking reason |
| How to fix | Exact next command, owner, due/SLA, evidence path | Operator can run the fix and verify via evidence path |
| Completeness gap | Completeness Board card red/yellow; Action row with command, owner, SLA, evidence path | Operator can see gap and run the stated fix |
| Approval not approved | Approvals state; red blocker; release disabled; Action row with command, owner, SLA, evidence path | Operator sees blocker and owner; cannot launch until resolved |
| Governance blocker fail | Governance Blockers Panel shows fail + next fix command; Action row with evidence path | Operator sees failure and next action |
| Any red status | Top-row blockers or Action queue: next command, owner, due/SLA, evidence path | Every red maps to an actionable row with evidence |

**Definition of pass:** For each scenario, put system in that state and assert the “Pass criterion” holds. The acceptance matrix is the testable checklist for “UI shows what is missing, why it blocks, and how to fix.” Implement automated or manual tests that cover this matrix.

---

### 9. Weekly Loop Automation Contract (final item 1)

Define **exactly** what runs weekly, what auto-PRs are allowed, and merge rules.

| Item | Definition |
|------|------------|
| **What runs weekly** | Explicit list: e.g. full test suite, production readiness gates, calibration run (EI V2 or marketing), dashboard refresh (artifact scrape), coverage report, system governance status. Document script names and schedule (e.g. “Every Monday 00:00 UTC”). |
| **Auto-PRs allowed** | Which automated PRs are permitted (e.g. “Dependabot”, “docs Last updated only from check_system_governance_status.py --fix”). No auto-merge of content or config without approval. |
| **Merge rules** | Branch protection: who can merge, required checks, required reviews. Release: only from `release/*`; only tagged `vX.Y.Z` can ship (per RELEASE_POLICY). |

**Deliverable:** One doc or config section (e.g. in runbook or REPO) that lists weekly jobs, allowed auto-PRs, and merge rules. Dashboard and PhoenixControl may show “Last weekly run” and link to this contract.

---

### 10. Decision Log (final item 2)

**In-app immutable log** of blocker transitions with commit/PR/evidence links.

| Stage | Description | Required link/field |
|-------|-------------|----------------------|
| **Detected** | Blocker first detected (timestamp, source check, result). | Timestamp; check id; result (e.g. fail reason). |
| **Assigned** | Owner assigned; due/SLA set. | Owner; due date; optional ticket/issue link. |
| **Fixed** | Fix applied (commit or PR). | Commit hash or PR URL. |
| **Verified** | Fix verified (re-run check, evidence). | Evidence path or run URL; verification timestamp. |

**Rule:** Each blocker transition (detected → assigned → fixed → verified) is logged with immutable timestamp. **Evidence links:** Commit, PR, or artifact path (e.g. `artifacts/governance/system_governance_report.json`) so the chain is auditable. **UI:** Decision Log panel or section in dashboard/PhoenixControl showing recent blocker lifecycle; optional export (e.g. JSONL or CSV) for audit.

---

## Autonomous loop UI (operable)

Add these to the UI/dashboard so the **autonomous loop** is operable end-to-end. Implement in Executive Dashboard and/or PhoenixControl as appropriate.

### 1. Loop Status panel

Shows each **stage** of the autonomous loop with current state and links:

| Stage | What to show |
|-------|----------------|
| **Detect** | Signals/issues detected (count, last run, link to source). |
| **Fix proposed** | Fix suggested or patch prepared; link to diff or proposal. |
| **PR open** | PR(s) opened by agent; link to PR. |
| **Checks** | CI/check status on PR (pass/fail/pending). |
| **Merged** | Merge status (merged / not merged); link to commit. |
| **Impact** | Before/after impact (e.g. metric delta, test result). |

**UI:** Single panel or strip showing the pipeline stages and current position for the latest (or selected) loop run. Operator can see where the loop is and drill into any stage.

### 2. Agent Queue view

**Pending / active / completed** fix jobs, with:

| Field | Description |
|-------|-------------|
| **Status** | Pending, active, or completed. |
| **Safe-fix reason** | Why this fix is considered safe (e.g. “docs only”, “config threshold change”). |
| **Scope** | Scope of the fix (e.g. “DOCS_INDEX”, “Gate 16b”, “locale en-US”). |

**UI:** Queue or table of agent-initiated fix jobs; filter by status; each row shows safe-fix reason and scope so the operator can approve or intervene.

### 3. PR Automation panel

| Element | Description |
|---------|-------------|
| **Bot PRs** | List of PRs opened by automation/bot; link to PR, title, branch. |
| **Auto-merge eligibility** | Whether each PR is eligible for auto-merge (e.g. checks pass, label present). |
| **Blocked reason** | If not eligible: **missing check**, **missing label**, or **scope violation** (e.g. change outside allowed paths). |

**UI:** Panel showing bot PRs, eligibility, and blocked reason so the operator can unblock or override.

### 4. KPI Trigger board

| Element | Description |
|---------|-------------|
| **Week-over-week KPIs** | Key metrics (e.g. completeness %, gate pass rate, coverage) with current vs previous week. |
| **Thresholds** | Configured thresholds that trigger enhancement jobs (e.g. “completeness &lt; 95% → run gap-fill”). |
| **Which enhancement job fired** | For each threshold breach: which job was triggered (e.g. “gap_fill_locale_en_US”, “calibration_run”). |

**UI:** Board or table: KPI, WoW value, threshold, and “job fired” so the operator sees what triggered the autonomous loop.

### 5. Weekly Orchestrator run page

**Last run** visibility:

| Section | Content |
|---------|---------|
| **Inputs** | Marketing signals (or other inputs) used for the run (e.g. signal snapshot path, config version). |
| **Decisions made** | What the orchestrator decided (e.g. “Run gate 16”, “Open PR for DOCS_INDEX date”). |
| **Outputs** | Artifacts produced (e.g. report path, PR link). |
| **Failures** | Any step that failed; error message or log link. |

**UI:** Dedicated page or tab for the latest Weekly Orchestrator run; operator can inspect inputs, decisions, outputs, and failures.

### 6. Operations Board tab

**Unified issue record** per signal or issue:

| Field | Description |
|-------|-------------|
| **signal_id** | Id of the signal or issue (e.g. from observability or governance). |
| **suggested_fix** | Fix suggested by agent or runbook (text or command). |
| **PR link** | Link to PR if one was opened. |
| **Merge status** | Open, merged, closed without merge. |
| **Before/after impact** | Metric or state before and after fix (e.g. pass rate, completeness %). |

**UI:** Tab “Operations Board” with a table or list of issues; each row is one issue with signal_id, suggested_fix, PR link, merge status, and before/after impact. Single place to see end-to-end status of autonomous fixes.

### 7. Manual override controls

Operator controls to **manage the autonomous system** safely:

| Control | Description |
|---------|-------------|
| **Pause / resume agent loop** | Global or per-job pause; resume when ready. No new fix jobs or PRs while paused. |
| **Disable auto-merge** | Turn off auto-merge for bot PRs; all merges require manual approval. |
| **Rerun one stage safely** | Button or action to rerun a single stage (e.g. “Rerun detect”, “Rerun checks”) without restarting the full loop; confirm before run. |

**UI:** Clearly visible controls (e.g. in sidebar or Operations Board); state (paused/resumed, auto-merge on/off) displayed. Rerun actions are scoped and require confirmation so the loop is operable without unintended side effects.

---

### Autonomous loop dashboard (minimal set)

A **small set** of UI elements is enough to operate the loop safely. All six must be present.

| # | Element | What to show |
|---|---------|----------------|
| 1 | **Loop Health card** | Status of Continuous / Daily / Weekly jobs (e.g. last run result: pass/fail/skip); **last run time** for each (from workflow run or local script timestamp). |
| 2 | **Operations Board table** | Render `artifacts/observability/operations_board.jsonl` (or equivalent) with **filters**: source, decision, severity (if present). Table columns: ts, book_id/issue_id, source, decision, confidence, evidence_path, suggested_fix. |
| 3 | **Promotion Queue panel** | **Queue size** (e.g. row count of promotion_queue.jsonl); **top candidates** (first N rows with book_id, decision, confidence); **why items are held/skipped** (e.g. below_confidence_floor, autonomy_disabled, gate_fail). |
| 4 | **Autonomy toggle state** | Display **autonomy_enabled** clearly as **ON** or **OFF**; show **current policy file source** (e.g. `config/ml_loop/promotion_policy.yaml`). Same as Safety Kill Switch “Autonomy OFF/ON” where the loop is the autonomous system. |
| 5 | **Artifact freshness** | **Last-updated** timestamp for: `weekly_report.json`, `baseline.json`, and loop logs (e.g. operations_board.jsonl last write, or audit log). So operator knows how stale the view is. |
| 6 | **Run-now actions** | **Buttons** for local script runs: run continuous loop, run daily promotion (optional dry-run), run weekly recalibration. **Links** to GitHub workflow runs (e.g. “Open workflow run” for ML loop continuous, daily promotion, weekly recalibration). |

**Rule:** When these 6 are present, the UI can operate the autonomous loop safely (health visibility, operations board with filters, promotion queue and hold reasons, autonomy state, freshness, and run-now + workflow links).

---

## Safety Kill Switch visibility

A **top-level** “Autonomy OFF/ON” state with **audit log** so operators can see and control the autonomous loop and who changed it.

| Requirement | Description |
|-------------|-------------|
| **Autonomy OFF/ON state** | One clearly visible control (e.g. in toolbar, sidebar, or status bar) showing current state: **Autonomy OFF** or **Autonomy ON**. When OFF, the autonomous loop does not run (no new fix jobs, no auto-PRs, no auto-merge). When ON, the loop may run per Weekly Loop Automation Contract. |
| **Audit log** | Every change to the Autonomy state is recorded in an **immutable audit log** with: **who** changed it (user id or “system”), **when** (timestamp, ISO8601 UTC), **why** (optional reason field or “Manual toggle”, “Schedule”, “Override”). |
| **Visibility** | The current state (OFF/ON) and a way to view the **audit log** (e.g. “View audit log” link or panel showing last N entries: who, when, why) must be visible in the UI without drilling into settings. |

**Rule:** No autonomous loop activity when Autonomy is OFF. All state changes are audited so the operator can see who turned autonomy on or off and when. With this, the Safety Kill Switch is complete.

---

**Definition:** When these 7 are present, the UI can manage the autonomous system end-to-end (visibility into loop status, agent queue, PR automation, KPI triggers, weekly run, operations board, and manual overrides).

---

## Blockers & Completeness Contracts

For operator goals, the following must be **explicit** and implemented. This section is the single reference for blockers and completeness.

### Completeness: exact formulas and thresholds

| Dimension | Formula | Green | Yellow | Red |
|-----------|---------|-------|--------|-----|
| **Locale** | `(locales_with_required_content / locales_in_scope) * 100` | ≥ 100% | &lt; 100% and ≥ 90% | &lt; 90% |
| **Language** | `(languages_with_required_content / languages_in_scope) * 100` | ≥ 100% | &lt; 100% and ≥ 90% | &lt; 90% |
| **Persona** | `(personas_with_min_atoms / personas_in_scope) * 100` | ≥ 100% | &lt; 100% and ≥ 90% | &lt; 90% |
| **Topic** | `(topics_with_min_atoms / topics_in_scope) * 100` | ≥ 100% | &lt; 100% and ≥ 90% | &lt; 90% |
| **Catalog** | `(books_meeting_quality_gates / books_in_catalog_scope) * 100` | ≥ 95% (or config) | &lt; 95% and ≥ 85% | &lt; 85% |

**Contract:** UI shows one card per dimension with completion % and color (red/yellow/green). Source: coverage/validation scripts (e.g. `book_script_content_validation.py`). Thresholds may be overridden in config; document the keys.

### Approval blocker states and hard release-stop rules

| State | Definition | Release blocked? |
|-------|------------|------------------|
| **missing** | SOT file or checklist row absent. | Yes. |
| **pending** | File/row present but not submitted or signed. | Yes. |
| **approved** | Checklist signed with name/date; not past expiry. | No. |
| **expired** | Approval date older than policy; re-approval required. | Yes. |

**Hard release-stop rules:** (1) **Pearl** — Pearl News church/governance approvals must be `approved` before Pearl News launch. (2) **Church** — Church/brand approvals (e.g. NorCal Dharma) must be `approved` for that domain’s release. (3) **Governance evidence** — Any approval marked “blocks release” in config must be `approved` before release. **UI:** Show approval id, name, state, SOT path; if state ≠ `approved`, show red blocker and disable release/go-live actions.

---

## Autonomous Loop Operations UI

Dedicated views and explicit failure→action mapping so the operator can run and debug the autonomous loop.

### Dedicated views (required)

| View | Purpose |
|------|---------|
| **Loop health** | Status of Continuous/Daily/Weekly jobs; last run time and result (pass/fail/skip). |
| **Agent queue** | Pending/active/completed fix jobs; safe-fix reason and scope per row. |
| **Promotion queue** | Queue size; top candidates; why items are held or skipped (e.g. below_confidence_floor, autonomy_disabled). |
| **KPI triggers** | Week-over-week KPIs, thresholds, and which enhancement job fired for each breach. |
| **Decision log** | Immutable log of blocker lifecycle: detected → assigned → fixed → verified; commit/PR/evidence links. |

**Contract:** Each view has a data contract (source path, refresh, stale, fallback). No view ships without it.

### Explicit mapping: failure → next command / owner / SLA / evidence

For **every** failed or blocked item (governance blocker, operations board row, promotion hold, gate fail), the UI must show:

| Field | Required | Description |
|-------|----------|-------------|
| **Next command** | Yes | Exact CLI or UI action to fix (e.g. `python scripts/ci/check_docs_governance.py`, “Sign checklist at docs/…”). |
| **Owner** | Yes | Team or person responsible (e.g. “platform”, “on-call”). |
| **SLA** | Yes | Time expectation (e.g. “Fix within 24h”, “Before release”) or “Document exception”. |
| **Evidence path** | Yes | Path or URL to prove fix (e.g. `artifacts/governance/system_governance_report.json`, workflow run URL). |

**Rule:** No failed status without all four. The UI must answer “what to do next” with a concrete command, owner, SLA, and where to verify.

---

## Acceptance Matrix

Testable **Definition of Done** proving the UI always answers the four operator questions. Every scenario must be testable (automated or manual).

| # | Operator question | UI must show | Pass criterion |
|---|-------------------|--------------|----------------|
| 1 | **What is broken?** | The specific broken item (e.g. locale gap, approval missing, gate fail, promotion hold). | Operator sees the exact broken item; no guessing. |
| 2 | **Why does it block?** | The blocking reason (e.g. “Blocks release”, “Gate 16b fail”, “Below confidence floor”). | Operator sees why it blocks (release, merge, promotion). |
| 3 | **What to do next?** | Next command, owner, SLA, and evidence path (per Action Mapping). | Operator can run the stated fix and know where to verify. |
| 4 | **Did the fix work?** | Verification state or evidence (e.g. re-run result, evidence path updated, decision log “Verified”). | Operator can confirm fix (e.g. check passed, approval approved, board row updated). |

**DoD:** For each of the four questions, define test scenarios (e.g. “completeness gap exists”, “approval pending”, “governance blocker fail”). Put the system in that state and assert the “Pass criterion” holds. The spec is **100% handoff-ready** when the Acceptance Matrix is implemented and all four questions are answerable for every blocker and failure path.

---

## Summary

- **Best fit:** Streamlit + Plotly in Python, with tabs for System operations, Sales, Marketing, and All system, all fed from existing artifacts under repo root.
- **Mac integration:** PhoenixControl launches this dashboard (with repo path) and opens http://localhost:8501 in the browser (or later in a WKWebView).
- **Stack:** Streamlit + Plotly + Pandas; optional GitHub API for CI/workflows; no DB.
- **Operator-completeness (5 + 2):** (1) Completeness Board with locale/lang/persona/topic/catalog % and red/yellow/green thresholds; (2) Approval Blockers with formal states and hard stop rules (Pearl/church/governance evidence); (3) Governance Blockers Panel showing and running DOCS link integrity, Gate 16/16b, Gate 17, freebies index health, and next fix command; (4) Action Mapping with exact next command, owner, due/SLA, and evidence path for every failed status; (5) Acceptance Matrix proving “UI shows what is missing, why it blocks, and how to fix”; (6) Weekly Loop Automation Contract (what runs weekly, auto-PRs allowed, merge rules); (7) Decision Log (immutable log of blocker transitions: detected → assigned → fixed → verified, with commit/PR/evidence links).
- **Autonomous loop UI (7):** Loop Status panel; Agent Queue view; PR Automation panel; KPI Trigger board; Weekly Orchestrator run page; Operations Board tab; Manual override controls. **Minimal set (6):** Loop Health card, Operations Board table with filters, Promotion Queue panel, Autonomy toggle state, Artifact freshness, Run-now actions — enough for UI to operate the loop safely.
- **App distribution:** PhoenixControl is a proper .app bundle, installable to Applications, and appears in Finder and the Dock like other Mac apps.
- **Safety Kill Switch visibility:** Top-level “Autonomy OFF/ON” state with immutable audit log (who changed it, when, why); visible in UI; no autonomous activity when OFF.
- **100% handoff-ready:** Three explicit sections close operator goals: (1) **Blockers & Completeness Contracts** — exact formulas/thresholds for locale/lang/persona/topic/catalog completion; approval blocker states and hard release-stop rules. (2) **Autonomous Loop Operations UI** — dedicated views (loop health, agent queue, promotion queue, KPI triggers, decision log); explicit mapping from failure → next command/owner/SLA/evidence. (3) **Acceptance Matrix** — testable DoD: UI always answers what is broken, why it blocks, what to do next, whether fix worked.
- **Handoff:** The 6 acceptance bullets (§ Acceptance criteria), the test checklist (including minimal UI, autonomous loop UI, autonomous loop dashboard minimal set, app distribution, Safety Kill Switch), the 5 operator-completeness requirements plus 2 final items (§ Operator completeness), the 7 autonomous loop UI items (§ Autonomous loop UI), and the 3 sections above (Blockers & Completeness Contracts, Autonomous Loop Operations UI, Acceptance Matrix) make this the **full operator-grade spec**. With these 3 sections, the spec is **100% handoff-ready**.
