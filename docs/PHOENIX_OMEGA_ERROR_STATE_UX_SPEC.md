# Phoenix Omega — Error State UX Dev Outline

**Purpose:** Complete contract for error states in the control plane (PhoenixControl) so every error has a home, severity, copy rules, and recovery action before implementation.  
**Authority:** This doc. Audience: builders (SwiftUI), operators (runbook), PM (acceptance).  
**Related:** [CONTROL_PLANE_SPEC_PATCH_V1.1.md](./CONTROL_PLANE_SPEC_PATCH_V1.1.md), [EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md](./EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md).

---

## 1. Error State Taxonomy

Four severity tiers, each with distinct visual treatment and behavior:

| Tier | Visual | Behavior | Examples |
|------|--------|----------|----------|
| **Critical** | Red | Blocks all action; app cannot function without resolution | Repo path not found, Python not installed, ScriptRunner crash |
| **Warning** | Orange | Degraded functionality; app works partially | GitHub token missing, artifacts directory empty, JSONL malformed |
| **Info** | Blue | Contextual awareness; no action required | P4 observability not yet implemented, collector never run, no elevated failures found |
| **Empty** | Gray | Zero data state; neutral, non-alarming | evidence_log.jsonl has no rows yet, no workflows found, simulation not yet run |

---

## 2. Error Surfaces (Where They Appear)

| Surface | Location | Use |
|---------|----------|-----|
| **Inline** | Within a tab's content area | Replaces normal content when data unavailable. Full-width banner or centered card. Always has a primary action button. |
| **Toast / transient** | Bottom of window | Non-blocking errors that resolve themselves or need a quick nudge. Auto-dismiss after 5s for info; persist for critical. Max 2 stacked. |
| **Status badge** | Sidebar or tab header | Small dot or icon for tab-level health. Red dot = something broken in this tab. Click navigates to error detail. |
| **Toolbar strip** | Below main toolbar | Persistent narrow bar for app-wide issues (e.g. repo path invalid). Dismisses only when resolved, not by user click. |

---

## 3. Error Patterns Per Tab

### Dashboard

| Condition | Severity | Surface | Copy / action |
|-----------|----------|---------|----------------|
| Repo path not set | Critical | Full-screen onboarding | CTA: Open Settings |
| Snapshot missing | Info | Inline | "Run collect_signals to populate" + Run button |
| Elevated failures > 0 | Warning | Card highlighted red | Count + link to Observability tab |

### Pipeline / Simulation / Tests / Gates

| Condition | Severity | Surface | Copy / action |
|-----------|----------|---------|----------------|
| Python not found | Critical | Inline | Path diagnostic + "Check Environment" link |
| Script not found at expected path | Critical | Inline | Show expected path + "Verify Repo" CTA |
| Script running | — | Disabled Run, cancel affordance | Live log streaming |
| Script exited non-zero | Critical | Log header + status badge | Exit code in log header; red badge; log preserved |

### Observability

| Condition | Severity | Surface | Copy / action |
|-----------|----------|---------|----------------|
| evidence_log.jsonl missing | Info | Inline | "Run collector to generate logs" |
| elevated_failures.jsonl empty | Empty (green) | Inline | "No elevated failures — system healthy" |
| JSONL parse error on a line | Warning | Banner | "N lines skipped — malformed JSON" with line numbers |
| P4 not implemented | Info | Card | "Learn/Enhance phase is planned, not yet active" — non-alarming, no CTA |

### CI / Workflows

| Condition | Severity | Surface | Copy / action |
|-----------|----------|---------|----------------|
| No GitHub token | Warning | Inline | List what's unavailable + "Add Token" CTA to Settings |
| API rate limited | Warning | Inline | Retry countdown timer; show cached last-known data |
| Network unavailable | Info | Inline | "Showing cached data from [timestamp]" — no hard error |

### Pearl News / Teacher

