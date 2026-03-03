# Phoenix V4 — Complete System Architecture, Governance, and Rebuild Spec

**Status:** Canonical (repo-rebuild source of truth)  
**Audience:** Core engineers, infra, QA, content governance, brand ops  
**Last Updated:** 2026-02-12  
**Version:** 4.3 (industrial-grade — plan compiler, K-tables, strict mode, duplication simulation, audio, covers, spec freeze, semantic quality, entropy tracking, catalog planning, naming engine)  
**Scope:** Full end-to-end system definition — from teacher doctrine through publishing pipeline  

**Doc status & planning gaps (all docs, freebies/authors/narrators):** See [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md).

---

## 0. What This Document Is

This document is the single source of truth for rebuilding the Phoenix system after total loss.  
If the repo were deleted, a competent engineer could recreate:

- directory structure and data flow
- doctrine preprocessing layer
- content integrity engine (mining, exercises, scenes, assembly)
- deterministic plan compiler with K-table enforcement
- strict-mode capability gates
- book-level duplication simulation
- business orchestration layer (brands, SKUs, release waves, entropy)
- audio production pipeline (TTS, voice registry, SSML)
- cover generation and companion marketing assets
- spec freeze governance and evolution control
- CI invariants and governance rules
- ethical constraints and safety protocols
- enforcement mechanisms and determinism guarantees

No other document is required.

### Authority and scope (V4.5 Omega alignment)

**SYSTEMS_DOCUMENTATION may define:** catalog strategy, release wave policy, production velocity modeling, planning heuristics, domain → series → angle strategy, blueprint rotation strategy, capacity planning math, emotional inventory monitoring, Omega orchestration (brand affinity, release waves).

**SYSTEMS_DOCUMENTATION may not define:** format IDs (F001–F015), slot semantics, K-table thresholds, CI gates, tier logic. Canonical Spec is the single source of truth for these. The format portfolio matrix in this doc is **advisory**; authoritative format definitions live in Canonical Spec Part 2.

**Config locations (machine-readable; this doc describes strategy and references them):**
- **Stage 1 catalog planning:** config/catalog_planning/ — domain_definitions.yaml, series_templates.yaml, capacity_constraints.yaml
- **Stage 2 format selection:** config/format_selection/ — format_registry.yaml, selection_rules.yaml
- **Stage 3 assembly:** config/ — topic_engine_bindings.yaml, topic_skins.yaml

Handoff schemas: specs/OMEGA_LAYER_CONTRACTS.md.

