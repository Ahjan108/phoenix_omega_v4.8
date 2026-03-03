# Production Observability, Learning & Self-Healing System

**Purpose:** Spec for a system that observes production live (100% repo), documents success, elevates and auto-fixes failures with retest, and learns/enhances over time.  
**Authority:** Extends [RIGOROUS_SYSTEM_TEST.md](RIGOROUS_SYSTEM_TEST.md) and [V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md). Aligns with [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md).  
**Last updated:** 2026-03-04

---

## 1. Overview

A **Production Observability, Learning & Enhancement System** (POLES) does four things:

| Function | When | Action |
|----------|------|--------|
| **Observe** | Always | Monitor all production signals (CI, gates, smoke, releases) across 100% of the repo |
| **Document** | When things work | Capture evidence, update runbooks, record baselines |
| **Elevate & fix** | When things fail | Alert, attempt auto-fix, retest, escalate if unrecoverable |
| **Learn & enhance** | Continuously | Store patterns, improve fix strategies, refine thresholds |

This spec defines architecture, data model, and implementation phases.

---

## 2. Observability Layer (100% repo coverage)

### 2.1 Production signals to observe

All signals that indicate production health. Each has a **signal_id**, **category**, and **evidence path**.

| Signal | Source | Category | Evidence |
|--------|--------|----------|----------|
| `ci_teacher_gates` | `.github/workflows/teacher-gates.yml` | teacher_mode | Workflow run URL, exit code |
| `ci_brand_guards` | `.github/workflows/brand-guards.yml` | brand | Workflow run URL, exit code |
| `ci_pearl_news_gates` | `.github/workflows/pearl_news_gates.yml` | pearl_news | Workflow run URL, exit code |
| `ci_docs` | `.github/workflows/docs-ci.yml` | docs | Workflow run URL, link integrity |
| `gate_production_readiness` | `scripts/run_production_readiness_gates.py` | core | 17 conditions, pass/fail per gate |
| `systems_test` | `scripts/systems_test/run_systems_test.py` | core | Phases 1–7, suggested_fix per failure |
| `atoms_coverage` | `tests/test_atoms_coverage_100_percent.py` | coverage | 450/450 pass |
| `simulation_10k` | `simulation/run_simulation.py --n 10000` | simulation | Pass rate, artifact path |
| `pearl_news_networked` | `scripts/pearl_news_networked_run_and_evidence.sh` | pearl_news | `networked_run_evidence.json` |
| `pipeline_canary` | `scripts/run_pipeline.py` (worst/best combos) | pipeline | CompiledBook, plan_hash |
| `release_smoke` | Release path smoke + rollback proof | release | Runbook evidence |

### 2.2 Signal registry

A single config file defines all production signals:

```yaml
# config/observability_production_signals.yaml (to create)
signals:
  - id: ci_teacher_gates
    category: teacher_mode
    source: workflow
    workflow: teacher-gates.yml
    evidence_path: null  # GitHub Actions URL
  - id: gate_production_readiness
    category: core
    source: script
    script: scripts/run_production_readiness_gates.py
    evidence_path: artifacts/observability/gates_{timestamp}.json
  # ... etc
```

### 2.3 Observer runner

A script that **collects** all signals (or runs them):

- **Passive:** Read GitHub Actions API, workflow run status, artifact links
- **Active:** Run local scripts (gates, systems test, simulation) and capture output

Output: `artifacts/observability/signal_snapshot_{timestamp}.json`

---

## 3. Documentation Layer (when things work)

### 3.1 Success → evidence capture

When a signal passes:

1. **Capture evidence** — Timestamp, signal_id, artifact path, run URL
2. **Append to evidence log** — `artifacts/observability/evidence_log.jsonl` (append-only)
3. **Update runbook** — If a runbook exists for this signal, append "Last verified: {timestamp}"
4. **Baseline update** — For simulation/analyzer: pass rate, dimension baselines → `artifacts/observability/baselines.json`

### 3.2 Auto-documentation rules

| Rule | Trigger | Action |
|------|---------|--------|
| All gates pass | `run_production_readiness_gates.py` exit 0 | Append to evidence_log; update `docs/PLANNING_STATUS.md` "Last production gates: {date}" if present |
| Systems test pass | `run_systems_test.py --all` exit 0 | Append to evidence_log; link report in `artifacts/systems_test/` |
| Pearl News networked run | `pearl_news_networked_run_and_evidence.sh` | Write `networked_run_evidence.json`; link in GO/NO-GO checklist |
| CI green on main | Workflow success | Record in evidence_log; optional: update DOCS_INDEX "Last CI green" |

### 3.3 Evidence schema

```json
{
  "timestamp": "2026-03-04T12:00:00Z",
  "signal_id": "gate_production_readiness",
  "status": "pass",
  "artifact_path": "artifacts/observability/gates_20260304T120000.json",
  "run_url": null,
  "summary": "17/17 gates passed"
}
```

---

## 4. Elevation & Auto-Fix Layer (when things fail)

### 4.1 Failure flow

```
Failure detected → Classify → Attempt auto-fix (if available) → Retest → Escalate if still failing
```

### 4.2 Failure classification

| Category | Examples | Auto-fix available? |
|----------|----------|----------------------|
| `config_missing` | Missing YAML, wrong path | No (human must create) |
| `config_schema` | Invalid YAML, schema violation | Yes (syntax fixes) or No (semantic) |
| `content_gap` | Missing STORY band, atom pool empty | No (content authoring) |
| `dependency` | Missing pip package | Yes (`pip install X`) |
| `pipeline_runtime` | Resolver error, plan failure | Sometimes (depends on error) |
| `test_assertion` | Unit test fail | No (code fix) |

