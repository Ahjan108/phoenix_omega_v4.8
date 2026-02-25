# Phase 13-C — Deterministic Constraint Solver Wave Optimizer (DWO-CS)

**Purpose:** Single canonical system document for the fully deterministic wave optimizer. Produces a wave that *provably* satisfies hard constraints (or fails with actionable infeasibility reasons) and optimizes a clear objective under soft constraints. No randomness; no ML.

**Audience:** Ops, release, engineers.  
**Authority:** This doc is the system reference; config and CLI are the contract.  
**Last updated:** 2026-02-25

---

## 1. Core contract

### Inputs

- **Candidate items** — Compiled plan candidates (or tuple candidates) for a target wave (week). Supplied as JSON: `candidates` or `items` list.
- **Ops signals** (loaded from `--ops-dir` when present):
  - Coverage Health (v1.1) — risk used for eligibility.
  - Catalog Emotional Distribution (Phase 9) — referenced for objective design.
  - Cross-Brand Divergence (Phase 10) — convergent brand pairs → no arc overlap in same wave.
  - Brand Identity Stability (Phase 11) — drift-critical brands → cap on “new” arc_id/slot_sig.
  - Release-wave caps / clustering rules (Phase 6 parity) — weekly_caps in config.
- **Target wave size** `N` (books to release).
- **Config** — `config/wave_optimizer_constraint_solver.yaml` (or `--config` path).

### Output

- **Solved:** Selected set of `N` items plus proof artifacts: constraint satisfaction note, objective score behavior, determinism note.
- **Infeasible:** Minimal infeasibility explanation + blocking constraints + recommended ops actions.

### Determinism guarantee

Given identical inputs and config:

- Identical selection.
- Identical tie-break (via `candidate_sort_key`).
- Identical reports.

---

## 2. Files and CLI

| Item | Location |
|------|----------|
| **Module** | `phoenix_v4/ops/wave_optimizer_constraint_solver.py` |
| **Config** | `config/wave_optimizer_constraint_solver.yaml` |
| **Tests** | `tests/test_wave_optimizer_constraint_solver.py` |

### CLI

```bash
PYTHONPATH=. python3 phoenix_v4/ops/wave_optimizer_constraint_solver.py \
  --wave-id 2026-W10 \
  --target-size 90 \
  --candidates-json artifacts/ops/wave_candidates_2026-W10.json \
  --ops-dir artifacts/ops \
  --config config/wave_optimizer_constraint_solver.yaml \
  --out-dir artifacts/ops/wave_optimizer
```

### Outputs

| Outcome | Artifacts |
|--------|-----------|
| **SOLVED** | `artifacts/ops/wave_optimizer/wave_optimizer_solution_{wave_id}.json`, `wave_optimizer_solution_{wave_id}.md` |
| **INFEASIBLE** | `artifacts/ops/wave_optimizer/wave_optimizer_infeasible_{wave_id}.json` only |

### Exit codes

- **0** — SOLVED  
- **1** — INFEASIBLE (hard constraints cannot be satisfied)  
- **2** — SOLVED_WITH_WARN (reserved; when warn-level constraints are allowed)

---

## 3. Candidate item schema

Each candidate corresponds to a book plan or tuple planned for release. Minimal required fields:

| Field | Type | Description |
|-------|------|-------------|
| `candidate_id` | string | Unique id (required). |
| `candidate_sort_key` | string | Deterministic stable ordering; default `candidate_id` or precomputed stable hash. |
| `tuple_id` | string | e.g. `persona\|topic\|E1\|F006`. |
| `brand_id` | string | Brand. |
| `persona_id` | string | Persona. |
| `topic_id` | string | Topic. |
| `engine_id` | string | Engine. |
| `arc_id` | string | Arc. |
| `slot_sig` | string | Slot signature. |
| `band_sig` | string | Band signature (e.g. `3-3-4-4-2-4`). |
| `variation_signature` | string | Variation id. |
| `teacher_mode` | bool | Teacher-mode book. |
| `teacher_id` | string or null | Teacher id when teacher_mode. |
| `risk` | string | From coverage health: `GREEN`, `YELLOW`, `RED`, `BLOCKER`. |
| `volatility` | float | Optional; derived from band_sig if missing. |
| `age_days` | int | Optional; for freshness objective. |
| `is_new_arc` | bool | Optional; when true and brand is drift-critical, counts toward new-arc cap. |

**Wave fingerprint** (computed if missing): `arc_id|slot_sig|band_sig|variation_signature`. Used for `max_same_wave_fingerprint_per_week` cap.

