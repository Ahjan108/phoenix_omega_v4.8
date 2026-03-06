# Writer reading list: stories and atoms

**Purpose:** Single list of every file a writer needs to understand to write STORY atoms for the whole system (funnel, Teacher Mode, regular persona/topic).  
**Use:** Hand this to the writer with the repo; read in the order below.

**If the full Writer Spec doesn’t load:** Give the writer **docs/WRITER_SPEC_EXTRACT_FOR_ATOMS.md**. It contains the exact text for: five STORY role types (for `role:`), §4.3 STORY, §6 Four Story Rules (Misfire Tax, Silence Beat, Never-Know, Interrupt), §3 TTS Prose Law, §12 TTS formal gates (sentence caps, T01–T07), and which atom-level fields are required vs optional.

---

## Must read first (core story + prose)

| Order | File | What it covers |
|-------|------|----------------|
| 1 | **STORY_TYPES_AND_STRUCTURES.md** (repo root) | Story origin (true vs composite), five story types, structure templates, principle-teacher rule, five-element check, schema. Primary story authority. |
| 2 | **specs/PHOENIX_V4_5_WRITER_SPEC.md** | Voice, TTS rules, six atom types; §4.3 STORY and §6 Four Story Rules (Misfire Tax, Silence Beat, Never-Know, Interrupt). Prose and atom rules. **Backup:** [docs/WRITER_SPEC_EXTRACT_FOR_ATOMS.md](./WRITER_SPEC_EXTRACT_FOR_ATOMS.md) if the full spec won’t open. |
| 3 | **docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md** | Specificity, cost, conflict, insight pivot, residual echo. Quality bar for every STORY. |

---

## Teacher Mode (if writing teacher-scoped atoms)

| Order | File | What it covers |
|-------|------|----------------|
| 4 | **specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md** | Workflow: onboard teacher, check gaps, gap-fill, approve; where atoms live (candidate_atoms vs approved_atoms); content-team rules. |
| 5 | **specs/TEACHER_MODE_STRUCTURAL_SPEC.md** | Author voice (interpreter, not originator), Pre-Intro chapter, TPS, framing sentences, exercise attribution. |
| 6 | **specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md** | belief_flip STORY pattern (§3), invisible_script HOOK, SCENE micro-failure. Optional but useful for Band 3–4 stories. |

---

## Funnel (if writing Email 3 / Proof Loop stories)

| Order | File | What it covers |
|-------|------|----------------|
| 7 | **specs/FUNNEL_AND_BOOK_COPY_WRITER_SPEC.md** | Proof Loop, Email 3 story format (Before/Practice/After, 120–150 words), composite disclaimer, where to put stories (`funnel/<hub>/stories/<topic>.md`). |

---

## Example STORY atoms (exact YAML format)

**Path:** `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/STORY/`

Open any file in that folder to match the exact YAML structure. Examples:

- **ahjan_STORY_007_mined.yaml** — Mined atom (short body, source_refs, synthesis_method).
- **ahjan_STORY_003_mined.yaml** — Mined with longer body and multiple source_refs.
- **SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/STORY/junko_STORY_007.yaml** — Authored atom (no source_refs; body as multi-line `|`).

**Minimal format (required):**

```yaml
atom_id: <teacher_id>_STORY_<NNN>   # e.g. ahjan_STORY_012
body: |
  Your prose here. Third-person present. Named character, specific moment, cost, no tidy resolution unless direct_teaching.
band: 1 | 2 | 3 | 4 | 5
teacher:
  teacher_id: ahjan
  source_refs: []                  # [] for authored; list of {doc_id, span, quote_hash} for mined
  synthesis_method: authored_v1    # or kb_mine_v1
```

**Optional (STORY_TYPES_AND_STRUCTURES):** Add when you use the story-type system:

```yaml
story_origin: true_story | composite
story_type: parable | direct_teaching | character_study | atmospheric | recognition_exchange
```

