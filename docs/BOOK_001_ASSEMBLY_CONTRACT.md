# BOOK_001 ASSEMBLY CONTRACT

**Version:** V4.5 LOCKED  
**Status:** Active until Book_001 validated and shipped  
**Effective:** February 2026

No structural spec changes. No format additions. No governance layers. One book assembled, validated, shipped. Then reassess.

---

## Authority table

| Layer | Responsible | Tool |
|-------|-------------|------|
| Atoms | Writer | get_these/ → CANONICAL.txt |
| Lint | QA | lint_atoms.py (if present) |
| Plan | Stage 2 | format_selector → FormatPlan |
| Assembly | Stage 3 | assembly_compiler.py / run_pipeline.py |
| Emotional curve | Compiler | format_plan + band rules |
| Book rendering | Stage 6 | phoenix_v4/rendering (prose_resolver, book_renderer); QA: scripts/render_plan_to_txt.py; pipeline: --render-book. Output: .txt manuscript/QA. |

**Hard rule:** No layer touches the layer above or below it. Writers do not assemble. Assembler does not rewrite prose. Renderer does not edit atoms.

---

## Slot authority

Assembly pulls **only** from:

```
atoms/<persona_id>/<topic_id>/<engine>/CANONICAL.txt
```

Example: `atoms/gen_z_professional/self_worth/shame/CANONICAL.txt` or `atoms/nyc_executives/self_worth/shame/CANONICAL.txt`.

- No rewriting prose at assembly time.
- No injecting bridge language between chapters.
- No reordering role logic within atoms.

If an atom doesn’t fit, fix the atom and recompile. Do not patch at assembly.

---

## BAND rules

- STORY atoms without explicit BAND default to 3 (Canonical Spec §5.3).
- Book_001 requires minimum 3 distinct bands across the book (or 2 if &lt;3 chapters).
- No more than 3 consecutive chapters with the same dominant band (Canonical); for 6-chapter format, no more than 2 consecutive.
- Compiler enforces. If violated → reselect atom, not rewrite.
- **Pool tagging:** For multi-seed curve pass (e.g. Book_002, Book_003), assign explicit BAND to every STORY atom in the lane. Recommended distribution for a 20-atom pool per engine: BAND 1:1, 2:4, 3:7, 4:5, 5:3. See docs/BOOK_001_READINESS_CHECKLIST.md and artifacts/THREE_BOOK_STRESS_TEST.md.

---

## Chapter structure authority

Slot definitions come from **format_plan.slot_definitions** only. Stage 3 does not infer or default slots.

Example 6-chapter compact: `[STORY, REFLECTION, EXERCISE, INTEGRATION]` per chapter. No additions, no removals.

HOOK and SCENE slots are used when the selected format includes them (e.g. standard_book). Do not add them manually when format does not define them.

---

## Integration mode rules

- STILL-HERE: one use maximum; final chapter only.
- No two consecutive chapters with the same integration mode.
- FMT endings allowed on all non–STILL-HERE chapters where format allows.

---

## Optional slots and silence budget

- **optional_slot_types** (format_plan or book_spec): list of slot types (e.g. `REFLECTION`) that may be left empty when the pool is exhausted or no eligible atom remains.
- **silence_budget** (format_plan or book_spec): integer; maximum number of slots that may be filled with "silence" (empty) across the book. Only slots whose type is in optional_slot_types can use the budget. When used, atom_ids contain entries like `silence:REFLECTION:ch0:slot3`; downstream renderers should emit no content for these.
- CompiledBook.silence_budget_used reports how many silence slots were used.

## Repetition decay (semantic single-use)

- Atoms may carry **semantic_family** (in CANONICAL.txt metadata as `SEMANTIC_FAMILY: id`, or in teacher/compression YAML as `semantic_family`). The resolver ensures **at most one atom per semantic_family per book**; once an atom from a family is chosen, no other atom from that family is eligible for the rest of the plan. This avoids repeating the same insight.

## Asymmetry (chapter weights)

- Arcs may define optional **chapter_weights**: a list of numeric weights (length = chapter_count). CompiledBook carries this through as chapter_weights. Validators do not require symmetry; weights are for downstream use (e.g. pacing, density).

---

## Reflection / exercise reuse rules

- **Canonical rule (Part 3.3):** Each atom is used **at most once per compiled plan** (no reuse within a book). The plan compiler enforces this by default.
- **Relaxed policy (Book_001 only):** "REFLECTION max 2 / EXERCISE max 3" is a **relaxed policy** for Book_001 only, not the default spec. It is gated behind a single config flag: `planning.policy.allow_limited_reuse: false` (default). The codebase must not implement Book_001 relaxed reuse as the default; if limited reuse is ever enabled, it is explicit and config-driven.
- Reuse in non-consecutive chapters is preferred when limited reuse is enabled.

---

## Voice rules (Writer Spec — non-negotiable)

- STORY: third-person present. Always.
- No rhetorical questions anywhere.
- No motivational crescendo in integration.
- No empowerment language in embodiment.
- No resolution that removes social cost.
- Ending = stillness, non-response, or FMT open loop.

---

## No-edit rule

The compiled book is not manually edited.

If something reads wrong → identify which atom is the source → fix atom → recompile.

This rule exists to keep atoms clean for reuse across books. Manual edits to compiled output contaminate the pool.

---

## What unlocks after Book_001

After one book assembled, validated (band check, engine purity, TTS scan, duplication check), and shipped:

- Inventory expansion (e.g. commission additional exercise atom to fix overuse).
- Persona morph test (e.g. Healthcare RN or Gen Alpha).
- STILL-HERE positioning review.
- Exercise pool expansion.

None of these happen before Book_001 is complete.

---

**Reference:** [specs/PHOENIX_V4_CANONICAL_SPEC.md](../specs/PHOENIX_V4_CANONICAL_SPEC.md) §3.0 Stage 3 contract; [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md).