JSON may be a list or an object with `candidates` or `items` key.

---

## 4. Hard constraints (must satisfy)

Enforced as hard constraints in the solver.

### 4.1 Release-wave caps (Phase 6 parity)

From `hard_constraints.weekly_caps`:

- `max_same_topic`, `max_same_persona`, `max_same_topic_persona_pair`
- `max_same_arc_id`, `max_same_engine_id`, `max_same_band_sig`, `max_same_slot_sig`, `max_same_variation_signature`
- `max_same_wave_fingerprint` (arc|slot|band|var)
- `max_teacher_mode_books`, `max_same_teacher_id`

### 4.2 Eligibility

- Exclude candidates with `risk` in `exclude_risks` (default `BLOCKER`, `RED`).
- If `allow_yellow` is false, exclude `YELLOW`.
- Candidates without `candidate_id` are dropped.

### 4.3 Cross-brand separation (Phase 10)

When CBDI indicates convergence between brand A and B (from `cross_brand_divergence_{report_date}.json` alerts `BRAND_CONVERGENCE_LOW` / `BRAND_CONVERGENCE_CRITICAL`):

- Hard constraint: the same `arc_id` must not appear in both brand A and brand B in the selected wave (no arc overlap for that convergent pair).

### 4.4 Brand identity stability (Phase 11)

When a brand is drift-critical (from `brand_identity_stability_{report_date}.json` alert `BRAND_IDENTITY_DRIFT_CRITICAL`):

- Hard constraint: cap “new” arc_ids for that brand: at most `max_new_arcs_per_brand_when_critical` selected items with `is_new_arc` true for that brand.

---

## 5. Soft constraints (objective)

The solver maximizes a deterministic score while satisfying all hard constraints.

- **Diversity:** Prefer first use of topic, persona, arc, band (reward for first selected in that category).
- **Volatility:** Prefer higher volatility (bucketed by `volatility_bins.low` / `high`).
- **Freshness:** Prefer smaller `age_days` (e.g. ≤ 14).
- **Risk:** Penalize `YELLOW` risk (optional penalty weight).

Weights are in `objective.weights`: `topic_diversity`, `persona_diversity`, `arc_diversity`, `band_diversity`, `volatility_preference`, `freshness_preference`, `yellow_risk_penalty`.

**Tie-break:** Deterministic via `candidate_sort_key` (lexicographic); same inputs → same selection.

---

## 6. Solver implementation

- **Implementation:** Deterministic greedy solver: sort eligible by `candidate_sort_key`; repeatedly choose a candidate that (1) does not violate any cap, (2) does not add same-arc overlap for a convergent brand pair, (3) does not exceed new-arc cap for drift-critical brands; score by diversity/volatility/freshness/risk; tie-break by smaller sort key. If no valid candidate before reaching N, return INFEASIBLE with blocking reason.
- **Determinism:** Single-threaded; no random seed needed; candidate order and tie-break are fixed by config and input data.

---

## 7. Infeasibility diagnostics

When status is INFEASIBLE, the output includes:

- **blocking_reasons:** List of objects with at least:
  - `code`: e.g. `INSUFFICIENT_ELIGIBLE_CANDIDATES`, `NO_VALID_CANDIDATE_AT_STEP`
  - For INSUFFICIENT_ELIGIBLE_CANDIDATES: `eligible_count`, `needed`, `exclusion_breakdown` (e.g. risk_red_blocker, risk_yellow).
  - For NO_VALID_CANDIDATE_AT_STEP: `selected_so_far`, `needed`, `note`.
- **recommended_ops_actions:** Fixed list of remediation steps (e.g. increase candidate pool diversity or reduce target_size; do not reopen content unless coverage deficits exist).

Diagnostics are deterministic from counts and constraints, not heuristic.

---

## 8. Config reference

`config/wave_optimizer_constraint_solver.yaml`:

- **wave_optimizer.target_size_default** — Default N when `--target-size` not given.
- **wave_optimizer.eligibility** — `exclude_risks`, `allow_yellow`.
- **wave_optimizer.hard_constraints.weekly_caps** — All Phase 6 parity caps.
- **wave_optimizer.hard_constraints.cross_brand** — `enforce_no_arc_overlap_when_convergent`, thresholds (convergent_warn_threshold, convergent_fail_threshold).
- **wave_optimizer.hard_constraints.brand_identity** — `max_new_arcs_per_brand_when_critical`, drift_critical_threshold.
- **wave_optimizer.objective.weights** — Diversity, volatility, freshness, yellow_risk_penalty.
- **wave_optimizer.objective.volatility_bins** — `low`, `high` for bucketing.
- **wave_optimizer.determinism** — `tie_breaker` (candidate_sort_key), `epsilon_weight` (reserved).

