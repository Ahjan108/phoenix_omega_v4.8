# Unified Personas — Book Readiness Analysis

**Purpose:** What is ready to write books today, what is missing, and what is left for the writing team so the system can write books for **all** active personas.  
**Sources:** [unified_personas.md](../unified_personas.md) (source of truth), docs/, specs/, config/, atoms/, BOOK_001_*, WRITER_COMMS_SYSTEMS_100, GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.

**100% atoms sim test:** To assert that there are atoms to make **all** books for all personas and all topics, run from repo root: `python3 tests/test_atoms_coverage_100_percent.py`. Exit 0 only when every (persona, topic, engine) in the catalog has a non-empty STORY pool. See [docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md](./TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md) §7.

---

## 1. What “unified_personas” refers to

- **Source of truth:** [unified_personas.md](../unified_personas.md) is the single source of truth for **active** personas and **active** topics. It defines **10 active personas** and **12 active topics**; pipeline, config, and catalog planning must use only those IDs.
- **Active personas** (from unified_personas.md Part 1): `millennial_women_professionals`, `tech_finance_burnout`, `entrepreneurs`, `working_parents`, `gen_x_sandwich`, `corporate_managers`, `gen_z_professionals`, `healthcare_rns`, `gen_alpha_students`, `first_responders`.
- **Active topics** (from unified_personas.md Part 2): `overthinking`, `burnout`, `boundaries`, `self_worth`, `social_anxiety`, `financial_anxiety`, `imposter_syndrome`, `sleep_anxiety`, `depression`, `grief`, `compassion_fatigue`, `somatic_healing`.
- **Inactive (legacy):** Personas such as `nyc_executives`, `educators`, `sf_founders`, `smb_owners`, `parents_teens` are **inactive**; atoms or config may still reference them for migration (e.g. tech_finance_burnout migrates_from nyc_executives). Identity aliases map variants to canonical dir names.
- **Config:** `config/catalog_planning/canonical_personas.yaml` and `canonical_topics.yaml` should align with unified_personas.md.

Design foundation (in unified_personas.md Part 0):
- **Atom roles (story arc):** RECOGNITION → MECHANISM_PROOF → TURNING_POINT → EMBODIMENT.
- **Canonical = mechanism truth;** persona templates = voiced expression per listener.
- **Scaling:** Templates = Topics × Engines × Personas × Roles; see unified_personas.md for catalog math (e.g. 10×12 production grid, 1,008 titles).

---

## 2. What is ready to write books (today)

### 2.1 One proven book lane (STORY-only, with placeholders elsewhere)

| Item | Status |
|------|--------|
| **Lane** | `nyc_executives × self_worth × (shame + comparison)` |
| **STORY pool** | 40 atoms (20 shame + 20 comparison), all BAND-tagged; roles RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT |
| **Format** | F006, 12 chapters, `[STORY, REFLECTION, EXERCISE, INTEGRATION]` per chapter |
| **Books** | Book_001, Book_002, Book_003 (seeds book001–book003) — compile and emotional curve **PASS** |
| **QA render** | `artifacts/books_qa/book_001.txt` — STORY prose present; **REFLECTION, EXERCISE, INTEGRATION render as `[Placeholder: REFLECTION]` etc.** |

So: the **pipeline** runs end-to-end for this lane; **only STORY slots are filled with real prose**. All other slot types are placeholders until pools exist.

### 2.2 STORY atom coverage (atoms/<persona>/<topic>/<engine>/CANONICAL.txt)

- **All 10 active personas** have book-writing content in `atoms/`: each has **122 or 136 CANONICAL.txt files** (STORY and, where present, REFLECTION, EXERCISE, INTEGRATION, HOOK, SCENE, COMPRESSION). The three with 136 files (gen_z_professionals, healthcare_rns, gen_alpha_students) include extra legacy topic/engine combos (e.g. anxiety, financial_stress, courage).
- **Legacy personas** (nyc_executives, educators) still have atoms on disk but are **inactive** per unified_personas.md; the pipeline uses the 10 active personas from canonical_personas.yaml.
- **Topics:** active 12 (overthinking, burnout, boundaries, self_worth, social_anxiety, financial_anxiety, imposter_syndrome, sleep_anxiety, depression, grief, compassion_fatigue, somatic_healing); legacy bindings may include anxiety, financial_stress, courage (see `config/topic_engine_bindings.yaml`).
- **Engines** vary by topic. Each CANONICAL file contains atoms with role headers and BAND metadata (where tagged).

So: **every active persona has atom content for book writing**; STORY is the slot type most broadly populated; REFLECTION/EXERCISE/INTEGRATION (and HOOK/SCENE where used) exist for some persona×topic lanes and placeholders are used elsewhere until pools are added.

