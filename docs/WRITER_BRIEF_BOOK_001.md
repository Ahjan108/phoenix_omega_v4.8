# WRITER BRIEF — FULL BOOK ASSEMBLY TEST (Book_001)

**Primary proof path (existing pool):** persona `nyc_executives`, topic `self_worth`, engines `shame` and `comparison` — full pool BAND-tagged (40 STORY atoms); pipeline run for Book_001, Book_002, Book_003; see `artifacts/book_001.plan.json`, `book_002.plan.json`, `book_003.plan.json` and `artifacts/THREE_BOOK_STRESS_TEST.md`.

**Alternative path (when pool exists):** persona `gen_z_professional`, topic `self_worth`, engine `shame`, 6 chapters — use structure and rules below.

---

## Goal

Produce the strongest possible book using **only current inventory** for the chosen persona / topic / engine.

No new atoms. This validates the system, not volume.

---

## Locked parameters (gen_z 6-chapter variant)

| Parameter | Value |
|-----------|--------|
| Persona | gen_z_professional |
| Topic | self_worth |
| Engine | shame |
| Locale | nyc |
| Format | 6 chapters |
| Seed | invisible_correction_v1 |

---

## Current inventory (example — gen_z 6-chapter)

| Type | Count | Notes |
|------|-------|------|
| RECOGNITION | 3 | BAND 3, 4, 5 |
| MECHANISM_PROOF | 2 | BAND 3, 2 |
| TURNING_POINT | 1 | BAND 4 |
| EMBODIMENT | 1 | BAND 5 |
| REFLECTION | 3 | v01, v02, v03 |
| EXERCISE | 2 | weight_drop (90s), jaw_release (75s) |
| INTEGRATION | 4 modes | BODY-LANDED, COST-VISIBLE, QUESTION-OPEN, FMT |

**Production note:** For production, commission **one new exercise atom** (cool or warm band) so no single exercise exceeds 3 uses. weight_drop used 4 times in assembly test is acceptable for validation only; limit is 3 for production.

---

## Allowed

- Reorder and position atoms to form one coherent arc.
- Reuse one REFLECTION at most once (different chapter, different band context).
- Reuse one EXERCISE at most **twice** (max 3 appearances per book).
- Use integration modes per contract; STILL-HERE reserved for final chapter only.
- FMT endings on all non-final chapters where format allows.

---

## Not allowed

- Write new STORY / REFLECTION / EXERCISE / INTEGRATION atoms (until Book_001 is validated and scope unfrozen).
- Add new prose content.
- Change BAND or role of existing atoms.
- Manually bridge between chapters with new language.

---

## Target emotional arc (6-chapter example)

Band sequence: 2 → 3 → 4 → 5 → 4 → 3

- At least 3 distinct bands across the book.
- No more than 2 consecutive chapters with the same dominant band (per assembly contract).

---

## Slot structure per chapter (6-chapter compact)

STORY → REFLECTION → EXERCISE → INTEGRATION

No HOOK or SCENE in this short format. Chapter begins directly with STORY.

---

## Integration rules

- STILL-HERE: one use maximum, final chapter only.
- No two consecutive chapters with the same integration mode.
- FMT allowed on non–STILL-HERE chapters.

---

## Output

One ordered book plan: chapter → slot type → atom ID.

Deliver to product/ops for assembly. Do not deliver compiled prose; system assembles.

---

**Authority:** [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md). Shame engine: [talp/analyze_intake/WRITER_ONBOARDING_SHAME_ENGINE.md](../talp/analyze_intake/WRITER_ONBOARDING_SHAME_ENGINE.md). Assembly: [BOOK_001_ASSEMBLY_CONTRACT.md](BOOK_001_ASSEMBLY_CONTRACT.md).
