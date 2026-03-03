# Book_001 — Scope Freeze

**Status:** V4.5 LOCKED until Book_001 complete.

No structural spec changes. No new formats. No new governance layers. No inventory expansion (no commissioning of new atoms) until one book is assembled, validated, and—if TTS is in use—listened to.

## Locked book parameters

| Parameter | Value |
|-----------|--------|
| Persona | `nyc_executives` (canonical) |
| Topic | `self_worth` |
| Engine | `shame` and `comparison` (allowed for self_worth per topic_engine_bindings) |
| Atom pool | `atoms/nyc_executives/self_worth/shame/CANONICAL.txt` and `comparison/CANONICAL.txt` (20 STORY atoms each; all 40 BAND-tagged) |
| Seed (example) | `book001` |
| Proof run format | `--runtime-format standard_book --structural-format F006` (12 chapters) |

Format and chapter count are determined by Stage 2 when the pipeline runs; for Book_001 proof we constrained to 12 chapters so the plan uses only current inventory (no STORY placeholders). No manual override of slot_definitions; Stage 3 uses FormatPlan output only.

## Unfreeze when

- One assembled book plan has been produced by the pipeline. (Done: Book_001, Book_002, Book_003 with seeds book001, book002, book003.)
- Readiness validator (or checklist) has been run and passed. (Post-compile emotional curve: `--plan` pass for all three.)
- Output has been inspected (plan_hash, chapter_slot_sequence, atom_ids, dominant_band_sequence).
- Optional: duplication check and/or TTS render and listen are done.
- Post-mortem is complete and the decision is to expand (inventory or persona/topic) or to fix and re-run.

Until then, do not add formats, add governance, or commission new atoms.

**Production after Book_001:** If a book plan uses one exercise more than 3 times (e.g. weight_drop × 4), commission one new exercise atom (cool or warm band) and re-plan; do not ship with exercise overuse.
