# Teacher Mode Master Spec

**Authority:** Single canonical doc for strict-by-default behavior, coverage gate, fallback, TDEL, and CI.  
**See also:** [TEACHER_MODE_INVARIANTS.md](../TEACHER_MODE_INVARIANTS.md) (repo root), [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md).

---

## Summary

- **Strict by default:** When `teacher_mode=true`, `require_full_resolution=True`; no placeholders. Build fails if any slot cannot resolve.
- **Pre-compile coverage gate:** After arc + format expanded, before compile: validate teacher atom inventory vs required slots. If insufficient → write `artifacts/teacher_coverage_report.json`, raise `TeacherCoverageError`. Gate M: format slot types must have teacher support (or EXERCISE fallback when enabled and teacher pool > 0).
- **Controlled EXERCISE fallback:** Config `config/teachers/<teacher_id>.yaml`: `teacher_exercise_fallback`, `exercise_wrapper`. Fallback only when teacher EXERCISE pool non-empty and smaller than required; merge with practice library; deterministic ordering (source_priority, stable_hash(atom_id)); wrapper only when `atom_source == practice_fallback`.
- **Three-way taxonomy:** Every resolved slot has `atom_source`: teacher_native | teacher_synthetic | practice_fallback. Teacher-sourced (native + synthetic) ≥ 70% of book; native ≥ 60%.
- **TDEL:** Offline synthetic gap-fill only; doctrine fingerprint; allowlist schema (Gate N); scripts: generate_teacher_gap_atoms, validate_and_stage_synthetic_atoms, promote_approved_synthetic_atoms.
- **CI:** check_teacher_synthetic_governance (recompute from slots), check_teacher_readiness, check_doctrine_schema, check_doctrine_drift; artifacts: teacher_coverage_report, teacher_synthetic_report.

Implementation details and consolidated gate table are in the plan: Teacher Mode Strict and Fallback + TDEL.
