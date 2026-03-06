# Control Plane Spec Patch v1.1

**Purpose:** Add explicit requirements for completeness management, approval state, and auto-agent learning visibility so the control plane app is **implementation-ready** for real operator goals.  
**Authority:** Extends the existing control plane design spec (plan + [CONTROL_PLANE_GO_NO_GO.md](./CONTROL_PLANE_GO_NO_GO.md)).  
**Status:** Spec only — not 100% ready to code until this patch is integrated and data sources/contracts are verified.

**Required companion docs (must exist and be linked):**

- [CONTROL_PLANE_GO_NO_GO.md](./CONTROL_PLANE_GO_NO_GO.md) — Pass/fail per tab; production-ready when all pass and evidenced.
- [CONTROL_PLANE_RUNBOOK.md](./CONTROL_PLANE_RUNBOOK.md) — Runbook proving each tab runs real commands/artifacts; evidence per tab.
- [PRODUCTION_100_PLAN.md](./PRODUCTION_100_PLAN.md) — Production 100% handoff; blockers; freeze policy.
- [RELEASE_POLICY.md](./RELEASE_POLICY.md) — Freeze policy: release/* only, tagged vX.Y.Z to ship.
- [PHOENIX_OMEGA_ERROR_STATE_UX_SPEC.md](./PHOENIX_OMEGA_ERROR_STATE_UX_SPEC.md) — Error state UX: taxonomy, surfaces, per-tab patterns, SwiftUI component contracts, copy rules, recovery actions, startup health check.

---

## 1. Completeness Engine (required)

### 1.1 Data source

- **Canonical script:** [scripts/book_script_content_validation.py](../scripts/book_script_content_validation.py).
- **Invocation:** `python scripts/book_script_content_validation.py [--locale LOC] [--teacher ID] [--plan PATH] [--json]`.
- **Role:** First-class data source for content/completeness; not optional.

### 1.2 Canonical completeness scorecard

Define **one** canonical completeness scorecard with:

- **Global %** — overall pass rate across all dimensions.
- **By locale** — pass % and gap count per locale.
- **By language** — pass % and gap count per language.
- **By persona** — pass % and gap count per persona.
- **By topic** — pass % and gap count per topic.
- **By engine** — pass % and gap count per engine.
- **By teacher** — pass % and gap count per teacher.

Each slice: **pass/fail** + **gap counts** + **drill-down path** (e.g. click locale → see personas/topics under that locale).

### 1.3 UI requirement

- New **Completeness** tab (or dedicated section in Dashboard).
- Show scorecard; support drill-down by locale, language, persona, topic, engine, teacher.
- Display pass/fail and gap counts; link or button to run validation for a selected slice.

### 1.4 Data contract (Completeness tab)

| Item | Value |
|------|--------|
| **Command** | `scripts/book_script_content_validation.py --json` (and optional `--locale`, `--teacher`, `--plan`) |
| **Artifact path** | Stdout (JSON) or optional `--out` file if added to script |
| **Refresh cadence** | On tab open / manual Refresh; optional scheduled run artifact |
| **Failure behavior** | Show last known scorecard + error message; red banner; do not clear previous data |

### 1.5 Completeness data contract (all KPIs) — canonical schema

Implement one canonical scorecard. All KPIs below must be represented; UI shows pass/fail + gap counts + drill-down path for each.

| KPI | Key / slice | Fields required | Drill-down path |
|-----|-------------|------------------|------------------|
| **Global %** | `global_pct`, `global_pass`, `global_fail`, `global_gap_count` | overall pass rate (0–100), pass/fail count, total gaps | — |
| **By locale** | `by_locale[]` | `locale_id`, `pass_pct`, `pass`, `fail`, `gap_count`, `drill_down_id` | → by_language, by_persona for this locale |
| **By language** | `by_language[]` | `language_id`, `pass_pct`, `pass`, `fail`, `gap_count`, `drill_down_id` | → by_locale, by_persona for this language |
| **By persona** | `by_persona[]` | `persona_id`, `pass_pct`, `pass`, `fail`, `gap_count`, `drill_down_id` | → by_topic, by_engine for this persona |
| **By topic** | `by_topic[]` | `topic_id`, `pass_pct`, `pass`, `fail`, `gap_count`, `drill_down_id` | → by_persona, by_engine for this topic |
| **By engine** | `by_engine[]` | `engine_id`, `pass_pct`, `pass`, `fail`, `gap_count`, `drill_down_id` | → by_persona, by_topic for this engine |
| **By teacher** | `by_teacher[]` | `teacher_id`, `pass_pct`, `pass`, `fail`, `gap_count`, `drill_down_id` | → doctrine coverage, approved_atoms for this teacher |

- **Pass/fail:** per slice, derived from validation (e.g. all required content present = pass).
- **Gap count:** number of missing or failing items in that slice.
- **drill_down_id:** optional identifier to load next level (e.g. locale_id for by_locale so UI can request by_locale?locale=xy).

If the script does not yet output this exact shape, extend `book_script_content_validation.py` to emit it (e.g. `--json` with this schema) or add a thin adapter in the app that maps script output to this contract.

---

## 2. Approval & Compliance State (required)

### 2.1 Model

- **Required approvals** model: each approval has an **id**, **name**, **source-of-truth file or checklist**, **status**.
- **Status enum:** `missing` | `present` | `approved` | `expired`.
- Example: Pearl News church docs — approved/not approved; required sign-off checklist.

### 2.2 Source-of-truth for approval state

- Define **exact** source-of-truth files or checklist docs for each required approval (e.g. `pearl_news/governance/`, GO/NO-GO checklist signed section).
- Define how status is derived: file exists, file content hash, date, or explicit approval record (e.g. in a YAML/JSON or checklist).

### 2.3 Blocking rules

- If any required approval is not `approved`:
  - Show **red blocker** in UI (Dashboard and/or dedicated Approval view).
  - **Disable launch actions** (e.g. “Run pipeline to production”, “Post to WP”) until blocker cleared.
- Optional: allow override with reason (audit log).

### 2.4 UI requirement

- **Approvals** tab or section: list required approvals, status, source file/link, last updated.
- Dashboard: at least one summary (e.g. “Approvals: 2/3 approved”) and link to Approvals tab; if any not approved, show blocker and disable launch actions.

### 2.5 Data contract (Approvals tab)

| Item | Value |
|------|--------|
| **Command** | None (read-only) or script that aggregates approval state from SOT files |
| **Artifact path** | See approval-state contract below |
| **Refresh cadence** | On tab open / manual Refresh |
| **Failure behavior** | Show “Unknown” for failed reads; treat as blocking (red) until resolved |

### 2.6 Approval-state contract (church docs approved/missing)

Exact source-of-truth and status derivation for required approvals. Example: Pearl News church docs.

| Approval id | Name | Source-of-truth (file or checklist) | How status is derived | Blocking if not `approved` |
|-------------|------|-------------------------------------|------------------------|-----------------------------|
| `pearl_news_church_docs` | Pearl News church / governance docs | `pearl_news/governance/` dir + signed row in `docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md` (or equivalent) | Dir present + required files exist + checklist row signed with date | Yes: disable Pearl News launch/post |
| (add others) | e.g. Brand/church compliance | e.g. `docs/church_docs/`, church YAML per brand | File exists; optional: approval date in checklist | Yes per domain |

**Status enum:** `missing` | `present` | `approved` | `expired`.

- **missing:** SOT file or checklist row absent.
- **present:** File(s) exist but no explicit approval (e.g. unsigned checklist).
- **approved:** Checklist signed with name/date or approval record present; not past expiry if applicable.
- **expired:** Approval date older than policy (e.g. 12 months); re-approval required.

**Church docs (Pearl News) — exact SOT:**

- `pearl_news/governance/GOVERNANCE_PAGE.md`
- `pearl_news/governance/EDITORIAL_STANDARDS.md`
- `pearl_news/governance/CORRECTIONS_POLICY.md`
- `pearl_news/governance/CONFLICT_OF_INTEREST_POLICY.md`
- `docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md` — signed section (e.g. “Church docs reviewed and approved by [name], [date]”).

If any required approval is not `approved`, show red blocker and disable launch actions (e.g. “Post to WP”, “Run production pipeline”) until resolved.

---

## 3. Metadata Inventory View (required)

### 3.1 Purpose

- Show **BookSpec/CompiledBook** fields.
- Which are **present** in latest plans.
- Which are **not rendered** into script text (metadata-only).

### 3.2 Data source

- [scripts/book_script_content_validation.py](../scripts/book_script_content_validation.py) with `--plan <path>`.
- Script documents **SYSTEM_METADATA_NOT_IN_SCRIPT** and system content; use `--json` output for structured inventory.

### 3.3 UI requirement

- **System Metadata** tab:
  - Table or list: field name, present in latest plans (Y/N or count), rendered into script (Y/N).
  - Use validation script output; allow selecting a plan file for `--plan`.
  - Show which fields are metadata-only (not in script) per spec.

### 3.4 Data contract (System Metadata tab)

| Item | Value |
|------|--------|
| **Command** | `scripts/book_script_content_validation.py --plan <path> --json` |
| **Artifact path** | Stdout JSON or script’s optional output file |
| **JSON schema** | Fields from script’s SYSTEM_METADATA_NOT_IN_SCRIPT and plan schema; document keys for “present in plan”, “in script” |
| **Refresh cadence** | On plan select / manual Refresh |
| **Failure behavior** | Show error; retain last successful inventory if any |

---

## 4. Agent Learning & Auto-Enhancement View (required)

### 4.1 Purpose

- Visibility into **recent GitHub agent PRs**, what changed (files/config), **test impact** before/after, **learned signals/recommendations**.

### 4.2 Data sources (to be defined explicitly)

- **Workflow artifacts:** e.g. from runs that produce “agent impact” or “learning” reports.
- **PR metadata:** GitHub API — PRs labeled or from certain authors/bots; changed files, config paths.
- **EI reports:** Enlightened Intelligence or evaluator reports (artifacts path and schema).

Define for implementation:

- Exact workflow(s) that produce agent/learning artifacts.
- PR filter (label, author, branch).
- EI report path and schema (e.g. `artifacts/ei_v2/` or similar).

### 4.3 UI requirement

- **Agents & Learning** tab:
  - Recent agent PRs (title, link, changed files/config).
  - Test impact before/after (e.g. pass rate or test list).
  - Learned signals / recommendations (list or table).
  - Data from workflow artifacts + PR metadata + EI reports per data contract.

### 4.4 Data contract (Agents & Learning tab)

| Item | Value |
|------|--------|
| **Command** | GitHub API (PRs, files); optional local script that aggregates EI/learning artifacts |
| **Artifact path** | TBD: e.g. `artifacts/ei_v2/eval_*.json`, `artifacts/learning/recommendations.json`; PR data via API |
| **JSON schema** | TBD: PR list schema; learning report schema; EI report schema |
| **Refresh cadence** | On tab open / manual Refresh; API rate-limit aware |
| **Failure behavior** | Offline/rate-limit message; show last cached data |

---

## 5. Pearl News Operations Board (required)

### 5.1 Purpose

- **Single board** for Pearl News ops: GO/NO-GO checklist status, required docs/approvals, secrets readiness, scheduled workflow health, rollback proof status.
- **Hard blockers** at top.

### 5.2 Content

- GO/NO-GO checklist status (from [PEARL_NEWS_GO_NO_GO_CHECKLIST.md](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md) or equivalent).
- Required docs/approvals (link to Approval model).
- Secrets readiness (e.g. WP creds in Keychain; no plaintext).
- Scheduled workflow health (last run of pearl_news_scheduled or similar).
- Rollback proof status (evidence file or checklist row).
- **Hard blockers** section at top: any item that blocks launch (red).

### 5.3 UI requirement

- **Pearl News Board** tab (or replace/enhance existing Pearl News tab):
  - Top: Hard blockers list.
  - Then: GO/NO-GO rows, required approvals, secrets status, workflow health, rollback proof.
  - Actions: link to run pipeline, view drafts, open checklist doc.

### 5.4 Data contract (Pearl News Board tab)

| Item | Value |
|------|--------|
| **Command** | Read checklist doc; optional script that returns structured status; workflow status via GitHub API |
| **Artifact path** | `docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md`, `artifacts/pearl_news/evaluation/networked_run_evidence.json`, workflow run status |
| **Schema** | Checklist rows; approval status; secrets (boolean readiness); workflow last run; rollback proof present (boolean) |
| **Refresh cadence** | On tab open / manual Refresh |
| **Failure behavior** | Show “Unknown” for failed reads; treat as blocker until resolved |

---

## 6. Explicit Data Contracts (required)

### 6.1 Rule

- **For every tab:** document **command**, **artifact path**, **JSON schema** (or “none” if N/A), **refresh cadence**, **failure behavior**.
- Without this, implementation will drift.

### 6.2 Format per tab

- **Tab name**
- **Command:** exact CLI or API.
- **Artifact path:** file(s) or API endpoint(s).
- **JSON schema:** path to schema doc or key fields.
- **Refresh cadence:** on open / manual / scheduled (interval).
- **Failure behavior:** what the UI shows and does when the command or read fails.

### 6.3 Existing tabs

- Apply this to all current tabs (Dashboard, Pipeline, Simulation, Tests, Observability, Gates & Release, Pearl News, Teacher, CI, Docs) and to every new tab from this patch (Completeness, Approvals, System Metadata, Agents & Learning, Pearl News Board).
- Maintain a single **Data Contracts** section or doc that lists every tab and its contract.

---

## 7. Operator UX: “What’s Missing” / Missing/Blocked Queue (required)

### 7.1 Purpose

- Global **Missing/Blocked** queue so operators see everything that blocks or is missing in one place.

### 7.2 Fields per item

- **Severity** (e.g. blocker / warning / info).
- **Owner** (team or person).
- **Source file** (or artifact).
- **Fix command/button** (e.g. “Run validation”, “Open doc”, “Set secret”).
- **Due date / status** (optional).

### 7.3 Data source

- Aggregate from: completeness gaps, approval blockers, failed checks, missing evidence, missing secrets, failed workflows.
- Define one canonical list (e.g. generated by a script or assembled from each tab’s “blockers” and “gaps”).

### 7.4 UI requirement

- **Missing/Blocked** queue view (sidebar widget, Dashboard section, or dedicated tab):
  - List of items with severity, owner, source file, fix command/button, due/status.
  - Sort by severity; filter by owner/source.
  - Click fix: run command or open file/link.

### 7.5 Data contract (Missing/Blocked queue)

| Item | Value |
|------|--------|
| **Command** | Script or in-app aggregation that produces queue from completeness, approvals, checks, evidence, secrets, workflows |
| **Artifact path** | Output of aggregation script or in-memory from other tabs’ state |
| **Schema** | `{ severity, owner, source_file, fix_command_or_button, due_date, status }[]` |
| **Refresh cadence** | On Dashboard open / manual Refresh; after any tab refresh that affects blockers |
| **Failure behavior** | Show partial list; errors in aggregation shown as queue items (severity: warning) |

---

## High-end control-plane UX (enhancements)

Current spec has basics (cards, badges, shortcuts). The following upgrades make the app a **high-end control-plane UX** while staying **native SwiftUI** (no HTML).

### 8.1 Visual hierarchy

- **Big “Mission Control” header** with **global health ring** (single at-a-glance indicator: green / yellow / red).
- **Color-coded system map** by subsystem: each major area (Observability, Completeness, Approvals, Pearl News, CI, etc.) shows green/yellow/red; click to drill into that subsystem.

### 8.2 Animated status transitions

- **Smooth state changes** for pass → fail → blocked (e.g. crossfade or short transition, not instant flip).
- **Pulse animation** for active jobs (e.g. running script, collecting signals).
- **Subtle shake** for failed blockers so they attract attention without being noisy.

### 8.3 Timeline + playback

- **“What changed” timeline** with run diffs (e.g. last N runs with timestamp; what passed/failed vs previous).
- **Click any point** to view **system state snapshot** at that time (evidence log tail, snapshot, blocker list as of then).
- Data: from evidence log, snapshot history, or run-history artifact; store minimal snapshots for replay.

### 8.4 Rich drilldowns

- **Expandable cards** with inline logs, artifacts, and **fix actions**.
- **One-click actions:** “Open file”, “Open workflow run”, “Run check”, “Copy log”.
- Every major card (run result, blocker, approval, workflow) supports expand → see detail + actions.

### 8.5 Completeness heatmaps

- **Persona × topic** heatmap: grid; cell color = pass/fail/gap; missing cells **glow red** with **direct remediation command** (e.g. “Add atoms”, “Run validation for this slice”).
- **Locale × language** heatmap (same idea).
- **Teacher × doctrine coverage** heatmap.
- Tapping a red cell shows what’s missing and a button to run the fix or open the right doc/script.

### 8.6 Image support

- **Thumbnail previews** for cover assets / freebies (where artifact paths point to images).
- **Evidence screenshots panel:** e.g. branch protection screenshot, rollback proof screenshot; store paths or embed in evidence bundle; show in a dedicated “Evidence” or “Screenshots” area (Dashboard or Docs tab).
- Native SwiftUI image loading; support common formats (PNG, JPG, WebP if needed).

### 8.7 Operator cockpit mode

- **Full-screen monitor layout** for live operations: maximize use of space; minimal chrome; key metrics large.
- **Persistent top alerts + blocker queue** always visible (e.g. top bar or sidebar that stays on screen).
- Optional: separate “Cockpit” window or tab that is optimized for a dedicated ops display.

### 8.8 Micro-interactions

- **Hover previews** (macOS: hover over run, blocker, or card → tooltip or popover with summary).
- **Keyboard command palette** (e.g. Cmd+K): quick jump to tab, run “Collect signals”, “Refresh all”, open doc.
- **Quick filters** (e.g. filter evidence log by status, filter blockers by severity) with keyboard-friendly toggles.
- **“Explain this failure”** contextual assistant panel: for a selected failure/blocker, show a short explanation (from rule or template) and suggested fix; optional future: link to runbook or AI-generated summary.

---

## Acceptance Criteria (summary)

1. **Completeness:** Scorecard (global, by locale/language/persona/topic/engine/teacher) with pass/fail, gap counts, drill-down; data from `book_script_content_validation.py`; data contract documented.
2. **Approvals:** Required approvals model and SOT; status missing/present/approved/expired; red blocker and disabled launch actions when not approved; data contract documented.
3. **System Metadata:** Tab shows BookSpec/CompiledBook fields, present-in-plan, rendered-in-script; uses validation script `--plan`; data contract documented.
4. **Agents & Learning:** Tab shows recent agent PRs, changes, test impact, learned signals; data sources (workflow artifacts, PR metadata, EI reports) defined and contract documented.
5. **Pearl News Board:** Single board with GO/NO-GO, approvals, secrets readiness, workflow health, rollback proof; hard blockers at top; data contract documented.
6. **Data contracts:** Every tab has command, artifact path, schema, refresh cadence, failure behavior in one place.
7. **Missing/Blocked queue:** Global queue with severity, owner, source file, fix command/button, due/status; aggregated from completeness, approvals, checks, evidence, secrets, workflows; data contract documented.

8. **High-end UX (enhancements):** Where feasible within native SwiftUI: (1) Mission Control header + global health ring + color-coded system map; (2) animated status transitions (smooth pass/fail, pulse for active jobs, subtle shake for blockers); (3) timeline + playback for “what changed” and state snapshots; (4) expandable cards with inline logs/artifacts and one-click fix actions; (5) completeness heatmaps (persona×topic, locale×language, teacher×doctrine) with red glow and remediation; (6) image support (thumbnails for covers/freebies, evidence screenshots panel); (7) operator cockpit mode (full-screen layout, persistent alerts/blocker queue); (8) micro-interactions (hover previews, command palette Cmd+K, quick filters, “Explain this failure” panel).

---

## Tab summary after patch

| Tab | Purpose |
|-----|--------|
| Dashboard | Status, observability phase, evidence tail, approvals summary, **Missing/Blocked** summary, branch protection. |
| Completeness | **NEW.** Scorecard by locale/language/persona/topic/engine/teacher; pass/fail; gap counts; drill-down. |
| Approvals | **NEW.** Required approvals list; status; blocker; disable launch if not approved. |
| System Metadata | **NEW.** BookSpec/CompiledBook fields; present in plan; rendered in script; validation script `--plan`. |
| Agents & Learning | **NEW.** Agent PRs; changes; test impact; learned signals; EI/workflow/PR data. |
| Pearl News Board | **NEW or replace.** GO/NO-GO, approvals, secrets, workflow health, rollback; blockers at top. |
| Pipeline | (existing) |
| Simulation | (existing) |
| Tests | (existing) |
| Observability | (existing) |
| Gates & Release | (existing) |
| Pearl News | (existing; may merge into Board) |
| Teacher | (existing) |
| CI / Workflows | (existing) |
| Docs & Config | (existing) |
| **Missing/Blocked** | **NEW (or Dashboard section).** Global queue; severity, owner, source, fix, due/status. |

---

## Acceptance tests per tab (missing/blocked detection)

Each tab must be testable for “something is missing or blocked” so the operator can act. Below: minimal acceptance test for missing/blocked detection per tab.

| Tab | Acceptance test (missing/blocked) | Pass criteria |
|-----|-----------------------------------|---------------|
| **Dashboard** | When any subsystem is red or any approval is not approved, Dashboard shows a blocker or red indicator; Missing/Blocked summary shows at least one item when a blocker exists. | Blocker visible; count or list updates when state changes. |
| **Completeness** | When validation reports gaps (gap_count > 0 for any slice), those slices show as fail or red; drill-down reveals missing items; remediation command/button available. | Gaps visible; drill-down and fix action available. |
| **Approvals** | When status is not `approved` for any required approval, tab shows red blocker and lists which approval is missing/expired; launch actions disabled. | Blocker and list correct; launch disabled. |
| **System Metadata** | When a plan is selected and a field is missing or not rendered, table shows N or “not in script”; no silent omission. | Missing/metadata-only fields visible. |
| **Agents & Learning** | When there are no PRs or reports, show “No data” or empty state; when there are failures in reports, show as blocked or failed. | Empty vs present; failures visible. |
| **Pearl News Board** | When GO/NO-GO checklist has an unchecked row or approval missing or secrets not ready or workflow failed, hard blockers at top show those items; launch disabled. | Blockers at top; launch disabled when blocked. |
| **Missing/Blocked queue** | When completeness has gaps, or approvals not approved, or a check failed, or evidence missing, queue lists at least one item with severity, owner, source, fix action. | Queue reflects all blocker sources; fix action present. |
| **Observability** | When collector run fails or elevated_failures has rows, UI shows fail count and elevated table; no silent success. | Failures and elevated visible. |
| **CI / Workflows** | When a workflow run failed, show failed status and link to run; when rate-limited or offline, show message. | Failed run and offline/rate-limit visible. |
| **Pipeline / Simulation / Tests / Gates / Teacher / Docs** | When run fails, log shows error and exit code; global error alert or inline error shown; not silent. | Failure visible; no silent fail. |

Implement automated or manual tests that assert: for a given “missing” or “blocked” state, the tab shows the expected indicator and (where applicable) the Missing/Blocked queue includes the item.

---

## Next steps

1. Confirm data contracts with actual script outputs and artifact paths (e.g. run `book_script_content_validation.py --json` and document schema).
2. Define approval SOT files and status derivation for Pearl News (and any other domains).
3. Define agent/learning artifact paths and EI report schema.
4. Implement tabs and data contracts in order; add each tab’s contract to the single Data Contracts doc/section.
5. Wire Missing/Blocked queue to completeness, approvals, and other blocker sources.
6. Implement acceptance tests per tab for missing/blocked detection (table above).
7. Implement high-end UX enhancements in phases: (a) visual hierarchy + health ring + system map, (b) animated transitions + pulse/shake, (c) timeline + playback, (d) drilldowns + one-click actions, (e) heatmaps + images + cockpit mode + micro-interactions.
