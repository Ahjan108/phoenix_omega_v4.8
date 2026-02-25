# Ahjan — teacher source materials

**Teacher id:** `ahjan` (canonical display name: Ahjan; sources may say "Samvara" or "BD").

## Layout

| Purpose | Location |
|--------|----------|
| **Source / intake** | This folder: `teachers/ahjan/` (e.g. `intake/` = raw talks, blogs) |
| **Runtime content** | `SOURCE_OF_TRUTH/teacher_banks/ahjan/` (approved_atoms, candidate_atoms, doctrine, kb, raw) |
| **Config** | `config/teachers/ahjan.yaml` and `config/teachers/teacher_registry.yaml` |

Pipeline and Teacher Mode read from **SOURCE_OF_TRUTH/teacher_banks/ahjan/** only. This folder is for authoring and intake; `scripts/intake_teacher_ahjan.py` copies from `teachers/ahjan/intake/` into the bank’s `raw/` and runs the KB build.
