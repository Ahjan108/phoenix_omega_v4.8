# BOOK_001 READINESS CHECKLIST

Run this before calling the pipeline. Every box must be checked (or explicitly waived for a given run).

**Structural checks** can be run via:  
`python scripts/validate_book_001_readiness.py --persona <persona> --topic <topic> --engine <engine> [--chapter-count N]`  
Exit 0 = structural pass.

**Emotional curve (books ≥ 6 chapters):** After compiling, run with `--plan <path>` to enforce ≥ 3 distinct BAND values and no more than 3 consecutive chapters with same BAND:  
`python scripts/validate_book_001_readiness.py --persona <persona> --topic <topic> --engine <engine> --plan artifacts/book_001.plan.json`  
Flat all-BAND-3 books will fail until inventory has band diversity or chapter count is &lt; 6.

**100% pipeline (compiled plan validation):** For a fully resolved plan, the compiled output must have no duplicate atom IDs and must pass `validate_compiled_plan` (slot sequence parity with `format_plan.slot_definitions`, total atom_ids length, emotional curve when chapter_count ≥ 6). Run validation as part of the pipeline (scripts/run_pipeline.py) or explicitly: load the plan and call `phoenix_v4.qa.validate_compiled_plan.validate_compiled_plan(plan, format_plan)`; if not valid, exit non-zero.

**Current state (nyc_executives × self_worth):** All 40 STORY atoms (engines shame + comparison) have explicit BAND; target distribution per engine 1:1, 2:4, 3:7, 4:5, 5:3. Book_001, Book_002, and Book_003 all pass curve (seeds book001, book002, book003). See `artifacts/THREE_BOOK_STRESS_TEST.md`.

Engine, TTS, integration, reuse, and duplication checks below are manual or via a future extended validator.

**Example Book:** invisible_correction_v1 — Persona: gen_z_professional, Topic: self_worth, Engine: shame, Format: 6 chapters × [STORY, REFLECTION, EXERCISE, INTEGRATION].

---

## STRUCTURAL CHECKS

- [ ] `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` exists
- [ ] CANONICAL.txt contains at least N STORY atoms (one per chapter)
- [ ] All STORY atoms have explicit BAND (1–5) or accept default 3
- [ ] At least 3 distinct BAND values across assigned atoms (or 2 if &lt;3 chapters)
- [ ] No more than 3 consecutive chapters share the same dominant BAND (2 for 6-chapter compact)
- [ ] No duplicate atom IDs in the plan
- [ ] No unknown roles (only: RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT)
- [ ] Slot definitions match format (from format_plan / Stage 2)

---

## ENGINE PURITY CHECKS (SHAME)

- [ ] Every STORY has a visible exposure moment (not internal only)
- [ ] Every STORY has a named or implied witness
- [ ] Every STORY has at least one body anchor (face heat, chest drop, shoulders in, stillness, freeze)
- [ ] No STORY ends with resolution, empowerment, or insight
- [ ] No STORY contains: "embarrassed", "humiliated", "ashamed", "self-esteem", "owned it", "no one cares"
- [ ] No anxiety bleed: no future-consequence spirals, no job-loss fear, no "what if" chains
- [ ] TURNING_POINT ends with crack not cure
- [ ] EMBODIMENT ends with protective action, not triumph

---

## TTS COMPLIANCE CHECKS

- [ ] No rhetorical questions (search "?" — zero outside dialogue)
- [ ] No tentative language (perhaps, you might, maybe, it's possible, consider trying)
- [ ] No sentence exceeds 18 words in REFLECTION or EXERCISE blocks (or 25 per Writer Spec if different)
- [ ] No paragraph exceeds 6 lines
- [ ] No forbidden terms from topic_skins.yaml
- [ ] Rhythm variance present where required by Writer Spec

---

## INTEGRATION CHECKS

- [ ] STILL-HERE used exactly once (peak/final chapter as per plan)
- [ ] No two consecutive chapters share the same integration mode
- [ ] Final chapter does not contain resolution language ("that's enough", "you'll be okay") unless format allows
- [ ] FMT present where required for non-final chapters (per format)

---

## REFLECTION / EXERCISE REUSE CHECKS

- [ ] No REFLECTION appears more than twice
- [ ] No EXERCISE appears more than **three** times (if four uses → fail until new exercise or plan change)
- [ ] Reused REFLECTION in non-consecutive chapters where possible
- [ ] Each EXERCISE reuse contextually reframed (different band, different body note) where possible

---

## DUPLICATION CHECKS

- [ ] No atom prose appears more than once in the plan
- [ ] No 6-gram duplication across selected atoms (run n-gram check or manual scan)
- [ ] No identical carry lines across chapters

---

## FINAL GO / NO-GO

All boxes checked → run pipeline.

Any box fails → fix atom or plan → recheck → then run.

Do not patch at compile time. Fix the source.

**Pipeline (example):**  
`python scripts/run_pipeline.py --topic self_worth --persona nyc_exec --seed book001 --out artifacts/book_001.plan.json --runtime-format standard_book --structural-format F006`  
For Book_002 / Book_003: same args with `--seed book002` or `--seed book003`. For gen_z when pool exists: use persona `gen_z_professionals` (canonical) and appropriate format overrides.

**QA render (plan → text):** To produce readable book text for QA, run  
`python scripts/render_plan_to_txt.py artifacts/book_001.plan.json -o artifacts/books_qa/book_001.txt [--allow-placeholders]`  
Uses **Stage 6** (`phoenix_v4.rendering`): prose_resolver + TxtWriter. Outputs go to `artifacts/books_qa/`. Options: `--allow-placeholders`, `--on-missing fail|placeholder`, `--no-title-page`, `--atoms-root`. If the plan contains placeholders and `--allow-placeholders` is not set, the script exits with an error; use `--allow-placeholders` to emit `[Placeholder: TYPE]` or `[Silence: TYPE]` for unresolved slots. See [V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md) §1 (Stage 6).
