# Phase 3 MVP — Content-Aware Emotional Force Validation

Phase 1 = structural geometry. Phase 2 = narrative topology. **Phase 3 = emotional force validation** on actual text.

Phase 3 answers: *“Does this book actually feel alive?”* — not just “are slots correct?” or “is arc metadata present?”

---

## What Phase 3 Does

It runs **after assembly** (or on synthetic chapter text in simulation). It reads **chapter text** and outputs:

- `phase3_passed` (bool)
- `phase3_errors` (list)
- `phase3_scores` (volatility_strength, embodiment_balance, consequence_authenticity, reassurance_repetition, overall)

**Four engines:**

1. **Volatility reality check** — If a chapter is marked volatile, it must contain ≥3 escalation verbs, ≥2 sensory stress words, ≥1 reaction marker. Otherwise volatility is labeled but not lived.
2. **Cognitive overload detector** — Ratio of cognitive verbs to body words. >5 → fail, >3 → warning. Prevents mechanism-lecture tone.
3. **Consequence authenticity** — If the chapter has action verbs, it must also contain reaction markers (so “act anyway” has visible consequence).
4. **Reassurance repetition** — Across a stack of books, no reassurance phrase (e.g. “You are not broken”, “Still here”) in >60% of books (fail) or >40% (warn).

All checks are **heuristic** (word lists + counts). No LLM, no embeddings in the MVP.

---

## Integration With Real Content

Pipeline:

1. Assemble book (plan compiler + atoms).
2. Phase 1: structure (slot/chapter/format).
3. Phase 2: waveform + arc + drift (metadata).
4. **Phase 3:** Pass **compiled chapter text** into `phase3_mvp.validate_book_phase3(chapters)` where each `ChapterInput` has `text`, `volatile`, `interrupt`. Then run `check_reassurance_repetition(all_book_texts)` on stacks (e.g. last 20 books).
5. If Phase 3 fail → rewrite or flag specific chapters; do not ship.

In simulation we generate **synthetic** chapter text (dense vs flat) so Phase 3 gates are exercised; ~12% of books get flat text and fail (cognitive overload). With real content, the same engines run on real prose.

---

## Files

- **phase3_mvp.py** — Lexicons, thresholds, `check_volatility_strength`, `check_cognitive_balance`, `check_consequence_authenticity`, `check_reassurance_repetition`, `validate_book_phase3`, `run_phase3_on_results`, `generate_synthetic_chapters`.
- **run_simulation.py** — `--phase3` runs Phase 3 after Phase 1 (and Phase 2 if `--phase2`).

---

## Pass logic

- Book **fails** if: any volatile chapter fails volatility check, or cognitive ratio >5, or reassurance repetition >60% in stack.
- **Warnings** (do not fail): cognitive ratio >3, reassurance in >40% of stack. Logged for review.
