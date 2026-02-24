# Teacher Mode — System Reference

**Purpose:** Single reference for all Teacher Mode implementation: modules, scripts, config, artifacts, and pipeline flow.  
**Authority:** [TEACHER_MODE_INVARIANTS.md](../TEACHER_MODE_INVARIANTS.md) (repo root), [specs/TEACHER_MODE_MASTER_SPEC.md](../specs/TEACHER_MODE_MASTER_SPEC.md), [specs/TEACHER_MODE_V4_CANONICAL_SPEC.md](../specs/TEACHER_MODE_V4_CANONICAL_SPEC.md).  
**Last updated:** 2026-02-23

---

## 1. Invariants (summary)

When `teacher_mode=true`:

- **No placeholders** — All slots resolve to real atoms; build fails otherwise (Gate A).
- **No runtime generation** — Content from teacher_native, teacher_synthetic (TDEL approved), or practice_fallback (EXERCISE only, opt-in).
- **Pre-compile coverage gate** — Inventory validated after arc+format expanded, before compile; gaps → `TeacherCoverageError` + `artifacts/teacher_coverage_report.json`.
- **Three-way taxonomy** — Every slot has `atom_source`: `teacher_native` | `teacher_synthetic` | `practice_fallback`. Teacher-sourced ≥ 70%; native ≥ 60%.
- **Determinism** — Pools sorted by `(atom_source_priority, stable_hash(atom_id))`; wrapper choice by hash of `(book_id, chapter_index, slot_index)`.

Full list: [TEACHER_MODE_INVARIANTS.md](../TEACHER_MODE_INVARIANTS.md).

---

## 2. Pipeline flow (teacher path)

1. **Stage 1** — `run_pipeline.py`: BookSpec with `teacher_mode=True` when `teacher_id` set and not `default_teacher`.
2. **Stage 2** — Format + arc aligned; `format_plan_dict` has final `slot_definitions` and `chapter_count`.
3. **Pre-compile (mandatory)** — `phoenix_v4.teacher.coverage_gate.run_coverage_gate(book_spec, format_plan, arc, ...)`. If gaps and not EXERCISE-with-fallback → write `artifacts/teacher_coverage_report.json`, raise `TeacherCoverageError`.
4. **Stage 3** — `compile_plan(..., require_full_resolution=True)` when teacher_mode. Resolver gets `required_slots_by_type`, `teacher_exercise_fallback`; pool_index merges EXERCISE with practice library when fallback enabled and `0 < len(teacher_pool) < required`. Resolver raises `TeacherCoverageError` if no candidates (never returns None). CompiledBook includes `atom_sources` (same length as `atom_ids`).
5. **Post-compile** — `validate_teacher_exercise_share`: when any EXERCISE is `practice_fallback`, teacher EXERCISE share ≥ 60%. §3.12: if any `teacher_synthetic` and no `teacher_doctrine_version` in output → fail.
6. **Output** — Plan JSON includes `teacher_id`, `teacher_mode`, `atom_sources`, `teacher_doctrine_version`, `doctrine_fingerprint` (when doctrine.yaml present).

---

## 3. Modules and packages

