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
- Optional: `teacher_constraints.<teacher_id>.max_books_per_topic`, `max_books_per_persona` — topic/persona saturation guardrails (diversity only)

**Release cadence:** `max_books_per_wave`, `release_spacing_days`, and `max_books_per_brand_per_month` are **restored as fail-safe guardrails** in `brand_teacher_matrix.yaml` defaults. Release timing is driven by **week-by-week schedule** and **safe velocity** config; the scheduler fails hard if any brand/platform/week exceeds platform cap. See **§7** and `docs/RELEASE_VELOCITY_AND_SCHEDULE.md`.

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

## 7. Release Velocity and Week-by-Week Schedule

**Authority:** `config/release_velocity/safe_velocity.yaml`, `config/release_velocity/velocity_ramp.yaml`, `scripts/release/generate_weekly_schedule.py`. See **docs/RELEASE_VELOCITY_AND_SCHEDULE.md**.

- **Target:** 70–84 books per week per brand (publishing-house research). Stagger weekly amounts so they look organic.
- **Ramp:** Start with 1 series → build slowly to 90 days → grow by 30% to 6 months → over 60 days reach 70–84/wk per brand.
- **Schedule:** Week-by-week plan: user sees which books to upload each week. Generate with `generate_weekly_schedule.py` from a wave or candidates dir.
- **Safe velocity (platform):** Google Play (new 10–20/wk, established 25–50/wk), Findaway (new 5–15/wk, established 15–30/wk), Ximalaya (5–10/wk per verified account). Do not exceed these when assigning uploads.
- Old rules **decommissioned:** max 1 book per teacher per 14–21 days; max 6–8 per brand per month. No longer enforced; replaced by the schedule and safe velocity config.

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
- **Numeric caps:** Per-platform safe velocity (new vs established imprint/account) is in `config/release_velocity/safe_velocity.yaml` (Google Play Books, Findaway Voices, Ximalaya). No explicit platform cap was previously in repo; caps are now centralized there and respected when building the weekly schedule.

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

---

## 13. Scale and Cross-Account Risk Stance

**Do not assume "safe by default" at high throughput.** Multi-brand, multi-teacher scale can work only with **strict pacing, diversity, and monitoring**.

### What platforms mainly enforce

- **Duplication** — identical or confusingly similar metadata, low-effort/templated content.
- **Manipulative behavior** — bots, fake reviews, policy gaming.
- **Per-account quality** — metadata uniqueness, description/title variation, category spread.

Diversity controls (brand matrix, teacher_constraints, topic/persona saturation, diversity_guards) **help** and align with these signals.

### What remains risky at scale

- **Volume pattern** — e.g. 24 brands × 25 books/week is an extreme aggregate pattern even if each account stays within per-account caps.
- **Same N teachers everywhere** — a small, fixed set of teachers across all brands is a strong **catalog fingerprint**; platforms may or may not correlate accounts, but the pattern is identifiable.
- **Internal per-author guard** — `docs/audiobook_ops_manual.md` states: *"Same author name on > 50 titles released in < 90 days"* is a spam signal. At high volume per teacher this is exceeded unless author/teacher count is increased.

### Stance

- Treat **cross-account risk as non-zero**, not minimal. Do not claim "minimal spam risk" at 24×25/week with the same 12 teachers across all brands.
- **Keep** per-account hard caps (safe_velocity, matrix defaults) and add a **catalog-wide teacher-share cap** (e.g. in `diversity_guards.yaml`: `max_share_per_teacher`).
- **Increase** author/teacher diversity as volume rises (e.g. more teachers per brand or more brands per teacher so no single teacher dominates allocation).
- **Roll out by cohorts** — start with 1–3 brands at target velocity; watch rejection rates, Partner Center/dashboard alerts, and quality signals; then scale only when signals are clean.

### Implementation

- **Catalog-wide teacher cap:** `config/catalog_planning/diversity_guards.yaml` → `max_share_per_teacher` (e.g. 0.08 = 8% max of allocation from any one teacher). Enforced in `scripts/generate_full_catalog.py` when diversity guards run (locale-group or brand-matrix flow).
- **Per-author 90-day guard:** Operational guideline remains ≤ 50 titles per author/teacher per 90 days per account unless explicitly relaxed with monitoring. Scale author/teacher count so this is not exceeded at target monthly volume.
- **Rollout:** Document in `docs/RELEASE_VELOCITY_AND_SCHEDULE.md` — cohort-based rollout (1–3 brands first), monitor, then scale.
- **Network-level caps and audits:** See **docs/CATALOG_ARCHITECTURE_AT_SCALE.md**. Four strongest actionable items: (1) Cross-network teacher share — implemented via max_share_per_teacher; (2) Title/description template similarity — audit/cap required; (3) Keyword overlap per brand cluster — audit/cap required; (4) Same-day multi-account release bursts — stagger by brand/cohort in schedule and process. Treat that doc as operational checklist and risk heuristic, not confirmed platform policy.