---

## 9. Integration — wave build pipeline order

1. **Generate candidate set** — Produce e.g. `artifacts/ops/wave_candidates_{wave_id}.json` (list of candidates with required fields).
2. **Run DWO-CS** — `wave_optimizer_constraint_solver.py` with `--wave-id`, `--target-size`, `--candidates-json`, `--ops-dir`, `--config`, `--out-dir`.
3. **Run Phase 6** — `check_release_wave.py` on the selected plans as final verification.
4. **Export wave** — Proceed to export only if Phase 6 passes.

Phase 6 remains the final gate; DWO-CS constraints mirror it for selection so that the chosen wave is designed to pass.

---

## 10. Ops playbook (deterministic)

If the solver returns INFEASIBLE, ops should **only**:

1. Reduce `target_size` **or** expand the candidate pool (upstream selection step).
2. Relax **one** cap family in config (e.g. topic cap first, then arc cap) if policy allows.
3. Re-run the solver.
4. Reopen content **only** if coverage deficits exist (explicit gate codes); otherwise treat as a scheduling pool issue.

No ad hoc changes.

---

## 11. Tests

`tests/test_wave_optimizer_constraint_solver.py`:

| Test | Description |
|------|-------------|
| `test_solves_wave_with_caps_satisfied` | Diverse candidates, target 10, caps that allow it → SOLVED, 10 selected. |
| `test_determinism_same_inputs_twice` | Same candidates and config → same selected candidate_ids. |
| `test_infeasible_insufficient_eligible` | Fewer eligible than target → INFEASIBLE, code INSUFFICIENT_ELIGIBLE_CANDIDATES. |
| `test_infeasible_eligible_but_caps_impossible` | All same topic, tight topic cap → INFEASIBLE. |
| `test_cross_brand_convergent_no_arc_overlap` | Convergent pair (A,B); selection must not include same arc_id in both A and B. |
| `test_drift_critical_brand_new_arc_cap` | Drift-critical brand; at most max_new_arcs_per_brand_when_critical with is_new_arc true. |
| `test_run_produces_solution_or_infeasible` | `run()` with temp candidates file and ops_dir → status SOLVED or INFEASIBLE; wave_id and target_size set. |

---

## 12. JSON Schemas and blocking codes (enterprise determinism)

- **Wave candidates:** `schemas/wave_candidates.schema.json` — Contract for `wave_candidates_*.json` (schema_version, wave_id pattern `YYYY-Www`, generated_at_utc, candidates[] with required fields and risk enum).
- **Solution:** `schemas/wave_optimizer_solution.schema.json` — Contract for `wave_optimizer_solution_*.json` (status SOLVED | SOLVED_WITH_WARN, selected_count, selected / selected_candidates).
- **Infeasible:** `schemas/wave_optimizer_infeasible.schema.json` — Contract for `wave_optimizer_infeasible_*.json` (status INFEASIBLE, blocking_reasons[] with required `code`).
- **Canonical blocking codes:** `config/wave_optimizer_blocking_codes.yaml` — Enumerated codes (e.g. INSUFFICIENT_ELIGIBLE_CANDIDATES, CROSS_BRAND_ARC_CONFLICT, BRAND_NEW_ARC_CAP_EXCEEDED) and Slack/Jira routing. Machine-parseable; no free-text ambiguity.
- **Registry:** `config/ops_schema_registry.yaml` — Ops artifact types, schema paths, artifact patterns. Used by CI validators.

**CI validation:** Run `python scripts/ci/validate_ops_artifacts.py` (requires `jsonschema`; see `requirements.txt`). Fails build if any ops JSON does not match its schema. Run `python scripts/ci/validate_ops_registry_consistency.py` to ensure registry and schema files are in sync.

---

## 13. Related docs

- **phoenix_v4/ops/README.md** — Ops tooling index; Phase 13-C CLI and pipeline summary.
- **docs/SYSTEMS_V4.md** — Canonical systems overview; §6 Phase 13-C and wave build order; §9 config table; §11 doc map.
- **docs/SCHEMA_CHANGELOG.md** — Schema version history and migration notes.
- **Phase 6** — `check_release_wave.py`, `config/release_wave_controls.yaml` (final verification gate).
- **Phase 10** — CBDI (`cross_brand_divergence_*.json`) for convergent pairs.
- **Phase 11** — BISI (`brand_identity_stability_*.json`) for drift-critical brands.