| Location | Role |
|----------|------|
| **phoenix_v4/teacher/** | Teacher Mode package. |
| **phoenix_v4/teacher/__init__.py** | Exports: `TeacherCoverageError`, `compute_required_slots`, `compute_available_teacher_atoms`, `compute_story_band_inventory`, `make_gap_report`, `run_coverage_gate`. |
| **phoenix_v4/teacher/coverage_gate.py** | Pre-compile coverage gate. `compute_required_slots(book_spec, format_plan, arc)`, `compute_available_teacher_atoms(teacher_id)`, `compute_story_band_inventory(teacher_id)`, `make_gap_report(...)`, `run_coverage_gate(...)`. Raises not used inline; caller raises `TeacherCoverageError` on failure. |
| **phoenix_v4/teacher/teacher_config.py** | Loads `config/teachers/<teacher_id>.yaml`: `teacher_quality_profile`, `teacher_exercise_fallback`, `fallback_exercise_share_min`, `teacher_total_share_min`, `exercise_wrapper` (intro_templates, close_templates). |
| **phoenix_v4/teacher/doctrine_fingerprint.py** | `load_doctrine_yaml(path)`, `canonicalize_doctrine(obj)`, `fingerprint_doctrine(obj)`. Canonical JSON (sorted keys, NFKC, strip non-doctrinal keys) → sha256. |
| **phoenix_v4/planning/pool_index.py** | `AtomEntry` has `atom_source`. Teacher pool stamps `teacher_native` / `teacher_synthetic` from YAML `source`. EXERCISE fallback: when `teacher_exercise_fallback` and `0 < len(teacher_pool) < required_count`, merge with `get_backstop_pool()`, sort by `(source_priority, stable_hash(atom_id))`. |
| **phoenix_v4/planning/slot_resolver.py** | `ResolverContext`: `teacher_mode`, `required_slots_by_type`, `teacher_exercise_fallback`. When teacher_mode and no candidates → raise `TeacherCoverageError`. Returns `(atom_id, atom_source)`. |
| **phoenix_v4/planning/assembly_compiler.py** | Builds context with `required_slots_by_type`, `teacher_exercise_fallback`; records `atom_sources`; adds `atom_sources` to CompiledBook. |
| **phoenix_v4/planning/practice_selector.py** | Backstop entries use `atom_source="practice_fallback"`. |
| **phoenix_v4/planning/teacher_portfolio_planner.py** | `allocate_wave(..., min_exercise_coverage=0, min_story_coverage=0)`. `_teacher_meets_coverage_threshold(teacher_id, min_exercise, min_story_total)` excludes teachers below threshold. |
| **phoenix_v4/rendering/book_renderer.py** | For EXERCISE with `atom_source == "practice_fallback"`, wraps prose via `_wrap_practice_fallback_exercise(prose, plan, chapter_index, slot_index)` (deterministic intro/close from teacher config). |
| **phoenix_v4/qa/validate_teacher_exercise_share.py** | When teacher_mode and any EXERCISE is practice_fallback, (teacher EXERCISE count)/(total EXERCISE) ≥ 60%. `validate_plan(plan, min_share=0.60)`. |

---

## 4. Scripts

| Script | Role |
|--------|------|
| **scripts/run_pipeline.py** | Sets `teacher_mode` when teacher_id set; runs coverage gate before compile; passes `require_full_resolution`; runs `validate_teacher_exercise_share` after compile; emits `teacher_doctrine_version`, `doctrine_fingerprint`, `atom_sources`; fails when synthetic present but no doctrine version. |
| **scripts/ci/check_teacher_synthetic_governance.py** | Recomputes counts from `atom_ids` + `atom_sources`. Rules: no placeholders, synthetic ratio caps, native ratio min, teacher_sourced min, max synthetic per book, doctrine_fingerprint when synthetic; Gate B (≥3 STORY bands); Gate O (no atom reuse). Writes `artifacts/teacher_synthetic_report.json` with `--out`. |
| **scripts/ci/check_teacher_readiness.py** | Gate F: min EXERCISE, HOOK, REFLECTION, INTEGRATION per teacher. `--teacher`, `--min-exercise`, etc. |
| **scripts/ci/check_doctrine_schema.py** | Gate N: doctrine.yaml allowlist; required keys; nested allowlist (fallback_alignment, constraints). `--teacher` or path to doctrine. |
| **scripts/ci/check_doctrine_drift.py** | Compares current doctrine fingerprint to `teacher_banks/<id>/reports/doctrine_registry.json`; fails if fingerprint changed but doctrine_version not incremented (or version bumped but fingerprint unchanged). |
| **scripts/generate_teacher_gap_atoms.py** | TDEL stub: reads gap report, creates pending dirs. Actual LLM generation is separate. |
| **scripts/validate_and_stage_synthetic_atoms.py** | TDEL stub: validates and stages synthetic atoms for approval. |
| **scripts/promote_approved_synthetic_atoms.py** | TDEL: promotes manifest-listed atoms from staging to `approved_atoms/`. |

---

## 5. Config and paths

| Purpose | Location |
|---------|----------|
| **Per-teacher config** | `config/teachers/<teacher_id>.yaml` — `teacher_id`, `teacher_quality_profile`, `teacher_exercise_fallback`, `fallback_exercise_share_min`, `teacher_total_share_min`, `exercise_wrapper.intro_templates`, `exercise_wrapper.close_templates`. Example: `config/teachers/master_feng.yaml`. |
| **Teacher registry** | `config/teachers/teacher_registry.yaml` — one entry per teacher (allowed_topics, allowed_engines, teacher_mode_defaults). |
| **Teacher banks** | `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/` — `approved_atoms/<slot_type>/*.yaml`, optional `doctrine/doctrine.yaml`, `synthetic_atoms/` (pending, approved_staging, rejected), `reports/` (doctrine_registry.json, gap report). |
| **Doctrine** | `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/doctrine.yaml` or `.../doctrine.yaml`. Allowlist: teacher_id, doctrine_version, tradition, primary_methods, core_principles, tone_profile, signature_metaphors, signature_practices, transformation_model, forbidden_language, avoid_claims, fallback_alignment, constraints. |

---

## 6. Artifacts

| Artifact | When / who |
|----------|------------|
| **artifacts/teacher_coverage_report.json** | Written when coverage gate fails (and optionally on pass). Required vs available by slot; gaps; story by band; fallback_required flag. |
| **artifacts/teacher_synthetic_report.json** | Written by `check_teacher_synthetic_governance.py --out`. Per-book diagnostics: counts, ratios, violations. |
| **teacher_coverage_report.json** (in gate) | Same structure; gate writes to `artifacts_dir` when passed/failed for teacher. |

---

## 7. CompiledBook / plan output (teacher)

When teacher_mode, the written plan JSON includes:

- `teacher_id`, `teacher_mode`
- `atom_sources` (list, same length as `atom_ids`): `teacher_native` | `teacher_synthetic` | `practice_fallback` | null
- `teacher_doctrine_version`, `doctrine_fingerprint` (when doctrine.yaml exists under teacher bank)

CI and governance use `atom_sources` to recompute counts and ratios; do not trust stored counts for gates.

---

## 8. References

- **Invariants:** [TEACHER_MODE_INVARIANTS.md](../TEACHER_MODE_INVARIANTS.md)
- **Master spec:** [specs/TEACHER_MODE_MASTER_SPEC.md](../specs/TEACHER_MODE_MASTER_SPEC.md)
- **Canonical Teacher Mode spec:** [specs/TEACHER_MODE_V4_CANONICAL_SPEC.md](../specs/TEACHER_MODE_V4_CANONICAL_SPEC.md)
- **Practice library teacher fallback:** [docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md](PRACTICE_LIBRARY_TEACHER_FALLBACK.md)
- **Config teachers README:** [config/teachers/README.md](../config/teachers/README.md)
