# Teacher Mode Normalization Spec

## Structure without templating — anti-fragment, platform diversity

**Status:** Canonical  
**Subordinate to:** [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md)  
**Audience:** Devs, content pipeline

Raw mined atoms are not runtime-ready. Normalization adds structural coherence and family diversity without prose scoring or LLM.

---

## 1. Pipeline order

```text
build_kb.py
↓
mine_kb_to_atoms.py
↓
assign band (STORY)
↓
identify_core_teachings.py   (cap 20, two-of-three rule)
↓
expand_story_atoms.py        (optional; short/low-band STORY)
↓
normalize_story_atoms.py
↓
normalize_exercise_atoms.py
↓
candidate review
↓
approval
↓
Arc-First compile
↓
check_structural_entropy.py  (CI gate)
↓
publish
```

---

## 2. STORY normalization

**Script:** `tools/teacher_mining/normalize_story_atoms.py`

- **structure_family:** One of `NARRATIVE`, `CASE_STUDY`, `PARABLE`, `DIALOGUE` (deterministic by `hash(atom_id) % 4`).
- **Length:** 120–450 words. Expand if &lt;120; compress at sentence boundary if &gt;450.
- **Tension:** If no friction/cost keyword, append one consequence sentence.
- **Teacher anchor:** If no `core:*` tag in body, append one sentence using atom tags or glossary.
- **Framing:** Optional author intro/outro from fixed set (rotation by hash).
- **Metadata:** `persona_overlay: true`, `topic_overlay: true`, `teacher_framed: true`.

---

## 3. EXERCISE normalization

**Script:** `tools/teacher_mining/normalize_exercise_atoms.py`

- **exercise_family:** One of `E1_BREATH`, `E2_REFLECTION`, `E3_MICRO_EXPERIMENT`, `E4_BODY_SCAN`, `E5_REFRAME` (deterministic by hash).
- **Length:** 90–280 words.
- **Clear instruction:** If no action verb, prepend setup sentence.
- **Time marker:** If missing, append minimal time instruction.
- **Closure:** If missing, append one closing line from fixed set.
- **Teacher context:** One sentence linking to core teaching (from tags) when teacher_id present.

---

## 4. Structural entropy CI

**Script:** `scripts/ci/check_structural_entropy.py`

**Inputs:** Compiled plan JSON, optional BookSpec. Only runs when `teacher_mode` and `teacher_id` are set.

**FAIL:**

- Any STORY atom &lt; 120 words.
- Any EXERCISE atom &lt; 90 words.
- Story structure_family concentration &gt; 60%.
- Exercise family concentration &gt; 60%.
- Unique core teaching anchors in book &lt; 4.

**WARN:**

- Family concentration 45–60%.
- Core anchors &lt; 6.

**Policy:** FAIL blocks build/publish; WARN allows build but flags for review.

---

## 5. Persona × Teacher matrix

**Config:** `config/catalog_planning/teacher_persona_matrix.yaml`

- **allowed_personas** / **disallowed_personas** per teacher.
- **preferred_locales**, **allowed_engines**.
- **constraints:** peak_intensity_limit, min_tps_per_chapter.
- **persona_overlays:** default_angle, preferred_story_style, locale_overlays per persona.

Planner (Stage 0 / portfolio) must restrict (teacher, persona, engine) to matrix.

---

## 6. Teacher Mode arc template (optional)

Arc YAML may include:

```yaml
teacher_mode: true
teacher_id: ahjan
teacher_presence_targets:
  min_tps_per_chapter: 5
  min_teacher_story_chapters: 4
  min_teacher_exercise_chapters: 5
  min_core_teaching_anchors: 8
chapter_intent:  # optional
  1: { intent_type: pattern_exposure, core_anchor: subtle_resistance }
  ...
```

Emotional curve and resolution_type remain per engine/arc author.

---

## 7. What normalization does not do

- No persona/topic/locale-specific text injection in atom body (that is book-level framing).
- No prose scoring, no sentiment, no embeddings.
- No rigid sentence-by-sentence templates; structural families and fixed variant sets only.

---

## 8. Still to do (whole system)

Normalization scripts (STORY/EXERCISE with structure_family, exercise_family, style IDs), structural entropy CI, and platform similarity CI are implemented. Remaining for the whole system (coverage enforcement, Gate #49, optional freebie/narrator) is in the canonical systems doc and planning status:

- [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md) — § Remaining to finish whole system
- [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md)