**100% atoms coverage sim test:** The test `tests/test_atoms_coverage_100_percent.py` enforces that **every** (persona, topic, engine) in the catalog (from `canonical_personas.yaml` × `topic_engine_bindings.yaml`) has `atoms/{persona}/{topic}/{engine}/CANONICAL.txt` existing and non-empty (at least one valid STORY atom). It fails (BLOCKER) if any tuple is missing a STORY pool and prints the missing paths; it **reports** (does not fail) pools below `min_story_pool_size` from `config/gates.yaml` (RED in coverage report). Run: `python3 tests/test_atoms_coverage_100_percent.py` or `pytest tests/test_atoms_coverage_100_percent.py -v`. Authority: **docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md** §7.

### 2.3 Content scale (translation and adding personas)

| Metric | Value |
|--------|--------|
| **Total words** (CANONICAL*.txt under atoms/) | **~4.1M** |
| **Total characters** | ~25.7M |
| **Total CANONICAL files** | **~1,911** |
| **Words per active persona** | ~240k–420k (average ~370k) |

Use these for translation cost (e.g. per-word or per-token) and for sizing a new persona (~250k–400k words and ~120–140 files if mirroring current coverage).

### 2.4 System and spec readiness

- **Arc-first, Stage 1→2→3→6:** Implemented (BookSpec, FormatPlan, CompiledBook, prose_resolver, render_plan_to_txt).
- **Writer Spec (PHOENIX_V4_5_WRITER_SPEC):** Six atom types, TTS rules, persona/topic/engine gates, §23–§25.
- **Config:** topic_engine_bindings.yaml, topic_skins.yaml, identity_aliases.yaml, canonical_personas/topics.
- **Validation:** BOOK_001_READINESS_CHECKLIST, emotional curve, engine purity (e.g. shame), TTS/compliance.
- **Golden Phoenix upgrade guide:** Micro-stakes, environmental cues, persona specificity score, promotion workflow (provisional_template → confirmed).

---

## 3. Atom types — where they live and what exists

| Atom type | Source path | Ready? | Notes |
|-----------|-------------|--------|-------|
| **STORY** | `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` | **Yes for all 10 active personas** | Part of ~1,911 CANONICAL files; roles RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT; BAND required. |
| **REFLECTION** | `atoms/<persona>/<topic>/REFLECTION/CANONICAL.txt` | **Only 1** | gen_z_professionals/anxiety only. |
| **EXERCISE** | `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` | **Only 1** | gen_z_professionals/anxiety only. |
| **INTEGRATION** | `atoms/<persona>/<topic>/INTEGRATION/CANONICAL.txt` | **No** | No INTEGRATION CANONICAL.txt under atoms/. |
| **HOOK** | `atoms/<persona>/<topic>/HOOK/CANONICAL.txt` | **Only 1** | gen_z_professionals/anxiety only. |
| **SCENE** | `atoms/<persona>/<topic>/SCENE/CANONICAL.txt` | **Only 1** | gen_z_professionals/anxiety only. |
| **COMPRESSION** | `SOURCE_OF_TRUTH/compression_atoms/approved/<persona>/<topic>/*.yaml` | **Only 1 lane** | gen_z_professional/burnout only (2 YAMLs). |

So: **STORY is the only slot type broadly populated across all 10 active personas.** Non-STORY slot types (REFLECTION, EXERCISE, INTEGRATION, HOOK, SCENE) exist for only a subset of persona×topic lanes (e.g. gen_z_professionals × anxiety). The compiler emits **placeholders** when a pool is empty unless `require_full_resolution=True`. Every active persona has sufficient STORY (and other slots where filled) to compile books; full books without placeholders require REFLECTION/EXERCISE/INTEGRATION pools per (persona, topic) you ship.

---

## 4. What is missing for “books for all personas”

### 4.1 Non-STORY pools (main gap)

For the system to **render full books without placeholders** for every canonical persona × topic:

- **REFLECTION** — need `atoms/<persona>/<topic>/REFLECTION/CANONICAL.txt` for each (persona, topic) you ship.
- **EXERCISE** — same.
- **INTEGRATION** — same; currently **no** INTEGRATION pool anywhere.
- **HOOK / SCENE** — only if the chosen format includes these slots (e.g. standard_book with HOOK, SCENE).

**Active personas × topics:** 10 × 12 = 120 (persona, topic) pairs in the catalog; only gen_z_professionals × anxiety has any non-STORY atoms. So **119 persona×topic combinations** lack REFLECTION, EXERCISE, INTEGRATION (and HOOK/SCENE where required) for full books without placeholders.

### 4.2 STORY depth and BAND diversity