**Mined example (with source_refs):**

```yaml
atom_id: ahjan_STORY_007_mined
body: The story of the Zen master turned samurai illustrates how one can transition...
teacher:
  teacher_id: ahjan
  source_refs:
  - doc_id: 'raw/BD Blog - Personal Power....rtf'
    span: [3627, 4214]
    quote_hash: 9af7373a4766b61f
  synthesis_method: kb_mine_v1
band: 3
```

**Authored example (Junko-style, no teacher in scene):**

```yaml
atom_id: junko_STORY_007
body: |
  Yumi has always needed permission. Permission to rest, permission to want things...
  One morning her therapist asks: "Who are you waiting for permission from?"
  ...
band: 4
teacher:
  teacher_id: junko
  source_refs: []
  synthesis_method: authored_v1
```

---

## Reference (where things live + config)

| File | What it covers |
|------|----------------|
| **config/teachers/teacher_registry.yaml** | All 12 teachers, `display_name`, `allowed_topics`, `disallowed_topics`. Use for scope. |
| **config/catalog_planning/canonical_personas.yaml** | Canonical persona IDs (e.g. tech_finance_burnout, healthcare_rns, gen_z_professionals). |
| **config/catalog_planning/canonical_topics.yaml** | Canonical topic IDs (anxiety, burnout, shame, self_worth, etc.). |
| **funnel/burnout_reset/stories/burnout.md** | Example funnel story file (Before/Practice/After, story_id blocks). |
| **funnel/burnout_reset/stories/anxiety.md** | Same for anxiety hub. |
| **SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/STORY/** | Example Teacher Mode STORY atoms (one YAML per atom). Open any `.yaml` to copy format. |
| **SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/STORY/** | Authored STORY examples (character study, no teacher in scene). |
| **SOURCE_OF_TRUTH/teacher_banks/ahjan/doctrine/story_helpers.yaml** | Ahjan transformation_patterns, band_templates (if writing for ahjan). |

---

## Optional / as needed

| File | What it covers |
|------|----------------|
| **specs/WRITER_DEV_SPEC_PHASE_2.md** | Band targets (e.g. Band 3 ≥4, Band 4 ≥3 per 8-chapter pool), coverage dashboard, slot pool counts. |
| **docs/authoring/AUTHOR_ASSET_WORKBOOK.md** | Pen-name author assets (bio, why_this_book, etc.) if writer also does author copy. |
| **docs/WRITER_COMMS_SYSTEMS_100.md** | What “100%” means for writers; systems view. |
| **ONBOARDING.md** | Repo-level onboarding (vision, DOCS_INDEX, Arc-First, Writer Spec). |
| **specs/TEACHER_MODE_V4_CANONICAL_SPEC.md** | Dev spec for Teacher Mode; reference if writer needs pipeline/compile context. |
| **specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md** | Arc-First system authority; reference only unless writer touches arcs. |

---

## Quick path list (copy-paste)

```
STORY_TYPES_AND_STRUCTURES.md
specs/PHOENIX_V4_5_WRITER_SPEC.md
docs/WRITER_SPEC_EXTRACT_FOR_ATOMS.md   # use if full Writer Spec won't load: §4.3, §6, TTS, five role types
docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md
specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md
specs/TEACHER_MODE_STRUCTURAL_SPEC.md
specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md
specs/FUNNEL_AND_BOOK_COPY_WRITER_SPEC.md
config/teachers/teacher_registry.yaml
config/catalog_planning/canonical_personas.yaml
config/catalog_planning/canonical_topics.yaml
funnel/burnout_reset/stories/burnout.md
funnel/burnout_reset/stories/anxiety.md
SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/STORY/
SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/STORY/
SOURCE_OF_TRUTH/teacher_banks/ahjan/doctrine/story_helpers.yaml
```

---

*Last updated to match the writer story brief and Teacher Mode + funnel scope.*