**Catalog planning (V4.5):** Domain → series → angle strategy is in **§29** below. Machine-readable config lives at repo-root **config/catalog_planning/** (domain_definitions.yaml, series_templates.yaml, capacity_constraints.yaml). Stage 1 catalog planner reads these.

**Format portfolio & blueprint rotation:** Advisory format matrix (F001–F015, chapter count, persona fit, priority) may appear in this doc; **authoritative format definitions are in Canonical Spec Part 2 only.** Blueprint rotation (linear, wave, scaffold, rupture) is in **§28**; selection rules in config/format_selection/selection_rules.yaml.

**K-table capacity & production velocity:** Canonical Spec §2.5 has the K-table capacity/velocity summary table and production strategy (prioritize F003–F006, Golden Phoenix provisional, human approval rate limiter). This doc may define **velocity modeling** (atoms per week, replenishment needs); K-table thresholds and slot semantics stay in Canonical.

**Reconciliation / gap closure:** Single role schema = **5 roles** (recognition, embodiment, pattern, mechanism_proof, agency_glimmer); Canonical Spec is source of truth. Canonical story-atom path = **atoms/\<persona\>/\<topic\>/\<engine\>/CANONICAL.txt**. Legacy 4-role or HARDSHIP/HELP/HEALING/HOPE template: document mapping in gap closure; see talp/analyze_intake/cursor_documentation_and_feature_analys.md for file manifest (persona_topic_variables.schema.yaml, unified_personas, etc.).

---

## 1. System Mission

Phoenix exists to scale therapeutic, culturally grounded audio content without:

- flattening meaning
- reusing prose
- introducing false reassurance
- automating ethical judgment

It is not a text generator.  
It is a **meaning-preserving assembly engine** with a **business orchestration layer**.

---

## 2. Three-Layer Architecture (Master Model)

Phoenix operates as three strictly separated layers.  
Each layer has different responsibilities, different governance rules, and different failure modes.

```
┌─────────────────────────────────────────────────────┐
│  LAYER 0 — TEACHER DOCTRINE PREPROCESSING           │
│  (human-governed, offline, meaning-defining)         │
│                                                      │
│  doctrine synthesis → doctrine approval →            │
│  locked doctrine files → seed generation             │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  LAYER 1 — PHOENIX V4.1+ (CONTENT INTEGRITY)        │
│  (governed, deterministic, safety-enforced)          │
│                                                      │
│  mining → story atoms → exercise atoms →             │
│  scene atoms → plan compiler → assembly →            │
│  duplication simulation → validation → CI            │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  LAYER 2 — OMEGA ORCHESTRATOR (BUSINESS LOGIC)       │
│  (no meaning, no content modification)               │
│                                                      │
│  brand matrix → SKU planning → release waves →       │
│  title entropy → platform upload → pricing           │
└─────────────────────────────────────────────────────┘
```

### Separation Principles

| Rule | Enforcement |
|------|-------------|
| **Layer 0 defines meaning** — only humans decide what a teacher believes | Doctrine files require human approval gate |
| **Layer 1 enforces structure** — mining, lint, cadence, safety, assembly, CI | All content passes through governed pipeline |
| **Layer 1 fails instead of degrades** — strict mode is default | Capability gates block thin output |
| **Layer 2 composes plans** — which books go where, when, under what brand | Layer 2 never modifies atom content |
| **Meaning flows down only** — Layer 2 cannot reach into Layer 1; Layer 1 cannot modify Layer 0 | CI enforces import boundaries |

**If any layer violates its boundary, the system is broken.**

---

## 3. Absolute Non-Negotiables

These rules are enforced by CI and must never be weakened:

1. Human long-form prose is never ingested directly
2. Runtime reads only approved micro-atoms (story, exercise, and scene)
3. All sensitive content requires human witnessing
4. Automation may assist, never override
5. Cultural specificity lives outside prose atoms
6. No reassurance, no resolution, no "healing language"
7. Teacher doctrine is locked before any mining begins
8. Exercises carry the same governance as story atoms
9. Scenes carry the same governance as story atoms
10. Layer 2 (Omega) never modifies content — only composes plans
11. **The system fails instead of degrades — no silent quality reduction**
12. **No book is published that would fail the duplication simulation**

**Violations are system failures, not bugs.**

---

## 4. Repository Topology (Rebuild Canon)

```
SOURCE_OF_TRUTH/
│
├── teacher_doctrine/                # LAYER 0 — locked doctrine
│   └── <teacher_id>/
│       ├── doctrine.yaml
│       ├── doctrine_approval.yaml
│       ├── therapeutic_frame.yaml
│       ├── stories/
│       ├── exercises/
│       └── DOCTRINE_NOTES.md
│
├── human_seeds/                     # READ-ONLY human truth
│   ├── README.md
│   └── <packs>/
│       ├── doctrine/
│       ├── seeds/
│       └── EXEMPLARS.md
│
├── candidate_atoms/                 # mined, linted, NOT runtime-visible
│   ├── story/
│   │   └── <persona>/<topic>/<role>/*.yaml
│   ├── exercise/
│   │   └── <persona>/<topic>/<exercise_type>/*.yaml
│   └── scene/
│       └── <persona>/<topic>/<scene_type>/*.yaml
│
├── approved_atoms/                  # ONLY runtime input
│   ├── story/
│   │   └── <persona>/<topic>/<role>/<atom_id>.yaml
│   ├── exercise/
│   │   └── <persona>/<topic>/<exercise_type>/<atom_id>.yaml
│   └── scene/
│       └── <persona>/<topic>/<scene_type>/<atom_id>.yaml
│
├── human_reject_notes/
│   └── <atom_id>.md
│
├── data/
│   ├── story_arc_registry.yaml      # arc types, stake domains, diversity policy (§7.0)
│   └── story_bank/
│       ├── location_variables/
│       ├── social_patterns/
│       ├── cultural_overlays/
│       └── pressure_themes/
│
├── registry/
│   ├── personas.yaml
│   ├── teachers.yaml
│   ├── styles.yaml
│   ├── exercise_registry.yaml
│   ├── scene_registry.yaml
│   └── doctrine_refs.yaml
│
├── omega/                           # LAYER 2 — business orchestration
│   ├── brand_registry/
│   ├── sku_plans/
│   ├── release_waves/
│   ├── title_entropy/
│   ├── catalog_planning/            # domain→series→angle hierarchy
│   │   ├── domains/
│   │   ├── series/
│   │   ├── angles/
│   │   └── planning_output/
│   ├── blueprint_rotation/
│   ├── global_fingerprint_index.json
│   ├── cover_generation/
│   ├── companion_assets/
│   └── platform_exports/
│
└── artifacts/
    ├── seed_mining/
    │   ├── _rejects/
    │   └── _safety_flags/
    ├── approval_logs/
    │   └── writer_trust/
    ├── doctrine_logs/
    ├── plan_compiler/
    │   ├── compiled_plans/
    │   ├── capability_reports/
    │   ├── compilation_failures/
    │   └── selection_traces/
    ├── duplication_simulation/
    ├── semantic_index/              # embedding cache per scope
    ├── entropy/                     # slot usage tracking
    ├── audit/                       # atom health audit results
    ├── build_manifests/             # per-book birth certificates
    ├── quarantine_registry.yaml     # failed compilations awaiting human review
    ├── omega_logs/
    └── template_eval/
```

---

# LAYER 0 — TEACHER DOCTRINE PREPROCESSING

---

## 5. Teacher Doctrine System

### 5.1 Purpose

Teacher doctrine is where meaning originates. Before any mining, assembly, or publishing can happen, the system must formalize *what a teacher believes and how they frame therapeutic truth*.

Doctrine synthesis is **meaning-defining work**. It is governed, not automated.

### 5.2 What Doctrine Encodes

Each teacher doctrine file captures:

- **Core beliefs** — what the teacher holds to be true about suffering, healing, and human experience
- **Therapeutic frame** — how the teacher approaches pain (e.g. somatic, cognitive, contemplative, narrative)
- **Forbidden framings** — what this teacher would never say or imply
- **Story archetypes** — recurring narrative patterns the teacher uses
- **Exercise philosophy** — what exercises mean in this teacher's tradition
- **Cultural anchors** — traditions, lineages, or practices that ground this teacher's work

### 5.3 Doctrine File Schema

**Location:**

```
SOURCE_OF_TRUTH/teacher_doctrine/<teacher_id>/doctrine.yaml
```

**Schema:**

```yaml
teacher_id: "sai_maa"
teacher_name: "Sai Maa"
version: 1
status: locked                    # draft | review | locked
locked_at: <UTC ISO 8601>
locked_by: <human>

core_beliefs:
  - "Suffering is not punishment — it is signal"
  - "The body knows before the mind names"
  - "Awakening happens through presence, not escape"

therapeutic_frame:
  primary: somatic
  secondary: contemplative
  approach: "Meet the sensation without narrating it"

forbidden_framings:
  - "positive thinking heals trauma"
  - "forgive and move on"
  - "everything happens for a reason"
  - "you chose this experience"

story_archetypes:
  - recognition_of_pattern
  - body_as_teacher
  - stillness_before_choice

exercise_philosophy:
  type: somatic_and_breath
  purpose: "Return attention to the body — not fix the body"
  forbidden_exercise_types:
    - affirmation_repetition
    - visualization_of_outcomes
    - gratitude_journaling

cultural_anchors:
  lineage: "Vedic tradition, adapted for Western practitioners"
  practices:
    - pranayama
    - mantra (non-devotional framing)
    - body scan
```

### 5.4 Doctrine Approval Gate

Doctrine files require explicit human approval before any downstream use.

**Approval file:**

```
SOURCE_OF_TRUTH/teacher_doctrine/<teacher_id>/doctrine_approval.yaml
```

```yaml
approval:
  status: approved
  approved_by: <human — must be content lead or teacher themselves>
  approved_at: <UTC ISO 8601>
  review_notes: "Verified with Sai Maa's team. Core beliefs accurate."
```

**Rules:**

- No mining may begin for a teacher until doctrine status = `locked` AND approval status = `approved`
- Doctrine changes require re-approval — version increments, re-lock, re-sign
- CI validates: no atoms exist for a teacher whose doctrine is not locked+approved

### 5.5 Doctrine-to-Mining Handoff

Once doctrine is locked and approved:

1. Teacher story seeds are generated (or authored) based on `story_archetypes` and `therapeutic_frame`
2. Teacher exercise seeds are generated based on `exercise_philosophy`
3. Seeds are placed in `human_seeds/` or `teacher_doctrine/<teacher_id>/exercises/`
4. Standard Layer 1 mining pipeline (§11) takes over

**Doctrine constrains mining.** The mining pipeline checks every candidate atom against the teacher's `forbidden_framings` and `exercise_philosophy.forbidden_exercise_types`. Any violation → hard reject.

### 5.6 Doctrine Coverage Enforcement

**Tool:**

```
tools/doctrine/check_doctrine_coverage.py
```

For each teacher, validates:

- All 5 story roles have ≥ N approved atoms per topic (N defined by format policy K-table — see §19)
- All required exercise types have ≥ N approved atoms per topic
- All required scene types have ≥ N approved atoms per topic
- No approved atom contradicts `forbidden_framings`

Coverage report written to:

```
artifacts/doctrine_logs/<teacher_id>_coverage.json
```

### 5.7 Golden Phoenix Coverage Agent

The coverage enforcement tool (§5.6) *detects* gaps. The Golden Phoenix Coverage Agent *fills* them deterministically. Without this tool, every K-table failure requires manual seed creation → mining → lint → approval — a bottleneck that blocks the entire pipeline.

**Tool:**

```
tools/coverage/golden_phoenix_agent.py
```

**Purpose:** Automatically generate **provisional** micro-story atoms to fill coverage gaps for any `(persona × topic × role)` combination that falls below K-table minimums.

**Command:**

```bash
python3 tools/coverage/golden_phoenix_agent.py \
  --persona gen_z_la \
  --topic burnout \
  --min-per-role 5 \
  --teacher sai_maa
```

**Scope — what it does:**

- Generates provisional story atoms for missing (persona, topic, role) combinations
- Generates provisional exercise atoms for missing (persona, topic, exercise_type) combinations
- Generates provisional scene atoms for missing (persona, topic, scene_type) combinations
- Every generated atom passes the full lint pipeline (§10, §8.4, §9.4) before writing
- Every generated atom passes doctrine compliance check (§5.5)
- Every generated atom passes safety scanner (§23)

**Scope — what it does NOT do:**

- Never promotes atoms to approved/confirmed — provisional only
- Never modifies doctrine files
- Never overrides lint rules or safety checks
- Never writes atoms for no-auto-promotion families (§17) — those require human authoring
- Never writes outside its designated output directory

**Output location:**

```
candidate_atoms/<category>/<persona>/<topic>/<role_or_type>/gp_<atom_id>.yaml
```

All Golden Phoenix atoms carry a `source: golden_phoenix` provenance tag:

```yaml
provenance:
  source: golden_phoenix
  generated_at: <UTC ISO 8601>
  teacher_doctrine: "sai_maa"
  generation_reason: "coverage_gap"
  lint_passed: true
  safety_passed: true
```

**Lint requirements (same as all atoms):**

- Role purity (§7)
- Word count: 60–90 story, 40–120 exercise, 30–90 scene
- Body lexeme for embodiment (§7.1) and applicable exercises (§8.2)
- Forbidden resolution lexemes (§10.2)
- Doctrine compliance (§5.5)
- Safety scan (§23)
- If lint fails → retry max 2 times → if still fails → log and skip

**CI enforcement:**

- Golden Phoenix atoms must have `source: golden_phoenix` in provenance
- Golden Phoenix atoms must start with status `provisional` — never `approved`
- CI fails if any Golden Phoenix atom is found in `approved_atoms/` without human review
- Coverage agent may only generate for combinations below K-table minimum

**Interaction with strict mode:**

- In strict mode: Golden Phoenix atoms are **not** used in production assembly (provisional atoms blocked)
- In QA mode: Golden Phoenix atoms may be used if `V4_QA_ALLOW_PROVISIONAL=true`
- Purpose: rapidly fill coverage for QA campaigns, then human reviewers promote the good ones

---

# LAYER 1 — PHOENIX V4.1+ (CONTENT INTEGRITY ENGINE)

---

## 6. Canonical Transformation Rule

**1 human seed → 5–7 micro-story atoms**

Human prose is **mined, not reused**.

Atoms must be:

- unresolved
- role-pure
- location-agnostic
- composable
- ethically safe
- consistent with teacher doctrine (§5)

---

## 7. Story Roles (Ordered, Required)

| Role | Description |
|------|-------------|
| **recognition** | Incident + validation, no body language |
| **embodiment** | Body sensation only (must include body lexeme — see §7.1) |
| **pattern** | Repetition without relief or hope |
| **mechanism_proof** | Explanation without solution |
| **agency_glimmer** | Choice without reassurance |

**Ordering is enforced mechanically (see §7.2).**

### 7.0 Story Arc Classification

Role purity (§7) ensures every recognition atom *is* a recognition atom. Narrative delta (§16.3.2) ensures every recognition atom *tells a different story*. Arc classification ensures that across a book, the stories *feel different* — not just in words, but in emotional shape. At 10K books, if every recognition atom follows "she was exhausted → something broke → she noticed," readers detect the formula even when every lint check passes.

Every story atom carries two additional metadata fields:

```yaml
# Added to story atom metadata:
arc_type: collapse | drift | exposure | threshold | consequence | resistance | mirror | return
stake_domain: career | relationship | health | identity | social | family | financial
```

**Arc types (what kind of emotional movement the atom dramatizes):**

| Arc Type | Engine | When to Use |
|----------|--------|------------|
| **collapse** | Competence under load breaks → visible consequence → identity fracture | Burnout, perfectionism, overcontrol |
| **drift** | Slow erosion normalizes → numbness → quiet recognition (no explosion) | Emotional withdrawal, chronic stress |
| **exposure** | Hidden strain → facade maintenance → truth becomes visible → forced honesty | Imposter syndrome, masking, hidden anxiety |
| **threshold** | Ongoing tension → clear fork → irreversible decision → commitment | Career pivot, boundary setting, leaving |
| **consequence** | Small compromise → repeated compromise → cost emerges → accountability | Avoidance, people pleasing |
| **resistance** | External pressure → internal refusal → friction → self-definition | Family expectations, cultural strain |
| **mirror** | Judgment of another → recognition of self → reframing | Projection, envy, competition |
| **return** | Old pattern resurfaces → regression → familiar shame → different response | Recovery, relapse, repeated burnout |

**Stake domains (what's at risk):**

| Domain | Examples |
|--------|---------|
| **career** | Job loss, promotion, reputation, performance error |
| **relationship** | Partner, friendship, trust, distance, conflict |
| **health** | Physical symptoms, sleep, chronic pain, breakdown |
| **identity** | Self-image, worth, competence belief, role in family |
| **social** | Public perception, belonging, exclusion, judgment |
| **family** | Parenting, obligation, generational patterns, caretaking |
| **financial** | Debt, job dependence, security, sacrifice |

**Arc Registry file:**

```yaml
# data/story_arc_registry.yaml

schema_version: 1

arc_types:
  collapse:
    description: "Competence under load breaks; visible consequence forces identity question"
    common_with_roles: [recognition, mechanism_proof]
    pairs_well_with_exercises: [grounding, release]
    
  drift:
    description: "Slow erosion normalizes; the shift is noticing, not exploding"
    common_with_roles: [embodiment, pattern]
    pairs_well_with_exercises: [grounding, activation]
    
  exposure:
    description: "Hidden strain becomes visible; forced honesty changes the dynamic"
    common_with_roles: [recognition, agency_glimmer]
    pairs_well_with_exercises: [activation, release]
    
  threshold:
    description: "A fork appears; the decision is irreversible enough to matter"
    common_with_roles: [agency_glimmer, mechanism_proof]
    pairs_well_with_exercises: [integration]
    
  consequence:
    description: "Small compromises accumulate; cost becomes visible"
    common_with_roles: [pattern, mechanism_proof]
    pairs_well_with_exercises: [grounding, activation]
    
  resistance:
    description: "External pressure meets internal refusal; friction defines self"
    common_with_roles: [agency_glimmer, recognition]
    pairs_well_with_exercises: [activation, integration]
    
  mirror:
    description: "Judgment of another reveals something about self"
    common_with_roles: [recognition, pattern]
    pairs_well_with_exercises: [grounding]
    
  return:
    description: "Old pattern resurfaces; same trigger, different response"
    common_with_roles: [pattern, agency_glimmer]
    pairs_well_with_exercises: [integration, release]

# Diversity constraints (enforced by plan compiler)
diversity_policy:
  per_book:
    max_same_arc_type: 2              # no more than 2 atoms of same arc_type in one book
    min_distinct_arc_types: 3         # at least 3 different arc types per book
    min_distinct_stake_domains: 2     # at least 2 different stake domains per book
    forbid_adjacent_same_arc: true    # no two adjacent chapters use same arc_type
    
  per_wave:
    max_same_arc_type_ratio: 0.35     # no single arc_type > 35% of all story atoms in a wave
```

**Rules:**

- `arc_type` is assigned during mining (by the generation prompt) and validated during lint
- `arc_type` must be from the canonical list in `data/story_arc_registry.yaml`
- `stake_domain` is assigned during mining and validated during lint
- Missing `arc_type` or `stake_domain` on a story atom → lint failure
- Arc diversity constraints are enforced by the plan compiler during atom selection (§20.3)
- The quality-ranked selector (§20.3) uses arc diversity as a selection factor: prefer atoms whose arc_type hasn't been used in the current book

**Story–exercise coherence:**

The arc registry declares `pairs_well_with_exercises` for each arc type. This is a *soft preference*, not a hard constraint — the plan compiler uses it as a scoring boost in the injection scorer (§20.3) when a story atom's arc_type pairs well with the exercise cadence_role in the same chapter. It's not a hard gate because therapeutic exercises are valid in any context; the pairing just feels more earned.

```yaml
# Example: chapter 3
# Story atom: arc_type=collapse, stake_domain=career
# Exercise: cadence_role=release, exercise_type=breathwork
# Pairing: collapse → release = preferred (collapse.pairs_well_with_exercises includes "release")
# Scoring boost: +0.05 on arc_coherence factor in injection scorer
```

### 7.1 Body Lexeme Registry

The `embodiment` role requires at least one body lexeme from the canonical registry.

**Registry location:**

```
docs/BODY_LEXEMES.yaml
```

**Canonical lexeme list (atom must contain ≥ 1):**

```yaml
required_any_of:
  - chest
  - throat
  - stomach
  - jaw
  - shoulders
  - breath
  - pulse
  - spine
  - hands
  - ribs
  - neck
  - temples
  - lungs
  - gut
  - skin
  - knees
  - forehead
  - wrists
  - teeth
  - tongue
```

**Rules:**

- Exact substring match (case-insensitive) against atom body text
- Metaphorical body language is **allowed** only if a literal body lexeme also appears
- Synonyms do not count unless they appear in the registry
- If no body lexeme is found → hard lint failure → repair attempt (max 2)

**Enforcement:**

```
tools/seed_mining/lint_atoms.py  →  checks body lexeme presence for embodiment role
```

### 7.2 Role Ordering Enforcement

**Validator:**

```
tools/seed_mining/validate_role_order.py
```

**Canonical sequence (strict):**

```
recognition → embodiment → pattern → mechanism_proof → agency_glimmer
```

**Enforcement rules:**

- Ordering applies **per chapter** (the atom chain that forms one therapeutic arc)
- No role may appear twice in a single chapter
- No role skipping (every role must be present)
- Ordering violations are **hard failures** — no repair, no override
- Validated at two points:
  1. **Mining time:** `validate_role_order.py` checks role assignments before candidate promotion
  2. **Plan compile time:** plan compiler validates selected atom sequence before assembly

**CI enforcement:**

```
CI runs validate_role_order.py against all approved_atoms/story/ sequences
Failure → CI blocks merge
```

---

## 8. Exercise System (Governed)

Exercises are therapeutic content. They carry the same governance, lint, safety, and approval requirements as story atoms.

### 8.1 Why Exercises Are in Layer 1

Exercises instruct people to do things with their bodies and minds. A badly constructed exercise can cause harm. Therefore:

- Exercises **must** pass the same lint, cadence, and safety gates as story atoms
- Exercises in sensitive families (§17) **cannot** auto-promote
- Exercises **must** be consistent with teacher doctrine `exercise_philosophy` (§5.3)

### 8.2 Exercise Types (Canonical)

| Exercise Type | Description | Body Lexeme Required? |
|---------------|-------------|----------------------|
| **breathwork** | Breathing exercises — pacing, rhythm, regulation | ✅ Yes |
| **somatic** | Body-awareness practices — scanning, grounding, releasing | ✅ Yes |
| **integration** | Transitional exercises — bridging insight to daily life | ❌ No |
| **stillness** | Non-doing practices — sitting with sensation, waiting | ✅ Yes |
| **movement** | Gentle physical movement — not fitness, not performance | ✅ Yes |

**Registry location:**

```
registry/exercise_registry.yaml
```

```yaml
exercise_types:
  breathwork:
    body_lexeme_required: true
    max_duration_seconds: 300
    forbidden_instructions:
      - "hold your breath as long as you can"
      - "breathe faster"
      - "hyperventilate"
    safety_tier: elevated

  somatic:
    body_lexeme_required: true
    max_duration_seconds: 600
    forbidden_instructions:
      - "push through the pain"
      - "ignore the sensation"
    safety_tier: elevated

  integration:
    body_lexeme_required: false
    max_duration_seconds: null
    forbidden_instructions:
      - "write a letter to your abuser"
      - "confront the person"
    safety_tier: standard

  stillness:
    body_lexeme_required: true
    max_duration_seconds: 600
    forbidden_instructions:
      - "empty your mind"
      - "think of nothing"
    safety_tier: standard

  movement:
    body_lexeme_required: true
    max_duration_seconds: 300
    forbidden_instructions:
      - "push past your limit"
      - "no pain no gain"
      - "faster"
    safety_tier: standard
```

### 8.3 Exercise Atom Schema

```yaml
atom_id: "ex_breath_gzla_anx_001"
atom_category: exercise
version: 1
deprecated: false
persona: gen_z_la
topic: anxiety
teacher_id: "sai_maa"
exercise_type: breathwork
duration_seconds: 120
body: |
  Place one hand on your chest. Notice the rise. Don't change it.
  Count silently: in for four, hold for two, out for six.
  If your mind pulls you somewhere, let it. Then return to the count.
  There is nothing to fix here. Just rhythm. Just breath.
  Notice if the pressure in your chest shifts — or doesn't.
  Either is information.
word_count: 65
approval:
  status: approved
  approved_by: <human>
  approved_at: <UTC ISO 8601>
  promotion_reason: manual | auto_confident
provenance:
  source_seed: "ex_seed_breath_001"
  teacher_doctrine: "sai_maa"
  mined_at: <UTC ISO 8601>
```

### 8.4 Exercise Lint Rules

| Constraint | Specification |
|-----------|---------------|
| **Word count** | 40–120 words (inclusive) — wider range than story atoms |
| **Word count method** | `len(text.strip().split())` |
| **Person** | Second person ("you") |
| **Tense** | Present tense (imperative allowed) |
| **Ending** | Open — no outcome prediction |
| **Body lexeme** | Required for breathwork, somatic, stillness, movement |
| **Forbidden instructions** | Per exercise type (from `exercise_registry.yaml`) |
| **Forbidden resolution** | Same as story atoms (§10.2) |
| **Doctrine consistency** | Must not contradict teacher's `exercise_philosophy.forbidden_exercise_types` |
| **Duration** | Must not exceed `max_duration_seconds` for exercise type |

### 8.5 Exercise Safety Rules

Exercises with `safety_tier: elevated` receive additional checks:

- Safety scanner (§23) runs with exercise-specific lexicon
- Must not instruct breath-holding beyond 4 seconds without explicit "release" within 2 sentences
- Must not instruct revisiting specific traumatic memories
- Must include at least one "return to present" cue
- Sensitive-family exercises (§17) **cannot** auto-promote

### 8.6 Exercise Cadence Roles (Pacing Enforcement)

Beyond exercise *type* (breathwork, somatic, etc.), each exercise carries a **cadence role** that governs its pacing function within the therapeutic arc. This is a separate enforcement layer from exercise type.

**Cadence roles:**

| Cadence Role | Purpose | Chapter Position |
|-------------|---------|-----------------|
| **grounding** | Anchor the reader in present-moment sensation before emotional depth | Early (slot_04, chapters 1–3) |
| **activation** | Intensify somatic awareness during pattern/mechanism exploration | Mid (slot_04 or slot_07, chapters 4–7) |
| **release** | Discharge accumulated tension after mechanism_proof | Mid-late (slot_07, chapters 5–9) |
| **integration** | Bridge insight to daily embodiment before closing | Late (slot_07, chapters 8+) |

**Registry extension (added to `exercise_registry.yaml`):**

```yaml
cadence_roles:
  grounding:
    chapter_position_ok: [1, 2, 3, 4]
    slot_position_ok: [slot_04_exercise_a]
    may_follow_roles: [recognition, embodiment]
    
  activation:
    chapter_position_ok: [3, 4, 5, 6, 7]
    slot_position_ok: [slot_04_exercise_a, slot_07_exercise_b]
    may_follow_roles: [embodiment, pattern]
    
  release:
    chapter_position_ok: [5, 6, 7, 8, 9]
    slot_position_ok: [slot_07_exercise_b]
    may_follow_roles: [mechanism_proof]
    
  integration:
    chapter_position_ok: [7, 8, 9, 10, 11, 12]
    slot_position_ok: [slot_07_exercise_b]
    may_follow_roles: [mechanism_proof, agency_glimmer]
```

**Enforcement rules:**

- Each exercise atom must declare a `cadence_role` in its metadata
- Plan compiler validates: exercise cadence_role matches `chapter_position_ok` for its chapter number
- Plan compiler validates: exercise cadence_role matches `slot_position_ok` for its slot
- No two adjacent chapters may use the same cadence_role (pacing variety)
- Cadence role violations are **hard failures** in strict mode
- The overall book arc should progress: grounding → activation → release → integration (not enforced per-chapter, but validated as a trend across the book)

**Exercise atom schema extension:**

```yaml
# Added to exercise atom metadata:
cadence_role: grounding | activation | release | integration
chapter_position_ok: [1, 2, 3, 4]
```

---

## 9. Scene System (Governed)

Scenes set emotional and situational context for the reader.

### 9.1 Why Scenes Are in Layer 1

Scenes frame how the reader enters the experience. A scene that trivializes suffering or creates false urgency can undermine the entire therapeutic sequence. Therefore scenes carry full governance.

### 9.2 Scene Types (Canonical)

| Scene Type | Description |
|------------|-------------|
| **entry** | Opens the experience — situational grounding, sensory context |
| **transition** | Bridges between chapters or sequences |
| **closing** | Final moment — no resolution, open awareness |

**Registry location:**

```
registry/scene_registry.yaml
```

```yaml
scene_types:
  entry:
    purpose: "Ground the reader in a specific moment and sensory context"
    must_include: sensory_detail
    must_not_include: resolution_or_comfort
    placement: before_recognition

  transition:
    purpose: "Bridge between sequences without resolving tension"
    must_include: continuity_signal
    must_not_include: summary_or_recap
    placement: between_sequences

  closing:
    purpose: "Leave the reader in open awareness — not comfort"
    must_include: present_moment_anchor
    must_not_include: reassurance_or_outcome
    placement: after_agency_glimmer
```

### 9.3 Scene Atom Schema

```yaml
atom_id: "sc_entry_gzla_anx_001"
atom_category: scene
version: 1
deprecated: false
persona: gen_z_la
topic: anxiety
teacher_id: "sai_maa"
scene_type: entry
body: |
  You're sitting in the car after the shift. Engine off.
  The parking lot is almost empty. Your phone has
  three notifications you haven't opened. The seat belt
  is still on. You haven't moved. Something in your
  chest says wait — but doesn't say what for.
word_count: 52
approval:
  status: approved
  approved_by: <human>
  approved_at: <UTC ISO 8601>
  promotion_reason: manual
```

### 9.4 Scene Lint Rules

| Constraint | Specification |
|-----------|---------------|
| **Word count** | 30–90 words (inclusive) |
| **Person** | Second person ("you") |
| **Tense** | Present tense |
| **Ending** | Open — no resolution |
| **Sensory detail** | Entry scenes must contain ≥ 1 sensory lexeme (from `docs/SENSORY_LEXEMES.yaml`) |
| **Forbidden resolution** | Same as story atoms (§10.2) |
| **Location** | Placeholders only — no hardcoded locations |
| **Doctrine consistency** | Must not contradict teacher `forbidden_framings` |

**Sensory lexeme registry:**

```
docs/SENSORY_LEXEMES.yaml
```

```yaml
sensory_lexemes:
  visual: [light, shadow, glow, dim, bright, dark, color, screen, window]
  auditory: [sound, hum, buzz, silence, ring, click, voice, noise, quiet]
  tactile: [cold, warm, rough, smooth, pressure, weight, tight, soft, hard]
  olfactory: [smell, scent, air, stale, fresh, smoke]
  proprioceptive: [sitting, standing, leaning, still, weight, heavy, light]
```

---

## 10. Rewrite Rules (Hard) — Story Atoms

### Structural Requirements

| Constraint | Specification |
|-----------|---------------|
| **Word count** | 60–90 words (inclusive) |
| **Word count method** | `len(text.strip().split())` |
| **Person** | Second person ("you") |
| **Tense** | Present tense |
| **Ending** | Open (see §10.1) |
| **Location** | No location names or proper nouns |

### 10.1 "Open Ending" — Explicit Definition

An open ending means the atom must **not** contain:

- Future certainty ("will", "going to", "soon")
- Resolution verbs (see §10.2)
- Outcome language ("gets better", "works out", "finds peace")
- Reassurance ("it's okay", "you're safe now", "this too shall pass")
- Comfort framing ("everything will be okay", "you'll get through this")

An atom ends open when the reader **remains in the feeling** without being told what comes next.

### 10.2 Forbidden Resolution Lexemes

**Registry location:**

```
docs/FORBIDDEN_RESOLUTION_LEXEMES.yaml
```

```yaml
forbidden_verbs:
  - heal
  - recover
  - resolve
  - overcome
  - conquer
  - transcend
  - fix
  - cure
  - mend
  - repair
  - transform

forbidden_phrases:
  - "gets better"
  - "will be okay"
  - "it passes"
  - "you'll see"
  - "in time"
  - "one day"
  - "everything will"
  - "nothing to worry"
  - "safe now"
  - "you're fine"
  - "don't worry"
  - "it's going to be"
  - "healing journey"
  - "on the other side"
  - "light at the end"

forbidden_reassurance:
  - "you are enough"
  - "you've got this"
  - "you're stronger than"
  - "believe in yourself"
  - "trust the process"
```

**Enforcement:** Substring match (case-insensitive). Any match → hard lint failure. Applies to **all atom categories**.

---

## 11. Seed Mining Pipeline (Offline)

### Tools Location

```
tools/seed_mining/
├── semantic_segmenter.py
├── role_extractor.py
├── role_mapper.py
├── rewrite_as_atom.py
├── lint_atoms.py
├── lint_exercises.py
├── lint_scenes.py
├── cadence_checks.py
├── validate_role_order.py
├── validate_atom_structure.py
├── similarity_check.py
├── safety_scanner.py
├── doctrine_compliance_check.py
├── repair_loop.py
└── approve_cli.py
```

### Pipeline — Story Atoms

```
human_seeds → semantic_segmenter → role_extractor → rewrite_as_atom
→ validate_atom_structure → lint_atoms → doctrine_compliance_check
→ safety_scanner → cadence_checks → similarity_check → validate_role_order
→ candidate_atoms/story/ → (approval) → approved_atoms/story/
```

### Pipeline — Exercise Atoms

```
teacher_doctrine exercises → exercise_segmenter → rewrite_as_exercise_atom
→ lint_exercises → doctrine_compliance_check → safety_scanner
→ similarity_check → candidate_atoms/exercise/ → (approval) → approved_atoms/exercise/
```

### Pipeline — Scene Atoms

```
human_seeds or teacher_doctrine → scene_extractor → rewrite_as_scene_atom
→ lint_scenes → doctrine_compliance_check → safety_scanner
→ similarity_check → candidate_atoms/scene/ → (approval) → approved_atoms/scene/
```

### Key Properties (All Pipelines)

- Offline only
- Deterministic (see §24)
- Fail-fast
- No runtime dependencies

---

## 12. Cadence Enforcement

Cadence is enforced **between roles**, not in isolation.

- `recognition → embodiment` must enter the body immediately
- Final role (`agency_glimmer`) must end in open choice, not comfort
- Scene `entry` → `recognition` must maintain sensory continuity
- Exercise placement must not break emotional arc

Cadence failures are lint failures. Per-family thresholds defined in `docs/CADENCE_THRESHOLDS_BY_FAMILY.yaml`.

---

## 13. Repair Loop (Bounded, Auditable)

On lint or cadence failure (any atom category):

1. Emit `<role_or_type>_repair.json`
2. Attempt repair (max 2 attempts)
3. Validate: different from original, passes all lint, passes cadence, passes doctrine
4. Accept only if all gates pass

All failures logged to `artifacts/seed_mining/_rejects/<seed_id>/`.

---

## 14. Candidate vs Approved Atoms

### `candidate_atoms/` — lint-clean, not runtime-visible, require human judgment

### `approved_atoms/` — human-approved, runtime-visible, CI-enforced

### Atom File Schema (Universal)

```yaml
atom_id: "rec_gzla_anx_001"
atom_category: story | exercise | scene
version: 1
deprecated: false
persona: gen_z_la
topic: anxiety
teacher_id: "sai_maa"
role: recognition              # story atoms
exercise_type: breathwork      # exercise atoms
scene_type: entry              # scene atoms
arc_type: collapse             # story atoms only — from arc registry (§7.0)
stake_domain: career           # story atoms only — from arc registry (§7.0)
body: |
  ...
word_count: 62
approval:
  status: approved
  approved_by: <human>
  approved_at: <UTC ISO 8601>
  promotion_reason: manual | auto_confident
provenance:
  source_seed: "pf_sgv_sr_001"
  teacher_doctrine: "sai_maa"
  mined_at: <UTC ISO 8601>
  mining_tool_version: "1.0.0"
```

### 14.1 Versioning Rules

- Every atom carries a `version` integer, starting at 1
- Atom content is **immutable** once approved — to change content, create a new atom
- Metadata updates (e.g. `deprecated: true`) increment `version`
- Deprecated atoms excluded from runtime; retained for audit
- To retire atoms: set `deprecated: true` — never delete

---

## 15. Approval Tooling

**Tool:** `tools/approval/approve_atoms.py`

**Commands:** `list`, `approve`, `reject`, `auto` (guarded — see §16), `--dry-run`, `--category`

This tool only moves files and metadata. **It never rewrites content.**

---

## 16. Auto-Promotion Rules

**All must pass:**

| Gate | Specification |
|------|--------------|
| **Lint** | All lint gates passed (category-specific) |
| **Cadence** | Score ≥ family minimum + buffer |
| **Forbidden language** | Zero matches against `FORBIDDEN_RESOLUTION_LEXEMES.yaml` |
| **Forbidden instructions** | Zero matches (exercise atoms only) |
| **Location leakage** | Zero proper nouns or location names |
| **Doctrine compliance** | Zero contradictions with teacher `forbidden_framings` |
| **Similarity** | Cosine similarity < 0.82 vs approved atoms in same namespace |
| **Arc classification** | Story atoms must have valid `arc_type` and `stake_domain` from arc registry (§7.0) |
| **Writer trust** | Per-writer, per-role/type threshold met |

### 16.1 Similarity Gate

| Parameter | Value |
|-----------|-------|
| **Model** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Metric** | Cosine similarity |
| **Threshold** | 0.82 (tightened from 0.85 at scale — prevents near-duplicate atoms compounding across 1000+ books) |
| **Scope** | Per `<category>/<persona>/<topic>/<role_or_type>` |
| **Failure** | Hard fail — atom cannot be promoted |
| **Cache** | Embeddings cached in `artifacts/semantic_index/{persona}_{topic}_{role}.json` |

When embedding model is updated: all cached embeddings recomputed, all atoms re-checked against new threshold, atoms newly exceeding threshold flagged for review.

### 16.2 Writer Trust

```yaml
writer_trust:
  min_approved_atoms: 20
  max_recent_reject_rate: 0.10    # over last 50 atoms
```

Stored in `artifacts/approval_logs/writer_trust/<writer_id>.yaml`. Computed per role/type, not globally.

### 16.3 Semantic Quality Gates

Structural lint (word count, forbidden lexemes, role purity) ensures atoms are *well-formed*. Semantic quality gates ensure atoms are *meaningfully different*. At 10,000+ atoms, structural validity without semantic density produces a catalog that passes every lint check but reads like the same book 1,000 times.

**Tool:**

```
tools/semantic/semantic_quality_gate.py
```

#### 16.3.1 Filler Density Detection

Detect repeated structural filler patterns that pass lint but indicate lazy or template-driven generation:

```yaml
# phoenix_v4/policy/filler_patterns.yaml

filler_patterns:
  high_frequency_flags:
    - "They noticed"
    - "There was pressure"
    - "The signal was"
    - "They had tried"
    - "Something shifted"
    - "It was as if"
    - "There was a sense of"
    - "They could feel"
    - "It had always been"
    - "The weight of"

  thresholds:
    per_atom_max: 1                  # max 1 filler pattern per atom
    per_100_atoms_same_filler: 8     # no single filler in >8% of atoms in a scope
    per_role_filler_ratio: 0.30      # if >30% of atoms in a role contain ANY filler → FAIL
```

**Enforcement:**

- Filler scan runs during lint (after word count, before promotion)
- Per-atom violations are repairable (max 2 repair attempts)
- Per-scope ratio violations trigger a **mining quality alert** — the pipeline is producing template-driven output and needs seed diversification
- Filler pattern list is maintained in policy YAML, not hardcoded

#### 16.3.2 Narrative Delta Scoring

Each role must show *meaningful variation* across its atom pool. Role purity ensures every recognition atom *is* a recognition atom. Narrative delta ensures every recognition atom *tells a different story*.

```yaml
# phoenix_v4/policy/narrative_delta.yaml

narrative_delta:
  recognition:
    required_variation: situational_trigger
    description: "Each recognition atom must describe a different life moment/situation"
    min_unique_triggers_per_20_atoms: 15    # at least 75% distinct situations
    
  embodiment:
    required_variation: somatic_focus
    description: "Each embodiment atom must target a different body region or sensation type"
    min_unique_body_regions_per_20_atoms: 12  # at least 60% distinct body focus
    
  pattern:
    required_variation: repetition_type
    description: "Each pattern atom must describe a different behavioral loop"
    min_unique_patterns_per_20_atoms: 15
    
  mechanism_proof:
    required_variation: failed_strategy
    description: "Each mechanism_proof atom must describe a different coping strategy that doesn't work"
    min_unique_strategies_per_20_atoms: 12
    
  agency_glimmer:
    required_variation: micro_choice_type
    description: "Each agency_glimmer atom must present a different type of small choice"
    min_unique_choices_per_20_atoms: 15
```

**Tool:**

```
tools/semantic/check_role_diversity.py
```

**Enforcement:**

- Runs as a pool health check, not per-atom lint (you need 20+ atoms in a scope before it fires)
- Below minimum unique variation → **mining diversity alert** (not hard fail on individual atoms)
- Report output: `artifacts/semantic_index/{persona}_{topic}_delta_report.json`
- Plan compiler checks: if a scope fails narrative delta, capability gate downgrades from `CAPABLE` to `THIN` with warning

---

## 17. Families That NEVER Auto-Promote

```yaml
no_auto_promotion_families:
  - grief_pack
  - trauma_recovery
  - suicide_loss
  - terminal_illness
  - child_abuse
  - domestic_violence
```

**Applies to ALL atom categories.** Ethical constraint, not quality constraint.

### 17.1 Atom Health Audit Cycle

At scale, atoms that were healthy at approval time may become problematic: overused, drifted into similarity clusters, or outpaced by newer, better atoms. The health audit cycle catches degradation before it compounds.

**Tool:**

```
tools/audit/atom_health_check.py
```

**Trigger:** Runs automatically every 500 compiled books (configurable), or manually via:

```bash
make atom_health_audit SCOPE=gen_z_la/anxiety
```

**Checks:**

| Check | Condition | Action |
|-------|-----------|--------|
| **Overuse** | Atom used in >10% of books in its scope | Flag for review; consider deprecation or pool expansion |
| **Similarity cluster** | 3+ approved atoms in same scope with pairwise cosine >0.75 | Flag cluster; deprecate weakest or most overused |
| **Filler accumulation** | Scope exceeds filler density threshold (§16.3.1) | Mining priority alert |
| **Narrative delta erosion** | Scope falls below narrative delta minimums (§16.3.2) | Mining diversity alert |
| **Stale atom** | Atom not selected in last 200 books for its scope | Review — may be outcompeted by better atoms |

**Output:**

```
artifacts/audit/atom_health_<scope>_<date>.json
```

**Rules:**

- Health audit results are logged, not auto-acted-upon
- Deprecation recommendations require human review
- Mining priority alerts feed into seed generation planning
- Audit history is retained for trend analysis

---

## 18. Story Bank (Cultural Specificity)

All cultural detail lives outside atoms in `data/story_bank/`. Atoms reference placeholders only:

```
{{social.hangout_spot}}   {{pressure.theme}}   {{location.neighborhood}}
{{cultural.food_reference}}   {{sensory.ambient_sound}}
```

Hydration at assembly time via `runtime/variable_hydrator.py`.

---

## 19. Format Policy System (Replaces Templates)

### 19.1 Why Not Templates

The old model used fixed templates: 12 chapters × 10 sections × 3-5 variations = combinatorial permutation. This produced formulaic books with high duplication risk at scale.

The V4.3 model uses **format policies** that define constraints, and a **plan compiler** that produces unique book plans within those constraints. Scale comes from genuine content diversity across teachers, personas, topics, and cultural overlays — not from reshuffling variations into identical structures.

### 19.2 Format Policy Schema

**Location:**

```
phoenix_v4/policy/format_policies/
├── standard_book.yaml
├── short_form.yaml
├── deep_dive.yaml
├── guided_session.yaml
└── micro_collection.yaml
```

**Canonical format policy (standard_book):**

```yaml
format_id: standard_book
version: 2

# ----- Chapter & Section Bounds -----
chapter_count:
  min: 8
  max: 12
  determined_by: atom_pool_depth    # more approved atoms = more chapters

sections_per_chapter:
  min: 7                            # scene_entry + 5 story roles + scene_closing
  max: 10                           # with optional exercises

# ----- Word Targets -----
word_targets:
  per_chapter:
    min: 600
    max: 1200
  per_book:
    min: 6000
    max: 14000

# ----- Therapeutic Arc Per Chapter (Slot Definitions) -----
chapter_arc:
  slots:
    - slot_id: slot_01_entry
      category: scene
      scene_type: entry
      required: true

    - slot_id: slot_02_recognition
      category: story
      role: recognition
      required: true

    - slot_id: slot_03_embodiment
      category: story
      role: embodiment
      required: true

    - slot_id: slot_04_exercise_a
      category: exercise
      exercise_type: [breathwork, somatic, stillness]
      required: true
      placement: after_embodiment

    - slot_id: slot_05_pattern
      category: story
      role: pattern
      required: true

    - slot_id: slot_06_mechanism
      category: story
      role: mechanism_proof
      required: true

    - slot_id: slot_07_exercise_b
      category: exercise
      exercise_type: [integration, somatic, movement]
      required: false                # optional enrichment slot
      placement: after_mechanism

    - slot_id: slot_08_agency
      category: story
      role: agency_glimmer
      required: true

    - slot_id: slot_09_closing
      category: scene
      scene_type: closing
      required: true

    - slot_id: slot_10_transition
      category: scene
      scene_type: transition
      required: false               # only between chapters, not after last
      placement: between_chapters

# ----- Inter-Chapter Rules -----
inter_chapter:
  transition_scene_required: true     # between every chapter pair
  no_adjacent_exercise_type_reuse: true
  scene_entry_min_unique: 3           # at least 3 different entry scenes per book
  scene_closing_min_unique: 3
```

### 19.3 K-Table: Minimum Atom Pool Depth Per Slot

The K-table defines the **minimum number of approved atoms** that must exist in the pool for each slot type before the plan compiler will attempt compilation. This is what prevents thin, repetitive books.

**K-table location:**

```
phoenix_v4/policy/k_tables/
├── standard_book.yaml
├── short_form.yaml
└── deep_dive.yaml
```

**Canonical K-table (standard_book):**

```yaml
# K-TABLE: standard_book
# Format: slot_id → min_approved_atoms per (teacher, persona, topic) namespace
# "K" = the minimum pool depth. If any slot is below K, compilation fails.

k_table:
  # Story roles — need enough unique atoms to fill all chapters without reuse
  story:
    recognition:
      k_min: 12          # 12 chapters max → need 12 unique atoms minimum
      k_recommended: 20  # headroom for variety and duplication avoidance
    embodiment:
      k_min: 12
      k_recommended: 20
    pattern:
      k_min: 12
      k_recommended: 20
    mechanism_proof:
      k_min: 12
      k_recommended: 20
    agency_glimmer:
      k_min: 12
      k_recommended: 20

  # Exercise types — one required per chapter, one optional
  exercise:
    breathwork:
      k_min: 6           # will rotate across types, not all breathwork
      k_recommended: 10
    somatic:
      k_min: 6
      k_recommended: 10
    integration:
      k_min: 4           # optional slot only
      k_recommended: 8
    stillness:
      k_min: 4
      k_recommended: 8
    movement:
      k_min: 4
      k_recommended: 8

  # Scene types
  scene:
    entry:
      k_min: 6           # min 3 unique per book; 6 gives 2 books headroom
      k_recommended: 12
    closing:
      k_min: 6
      k_recommended: 12
    transition:
      k_min: 4
      k_recommended: 8

# Combined exercise pool check (across all types)
exercise_pool_combined:
  k_min: 18              # at least 18 total exercise atoms across all types
  k_recommended: 30      # enough for 12 chapters × ~1.5 exercises avg

# ----- Variant Threshold -----
# The plan compiler checks: for each chapter being compiled, can every
# required slot be filled by an atom NOT yet used in this book?
# If at any chapter the answer is no → compilation fails (strict mode)
# or reduces chapter count to what the pool supports (relaxed mode)
variant_threshold:
  mode: strict            # strict | relaxed
  # strict: fail if pool cannot fill all chapters at max chapter_count
  # relaxed: reduce chapter_count to what pool supports (min = chapter_count.min)
```

### 19.4 How K-Table Enforcement Works

```
Plan Compiler receives: (teacher, persona, topic, format_id, overlay)
                                    ↓
Step 1: CAPABILITY CHECK
  → Load K-table for format_id
  → Query approved_atoms/ for (teacher, persona, topic)
  → Count available atoms per slot type
  → For each slot type: if count < k_min → CAPABILITY FAILURE
  → Log failure to artifacts/plan_compiler/capability_reports/
  → In strict mode: STOP. No book produced.
  → In relaxed mode: reduce chapter_count until pool supports it
     (if reduced below chapter_count.min → STOP)
                                    ↓
Step 2: ACHIEVABLE CHAPTER COUNT
  → achievable_chapters = min(
      chapter_count.max,
      min(pool_size[role] for role in story_roles),
      floor(total_exercises / exercises_per_chapter_avg)
    )
  → In strict mode: if achievable_chapters < chapter_count.max → FAIL
  → In relaxed mode: use achievable_chapters (must be ≥ chapter_count.min)
                                    ↓
Step 3: PLAN COMPILATION (see §20)
```

**Capability report schema:**

```yaml
# artifacts/plan_compiler/capability_reports/<book_request_id>.yaml
book_request:
  teacher: sai_maa
  persona: gen_z_la
  topic: anxiety
  format: standard_book
  overlay: west_la
capability:
  status: CAPABLE | THIN | BLOCKED
  achievable_chapters: 10
  pool_depths:
    story:
      recognition: { available: 24, k_min: 12, status: ok }
      embodiment: { available: 22, k_min: 12, status: ok }
      pattern: { available: 18, k_min: 12, status: ok }
      mechanism_proof: { available: 15, k_min: 12, status: ok }
      agency_glimmer: { available: 20, k_min: 12, status: ok }
    exercise:
      breathwork: { available: 8, k_min: 6, status: ok }
      somatic: { available: 7, k_min: 6, status: ok }
      integration: { available: 5, k_min: 4, status: ok }
      stillness: { available: 3, k_min: 4, status: BELOW_K }
      movement: { available: 6, k_min: 4, status: ok }
    scene:
      entry: { available: 10, k_min: 6, status: ok }
      closing: { available: 9, k_min: 6, status: ok }
      transition: { available: 6, k_min: 4, status: ok }
  exercise_pool_combined: { available: 29, k_min: 18, status: ok }
  blocking_slots: [stillness]
  recommendation: "Add 1+ stillness exercise atoms or switch to relaxed mode"
checked_at: <UTC ISO 8601>
```

---

## 20. Deterministic Plan Compiler

### 20.1 Purpose

The plan compiler is the core of Layer 1's assembly engine. It takes a book request and produces a **deterministic, unique book plan** — a complete mapping of which specific atom fills which slot in which chapter.

**Tool:**

```
runtime/plan_compiler.py
```

### 20.2 Compilation Pipeline

```
Book Request (teacher, persona, topic, format, overlay)
  ↓
1. CAPABILITY CHECK (§19.4)
  → K-table enforcement
  → Pool depth validation
  → Achievable chapter count
  ↓
2. CHAPTER PLANNING
  → For each chapter (1..N):
     → For each required slot in chapter_arc:
        → Query pool for eligible atoms:
           - matching (teacher, persona, topic, category, role/type)
           - not deprecated
           - not already used in this book
           - not used in recently published books for same combo (§21)
        → Select atom using deterministic selection (see §20.3)
        → If no eligible atom exists for required slot → FAIL (strict) or SKIP CHAPTER (relaxed)
     → Validate chapter:
        - story role ordering (§7.2)
        - exercise placement valid
        - scene bracketing correct
        - word count within chapter bounds
        - doctrine consistency for all atoms
  ↓
3. INTER-CHAPTER VALIDATION
  → No atom reuse across any chapter in this book
  → No adjacent chapters use same exercise type in slot_04
  → scene_entry variety ≥ min_unique
  → scene_closing variety ≥ min_unique
  → transition scenes placed between all chapter pairs
  ↓
4. BOOK-LEVEL VALIDATION
  → Total word count within book bounds
  → All required chapters compiled
  → Duplication simulation passed (§21)
  ↓
5. PLAN OUTPUT
  → Deterministic plan.yaml written to artifacts/plan_compiler/compiled_plans/
  → Plan is sealed (hash computed)
  → Ready for hydration and rendering
```

### 20.3 Deterministic Atom Selection (Quality-Ranked)

Atom selection must be deterministic — same input always produces same plan. But deterministic does not mean random. The selector ranks candidates by quality fit, then uses a deterministic tiebreaker.

**Selection algorithm:**

```python
def select_atom(eligible_atoms, book_seed, chapter_index, slot_id, book_context):
    """
    Quality-ranked deterministic selection.
    book_seed = sha256(teacher + persona + topic + format + overlay + book_sequence)
    """
    # Score each candidate
    scored = [(atom, compute_score(atom, book_context)) for atom in eligible_atoms]
    
    # Sort by score descending, then by atom_id for deterministic tiebreaking
    scored.sort(key=lambda x: (-x[1].total, x[0].atom_id))
    
    # If top N candidates are within 0.05 of each other, use seed-based selection
    # among that tier (prevents always picking the same "best" atom across books)
    top_score = scored[0][1].total
    tier = [s for s in scored if s[1].total >= top_score - 0.05]
    
    if len(tier) > 1:
        selection_seed = sha256(f"{book_seed}:{chapter_index}:{slot_id}")
        index = int(selection_seed[:8], 16) % len(tier)
        return tier[index][0], tier[index][1]
    
    return scored[0][0], scored[0][1]
```

**Scoring function:**

```python
def compute_score(atom, book_context):
    """
    Multi-factor quality score for candidate atom selection.
    All factors 0.0-1.0, weighted by injection_scoring.yaml policy.
    """
    return Score(
        persona_fit     = score_persona_fit(atom, book_context.persona),
        topic_fit       = score_topic_fit(atom, book_context.topic),
        novelty         = score_novelty(atom, book_context.atoms_already_selected),
        arc_coherence   = score_arc_coherence(atom, book_context.preceding_role),
        dup_penalty     = score_duplication_penalty(atom, book_context.fingerprint_index),
        overuse_penalty = score_overuse_penalty(atom, book_context.entropy_tracker),
        total           = weighted_sum(weights_from_policy)
    )
```

**Scoring weights:**

```yaml
# phoenix_v4/policy/injection_scoring.yaml

injection_scoring:
  version: 1
  weights:
    persona_fit: 0.20       # lexical cues match persona registry
    topic_fit: 0.25         # keyword overlap with topic pressure themes
    novelty: 0.15           # penalize if atom's point already used in this book
    arc_coherence: 0.15     # role alignment with neighboring slots and cadence
    duplication_penalty: 0.20  # predicted similarity vs fingerprint index
    overuse_penalty: 0.05   # how often this atom has been used recently
```

**Scoring factors:**

| Factor | What It Measures | How |
|--------|-----------------|-----|
| **persona_fit** | Atom language matches persona | Lexical cue overlap with persona registry (location cues, social patterns) |
| **topic_fit** | Atom addresses topic's core themes | Keyword overlap with `data/story_bank/pressure_themes/` |
| **novelty** | Atom adds something new to this book | 1.0 if point_fingerprint unique in book, 0.0 if duplicate |
| **arc_coherence** | Atom flows from previous slot + adds arc diversity | Role alignment + cadence role compatibility (§8.6) + arc_type diversity in book (§7.0) + exercise pairing bonus from arc registry |
| **dup_penalty** | Atom increases duplication risk | Predicted slot similarity vs fingerprint index (§22.10) |
| **overuse_penalty** | Atom used too often across catalog | Inverse of usage frequency from entropy tracker (§22.9) |

**No-two-same-point constraint:**

Each atom carries a `point_fingerprint`:

```python
# If atom metadata has explicit 'point' field:
point_fingerprint = sha256(normalize(atom.point))
# Otherwise:
point_fingerprint = sha256(normalize(first_sentence(atom.body)))
```

Within a single book, no two story atoms may share the same `point_fingerprint`. Candidates with duplicate point_fingerprints are excluded from the eligible pool before scoring. This is a hard constraint, not a scoring factor.

**Arc diversity constraints (§7.0):**

The plan compiler enforces arc diversity from the arc registry's `diversity_policy`:

- **No adjacent same arc_type:** If chapter N's story atom has `arc_type: collapse`, chapter N+1's story atom cannot also be `collapse`. Candidates with the same arc_type as the previous chapter are excluded from the eligible pool before scoring.
- **Max 2 same arc_type per book:** After 2 atoms of any single arc_type are selected, further candidates with that arc_type are excluded.
- **Min 3 distinct arc_types per book:** If the book has 10 chapters with story atoms and only 2 arc_types are represented after 7 chapters, the remaining selections *must* introduce a third arc_type. Candidates that wouldn't contribute a new arc_type are deprioritized (not excluded, but -0.10 on arc_coherence).
- **Min 2 distinct stake_domains per book:** Same logic — if all selected atoms so far have `stake_domain: career`, candidates with different stake_domains get a +0.05 boost on arc_coherence.

These constraints are applied *before* scoring (hard exclusions) and *during* scoring (soft preferences), matching the pattern of the no-two-same-point constraint.

**Selection trace (explainability):**

Every atom selection produces a trace for debugging and audit:

```
artifacts/plan_compiler/selection_traces/<book_id>.json
```

```json
{
  "book_id": "bk_gzla_anx_saimaa_001",
  "chapter": 1,
  "slot": "slot_02_recognition",
  "eligible_count": 24,
  "top_candidates": [
    {
      "atom_id": "rec_gzla_anx_017",
      "score": { "persona_fit": 0.85, "topic_fit": 0.92, "novelty": 1.0, "arc_coherence": 0.88, "dup_penalty": 0.05, "overuse_penalty": 0.02, "total": 0.87 },
      "selected": true,
      "reason": "top_tier_seed_selected"
    },
    {
      "atom_id": "rec_gzla_anx_003",
      "score": { "total": 0.84 },
      "selected": false
    }
  ],
  "constraints_active": ["no_reuse", "no_duplicate_point", "cadence_role_match"],
  "point_fingerprints_used": ["a3f8c2...", "b7d1e4..."]
}
```

**Properties:**

- Same book request with same pool and same fingerprint index always produces same plan
- Different book_sequence numbers produce different selections
- No randomness — scoring functions and tiebreaking are fully deterministic
- Quality-ranked: better atoms are preferred over worse atoms
- Explainable: selection traces show why each atom was chosen or rejected

### 20.4 Compiled Plan Schema

```yaml
# artifacts/plan_compiler/compiled_plans/<book_id>_plan.yaml

plan:
  book_id: "bk_gzla_anx_saimaa_001"
  format: standard_book
  teacher: sai_maa
  persona: gen_z_la
  topic: anxiety
  overlay: west_la
  book_seed: "a3f8c2..."
  chapters: 10
  compiled_at: <UTC ISO 8601>
  plan_hash: <sha256 of plan content>
  strict_mode: true

  chapter_plans:
    - chapter: 1
      slots:
        - slot_id: slot_01_entry
          atom_id: "sc_entry_gzla_anx_003"
          category: scene
          word_count: 48
        - slot_id: slot_02_recognition
          atom_id: "rec_gzla_anx_017"
          category: story
          word_count: 72
        - slot_id: slot_03_embodiment
          atom_id: "emb_gzla_anx_009"
          category: story
          word_count: 68
        - slot_id: slot_04_exercise_a
          atom_id: "ex_breath_gzla_anx_004"
          category: exercise
          exercise_type: breathwork
          word_count: 85
        - slot_id: slot_05_pattern
          atom_id: "pat_gzla_anx_012"
          category: story
          word_count: 77
        - slot_id: slot_06_mechanism
          atom_id: "mech_gzla_anx_006"
          category: story
          word_count: 81
        - slot_id: slot_07_exercise_b
          atom_id: null               # optional, not filled
          category: exercise
        - slot_id: slot_08_agency
          atom_id: "ag_gzla_anx_020"
          category: story
          word_count: 66
        - slot_id: slot_09_closing
          atom_id: "sc_close_gzla_anx_005"
          category: scene
          word_count: 42
      chapter_word_count: 539
      
    - chapter: 2
      slots:
        - slot_id: slot_10_transition
          atom_id: "sc_trans_gzla_anx_002"
          category: scene
          word_count: 35
        # ... remaining slots
      # ...

  book_word_count: 8420
  atoms_used: 87               # total unique atoms in plan
  atom_reuse_count: 0          # must be 0
  
  validation:
    role_ordering: passed
    exercise_placement: passed
    scene_bracketing: passed
    word_count_bounds: passed
    doctrine_consistency: passed
    k_table_satisfied: true
    duplication_simulation: passed
```

### 20.5 Compilation Failure Behavior

```yaml
# artifacts/plan_compiler/compilation_failures/<book_request_id>.yaml

failure:
  book_request:
    teacher: sai_maa
    persona: gen_z_la
    topic: burnout
    format: standard_book
  failure_type: CAPABILITY_BLOCKED | SLOT_EXHAUSTION | VALIDATION_FAILURE | DUPLICATION_FAILURE
  failure_detail: "Pool exhausted at chapter 9, slot_03_embodiment — only 8 unique embodiment atoms available"
  strict_mode: true
  action_taken: "No book produced. Logged for atom mining prioritization."
  failed_at: <UTC ISO 8601>
```

**Failure types:**

| Type | Cause | Resolution |
|------|-------|------------|
| `CAPABILITY_BLOCKED` | K-table minimum not met for one or more slots | Mine more atoms for the deficit slot type |
| `SLOT_EXHAUSTION` | Pool ran out of unique atoms mid-compilation | Mine more atoms or reduce chapter_count (relaxed mode) |
| `VALIDATION_FAILURE` | Compiled plan fails role ordering, cadence, or doctrine check | Review and fix the offending atoms |
| `DUPLICATION_FAILURE` | Book too similar to existing published book (§21) | Change overlay, adjust book_sequence, or mine differentiated atoms |

### 20.6 Build Manifest

Every successfully compiled and validated book produces a consolidated build manifest. This is the single artifact that proves a book is reproducible, traceable, and governance-complete.

**Location:**

```
artifacts/build_manifests/<book_id>.json
```

**Schema:**

```json
{
  "book_id": "bk_gzla_anx_saimaa_001",
  "build_version": "4.3.0",
  "build_timestamp": "<UTC ISO 8601>",
  
  "inputs": {
    "teacher": "sai_maa",
    "persona": "gen_z_la",
    "topic": "anxiety",
    "format": "standard_book",
    "overlay": "west_la",
    "blueprint": "bp_standard_B",
    "book_sequence": 1
  },
  
  "plan": {
    "plan_hash": "<sha256>",
    "chapters": 10,
    "total_word_count": 8420,
    "atoms_used": 87,
    "atom_reuse_count": 0,
    "strict_mode": true
  },
  
  "atom_manifest": {
    "story_atoms": ["rec_gzla_anx_017", "emb_gzla_anx_009", "..."],
    "exercise_atoms": ["ex_breath_gzla_anx_004", "..."],
    "scene_atoms": ["sc_entry_gzla_anx_003", "..."]
  },
  
  "capability_gate": {
    "status": "CAPABLE",
    "blocking_slots": [],
    "k_table_satisfied": true
  },
  
  "duplication_simulation": {
    "status": "PASSED",
    "paragraph_collisions": 0,
    "sentence_collisions": 1,
    "sixgram_overlap_max": 0.06,
    "structural_fingerprint_unique": true,
    "opening_paragraph_collision": false,
    "closing_paragraph_collision": false,
    "marker_leakage": false,
    "tone_drift_max": 0.28
  },
  
  "entropy_metrics": {
    "blueprint_variant": "bp_standard_B",
    "title_cosine_nearest": 0.42,
    "word_count_band_unique": true,
    "exercise_type_diversity": 4,
    "scene_entry_unique_count": 5
  },
  
  "qa_gates": {
    "role_ordering": "passed",
    "exercise_placement": "passed",
    "scene_bracketing": "passed",
    "doctrine_consistency": "passed",
    "cadence_roles": "passed",
    "metadata_safety": "passed"
  },
  
  "assembly_hash": "<sha256 of final assembled content>",
  "reproducible": true
}
```

**Reproducibility command:**

```bash
make reproduce BOOK_ID=bk_gzla_anx_saimaa_001
# Rebuilds from plan, rehashes, diffs output
# Fails if assembly_hash differs
```

The build manifest is the book's birth certificate. It proves exactly what went in, what was checked, and what came out.

### 20.7 Quarantine Registry

When strict mode blocks a book, the failed compilation is quarantined — not silently retried.

**Location:**

```
artifacts/quarantine_registry.yaml
```

**Schema:**

```yaml
quarantine:
  - book_request_id: "req_gzla_burnout_saimaa_003"
    quarantined_at: <UTC ISO 8601>
    failure_type: CAPABILITY_BLOCKED
    failure_detail: "stillness exercises below k_min (3 available, 4 required)"
    auto_retry: false            # ALWAYS false
    status: quarantined          # quarantined | human_reviewed | re_queued | abandoned
    reviewed_by: null
    reviewed_at: null
    resolution: null             # re_queue | mine_more_atoms | change_format | abandon
    re_queue_count: 0            # tracks how many times human has re-queued
```

**Rules:**

- Failed compilations are **always** quarantined — never silently discarded
- No auto-retry — a human must explicitly review and re-queue
- Re-queue requires the failure reason to be resolved (e.g. more atoms mined, format changed)
- Quarantine registry is append-only — entries are never deleted
- CI gate: no book in `quarantined` status may appear in any release wave
- Quarantine report generated weekly: `artifacts/quarantine_registry_report.json`

**This prevents:**

- Silent retry loops that mask pool depth problems
- "Try again and hope" engineering
- Books that repeatedly fail from consuming pipeline resources
- Drift where engineers ignore failures because they auto-retry

---

## 21. Strict Mode & Capability Gates

### 21.1 Core Philosophy

**Phoenix fails instead of degrades.** This is not a preference — it is a system invariant.

A thin book, a repetitive book, or a book that reuses content is worse than no book. The system must never silently reduce quality to meet a quota.

### 21.2 Strict Mode Flag

```yaml
# phoenix_v4/policy/strict_mode.yaml

strict_mode:
  default: true
  
  # When strict_mode is TRUE:
  rules:
    - capability_check_must_pass: true      # K-table enforcement, no exceptions
    - no_fallback_to_candidate_atoms: true  # never use unapproved content
    - no_chapter_count_reduction: true      # hit max or fail
    - no_atom_reuse_within_book: true       # zero tolerance
    - no_atom_reuse_across_recent_books: true  # per overlap window
    - duplication_simulation_must_pass: true    # §22
    - all_required_slots_must_fill: true
    - partial_assembly_forbidden: true
    
  # When strict_mode is FALSE (relaxed, QA/dev only):
  relaxed_overrides:
    - chapter_count_may_reduce_to_min: true
    - allow_coverage_gaps: true             # provisional atoms allowed
    - duplication_simulation_warning_only: true
    
  # Strict mode may ONLY be disabled for:
  relaxed_allowed_contexts:
    - development_testing
    - qa_campaign_dry_run
    - atom_coverage_assessment
    
  # Strict mode may NEVER be disabled for:
  relaxed_forbidden_contexts:
    - production_assembly
    - any_book_that_will_be_published
    - omega_release_wave_input
```

### 21.3 Capability Gate

The capability gate runs **before** plan compilation and determines whether a book can be produced at the required quality level.

**Tool:**

```
runtime/capability_gate.py
```

**Gate checks (all must pass in strict mode):**

| Check | Requirement | Failure Behavior |
|-------|-------------|-----------------|
| **K-table all slots** | Every slot type meets `k_min` for the format | BLOCKED — no compilation attempted |
| **Combined exercise pool** | Total exercises ≥ `exercise_pool_combined.k_min` | BLOCKED |
| **Doctrine locked** | Teacher doctrine status = locked + approved | BLOCKED |
| **Overlay available** | Requested cultural overlay exists in story_bank | BLOCKED |
| **Recent-book headroom** | Pool depth exceeds atoms used in recent books for same combo | BLOCKED if no unique plan possible |

**Output:** `CAPABLE` / `THIN` / `BLOCKED`

- `CAPABLE` — all K minimums met, pool has headroom beyond k_recommended
- `THIN` — all K minimums met, but some slots below k_recommended (warning)
- `BLOCKED` — one or more K minimums not met (no compilation in strict mode)

### 21.4 No-Fallback Rule

In strict mode, the system **never** falls back to:

- Candidate atoms (unapproved)
- Provisional atoms (unless `V4_QA_ALLOW_PROVISIONAL` is set for QA only)
- Atoms from a different teacher (unless doctrine explicitly allows teacher compatibility)
- Atoms from a different persona (unless persona fallback is enabled and documented)
- Reduced quality thresholds
- Fewer chapters than the format allows at full pool depth
- Recycled atoms from other books in the same combo

**If the pool can't support the book at full quality, produce nothing.**

### 21.5 Persona Fallback Logic

In strict mode, persona fallback is **disabled** — if persona `gen_z_la` has zero atoms for a role, assembly fails. But during QA campaigns and development, controlled fallback prevents total pipeline blockage while maintaining traceability.

**Config:**

```yaml
# phoenix_v4/policy/persona_fallback.yaml

persona_fallback:
  strict_mode: disabled          # NEVER fallback in production
  qa_mode: allowed               # controlled fallback for QA campaigns
  
  fallback_map:
    gen_z_la: ["gen_z"]          # fall back to broader persona
    gen_z_professionals: ["gen_z"]
    healthcare_burnout: ["burned_out_professional"]
    # ... per persona
    
  rules:
    - "Only fallback if primary persona has ZERO atoms for requested role"
    - "Never fallback across topic — persona fallback only"
    - "Never fallback across teacher — teacher purity preserved"
    - "Log EVERY fallback usage"
    
  logging:
    output: artifacts/coverage/fallback_log.json
```

**Fallback log schema:**

```json
{
  "book_id": "bk_gzla_burnout_saimaa_003",
  "requested_persona": "gen_z_la",
  "fallback_persona": "gen_z",
  "role": "embodiment",
  "reason": "zero approved atoms for gen_z_la/burnout/embodiment",
  "timestamp": "<UTC ISO 8601>"
}
```

**CI enforcement:**

- If `strict_mode=true` and any fallback log entry exists for a production book → CI fail
- Fallback log is reviewed before promoting QA results to production readiness
- Persistent fallback usage for a persona × role indicates a mining priority (feed to Golden Phoenix — §5.7)

---

## 22. Book-Level Duplication Simulation

### 22.1 Purpose

Atom-level similarity (§16.1) ensures individual atoms aren't too similar. But at scale (1,000+ books), two books assembled from different atoms can still read too similarly — similar opening patterns, similar exercise rhythms, similar emotional arcs.

The duplication simulation catches **book-level** similarity before publishing.

### 22.2 Tool

```
runtime/duplication_simulator.py
```

### 22.3 Simulation Process

For each newly compiled book plan, the simulator:

```
1. FINGERPRINT GENERATION
   → Compute paragraph-level hashes (sha256 of each hydrated paragraph)
   → Compute sentence-level hashes (sha256 of each sentence)
   → Compute 6-gram fingerprints (sliding window, normalized, lowercased)
   → Compute structural fingerprint (slot sequence + exercise types + scene types)
   
2. COMPARISON
   → Compare against all published books in same (persona, topic) namespace
   → Compare against all books in current release wave
   → Compare against all books across all brands (broader check, higher tolerance)
   
3. COLLISION DETECTION
   → Flag if thresholds exceeded (see §22.4)
```

### 22.4 Duplication Thresholds

```yaml
# phoenix_v4/policy/duplication_thresholds.yaml

duplication_thresholds:

  # ----- Same (persona, topic) namespace -----
  same_namespace:
    paragraph_hash_collision_max: 0       # zero shared paragraphs allowed
    sentence_hash_collision_max: 2        # max 2 identical sentences (common phrases)
    sixgram_overlap_ratio_max: 0.08       # max 8% of 6-grams shared
    structural_fingerprint_identical: false  # slot sequences must differ

  # ----- Same release wave -----
  same_wave:
    paragraph_hash_collision_max: 0
    sentence_hash_collision_max: 1
    sixgram_overlap_ratio_max: 0.05
    title_cosine_max: 0.70
    word_count_band_collision: false       # no two books in same ±500 word band

  # ----- Cross-brand (all published) -----
  cross_brand:
    paragraph_hash_collision_max: 0
    sentence_hash_collision_max: 5        # slightly more tolerant
    sixgram_overlap_ratio_max: 0.12
```

### 22.5 Normalization Pipeline (Versioned)

All duplication checks depend on text normalization. The normalization function must be deterministic and versioned — if normalization changes, all fingerprints must be recomputed.

**Tool:**

```
runtime/normalize.py
```

**Normalization function `N(text)`:**

```python
def normalize(text, version=1):
    """Versioned text normalization. Version tracked in all fingerprint outputs."""
    text = text.lower()                    # lowercase
    text = re.sub(r'[^\w\s]', '', text)    # strip punctuation
    text = re.sub(r'\s+', ' ', text)       # collapse whitespace
    text = text.strip()
    return text
```

**Versioning rules:**

- Normalization version is stored in every fingerprint record (build manifest, fingerprint index, simulation output)
- If normalization function changes → version increments
- Version change triggers: recompute all fingerprints in global index, re-run similarity checks, flag any newly-exceeding pairs
- Two fingerprints computed with different normalization versions cannot be compared — must recompute

### 22.6 Specific Duplication Checks

**Paragraph hash collision:**

```
hash = sha256(normalize(paragraph_text))
```

Any paragraph that appears verbatim in another published book → FAIL.

**Sentence hash collision:**

Same as paragraph but at sentence level. Small tolerance for common short phrases ("You notice it first.") but threshold is low.

**6-gram fingerprint overlap:**

```
For each book:
  tokens = normalize(full_book_text).split()
  sixgrams = set(tuple(tokens[i:i+6]) for i in range(len(tokens)-5))
  
overlap_ratio = len(book_a_sixgrams & book_b_sixgrams) / min(len(book_a_sixgrams), len(book_b_sixgrams))
```

This catches paraphrased similarity — even if no exact sentences match, high 6-gram overlap means the books read too similarly.

**Structural fingerprint:**

```
fingerprint = [slot_types_per_chapter] + [exercise_type_sequence] + [scene_type_sequence]
```

Two books with identical structural fingerprints (same exercise types in same order, same scene types in same order) are too formulaic even if prose differs.

**Recognition-first violation:**

Every chapter must open with a recognition atom. If the duplication simulator finds that all books in a namespace open chapters with recognition atoms that share the same emotional trigger pattern (e.g. all start with "You notice..."), it flags a **recognition-first monotony warning**.

**Opening/closing paragraph collision scan:**

Platform reviewers disproportionately read first and last paragraphs. Two books that open or close identically will be flagged even if the middle 95% differs completely.

```yaml
opening_closing_collision:
  # Hash the first paragraph of chapter 1 and last paragraph of final chapter
  opening_hash: sha256(normalize(chapter_1_paragraph_1))
  closing_hash: sha256(normalize(final_chapter_last_paragraph))
  
  # Zero tolerance — across entire catalog, not just namespace
  max_opening_collisions_catalog: 0
  max_closing_collisions_catalog: 0
  
  # Also check opening paragraphs of ALL chapters (not just ch1)
  per_chapter_opening_collision_max: 0    # within same book
  cross_book_chapter_opening_max: 3       # across catalog (some shared phrasing tolerable)
```

This catches the most common platform review trigger for AI-generated content: formulaic openings and closings that survive even when middle content is unique.

**Marker leakage detection:**

After hydration, the simulator scans final assembled text for unresolved variable markers:

```
Scan for: {{...}} patterns in hydrated output
Any match → HARD FAIL
```

Unresolved markers (e.g. `{{social.hangout_spot}}`, `{{location.neighborhood}}`) indicate hydration failure. A book with visible placeholders cannot be published. This check runs after variable hydration and before final output rendering.

Common causes: missing Story Bank entry for the requested overlay, typo in placeholder name, new placeholder added to atom but not to Story Bank.

**Tone drift scanning:**

Across chapters within a single book, the simulator checks for tone consistency:

```yaml
tone_drift:
  method: sentence_embedding_variance
  model: sentence-transformers/all-MiniLM-L6-v2
  
  checks:
    # Compute embedding centroid per chapter, measure inter-chapter drift
    chapter_centroid_max_distance: 0.40    # max cosine distance between any two chapter centroids
    
    # Check that opening chapters are not dramatically different in tone from closing chapters
    arc_drift_max: 0.35                    # max cosine distance between ch1-3 centroid and ch(N-2)-N centroid
    
    # Flag if any single chapter is an outlier vs book average
    chapter_outlier_threshold: 0.45        # cosine distance from book centroid
```

Tone drift failures indicate:

- An atom from a different teacher's voice slipped through (doctrine compliance issue)
- Exercise atoms have dramatically different register than story atoms
- Scene atoms are stylistically inconsistent with the therapeutic arc

Tone drift is a **WARNING** in strict mode (not hard fail), because some therapeutic arcs intentionally shift tone. But it triggers human review.

### 22.7 Simulation Output

```yaml
# artifacts/duplication_simulation/<book_id>_sim.yaml

simulation:
  book_id: "bk_gzla_anx_saimaa_001"
  status: PASSED | WARNING | FAILED
  compared_against: 47              # number of books compared
  
  results:
    paragraph_collisions: 0
    sentence_collisions: 1
    sixgram_overlap_max: 0.06       # highest overlap with any single book
    sixgram_overlap_against: "bk_gzla_anx_saimaa_003"
    structural_fingerprint_unique: true
    recognition_monotony: false
    marker_leakage: false            # no unresolved {{...}} in hydrated output
    opening_paragraph_collision: false  # no catalog-wide opening match
    closing_paragraph_collision: false  # no catalog-wide closing match
    tone_drift:
      chapter_centroid_max_distance: 0.28
      arc_drift: 0.19
      outlier_chapters: []           # no outlier chapters
    
  verdict: PASSED
  simulated_at: <UTC ISO 8601>
```

### 22.8 Failure Behavior

| Result | Action |
|--------|--------|
| `PASSED` | Book proceeds to hydration and Omega |
| `WARNING` | Book proceeds but flagged for human review |
| `FAILED` | Book is blocked — no output, logged as duplication failure |

In strict mode, `WARNING` and `FAILED` both block.

### 22.9 Slot-Level Entropy Tracking

At 100+ books, the duplication simulator catches book-level similarity. But a subtler problem emerges: the system may be *technically* unique per book while *practically* drawing from a thin slice of the atom pool. Slot entropy tracking measures how many unique atoms are actually being selected per slot type across the catalog.

**Tool:**

```
tools/entropy/slot_entropy_tracker.py
```

**Tracker output:**

```
artifacts/entropy/slot_usage_tracker.json
```

**What it tracks (per 100 books in same persona × topic):**

```yaml
slot_entropy_floors:
  story:
    recognition:     { min_unique_per_100: 25 }
    embodiment:      { min_unique_per_100: 25 }
    pattern:         { min_unique_per_100: 30 }
    mechanism_proof: { min_unique_per_100: 25 }
    agency_glimmer:  { min_unique_per_100: 25 }
  exercise:
    breathwork:      { min_unique_per_100: 15 }
    somatic:         { min_unique_per_100: 15 }
    integration:     { min_unique_per_100: 12 }
    stillness:       { min_unique_per_100: 10 }
    movement:        { min_unique_per_100: 10 }
  scene:
    entry:           { min_unique_per_100: 20 }
    closing:         { min_unique_per_100: 20 }
    transition:      { min_unique_per_100: 15 }
```

**Report output:**

```yaml
# artifacts/entropy/entropy_report_<persona>_<topic>.json
{
  "persona": "gen_z_la",
  "topic": "anxiety",
  "books_analyzed": 142,
  "slot_entropy": {
    "recognition": { "unique_atoms_used": 38, "per_100": 26.7, "floor": 25, "status": "ok" },
    "embodiment": { "unique_atoms_used": 29, "per_100": 20.4, "floor": 25, "status": "BELOW_FLOOR" },
    ...
  },
  "heavy_hitters": [
    { "atom_id": "emb_gzla_anx_003", "usage_count": 18, "percent_of_books": 12.7 }
  ],
  "recommendation": "Mine 10+ new embodiment atoms for gen_z_la/anxiety"
}
```

**Enforcement:**

- Entropy tracking runs after every 50 books compiled for a given persona × topic
- Below-floor slots generate a **mining priority alert** (not a per-book hard fail)
- Heavy hitter atoms (>10% usage across books in scope) are flagged for review
- In strict entropy mode (`V4_ENTROPY_STRICT=true`), a new book that would push a slot below the entropy floor is blocked until more atoms are mined

**Arc entropy tracking (extension):**

The slot entropy tracker also monitors arc_type and stake_domain distribution across compiled books. This catches *emotional sameness* that lexical deduplication misses.

```yaml
# Added to entropy report per persona × topic:

arc_entropy:
  arc_type_distribution:
    collapse: 0.28
    drift: 0.15
    exposure: 0.22
    threshold: 0.12
    consequence: 0.08
    resistance: 0.07
    mirror: 0.05
    return: 0.03
  arc_type_max_ratio: 0.35         # from diversity_policy.per_wave
  status: ok                        # or ABOVE_MAX if any type > 35%
  
  stake_domain_distribution:
    career: 0.42
    relationship: 0.18
    health: 0.15
    identity: 0.12
    social: 0.08
    family: 0.03
    financial: 0.02
  stake_concentration_warning: true  # career > 40% → flag for mining diversity
```

**Rules:**

- Arc entropy is tracked per persona × topic (same scope as slot entropy)
- If any single arc_type exceeds 35% of story atoms in a wave → **mining diversity alert**
- If any single stake_domain exceeds 40% of story atoms in a scope → **mining diversity alert**
- Arc entropy data feeds back to Golden Phoenix agent (§5.7) — coverage gaps now include arc diversity gaps, not just role count gaps

### 22.10 Global Fingerprint Registry

The duplication simulator (§22.3) compares each new book against published books. But at 3,000+ books across 24 brands, per-simulation comparison becomes expensive and risks inconsistency. The global fingerprint registry provides a persistent, append-only index of all compiled books.

**Location:**

```
omega/global_fingerprint_index.json
```

**Fingerprint function:**

```python
book_fingerprint = sha256(
    brand_id +
    persona +
    topic +
    format +
    blueprint_variant +
    "|".join(sorted(story_atom_ids)) +
    "|".join(sorted(exercise_atom_ids)) +
    "|".join(sorted(scene_atom_ids))
)
```

**Rules:**

- Every compiled book's fingerprint is added to the registry at plan compilation time
- Before compilation, the plan compiler checks the fingerprint against the registry
- Identical fingerprint → **hard fail** (duplicate book, even across different brands)
- Registry is append-only — entries are never deleted (deprecated books are marked, not removed)
- Registry is compacted weekly (remove deprecated entries older than 6 months)
- Cross-brand collision = CI failure (§25 gate 22)

**Registry schema:**

```json
{
  "fingerprints": [
    {
      "book_id": "bk_gzla_anx_saimaa_001",
      "brand_id": "stabilizer",
      "fingerprint": "<sha256>",
      "plan_hash": "<sha256>",
      "compiled_at": "<UTC ISO 8601>",
      "status": "active"
    }
  ]
}
```

---

## 23. Content Safety & Escalation Protocol

### 23.1 Purpose

Therapeutic content carries inherent risk. The mining pipeline may encounter self-harm ideation, suicide framing, or trauma triggers. The system must handle these safely without automating clinical judgment.

### 23.2 Safety Scanner

**Tool:** `tools/seed_mining/safety_scanner.py`

```yaml
safety_lexemes:
  self_harm:
    - "kill myself"
    - "end it"
    - "cut myself"
    - "don't want to be here"
    - "better off dead"
    - "no reason to live"
    - "want to disappear"

  suicide_framing:
    - "suicide"
    - "overdose"
    - "jump off"
    - "hang myself"
    - "slit"

  escalation_triggers:
    - "no one would notice"
    - "they'd be better off"
    - "can't take it anymore"
    - "nothing left"

  exercise_safety:
    - "hold your breath until"
    - "don't stop until"
    - "ignore the dizziness"
    - "push through the panic"
    - "remember the worst moment"
    - "go back to when it happened"
```

**Note:** Starter lexicon. Must be maintained by qualified clinical advisor.

### 23.3 Escalation Rules

| Trigger | Action |
|---------|--------|
| Safety lexeme in **human seed** | Flag for clinical review; do not mine |
| Safety lexeme in **candidate atom** | Hard block; reject automatically |
| Safety lexeme in **repair output** | Hard block; no further repair |
| Safety lexeme in **approved atom** (CI) | CI hard failure; manual review |
| Exercise safety lexeme in **exercise** | Hard block; reject; safety flag |

### 23.4 What the System Must NEVER Do

- Never insert crisis hotline language automatically
- Never soften trauma language automatically
- Never add reassurance to "balance" a dark atom
- Never make clinical judgments
- Never suppress a safety flag
- Never auto-generate exercise instructions not in source material

### 23.5 Escalation Log

```yaml
# artifacts/seed_mining/_safety_flags/<id>.yaml
flagged_id: "pf_west_sr_002"
flagged_type: human_seed | candidate_atom | repair_output | exercise_atom
trigger_lexeme: "end it"
trigger_category: self_harm | exercise_safety
flagged_at: <UTC ISO 8601>
reviewed: false
reviewed_by: null
review_outcome: null    # safe | remove | escalate_clinical
```

---

## 24. Determinism & Reproducibility Guarantees

### 24.1 Determinism Rules

| Parameter | Requirement |
|-----------|-------------|
| **LLM temperature** | 0 (if LLM used in any step) |
| **Random seeds** | Fixed: `hashlib.sha256(seed_id.encode()).hexdigest()` |
| **Plan compiler** | Deterministic atom selection (§20.3) |
| **Parallelism** | Output must be identical regardless of execution order |
| **Stochastic behavior** | Forbidden |

### 24.2 Reproducibility Test

```bash
python tools/seed_mining/run_pipeline.py --input seeds/test_pack/ --out /tmp/run_a/
python tools/seed_mining/run_pipeline.py --input seeds/test_pack/ --out /tmp/run_b/
diff -r /tmp/run_a/ /tmp/run_b/
# Expected: no differences
```

### 24.3 Embedding Determinism

Fixed model version for similarity. If updated: recompute all scores, flag atoms exceeding 0.82, log model version.

---

## 25. CI Gates (Mandatory)

CI must fail if:

**Layer 1 — Content Integrity:**

1. Runtime code references `human_seeds/`, `candidate_atoms/`, or unlocked `teacher_doctrine/`
2. Approved atom (any category) lacks `approval` metadata
3. Approved atom has `approval.status` ≠ `approved`
4. Approved atom fails lint or cadence (category-specific)
5. No-auto-promotion family has atom with `promotion_reason: auto_confident`
6. Story role ordering fails on any approved sequence
7. Any approved atom fails word count bounds
8. Body lexeme missing from approved `embodiment` atom
9. Body lexeme missing from approved exercise atom that requires it
10. Sensory lexeme missing from approved `entry` scene
11. Doctrine not locked+approved for any teacher with atoms in `approved_atoms/`
12. Any approved atom contradicts its teacher's `forbidden_framings`

**Layer 1 — Plan Compiler & Quality:**

13. Plan compiled with strict_mode=false for production context
14. Any compiled plan has atom_reuse_count > 0
15. Any compiled plan fails duplication simulation
16. Any book published without passing capability gate
17. Compiled plan hash doesn't match assembly output hash (tampering check)
18. Opening paragraph hash collision detected across catalog (§22.6)
19. Closing paragraph hash collision detected across catalog (§22.6)
20. Quarantined book appears in any release wave (§20.7)
21. Published book lacks build manifest (§20.6)

**Layer 2 — Omega:**

22. Omega code imports from `approved_atoms/`, `candidate_atoms/`, `human_seeds/`, or `teacher_doctrine/`
23. Omega modifies `book_assembly` content (hash verified)
24. Brand exceeds quarterly quota
25. Release wave violates similarity protection
26. Title duplicates within or across brands
27. SKUs not unique
28. Platform exports invalid (schema-checked)
29. Metadata contains blocked terms (§34.6) — medical claims, therapeutic overclaims, or platform-risk language
30. More than 6 brands publishing on same calendar day (§30.2)

**Layer 1 — Semantic Quality (V4.4):**

31. Approved atom exceeds 0.82 cosine similarity to another approved atom in same scope (§16.1)
32. Approved atom scope exceeds filler density threshold (§16.3.1)
33. Book fingerprint collision in global fingerprint registry (§22.10)

**Layer 2 — Naming Engine:**

34. Mechanism blacklist word appears in any title or subtitle (§29.2.2)
35. Any title missing primary keyword from both title and subtitle (§29.2.3)
36. Title cosine similarity > 0.90 or 3-gram overlap > 0.65 vs existing title (§29.2.3)
37. Same title skeleton pattern > 3 times in one wave (§29.2.6)

**Layer 1 — Narrative Diversity:**

38. Story atom missing `arc_type` or `stake_domain` metadata (§7.0)
39. Compiled book violates arc diversity policy: adjacent same arc_type, >2 same arc_type, <3 distinct arc_types, or <2 distinct stake_domains (§7.0)

**CI is the final authority.**

**CI exit code contract:**

| Code | Status | Meaning |
|------|--------|---------|
| `0` | **GREEN** | All gates passed |
| `10` | **YELLOW** | Warnings exist but no hard failures (QA mode only) |
| `1` | **RED** | Any hard failure — blocks merge/release |

- On QA pipelines: exit code 10 is allowed but annotated (warnings visible)
- On RELEASE pipelines: exit code 10 is treated as failure (no warnings in production)
- All CI tools (`k_table_enforce`, `duplication_sim`, `metadata_policy_scan`, etc.) must conform to this contract

### 25.1 Pre-Release QA Campaign (1000-Book Validation)

Before any production release wave, the system must validate at scale. Individual CI gates catch per-atom and per-book issues. The QA campaign validates the *system* — that 1,000 books can compile, assemble, and pass all gates without systemic failure.

**Command:**

```bash
make v4_qa_1000
```

**Behavior:**

- Compiles 1,000 book plans across the full persona × topic × teacher matrix
- Runs the complete gate stack per book: role ordering, duplication simulation, lint, cadence, doctrine consistency, semantic similarity, K-table, capability gate
- Appends results to JSONL (resumable — skips already-run book_ids)
- Logs failures without stopping the campaign (collect all failures, don't halt on first)
- In QA mode: may use provisional atoms (`V4_QA_ALLOW_PROVISIONAL=true`) and persona fallback

**Output:**

```
artifacts/v4_qa_results.jsonl
```

**Per-book entry:**

```json
{
  "book_id": "bk_gzla_anx_saimaa_001",
  "persona": "gen_z_la",
  "topic": "anxiety",
  "teacher": "sai_maa",
  "format": "standard_book",
  "status": "OK",
  "chapters_compiled": 10,
  "atoms_used": 87,
  "provisional_used": false,
  "fallback_used": false,
  "duplication_status": "PASSED",
  "entropy_warnings": [],
  "gate_failures": []
}
```

**Campaign summary:**

```bash
make v4_qa_summary
```

Outputs:

```yaml
qa_summary:
  total_attempted: 1000
  passed: 947
  failed: 53
  pass_rate: 0.947
  provisional_usage_rate: 0.12     # % of books using provisional atoms
  fallback_usage_rate: 0.03        # % of books using persona fallback
  duplication_warnings: 7
  coverage_gaps:
    - { persona: gen_z_la, topic: burnout, role: stillness, available: 2, needed: 4 }
    - { persona: healthcare_burnout, topic: grief, role: mechanism_proof, available: 0, needed: 12 }
  top_failure_reasons:
    - { reason: "CAPABILITY_BLOCKED", count: 28 }
    - { reason: "SLOT_EXHAUSTION", count: 15 }
    - { reason: "DUPLICATION_FAILURE", count: 10 }
  recommendation: "Mine 15+ atoms for healthcare_burnout/grief before production"
```

**Production readiness rule:**

- QA campaign must achieve ≥ 95% pass rate before any production release wave
- All coverage gaps must be resolved (Golden Phoenix + human review)
- Provisional usage rate must be 0% for production-targeted books
- Fallback usage rate must be 0% for production-targeted books

### 25.2 Coverage Verification Gate (Pre-Release-Wave)

Before any Omega release wave is generated, coverage must be verified for all books in the wave.

**Command:**

```bash
make v4_story_coverage
```

**Output:**

```
artifacts/coverage/story_atoms_coverage.json
```

**Per persona × topic entry:**

```json
{
  "persona": "gen_z_la",
  "topic": "anxiety",
  "teacher": "sai_maa",
  "status": "READY",
  "roles": {
    "recognition": { "approved": 24, "k_min": 12, "status": "ok" },
    "embodiment": { "approved": 22, "k_min": 12, "status": "ok" },
    "pattern": { "approved": 18, "k_min": 12, "status": "ok" },
    "mechanism_proof": { "approved": 15, "k_min": 12, "status": "ok" },
    "agency_glimmer": { "approved": 20, "k_min": 12, "status": "ok" }
  },
  "exercises_ready": true,
  "scenes_ready": true
}
```

**READY definition:**

- All 5 story roles ≥ K-table `k_min` for the requested format
- All required exercise types ≥ K-table `k_min`
- All required scene types ≥ K-table `k_min`
- No missing required roles (zero = hard block)
- All atoms are `approved` status (no provisional in READY assessment)
- Doctrine locked and approved for teacher

**Enforcement:**

- `make v4_story_coverage` must pass before `release_wave_generator.py` (§30) will execute
- Any persona × topic marked NOT_READY → those books excluded from the wave
- Coverage report is stored and version-stamped for audit trail

---

# LAYER 2 — OMEGA ORCHESTRATOR (BUSINESS LOGIC)

---

## 26. Omega Orchestrator — Purpose & Boundaries

### 26.1 What Omega Does

Omega decides **which already-assembled books go where, when, under what brand, at what price**.

### 26.2 What Omega Never Does

- Never modifies atom content
- Never accesses Layer 0 or Layer 1 content directories
- Never makes therapeutic decisions
- Never changes assembly sequences
- Never selects atoms directly

**Omega composes plans. Layer 1 composes content.**

### 26.3 Omega's Input

Omega receives **sealed book assemblies** from Layer 1:

```yaml
book_assembly:
  book_id: "bk_gzla_anx_saimaa_001"
  persona: gen_z_la
  topic: anxiety
  teacher_id: "sai_maa"
  format: standard_book
  chapters: 10
  total_word_count: 8420
  assembly_hash: <sha256>
  assembled_at: <UTC ISO 8601>
  validation_passed: true
  duplication_simulation: passed
  strict_mode: true
  blueprint_id: "bp_standard_A"    # which blueprint variant (§28)
```

---

## 27. Brand Registry

### 27.1 Structure

```yaml
# omega/brand_registry/<brand_id>.yaml
brand_id: "mindful_harbor"
brand_name: "Mindful Harbor"
brand_number: 7
status: active
persona_targets: [gen_z_la, gen_z_professionals]
topic_coverage: [anxiety, burnout, stress]
teacher_affiliations: [sai_maa, kevin_costner]
format_mix:
  standard_book: 0.60
  short_form: 0.25
  deep_dive: 0.15
pricing:
  floor: 2.99
  ceiling: 9.99
  default: 4.99
platform: google_play
quarterly_quota: 42
```

### 27.2 Brand Matrix

**Tool:** `tools/omega/brand_matrix_compiler.py`

Computes total books per quarter, persona × topic × teacher coverage per brand, overlap detection, format distribution enforcement.

---

## 28. Blueprint Rotation & Structural Entropy

### 28.1 Why Blueprint Rotation Matters

If every `standard_book` uses the exact same chapter_arc (same slot order, same exercise type preferences, same transition pattern), platform algorithms may detect structural similarity even if prose content differs.

Blueprint rotation creates **structural variety** across books.

### 28.2 Blueprint Variants

```
omega/blueprint_rotation/
├── standard_book/
│   ├── bp_standard_A.yaml    # exercise-first emphasis
│   ├── bp_standard_B.yaml    # somatic-heavy variant
│   ├── bp_standard_C.yaml    # stillness-integrated variant
│   └── bp_standard_D.yaml    # movement-rich variant
├── short_form/
│   ├── bp_short_A.yaml
│   └── bp_short_B.yaml
└── deep_dive/
    ├── bp_deep_A.yaml
    └── bp_deep_B.yaml
```

**Blueprint variant differences:**

```yaml
# bp_standard_A.yaml — exercise-first emphasis
variant_id: bp_standard_A
base_format: standard_book
overrides:
  slot_04_exercise_a:
    preferred_types: [breathwork, somatic]    # breathwork/somatic first
    weight: [0.5, 0.3, 0.1, 0.1]             # weighted preference
  slot_07_exercise_b:
    required: true                             # make optional slot required
    preferred_types: [integration]
  inter_chapter:
    exercise_type_pattern: alternating         # alternate exercise types across chapters

# bp_standard_B.yaml — somatic-heavy
variant_id: bp_standard_B
base_format: standard_book
overrides:
  slot_04_exercise_a:
    preferred_types: [somatic, movement]
    weight: [0.6, 0.3, 0.1]
  slot_07_exercise_b:
    required: false                            # keep optional
  inter_chapter:
    exercise_type_pattern: clustered           # group similar exercises
```

### 28.3 Blueprint Assignment

**Tool:** `tools/omega/blueprint_assigner.py`

Rules:

- No two books in the same release wave use the same blueprint
- No three consecutive books for the same (persona, topic) use the same blueprint
- Blueprint assignment is deterministic (based on book_sequence hash)
- Blueprint rotation logged in `omega/blueprint_rotation/assignment_log.yaml`

---

## 29. Catalog Planning, SKU Generation & Naming Engine

### 29.0 Catalog Planning Hierarchy

The spec defines how atoms become books (§20), how books are deduplicated (§22), and how brands publish (§30). But it did not define *which books to create in the first place*. Without a planning hierarchy, the system can produce 1,000 structurally valid books that nobody searches for, or 50 books that all target the same micro-niche.

The catalog planner operates at three levels:

```
Level 1 — Domain (emotional territory)
  │  anxiety, burnout, grief, sleep, adhd...
  │  Source: topic registry (existing)
  │
Level 2 — Series (reader-world search topic)
  │  social anxiety, panic attacks, health anxiety, GAD...
  │  Source: domain decomposition templates
  │  Each domain produces 6–12 series
  │
Level 3 — Angle Book (high-frequency scenario)
     social anxiety at work, dating anxiety, public speaking anxiety...
     Source: angle generator per series
     Each series produces 3–12 angle books (capacity-dependent)
     
Level 4 — Internal Therapeutic Spine
     Recognition → embodiment → pattern → mechanism → agency → integration
     Source: plan compiler (§20) assembles from approved atoms
     This level already exists. Levels 1–3 are the planning layer above it.
```

**The critical insight:** "Reassurance Addiction in GAD" is a powerful chapter but a terrible book title. Nobody searches for it. The domain→series→angle hierarchy ensures books are named at the altitude where real people search, while the internal spine (atoms) handles the therapeutic depth.

**Tool:**

```
tools/omega/catalog_planner.py
```

**Directory structure:**

```
omega/catalog_planning/
├── domains/                         # Level 1 — one file per domain
│   ├── anxiety.yaml
│   ├── burnout.yaml
│   └── grief.yaml
├── series/                          # Level 2 — generated from domain decomposition
│   ├── anxiety/
│   │   ├── social_anxiety.yaml
│   │   ├── panic_attacks.yaml
│   │   └── health_anxiety.yaml
│   └── burnout/
│       ├── workplace_burnout.yaml
│       └── caregiver_burnout.yaml
├── angles/                          # Level 3 — generated per series
│   ├── social_anxiety/
│   │   ├── at_work.yaml
│   │   ├── dating.yaml
│   │   └── public_speaking.yaml
│   └── panic_attacks/
│       ├── at_night.yaml
│       └── driving.yaml
└── planning_output/
    └── catalog_plan_<quarter>.yaml  # final approved plan
```

**Domain decomposition templates (Level 1 → 2):**

Each domain has a decomposition template defining how it splits into series:

```yaml
# omega/catalog_planning/domains/anxiety.yaml

domain_id: anxiety
decomposition:
  method: clinical_subtypes + scenario_clusters
  series:
    - series_id: social_anxiety
      description: "Fear and avoidance in social situations"
      search_keywords: ["social anxiety", "social phobia", "fear of people"]
      persona_affinity: [gen_z_la, gen_z_professionals, nyc_executives]
      
    - series_id: panic_attacks
      description: "Acute panic episodes and anticipatory anxiety"
      search_keywords: ["panic attacks", "panic disorder", "anxiety attacks"]
      persona_affinity: [healthcare_burnout, gen_z_la]
      
    - series_id: health_anxiety
      description: "Excessive worry about physical symptoms and illness"
      search_keywords: ["health anxiety", "hypochondria", "medical anxiety"]
      persona_affinity: [longevity_optimizers, healthcare_burnout]
```

**Angle generation (Level 2 → 3):**

For each series, the angle generator produces scenario-specific book candidates:

```yaml
# omega/catalog_planning/series/anxiety/social_anxiety.yaml

series_id: social_anxiety
domain_id: anxiety

angle_generation:
  templates:
    - type: environment      # WHERE it happens
      angles: [at_work, at_school, at_parties, online, in_public]
    - type: relationship     # WITH WHOM
      angles: [dating, friendships, authority_figures, strangers]
    - type: trigger          # WHAT triggers it
      angles: [public_speaking, phone_calls, networking, conflict]
    - type: identity         # WHO you are
      angles: [for_introverts, for_new_employees, for_parents]

  max_angles_per_series: 12
  min_angles_per_series: 4
```

### 29.0.1 Capacity-Aware Series Sizing

Not every series can support the same number of angle books. A series with 40 recognition atoms can support more books than one with 12. The capacity score determines the safe book count per series before entropy collapse.

**Capacity formula:**

```python
def compute_capacity(series_id, persona, topic):
    """
    Determines how many books a series can safely produce
    without atom exhaustion or duplication collapse.
    """
    roles = ['recognition', 'embodiment', 'pattern', 'mechanism_proof', 'agency_glimmer']
    
    # Average atoms per role for this persona × topic
    avg_atoms = mean([count_approved(persona, topic, role) for role in roles])
    atoms_per_book = format_policy.atoms_required  # from K-table
    
    # Unique mechanism clusters (semantic groupings)
    mechanism_clusters = count_unique_clusters(persona, topic, 'mechanism_proof')
    required_clusters = 4  # minimum for meaningful variation
    
    # Heavy hitter rate from entropy tracker
    heavy_hitter_rate = get_heavy_hitter_rate(persona, topic)
    
    # Raw capacity
    raw_capacity = (avg_atoms / atoms_per_book) * (mechanism_clusters / required_clusters)
    
    # Apply entropy modifier — heavy reuse shrinks effective capacity
    effective_capacity = raw_capacity * (1 - heavy_hitter_rate)
    
    # Clamp to safe bounds
    return clamp(floor(effective_capacity), min=3, max=12)
```

**Capacity thresholds:**

```yaml
# phoenix_v4/policy/catalog_planning.yaml

capacity_thresholds:
  min_safety_margin: 1.2          # capacity must exceed 1.2× planned book count
  max_heavy_hitter_rate: 0.25     # if >25% of atoms are heavy hitters, cap series
  min_semantic_delta_avg: 0.55    # if avg semantic delta < 0.55, pool is too homogeneous
  min_mechanism_clusters: 4       # fewer than 4 distinct mechanism clusters → too thin
```

**Hard guards — the planner must refuse to create:**

- Topics with capacity < 1.2× planned book count
- Topics with heavy_hitter_rate > 0.25
- Topics where semantic_delta_avg < 0.55
- Topics where duplication risk exceeds threshold (§22.4)

No exceptions. If the atom pool can't support the planned series size, the planner shrinks the series or blocks it until more atoms are mined.

### 29.0.2 Angle Legitimacy Filter

At 27 domains × 8 series × 10 angles × 17 personas, unconstrained angle generation produces thousands of candidates. Most will be redundant. The legitimacy filter gates every angle before it becomes a planned book.

**Every angle must pass three gates:**

**Gate 1 — Recognition Strength:**

Would this persona say "yes, that's me" — not "that's vaguely related"?

```yaml
recognition_test:
  required: true
  method: "persona_lexeme_overlap + scenario_specificity"
  min_score: 0.70
  
  # A high recognition score means:
  # - The angle names a specific situation (not a general feeling)
  # - The angle uses persona-world language (not clinical language)
  # - A person in this persona would search for this or click on this title
```

**Gate 2 — Mechanism Density:**

Can this angle support a full book's worth of therapeutic content?

```yaml
mechanism_density:
  required: true
  min_recognition_atoms: 8
  min_mechanism_atoms: 6
  min_embodiment_arcs: 4
  min_exercises: 4
  
  # If the angle can't fill these minimums from the approved atom pool,
  # it's a chapter, not a book.
```

**Gate 3 — Differentiation Index:**

Is this angle materially different from other angles in the same series and from other personas' versions?

```yaml
differentiation:
  required: true
  min_cosine_distance_same_series: 0.30    # from other angles in this series
  min_cosine_distance_cross_persona: 0.25  # from same angle in another persona
  max_keyword_overlap_same_series: 0.50    # keyword dedup
  
  # "Social Anxiety at Work" and "Workplace Social Fear" are duplicates.
  # "Social Anxiety at Work" and "Social Anxiety While Dating" are distinct.
```

**Planner output (per quarter):**

```yaml
# omega/catalog_planning/planning_output/catalog_plan_Q2_2026.yaml

plan:
  quarter: Q2-2026
  
  approved_series:
    - series_id: social_anxiety
      domain_id: anxiety
      score: 0.83
      safe_book_count: 9
      approved_angles:
        - { angle_id: at_work, recognition: 0.93, capacity: ok, differentiation: ok }
        - { angle_id: dating, recognition: 0.88, capacity: ok, differentiation: ok }
        - { angle_id: public_speaking, recognition: 0.91, capacity: ok, differentiation: ok }
      rejected_angles:
        - { angle_id: networking_events, reason: "differentiation fail — too close to at_work (cosine 0.82)" }
        
    - series_id: panic_attacks
      domain_id: anxiety
      score: 0.79
      safe_book_count: 7
      
  rejected_series:
    - { series_id: anxiety_about_weather, reason: "recognition score 0.31 — too niche" }
    - { series_id: existential_dread, reason: "capacity 0.8 — below 1.2× safety margin" }
```

### 29.1 SKU Planner

**Tool:** `tools/omega/sku_planner.py`

```yaml
sku: "MH-GZLA-ANX-SM-SB-001-Q1-2026"
# brand-persona-topic-teacher-format-sequence-quarter-year
```

### 29.2 Naming Engine (SEO-Aware, Recognition-Gated)

**Tool:** `tools/omega/naming_engine.py`

**Purpose:** Generate standalone, recognition-strong book titles and subtitles that are SEO-aligned, persona-aware, duplication-safe, and deterministic. This replaces simple title template rendering with a scored, validated naming pipeline.

**Module layout:**

```
phoenix_v4/naming/
├── keyword_bank.py       # keyword registries per domain/series/angle
├── intent.py             # intent classification (scenario, solution, crisis, identity)
├── templates.py          # title/subtitle structural templates
├── generator.py          # candidate generation (deterministic)
├── scorer.py             # multi-factor title scoring
├── dedupe.py             # title similarity + collision detection
├── validator.py          # hard gates (mechanism blacklist, length, keyword presence)
└── cli.py                # CLI entry point
```

**Components (file registry):**

```
omega/title_entropy/
├── title_stems.yaml           # pre-approved title roots
├── subtitle_patterns.yaml     # structural patterns for subtitles
├── forbidden_title_words.yaml # words that trigger platform filters
├── mechanism_blacklist.yaml   # clinical/mechanism terms banned from titles (NEW)
├── intent_taxonomy.yaml       # search intent classification (NEW)
├── persona_title_flavor.yaml  # persona-specific vocabulary for titles
├── title_collision_index.json # running index of all generated titles
└── entropy_report.json        # diversity metrics
```

#### 29.2.1 Intent Taxonomy

Every title must align with a search intent class. Books named at the wrong intent altitude fail to convert.

```yaml
# omega/title_entropy/intent_taxonomy.yaml

intents:
  scenario_specific:
    description: "Specific situation the reader is in"
    examples: ["at work", "in meetings", "at night", "while driving"]
    recognition_boost: 0.15    # highest conversion
    
  solution_seeking:
    description: "Reader wants an outcome"
    examples: ["how to stop", "tools for", "steps to calm", "overcome"]
    recognition_boost: 0.10
    
  identity_based:
    description: "Reader identifies with a group"
    examples: ["for introverts", "for new parents", "for students"]
    recognition_boost: 0.10
    
  crisis:
    description: "Reader is in acute distress"
    examples: ["can't stop worrying", "panic at night", "spiraling"]
    recognition_boost: 0.05    # high engagement but narrow
    
  informational:
    description: "Reader wants to understand"
    examples: ["what is", "understanding", "why you feel"]
    recognition_boost: 0.0     # lowest conversion — avoid for titles
```

#### 29.2.2 Mechanism Blacklist

Clinical and mechanism terms that belong inside the book, never in titles or subtitles. These terms cause "curriculum module" titles that fail the recognition test.

```yaml
# omega/title_entropy/mechanism_blacklist.yaml

mechanism_blacklist:
  clinical_terms:
    - spotlight effect
    - cognitive defusion
    - intolerance of uncertainty
    - operant conditioning
    - exposure hierarchy
    - limbic system
    - amygdala hijack
    - schema therapy
    - polyvagal
    - window of tolerance
    - nervous system regulation
    - somatic experiencing
    
  abstraction_terms:
    - neurological pathway
    - behavioral pattern disruption
    - cognitive restructuring
    - emotional processing
    - psychoeducation
    - metacognitive awareness
    
  enforcement: hard_reject   # any match in title or subtitle → reject candidate
```

**Exception:** Brands with `clinical_imprint: true` in brand registry may use clinical terms. Default brands may not.

#### 29.2.3 Title Scoring

Four scores, not five. The previous draft had overlapping dimensions (recognition, conversion, abstraction_penalty). Consolidated to eliminate ambiguity:

```
Total Score = SEO Score + Human Appeal Score - Duplication Risk - Penalty Score
```

Each score is 0.0–1.0. Total can range from -1.0 to 2.0 (in practice 0.5–1.8 for valid candidates).

**Policy file:**

```yaml
# phoenix_v4/policy/naming_scoring.yaml

naming_scoring:
  version: 2
  model: "seo + human_appeal - dup_risk - penalties"
  min_total_score: 0.80    # candidates below this are rejected
```

---

**SEO Score (max 1.0) — deterministic, no external APIs:**

| Condition | Points |
|-----------|--------|
| Primary keyword appears in title | +0.50 |
| Primary keyword appears in subtitle (if not in title) | +0.30 |
| 1–3 secondary keywords appear in subtitle | +0.10 |
| Title matches intended intent template class (§29.2.1) | +0.10 |

Hard rules:

- Primary keyword appears nowhere (title or subtitle) → **reject** (not scored, eliminated)
- Same keyword stem repeated >2 times across title+subtitle → -0.10 penalty

---

**Human Appeal Score (max 1.0) — the core gate:**

This is what separates "Social Anxiety at Work" from "The Spotlight Effect in Professional Environments." Every point is earned from a specific lexeme registry lookup — no vibes, no subjective judgment.

**Recognition signals (+):**

| Signal | Points | Source |
|--------|--------|--------|
| Scenario lexeme present ("at work", "in meetings", "at night", "on dates") | +0.25 | `policy/recognition_lexemes.yaml → scenario_words` |
| Persona-world lexeme present ("billable hours", "hospital shift", "startup pitch") | +0.25 | `policy/recognition_lexemes.yaml → persona_lexemes` |
| Distress verb present ("freeze", "spiral", "overthink", "panic", "shut down") | +0.20 | `policy/recognition_lexemes.yaml → distress_verbs` |
| Outcome clarity ("How to…", "Stop…", "Feel Confident…", "Calm…") | +0.20 | `policy/recognition_lexemes.yaml → outcome_phrases` |
| Specificity bonus ("in Meetings" scores higher than "at Work") | +0.10 | Depth-of-scenario heuristic: 3+ word scenario phrase |

**Abstraction penalties (-):**

| Signal | Penalty | Source |
|--------|---------|--------|
| Mechanism blacklist word in title or subtitle | -0.25 | `omega/title_entropy/mechanism_blacklist.yaml` |
| Abstract noun dominance (>50% of title nouns are abstract) | -0.15 | POS tag analysis on title |
| Metaphor-only title without keyword anchor | -0.10 | Title lacks primary keyword AND lacks scenario lexeme |

A title can score above 1.0 on the recognition signals, but abstraction penalties pull it down. Net max is 1.0 (clamped).

---

**Duplication Risk (0.0–1.0, lower is better):**

Computed against three scopes, worst score wins:

```python
dup_risk = max(
    tfidf_cosine_sim_vs_catalog_titles,
    tfidf_cosine_sim_vs_wave_titles,
    tfidf_cosine_sim_vs_series_titles
)
```

**Plus 3-gram overlap check:**

```python
ngram_risk = trigram_overlap_ratio(candidate_title, nearest_existing_title)
```

**Hard fail thresholds:**

- `cosine > 0.90` → **reject** (not scored, eliminated)
- `ngram_overlap > 0.65` → **reject**

**Soft penalty:**

- Same skeleton pattern used >3 times in current wave → +0.15 to dup_risk

---

**Penalty Score (0.0–1.0):**

Aggregates non-content penalties:

| Condition | Penalty |
|-----------|---------|
| Title exceeds max length (60 chars standard, 50 chars pocket) | +0.30 |
| Keyword stuffing (>2 repetitions of same stem) | +0.10 |
| No outcome verb or promise phrase in subtitle | +0.10 |
| Same template skeleton as another book in same series | +0.10 |

---

**Hard validators (fail-fast, before scoring):**

These eliminate candidates entirely — they never reach the scorer:

- Mechanism blacklist match in title → **reject**
- Primary keyword absent from both title and subtitle → **reject**
- Title cosine similarity > 0.90 vs any existing title → **reject**
- 3-gram overlap > 0.65 vs any existing title → **reject**
- Title exceeds max length → **reject**
- Same title skeleton > 3 times in one wave → **reject**

#### 29.2.4 Recognition Lexeme Registry

The Human Appeal score pulls from a single canonical registry. Without this file, scoring is subjective. With it, scoring is a lookup.

**File:** `phoenix_v4/policy/recognition_lexemes.yaml`

```yaml
# phoenix_v4/policy/recognition_lexemes.yaml

version: 1

scenario_words:
  # WHERE / WHEN the struggle happens
  - at work
  - in meetings
  - at night
  - on dates
  - during presentations
  - during hospital shifts
  - in the classroom
  - at family gatherings
  - while driving
  - in public
  - on the phone
  - during interviews
  - at networking events
  - before deadlines
  - in the morning

distress_verbs:
  # WHAT the struggle feels like (action/state verbs)
  - freeze
  - spiral
  - panic
  - overthink
  - shut down
  - dread
  - avoid
  - ruminate
  - dissociate
  - catastrophize
  - withdraw
  - procrastinate

outcome_phrases:
  # WHAT the reader wants (promise language)
  - how to stop
  - how to calm
  - feel confident
  - speak up
  - sleep better
  - stop worrying
  - find calm
  - take control
  - break free
  - let go
  - feel safe

persona_lexemes:
  # WHO the reader is (per-persona world language)
  gen_z_la:
    - content creator
    - social media
    - comparison trap
    - hustle culture
  gen_z_professionals:
    - networking
    - startup
    - performance review
    - imposter syndrome
    - first job
  healthcare_burnout:
    - shift
    - patient load
    - charting
    - compassion fatigue
    - on call
  nyc_executives:
    - board meeting
    - quarterly review
    - leadership
    - high stakes
    - stakeholders
  longevity_optimizers:
    - biohacking
    - recovery protocol
    - cortisol
    - sleep architecture
```

This registry is maintained, not generated. New scenario words, distress verbs, and persona lexemes are added as personas and domains expand. The naming engine reads this file at runtime — no hardcoded lists in code.

#### 29.2.5 Title Generation Pipeline

```
Step A — Generate N candidates from templates × keyword bank × angle
         Deterministic: seed = sha256(book_id + persona + angle + brand)
         Use seeded shuffle on template list, generate first 12 candidates
         
Step B — Hard validation pass (reject blacklisted, overlength, missing keyword,
         cosine > 0.90, ngram > 0.65)

Step C — Score surviving candidates: SEO + Human Appeal - Dup Risk - Penalties

Step D — Reject candidates below min_total_score (0.80)

Step E — Select highest total score
         Tiebreak: deterministic by candidate_id (alphabetical)

Step F — Emit naming trace to plan artifact
```

**Template policy:**

```yaml
template_policy:
  max_templates_per_intent_per_format: 6   # prevents template explosion
  allow_metaphor_titles: false              # unless keyword-anchored in subtitle
  require_scenario_or_outcome: true         # every title must have one or both
```

**Template examples:**

```yaml
# omega/title_entropy/subtitle_patterns.yaml

title_templates:
  scenario_direct:     "{PrimaryKeyword}"
  scenario_promise:    "{PrimaryKeyword}: {PromiseClause}"
  persona_targeted:    "{PrimaryKeyword} for {PersonaRole}"
  outcome_focused:     "How to {OutcomeVerb} When You {ScenarioPhrase}"
  
subtitle_templates:
  three_part:          "{Benefit1}, {Benefit2}, and {Benefit3}"
  how_to_stack:        "How to {Action1}, {Action2}, and {Action3}"
  persona_anchor:      "A {FormatType} Guide for {PersonaDescription}"
```

**Example output (4-score model):**

```yaml
naming:
  title: "Social Anxiety at Work"
  subtitle: "How to Speak Up in Meetings, Stop Overthinking, and Feel Confident Around Colleagues"
  keywords:
    primary: ["social anxiety at work"]
    secondary: ["meeting anxiety", "fear of speaking up", "workplace confidence"]
  intent: scenario_specific
  scores:
    seo: 0.90          # primary keyword in title (+0.50) + secondary in subtitle (+0.10) + intent match (+0.10) + subtracted nothing
    human_appeal: 0.95  # scenario "at work" (+0.25) + persona "meetings" (+0.25) + distress "overthinking" (+0.20) + outcome "speak up, feel confident" (+0.20) + specificity "in meetings" (+0.10) - no penalties
    dup_risk: 0.07      # low similarity to existing catalog
    penalties: 0.0      # no violations
    total: 1.78         # 0.90 + 0.95 - 0.07 - 0.0
  trace:
    template_id: scenario_direct + three_part
    candidates_generated: 12
    candidates_rejected: 4
    rejection_reasons: ["mechanism_leak: 1", "over_length: 2", "dup_collision: 1"]
    top_3: [
      { title: "Social Anxiety at Work", total: 1.78 },
      { title: "Meeting Anxiety: How to Stop Freezing Up", total: 1.65 },
      { title: "Workplace Anxiety: A Guide for Professionals", total: 1.52 }
    ]
```

#### 29.2.6 Entropy Rules (updated)

| Rule | Threshold |
|------|-----------|
| No two titles same brand | cosine < 0.70 |
| No two titles same wave | cosine < 0.60 |
| No two titles cross-brand same persona+topic | cosine < 0.75 |
| Title pattern diversity | No more than 30% of titles in any single structural pattern |
| Subtitle uniqueness | No repeated subtitles within a brand |
| Same skeleton per wave | Max 3 instances of same template pattern |

**Title deduplication is offline** — TF-IDF vectors on normalized titles, no embeddings required.

**Title generation is constrained, not creative.** Titles are assembled from pre-approved components, scored, and validated. No LLM in release mode.

### 29.3 Persona-Seed Diversification

Within a single (persona, topic) combination, books are diversified across:

| Diversification Lever | Method |
|----------------------|--------|
| **Teacher** | Different teacher doctrines produce different therapeutic framing |
| **Cultural overlay** | Different location/cultural variables produce different sensory context |
| **Blueprint variant** | Different structural patterns (§28) |
| **Book sequence** | Different atom selection via deterministic seed rotation |
| **Format** | standard_book vs short_form vs deep_dive |

### 29.4 Word-Length Variance Distribution

To prevent platform detection of formulaic word counts:

```yaml
word_length_variance:
  standard_book:
    target_range: [6000, 14000]
    distribution: uniform            # not clustered at one length
    band_width: 1000                 # no two same-combo books within ±500 words
  short_form:
    target_range: [2000, 5000]
    distribution: uniform
    band_width: 500
  deep_dive:
    target_range: [12000, 20000]
    distribution: uniform
    band_width: 1500
```

The plan compiler adjusts chapter_count within format bounds to hit a target word count that avoids clustering with other books in the same namespace.

---

## 30. Release Wave Scheduling

### 30.1 Tool

```
tools/omega/release_wave_generator.py
```

### 30.2 Wave Rules

**Scope: Wave limits apply per brand, not globally across the catalog.**

With 24 brands, each running independent waves:

```
Per brand:  3 waves/month × 12 books/wave = 36 books/month
Catalog:    36 × 24 brands = 864 books/month theoretical max
```

This resolves the apparent contradiction between "max 3 waves/month" and a 3,000+ book target. Each brand operates its own wave schedule. Cross-brand waves may overlap on the same calendar day — they are independent publishing operations from the platform's perspective (different pen names, different brand identities).

```yaml
release_waves:
  scope: per_brand                     # NOT global
  max_books_per_wave: 12
  min_days_between_waves: 7
  max_waves_per_month: 3               # per brand
  same_brand_same_wave_max: 3
  same_topic_same_wave_max: 2
  same_teacher_same_wave_max: 2
  same_blueprint_same_wave_max: 1      # force blueprint diversity per wave
  
  # Cross-brand coordination
  max_brands_publishing_same_day: 6    # don't upload from all 24 on one day
  min_brands_between_same_persona: 2   # stagger same-persona books across brands
```

### 30.3 Tiered Rollout Policy

Not all 24 brands launch at full velocity simultaneously. Publishing velocity scales with platform trust.

```yaml
rollout_tiers:
  phase_1_trust_building:
    duration: "months 1-3"
    active_brands: 6                   # start with highest-priority brands
    waves_per_month_per_brand: 2       # conservative
    max_catalog_per_brand: 20
    focus: "establish accounts, build review history, validate no flags"
    
  phase_2_expansion:
    duration: "months 4-6"
    active_brands: 12
    waves_per_month_per_brand: 3
    max_catalog_per_brand: 42
    focus: "scale proven brands, launch second wave of brands"
    
  phase_3_full_scale:
    duration: "months 7+"
    active_brands: 24
    waves_per_month_per_brand: 3
    max_catalog_per_brand: 42+
    focus: "full catalog velocity, adaptive scheduling based on sales data"
```

**Phase 1 brands** should be selected from `revenue_priority: high` brands in the brand registry (stabilizer, panic_first_aid, adhd_anchor, sleep_repair recommended).

### 30.4 Similarity Wave Protection

Within a single wave, no two books may:

- Share the same (persona, topic, teacher) triple
- Have titles with cosine similarity > 0.60
- Be in the same format with the same word count range (± band_width)
- Use the same blueprint variant

---

## 31. Platform Export

### 31.1 Google Play XLS Generator

**Tool:** `tools/omega/google_play_xls_exporter.py`

Generates upload spreadsheets: ISBN/GTIN, title, subtitle, author (brand pen name), description, category codes, pricing, publication date, file references.

### 31.2 Future Platforms

Omega supports additional platforms (Audible, Apple Books, Kobo) via platform-specific exporters reading from `release_waves/`.

---

## 32. Audio System (Omega TTS)

### 32.1 Purpose

Phoenix produces audiobooks, not just text. The audio pipeline transforms assembled book text into TTS audio with persona-appropriate voice, pacing, and locale-aware pronunciation.

### 32.2 Tool

```
python3 -m phoenix_v4.tts.omega_tts plan.yaml -o out/audio/
```

### 32.3 Voice Registry

**Location:**

```
registry/voice_registry.yaml
```

**Schema:**

```yaml
voices:
  gen_z_la_female:
    symbolic_id: "voice_gzla_f_01"
    provider: elevenlabs
    model: eleven_multilingual_v2
    voice_name: "Aria"
    locale: en-US
    persona_targets: [gen_z_la]
    tone: warm, grounded, unhurried
    pace_wpm: 140-160

  gen_z_professionals_male:
    symbolic_id: "voice_gzpro_m_01"
    provider: elevenlabs
    model: eleven_multilingual_v2
    voice_name: "Marcus"
    locale: en-US
    persona_targets: [gen_z_professionals]
    tone: steady, clear, professional
    pace_wpm: 150-170

  healthcare_burnout_female:
    symbolic_id: "voice_hcb_f_01"
    provider: elevenlabs
    model: eleven_multilingual_v2
    voice_name: "Serena"
    locale: en-US
    persona_targets: [healthcare_burnout]
    tone: calm, empathetic, measured
    pace_wpm: 130-150
```

### 32.4 Voice Selection Rules

- Voice is selected by **symbolic ID** from persona mapping — never by raw provider voice ID
- No raw ElevenLabs voice IDs in production plans or compiled output
- Voice assignment is deterministic: `persona → symbolic_id → provider voice`
- Locale-aware selection: if book overlay is Japanese → use Japanese-locale voice
- Teacher doctrine may specify voice preferences (e.g. "contemplative pace" → lower WPM)

### 32.5 Audio Production Pipeline

```
Compiled Plan (§20.4)
  ↓
Hydrated Text (post-variable hydration)
  ↓
SSML Formatter
  → Adds pauses between sections (scene → story transition: 1.5s)
  → Adds breathing pauses after exercises (2.0s)
  → Adds chapter breaks (3.0s silence)
  → Marks emphasis per role (embodiment = slower pace)
  ↓
TTS Engine (ElevenLabs API)
  → Per-chapter audio files
  → Concatenated full audiobook
  ↓
Audio Validation
  → Duration within expected range (±15% of WPM × word count)
  → No silence gaps > 5s (except chapter breaks)
  → No audio artifacts (clipping, truncation)
  ↓
Output: out/audio/<book_id>/
  ├── chapter_01.mp3
  ├── chapter_02.mp3
  ├── ...
  ├── full_audiobook.mp3
  └── audio_manifest.yaml
```

### 32.6 Audio Governance

- Audio is produced **only** from validated, hydrated, simulation-passed book assemblies
- Audio pipeline never modifies text content — it renders what the plan compiler produced
- If TTS fails for any chapter → entire audiobook fails (no partial audio books)
- API key management via `11.txt` key system — no keys in code or plans
- Audio manifest includes: per-chapter duration, total duration, voice used, TTS model version

---

## 33. Cover Generation Pipeline

### 33.1 Purpose

Every published book needs a cover. Covers must be brand-consistent, persona-appropriate, and visually diverse across the catalog to avoid platform detection of formulaic publishing.

### 33.2 Cover Architecture

```
omega/cover_generation/
├── brand_visual_identity/
│   └── <brand_id>/
│       ├── color_palette.yaml
│       ├── font_stack.yaml
│       ├── logo_assets/
│       └── layout_templates/
├── cover_templates/
│   ├── standard_book/
│   │   ├── template_A.svg
│   │   ├── template_B.svg
│   │   └── template_C.svg
│   ├── short_form/
│   └── deep_dive/
├── persona_imagery/
│   └── <persona_id>/
│       ├── mood_keywords.yaml
│       └── style_preferences.yaml
└── generated_covers/
    └── <book_id>/
        ├── cover_front.png
        ├── cover_full_spread.png
        └── cover_manifest.yaml
```

### 33.3 Cover Generation Rules

- Cover template selected based on (brand, format, blueprint variant)
- No two books in the same release wave may use the same cover template
- Brand visual identity (colors, fonts, logo) is enforced per `brand_visual_identity/`
- Title and subtitle rendered from Omega title entropy output
- Author name = brand pen name from brand registry
- Cover imagery style guided by `persona_imagery/mood_keywords.yaml`
- Cover must pass visual diversity check: no two covers in same brand visually identical

### 33.4 Cover Manifest

```yaml
# omega/cover_generation/generated_covers/<book_id>/cover_manifest.yaml
book_id: "bk_gzla_anx_saimaa_001"
brand_id: "mindful_harbor"
template_used: "template_B.svg"
color_palette: "mindful_harbor_primary"
title_rendered: "The Weight Before Words"
subtitle_rendered: "A Somatic Guide to Anxiety"
author_rendered: "Harbor Collective"
format: standard_book
generated_at: <UTC ISO 8601>
```

---

## 34. Companion Page & Metadata Generation

### 34.1 Purpose

Each published book requires companion marketing assets: book descriptions, author bios, landing page content, and platform-specific metadata. These are assembled from pre-approved components, not generated freeform.

### 34.2 Components

```
omega/companion_assets/
├── description_templates/
│   └── <format>/
│       ├── template_A.md
│       ├── template_B.md
│       └── template_C.md
├── author_bios/
│   └── <brand_id>/
│       └── bio.yaml
├── landing_pages/
│   └── <book_id>/
│       ├── landing_page.html
│       └── landing_manifest.yaml
└── metadata/
    └── <book_id>/
        └── platform_metadata.yaml
```

### 34.3 Book Description Generation

Book descriptions are assembled from:

- **Opening hook** — persona-targeted, selected from pre-approved hooks per (persona, topic)
- **Topic framing** — what the book addresses (from topic registry)
- **Teacher authority** — teacher credential summary (from doctrine)
- **Format indicator** — "10 guided chapters" / "5 focused sessions" etc.
- **Call to action** — brand-specific closing line

Descriptions are **assembled, not generated.** No LLM writes descriptions. Components are pre-approved and hydrated with book-specific variables.

### 34.4 Author Bio Per Brand

```yaml
# omega/companion_assets/author_bios/<brand_id>/bio.yaml
brand_id: "mindful_harbor"
pen_name: "Harbor Collective"
bio_short: "Harbor Collective creates evidence-informed guides for navigating life's difficult moments, grounded in somatic and contemplative practice."
bio_long: |
  Harbor Collective is a team of practitioners, writers, and researchers
  dedicated to making therapeutic wisdom accessible. Their work draws on
  somatic psychology, contemplative traditions, and modern neuroscience
  to create practical guides that meet readers where they are.
platform_overrides:
  google_play:
    bio: <bio_short>
  audible:
    bio: <bio_long>
```

### 34.5 Companion Page Rules

- No LLM-generated descriptions — assembly only
- Descriptions must not contain resolution language (same forbidden lexemes as atoms)
- Author bios are fixed per brand — not per book
- Landing pages are optional; generated for premium formats only
- All companion assets are logged in `omega/companion_assets/` and included in platform export

### 34.6 Metadata Safety Gate

**Tool:**

```
tools/omega/metadata_policy_scan.py
```

Platform reviewers and algorithm scanners flag therapeutic, medical, or clinical claims in book metadata. This gate scans all outward-facing text (titles, subtitles, descriptions, category tags) before platform export.

**Blocked terms:**

```yaml
metadata_blocked_terms:
  medical_claims:
    - "cure"
    - "treat"
    - "treatment"
    - "clinically proven"
    - "FDA"
    - "diagnosis"
    - "prescribed"
    - "medication alternative"
    
  therapeutic_overclaims:
    - "heal depression"
    - "cure anxiety"
    - "trauma recovery guaranteed"
    - "guaranteed results"
    - "proven to work"
    - "scientifically proven"
    
  platform_risk:
    - "instant results"
    - "miracle"
    - "secret cure"
    - "doctors don't want you to know"
    - "pharmaceutical industry"
```

**Enforcement:**

- Substring match (case-insensitive) against title, subtitle, description, and category tags
- Any match → hard block — metadata cannot be exported
- Scan runs as part of `google_play_xls_exporter.py` (§31.1) — no export without passing
- Also runs against companion page content (§34.3)
- Brand-level `emotional_vocabulary.banned` list (from brand registry) is checked in addition to global blocked terms
- Violations logged to `artifacts/omega_logs/metadata_safety_flags/`

---

## 35. Spec Freeze & Governance Evolution

### 35.1 Purpose

Phoenix architecture must not drift. The system that ships book #1 must be provably the same system that ships book #3,000. Without governance evolution control, "small tweaks" accumulate into architecture collapse.

**Phoenix is a protocol, not a product.** It is versioned, frozen, and evolved only through formal proposals — the same way networking protocols or compiler specifications are maintained. This framing matters culturally: engineers must treat the spec as law, not guidance.

### 35.2 Canonical Authority

**Required file:**

```
docs/CANONICAL_AUTHORITY.md
```

**Content (verbatim):**

```markdown
# Canonical Authority — Phoenix V4

Phoenix V4 is defined exclusively by:

1. docs/SYSTEMS_DOCUMENTATION.md (this version, frozen)
2. docs/ YAML registries referenced by SYSTEMS_DOCUMENTATION.md
3. phoenix_v4/policy/ format policies and K-tables

No prior chats, drafts, brainstorms, or experiments are authoritative.
No Slack messages, email threads, or meeting notes override this document.

If something is unclear, we amend the docs through the proposal process.
We do not infer from history.
We do not reverse-engineer intent from past commits.
We do not consult old chat transcripts for system behavior.

This is intentional.
```

**Rules:**

- This file must exist in the repo before any development begins
- It is shown to every new engineer on day one
- It prevents "but we used to..." conversations that introduce drift

### 35.3 No Historical Inference Rule

This deserves explicit statement because it is the most commonly violated governance principle:

- Engineers may **not** use old chat logs to determine system behavior
- Engineers may **not** reverse-engineer intent from abandoned code or prior commits
- Engineers may **not** consult brainstorm documents, prior spec versions, or transitional drafts
- If the current frozen spec does not define a behavior → the behavior does not exist
- If an engineer believes something is missing → they file a proposal (§35.5), not an inference

**The moment an engineer asks "which version do we follow?" — authority has been lost.** There is only one version: the frozen spec.

### 35.4 Freeze Rule

Once Phoenix passes all acceptance criteria (§39):

1. **Tag the repo:** `v4.3.0`
2. **Freeze this document:** `SYSTEMS_DOCUMENTATION.md` becomes immutable at this version
3. **All future changes** must go through the proposal process (§35.5)
4. **No silent evolution** — no "quick fix" commits that alter system behavior

### 35.5 Proposal Process

```
docs/PROPOSALS/
├── V4_3_1_add_new_exercise_type.md
├── V4_3_2_expand_safety_lexicon.md
├── V4_4_0_add_multi_teacher_chapters.md
└── PROPOSAL_TEMPLATE.md
```

**Proposal schema:**

```yaml
proposal_id: "V4_3_1"
title: "Add 'journaling' exercise type"
author: <human>
status: draft | review | approved | rejected
impact:
  layers_affected: [Layer 1]
  sections_modified: [§8.2, §8.4, §19.3]
  ci_gates_affected: [9]
  breaks_backward_compatibility: false
rationale: |
  Journaling exercises are requested by 3 teachers.
  They require no body lexeme but need doctrine compliance.
approval:
  approved_by: <system architect>
  approved_at: <UTC ISO 8601>
```

**Rules:**

- No proposal may weaken non-negotiables (§3)
- No proposal may relax strict mode for production contexts
- No proposal may remove CI gates — only add new ones
- Proposals that affect Layer 0 (doctrine) require teacher sign-off
- Proposals that affect safety (§23) require clinical advisor review
- Approved proposals are implemented, then this document is updated and re-frozen at new version

### 35.6 Domain Ownership

Phoenix is built by specialists, not generalists. Each layer has a designated owner to prevent cross-layer violations:

| Domain | Scope | Owner |
|--------|-------|-------|
| **Seed Mining + Lint** | §6–§13: mining pipelines, lint rules, repair loop, cadence | Dev A |
| **Approval + Governance** | §14–§17: atom lifecycle, auto-promotion, writer trust, sensitive families | Dev B |
| **Plan Compiler + Runtime** | §19–§22: format policies, K-tables, plan compilation, duplication simulation, strict mode | Dev C |
| **CI + Safety** | §23–§25: safety scanner, escalation, CI gates, determinism | Dev D |
| **Omega Orchestrator** | §26–§31: brands, SKUs, release waves, platform export | Dev E |
| **Audio + Assets** | §32–§34: TTS, covers, companion pages, metadata | Dev F |
| **Doctrine** | §5: teacher doctrine synthesis, approval, coverage | Content Lead |

**Rules:**

- No one owns "the whole system" except the system architect (you)
- Domain owners may not modify code outside their domain without a cross-domain review
- Cross-layer imports are detected by CI (§25) — but ownership prevents the attempt in the first place
- If a feature requires changes in multiple domains → it requires a proposal (§35.5)

### 35.7 Version History

| Version | Date | Changes |
|---------|------|---------|
| 4.0 | 2026-01-07 | Initial canonical spec |
| 4.1 | 2026-02-12 | Hardened enforcement specs (10 structural gaps patched) |
| 4.2 | 2026-02-12 | 3-layer architecture, exercises, scenes, doctrine, Omega |
| 4.3 | 2026-02-12 | Plan compiler, K-tables, strict mode, duplication simulation, audio, covers, governance, semantic quality gates, entropy tracking, global fingerprint registry, catalog planning hierarchy, naming engine |

---

## 36. Definition of Done — V4

Phoenix V4 is "done" only when **all** of the following are provably true:

### Structural Invariants

1. One human seed → 5–7 atoms, deterministically (same input = same output, every time)
2. All atoms fail lint if reassurance language is added
3. Runtime cannot import `human_seeds/` — CI verified by grep/AST scan
4. Every approved atom has complete `approval` metadata with human identity
5. Grief/trauma families cannot auto-promote — CI hard-blocks `auto_confident`
6. Runtime assembles unresolved content only — no resolution, no reassurance, no outcome
7. Runtime output is byte-derived from approved atoms + hydration only — hash verified

### Capability Invariants

8. Capability gate blocks compilation when any slot type falls below K-table minimum
9. No book is compiled with atom_reuse_count > 0
10. No book passes duplication simulation with paragraph hash collisions > 0
11. No book is published with unresolved `{{...}}` markers
12. Strict mode is active for all production assemblies — no exceptions

### Scale Invariants

13. 1,000 books can be compiled without a single duplication failure (10K simulation validates)
14. 24 brands can publish simultaneously without cross-brand content overlap
15. Every release wave passes similarity wave protection
16. Blueprint rotation produces ≥ 3 structurally distinct variants per format

### Governance Invariants

17. `docs/CANONICAL_AUTHORITY.md` exists and is shown to all engineers
18. `SYSTEMS_DOCUMENTATION.md` is frozen at tagged version
19. All changes go through `docs/PROPOSALS/` — no silent evolution
20. Domain ownership is assigned and enforced

**If an engineer says "it mostly works" — it is not done.**
**If any of the 20 invariants above is false — it is not done.**

---

## 37. Definition of "As Good or Better"

Quality is preserved by:

- emotional ordering
- role integrity
- exercise safety
- scene framing
- ethical constraints
- cultural truth via overlays
- teacher doctrine fidelity
- K-table enforcement (no thin books)
- duplication simulation (no repetitive books)
- blueprint rotation (no formulaic books)

Quality is **not** measured by prose similarity.  
Low lexical similarity is intentional.

---

## 38. Final Principle

> **Humans define meaning.** (Layer 0)  
> **Machines enforce structure.** (Layer 1)  
> **The system fails instead of degrades.** (Layer 1)  
> **Runtime assembles, never decides.** (Layer 1)  
> **Orchestration composes plans, never content.** (Layer 2)

If any layer violates its boundary, Phoenix is no longer Phoenix.

---

## 39. Rebuild Acceptance Checklist

A Phoenix rebuild is complete **only** when every item below passes:

### Layer 0 — Teacher Doctrine

- [ ] `teacher_doctrine/` exists with per-teacher subdirectories
- [ ] Doctrine schema matches §5.3
- [ ] Doctrine approval gate enforced (§5.4)
- [ ] No mining for teachers without locked+approved doctrine
- [ ] `doctrine_compliance_check.py` validates atoms against `forbidden_framings`
- [ ] `check_doctrine_coverage.py` reports coverage per teacher × topic × category
- [ ] Golden Phoenix Coverage Agent exists and writes only provisional atoms (§5.7)
- [ ] Coverage agent respects doctrine constraints and safety rules

### Layer 1 — Repository & Structure

- [ ] Repo topology matches §4
- [ ] `candidate_atoms/` has `story/`, `exercise/`, `scene/` subdirs — not runtime-visible
- [ ] `approved_atoms/` has `story/`, `exercise/`, `scene/` subdirs — sole runtime input
- [ ] `registry/exercise_registry.yaml` matches §8.2
- [ ] `registry/scene_registry.yaml` matches §9.2

### Layer 1 — Mining Pipeline

- [ ] All tools listed in §11 exist and are executable
- [ ] Three separate pipelines functional: story, exercise, scene
- [ ] Pipeline is deterministic (§24 reproducibility test passes)
- [ ] Word count enforcement per category
- [ ] Forbidden resolution lexemes enforced (§10.2)
- [ ] Body lexeme for embodiment (§7.1), sensory lexeme for entry scenes (§9.4)
- [ ] Exercise-specific lint (§8.4) and scene-specific lint (§9.4)
- [ ] Doctrine compliance check for all atoms
- [ ] Safety scanner with exercise safety lexicon (§23)
- [ ] Similarity gate at 0.82 cosine (§16.1)
- [ ] Role ordering enforcement (§7.2)
- [ ] Arc registry exists at `data/story_arc_registry.yaml` with all 8 arc types (§7.0)
- [ ] All story atoms carry valid `arc_type` and `stake_domain` metadata (§7.0)
- [ ] Plan compiler enforces: no adjacent same arc_type, max 2 per book, min 3 distinct (§7.0)
- [ ] Plan compiler enforces: min 2 distinct stake_domains per book (§7.0)
- [ ] Arc entropy tracked per persona × topic alongside slot entropy (§22.9)
- [ ] Arc type concentration > 35% generates mining diversity alert
- [ ] Repair loop bounded to max 2 attempts

### Layer 1 — Approval & Governance

- [ ] `approve_atoms.py` works for all categories with dry-run
- [ ] All approved atoms have `approval` metadata, `version`, `deprecated` fields
- [ ] Writer trust tracked per writer per role/type (§16.2)
- [ ] No-auto-promotion families enforced across all categories (§17)

### Layer 1 — Format Policy & Plan Compiler

- [ ] Format policies exist for all supported formats (§19.2)
- [ ] K-tables exist for all formats (§19.3)
- [ ] K-table enforcement blocks compilation when pool below k_min
- [ ] Plan compiler produces deterministic output (§20.3)
- [ ] Compiled plans include all validation fields (§20.4)
- [ ] Atom selection uses quality-ranked scoring (§20.3)
- [ ] Selection traces generated per book in `artifacts/plan_compiler/selection_traces/`
- [ ] No-two-same-point constraint enforced within each book (§20.3)
- [ ] Injection scoring weights defined in policy YAML
- [ ] Capability gate runs before compilation (§21.3)
- [ ] Strict mode is default for production (§21.2)
- [ ] No-fallback rule enforced (§21.4)
- [ ] Compilation failures logged with actionable detail (§20.5)
- [ ] Build manifest generated for every published book (§20.6)
- [ ] `make reproduce BOOK_ID=<id>` command functional and hash-verified
- [ ] Quarantine registry exists and is append-only (§20.7)
- [ ] No quarantined book auto-retries — human review required
- [ ] Quarantine weekly report generated

### Layer 1 — Duplication Simulation

- [ ] Duplication simulator runs on every compiled plan (§22)
- [ ] Paragraph hash: zero collisions (§22.4)
- [ ] Sentence hash: within threshold
- [ ] 6-gram overlap: within threshold
- [ ] Structural fingerprint uniqueness checked
- [ ] Recognition-first monotony detected
- [ ] Opening paragraph hash: zero collisions across catalog (§22.6)
- [ ] Closing paragraph hash: zero collisions across catalog (§22.6)
- [ ] Marker leakage detection: zero unresolved `{{...}}` in hydrated output (§22.6)
- [ ] Tone drift scanning active with chapter centroid checks (§22.6)
- [ ] Simulation results logged (§22.7)
- [ ] Failed books blocked in strict mode

### Layer 1 — Semantic Quality & Entropy (V4.4)

- [ ] Similarity threshold set to 0.82 (§16.1)
- [ ] Embedding cache exists at `artifacts/semantic_index/`
- [ ] Filler density detection active with policy YAML (§16.3.1)
- [ ] Narrative delta scoring runs on pools with 20+ atoms (§16.3.2)
- [ ] Narrative delta reports generated per scope
- [ ] Slot entropy tracker operational (§22.9)
- [ ] Entropy floors defined per slot type
- [ ] Heavy hitter atoms (>10% usage) flagged for review
- [ ] Global fingerprint registry exists and is append-only (§22.10)
- [ ] Fingerprint collision → hard fail at compilation
- [ ] Atom health audit runs every 500 books (§17.1)
- [ ] Overuse, similarity clusters, and stale atoms detected and logged

### Layer 1 — CI & Safety

- [ ] CI runs all 39 gates listed in §25
- [ ] Safety scanner runs on all atoms and repair outputs
- [ ] Safety flags require human review
- [ ] No safety flag auto-dismissed

### Layer 1 — Coverage & QA Operations

- [ ] Golden Phoenix Coverage Agent functional (§5.7)
- [ ] Coverage agent writes only provisional atoms with `source: golden_phoenix`
- [ ] Coverage agent passes full lint + doctrine + safety pipeline
- [ ] Coverage agent blocked from no-auto-promotion families (§17)
- [ ] Persona fallback disabled in strict mode, configurable in QA (§21.5)
- [ ] Fallback log exists and is reviewed before production
- [ ] `make v4_qa_1000` runs full 1000-book campaign (§25.1)
- [ ] QA campaign achieves ≥ 95% pass rate before production release
- [ ] QA summary reports provisional usage, fallback usage, and coverage gaps
- [ ] `make v4_story_coverage` verifies all persona × topic combos (§25.2)
- [ ] Coverage verification gate runs before every release wave
- [ ] NOT_READY combos excluded from release waves

### Layer 1 — Exercise Cadence

- [ ] Exercise atoms declare `cadence_role` (grounding, activation, release, integration) — §8.6
- [ ] Plan compiler validates cadence_role against `chapter_position_ok`
- [ ] No two adjacent chapters use same cadence_role
- [ ] Book-level arc progression validated (grounding → activation → release → integration trend)

### Layer 2 — Omega Orchestrator

- [ ] `omega/` directory exists with all subdirectories
- [ ] Brand registry schema matches §27.1
- [ ] Blueprint rotation active with ≥ 3 variants per format (§28)
- [ ] Blueprint assignment deterministic and logged

### Layer 2 — Catalog Planning & Naming

- [ ] Domain decomposition templates exist per domain (§29.0)
- [ ] Series generated from domain templates with search keywords and persona affinity
- [ ] Angle generator produces 3–12 candidates per series (§29.0)
- [ ] Capacity-aware series sizing implemented (§29.0.1)
- [ ] Capacity hard guards enforced (safety margin 1.2×, heavy_hitter_rate < 0.25, semantic_delta > 0.55)
- [ ] Angle legitimacy filter: recognition gate, mechanism density, differentiation (§29.0.2)
- [ ] Rejected angles and series logged with reasons
- [ ] Quarterly catalog plan generated with approved/rejected series and angles
- [ ] SKU planner generates unique SKUs (§29.1)
- [ ] Naming engine scores titles: SEO + Human Appeal - Dup Risk - Penalties (§29.2.3)
- [ ] Human Appeal score uses point-based lookup from recognition lexeme registry (§29.2.3)
- [ ] Recognition lexeme registry exists with scenario_words, distress_verbs, outcome_phrases, persona_lexemes (§29.2.4)
- [ ] Mechanism blacklist enforced — clinical terms rejected from titles/subtitles (§29.2.2)
- [ ] Intent taxonomy classifies every title (§29.2.1)
- [ ] Hard validators: blacklist, length, keyword presence, similarity, skeleton cap (§29.2.3)
- [ ] Naming traces generated per book showing candidates, scores, rejections (§29.2.5)
- [ ] Title entropy rules enforced: cosine thresholds, pattern caps, subtitle uniqueness (§29.2.6)
- [ ] Title deduplication is offline (TF-IDF, no embeddings required)
- [ ] Persona-seed diversification across 5 levers (§29.3)
- [ ] Word-length variance distribution enforced (§29.4)
- [ ] Release wave generator respects all rules (§30.2)
- [ ] Wave scope is per-brand, not global (§30.2)
- [ ] Tiered rollout policy defined (§30.3) — Phase 1 brands identified
- [ ] Max 6 brands publishing same calendar day enforced
- [ ] Similarity wave protection active (§30.4)
- [ ] Google Play XLS exporter functional (§31.1)
- [ ] Omega CI gates pass (§25 items 22–30)
- [ ] Omega never modifies book assembly content (hash verification)

### Audio System

- [ ] Voice registry exists with symbolic IDs per persona (§32.3)
- [ ] No raw provider voice IDs in production plans or output
- [ ] SSML formatter adds appropriate pauses per section type (§32.5)
- [ ] Audio produced only from validated, simulation-passed assemblies
- [ ] Audio validation: duration within ±15% of expected, no artifacts
- [ ] Partial audiobook failure → entire audiobook blocked
- [ ] API key management via `11.txt` system — no keys in code
- [ ] Audio manifest generated per book (§32.5)

### Cover & Companion Assets

- [ ] Brand visual identity defined per brand (§33.2)
- [ ] Cover templates exist for all formats with ≥ 3 variants (§33.2)
- [ ] No two books in same wave use same cover template (§33.3)
- [ ] Cover manifest generated per book (§33.4)
- [ ] Book descriptions assembled from pre-approved components — no LLM generation (§34.3)
- [ ] Author bios fixed per brand (§34.4)
- [ ] Companion assets do not contain forbidden resolution language
- [ ] Metadata safety gate blocks medical claims, therapeutic overclaims, and platform-risk terms (§34.6)
- [ ] Brand-level `emotional_vocabulary.banned` enforced in metadata
- [ ] Platform-specific metadata generated per book (§34.2)

### Governance

- [ ] `docs/CANONICAL_AUTHORITY.md` exists with verbatim content from §35.2
- [ ] Canonical authority file shown to all engineers before development begins
- [ ] No historical inference rule communicated to team (§35.3)
- [ ] Repo tagged at current version (§35.4)
- [ ] `SYSTEMS_DOCUMENTATION.md` frozen at tagged version
- [ ] `docs/PROPOSALS/` directory exists with `PROPOSAL_TEMPLATE.md`
- [ ] No changes to system behavior without approved proposal (§35.5)
- [ ] Proposals that affect safety require clinical advisor review
- [ ] Domain ownership assigned per §35.6
- [ ] All 20 "Definition of Done" invariants verified (§36)
- [ ] System treated as protocol, not product — engineers confirm understanding

### Documentation

- [ ] `docs/CANONICAL_AUTHORITY.md` exists and matches §35.2
- [ ] `docs/BODY_LEXEMES.yaml` matches §7.1
- [ ] `docs/SENSORY_LEXEMES.yaml` matches §9.4
- [ ] `docs/FORBIDDEN_RESOLUTION_LEXEMES.yaml` matches §10.2
- [ ] `docs/NO_AUTO_PROMOTION_FAMILIES.yaml` matches §17
- [ ] `docs/CADENCE_THRESHOLDS_BY_FAMILY.yaml` exists
- [ ] `docs/RUNTIME_ASSEMBLY_SCHEMA.yaml` matches §19.2
- [ ] `docs/ESCALATION_PROTOCOL.md` references §23
- [ ] `phoenix_v4/policy/format_policies/` contains all format YAMLs
- [ ] `phoenix_v4/policy/k_tables/` contains all K-table YAMLs
- [ ] `phoenix_v4/policy/strict_mode.yaml` exists and matches §21.2
- [ ] `phoenix_v4/policy/duplication_thresholds.yaml` exists and matches §22.4
- [ ] `phoenix_v4/policy/filler_patterns.yaml` exists and matches §16.3.1
- [ ] `phoenix_v4/policy/narrative_delta.yaml` exists and matches §16.3.2
- [ ] `phoenix_v4/policy/persona_fallback.yaml` exists and matches §21.5
- [ ] `phoenix_v4/policy/injection_scoring.yaml` exists and matches §20.3
- [ ] `phoenix_v4/policy/catalog_planning.yaml` exists and matches §29.0.1
- [ ] `phoenix_v4/policy/naming_scoring.yaml` exists and matches §29.2.3
- [ ] `phoenix_v4/policy/recognition_lexemes.yaml` exists and matches §29.2.4
- [ ] `omega/title_entropy/mechanism_blacklist.yaml` exists and matches §29.2.2
- [ ] `omega/title_entropy/intent_taxonomy.yaml` exists and matches §29.2.1
- [ ] `omega/blueprint_rotation/` contains ≥ 3 variants per format
- [ ] `registry/voice_registry.yaml` exists and matches §32.3
- [ ] `omega/cover_generation/brand_visual_identity/` exists per brand
- [ ] `omega/companion_assets/` exists with description templates and author bios
- [ ] This document (`SYSTEMS_DOCUMENTATION.md`) is present and frozen at v4.3

---

**END OF SYSTEMS_DOCUMENTATION.md**
