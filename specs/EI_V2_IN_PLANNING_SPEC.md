# EI v2 In Planning: Full Operating Outline

**Status:** Canonical  
**Subordinate to:** [TEACHER_PORTFOLIO_PLANNING_SPEC.md](./TEACHER_PORTFOLIO_PLANNING_SPEC.md), [TEACHER_UNIVERSAL_AND_SCORING_SPEC.md](./TEACHER_UNIVERSAL_AND_SCORING_SPEC.md)  
**Audience:** Planning, EI v2, control plane / human-in-loop UI.

EI v2 participates in **planning** as an **advisory layer only**. The deterministic planner remains source of truth; EI v2 scores, ranks, and recommends. Humans approve; optional auto-apply is gated by trust thresholds.

---

## 1. Decision Architecture (who decides what)

### 1.1 Deterministic planner (source of truth)
- **Inputs:** `brand_teacher_matrix`, `teacher_constraints`, diversity guards, release scheduler.
- **Output:** Valid weekly candidate set: (teacher, topic, persona, brand, program, worldview, series).
- **Guarantees:** Policy compliance, caps, feasibility. No policy override by EI.

### 1.2 EI v2 advisory layer (optimizer)
- **Inputs:** Deterministic candidates + historical outcomes + content quality signals.
- **Output:** Scores, ranked recommendations, warnings, suggested reallocations.
- **Guarantees:** No policy override; recommendations only.

### 1.3 Human-in-loop control
- Approves, edits, or rejects EI recommendations.
- Final publish plan is human-approved.

### 1.4 Optional auto-apply
- Enabled only after trust criteria are met.
- Applies limited classes of EI recommendations automatically (see §7).

---

## 2. Pipeline Stages (weekly)

1. **Generate valid baseline plan** — Planner creates week plan with all hard constraints satisfied.
2. **Run EI planning advisory** — Score each tuple (brand, teacher, topic, persona, program, series slot).
3. **Produce recommendation set** — Boost/cut suggestions, series continuation priorities, risk flags.
4. **UI review** — Show baseline vs EI-adjusted proposal, confidence, expected impact, policy safety checks.
5. **Approval and lock** — Human signs off; plan is frozen for assembly/export.
6. **Post-week learning** — Ingest outcomes, update EI models/thresholds, recompute trust metrics.

---

## 3. Deterministic Planner Responsibilities (hard rules)

### 3.1 Allocation
- Teacher–brand eligibility.
- Topic/persona compatibility.
- Program/worldview assignment.

### 3.2 Constraint enforcement
- Teacher caps (topic/persona/month/90-day).
- Diversity caps (topic/persona/teacher/worldview share).
- Release topology caps (day/brand/sync limits).

### 3.3 Feasibility and fail-fast
- Unsatisfiable plans fail clearly with actionable errors.

### 3.4 Output contract
- Emits stable IDs/keys used by EI: `program_id`, `worldview_id`, `series_id`, `concept_id`.

---

## 4. EI v2 Advisory Responsibilities

### 4.1 Tuple scoring
- Score expected quality/performance risk per planned tuple.
- Dimensions: quality confidence, duplication risk, metadata risk, likely engagement.

### 4.2 Boost/Cut recommendations
- Suggest increase/decrease by:
  - `program_id`
  - `teacher_id`
  - `topic_id`
  - `persona_id`
- Include expected effect and confidence.

### 4.3 Series recommendations
- Prioritize continuation vs new starts.
- Recommend “complete cluster first” where read-through potential is higher.

### 4.4 Warning generation for UI
- High similarity risk.
- Weak differentiation across programs.
- Over-concentration risk despite being technically valid.
- Expected low-performance slots.

### 4.5 Reorder semantics (priority vs selection)
- **Reorder-only** changes **execution priority**: the order in which allocations are passed to BookSpec/compile is EI-ranked. When every allocation in the wave is built (no capacity limit), reorder affects only sequence, not which books exist.
- **Selection/composition** is affected only when a **cutoff** exists: e.g. `max_books` per wave, resource cap, or wave size. Then position determines who is built vs deferred; allocations below the cutoff are effectively deferred (not built this wave).
- **Below-cutoff deferral** is an EI influence on catalog composition. It must be constrained by policy: e.g. cap the fraction of the wave that EI can “move” below cutoff, or require human approval when deferral rate exceeds a threshold. Planner remains source of truth for eligibility; EI only reorders within the valid set.

---

## 5. Recommendation Types (bounded actions)

### 5.1 Safe advisory-only
- Ranking order changes.
- Suggested substitutions within allowed policy envelope.
- Suggested hold/rework flags.

### 5.2 Never allowed for EI
- Breaking hard caps/policy.
- Assigning disallowed teacher–brand combos.
- Overriding compliance constraints directly.

### 5.3 Auto-apply eligible (later)
- Low-risk reorder/rank changes.
- Series continuation priority changes within same cap envelope.

---

## 6. UI Contract (human-in-loop)

### 6.1 Views
- Baseline plan vs EI-adjusted proposal.
- Per-brand and per-program summary.
- Risk heatmap and confidence bands.

### 6.2 Per-recommendation fields
- `reason`, `score_delta`, `confidence`, `expected_kpi_effect`, `policy_check_status`.

### 6.3 Actions
- Approve all, approve selective, reject, request re-run with stricter settings.

### 6.4 Audit trail
- Record who approved what and why.

---

## 7. Trust Threshold for Auto-Apply

