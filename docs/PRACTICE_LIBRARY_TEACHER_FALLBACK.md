# Practice Library — Teacher Fallback

When a teacher has **fewer approved EXERCISE atoms than needed** for a book (e.g. fewer than the number of EXERCISE slots in the plan), the system can supplement from the **practice library** so books still compile. To keep exercises aligned with the teacher’s voice, a **teacher wrapper** ties each library exercise to the teacher’s teachings or doctrine.

---

## 1. When fallback applies

- **Teacher mode** is on (`teacher_atoms_root` set).
- EXERCISE pool from `teacher_banks/<teacher_id>/approved_atoms/EXERCISE/` is **non-empty but smaller than** the number of EXERCISE slots required by the format (e.g. 6 chapters × 1 EXERCISE = 6 slots, but teacher has 2 approved).
- Optional: config or feature flag to enable “teacher + practice library” merge (e.g. `teacher_exercise_fallback: true`).

---

## 2. Teacher wrapper (doctrine tie-in)

Library exercises are **generic**; the wrapper makes them **on-brand** for the teacher.

- **Wrapper** = short doctrine-aligned **intro/framing** (and optionally a **close**) around the library exercise text.
- Stored or generated per teacher (e.g. template or 1–2 sentences that reference the teacher’s framework, language, or key ideas).
- At **render time**: for any EXERCISE slot filled from the practice library, output = `[teacher_wrapper_intro]` + `[practice_item.text]` + optional `[teacher_wrapper_close]`.

**Example:**  
Teacher’s doctrine: “nervous system first.”  
Wrapper intro: “Using our nervous-system-first approach, try this grounding practice.”  
Then the full practice library exercise text.  
Optional close: “Notice how this supports your nervous system before we move on.”

---

## 3. Implementation options (no distribution logic yet)

- **Config:** e.g. `config/teachers/<teacher_id>.yaml` with `exercise_fallback: true` and optional `exercise_wrapper_intro` / `exercise_wrapper_close` (or paths to approved snippets).
- **Pool merge:** When building the EXERCISE pool for a teacher, if `len(teacher_pool) < required_slots`, append practice-library items (from `get_backstop_pool()` or a teacher-filtered subset) and mark them (e.g. `metadata.source = "practice_library"`) so the renderer can apply the wrapper only to those.
- **Rendering:** In prose resolution, if `atom_id` is a practice_id and the plan/context indicates teacher mode and “use wrapper,” resolve to `wrapper_intro + practice_text + wrapper_close` instead of raw `practice_text`.

Distribution (e.g. 65% teacher / 25% library / 10% mixed) is **not** defined here; that will be specified in a later config/prompt.

---

## 4. References

- **Practice store:** `SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl`
- **Selection:** `config/practice/selection_rules.yaml` (EXERCISE_BACKSTOP allowed_content_types)
- **Schema:** `specs/PRACTICE_ITEM_SCHEMA.md`
