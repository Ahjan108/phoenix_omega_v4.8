# Teacher Mode config

**Authority:** [specs/TEACHER_MODE_MASTER_SPEC.md](../../specs/TEACHER_MODE_MASTER_SPEC.md), [TEACHER_MODE_INVARIANTS.md](../../TEACHER_MODE_INVARIANTS.md). **Full reference:** [docs/TEACHER_MODE_SYSTEM_REFERENCE.md](../../docs/TEACHER_MODE_SYSTEM_REFERENCE.md).

## teacher_registry.yaml

One entry per teacher. Defines `allowed_topics`, `allowed_engines`, `teacher_mode_defaults`, etc. Required for Teacher Mode books; `teacher_allocator` and pipeline read this.

## Per-teacher config: \<teacher_id\>.yaml

Optional file **config/teachers/\<teacher_id\>.yaml** controls strictness and EXERCISE fallback for that teacher. Loaded by `phoenix_v4.teacher.teacher_config.load_teacher_config(teacher_id)`.

| Field | Meaning |
|-------|---------|
| **teacher_id** | Must match filename. |
| **teacher_quality_profile** | `strict` \| `balanced` \| `minimal`. Affects fallback allowance and caps (see master spec). |
| **teacher_exercise_fallback** | If `true`, when teacher EXERCISE pool is non-empty but smaller than required slots, pool is merged with practice library (teacher atoms first). Default `false`. |
| **fallback_exercise_share_min** | When fallback used: teacher-sourced EXERCISE share must be ≥ this (e.g. 0.60). |
| **teacher_total_share_min** | (teacher_native + teacher_synthetic) / total_atoms ≥ this (e.g. 0.70). |
| **exercise_wrapper** | Optional. `intro_templates` and `close_templates` (lists of strings). When an EXERCISE slot is filled from practice library (`atom_source=practice_fallback`), renderer wraps prose with a deterministic intro/close from these lists. |

Examples: **config/teachers/master_feng.yaml**, **config/teachers/ahjan.yaml**. Teacher doctrine (forbidden claims, tone, glossary) lives under `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/doctrine.yaml` (or `doctrine.yaml` in teacher bank root).
