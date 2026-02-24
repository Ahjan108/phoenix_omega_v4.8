# Book_001 post-mortem

**Run:** Pipeline produced `artifacts/book_001.plan.json` with 12 chapters (F006 + standard_book), persona `nyc_executives`, topic `self_worth`, seed `book001`. STORY slots filled from current inventory (shame + comparison); HOOK/SCENE/REFLECTION/EXERCISE/INTEGRATION are placeholders.

---

## System

- **Deterministic?** Yes. Same `--topic self_worth --persona nyc_executives --seed book001 --runtime-format standard_book --structural-format F006` → same `plan_hash` and `atom_ids`.
- **Manual intervention?** Format was constrained so the book fits the atom pool: without `--runtime-format standard_book --structural-format F006`, Stage 2 chose F001 (90 chapters), which would have exhausted STORY atoms and produced placeholders for later chapters.
- **Slot authority?** Yes. Assembly pulled STORY only from `atoms/<persona>/<topic>/<engine>/CANONICAL.txt`; slot_definitions from FormatPlan; no extra slots.

---

## Content

- **Arc?** Plan has 12 STORY atoms (mix of RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT) across shame and comparison engines. Arc is ordering-dependent; no editorial reorder was applied.
- **Repetition?** No duplicate atom IDs in the plan.
- **Band diversity?** Done. All 40 STORY atoms (shame + comparison) have explicit BAND; target distribution per engine 1:1, 2:4, 3:7, 4:5, 5:3. Book_001, Book_002, and Book_003 pass emotional curve validation (seeds book001, book002, book003). See `artifacts/THREE_BOOK_STRESS_TEST.md`.
- **Ship?** As a proof-of-execution artifact, yes. For shippable product, fill non-STORY slots (HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION) from pools when available; curve and BAND diversity are in place.

---

## Next

- **If it works →** Expand inventory or add persona/topic; consider filling REFLECTION/EXERCISE/INTEGRATION from pools.
- **If it doesn’t →** Fix atom pool (e.g. BAND annotations) or pipeline, then re-run. Do not add formats or governance until this one book is validated.

**Command used for this run:**

```bash
python3 scripts/run_pipeline.py --topic self_worth --persona nyc_executives --seed book001 \
  --out artifacts/book_001.plan.json --runtime-format standard_book --structural-format F006
```