### 7.0 Baseline for trust metrics
- The first **min_observation_weeks** (configurable in `trust_thresholds`) with EI advisory enabled but auto-apply disabled form the **baseline cohort**.
- Outcomes in that period are treated as baseline; `quality_lift_vs_baseline` is the delta between post-baseline outcome quality and baseline cohort quality (same metric, comparable tuples).
- Baseline is defined by week order (first N distinct weeks chronologically). Lift is computed only against this cohort so the reference point is explicit and testable.

### 7.1 Prerequisites
- Minimum observation window (e.g., several weeks).
- Stable low flag/rejection rates.
- Positive quality/performance lift vs baseline.

### 7.2 Guardrails
- Auto-apply only to pre-approved recommendation classes.
- Max percent of week plan touched automatically.
- Immediate rollback on degraded metrics.

### 7.3 Kill switch
- One toggle to return to advisory-only mode instantly (config: `auto_apply_enabled: false`).

---

## 8. Metrics to Monitor

### 8.1 Planning quality
- Constraint violations (should be zero).
- Feasibility failure rate.
- Human override rate on EI recommendations.

### 8.2 Content/store outcomes
- Flag/rejection/takedown/refund rates.
- Read-through/completion.
- Conversion and downstream series uptake.

### 8.3 EI quality
- Recommendation acceptance rate.
- Lift vs baseline.
- Confidence calibration accuracy.

---

## 9. Data Feedback Loop

1. Collect weekly outcomes by tuple dimensions.
2. Aggregate by program/teacher/topic/persona/series.
3. Update EI advisory model/weights.
4. Do not auto-write deterministic config by default.
5. Present config-change suggestions for human review.

---

## 10. Rollout Plan

| Phase | Mode | Description |
|-------|------|-------------|
| **1** | Advisory-only | EI scores + UI warnings; no auto changes. |
| **2** | Assisted planning | Human approves EI reorder/boost/cut suggestions. |
| **3** | Limited auto-apply | Only for low-risk classes under trust threshold controls. |
| **4** | Broader optimization | Expand auto-apply scope if metrics remain healthy. |

---

## 11. Practical Principle

- **Planner** = safety + compliance + deterministic feasibility.
- **EI v2** = intelligence + ranking + optimization.
- **Human** = accountability + final authority.

Scale and adaptability without losing operational control.

---

## 12. Input schema (stub-to-real handoff)

When replacing stub scoring with real EI models, the advisory consumes the following inputs. Contract: `config/quality/ei_v2_planning_advisory.yaml` (`required_signal_fields`, `missing_signal_policy`).

### 12.1 `historical_outcomes[]`

Keyed by `(brand_id, teacher_id, topic_id, persona_id, program_id, series_id, week)`. Each record may include:

| Field | Type | Description |
|-------|------|-------------|
| `sales` | number | Sales or conversion for that tuple/week. |
| `read_through` | number | Read-through rate (0–1 or ratio). |
| `completion` | number | Completion rate (0–1). |
| `refund_rate` | number | Refund rate (0–1). |
| `flag_rate` | number | Content-flag rate (0–1). |
| `rejection_rate` | number | Rejection/takedown rate (0–1). |

Missing keys for a given tuple/week are treated per `missing_signal_policy` in config.

**Cold-start fallback:** When there is no outcome for the full 7-tuple, scoring uses a deterministic fallback chain (configurable): full tuple → `(program_id, teacher_id)` → `program_id` → `brand_id` → global prior. Weights/priors for each level are in config so cold-start behavior is testable. Early weeks with sparse data thus produce stable, predictable scores instead of near-identical composites.

### 12.2 `content_quality_signals[]`

Aggregated EI metrics per book (or per tuple). Structure is implementation-defined; required fields are listed in config under `required_signal_fields`. Used for quality_confidence and related dimensions. Missing or partial signals are handled per `missing_signal_policy` (e.g. `warn`, `degrade_only`, `skip_scoring`).

---

## Implementation references

- **Planner output:** `phoenix_v4/planning/teacher_portfolio_planner.py` — `TeacherAllocation`, `allocate_wave()`.
- **EI planning advisory:** `phoenix_v4/planning/ei_planning_advisory.py` — `run_ei_planning_advisory()`, report schema.
- **Config:** `config/quality/ei_v2_planning_advisory.yaml` — trust thresholds, auto_apply, kill switch; §12 handoff: `required_signal_fields`, `missing_signal_policy`; adapter paths: `historical_outcomes_path`, `content_quality_signals_path`.
- **Report schema:** `schemas/ei_v2_planning_advisory_report_v1.schema.json`.
- **Outcome ingestion:** `phoenix_v4/planning/outcome_ingestion.py` — `load_historical_outcomes_from_file()`, strict validation, canonical key.
- **Content quality signals:** `phoenix_v4/planning/content_quality_signals.py` — `load_content_quality_signals_from_file()`, strict validation.
- **Trust gating:** `phoenix_v4/planning/trust_metrics.py` — `compute_trust_metrics()`, `is_trust_eligible()`; used when `auto_apply_enabled` to gate reorder.
- **Canonical tuple key:** `phoenix_v4/planning/ei_planning_contracts.py` — `planning_tuple_key()`, identity + dedup everywhere.
- **Catalog integration:** `scripts/generate_full_catalog.py` — loads outcomes/signals, runs advisory, reorders allocations by EI rank when eligible; writes baseline snapshot to `artifacts/ei_v2/planning_baseline_snapshot.json` for lift measurement.
- **Section 6 (learned params):** Usefulness of learned_params depends on EI V2 hybrid/shadow producing real signals. Implementation is in place; outputs are **non-decisive** until hybrid shadow is live. See Workstream 3 dependency.
