# Change observation, impact, and “running best” system

**Purpose:** Spec for a system that observes when assets are added, changed, or dropped; computes impact across the repo; triggers synergy recommendations when new systems or components appear (e.g. LLM-assisted “how do old and new marketing work together?”); and keeps the system running at its best.  
**Authority:** Complements [PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md](./PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md) (POLES) and [EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md](./EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md) (Agent change feed). Indexed in [DOCS_INDEX.md](./DOCS_INDEX.md) § Change observation and impact.  
**Last updated:** 2026-03-05

---

## 1. Goals

| Goal | Description |
|------|--------------|
| **Observe** | Detect when something is added, changed, or dropped; know what happened. |
| **Impact** | Know how each change affects other systems, downstream gates, and related domains. |
| **Synergy (Goal 1)** | When new stuff is added (e.g. new marketing system), have the system (e.g. GitHub/LLM) consider how it can work best with existing pieces in the same domain (e.g. old marketing). |
| **Running best (Goal 2)** | Ensure the system is running at its best (health, gates, impact-driven recommendations). |

---

## 2. Current state and gap

- **DOCS_INDEX** has “document all” subsections per domain (Marketing, Pearl News, Observability, etc.) but is human-oriented; no machine-readable “system X has these paths.”
- **POLES** observes signals (gates, CI, scripts), documents success, elevates failures. No “inventory diff” or “system impact” from file/add/change/drop.
- **Executive Dashboard** Agent change feed shows “what changed, why, impact, rollback link” from GitHub API + workflow artifacts; impact today is not derived from a system registry or change-events pipeline.
- **Structural drift** ([scripts/obs/build_structural_drift_dashboard.py](../scripts/obs/build_structural_drift_dashboard.py)) focuses on plan/wave metrics, not file-level add/change/drop.
- **Gap:** No machine-readable system/domain registry, no change-event pipeline (add/change/drop → system scope → impact → synergy trigger).

---

## 3. Architecture

1. **System registry** — Machine-readable list of systems (id, assets, related_systems, downstream). Used to scope changes and compute impact and synergy.
2. **Change observation** — Git-based (or optional inventory) diff → change events (kind: added/changed/dropped, path, system_ids).
3. **Impact analysis** — From change events: affected systems, downstream signals/workflows, related systems for synergy.
4. **Agent change feed** — Extended to consume impact summary and optional synergy artifact link.
5. **Synergy** — When “added” events touch a system with related_systems, run LLM (e.g. in GitHub Action) to produce “how can these work best together?”; post as PR comment or write artifact and link from feed.
6. **Running best** — Per-system health view (optional), impact-driven “run these after this change” recommendations; optional periodic “running best” LLM step.

---

## 4. System/domain registry

- **Location:** `config/governance/system_registry.yaml` (or `config/observability/system_registry.yaml`).
- **Implementation note:** Current repo implementation uses `config/governance/system_registry.yaml`.
- **Contents:**
  - **Systems:** id, name, domain (aligned with DOCS_INDEX sections): e.g. `marketing`, `pearl_news`, `teacher_mode`, `observability`, `freebies`, `title_engine`, `ei_v2`, `ml_loop`.
  - **Per system:**
    - **assets:** path globs or explicit paths (docs, configs, scripts, workflows) that belong to this system.
    - **related_systems:** ids of systems to consider together for **synergy** (e.g. `marketing` ↔ `pearl_news`, `marketing` ↔ `title_engine`).
    - **downstream:** optional list of signals/workflows that should run when this system’s assets change.
- **Authority:** DOCS_INDEX remains the human doc authority; the registry is the machine view. Optional validator script can check registry paths exist and align with DOCS_INDEX domains.

---

## 5. Change observation (add / change / drop)

- **Inputs:** Git diff between two refs (e.g. `main` vs branch, or last N commits); optional diff of registered assets vs filesystem for “dropped.”
- **Output — change events** (e.g. `artifacts/observability/change_events.jsonl`):
  - **kind:** `added` | `changed` | `dropped`
  - **path**
  - **system_ids** (from registry)
  - **scope** (optional short label)
- **Script:** e.g. `scripts/observability/detect_changes.py` — accepts two git refs, loads registry, outputs change_events JSONL.
- **Trigger:** GitHub Action on push/PR; optional scheduled run comparing “last known good” ref.