| Condition | Severity | Surface | Copy / action |
|-----------|----------|---------|----------------|
| WP credentials missing | Warning | Inline | Never expose in log output |
| Dry-run mode active | Info | Persistent strip | "Dry-run — no posts will be published" (blue) |

---

## 4. SwiftUI Implementation Patterns

| Component | Responsibility |
|-----------|-----------------|
| **ErrorStateView** | Reusable view: `severity`, `title`, `message`, `suggestion`, optional `primaryAction`, optional `secondaryAction`. Covers all four tiers with consistent layout. |
| **LiveLogView error integration** | Exit code ≥ 1 → colored header bar above log: "Exited with code N". Log text preserved and scrollable. Copy-to-clipboard always available on error. |
| **StatusBadge** | SF Symbol + color. Maps: `checkmark.circle.fill` green, `exclamationmark.triangle.fill` orange/red, `minus.circle` gray, `info.circle` blue. Used in sidebar row and tab headers. |
| **ToastManager** | `@EnvironmentObject` singleton. `post(message:severity:duration:)`. Max 2 concurrent. Z-index above content, bottom-anchored, 16px margin. |
| **ToolbarErrorStrip** | Conditional view in toolbar area. When `appState.repoPathValid == false`. Fixed height 36px, full width; dismisses only on resolution. |

---

## 5. Error Message Copy Rules

Every error has **three text fields** — no exceptions:

| Field | Rule | Example |
|-------|------|--------|
| **Title** | What happened, past tense, noun-first | "Repo path not found." not "Error: cannot open path." |
| **Message** | One sentence of context: what the system tried and what it got | "The app tried to read artifacts from the configured path but the directory does not exist." |
| **Suggestion** | One actionable sentence starting with a verb | "Open Settings and verify the repo root path." Never "Please try again." |

**Secrets rule:** Never interpolate token values, passwords, or credential paths into any error message or log output. Replace with `[REDACTED]`.

---

## 6. Error Recovery Actions (Standard Set)

Only these CTA labels — no freeform copy:

| Label | Use |
|-------|-----|
| **Open Settings** | Repo path, token, credentials |
| **Run Collector** | Triggers collect_signals.py |
| **Verify Environment** | Opens diagnostic sheet |
| **Retry** | Re-runs last script |
| **Cancel** | Aborts running script |
| **Open in GitHub** | Workflow or issue URL |
| **View Log** | Scrolls to or focuses LiveLogView |
| **Dismiss** | Info/warning only; never for critical |

---

## 7. Startup Health Check (App Launch)

On every launch, **before any tab renders**, validate in sequence:

| Step | Check | On failure |
|------|--------|------------|
| 1 | Repo path set and directory exists | Block UI; ErrorStateView critical; CTA Open Settings |
| 2 | `scripts/` subdirectory present | Block UI; ErrorStateView critical; CTA Open Settings |
| 3 | `artifacts/observability/` present or creatable | Block UI; ErrorStateView critical; CTA Open Settings |
| 4 | Python 3 resolvable on PATH | Block UI; ErrorStateView critical; CTA Open Settings |
| 5 | GitHub token present in Keychain | Non-blocking warning strip only |

**Rule:** Steps 1–4 must pass before tabs are enabled. Step 5 failure shows warning strip only. Any failure in 1–4 → block UI, show ErrorStateView critical with Open Settings CTA.

---

## 8. Out of Scope for MVP Error Handling

- No crash reporter UI (log to file; handle in future release)
- No retry queue for failed scripts (manual retry only)
- No diff/comparison of error states across runs
- No user-defined error suppression rules

---

## 9. Acceptance

- [ ] Every error condition in §3 has a matching ErrorStateView or surface.
- [ ] All error copy follows §5 (title, message, suggestion).
- [ ] All CTAs use only the standard set in §6.
- [ ] Startup health check (§7) runs before tabs; 1–4 block, 5 warns.
- [ ] LiveLogView shows exit code and preserves log on script failure.
- [ ] No secrets in any error message or log output.
