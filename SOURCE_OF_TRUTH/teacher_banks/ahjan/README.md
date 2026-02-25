# Ahjan — Teacher Mode V4

**Display name:** Ahjan (sources may say "Samvara" or "BD" / Buddha Dojo; same teacher).

- **raw/** — 21 RTF files from Buddha Dojo / BD Blog (happiness, purity, karma yoga, meditation, love, etc.). One file (`comparison videos AM.rtf`) is off-topic (affiliate marketing); can exclude from KB with `--exclude` if desired.
- **kb/** — Built by `python3 tools/teacher_mining/build_kb.py --teacher ahjan`. 22 docs, 224 chunks.
- **doctrine/** — doctrine.yaml: forbidden claims, tone, glossary, exercise safety.
- **approved_atoms/** — STORY, EXERCISE, QUOTE, TEACHING (and HOOK, SCENE, INTEGRATION). Populated by mining: `python3 tools/teacher_mining/mine_kb_to_atoms.py --teacher ahjan --approve`. Each atom: atom_id, band (STORY), body, teacher.source_refs.

To compile a Teacher Mode book: pass `teacher_id="ahjan"` and `teacher_mode=True` in BookSpec (e.g. from catalog planner or pipeline). Stage 3 will use this bank's approved_atoms. Add atoms to approved_atoms/STORY/ (and EXERCISE/, etc.) then run gap report and gap-fill as needed (see specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md).

**Intake script:** `python3 scripts/intake_teacher_ahjan.py` (copies from `teachers/ahjan/intake/` into `raw/`).