### 4.3 Auto-fix strategies

| Strategy | When | Action |
|----------|------|--------|
| `suggested_fix` | Systems test provides `suggested_fix` | Log it; optionally run if it's a single command (e.g. `pip install`) |
| `reinstall_deps` | Import/dependency errors | `pip install -r requirements.txt` (or equivalent) |
| `retry` | Transient (network, timeout) | Retry up to N times |
| `escalate` | No auto-fix available | Create issue, notify, or write to `artifacts/observability/elevated_failures.jsonl` |

### 4.4 Elevation output

When a failure cannot be auto-fixed:

- **File:** `artifacts/observability/elevated_failures.jsonl`
- **Fields:** timestamp, signal_id, category, message, suggested_fix, artifact_path, run_url
- **Optional:** GitHub Action to create issue from elevated failures; Slack/email webhook

### 4.5 Retest loop

After auto-fix attempt:

1. Re-run the same signal/script
2. If pass → document success (evidence layer)
3. If fail → escalate (elevation output)
4. Max retries: 1 (avoid infinite loops)

---

## 5. Learning & Enhancement Layer

### 5.1 Learning store

Persist patterns over time:

- **Failure history** — `artifacts/observability/failure_history.jsonl` (signal_id, category, timestamp, fix_attempted, outcome)
- **Fix effectiveness** — Which suggested_fix values led to pass on retry
- **Baseline trends** — Pass rate over time

### 5.2 Enhancement rules

| Rule | Input | Output |
|------|-------|--------|
| **Recurring failure** | Same signal_id fails 3+ times in 7 days | Suggest adding to CI or pre-merge gate |
| **Fix effectiveness** | `pip install X` → pass | Add X to requirements.txt or CI setup |
| **New baseline** | Simulation pass rate improves | Update baseline; alert if regression |
| **Doc drift** | Evidence path points to missing file | Suggest doc update |

### 5.3 Enhancement output

- **Weekly report** — `artifacts/observability/weekly_report_{date}.md`: signals passed/failed, new failures, fix attempts, recommendations
- **Baseline file** — `artifacts/observability/baselines.json`: current pass rates, thresholds

---

## 6. Implementation Phases

### Phase 1: Observe only (MVP)

- Create `config/observability_production_signals.yaml` with signal registry
- Create `scripts/observability/collect_signals.py` — runs local scripts (gates, systems test), reads workflow status if available
- Output: `artifacts/observability/signal_snapshot_{timestamp}.json`
- No auto-fix, no learning yet

### Phase 2: Document success

- Add evidence capture: on pass, append to `evidence_log.jsonl`
- Add optional runbook update: "Last verified" timestamps
- Wire into CI: `collect_signals.py` runs on schedule or post-merge

### Phase 3: Elevate & auto-fix

- Add failure classification from `suggested_fix` (systems test)
- Add auto-fix attempt for dependency errors (`pip install`)
- Add retest loop
- Add `elevated_failures.jsonl` for unrecoverable failures

### Phase 4: Learn & enhance

- Add failure_history, fix effectiveness tracking
- Add weekly report generation
- Add baseline trend tracking

---

## 7. Artifacts & Config

| Item | Location | Purpose |
|------|----------|---------|
| Signal registry | `config/observability_production_signals.yaml` | Define all production signals |
| Signal collector | `scripts/observability/collect_signals.py` | Run/collect signals |
| Auto-fix runner | `scripts/observability/attempt_auto_fix.py` | Apply fix strategies, retest |
| Signal snapshot | `artifacts/observability/signal_snapshot_{ts}.json` | Current state |
| Evidence log | `artifacts/observability/evidence_log.jsonl` | Success history |
| Elevated failures | `artifacts/observability/elevated_failures.jsonl` | Unrecoverable failures |
| Failure history | `artifacts/observability/failure_history.jsonl` | Learning store |
| Baselines | `artifacts/observability/baselines.json` | Pass rates, thresholds |
| Weekly report | `artifacts/observability/weekly_report_{date}.md` | Enhancement summary |

---

## 8. CI Integration

- **Schedule:** Run `collect_signals.py` on cron (e.g. daily) or on push to main
- **Workflow:** `.github/workflows/production-observability.yml` — collect signals, optionally attempt auto-fix, upload artifacts
- **Branch protection:** Observability does not block merge; it informs. Optional: block if critical signals fail and no evidence in 7 days

---

## 9. Governance

- **Authority:** This spec extends [RIGOROUS_SYSTEM_TEST.md](RIGOROUS_SYSTEM_TEST.md) and [V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md).
- **Reference:** [SYSTEM_OWNER_VISION.md](../SYSTEM_OWNER_VISION.md) §6 Hard NOs — no silent fallback; observability surfaces failures.
- **Index:** Add to [docs/DOCS_INDEX.md](DOCS_INDEX.md) under Core system docs or Production observability section.

---

## 10. Summary

| Layer | Function | Key deliverable |
|-------|----------|-----------------|
| **Observe** | 100% repo coverage | Signal registry, collector, snapshot |
| **Document** | When things work | Evidence log, runbook updates |
| **Elevate & fix** | When things fail | Auto-fix attempt, retest, elevated_failures |
| **Learn & enhance** | Continuously | Failure history, weekly report, baseline trends |

**Next step:** Implement Phase 1 (signal registry + collector script).
