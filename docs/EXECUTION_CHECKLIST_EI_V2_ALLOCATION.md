# Execution Checklist: EI v2 + Teacher Allocation Gaps

**Source plan:** EI v2 and allocation gaps (Workstream order 2 → 1 → 3).  
**Purpose:** Concrete execution checklist for the three workstreams plus explicit CI and hardening tasks.

---

## Pre-workstream / alongside Workstream 2

### CI fail-hard for angle/concept (production)

- [ ] **Production CI** runs catalog generation (or full-catalog checks) with strict overrides:
  - `fail_on_topic_angle_reuse=true`
  - `fail_on_concept_id_reuse=true`
  - `fail_on_similarity=true` (when `similarity_check_enabled`)
- [ ] **Local/dev:** Keep advisory defaults (false) in YAML.
- [ ] **Implementation:** Env flag or CI-only config fragment (e.g. `STRICT_ANGLE_CONCEPT=1`) that overrides the three keys when running on main/CI.

---

## Workstream 2: Harden release scheduler (do first)

**Goal:** Reassign-first, fail-hard-second. Enforce `brand_days` and `same_day_cross_brand_max`; feasibility precheck; fail only when no feasible assignment after reassignment.

- [ ] Load `config/release_velocity/release_scheduler.yaml` in `scripts/release/generate_weekly_schedule.py` (add `CONFIG_SCHEDULER`, reuse `_load_yaml`).
- [ ] **Feasibility precheck:** Before day assignment, verify `sum(day_capacity) >= brands_in_week` (e.g. `7 * same_day_cross_brand_max >= number of brands with books that week`). If infeasible, exit 1 with clear error.
- [ ] **brand_days:** For each candidate/book, resolve `brand_id` (and `program_id` if present). Assign release weekday only from that brand's `brand_days` (or `program_days[program_id]` when configured). If a brand has no `brand_days`, treat as "any day" or single default.
- [ ] **Reassignment logic:** When a weekday would exceed `same_day_cross_brand_max`, move overflow brands to their next available day in `brand_days`. Build with reassignment from the start.
- [ ] **Fail-hard only when impossible:** Exit 1 only when no feasible assignment exists after reassignment (e.g. too many brands for day capacity, or a brand has no allowed days).
- [ ] Add test or CI run: schedule respects `brand_days` and `same_day_cross_brand_max`; script fails when precheck or post-reassignment feasibility fails.
- [ ] Document in `docs/RELEASE_VELOCITY_AND_SCHEDULE.md`: scheduler enforces `release_scheduler.yaml` with reassign-first, fail-hard-second.

---

## Workstream 1: Expand editorial programs (do second)

**Goal:** Phase 1 done-state: 10 programs across top 5 output brands (2 each minimum). No duplicate `(brand_id, worldview_id, metadata_style_family)`.

- [ ] Add programs to `config/catalog_planning/editorial_programs.yaml`: **10 programs across top 5 output brands** (minimum 2 per brand).
- [ ] **Uniqueness:** No duplicate `(brand_id, worldview_id, metadata_style_family)`. Validate against angle_matrix_policy — two programs in same brand with same `worldview_id` = reject (cosmetic).
- [ ] Confirm `teacher_portfolio_planner.py` and `catalog_planner.py` / BookSpec include `program_id` and `worldview_id`.
- [ ] Document in `docs/CATALOG_ARCHITECTURE_AT_SCALE.md` or short note: top 5 brands, naming convention, no-duplicate-tuple rule.

---

## Workstream 3: Wire EI v2 hybrid selector (do third)

**Goal:** Shadow mode first; full override after measured uplift. Future-safe signature: `program_id`, `worldview_id` in `hybrid_select` now.

- [ ] Add optional kwargs to `hybrid_select(..., program_id=None, worldview_id=None)`. Pass through from pipeline immediately (even if unused).
- [ ] Implement real V2 path in `hybrid_selector.py`: call `run_ei_v2_analysis`, dimension_gates, learner; set `v2_chosen`, `final`, `override_applied`; log feedback.
- [ ] Add `--ei-hybrid-shadow` to `run_pipeline.py`: run full hybrid logic, never override selection (always emit V1); log what V2 would have chosen.
- [ ] Add `--ei-hybrid` (selection override) after shadow mode validated; require measured uplift before enabling globally.
- [ ] Extend tests for shadow (final always V1) and full hybrid (override when margin exceeded).
- [ ] Config: explicit hybrid / use_v2_for_selection toggle in `ei_v2_config.yaml`.

---

## Hardening backlog

### Per-author 90-day cap (≤50 titles/author/90 days per storefront)

- [ ] **Status check:** Verify whether enforced in code or only config/docs today.
- [ ] If advisory: implement enforcement gate. **Placement:** Prefer **allocation time** in `phoenix_v4/planning/teacher_portfolio_planner.py` (block the wave before books are planned) over `generate_weekly_schedule.py` (schedule time) to avoid wasted pipeline work.
- [ ] Emit blocking error when projected >50 titles/author/90 days per storefront account.

### EI v2 In Planning (advisory pipeline)

- [ ] **Spec:** [specs/EI_V2_IN_PLANNING_SPEC.md](../specs/EI_V2_IN_PLANNING_SPEC.md) — Planner = source of truth; EI = advisory only; human approves; optional auto-apply gated by trust.
- [ ] **Run advisory:** `scripts/generate_full_catalog.py ... --ei-planning-advisory` writes `artifacts/ei_v2/planning_advisory_report.json` (tuple scores, boost/cut recs, series recs, warnings).
- [ ] **Config:** [config/quality/ei_v2_planning_advisory.yaml](../config/quality/ei_v2_planning_advisory.yaml) — trust thresholds, `auto_apply_enabled: false` (kill switch), report path.

### Future workstream: video ↔ book mapping

- [ ] **Note:** Explicit `video_channel_id → editorial_program_id` (or equivalent) mapping config so video and book identity stay aligned. Placeholder for future workstream.

---

## Summary table (from plan)

| Area            | Next step                                                                 |
|-----------------|---------------------------------------------------------------------------|
| Angle/concept   | CI fail-hard (explicit task above)                                        |
| Editorial programs | 10 programs, top 5 brands, no-duplicate tuple (Workstream 1)          |
| Release topology| Reassign-first, fail-hard-second, feasibility precheck (Workstream 2)    |
| EI v2 hybrid    | `program_id`/`worldview_id` in signature; shadow then full (Workstream 3) |
| Per-author 90-day | Hardening backlog; enforce at allocation time if advisory              |
| Video ↔ book    | Future workstream: channel → program mapping config                       |
