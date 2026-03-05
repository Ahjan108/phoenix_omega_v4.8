# Content coverage tooling — analysis (proper & complete)

**Purpose:** Confirm that existing checks answer “is any book prose/content missing?” and where the gaps are.

---

## 1. What exists and what it covers

| Tool | Scope | Proper? | Complete? | Notes |
|------|--------|--------|-----------|--------|
| **tests/test_atoms_coverage_100_percent.py** | Unified catalog: STORY (persona×topic×engine) + non-STORY (persona×topic × HOOK/SCENE/REFLECTION/EXERCISE/INTEGRATION) | Yes | Yes for catalog | Uses config (canonical_personas, topic_engine_bindings). Exposes `run_sim_test()`, `run_non_story_sim_test()` for programmatic use. Fails on any missing pool. |
| **scripts/ci/check_teacher_readiness.py** | Per-teacher: min EXERCISE, HOOK, REFLECTION, INTEGRATION (and optional MTA coverage) in SOURCE_OF_TRUTH/teacher_banks/{id}/approved_atoms | Yes | Per-teacher only | Requires `--teacher`. No single aggregated report; run_teacher_production_gates loops teachers and fails on first failure. |
| **phoenix_v4/planning/coverage_checker.py** | Plan-time: K-table + pool sizes per (persona, topic) **discovered from atoms layout** | Yes | Partial | Only checks pairs that already have dirs under atoms/. Does not assert full catalog coverage; complements the atoms test. |
| **scripts/fill_non_story_coverage_gaps.py** | Remediation: creates placeholder CANONICAL.txt for missing non-STORY slots | Yes | N/A | Uses same catalog as test_atoms_coverage; does not produce a report. |
| **scripts/generate_teacher_gap_atoms.py** | Remediation: reads artifacts/teacher_coverage_report.json, creates pending dirs for gaps | Yes | N/A | teacher_coverage_report.json is produced by coverage_gate when a plan fails (or run_pipeline). |
| **phoenix_v4/teacher/coverage_gate.py** | Teacher Mode: required vs available slots for a **specific** plan (teacher + format + arc); writes teacher_coverage_report.json on failure | Yes | Per-plan | Not a full-catalog report; run per plan to get gap report. |

---

## 2. Gaps (what is not covered by a single run)

- **No single “content missing” report** that aggregates: (1) atoms STORY + non-STORY, (2) plan-time coverage_check errors, (3) teacher readiness per teacher.
- **Teacher readiness** is only aggregated by running check_teacher_readiness per teacher (e.g. via run_teacher_production_gates) and collecting pass/fail; no JSON report of “which teachers have gaps” without running a full plan.
- **coverage_checker** discovers (persona, topic) from disk; it does not require every catalog pair to exist. So “missing” persona×topic combos (no atoms at all) are only detected by test_atoms_coverage_100_percent.

---

## 3. Conclusion

- **Unified catalog (atoms):** test_atoms_coverage_100_percent is the single source of truth and is complete for config-driven persona×topic×engine (STORY) and persona×topic (non-STORY).
- **Teacher Mode:** Teacher readiness (min counts) is per-teacher; teacher_coverage_report.json is plan-specific. A single “all teachers” content view requires running readiness per teacher and collecting results.
- **Plan-time (K-table / pool sizes):** coverage_checker is complementary; it checks discovered pairs only.

To get one place that answers “is any book content missing?” we add a **content coverage report script** that runs atoms tests (programmatic), coverage_check, and teacher readiness per teacher, then writes a single JSON + one-page summary.
