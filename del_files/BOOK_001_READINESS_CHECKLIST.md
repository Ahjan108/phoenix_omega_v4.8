# BOOK_001 READINESS CHECKLIST

Run this before calling the pipeline. Every box must be checked.

**Book:** invisible_correction_v1
**Persona:** gen_z_professional
**Topic:** self_worth
**Engine:** shame
**Format:** 6 chapters × [STORY, REFLECTION, EXERCISE, INTEGRATION]

---

## STRUCTURAL CHECKS

- [ ] `atoms/gen_z_professional/self_worth/shame/CANONICAL.txt` exists
- [ ] CANONICAL.txt contains minimum 6 STORY atoms (one per chapter)
- [ ] All STORY atoms have explicit BAND (1–5) set
- [ ] At least 3 distinct BAND values across 6 assigned atoms
- [ ] No more than 2 consecutive chapters share the same dominant BAND
- [ ] No duplicate atom IDs in the plan
- [ ] No unknown roles (only: RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT)
- [ ] Slot definitions match format: [STORY, REFLECTION, EXERCISE, INTEGRATION] × 6

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
- [ ] No sentence exceeds 18 words in REFLECTION or EXERCISE blocks
- [ ] No paragraph exceeds 6 lines
- [ ] No forbidden terms from topic_skins.yaml
- [ ] At least one sentence of 3 words or fewer per chapter
- [ ] Rhythm variance present: shortest-to-longest spread ≥ 12 words in any 10 consecutive sentences

---

## INTEGRATION CHECKS

- [ ] STILL-HERE used exactly once (Chapter 4 / peak chapter)
- [ ] No two consecutive chapters share the same integration mode
- [ ] Final chapter does not contain resolution language ("that's enough", "you'll be okay")
- [ ] FMT present in Chapters 1, 2, 3, 5, 6 (open loop endings)

---

## REFLECTION / EXERCISE REUSE CHECKS

- [ ] No REFLECTION appears more than twice
- [ ] No EXERCISE appears more than three times
- [ ] Reused REFLECTION appears in non-consecutive chapters where possible
- [ ] Each EXERCISE reuse is contextually reframed (different band, different body note)

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
