# Production 100% Plan (Final, No Gaps)

**Purpose:** Single handoff to Dev/Ops. If every item below is green, you are truly production-ready for current scope.  
**Authority:** [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md), [DOCS_INDEX.md](./DOCS_INDEX.md).

---

## Production readiness blockers (current)

Until resolved, the repo is **not 100%** for ship:

| # | Blocker |
|---|---------|
| 1 | Uncommitted/untracked critical work (UI app, workflows, EI hybrid, locale assets). |
| 2 | Release governance: CHANGELOG and release checklists present and current. |
| 3 | EI V2 promotion not green (safety regressions, consecutive passes). |
| 4 | Branch protection documented; real GitHub enforcement must be verified; path-dependent workflows. |
| 5 | New workflows (e.g. locale-gate, translation matrix) tracked and required where applicable. |
| 6 | Control plane: committed, tested, signed/notarized, GO/NO-GO evidence per [CONTROL_PLANE_GO_NO_GO.md](./CONTROL_PLANE_GO_NO_GO.md). |

---

## Freeze policy (before shipping)

1. **`release/*` branch only** — No direct pushes to `main` for release.
2. **Required checks must pass on that branch** — Same required status checks as for `main`.
3. **Only tagged releases (`vX.Y.Z`) can ship** — No untagged commit is shipped.

See [RELEASE_POLICY.md](./RELEASE_POLICY.md).

---

## 1. Scope lock

- Ship scope: **en-US + hu-HU ebooks only.** zh-CN deferred. **V1 authoritative**; V2 hybrid override only.

## 2. Source-of-truth files to own

Production readiness gates, prepublish gates, EI V2 config and promotion criteria, check scripts, PEARL_NEWS_GO_NO_GO_CHECKLIST, BRANCH_PROTECTION_REQUIREMENTS, DOCS_INDEX (see [CONTROL_PLANE_SPEC_PATCH_V1.1.md](./CONTROL_PLANE_SPEC_PATCH_V1.1.md) and DOCS_INDEX for full list).

## 3. Quality system

Hard gates for uniqueness, engagement, somatic_precision; hybrid V1+V2 logic; log overrides; reject release if dimension gate fails.

## 4. V2 promotion policy

Catalog calibration first; 3 consecutive green promotion-gate runs; no safety regression; promote by scope (canary → hu-HU → broader).

## 5. CI / workflow baseline

Required on `main`: Core tests, release-gates, ei-v2-gates, docs-ci, brand-guards; pearl_news_gates if active. Scheduled: production-observability, EI nightly. Alerts: production-alerts.

## 6. Operational evidence

Green CI URLs, networked run evidence, scheduled proof, rollback drill proof, branch protection proof, signed checklist.

## 7. Release-week commands

Run production readiness gates, prepublish gates, EI rigorous eval, catalog calibration, promotion gate check (see DOCS_INDEX / scripts for exact commands).

## 8. hu-HU rules

Constrained routing; TTS path; locale/territory gate; no en-US persona mix in hu-HU output.

## 9. Docs governance

DOCS_INDEX link check; missing files as plain text + ⚠️; no stale refs; last-updated current; docs check in required checks when docs change.

## 10. Do not ship

Hard gate fail; safety regression; missing evidence; branch protection not enforced; rollback proof absent; freeze policy violated; uncommitted critical work.

## 11. Start-now sequence

First week-1 book with V1 + EI compare; trigger EI and observability workflows; record evidence; week-2 gated on new thresholds.

## 12. Definition of 100%

All required CI enforced and green; all release gates pass; hybrid/V2 enforced by code; evidence present and signed; rollback proven; scope constraints respected.

---

Control plane: [CONTROL_PLANE_GO_NO_GO.md](./CONTROL_PLANE_GO_NO_GO.md). Pilot then scale: 1-week internal pilot, on-call owner/SLA, then broad use.
