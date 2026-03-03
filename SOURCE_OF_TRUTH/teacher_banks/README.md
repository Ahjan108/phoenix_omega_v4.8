# Teacher banks (Teacher Mode V4)

Per-teacher content under `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/`.

- **raw/** — Teacher source files (RTF, txt, md). Never read by runtime.
- **kb/** — Built index (e.g. `index.json`) for gap-fill. Built by `tools/teacher_mining/build_kb.py`.
- **doctrine/** — Teacher doctrine (forbidden claims, tone, glossary). Offline lint only.
- **candidate_atoms/** — Generated atoms awaiting approval.
- **approved_atoms/** — Runtime-visible atoms (HOOK, SCENE, STORY, EXERCISE, INTEGRATION). YAML per atom.

Authority: specs/TEACHER_MODE_V4_CANONICAL_SPEC.md