- Where STORY files **exist**, some lanes may have too few atoms per role or poor BAND spread for emotional-curve rules (≥3 distinct BANDs, no more than 3 consecutive same).
- Where STORY files **don’t exist** for an allowed (topic, engine) pair, that lane cannot compile STORY slots (would need new CANONICAL.txt per engine).
- **Legacy personas** (e.g. educators, nyc_executives) may have atoms on disk but are **inactive** per unified_personas.md; asset planning and validation use the active list from unified_personas.md / canonical_personas.yaml.

### 4.3 Compression atoms

- Formats that include COMPRESSION (e.g. F006) need `SOURCE_OF_TRUTH/compression_atoms/approved/<persona>/<topic>/*.yaml` (40–120 words, one insight, Writer Spec §25).
- Only **gen_z_professional/burnout** has compression atoms. All other persona×topic lanes that use COMPRESSION need these.

### 4.4 Arcs

- Books use `config/source_of_truth/master_arcs/` (e.g. `persona__topic__engine__format.yaml`).
- Not every persona×topic×engine×format has an arc; missing arcs can block or constrain compilation depending on pipeline config.

### 4.5 Golden Phoenix and author side

- **Micro-stakes research notes** per persona×topic (GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE §10) — needed before writing so atoms feel persona-specific.
- **Persona specificity score ≥ 0.70** and **repetition entropy** — many STORY atoms may still be `provisional_template` until reviewed and promoted.
- **Author registry and assets** — only 4 authors; author-bound books need author_id, positioning_profile, and assets (bio, why_this_book, etc.) for each author.

---

## 5. What is left for the writing team (so the system can write books for all personas)

Prioritized list of **concrete deliverables** so every canonical (and optionally educators) persona×topic can produce full books (no placeholders):

1. **REFLECTION, EXERCISE, INTEGRATION per (persona, topic)**  
   - Add `atoms/<persona>/<topic>/REFLECTION/CANONICAL.txt`, same for EXERCISE and INTEGRATION, for every persona×topic you intend to ship.  
   - Follow Writer Spec §§4–8 (sentence caps, no questions, body anchors, TTS-safe).  
   - REFLECTION/EXERCISE reuse rules: max 2 per REFLECTION, max 3 per EXERCISE per book (BOOK_001_READINESS_CHECKLIST); pool size must support that.

2. **HOOK and SCENE where the format requires them**  
   - For formats that include HOOK/SCENE, add `atoms/<persona>/<topic>/HOOK/CANONICAL.txt` and `.../SCENE/CANONICAL.txt` for the same (persona, topic) set.

3. **STORY pool completeness and BAND tagging**  
   - For each (persona, topic, engine) you ship: ensure STORY CANONICAL.txt exists and has enough atoms per role and **explicit BAND 1–5** with a good spread (e.g. 1:1, 2:4, 3:7, 4:5, 5:3 per engine) so emotional curve validation passes.  
   - Fill any missing (persona, topic, engine) lanes per `topic_engine_bindings.yaml`.

4. **Compression atoms for formats that use COMPRESSION**  
   - For each (persona, topic) on those formats: add 40–120 word, one-insight-only YAMLs under `SOURCE_OF_TRUTH/compression_atoms/approved/<persona>/<topic>/` (Writer Spec §25).

5. **Micro-stakes research notes and Golden Phoenix upgrade**  
   - Per persona×topic: write and approve micro-stakes research note (GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE §10) before drafting.  
   - Score STORY/SCENE atoms for persona specificity (≥0.70), check repetition entropy, and promote from `provisional_template` to `confirmed` where they pass.

6. **Arcs**  
   - Author or validate master arcs for each persona×topic×engine×format you plan to ship (ARC_AUTHORING_PLAYBOOK, emotional_role_sequence, etc.).

7. **Active vs legacy personas**  
   - Active personas and topics are defined in [unified_personas.md](../unified_personas.md). Ensure `canonical_personas.yaml` and `canonical_topics.yaml` align; run `validate_canonical_sources.py`. Legacy personas (e.g. educators, nyc_executives) are inactive unless added to unified_personas.md.

8. **Author assets (if expanding author-bound books)**  
   - Register new authors in `config/author_registry.yaml` with `persona_ids`, `topic_ids`, `positioning_profile`, and create bio, why_this_book, authority_position, audiobook_pre_intro per author.

---

## 6. Single-sentence summary

**Ready:** One lane (nyc_executives × self_worth) compiles with full STORY prose and passes curve; STORY pools exist for many persona×topic×engine combinations; system and specs are in place. **Missing:** REFLECTION, EXERCISE, INTEGRATION (and HOOK/SCENE/COMPRESSION where needed) for almost all persona×topic combinations; BAND/role depth and arcs in places; Golden Phoenix and author coverage. **Writing team:** Add and maintain non-STORY pools and compression per (persona, topic); ensure STORY depth and BAND; do micro-stakes research and Golden Phoenix promotion; add arcs and author assets as scope grows — then the system can write full books for all personas.