---

## 6. Impact analysis

- **Input:** Change events (path, system_ids).
- **Logic:**
  - **Affected systems:** from event.
  - **Downstream:** from registry `downstream` for those systems (and optionally from `config/observability_production_signals.yaml` by category).
  - **Related systems:** from registry `related_systems` for each affected system (for synergy).
- **Output:** Impact summary `{ affected_systems, downstream_signals_workflows, related_systems }`; optionally `artifacts/observability/impact_*.json` or append to evidence log with `signal_id: change_impact`.
- **Consumer:** Agent change feed (Executive Dashboard / PhoenixControl) shows impact and “run these after this change.”

---

## 7. Synergy (Goal 1)

- **Trigger:** Change events include **added** paths belonging to a system that has **related_systems** (or a new system id in registry).
- **Mechanism:** GitHub Action (or scheduled job):
  1. Run change detection for PR or last merge.
  2. If any “added” events touch a system with `related_systems`, call LLM with prompt: added/changed assets + related system names + “How can these work best together? Consider data flow, shared config, gates, docs, handoffs. Output concise recommendations.”
  3. Post result as PR comment or write `artifacts/observability/synergy_recommendations_{timestamp}.md` and link from Agent change feed.
- **Alternative:** Cursor rule/skill using same prompt and registry for “when I add or change marketing assets, suggest integration with existing marketing systems.”

---

## 8. Running best (Goal 2)

- **Existing:** POLES + gates + Executive Dashboard blockers, freshness, one-click verify.
- **Extensions:**
  - **Per-system health (optional):** Group signals by system/category using registry; dashboard shows “Marketing: gates X, Y green; Pearl News: gate Z red.”
  - **Impact-driven recommendations:** When a change affects system S, impact summary lists “run these workflows/gates”; Agent change feed shows them so operator keeps system running best.
  - **Optional “running best” LLM:** Periodic or on-demand job: evidence_log + elevated_failures + change_events → “3–5 concrete actions to get the system running at its best” → artifact or dashboard.

---

## 9. Data contracts and artifacts

| Artifact | Description |
|----------|--------------|
| `config/governance/system_registry.yaml` | System registry (systems, assets, related_systems, downstream). |
| `artifacts/observability/change_events.jsonl` | Append-only change events (kind, path, system_ids, scope). |
| `artifacts/observability/impact_*.json` | Impact summary per run (or stanza in evidence log). |
| `artifacts/observability/synergy_recommendations_*.md` | Human-readable synergy recommendations when LLM runs (e.g. in CI). |

**Agent change feed:** Source = change_events + impact summary + optional synergy file; refresh on dashboard load or after change-detection run. Shows what changed, why, **impact** (affected systems, downstream to run), and rollback link.

---

## 10. Implementation order

1. Define and add `system_registry.yaml` (3–5 systems: marketing, pearl_news, observability, teacher_mode, freebies; assets from DOCS_INDEX; related_systems; optional downstream).
2. Implement `scripts/observability/detect_changes.py` (git diff + registry → change_events.jsonl).
3. Implement impact step (script or function: change_events → impact summary; optional evidence log or impact_*.json).
4. Integrate impact (and synergy link when present) into Agent change feed (dashboard/PhoenixControl).
5. Add synergy workflow (GitHub Action or script: on “added” + related_systems → LLM → comment or artifact + link).
6. Optional: per-system health view in dashboard using registry.
7. Document in DOCS_INDEX (this spec and § Change observation and impact).

---

## 11. Files to add or touch

| Item | Action |
|------|--------|
| `config/governance/system_registry.yaml` | Create — systems, assets, related_systems, downstream. |
| `scripts/observability/detect_changes.py` | Create — git diff + registry → change_events.jsonl. |
| `scripts/observability/impact_from_changes.py` | Create — change_events → impact summary. |
| `.github/workflows/change-impact.yml` | Add — run detect + impact on PR; optionally synergy LLM and comment. |
| Executive Dashboard / PhoenixControl | Extend — include impact + synergy link in Agent change feed. |
| [docs/DOCS_INDEX.md](./DOCS_INDEX.md) | Update — § Change observation and impact (document all). |
| [docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md](./PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md) | Update — reference system registry, change detection, impact, synergy. |
