# WRITER BRIEF — FULL BOOK ASSEMBLY TEST (Book_001)

**Persona:** gen_z_professional
**Topic:** self_worth
**Engine:** shame
**Locale:** nyc
**Format:** 6 chapters
**Seed:** invisible_correction_v1

---

## Goal

Produce the strongest possible 6-chapter book using **only current inventory**.

No new atoms. This validates the system, not volume.

---

## Current Inventory

| Type | Count | IDs |
|------|-------|-----|
| RECOGNITION | 3 | v01 (BAND 3), v02 (BAND 4), v03 (BAND 5) |
| MECHANISM_PROOF | 2 | v01 (BAND 3), v02 (BAND 2) |
| TURNING_POINT | 1 | v01 (BAND 4) |
| EMBODIMENT | 1 | v01 (BAND 5) |
| REFLECTION | 3 | v01 (geometry), v02 (silence after), v03 (installment plan) |
| EXERCISE | 2 | weight_drop (90s), jaw_release (75s) |
| INTEGRATION | 4 modes | BODY-LANDED, COST-VISIBLE, QUESTION-OPEN, FMT |

---

## Allowed

- Reorder and position atoms to form one coherent arc
- Reuse one REFLECTION at most once (different chapter, different band context)
- Reuse one EXERCISE at most twice
- Use integration modes freely; STILL-HERE reserved for final chapter only
- FMT endings on all non-final chapters

## Not Allowed

- Write new STORY / REFLECTION / EXERCISE / INTEGRATION atoms
- Add new prose content
- Change BAND or role of existing atoms
- Manually bridge between chapters with new language

---

## Target Emotional Arc

Band sequence: 2 → 3 → 4 → 5 → 4 → 3

| Chapter | Target Band | Assigned Atom |
|---------|-------------|---------------|
| 1 | 2 | MECHANISM_PROOF v02 (Jonah/LinkedIn) |
| 2 | 3 | RECOGNITION v01 (Kayla/#client-launch) |
| 3 | 4 | RECOGNITION v02 (Marcus/Diane) |
| 4 | 5 | EMBODIMENT v01 (Sofia/mic) |
| 5 | 4 | TURNING_POINT v01 (Devin/elevator) |
| 6 | 3 | MECHANISM_PROOF v01 (Zoe/three moments) |

RECOGNITION v03 (Maya/performance review, BAND 5) is stranded at this scale. Do not force it into this arc. It anchors Book_002.

---

## Slot Structure Per Chapter

STORY → REFLECTION → EXERCISE → INTEGRATION

No HOOK or SCENE in this short format. Chapter begins directly with STORY.

---

## Reflection Assignment

| Chapter | Band | Reflection |
|---------|------|-----------|
| 1 | 2 (cool) | v03 — Installment Plan |
| 2 | 3 (cool-warm) | v01 — Geometry of Being Seen Wrong |
| 3 | 4 (warm) | v02 — Why the Silence After Is Louder |
| 4 | 5 (hot) | v02 — Why the Silence After Is Louder (second use — allowable at peak) |
| 5 | 4 (warm-descent) | v01 — Geometry of Being Seen Wrong (second use — institutional framing) |
| 6 | 3 (cool) | v03 — Installment Plan (second use — closes the arc) |

---

## Exercise Assignment

| Chapter | Exercise |
|---------|----------|
| 1 | weight_drop |
| 2 | weight_drop |
| 3 | jaw_release |
| 4 | jaw_release |
| 5 | weight_drop |
| 6 | weight_drop |

Note: weight_drop appears four times. Acceptable for assembly test. Third unique exercise needed for production expansion.

---

## Integration Mode Assignment

| Chapter | Mode | Constraint |
|---------|------|-----------|
| 1 | BODY-LANDED | — |
| 2 | COST-VISIBLE | — |
| 3 | QUESTION-OPEN | — |
| 4 | STILL-HERE | Final peak. One use only. |
| 5 | COST-VISIBLE | Not consecutive with Ch 2 — Ch 3 breaks the run |
| 6 | FMT | Open loop. Book ends without resolution. |

---

## Output

One ordered book plan: chapter → slot type → atom ID.

Deliver to: `get_these/gen_z_professional/self_worth/shame/`

Do not deliver compiled prose. System assembles.
