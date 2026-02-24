# Teacher Mode config

**Authority:** [specs/TEACHER_MODE_V4_CANONICAL_SPEC.md](../../specs/TEACHER_MODE_V4_CANONICAL_SPEC.md)

- **teacher_registry.yaml** — One entry per teacher. Defines `allowed_topics`, `allowed_engines`, `teacher_mode_defaults`, etc. Required for Teacher Mode books; `teacher_allocator` and pipeline read this.
- Teacher doctrine (forbidden claims, tone, glossary) lives per teacher under `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/doctrine.yaml`.
