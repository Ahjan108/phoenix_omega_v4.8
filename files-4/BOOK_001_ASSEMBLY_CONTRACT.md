# BOOK_001 ASSEMBLY CONTRACT

**Version:** V4.5 LOCKED
**Status:** Active until Book_001 validated and shipped
**Effective:** February 2026

No structural spec changes. No format additions. No governance layers. One book assembled, validated, shipped. Then reassess.

---

## Authority Table

| Layer | Responsible | Tool |
|-------|-------------|------|
| Atoms | Writer | get_these/ → CANONICAL.txt |
| Lint | QA | lint_atoms.py |
| Plan | Stage 2 | assembly_compiler.py |
| Assembly | Stage 3 | run_pipeline.py |
| Emotional curve | Compiler | format_plan + band rules |
| Book rendering | Renderer | markdown_renderer.py or tts |

**Hard rule:** No layer touches the layer above or below it. Writers do not assemble. Assembler does not rewrite prose. Renderer does not edit atoms.

---

## Slot Authority

Assembly pulls **only** from:
```
atoms/gen_z_professional/self_worth/shame/CANONICAL.txt
```

No rewriting prose at assembly time.
No injecting bridge language between chapters.
No reordering role logic within atoms.

If an atom doesn't fit, fix the atom and recompile. Do not patch at assembly.

---

## BAND Rules

- STORY atoms without explicit BAND default to 3.
- Book_001 requires minimum 3 distinct bands across 6 chapters.
- No more than 2 consecutive chapters with the same dominant band.
- Compiler enforces. If violated → reselect atom, not rewrite.

---

## Chapter Structure Authority

Slot definitions for Book_001:
```
[STORY, REFLECTION, EXERCISE, INTEGRATION]
```
Per chapter. No additions. No removals.

HOOK and SCENE slots are not activated for this format tier. Do not add them manually.

---

## Integration Mode Rules

- STILL-HERE: one use maximum. Final chapter only.
- No two consecutive chapters with the same integration mode.
- FMT endings allowed on all non-STILL-HERE chapters.

---

## Reflection / Exercise Reuse Rules

- One REFLECTION may be reused once (maximum two appearances per book).
- One EXERCISE may be reused twice (maximum three appearances per book).
- Reuse must be in non-consecutive chapters where possible.

---

## Voice Rules (From Writer Spec — Non-Negotiable)

- STORY: third-person present. Always.
- No rhetorical questions anywhere.
- No motivational crescendo in integration.
- No empowerment language in embodiment.
- No resolution that removes social cost.
- Ending = stillness, non-response, or FMT open loop.

---

## No-Edit Rule

The compiled book is not manually edited.

If something reads wrong → identify which atom is the source → fix atom → recompile.

This rule exists to keep atoms clean for reuse across books. Manual edits to compiled output contaminate the pool.

---

## What Unlocks After Book_001

After one book assembled, validated (band check, engine purity, TTS scan, flinch audit), and shipped:

- Inventory expansion (commission 6 gap atoms)
- Persona morph test (Healthcare RN or Gen Alpha)
- STILL-HERE positioning review
- Exercise pool expansion (third and fourth unique exercises)

None of these happen before Book_001 is complete.
