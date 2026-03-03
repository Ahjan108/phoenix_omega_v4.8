# Teacher subsystem — production readiness (go-live proof)

**Purpose:** Evidence and gates for 100% production-ready Teacher Mode: validation, E2E smoke tests, release path, and branch protection.

**Related:** [TEACHER_ONBOARDING_CHECKLIST.md](TEACHER_ONBOARDING_CHECKLIST.md), [TEACHER_MODE_SYSTEM_REFERENCE.md](TEACHER_MODE_SYSTEM_REFERENCE.md).

---

## 1. Scope of “100% production-ready”

- [x] **Onboarding/config:** All 12 teachers in registry with config, bank skeleton, doctrine metadata, wrappers, teacher_conclusion (§2).
- [x] **Runtime/go-live proof** (this doc):
  1. Strict validation and CI gates: `scripts/ci/run_teacher_production_gates.py` (doctrine schema + readiness; optional synthetic governance with `--plan`).
  2. E2E Teacher Mode compile smoke tests: `tests/test_teacher_mode_e2e_smoke.py` (one topic/persona/arc per teacher; pass when coverage or full compile succeeds).
  3. Release/publish path uses only approved assets (coverage gate + require_full_resolution; no fallback/missing-atom in plan).
  4. Evidence: archive run logs + artifacts + commit SHA in §5; re-run and fill after each green run on main.
  5. Branch protection: require **Teacher gates** status check (workflow `.github/workflows/teacher-gates.yml`).

---

## 2. Validation and CI gates

### 2.1 Script: `scripts/ci/run_teacher_production_gates.py`

Runs:

- **Doctrine schema** — `scripts/ci/check_doctrine_schema.py --teacher <id>` for every teacher in registry.
- **Teacher readiness** — `scripts/ci/check_teacher_readiness.py --teacher <id> --min-exercise 12 --min-hook 0 --min-reflection 0 --min-integration 0` (F006 EXERCISE/STORY minimums; HOOK/REFLECTION/INTEGRATION optional when F006 slot stubs are used).
- **Teacher synthetic governance** (optional) — `scripts/ci/check_teacher_synthetic_governance.py <plan.json>` when `--plan` is provided.

**Run (from repo root):**

```bash
python3 scripts/ci/run_teacher_production_gates.py
python3 scripts/ci/run_teacher_production_gates.py --plan artifacts/out.plan.json  # include synthetic check
```

**Exit 0** only if all gates pass.

### 2.2 F006 slot coverage (optional for full E2E)

To pass the **coverage gate** for F006 (HOOK, SCENE, STORY, REFLECTION, COMPRESSION, EXERCISE, INTEGRATION), each teacher needs at least 20 approved atoms per slot for a 20-chapter arc. Stub generator:

```bash
python3 scripts/teacher_stub_f006_slots.py
# Then for each teacher: python3 tools/approval/approve_atoms.py --teacher <id> approve-all
```

---

## 3. E2E Teacher Mode compile smoke tests

**Test file:** `tests/test_teacher_mode_e2e_smoke.py`

- Parametrizes over all teachers in registry.
- For each teacher: runs `run_pipeline.py --topic burnout --persona gen_z_professionals --arc <F006 arc> --teacher <id> --teacher-mode --out <tmp>/plan.json`.
- If teacher **lacks** F006 slot coverage: allows pipeline failure and asserts failure is coverage-related (TeacherCoverageError / “coverage” / “insufficient”).
- If teacher **has** F006 slot coverage: asserts pipeline exit 0, plan has `teacher_mode: true`, `teacher_id` matches, **no placeholders** in `atom_ids`, and no “Missing:” in output.

**Run:**

```bash
pytest tests/test_teacher_mode_e2e_smoke.py -v
pytest tests/test_teacher_mode_e2e_smoke.py -v --tb=short
```

**Unit tests (Teacher Arc):**

```bash
pytest tests/teacher_arc_test.py -v
```

---

## 4. Release / publish path

- **No fallback/missing-atom:** Teacher Mode uses `require_full_resolution=True`; compiler does not emit placeholders. Any missing slot fails the **coverage gate** before compile. Post-compile, `validate_teacher_exercise_share` and synthetic governance (when run) enforce teacher-sourced ratio and no placeholders.
- **Approved assets only:** Pipeline and prose resolver read from `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms/` only; no runtime fallback to unapproved candidates. Export/release scripts must not bypass teacher coverage or synthetic checks.

---

## 5. Evidence (run logs, artifacts, commit SHA)

Archive the following when gates and E2E are green on main:

| Item | Location / command |
|------|--------------------|
| **Commit SHA** | `git rev-parse HEAD` (main after merge) |
| **Teacher production gates log** | `python3 scripts/ci/run_teacher_production_gates.py 2>&1 \| tee artifacts/logs/teacher_production_gates.log` |
| **E2E smoke test log** | `pytest tests/test_teacher_mode_e2e_smoke.py tests/teacher_arc_test.py -v --tb=short 2>&1 \| tee artifacts/logs/teacher_e2e_smoke.log` |
| **Teacher arc test log** | Included in E2E log above |
| **Artifacts** | `artifacts/teacher_coverage_report.json` (if gate run), `artifacts/teacher_synthetic_report.json` (if --plan used) |

**Example evidence block (fill after run):**

```markdown
## Last production-ready run

- **Date:** YYYY-MM-DD
- **Commit (main):** <SHA>
- **Gates:** PASS (doctrine schema + teacher readiness [+ synthetic governance])
- **E2E:** PASS (all teachers parametrized; coverage-gate or full compile as applicable)
- **Logs:** artifacts/logs/teacher_production_gates.log, artifacts/logs/teacher_e2e_smoke.log
- **CI:** GitHub Actions workflow "Teacher gates" (`.github/workflows/teacher-gates.yml`) — required status check for branch protection.
```

---

## 6. Branch protection and required gates

To make the teacher subsystem **truly** 100% production-ready:

1. **Required status checks on main (or release branch):**
   - Run **Teacher production gates:** `scripts/ci/run_teacher_production_gates.py` (e.g. in a GitHub Actions job).
   - Run **Teacher E2E smoke:** `pytest tests/test_teacher_mode_e2e_smoke.py tests/teacher_arc_test.py -v`.

2. **GitHub workflow:** `.github/workflows/teacher-gates.yml` runs on push/PR when teacher-related paths change:
   - `scripts/ci/run_teacher_production_gates.py`
   - `pytest tests/teacher_arc_test.py`
   - `pytest tests/test_teacher_mode_e2e_smoke.py`
   - Workflow name: **Teacher gates**. Fails the run if any step fails.

3. **Branch protection rule:** In repo settings (Branches → main → Edit), add **Teacher gates** as a required status check so PRs cannot merge until the workflow passes.

Once these are in place and green on main, the teacher subsystem is **100% production-ready** for go-live.
