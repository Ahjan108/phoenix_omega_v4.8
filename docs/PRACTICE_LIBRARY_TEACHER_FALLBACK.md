# Practice Library — Teacher Fallback

When a teacher has **fewer approved EXERCISE atoms than needed** for a book, the system can supplement from the **practice library** so books still compile. A **teacher wrapper** (intro/close) ties each library exercise to the teacher's voice. **Implemented** as of Teacher Mode strict + fallback (see [TEACHER_MODE_SYSTEM_REFERENCE.md](TEACHER_MODE_SYSTEM_REFERENCE.md)).

---

## 1. When fallback applies

- **Teacher mode** is on (`teacher_id` set, not `default_teacher`).
- **Config:** `config/teachers/<teacher_id>.yaml` has `teacher_exercise_fallback: true`.
- EXERCISE pool from `teacher_banks/<teacher_id>/approved_atoms/EXERCISE/` is **non-empty but smaller than** the number of EXERCISE slots required by the format (after arc + format expanded).

If teacher EXERCISE pool is **empty** and fallback is enabled, the **coverage gate fails** (fallback not allowed when pool is 0). If fallback is disabled, any EXERCISE shortfall fails at the coverage gate.

---

## 2. Teacher wrapper (doctrine tie-in)

Library exercises are **generic**; the wrapper makes them **on-brand** for the teacher.

- **Wrapper** = short **intro** and optional **close** around the practice library exercise text.
- **Config:** `config/teachers/<teacher_id>.yaml` → `exercise_wrapper.intro_templates` and `exercise_wrapper.close_templates` (lists of strings).
- At **render time** (Stage 6): for any EXERCISE slot whose `atom_source == "practice_fallback"`, the renderer (`phoenix_v4.rendering.book_renderer._wrap_practice_fallback_exercise`) outputs intro + practice_text + close. Intro/close are chosen **deterministically** by hash of (book_id, chapter_index, slot_index) so the same book reproduces identically.

**Example:**  
Teacher's doctrine: "nervous system first."  
Intro template: "Using our nervous-system-first approach, try this grounding practice."  
Then the full practice library exercise text.  
Close template: "Notice how this supports your nervous system before we move on."

---

## 3. Implementation (current)

- **Config:** `config/teachers/<teacher_id>.yaml` — `teacher_exercise_fallback`, `exercise_wrapper.intro_templates`, `exercise_wrapper.close_templates`. Example: `config/teachers/master_feng.yaml`.
- **Pool merge:** `phoenix_v4.planning.pool_index.PoolIndex.get_pool("EXERCISE", ...)` when `teacher_exercise_fallback` and `0 < len(teacher_pool) < required_count`: merges with `get_backstop_pool()`; each practice item has `atom_source="practice_fallback"`. Pool is sorted by (atom_source_priority, stable_hash(atom_id)) (teacher_native=0, teacher_synthetic=1, practice_fallback=2).
- **Rendering:** Only when `atom_source == "practice_fallback"` (not for teacher_native or teacher_synthetic). See `phoenix_v4.rendering.book_renderer`.
- **Validation:** `phoenix_v4.qa.validate_teacher_exercise_share`: when fallback is used, teacher-sourced EXERCISE count must be ≥ 60% of total EXERCISE slots. Pipeline runs this after compile.

---

## 4. References

- **Practice store:** `SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl`
- **Selection:** `config/practice/selection_rules.yaml` (EXERCISE_BACKSTOP allowed_content_types)
- **Schema:** `specs/PRACTICE_ITEM_SCHEMA.md`
- **Teacher Mode system reference:** [TEACHER_MODE_SYSTEM_REFERENCE.md](TEACHER_MODE_SYSTEM_REFERENCE.md)
- **Master spec:** [specs/TEACHER_MODE_MASTER_SPEC.md](../specs/TEACHER_MODE_MASTER_SPEC.md)
