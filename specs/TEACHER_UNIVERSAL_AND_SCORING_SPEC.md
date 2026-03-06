# Teacher Universal Scope and Topic/Persona Scoring Spec

**Purpose:** Every teacher can teach every topic and every persona. Fit is expressed by **scores** (teacher×topic, teacher×persona). Scores inform adaptation (LLM or writer), the EI v2 system, and volume/format (weaker fit → fewer books or shorter formats).

**Authority:** This spec. Subordinate to [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md).  
**Audience:** Dev, content, catalog planning.

---

## 1. Universal scope

- **Every teacher can teach every canonical topic and every canonical persona.** No hard allowlists that restrict (teacher, topic) or (teacher, persona) at compile time.
- **Hard blocks remain:** `disallowed_topics` (e.g. manifestation, get_rich_quick) and `disallowed_personas` (if any) still block. Principle: allow by default; block only where explicitly disallowed.
- **Adaptation:** Content for (teacher, topic, persona) is adapted by:
  - **LLM** (gap-fill, expansion) when score and doctrine support it, or
  - **Writer** when stronger prose or doctrinal fidelity is required.
- Scores guide *how much* to publish and *which format* (long vs short), not *whether* a combination is allowed.

---

## 2. Teacher × topic and teacher × persona scores

### 2.1 Config source

**File:** `config/catalog_planning/teacher_topic_persona_scores.yaml`

- **Per teacher:** Optional `topic_scores` (topic_id → float 0–1) and `persona_scores` (persona_id → float 0–1).
- **Meaning:** Higher score = stronger fit (more doctrine, more content, better alignment). Lower score = weaker fit; system will publish less or prefer shorter formats for that pair.
- **Default when missing:** If a (teacher, topic) or (teacher, persona) pair has no score, treat as **0.5** (neutral). So all pairs are allowed; scores only tune volume and format.

### 2.2 Composite score for (teacher, topic, persona)

For allocation and format choice, use a **composite score** per (teacher, topic, persona), e.g.:

- `composite = (topic_score + persona_score) / 2`, or
- `composite = min(topic_score, persona_score)` (conservative), or
- Weighted average from config.

Config may define `composite_formula: average | min | weighted` and optional weights.

### 2.3 Score bands and policy

| Band   | Score range | Policy |
|--------|-------------|--------|
| Strong | ≥ 0.7       | Full allocation; any format (long preferred). |
| Medium | 0.4 – 0.7   | Normal allocation; prefer standard formats. |
| Weak   | &lt; 0.4     | Publish fewer books for this (teacher, topic, persona); prefer **shorter formats** (e.g. F002 over F006). |

Exact thresholds (e.g. 0.4, 0.7) are configurable in the same file or in `brand_teacher_matrix` / teacher_constraints.

---

## 3. Volume and format

- **Weaker fit → fewer books:** Catalog/portfolio planner uses scores to cap or down-weight allocation for low-score (teacher, topic, persona) pairs (e.g. `max_books_per_teacher_topic_persona` or sampling weight).
- **Weaker fit → shorter format:** When composite score is below threshold, format selector (or allocation) prefers shorter formats (e.g. F002, short_book) over long (e.g. F006, deep_book_6h). **Implementation:** `scripts/generate_full_catalog.py` loads `weak_fit_prefer_shorter_format` and `weak_fit_max_books_per_triple` from the scores config; for each allocation with `score_band == "weak"` it prefers arcs whose format is F001/F002/F003 when resolving the master arc, and caps weak (teacher, topic, persona) triples to at most `weak_fit_max_books_per_triple` books.

---

## 4. EI v2 integration

- **Input:** EI v2 (Enlightened Intelligence) receives or reads **teacher×topic×persona scores** (and composite) so it can:
  - **Adapt expectations:** E.g. domain_embeddings or thesis alignment can weight by fit; lower fit may relax or tighten thresholds by policy.
  - **Adaptation hints:** Gap-fill or writer tooling can request “adapt this teacher to this topic/persona” and use score to choose prompt or strategy (e.g. “strong fit” vs “adapt with care”).
  - **Learning over time:** EI v2 learner (`artifacts/ei_v2/learned_params.json`, feedback) can consume outcomes (e.g. promotion, listen-through) per (teacher, topic, persona) and suggest score updates or format preferences. Scores can be updated manually (config) or via a future “score update” pipeline from learner output.
- **No hard gate:** EI v2 does not *block* a book based on score; it uses scores to adapt and to recommend, and to learn.

---

## 5. Writer and LLM adaptation

- **Writer:** When writing or reshaping atoms for (teacher, topic, persona), the writer uses score (and doctrine) to adapt voice, examples, and persona overlay. Weak score may require more explicit adaptation (e.g. “apply this teaching to burnout for healthcare_rns”).
- **LLM (gap-fill, expansion):** When generating candidates for (teacher, topic, persona), the pipeline can pass score (or band) so the LLM adapts tone, examples, and depth. Strong fit → more direct use of doctrine; weak fit → more framing and application to the target topic/persona.

---

## 6. Config and schema summary

| Item | Location | Purpose |
|------|----------|---------|
| Teacher registry | `config/teachers/teacher_registry.yaml` | `allowed_topics` = all canonical (or omit = all). `disallowed_topics` only for hard blocks. |
| Teacher persona matrix | `config/catalog_planning/teacher_persona_matrix.yaml` | `allowed_personas` empty = all personas allowed. `allowed_engines` can remain or be relaxed per policy. |
| Scores | `config/catalog_planning/teacher_topic_persona_scores.yaml` | Per-teacher `topic_scores`, `persona_scores`; optional `composite_formula`, `score_bands`, `format_preference_by_band`. |
| EI v2 | `config/quality/ei_v2_config.yaml` | Optional `teacher_topic_persona_scores_path`; learner can suggest score updates. |
| Portfolio / format | `phoenix_v4/planning/teacher_portfolio_planner.py`, `scripts/generate_full_catalog.py` | Planner attaches composite_score/score_band to allocations; catalog script caps weak triples and prefers F001/F002/F003 arcs when weak. |

---

## 7. Migration

- **Backward compatibility:** If `teacher_topic_persona_scores.yaml` is missing, all scores are treated as 0.5 (neutral); allocation and format unchanged from “all allowed” behavior.
- **Existing allowed_topics / allowed_personas:** Replace with “all” (see §6): registry lists all canonical topics per teacher (or omit for “all”); matrix uses empty allowed_personas to mean “all”. Validation logic: empty allowed_personas = allow all; empty allowed_topics in registry = use canonical_topics in planner.

---

## 8. Files to add or change

| Action | File |
|--------|------|
| Add | `config/catalog_planning/teacher_topic_persona_scores.yaml` (schema + optional per-teacher scores, bands, formula) |
| Update | `config/teachers/teacher_registry.yaml` — set every teacher’s `allowed_topics` to full canonical list (or add “all” convention and planner change) |
| Update | `config/catalog_planning/teacher_persona_matrix.yaml` — set `allowed_personas: []` per teacher to mean “all”; update validation to treat empty as “all allowed” |
| Update | `phoenix_v4/planning/teacher_matrix.py` — allow empty `allowed_personas` = all personas allowed |
| Update | `phoenix_v4/planning/teacher_portfolio_planner.py` — build topic_pool from canonical_topics when teacher has no allowed_topics or all_topics; use scores to weight/cap allocation and prefer short format for low score |
| Update | `config/quality/ei_v2_config.yaml` — optional `teacher_topic_persona_scores_path`; document learner → score update path |
| Update | `specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md` — reference this spec; writer adapts all topics/personas using scores |
