# Teacher Portfolio Planning Spec

## Anti-Spam Layer: Brand × Teacher × Release Safety

**Status:** Canonical  
**Subordinate to:** [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md)  
**Audience:** Catalog planning, platform safety (Google Play, Spotify, Apple, etc.)

Avoid platform spam flags by controlling release velocity, metadata diversity, and structural variation across teacher books. Planning layer only — no content change.

---

## 1. Risk: Platforms Flag Teacher-Scaled Catalogs

Stores (Google Play Books, Spotify, Apple Books, Findaway) may flag:

- Highly similar titles
- Repeated subtitle patterns
- Same structure across many books
- Same chapter names / length distribution
- Overlapping preview content
- Too many books from same brand in short time
- "Guru templating" (same arc, swap teacher name)

Teacher Mode must **not** look like: "Anxiety Through Teacher A", "Anxiety Through Teacher B", same arc/structure. That gets flagged fast.

---

## 2. Brand × Teacher Segmentation

**Rule:** Each teacher belongs to a **primary brand** (and optionally one secondary). Limit topic and persona focus per teacher so the catalog doesn’t look like a content farm.

| Teacher   | Primary brand   | Topic focus        | Persona focus   |
|-----------|------------------|--------------------|-----------------|
| Ajahn X   | Stillness Press | shame, anxiety     | executives      |
| Dr. Y     | Cognitive Clarity | overthinking     | Gen Z           |
| Lama Z    | Presence Works  | grief              | caregivers      |

Brand identity must align with teacher philosophy. No mixing wildly divergent teachers under one imprint unless the brand explicitly supports it.

---

## 3. Brand Matrix Config

**File:** `config/catalog_planning/brand_teacher_matrix.yaml`

- `brands.<brand_id>.teachers` — list of teacher ids
- `brands.<brand_id>.max_books_per_wave` — cap per release wave
- `brands.<brand_id>.release_spacing_days` — minimum days between releases
- Optional: `teacher_constraints.<teacher_id>.max_books_per_topic`, `max_books_per_persona` — topic/persona saturation guardrails

This enforces controlled release velocity and brand coherence.

---

## 4. Topic Saturation Guardrail

- **max_books_per_teacher_per_topic** — e.g. 4. Prevents 15 books on "anxiety" under the same teacher.
- **max_books_per_teacher_per_persona** — e.g. 5. Prevents 20 "executive anxiety" variants.

Expand across topics and personas slowly.

---

## 5. Metadata Entropy Guardrail

Across teacher books, enforce variation in:

- Title syntax (different template families per teacher)
- Subtitle construction
- Hook framing
- Description angle

**metadata_style_family** per teacher so Teacher B does not use the same syntactic family as Teacher A. Prevents catalog-wide duplication.

---

## 6. Teacher Portfolio Planner

**Module:** `phoenix_v4/planning/teacher_portfolio_planner.py`

**Purpose:** Plan which teacher, topic, persona, brand, and release wave — in what order — **before** BookSpec generation.

**Inputs (e.g. wave plan):**

- `wave_id`, `teachers[]`, `total_books`, `spacing_days`

**Outputs:**

- Ordered list of (teacher_id, topic_id, persona_id, format_id, arc_id) that respects:
  - Brand matrix (teachers per brand, max per wave)
  - Topic/persona saturation
  - Release spacing (no back-to-back same-teacher)
  - Allowed topics/engines per teacher (from registry)

---

## 7. Release Velocity Rules

- Max 1 book per teacher per 14–21 days (configurable).
- Max 6–8 per brand per month (configurable).
- If a wave violates velocity → hard block.

---

## 8. Structural Diversity Rule

Across a teacher’s catalog:

- Arc variety, engine variety, format variety
- Chapter count variation, exercise density variation

If too many books share same arc, same chapter count, same band pattern → flag. Protects against "template farm" detection.

---

## 9. Cross-Teacher Similarity Check

- Compare slot order, arc band sequence, exercise placement across different teachers.
- If structural similarity > threshold (e.g. 80%) between two teachers’ books → block or flag.
- Prevents "same book, different guru."

---

## 10. Platform-Specific Notes

- **Spotify / Apple (audio):** Avoid rapid catalog dumps; duration variability (±8%); different narrator/voice per teacher when possible; cover art structural differences.
- **Google Play:** Vary preview segments, rotate excerpt chapters, stagger release waves; avoid excessive similar metadata.

---

## 11. Implementation

- **Config:** `config/catalog_planning/brand_teacher_matrix.yaml` (example provided).
- **Planner:** `phoenix_v4/planning/teacher_portfolio_planner.py` — reads matrix + teacher registry, consumes wave plan, outputs allocated (teacher, topic, persona) list with spacing.
- **CI / gate:** Before wave release, run portfolio planner (or validate plan against matrix); run teacher integrity dashboard; no report → no release.

---

## 12. What This Does NOT Do

- Does not write or alter book content
- Does not change arc or format at runtime
- Does not score prose or sentiment

Only **planning-layer** constraints to keep catalog diversity and platform safety.
