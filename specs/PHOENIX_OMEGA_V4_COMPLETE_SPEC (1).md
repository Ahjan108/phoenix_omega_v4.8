# PHOENIX OMEGA V4 — COMPLETE SYSTEM SPECIFICATION

**Status:** Canonical (supersedes all prior docs)
**Audience:** Senior engineers, infra, QA, content governance, leadership
**Last Updated:** 2026-02-11 (v4.1 — cross-layer coupling tightened, scene integration SOP added)
**Scope:** Full end-to-end system definition — philosophy, architecture, tooling, runtime, scaling, governance, cross-layer narrative coupling, content team workflow

> **One-line mission:** Phoenix Omega V4 scales human-written therapeutic journeys without letting machines invent, dilute, or resolve meaning.

---

## 0. What This Document Is

This document is the **single source of truth** for building or rebuilding the Phoenix Omega V4 system.

If the repo were deleted, a competent senior engineering team could recreate:

- directory structure and data flow
- content pipelines (mining, approval, coverage)
- runtime assembly and validation
- CI invariants and governance
- scaling and publishing infrastructure
- narrative intelligence enforcement

**No other document is required.** All prior chat history, partial specs, and brainstorm docs are superseded by this document.

### Canonical Authority Rule

> Phoenix Omega V4 is defined exclusively by this document.
> If something is unclear, we amend this document.
> We do not infer from history.

---

## 1. System Mission

Phoenix Omega V4 exists to scale therapeutic, culturally grounded audio content without:

- flattening meaning
- reusing prose
- introducing false reassurance
- automating ethical judgment
- collapsing narrative into bullet points

It is **not** a text generator. It is a **meaning-preserving assembly engine** with **narrative intelligence enforcement**.

---

## 2. Foundational Philosophy

Phoenix V4 enforces hard separation of responsibilities:

| Layer | Responsibility | May Decide Meaning? |
|---|---|---|
| Human Authors | Truth, ethics, cultural reality | ✅ Yes |
| Mining + Lint | Structure, safety, cadence | ❌ No |
| Planning | Arc selection, mechanism, slots | ❌ No |
| Runtime Assembly | Composition only | ❌ No |
| Validation | Quality + safety gates | ❌ No |

**If a machine decides meaning, the system is broken.**

### The Three Worlds (Never Mixed)

```
1. HUMAN WORLD    — Offline, read-only authoring
2. SYSTEM WORLD   — Approved assets (SOURCE_OF_TRUTH)
3. RUNTIME WORLD  — Assembly only, no prose generation
```

If something crosses worlds incorrectly → **hard failure**.

---

## 3. Absolute Non-Negotiables

These rules are enforced by CI and must never be weakened:

1. Human long-form prose is never ingested directly
2. Runtime reads only approved micro-atoms and approved scenes
3. All sensitive content requires human witnessing
4. Automation may assist, never override
5. Cultural specificity lives outside prose atoms (in Story Bank overlays)
6. No reassurance, no resolution, no "healing language"
7. Runtime never generates, rewrites, or "improves" prose
8. If something is missing, the system fails — no fallback content
9. Authority is declared, never generated — no fake experts
10. Exercises regulate experience, not outcomes — no fixing the reader

**Violations are system failures, not bugs.**

---

## 4. Repository Topology (Rebuild Canon)

```
phoenix_v4/
├── README.md
├── Makefile
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── SYSTEMS_DOCUMENTATION.md          # This document
│   ├── ARCHITECTURE_OVERVIEW.md
│   ├── NON_NEGOTIABLES.md
│   ├── CANONICAL_AUTHORITY.md
│   ├── WHY_PHOENIX_V4_EXISTS.md
│   ├── AUTHORING_GUIDE.md
│   ├── SEED_MINING_SPEC.md
│   ├── EXERCISE_SYSTEM_SPEC.md
│   ├── SCENE_INJECTION_ARCHITECTURE.md
│   ├── PLANNING_AND_ASSEMBLY.md
│   ├── VALIDATION_GATES.md
│   ├── PROSE_QA_GATE_STACK.md
│   ├── GOLDEN_PHOENIX_COVERAGE_SPEC.md
│   ├── MULTI_BRAND_OPERATIONS.md
│   ├── CADENCE_THRESHOLDS_BY_FAMILY.yaml
│   ├── NO_AUTO_PROMOTION_FAMILIES.yaml
│   ├── DOCTRINE_TO_V4_ROLE_MAP.yaml
│   └── GLOSSARY.md
│
├── SOURCE_OF_TRUTH/
│   ├── README.md
│   │
│   ├── human_seeds/                       # READ-ONLY human truth
│   │   ├── README.md
│   │   └── <pack_name>/                   # e.g. la_gen_alpha/
│   │       ├── doctrine/
│   │       ├── seeds/                     # pf_*.json
│   │       ├── CONTENT_TEAM_SPEC.md
│   │       └── EXEMPLARS.md
│   │
│   ├── data/
│   │   └── story_bank/
│   │       ├── story_atoms/               # THE ATOM LIBRARY
│   │       │   └── <persona>/
│   │       │       └── <topic>/
│   │       │           └── <engine>/      # e.g. avoidance_trap, legacy
│   │       │               └── <role>/    # recognition, embodiment, pattern, mechanism_proof, agency_glimmer
│   │       │                   └── micro/
│   │       │                       ├── v01.txt
│   │       │                       ├── v01_meta.yaml
│   │       │                       ├── v02.txt
│   │       │                       ├── v02_meta.yaml
│   │       │                       └── metadata.yaml   # folder-level defaults
│   │       ├── location_variables/
│   │       │   └── <locale_id>.yaml       # one file per location (nyc.yaml, la.yaml, etc.)
│   │       ├── social_patterns/
│   │       │   └── <persona_id>.yaml      # social pressures, status games, identity friction
│   │       ├── pressure_themes/
│   │       │   └── <persona_id>.yaml      # financial, career, relationship, health, existential pressures
│   │       └── cultural_overlays/
│   │           └── <persona_id>_<locale_id>.yaml  # persona×location intersection files
│   │
│   ├── approved_scenes/
│   │   ├── README.md
│   │   └── <persona>/<topic>/<stakes>/*.yaml
│   │
│   ├── exercises_v4/
│   │   ├── registry.yaml                  # global metadata, tag vocab, selection weights
│   │   ├── packs/                         # imported legacy/content-team collections (read-only-ish)
│   │   │   └── <pack_id>/
│   │   │       ├── _pack.yaml
│   │   │       └── exercises/<exercise_id>.yaml
│   │   ├── approved/                      # ONLY runtime source
│   │   │   └── <persona>/<topic>/<exercise_id>.yaml
│   │   ├── candidate/                     # awaiting approval
│   │   │   └── <persona>/<topic>/<exercise_id>.yaml
│   │   └── _rejects/
│   │       └── <exercise_id>.log
│   │
│   ├── human_reject_notes/                # human rejection reasoning
│   │   └── <atom_id>.md
│   │
│   └── registry/
│       ├── personas.yaml                  # base persona definitions (see §13.1)
│       ├── topics.yaml                    # canonical topic registry (see §13.2)
│       ├── locations.yaml                 # location registry index (see §13.3)
│       ├── stakes.yaml
│       ├── styles.yaml
│       ├── exercise_registry.yaml
│       ├── authority_rules.yaml
│       └── doctrine_refs.yaml
│
├── config/
│   └── publishing/
│       ├── brand_archetype_registry_v1_2.yaml
│       └── launch_waves_v1_2.yaml
│
├── phoenix_v4/
│   ├── README.md
│   ├── assembler/
│   │   ├── assemble_v4.py                 # main assembly engine
│   │   ├── section_assembler.py
│   │   ├── variant_selector.py
│   │   └── story_injector.py
│   ├── planning/
│   │   ├── compile_format_plan.py         # plan compiler
│   │   ├── topic_engine_bindings.yaml     # topic → allowed engines
│   │   ├── coverage_checker.py            # plan-time coverage validation
│   │   └── arc_planner.py
│   ├── policy/
│   │   ├── format_story_quality.yaml      # min atoms per role per format
│   │   └── format_rules.yaml
│   ├── libraries/
│   │   ├── micro_story_loader.py          # loads atoms, includes PERSONA_FALLBACK
│   │   ├── exercise_resolver.py
│   │   ├── scene_selector.py
│   │   └── location_hydrator_v4.py        # variable hydration module
│   ├── validators/
│   │   ├── validate_omega_v4.py           # full validation suite
│   │   ├── narrative_gate.py
│   │   ├── exercise_gate.py
│   │   ├── persona_gate.py
│   │   ├── safety_gate.py
│   │   ├── role_purity_gate.py            # lexeme detection: body words in recognition, cognitive framing in embodiment
│   │   ├── person_compliance_gate.py      # first-person detection in atoms
│   │   ├── mechanism_escalation_gate.py   # Omega: depth 1→4
│   │   ├── cost_gradient_gate.py          # Omega: cost intensity + identity coupling
│   │   ├── callback_integrity_gate.py     # Omega: setup→return
│   │   ├── identity_shift_gate.py         # Omega: identity progression
│   │   ├── macro_cadence_gate.py          # Omega: emotional wave
│   │   └── cross_layer_coupling_gate.py   # Cross-layer: cost↔identity, scene↔cadence, exercise↔identity, engine diversity
│   ├── registries/
│   │   ├── personas/
│   │   └── topics/
│   ├── ci/
│   │   ├── check_topic_readiness.py
│   │   ├── story_atoms_coverage_report.py
│   │   ├── check_no_human_seeds_reference.py
│   │   ├── check_approved_atoms_status.py
│   │   ├── check_approved_exercises_status.py
│   │   └── check_semantic_uniqueness.py     # anti-template similarity guard
│   └── tools/
│       ├── run_v4_prose_qa_campaign.py
│       ├── build_v4_prose_qa_summary.py
│       ├── generate_canonical_1008_plans.py
│       └── run_canonical_plan.py
│
├── tools/
│   ├── seed_mining/
│   │   ├── README.md
│   │   ├── mine_seed.py
│   │   ├── semantic_segmenter.py
│   │   ├── role_extractor.py
│   │   ├── rewrite_as_atom.py
│   │   ├── lint_atom.py
│   │   ├── cadence_checks.py
│   │   ├── repair_loop.py
│   │   └── execute_system_atom_packs.py   # template + LLM writer
│   ├── golden_phoenix/
│   │   ├── golden_phoenix_runner.py       # per-teacher compilation
│   │   ├── run_golden_phoenix.py          # batch + v4_full_coverage
│   │   ├── run_golden_phoenix_v4_coverage.py  # fill atom gaps
│   │   └── repair_legacy_story_atoms.py   # structural bar enforcement
│   ├── approval/
│   │   ├── approve_atoms.py
│   │   └── exercise_approve.py
│   ├── exercise_import/
│   │   └── import_legacy_exercises.py
│   ├── scene_integration/
│   │   ├── wrap_scene_yaml.py             # applies YAML wrapper to raw prose
│   │   ├── validate_scene_metadata.py     # checks all required fields
│   │   ├── mine_atoms_from_scene.py       # extracts atom candidates from scenes
│   │   └── scene_callback_audit.py        # validates callback setup/return pairs
│   ├── persona_research/
│   │   ├── persona_research_harvester.py  # validates + formats persona YAML into Phoenix registries
│   │   ├── research_inputs/               # raw research YAML per persona (researcher output)
│   │   │   └── personas/<persona_id>.yaml
│   │   └── generate_mining_priority.py    # ranks persona×topic combos by affinity for mining order
│   └── ci/
│       ├── no_human_source_runtime.py
│       └── enforce_approval_only.py
│
├── prompts/
│   └── v4/
│       └── system_atoms/                  # intermediate pack format
│
├── artifacts/
│   ├── seed_mining/
│   ├── approval_logs/
│   ├── template_eval/
│   ├── story_atoms_coverage.json
│   ├── mining_priority_matrix.yaml        # ranked persona×topic combos for mining order
│   ├── capability_gaps.json               # what's missing vs. what's been mined
│   ├── v4_prose_qa_results.jsonl
│   ├── v4_prose_qa_summary.json
│   ├── v4_prose_qa_report.md
│   ├── golden_phoenix_summary.json
│   └── v4_full_coverage_summary.json
│
├── tests/
│   ├── test_seed_mining.py
│   ├── test_exercises.py
│   ├── test_exercise_lint.py
│   ├── test_exercise_resolver.py
│   ├── test_planner.py
│   ├── test_coverage.py
│   └── test_end_to_end.py
│
└── .github/
    └── workflows/
        └── ci.yml
```

### Runtime Access Rules

- Runtime may **only** read from:
  - `SOURCE_OF_TRUTH/data/story_bank/story_atoms/` (approved atoms)
  - `SOURCE_OF_TRUTH/approved_scenes/`
  - `SOURCE_OF_TRUTH/exercises_v4/approved/`
  - `SOURCE_OF_TRUTH/registry/`
  - `SOURCE_OF_TRUTH/data/story_bank/location_variables/` (for hydration)
  - `phoenix_v4/planning/topic_engine_bindings.yaml`
  - `phoenix_v4/policy/`
  - `config/publishing/`

- Runtime may **never** read:
  - `SOURCE_OF_TRUTH/human_seeds/`
  - `SOURCE_OF_TRUTH/exercises_v4/candidate/`
  - `SOURCE_OF_TRUTH/exercises_v4/packs/`
  - Any file in `tools/`

---

## 5. Story Roles (Canonical — 5 Roles)

V4 uses **five** ordered story roles. Each atom is role-pure.

| Role | Purpose | Must Include | Must NOT Include | Word Range |
|---|---|---|---|---|
| **recognition** | Incident + validation, no body language | validation phrase, tension signal | body sensation, reassurance, solution | 60–90 |
| **embodiment** | Body sensation only | body lexeme (chest, jaw, hands, stomach, throat) | explanation, solution, cognitive framing | 60–80 |
| **pattern** | Repetition without relief or hope | repetition marker, temporal signal ("again," "every time") | hope, relief, progress, resolution | 60–90 |
| **mechanism_proof** | Explanation without solution | causal explanation of why the loop works | advice, fixing, cure, prescription | 60–120 |
| **agency_glimmer** | Choice without reassurance | choice verb, open ending | reassurance, outcome, triumph, celebration | 60–90 |

### Role Ordering

Within a chapter, roles are ordered: **recognition → embodiment → pattern → mechanism_proof → agency_glimmer**

Cadence is enforced across transitions:
- recognition → embodiment: must enter the body immediately — no cognitive bridge
- embodiment → pattern: must shift from single sensation to recurring loop
- pattern → mechanism_proof: must shift from naming the loop to explaining why it works
- mechanism_proof → agency_glimmer: must shift from explanation to open choice
- Final role must end in open choice, not comfort

Not all 5 roles are required in every chapter. But ordering must never regress within a chapter. A chapter may use roles [recognition, pattern, agency_glimmer] but never [pattern, recognition, agency_glimmer].

### Word Count Rationale (10K-Scale)

Word ranges are calibrated for cohesive flow across 10,000+ books covering deep persona × topic × location combinations:

- **Shorter atoms (60–90)** combine cleanly — atom A next to atom B feels like natural progression. Longer atoms compete for the reader's emotional attention. At scale, that collision multiplies.
- **Scenes carry narrative weight (300–600 words).** Atoms sit between them as sharp insight moments — a breath, a crack, a recognition. At 60–90 words, an atom is ~35 seconds of audio. At 150 words, it's ~60 seconds — long enough that listeners expect narrative movement, which belongs to scenes.
- **mechanism_proof gets extra room (60–120)** because explaining *why a loop works* without giving advice requires slightly more space than naming a pattern or offering a choice.
- **More atoms = more variety at scale.** Shorter atoms force greater variant counts per role, reducing repetition across books. At 10K scale, repetition is the real enemy.

### Atom Metadata Schema

Each atom variant has a corresponding `*_meta.yaml`:

```yaml
status: confirmed | provisional
point: "The pattern was clear once they saw it."
reversal_line: "They realized the feeling was not a verdict."  # required for agency_glimmer
stakes: "social exposure"
```

And a folder-level `metadata.yaml` for defaults.

---

## 6. Topic Engine Bindings

**Purpose:** Maps each topic to its allowed psychological engines. Engines determine *which mechanism* drives the narrative for a given topic.

**Location:** `phoenix_v4/planning/topic_engine_bindings.yaml`

```yaml
anxiety:
  allowed_engines:
    - avoidance_trap
    - false_alarm
    - legacy

burnout:
  allowed_engines:
    - legacy
    - depletion_cycle

grief:
  allowed_engines:
    - legacy
    - attachment_rupture

stress:
  allowed_engines:
    - legacy
    - overload_cascade

transformation:
  allowed_engines:
    - legacy
    - identity_evolution
```

### Rules

- At least one engine per topic must have content under `story_atoms/{persona}/{topic}/{engine}/{role}/micro/`
- Assembly selects atoms from engines listed for the book's topic
- New engines require adding to this file before atoms can reference them
- This file is a **planner input**, not runtime-generated

### Engine Diversity Enforcement

At scale (1,008+ plans), using a single engine for all 10 chapters flattens narrative depth. The planner must enforce:

```
For a 10-chapter arc:
  min_distinct_engines: 2
```

**Rules:**
- At least 2 distinct engines must appear across the chapters of a single book
- The planner should prefer engine shifts at narrative phase boundaries (early → mid, mid → late)
- If a topic has only 1 allowed engine with sufficient coverage, the diversity requirement is waived (but flagged in the coverage report as `engine_diversity: limited`)
- Engine shifts must not create mechanism incoherence — the planner selects compatible engine transitions (e.g., `avoidance_trap` → `false_alarm` is coherent for anxiety; `avoidance_trap` → `depletion_cycle` is not)

**CI validation:** `coverage_checker.py` must report `engine_diversity` status per persona × topic.

---

## 7. Human Seeds (Truth Layer)

### Purpose

Human seed packs encode: lived experience, therapeutic ordering, cultural nuance, ethical boundaries.

### Rules

- Stored under `SOURCE_OF_TRUTH/human_seeds/`
- **Never** read by runtime
- **Never** referenced by `phoenix_v4/` code
- Used **only** by offline mining tools
- CI must fail if any runtime file imports from `human_seeds/`

### Structure

```
human_seeds/<pack_name>/
├── doctrine/
├── seeds/pf_*.json
├── CONTENT_TEAM_SPEC.md
└── EXEMPLARS.md
```

### Canonical Transformation Rule

**1 human seed → 5–7 micro-story atoms**

Human prose is mined, not reused. Atoms must be:
- Unresolved
- Role-pure
- Location-agnostic
- Composable
- Ethically safe
- 60–120 words max (role-specific — see §5 word range table)
- Second person or third person (per role)
- Present tense
- Open ending — no resolution

---

## 8. Seed Mining Pipeline (Offline)

### Pipeline Flow

```
human_seeds/
    ↓
semantic_segmenter.py        → segment into: incident, body, validation, pattern, mechanism, agency
    ↓
role_extractor.py            → map to: recognition, embodiment, pattern, mechanism_proof, agency_glimmer
    ↓
rewrite_as_atom.py           → role-specific word count, role-pure, unresolved
    ↓
lint_atom.py + cadence_checks.py  → hard gates
    ↓
repair_loop.py               → max 2 attempts on failure
    ↓
candidate atoms              → await human approval
    ↓ (human approval)
approved atoms               → runtime-visible
```

### Rewrite Rules (Hard)

All atoms must satisfy:

- Role-specific word count (see §5): recognition 60–90, embodiment 60–80, pattern 60–90, mechanism_proof 60–120, agency_glimmer 60–90
- Role-pure (see §5 role table)
- Open ending
- No reassurance
- No outcome
- No location names or proper nouns
- No "you will heal", "this gets better", "everything will be okay"
- End with period
- No trailing fragments (e.g., "They h")
- No repeated sentences

### Repair Loop (Bounded, Auditable)

On lint or cadence failure:
1. Emit `<role>_repair.json`
2. Attempt repair (max 2 attempts)
3. Validate repaired text: different from original, passes lint, passes cadence
4. Accept only if all gates pass
5. All failures logged to `artifacts/seed_mining/_rejects/`

---

## 9. Golden Phoenix Coverage System

**Purpose:** Ensures 100% atom coverage across all persona × topic × engine × role combinations so assembly never fails due to missing content.

### Dual Writer Architecture

Two writer modes for generating atoms:

| Writer | Command | LLM Required? | Quality | Use Case |
|---|---|---|---|---|
| **template** | `--writer template` | No | Structural placeholder | Development, CI testing |
| **qwen** | `--writer qwen` | Yes (local LLM) | Production-quality | Content upgrade, scale |

### Key Tools

**Coverage filler:**
```bash
# Template writer (no LLM, fast)
make v4_story_fill
# or: python3 tools/golden_phoenix/run_golden_phoenix_v4_coverage.py --slots-per-role 5

# Qwen LLM writer (production quality)
make v4_story_fill_qwen
# or: python3 tools/golden_phoenix/run_golden_phoenix_v4_coverage.py \
#     --writer qwen --slots-per-role 5 --base-url http://127.0.0.1:1234/v1

# Full regeneration (clear existing + regenerate all)
python3 tools/golden_phoenix/run_golden_phoenix_v4_coverage.py \
    --writer qwen --clear-legacy --slots-per-role 5
```

**Legacy atom repair (structural bar):**
```bash
make v4_legacy_repair
# or: python3 tools/golden_phoenix/repair_legacy_story_atoms.py
```

Rewrites all legacy micro `.txt` to: no trailing fragment, no repeated sentences, end with period, ≤150 words.

**Per-teacher compilation:**
```bash
python3 tools/golden_phoenix/golden_phoenix_runner.py --teacher <id>
```

**Batch + full coverage verification:**
```bash
python3 tools/golden_phoenix/run_golden_phoenix.py --mode compile_universe
python3 tools/golden_phoenix/run_golden_phoenix.py --mode v4_full_coverage
```

`v4_full_coverage` runs `compile_universe` then verifies all personas, unified topics, and locations. Writes `artifacts/v4_full_coverage_summary.json`. Exit 0 only when 100%.

### System Atom Packs (Intermediate Format)

Between seeds and atoms, there is an intermediate "pack" format under `prompts/v4/system_atoms/`:

- Packs encode the prompt context for generating atoms
- Each pack targets one (persona, topic, role) combination
- Template writer uses hash of pack text for deterministic, unique content
- Qwen writer sends pack text to LLM for generation
- Output is linted before writing to `story_atoms/`

### Minimum Variant Thresholds

Defined in `phoenix_v4/policy/format_story_quality.yaml`:

```yaml
standard_book:
  min_atoms_per_role:
    recognition: 10
    embodiment: 8
    pattern: 10
    mechanism_proof: 10
    agency_glimmer: 8
  require_confirmed: true    # when V4_STRICT is on
```

Aim for **≥5 variants per role** minimum for any assembly to succeed. Format-specific policies may require more.

### Anti-Template Semantic Uniqueness Guard

At scale (1,008+ plans, 10+ variants per role), the template writer produces deterministic content that can converge semantically — different words, same meaning. The Qwen writer can also produce similar outputs across packs. Without a uniqueness guard, assembled books feel repetitive even when no literal repetition exists.

**Semantic fingerprint check:**

After atom generation (either writer), run a pairwise similarity check within each (persona, topic, role) group:

```
For all atoms in story_atoms/{persona}/{topic}/*/{role}/micro/:
  pairwise_similarity = cosine_similarity(embedding(atom_i), embedding(atom_j))
  if pairwise_similarity > SEMANTIC_UNIQUENESS_THRESHOLD:
    flag atom_j as redundant
```

**Thresholds:**

```yaml
semantic_uniqueness:
  threshold: 0.85            # flag if cosine similarity > 0.85
  hard_reject: 0.92          # auto-reject if > 0.92
  embedding_model: "default"  # use available sentence embedding
  check_scope: per_role       # within same (persona, topic, role)
```

**Enforcement:**
- `make v4_story_fill` and `make v4_story_fill_qwen` should run the uniqueness check after generation
- Flagged atoms are logged to `artifacts/semantic_duplicates.json` with the pair and similarity score
- Hard-rejected atoms are moved to `_rejects/` with reason `semantic_duplicate`
- Coverage report includes `semantic_diversity` status per (persona, topic, role): `diverse | partially_redundant | highly_redundant`

**CI gate addition:** `story_atoms_coverage_report.py` must report semantic diversity alongside variant counts.

---

## 10. Coverage Checking Infrastructure

**Purpose:** Verify atom availability before assembly so books never fail due to missing content.

### Tools

**Per persona × topic readiness:**
```bash
python3 phoenix_v4/ci/check_topic_readiness.py <topic> <persona> \
    --min-level RELEASE_READY --verbose
```

**Full coverage report (all personas × topics):**
```bash
python3 phoenix_v4/ci/story_atoms_coverage_report.py \
    --out artifacts/story_atoms_coverage.json
```

Output format per persona::topic:
```json
{
  "gen_z_la::anxiety": {
    "status": "READY",           // READY | PARTIAL | MISSING
    "roles": {
      "recognition": { "confirmed": 10, "provisional": 5 },
      "embodiment": { "confirmed": 8, "provisional": 3 },
      "pattern": { "confirmed": 10, "provisional": 4 },
      "mechanism_proof": { "confirmed": 8, "provisional": 3 },
      "agency_glimmer": { "confirmed": 7, "provisional": 4 }
    },
    "missing_hints": []
  }
}
```

**Plan-time coverage (when compiling a plan):**

`compile_format_plan` uses `phoenix_v4/planning/coverage_checker.py` and `phoenix_v4/policy/format_story_quality.yaml`. Without `--allow-coverage-gaps`, it raises when counts are below the format's `min_atoms_per_role` (when `V4_STRICT` is on).

### Status Levels

| Status | Meaning |
|---|---|
| **READY** | All required roles have ≥ min variants for at least one allowed engine |
| **PARTIAL** | Some roles covered, some below threshold |
| **MISSING** | No atoms for this persona × topic combination |

### V4_STRICT Mode

When `V4_STRICT=1`:
- Only `status: confirmed` atoms count toward coverage
- `provisional` atoms are ignored
- `--allow-coverage-gaps` is rejected

When `V4_STRICT=0` (development):
- Both `confirmed` and `provisional` atoms count
- `--allow-coverage-gaps` is accepted

---

## 11. Persona Fallback System

**Purpose:** Temporary mechanism to prevent assembly failure when atom coverage is incomplete.

**Location:** `phoenix_v4/libraries/micro_story_loader.py`

```python
PERSONA_FALLBACK = {
    "gen_z_la": "gen_z_professionals",
    "healthcare_burnout": "gen_z_professionals",
    # ... additional mappings
}
```

### Rules

- Enabled per-injector with `use_persona_fallback=True`
- When the requested (persona, topic, role, engine) has no atoms, falls back to another persona's atoms
- **This is NOT a substitute for real coverage** — prefer adding real atoms
- Fallback usage should be logged and tracked
- Target: deprecate once all persona × topic combinations reach READY status

---

## 12. Approval System

### Atom Approval

**Tool:** `tools/approval/approve_atoms.py`

**Commands:** `list`, `approve`, `reject`, `auto`, `dry-run`

This tool only moves files and metadata. It **never** rewrites content.

**Required metadata on every approved atom:**
```yaml
approval:
  status: approved
  approved_by: <human>
  approved_at: <ISO-8601 UTC>
  promotion_reason: manual | auto_confident
```

### Auto-Promotion Rules (All Must Pass)

| Category | Rule |
|---|---|
| Structural | Lint passed |
| Cadence | Cadence ≥ family minimum + buffer |
| Language | No forbidden language (resolution, reassurance) |
| Location | No location leakage (proper nouns, hardcoded places) |
| Role Purity | Role constraints satisfied (see §5) |
| Redundancy | Semantic similarity < 0.85 vs approved atoms in same role |
| Writer Trust | ≥20 approved atoms for this role |
| Writer Trust | Reject rate over last 50 atoms < 10% |

Auto-promotion failures are **silently skipped** — atom stays in candidate.

### Families That NEVER Auto-Promote

Defined in `docs/NO_AUTO_PROMOTION_FAMILIES.yaml`:

```yaml
- grief_pack
- trauma_recovery
- suicide_loss
- terminal_illness
- child_abuse
- domestic_violence
```

**Rationale:** These families require human witnessing, not statistical confidence. This is an **ethical** constraint, not a quality constraint.

### Exercise Approval

**Tool:** `tools/approval/exercise_approve.py`

**Commands:**
```bash
# Approve one
python3 tools/approval/exercise_approve.py approve \
    --id ex_90_second_reset --by "content_lead" --note "Fits gen_alpha anxiety"

# Reject one
python3 tools/approval/exercise_approve.py reject \
    --id ex_x --by "content_lead" --note "Too outcome-y in integration"

# Auto-promote batch (with safeguards)
python3 tools/approval/exercise_approve.py auto-promote \
    --persona gen_alpha --topic anxiety --min-score 0.9 --max-count 50
```

Auto-promote **hard fails** if target family is in never-auto-promote list.

---

## 13. Story Bank, Registries & Cultural Specificity

### 13.0 Principle

All cultural and geographic specificity lives **outside** atoms. Atoms use **placeholders only**. Hard-coded locations or proper nouns inside atoms are forbidden. The registries and Story Bank data files define what the system *knows about the world* — personas, topics, locations, and how they intersect.

### 13.1 Persona Registry Schema

**Location:** `SOURCE_OF_TRUTH/registry/personas.yaml`

Each persona entry must define:

```yaml
persona_id: gen_z_students              # unique identifier, used in all file paths
display_name: "Gen Z Students"
archetype: "The Overwhelmed Optimizer"
status: active

generation:
  label: "Gen Z"
  birth_years: [1997, 2012]
  age_band: "18-27"

roles:
  primary: "student"
  secondary: ["job_seeker", "gig_worker"]

demographics:
  geo_anchors: ["US metro areas"]       # broad geo; specifics come from overlays
  income_band: "entry_level"
  education_band: "college_current_or_recent"

psychographics:
  core_psychology: "<how they think about themselves>"
  relationship_to_self_help: "<how they find and consume therapeutic content>"
  wellness_paradox: "<the contradiction in their wellness behavior>"
  identity_tension: "<the core identity friction>"

wellness_priorities:                     # ranked — drives mining priority
  - anxiety
  - burnout
  - sleep_rest
  - social_connection
  - self_confidence

language:
  register: casual                       # casual | professional | clinical | mission_coded
  trigger_words: [...]                   # words/phrases that build trust
  repellent_words: [...]                 # words/phrases that break trust instantly
  framing_style: experiential            # experiential | evidence_based | narrative | clinical
  framing_examples:                      # same concept, persona-specific language
    breathwork: "body reset"             # gen_z
    # vs. "tactical breathing"           # military
    # vs. "diaphragmatic regulation"     # clinical

content_delivery:
  preferred_session_lengths: [10, 15, 20]
  peak_consumption_hours: ["22:00-23:30", "07:00-08:00"]
  consumption_contexts: ["commute", "bedtime", "study_break"]
  narration_preference:
    warmth: warm
    authority: peer
    pace: moderate
    tone: "<voice description for TTS>"
  depth_preference: moderate             # surface_practical | moderate | deep_contemplative

location_binding:
  primary_locale_id: null                # null for base personas
  overlay_ids: []                        # populated for location variants
```

**Critical fields for Phoenix runtime:**
- `language.trigger_words` / `language.repellent_words` — fed to atom lint to catch persona-inappropriate language
- `language.framing_examples` — fed to the hydrator so the same therapeutic concept uses persona-appropriate vocabulary
- `wellness_priorities` — ranked list drives mining priority matrix (see §13.5)
- `content_delivery.narration_preference` — feeds ElevenLabs TTS voice selection
- `psychographics.relationship_to_self_help` — informs scene writing briefs

### 13.2 Topic Registry Schema

**Location:** `SOURCE_OF_TRUTH/registry/topics.yaml`

Each topic entry must define:

```yaml
topic_id: anxiety
display_name: "Anxiety"
status: active

subtopics:
  - social_anxiety
  - performance_anxiety
  - generalized_worry
  - panic_response

allowed_engines:                         # mirrors topic_engine_bindings.yaml
  - avoidance_trap
  - false_alarm
  - legacy

generational_affinity:
  gen_z: primary
  gen_alpha: primary
  millennial: high
  gen_x: moderate
  boomer: moderate

no_auto_promotion: false                 # true for grief, trauma, etc.

per_persona_framing:                     # how this topic is named per persona
  gen_z_students: "when your brain won't shut up"
  healthcare_rns: "the anxiety that follows you home"
  startup_founders: "founder anxiety"
  military_veterans: "hypervigilance"
```

The `per_persona_framing` field is critical — it ensures the same topic is described in persona-appropriate language across titles, chapter headers, and scene briefs.

### 13.3 Location Registry & Base + Overlay Architecture

**Location:** `SOURCE_OF_TRUTH/registry/locations.yaml` (index) + `data/story_bank/location_variables/<locale_id>.yaml` (per location)

#### Base + Overlay Persona Architecture

At 20 personas × 20 locations, building 400 full persona definitions creates duplication. Instead, V4 uses a **base + overlay** system:

```
gen_z_students (BASE PERSONA)
  + nyc.yaml (LOCATION OVERLAY)
  + college.yaml (ENVIRONMENT OVERLAY)
  = gen_z_students_nyc_college (ASSEMBLED PERSONA CONTEXT)
```

**Base persona** — Full psychographic profile, topic affinities, language register, content delivery preferences. Location-agnostic. Defined in `registry/personas.yaml`.

**Location overlay** — City-level sensory cues, transit landmarks, neighborhoods, seasonal rhythms, sacred spaces. Persona-agnostic. Defined in `data/story_bank/location_variables/<locale_id>.yaml`.

**Environment overlay** — Context-specific sensory cues (hospital, campus, office). Stacks on top of location. Defined in `data/story_bank/location_variables/<environment_id>.yaml`.

**Cultural overlay** — The intersection: how *this persona* experiences *this location*. Defined in `data/story_bank/cultural_overlays/<persona_id>_<locale_id>.yaml`.

#### Location Variable File Schema

```yaml
locale_id: nyc
display_name: "New York City"
status: active

transit:
  lines:
    - id: "A_train"
      description: "Runs from Inwood to Far Rockaway"
      emotional_signature: "long haul, deep Brooklyn, late night"
    - id: "L_train"
      description: "Bedford Ave to 8th Ave"
      emotional_signature: "creative commute, Williamsburg"
  commute_landmarks:
    - "Westside Highway at 6 AM"
    - "Grand Central rush hour crowd"
    - "the Q train over the Manhattan Bridge"

neighborhoods:
  - id: "williamsburg"
    sensory_cues: ["coffee shop laptops", "vintage store awnings", "bike lanes"]
  - id: "washington_heights"
    sensory_cues: ["merengue from car windows", "bodega cats", "fire escapes"]

seasonal:
  summer: "fire hydrant spray, sticky subway platforms, rooftop at sunset"
  winter: "steam from grates, coat over coat, 4:30 PM dark"
  fall: "Central Park gold, back-to-school energy, first cold morning"
  spring: "cherry blossoms Fort Tryon, windows open finally, stoop sitting"

sacred_spaces:
  - "the quiet car on Metro-North"
  - "the Cloisters on a Tuesday afternoon"
  - "Prospect Park at dawn"
```

#### Cultural Overlay File Schema (Persona × Location)

```yaml
persona_id: gen_z_students
locale_id: nyc
overlay_id: gen_z_students_nyc

transit_experience:
  primary_line: "L train"
  emotional_context: "headphones in, avoiding eye contact, pretending to be somewhere else"
  commute_ritual: "AirPods → playlist → stare at phone → miss stop occasionally"

neighborhood_anchors:
  - neighborhood: "east_village"
    role: "weekend identity"
    scene_cue: "thrift stores and $1 pizza at 2 AM"
  - neighborhood: "morningside_heights"
    role: "academic pressure"
    scene_cue: "Butler Library at midnight, everyone pretending they're fine"

location_specific_pressure:
  - "NYC rent anxiety before they even graduate"
  - "everyone seems to already have an internship"
  - "the city moves fast and they feel behind"

sacred_spaces:
  - "the roof of their dorm at night"
  - "the back corner of a coffee shop where no one talks to them"
```

This is what the hydrator reads when it encounters `{{location.transit_line}}` or `{{sensory.sacred_space}}` for a Gen Z student in NYC. Without these files, placeholders resolve to nothing.

### 13.4 Social Patterns & Pressure Themes Schemas

**Social patterns** — per persona, not per location. Stored in `data/story_bank/social_patterns/<persona_id>.yaml`:

```yaml
persona_id: gen_z_students

social_pressures:
  - "group chat exclusion dynamics"
  - "follower counts as social currency"
  - "fear of being 'cringe'"

status_games:
  - "phone model and tech access"
  - "who knows the latest trends first"

identity_friction:
  - "online persona vs. classroom self"
  - "wanting independence while needing support"

common_scenes:
  - "lunch table choosing — who to sit with"
  - "lying in bed scrolling at midnight"
  - "bedroom door closed, finally alone"
```

**Pressure themes** — per persona. Stored in `data/story_bank/pressure_themes/<persona_id>.yaml`:

```yaml
persona_id: gen_z_students

financial_pressures:
  - "seeing peers with things they can't afford"
  - "parent financial stress absorbed through household tension"

career_pressures:
  - "premature pressure to know what you want to be"
  - "college prep anxiety starting in middle school"

health_pressures:
  - "anxiety as a background hum they've never not known"
  - "sleep disruption from screen use"

existential_pressures:
  - "climate anxiety absorbed from media"
  - "feeling like the world is broken and they'll have to fix it"
```

Scene writers receive these files as creative briefs. They inform what social dynamics and pressures appear in scenes — but writers don't copy them literally.

### 13.5 Mining Priority Matrix

At scale (20 personas × 100 topics × 20 locations = 40,000 combinations), you cannot mine everything at once. The mining priority matrix ranks combinations by affinity and market demand.

**Generated by:** `tools/persona_research/generate_mining_priority.py`

**Output:** `artifacts/mining_priority_matrix.yaml`

```yaml
priority_tier_1:    # mine first — entry points for highest-affinity personas
  - persona: gen_z_students
    topic: anxiety
    affinity: primary
    is_entry_point: true
    reason: "#1 ranked topic, primary affinity, entry point"
  - persona: healthcare_rns
    topic: burnout_recovery
    affinity: primary
    is_entry_point: true

priority_tier_2:    # mine second — high affinity, not entry points
  - persona: gen_z_students
    topic: loneliness
    affinity: high
    is_entry_point: false

priority_tier_3:    # mine when tier 1+2 coverage is READY
  # ...
```

**Rules:**
- Entry point topics (the acceptable door for each persona) are always tier 1
- Hidden need topics (what they actually need) are tier 2 — they come *after* the entry point hooks them
- Low-affinity combinations (e.g., elder_wisdom / digital_wellness) are tier 3 or deprioritized
- The matrix is regenerated when personas or topics are added
- Golden Phoenix coverage filler (§9) uses this matrix to decide what to fill first

### 13.6 Placeholder Catalog

Complete list of allowed placeholder namespaces:

```
{{location.neighborhood}}
{{location.transit_line}}
{{location.school_type}}
{{sensory.ambient_sound}}
{{sensory.school_sound}}
{{sensory.seasonal_cue}}
{{social.hangout_spot}}
{{social.peer_group}}
{{social.after_school_routine}}
{{transit.commute_style}}
{{transit.commute_landmark}}
{{pressure.theme}}
{{pressure.academic}}
{{pressure.social}}
{{cultural.food_reference}}
{{cultural.music_reference}}
{{seasonal.cue}}
{{language.framing}}              # persona-specific topic framing from registry
```

New placeholders require schema update in `docs/persona_topic_variables.schema.yaml` and review. Writers do NOT invent new variables casually.

### 13.7 Persona × Topic Variable Schema

**Location:** `docs/persona_topic_variables.schema.yaml`

This is a **compiler contract** — the planner must fail if required variables are missing for a given persona × topic × chapter combination.

```yaml
gen_z_la:
  anxiety:
    required_variables:
      - social.hangout_spot
      - transit.commute_style
      - pressure.academic_type
    per_chapter:
      ch01:
        emotional_requirement: recognition_of_pattern
        required_stakes: social_exposure
      ch05:
        emotional_requirement: mechanism_understanding
        required_stakes: internal_cost
      ch10:
        emotional_requirement: agency_without_resolution
        required_stakes: identity_cost
```

### 13.8 Rules

- Writers do **NOT** invent new variables casually
- New variables require schema update and review
- Planner must fail if required variables are missing
- Hydration occurs at assembly time via `location_hydrator_v4.py`
- Base personas are location-agnostic — location comes from overlays
- Cultural overlays define persona × location intersections — the hydrator reads these
- Social patterns and pressure themes are per-persona creative briefs, not per-location
- The mining priority matrix determines what gets mined first — entry points before deep topics

---

## 14. Scene Injection Architecture

### 14.1 Scene vs Story vs Atom (Architectural Distinction)

This distinction is critical. Confusing them breaks injection modularity.

**Atom** — An insight container. 60–120 words (role-specific). Role-pure. No character dependency. Injection-flexible. Answers: *"What did they realize?"*

**Scene** — A narrative container. 300–600 words. Person-based. Named character. Real location. Specific moment in time. Social stakes. Emotional cost. Unresolved. Injection-ready. Answers: *"What happened?"*

**Story** — A full arc. Multi-scene progression. Has escalation, cost, identity movement, turning point, embodiment. Answers: *"What changed?"*

A story is composed of:
```
Scene + Scene + Atom + Exercise + Scene + Atom + Scene
```

In V4:
- Scenes = narrative units (the bricks)
- Atoms = insight units (the mortar)
- Exercises = regulation units (the pauses)
- Story = the arranged arc across chapters (the architecture)

**Why this matters:** If you confuse scene and story, you overinflate scenes, try to make them resolve, weaken incompleteness, and break injection modularity. A scene must feel like *a slice of life*. A story must feel like *a shift in identity*.

### 14.2 What Scenes Are

- 300–600 word person-based authored assets
- Named character with age range
- Real-world location (persona-locked or overlay-ready)
- Social stakes present
- Emotional cost present
- Body sensations named
- At least one callback object
- Ends unresolved — no cure, no resolution, no moral
- Injection-ready modular container

A scene is **NOT**: a full arc, a motivational speech, an atom, a story, or an exercise.

### 14.3 Scene YAML Schema (Canonical)

Every scene must be stored in this format. This is what the planner, assembler, and validation gates read.

```yaml
id: scene_l01_birthday_post
asset_type: scene
version: 1
status: approved

persona: gen_z_students
topic: loneliness

locale_mode: persona_locked       # persona_locked | overlay_ready

v4_role: recognition              # recognition | embodiment | pattern | mechanism_proof | agency_glimmer
identity_stage: destabilization   # pre_awareness | destabilization | experimentation | self_claim
mechanism_depth: 1                # 1=surface, 2=behavioral, 3=nervous_system, 4=identity

cost_type: social                 # social | internal | opportunity | identity
cost_intensity: 2                 # 1–5

emotional_intensity: 3            # 1–5, aligns with macro cadence
regulation_support_required_after: false

stakes_type: social_invisibility

callback:
  callback_id: birthday_silence
  callback_phase: setup           # setup | escalation | return

epigraph_mechanism_line: |
  Loneliness isn't the absence of people — it's the gap between being known and being seen.

characters:
  - name: Amara
    age_range: 18-22

content: |
  <exact writer prose — no edits, no rewrites>

approval:
  status: approved
  approved_by: "content_lead"
  approved_at: "2026-02-10T00:00:00Z"
```

**Note on `epigraph_mechanism_line`:** Scenes may contain an insight statement that reads like a mechanism proof. These are NOT `mechanism_proof` atoms — they are author-voice epigraphs. They are extracted into this field so the assembler can place them as chapter headers or interstitials, but they do not participate in atom-level role assignment.

### 14.4 Scene Integration SOP (Writer → System Asset Workflow)

Writers write emotionally. Integrators make assets machine-intelligent. Writers do NOT write YAML. Integrators do NOT rewrite prose.

```
STEP 1 — Writer produces raw scene (Markdown prose)
STEP 2 — Integrator performs structural mapping (role, identity, cost, callbacks)
STEP 3 — YAML metadata wrapper applied (no prose changes)
STEP 4 — Scene validated against Omega gates
STEP 5 — Scene added to approved_scenes/ library
```

Writers stop at Step 1.

#### Writer Requirements (Step 1)

Writers **must:**
- Use named characters with specific ages/contexts
- Include body sensations (chest tightens, hands grip, jaw clenches)
- Include social stakes (something is at risk between people)
- Include at least one callback object (a physical thing that can recur)
- End unresolved — no cure, no comfort, no lesson
- Stay under 600 words
- Write in short sentences (24 words max, 8th grade reading level)
- Follow the AI Banned Word Lexicon

Writers must **NOT:**
- Assign v4 roles, mechanism depth, or cost intensity
- Think about YAML, engines, or system metadata
- Write therapist explanation tone
- Moralize, advise, or resolve
- Use any word from the banned lexicon

#### Integrator Structural Mapping (Step 2)

Integrator reads the scene once emotionally, second pass structurally. Assigns all metadata fields.

**Arc Role → v4_role Mapping Table:**

| Writer's Natural Tag | Map To | Decision Rule |
|---|---|---|
| Setup | `recognition` | Pattern/tension observed, no body |
| Body moment | `embodiment` | Body sensation dominant, no cognitive framing |
| Escalation (loop) | `pattern` | Repetition, "again," "every time" — no hope |
| Escalation (explanation) | `mechanism_proof` | Understanding why the loop works |
| Relapse | `pattern` OR `mechanism_proof` | If repeating → pattern; if understanding why → mechanism_proof |
| Identity / Identity erosion | `agency_glimmer` | Choice present, even if small |
| Social cost | `recognition` OR `pattern` | If external observation → recognition; if recurring → pattern |
| Quiet cost / body awareness | `embodiment` | Body sensation dominant |
| Hinge / crack | `agency_glimmer` | Open choice, no reassurance |

No dual roles. One primary role per scene. Integrator decides based on **function**, not emotion.

**Mechanism Depth Assignment:**

| Scene Contains | Depth |
|---|---|
| Observation of pattern (surface) | 1 |
| Behavioral loop recognition | 2 |
| Nervous system awareness (body-level) | 3 |
| Identity-level realization | 4 |

Final third of book must include depth 4. No regression across chapters.

**Cost Intensity Assignment:**

| Signal in Scene | Intensity |
|---|---|
| Discomfort | 1 |
| Social awkwardness / tension | 2 |
| Visible exclusion | 3 |
| Identity erosion | 4 |
| Existential isolation | 5 |

Escalation must increase through midpoint. Cross-gate coupling with identity stage enforced (see §18 Gate 2).

**Callback Enforcement:**

Every callback object declared in YAML. Later scenes must use `callback_phase: return`. No orphan callbacks. Max 2 new callback threads per 10-chapter arc.

**Locale Mode Decision:**

If scene will never leave this persona: `locale_mode: persona_locked` — naturalistic language stays intact.

If cross-persona scalable: `locale_mode: overlay_ready` — replace physical references with `{{location.study_spot}}`, `{{location.shared_kitchen}}`, etc.

#### Scene Validation Checklist (Step 4)

Before approval, confirm ALL:

- ✓ Named character with age range
- ✓ Real-world location present
- ✓ Body sensation present
- ✓ Social stakes present
- ✓ No cure language
- ✓ No reassurance
- ✓ Ends unresolved
- ✓ v4_role assigned (one of 5 canonical roles)
- ✓ identity_stage valid for planned chapter position
- ✓ mechanism_depth assigned and consistent with arc escalation
- ✓ cost_type and cost_intensity assigned
- ✓ emotional_intensity aligned with chapter macro-cadence
- ✓ At least one callback_id declared with phase
- ✓ locale_mode declared
- ✓ Prose unmodified from writer original

If any fail → return to integrator.

#### What Integrators Must NOT Do

- ❌ Rewrite sentences
- ❌ "Improve" prose
- ❌ Simplify language
- ❌ Remove ambiguity
- ❌ Add cure framing
- ❌ Add therapist explanation
- ❌ Add moral conclusions
- ❌ Change character names or details

Integrator role = **structural alignment only**.

### 14.5 Scene → Atom Mining Protocol

Scenes often contain standalone insight lines that are not scene content — they are atom candidates. These must be extracted and typed separately.

#### Step 1: Identify Atom Candidates

Look for: standalone insight lines, pattern observations, body-based realizations, internal contradictions, micro-hinges.

Example: *"There's a version of me that almost existed in public. I deleted her."* — This is not scene content. This is an atom.

Minimum 2 atom candidates per scene recommended.

#### Step 2: Assign Canonical Role

| Pattern Type | v4_role |
|---|---|
| Emotional mirror / "I saw myself" | `recognition` |
| Body sensation / "my chest did this" | `embodiment` |
| Repetition loop / "this keeps happening" | `pattern` |
| Loop explanation / "this is why it works" | `mechanism_proof` |
| Hinge decision / "and then something shifted" | `agency_glimmer` |

#### Step 3: Assign Identity Stage

| Identity Signal | Stage |
|---|---|
| Confusion, unawareness | `pre_awareness` |
| Shame destabilization | `destabilization` |
| Trying something new | `experimentation` |
| Subtle internal ownership | `self_claim` |

#### Step 4: Assign Mechanism Depth + Cost

Same tables as scene integration (see §14.4 above).

#### Step 5: Wrap as Atom YAML

```yaml
id: atom_s04_almost_existed_public
asset_type: atom
persona: gen_z_students
topic: shame

v4_role: embodiment
identity_stage: destabilization
mechanism_depth: 3
cost_type: identity
cost_intensity: 4

content: |
  There's a version of you that almost existed in public.
  You typed it out. You read it back. You felt your stomach tighten
  around the words. Not because they were wrong. Because they were true.
  And true felt like too much to hand to strangers.
  So you deleted it. Watched the cursor blink on the empty field.
  Your thumb hovered. Your chest held still.
  The version that almost existed is still in your body somewhere.
  You can feel where it lived before you pulled it back.

source_scene: scene_s04_reddit_comment
approval:
  status: candidate
```

The `source_scene` field traces provenance. Mined atoms start as `candidate` and require approval before assembly.

### 14.6 Scene Selection Rules

- Planner selects scenes by: persona, topic, stakes_type, v4_role, identity_stage, emotional_intensity
- Scenes are injected at designated scene slots in chapter templates
- No two adjacent chapters may use the same scene
- Deterministic selection: `hash(book_id + chapter_num + scene_slot) % len(pool)`

### 14.7 Scene–Cadence Coupling (Cross-Layer Constraint)

Scene intensity must respect the chapter's macro-cadence profile. Without this binding, a high-intensity scene can land in a regulation chapter, breaking the emotional wave.

**Rule:**

```
scene.intensity <= chapter_profile.emotional_intensity
```

**Enforcement table:**

| Chapter emotional_intensity | Allowed scene.intensity |
|---|---|
| 1–2 | gentle only |
| 3 | gentle, medium |
| 4–5 | gentle, medium, strong |

**Additional:**
- If `chapter_profile.regulation_support == high`, scene intensity must be `gentle` or `medium`
- Scene `cost_intensity` must align with the Cost Gradient requirements for that chapter phase (see §18 Gate 2)

The planner filters scene candidates by these constraints **before** deterministic selection.

### 14.8 Cross-Scene Callback Bridges

When scenes across different topics share callback objects (e.g., "phone_screen_silence" appears in both an anxiety scene and a loneliness scene), these create **cross-topic arc bridges** that the planner can use for multi-topic books.

Each bridge must be declared in scene YAML via matching `callback_id` values. The `callback_integrity_gate.py` validates that:
- Every `setup` has a corresponding `return` within the same book
- No more than 2 unclosed threads at any point
- Cross-topic bridges are flagged as `bridge_type: cross_topic` so the planner can intentionally select or avoid them

### 14.9 Quality Standard

If a scene feels like: advice, explanation, resolution, therapy, or a moral lesson → **reject**.

If a scene feels like: a moment someone lived, a cost someone paid, an identity slightly destabilized → **approve**.

### 14.10 Scene Integration Failure Modes

These are the most common mistakes. All are hard rejects.

**❌ Over-Labeling:** Don't assign multiple v4_roles to one scene. One primary role only. If a scene has both recognition and embodiment beats, pick the dominant function. The secondary beat can be mined as a standalone atom.

**❌ Premature Self-Claim:** `identity_stage` cannot be `self_claim` unless the scene is positioned in the final third of the arc. Self-claim in chapter 2 breaks identity progression. If the scene *feels* like agency, check — is it actually `experimentation` disguised as ownership?

**❌ Cost Underestimation:** If a scene contains identity erosion (character's self-concept shifts), `cost_intensity` cannot be 1 or 2. Identity erosion is a 4. Social awkwardness is a 2. Don't confuse discomfort with damage.

**❌ Callback Overload:** No more than 2 new callback objects introduced per 10-chapter arc. If a writer introduces 5 callback objects in 3 scenes, the integrator must select the 2 strongest and drop the rest. Unclosed callbacks create narrative debt the system cannot pay.

**❌ Mechanism Line Confusion:** An insight statement inside a scene ("Loneliness isn't the absence of people — it's the gap between being known and being seen") is NOT a `mechanism_proof` atom. It is an `epigraph_mechanism_line`. Extract it to the metadata field. Do not tag the scene as `v4_role: mechanism_proof` based on one line when the scene's primary function is `recognition`.

### 14.11 Key Principles

> Atoms support the arc; scenes deliver lived experience.
> Never generate scenes at runtime.
> Writers produce emotional truth. Integrators produce structural intelligence.
> V4 depends on both.

---

## 15. Exercise System

### Canonical Exercise Types (10)

```
00_breath_regulation
01_grounding_orientation
02_body_awareness_scan
03_somatic_release_discharge
04_nervous_system_downregulation
05_nervous_system_upregulation
06_vagal_stimulation_sound
07_self_contact_touch
08_emotional_processing_completion
09_embodied_intention_direction
10_integration_return_to_baseline
```

### Required Structure (Every Exercise)

```
intro               → why now (60–120 words, 2nd person, present tense, no fixing)
guided_practice     → what to do (stepwise, slow, embodied; may include counts; no promises)
aha_noticing        → what changed ("you might notice…"; insight without outcome)
integration         → return to life (soft close; open ending; no "you are healed now")
```

### Exercise YAML Schema

```yaml
id: ex_<slug>
version: 1
status: active

metadata:
  title: "The 90-Second Reset"
  persona: gen_alpha
  topic: anxiety
  intensity: gentle               # gentle | medium | strong
  duration_seconds: 120
  modalities: [breath, body_scan]
  contraindications: []
  tags:
    cadence_role: grounding       # grounding | activation | release | integration
    chapter_position_ok: [mid, late]
  language_level: "8th_grade"
  locale_mode: "location_agnostic"
  placeholders_required: []

content:
  intro: |
    <60–120 words>
  guided_practice: |
    <stepwise, embodied>
  aha_noticing: |
    <"you might notice…">
  integration: |
    <soft close, open ending>

quality:
  banned_phrases_checked: true
  contains_no_resolution_language: true
  second_person_present_tense: true
  min_words_per_section:
    intro: 60
    guided_practice: 80
    aha_noticing: 40
    integration: 40

approval:
  status: approved
  approved_by: "content_lead"
  approved_at: "2026-02-10T00:00:00Z"
  notes: ""
```

### ExerciseResolver (Deterministic Selection)

**Inputs:** persona_id, topic_id, chapter_num, template_family, slot_id, location_context, seed (book_id), constraints

**Algorithm:**
1. Filter approved exercises by persona/topic
2. Apply template-family filters
3. Apply constraints (intensity, modalities, duration)
4. **Apply identity-stage coupling** (see below)
5. Enforce no adjacent reuse across chapters
6. Deterministic choice: `hash(book_id + chapter_num + slot_id) % len(pool)`
7. Prefer exercises not used in previous N chapters

### Exercise–Identity Stage Coupling (Cross-Layer Constraint)

Exercises selected by modality alone are functionally correct but not narratively intelligent. The ExerciseResolver must also filter by the chapter's `identity_stage` so the exercise *supports where the reader is in their identity journey*.

**Required mapping:**

| Chapter identity_stage | Preferred exercise cadence_role | Preferred modalities |
|---|---|---|
| `pre_awareness` | grounding | breath, body_scan, grounding |
| `destabilization` | grounding, release | breath, body_scan, somatic_release, downregulation |
| `experimentation` | activation, release | upregulation, vagal_stimulation, emotional_processing |
| `self_claim` | integration | embodied_intention, integration_return |

**Rules:**
- The resolver **must** prefer exercises matching the identity stage (filter first, then fall back to all if pool is empty)
- A `destabilization` chapter must **never** select an `activation` exercise (risk of dysregulation)
- A `self_claim` chapter must **never** select a `grounding` exercise (undermines agency)
- Mismatches are logged as warnings; hard-fail only if the mismatch is in the blocked combinations above

### Exercise Slot Policy

```yaml
# docs/EXERCISE_SLOT_POLICY.yaml
slot_07_practice:
  required: true
  allowed_modalities: [breath, body_scan, grounding, visualization, journaling]
  allowed_intensity: [gentle, medium]
  max_duration_seconds: 240
  cadence_role: [grounding, release, integration]

template_overrides:
  bestseller_v2_1:
    slot_07_practice:
      allowed_intensity: [gentle]
      cadence_role: [grounding]
```

### Exercise Lint (Hard Gates)

1. Schema validity (required keys, valid persona/topic)
2. All 4 sections non-empty, min word counts
3. Voice: second-person dominant, present tense
4. No resolution/cure language ("you will feel better", "this will heal")
5. No unsafe therapy claims (no medical guarantees)
6. Cadence: intro has emotional safety line, integration doesn't "wrap up"
7. Placeholder integrity: only from allowed overlay schema
8. Style blacklist: no toxic positivity, shame language, "just…"

Reject logs written to `SOURCE_OF_TRUTH/exercises_v4/_rejects/<exercise_id>.log`.

### Families That NEVER Auto-Promote Exercises

```yaml
never_auto_promote:
  - grief_pack
  - trauma_sensitive
  - crisis_support
```

---

## 16. Planning Layer

### What Plans Are

Plans declare **requirements**, not text. They are contracts.

### Plan Compilation

**Tool:** `phoenix_v4/planning/compile_format_plan.py`

**Inputs:**
- format_type (e.g., `standard_book`)
- persona
- topic
- seed (for deterministic assembly)

**Process:**
1. Load `topic_engine_bindings.yaml` to determine allowed engines
2. Check coverage via `coverage_checker.py` against `format_story_quality.yaml`
3. Select arc variant
4. Assign required story roles per chapter
5. Assign scene injection points
6. Assign exercise function slots
7. Validate all requirements can be met from available assets
8. Output: compiled plan YAML

**Failure:** If required inputs are missing or coverage is insufficient → **hard fail** (no plan, no book).

### Plan Requirements

A compiled plan specifies per chapter:
- Which story roles (recognition, embodiment, pattern, mechanism_proof, agency_glimmer)
- Which scene slots and scene requirements (stakes type, intensity)
- Which exercise slots (function, intensity, modality)
- Required mechanism engine
- Required persona variables (from `persona_topic_variables.schema.yaml`)

### Format Types

| Format | Description | Chapters | Key Requirements |
|---|---|---|---|
| `standard_book` | Full-length therapeutic journey | 10 | Full arc, all roles, scenes + exercises |

Additional format types defined in `phoenix_v4/policy/` as needed.

---

## 17. Runtime Assembly

### Principle

Runtime **never generates prose**. It selects, orders, hydrates, and validates.

### Assembly Flow

```
Compiled Plan
    ↓
Select approved atoms (by persona, topic, engine, role)
    ↓
Select approved scenes (by persona, topic, stakes)
    ↓
Select approved exercises (by function, intensity, modality)
    ↓
Order by plan (chapter structure, slot assignments)
    ↓
Hydrate variables (location_hydrator_v4)
    ↓
Validate completeness (all slots filled, all requirements met)
    ↓
Output assembled book
```

### Runtime Cannot

- Rewrite text
- Generate new prose
- "Improve" content
- Fill missing meaning
- Summarize or compress
- Resolve pain

### Deterministic Assembly

- All selections use seeded determinism: `hash(book_id + chapter_num + slot_id)`
- Same seed → same book (reproducible)
- No randomness without seed

### Duration Modes

V4 supports duration-tagged section variants:

| Mode | Description |
|---|---|
| `short` | Condensed version (~15 min audiobook) |
| `standard` | Standard length (~30 min audiobook) |
| `long` | Extended version (~45 min audiobook) |

Section variants are tagged in their metadata. The assembler selects the matching variant based on the plan's requested duration mode.

### Location Hydration

**Module:** `phoenix_v4/libraries/location_hydrator_v4.py`

- Reads placeholder tokens in assembled text (e.g., `{{social.hangout_spot}}`)
- Looks up values from `SOURCE_OF_TRUTH/data/story_bank/location_variables/`
- Injects culturally appropriate, persona-specific values
- If no location context → placeholders remain unresolved (lint must allow this)

---

## 18. Validation Gates

### Structural Validation (Fail = No Book)

A book fails if:
- Narrative arc incomplete
- No stakes
- Exercises missing
- Cadence broken
- Persona violated
- Required story roles missing from any chapter

**There is no fallback content. Fail fast > degrade silently.**

### Role Purity & Person Compliance Gates

These gates run at atom approval time and at assembly time. They catch violations that manual review misses at scale.

#### `role_purity_gate.py`

Scans atom content against the §5 role table's "Must NOT Include" column using lexeme detection:

| Role | Forbidden Lexemes | Examples |
|---|---|---|
| `recognition` | Body lexemes | chest, jaw, hands, stomach, throat, shoulders, breath, spine, gut, knuckles |
| `embodiment` | Cognitive/explanatory framing | because, reason, understand, realize, means, therefore, explains |
| `pattern` | Hope/progress signals | better, improving, healing, finally, at last |
| `mechanism_proof` | Advice/prescription | should, try to, need to, the fix, the answer |
| `agency_glimmer` | Reassurance/triumph | everything will, you're going to be, it gets better, victory, overcame |

The lexeme lists are maintained in `phoenix_v4/policy/role_purity_lexicons.yaml` and can be extended without code changes.

**Behavior:** Flag as warning if 1 forbidden lexeme detected. Hard-fail if 2+ detected in same atom. Flagged atoms are logged to `artifacts/role_purity_flags.json` with the atom ID, role, and matched lexemes.

#### `person_compliance_gate.py`

Scans atom content for first-person pronouns: `I`, `my`, `me`, `mine`, `myself`, `we`, `our`, `us`.

**Rules:**
- Atoms must be second person ("you") or third person ("she," "they")
- First-person detected → hard fail, no exceptions
- Scenes are exempt (scene characters may use first person in dialogue and internal monologue)
- Exercises are exempt (exercise prompts may use first person in guided practice)

**CI gate:** Both gates run as part of `make lint` and as pre-approval checks in `approve_atoms.py`.

### V4 Prose QA Gate Stack (6 Gates)

Runs after assembly in `phoenix_v4/assembler/assemble_v4.py` and `phoenix_v4/validators/validate_omega_v4.py`:

| Gate | What It Checks | Fail Condition |
|---|---|---|
| **1. Order-Implication** | Narrative ordering is logical | Story roles appear out of sequence |
| **2. Format Banned Patterns** | No forbidden language patterns | Resolution, reassurance, cure language detected |
| **3. Topic Drift** | Book stays on-topic | Content drifts from declared topic |
| **4. Helpfulness** | Therapeutic value present | Book provides no therapeutic movement |
| **5. Repetition** | No repeated content | Same phrase/paragraph appears multiple times |
| **6. Safety/Voice** | Voice consistency + safety | Persona voice violated, unsafe content detected |

**Campaign tooling:**
```bash
# Run 1000-book validation campaign (resumable)
make v4_qa_1000
# or: python3 phoenix_v4/tools/run_v4_prose_qa_campaign.py \
#     --format-type standard_book --count 1000 --seeds 84 \
#     --allow-coverage-gaps --out-jsonl artifacts/v4_prose_qa_results.jsonl

# Generate summary report
make v4_qa_summary
# → artifacts/v4_prose_qa_summary.json
# → artifacts/v4_prose_qa_report.md

# Clean results
make v4_qa_clean
```

### Omega Narrative Intelligence Gates (5 Gates)

These sit **above** the structural validation layer. They enforce narrative quality, not just safety.

#### Gate 1: Mechanism Escalation

Atoms gain metadata:
```yaml
metadata:
  mechanism_depth: 1   # 1=surface, 2=behavioral, 3=nervous_system, 4=identity
```

**Required escalation per arc (10-chapter book):**

| Phase | Required Depth |
|---|---|
| Early (ch 1–3) | depth 1–2 |
| Mid (ch 4–6) | depth 2–3 |
| Late (ch 7–10) | depth 3–4 |

**Rules:**
- `max(mechanism_depth in chapter N) >= max(mechanism_depth in chapter N-1)` — no regression
- Depth must not plateau after midpoint
- No depth-4 identity-level mechanism required by final third

**CI gate:** `mechanism_escalation_gate.py`

#### Gate 2: Cost Gradient

Scenes and atoms gain metadata:
```yaml
metadata:
  cost_type: social | internal | opportunity | identity
  cost_intensity: 1-5
```

**Required arc gradient:**

| Phase | Required Cost |
|---|---|
| ch 1–2 | intensity 1–2 |
| ch 3–6 | intensity 2–4 |
| ch 7–9 | intensity 4–5 |
| Final chapter | resolution without erasing cost history |

**Rules:**
- `avg(cost_intensity per chapter)` must increase through midpoint
- Highest cost must not occur before midpoint
- No high-intensity cost before identity shift
- Cost must not disappear too early

**Cross-gate coupling (Cost → Identity):**

Cost and identity are **causally linked**, not parallel tracks. The planner must enforce:

```
If cost_intensity >= 4 in chapter N
→ identity_stage must be destabilization or experimentation in chapter N or N+1
```

```
If identity_stage == self_claim in chapter N
→ at least one chapter in N-3..N-1 must have cost_intensity >= 4
```

Without this binding, a book can have high cost with no identity movement (trauma without growth) or identity shift with no cost (cheap transformation). Both are narrative failures.

**CI gate:** `cost_gradient_gate.py` (must also validate cross-gate coupling with identity)

#### Gate 3: Callback Integrity

Scenes gain metadata:
```yaml
metadata:
  callback_id: "train_mirror"
  callback_phase: setup | escalation | return
```

**Rules:**
- If a `callback_id` appears in early chapter, it must reappear later with `callback_phase=return`
- No more than 2 unclosed symbolic threads
- Return requires setup; setup requires eventual return

**Arc requirements:**
```yaml
arc_requirements:
  requires_callback: true
  callback_min_count: 2
```

**CI gate:** `callback_integrity_gate.py`

#### Gate 4: Identity Shift

Atoms gain metadata:
```yaml
metadata:
  identity_stage: pre_awareness | destabilization | experimentation | self_claim
```

**Required progression:**

| Phase | Required Stage |
|---|---|
| Early | pre_awareness |
| Mid | destabilization |
| Late | experimentation |
| Final | self_claim (subtle, not grandiose) |

**Rules:**
- Identity stage progression is **monotonic** — no regression
- No experimentation before mid chapters
- Final chapter must include `self_claim`
- Identity shift must not happen too early

**CI gate:** `identity_shift_gate.py`

#### Gate 5: Macro-Cadence Wave

Each chapter declares:
```yaml
chapter_profile:
  emotional_intensity: 1-5
  regulation_support: low | medium | high
```

**Rules:**
- No 3 consecutive intensity=5 chapters
- Every high-intensity chapter must be followed by medium/high regulation chapter
- No monotonic increase without relief
- Regulation support required in second half

**CI gate:** `macro_cadence_gate.py`

---

## 19. Cadence Enforcement

### Per-Role Cadence

Cadence is enforced between role transitions, not per atom in isolation.

Examples:
- recognition → embodiment: must enter the body immediately — no cognitive bridge
- embodiment → pattern: must shift from single sensation to recurring loop
- pattern → mechanism_proof: must shift from naming the loop to explaining why
- mechanism_proof → agency_glimmer: must shift from explanation to open choice
- Final role (agency_glimmer) must end in open choice, not comfort

Cadence failures are treated as lint failures.

### Per-Family Thresholds

Defined in `docs/CADENCE_THRESHOLDS_BY_FAMILY.yaml`:

```yaml
generic_v4_slots:
  min: 0.60

bestseller_v2:
  min: 0.65

bestseller_v2_1:
  min: 0.70

grief_pack:
  min: 0.75

trauma_recovery:
  min: 0.80
```

A family fails if any gate fails. Auto-promotion requires cadence ≥ family min + buffer.

---

## 20. Canonical Multi-Brand v1.2 (Publishing Scale)

### Purpose

Scale from individual books to 1,008+ BookPlans via brand archetypes while keeping the assembler and engine unchanged.

### Architecture

- **Brand Archetype Registry:** `config/publishing/brand_archetype_registry_v1_2.yaml`
- 24 archetypes → 1,008 BookPlans
- Validators and generator extend the **planning/input** layer only — assembler unchanged
- **Launch Waves:** `config/publishing/launch_waves_v1_2.yaml`

### Operations

- **Kill/double-down:** Underperforming archetypes can be killed; high performers doubled
- **90-day freeze:** After launch, no archetype changes for 90 days
- **Plan hash:** Each plan is hash-locked so it's reproducible

### Tooling

```bash
# Validate the registry
make validate-brand-archetype-registry

# Generate all 1008 plans
python3 phoenix_v4/tools/generate_canonical_1008_plans.py

# Run a single canonical plan
python3 phoenix_v4/tools/run_canonical_plan.py --plan <plan_id>
```

---

## 21. Author Authority Registry

### Purpose

Governs who is allowed to author what. Prevents credibility drift.

### Rules

- Authors never generate runtime prose
- They only author sealed, approved assets
- First-person material must stay believable
- No borrowing credibility across personas

### Location

```
docs/authoring/
  author_authority_registry.md
```

### What It Defines

- Canonical author identities
- Author voice constraints
- Topic eligibility per author
- Persona alignment (which author can write for which persona)
- Credibility boundaries (what an author may/may not speak on)

---

## 22. CI Gates (Complete)

### Mandatory CI Gates

CI must fail if:

| Gate | Fails When |
|---|---|
| **No human seeds reference** | Runtime code references `human_seeds/` |
| **No candidate reference** | Runtime code references `candidate/` or `packs/` |
| **Approved atom status** | Any atom in approved path lacks `approval.status: approved` |
| **Approved exercise status** | Any exercise in approved path lacks approval |
| **No-auto-promotion family** | Any no-auto-promote family is auto-promoted |
| **Lint gate** | Any approved atom fails lint |
| **Cadence gate** | Any approved atom fails cadence (per family threshold) |
| **Coverage gate** | Required (persona, topic, role) combos below threshold |
| **Prose QA gate** | Assembled book fails any of the 6 prose QA gates |
| **Brand archetype registry** | Registry validation fails |
| **Cost–identity coupling** | High cost chapter has no identity movement (see §18 Gate 2) |
| **Engine diversity** | Book uses fewer than `min_distinct_engines` (see §6) |
| **Scene–cadence coupling** | Scene intensity exceeds chapter emotional_intensity (see §14) |
| **Exercise–identity coupling** | Blocked exercise–identity mismatch (e.g., activation in destabilization chapter; see §15) |
| **Semantic uniqueness** | Atom variants exceed `hard_reject` similarity threshold (see §9) |
| **Scene metadata completeness** | Any scene in `approved_scenes/` missing required YAML fields (see §14.3) |
| **Scene callback integrity** | Orphan callbacks — setup without return or return without setup (see §14.8) |
| **Scene prose unmodified** | Integrator changed writer prose (hash check against original submission) |
| **Role purity** | Atom contains lexemes forbidden for its role (e.g., body words in `recognition`, cognitive framing in `embodiment`) — see §5 |
| **Person compliance** | Atom uses first person ("I", "my", "me") — atoms must be second or third person per §8 |

### Makefile Targets

```makefile
.PHONY: lint test ci v4_qa_clean v4_qa_1000 v4_qa_summary \
        v4_story_fill v4_story_fill_qwen v4_legacy_repair \
        v4_story_coverage validate-brand-archetype-registry

lint:
	PYTHONPATH=. python3 phoenix_v4/ci/check_no_human_seeds_reference.py
	PYTHONPATH=. python3 phoenix_v4/ci/check_approved_atoms_status.py
	PYTHONPATH=. python3 phoenix_v4/ci/check_approved_exercises_status.py

v4_story_coverage:
	PYTHONPATH=. python3 phoenix_v4/ci/story_atoms_coverage_report.py \
	    --out artifacts/story_atoms_coverage.json

v4_story_fill:
	PYTHONPATH=. python3 tools/golden_phoenix/run_golden_phoenix_v4_coverage.py \
	    --slots-per-role 5

v4_story_fill_qwen:
	PYTHONPATH=. python3 tools/golden_phoenix/run_golden_phoenix_v4_coverage.py \
	    --writer qwen --slots-per-role 5 --base-url http://127.0.0.1:1234/v1

v4_legacy_repair:
	PYTHONPATH=. python3 tools/golden_phoenix/repair_legacy_story_atoms.py

v4_qa_clean:
	rm -f artifacts/v4_prose_qa_results.jsonl

v4_qa_1000:
	PYTHONPATH=. python3 phoenix_v4/tools/run_v4_prose_qa_campaign.py \
	    --format-type standard_book --count 1000 --seeds 84 \
	    --allow-coverage-gaps --out-jsonl artifacts/v4_prose_qa_results.jsonl

v4_qa_summary:
	PYTHONPATH=. python3 phoenix_v4/tools/build_v4_prose_qa_summary.py

validate-brand-archetype-registry:
	PYTHONPATH=. python3 phoenix_v4/tools/validate_brand_archetype_registry.py

test:
	PYTHONPATH=. pytest -v

ci: lint test v4_story_coverage validate-brand-archetype-registry
```

### GitHub Actions CI

```yaml
name: Phoenix Omega V4 CI

on:
  push:
  pull_request:

jobs:
  phoenix-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Lint & Governance
        run: make lint
      - name: Tests
        run: make test
      - name: Coverage Check
        run: make v4_story_coverage
      - name: Brand Registry Validation
        run: make validate-brand-archetype-registry
```

---

## 23. What "Quality" Means in V4

Quality is preserved by:

- Emotional ordering (role progression)
- Role purity (each atom does one thing)
- Structural discipline (plans are contracts)
- Ethical guardrails (no resolution, no reassurance)
- Cultural truth (via Story Bank overlays, not hardcoded)
- Narrative intelligence (Omega gates: escalation, cost, callbacks, identity, cadence)
- Stakes and cost (every book has real consequences)
- Scene injection (lived experience, not bullet points)

Quality is **not** measured by prose similarity. Low lexical similarity to human seeds is intentional.

### Definition of "As Good or Better"

A V4 book is "as good or better" when it:
- Has real people with real stakes
- Escalates in mechanism depth
- Includes setback and recovery
- Never resolves pain cleanly
- Ends with agency, not reassurance
- Feels like a journey someone walked with the reader

---

## 24. Rebuild Order (Recommended)

### Week 1 — Foundation
- Set up repo structure (§4)
- Enforce world separation (human/system/runtime)
- Add CI guards (§22)
- Define registries: personas, topics, stakes

### Week 2 — Content Pipeline
- Seed mining tools (§8)
- Atom lint + cadence enforcement (§5, §19)
- Approval tooling (§12)
- Golden Phoenix coverage filler (§9)
- Coverage checking (§10)

### Week 3 — Runtime + Scene Integration
- Topic engine bindings (§6)
- Plan compilation (§16)
- Assembly engine (§17)
- Exercise resolver + slotting (§15)
- Scene injection + YAML wrapper tooling (§14)
- Scene integration SOP deployed to content team (§14.4)
- Location hydration (§13)

### Week 4 — Validation & Scale
- Prose QA 6-gate stack (§18)
- Omega narrative intelligence gates (§18)
- 1000-book campaign validation
- Multi-brand plan generation (§20)
- End-to-end test book

### Dev Ownership Domains

| Domain | Owner | Sections |
|---|---|---|
| Seed Mining + Lint | Dev A | §7, §8, §9 |
| Approval + Governance | Dev B | §12, §21 |
| Runtime Assembly + Planning | Dev C | §6, §15, §16, §17 |
| Scene Integration + Content Ops | Dev C + Content Lead | §14 |
| Validation + CI | Dev D | §10, §18, §19, §22 |
| Publishing + Scale | Dev E | §20 |

No one owns "the whole system" except the system architect.

---

## 25. What Phoenix V4 Will NEVER Do (Safety Doctrine)

### ❌ Generate long-form story prose
All lived experience is authored by humans.

### ❌ Resolve pain for the reader
Pain is respected, not erased. No "you are healed." No "this fixes it."

### ❌ Give medical, diagnostic, or prescriptive advice
Exercises regulate experience, not outcomes. No diagnoses, no treatment plans.

### ❌ Change approved content at runtime
No paraphrasing, rewriting, tone optimization, or safety "patches" after approval.

### ❌ Invent authority or voice
No fake experts. No first-person claims unless authored and approved.

### ❌ Collapse narrative into bullet points
No checklist therapy. No motivational fragments. Books must feel lived, not instructional.

### ❌ Generate exercises dynamically
Exercises are authored, selected by function, always structured (intro → practice → ah-ha → integration).

### ❌ Ignore stakes, setbacks, or regression
Stories must include cost. Relapse is allowed. Progress is nonlinear.

---

## 26. Final Principles

> **Humans define meaning.**
> **Machines enforce structure.**
> **Runtime assembles, never decides.**
> **Narrative escalates, never flattens.**
> **Layers couple, never drift.**
> **If the system ever starts "writing," it is broken.**
> **If it ever resolves pain too cleanly, it is broken.**
> **If it ever sounds clever, it is broken.**
> **If cost rises but identity doesn't move, it is broken.**
> **If exercises ignore where the reader is, it is broken.**

This separation — and these couplings — are the reason Phoenix Omega V4 scales safely.

---

## 27. Dev Acceptance Criteria

V4 is "done" only when **all** are true:

- [ ] One human seed → 5–7 atoms (one per role), deterministically
- [ ] All atoms fail lint if reassurance is added
- [ ] No runtime file can import `human_seeds/`
- [ ] Approved atoms require human metadata
- [ ] Grief family cannot auto-promote
- [ ] CI fails on any governance breach
- [ ] Runtime assembles unresolved content only
- [ ] Scenes carry narrative weight with callbacks
- [ ] Exercises follow 4-section structure
- [ ] Coverage report shows READY for all campaign persona × topic combos
- [ ] 1000-book QA campaign passes all 6 prose gates
- [ ] Mechanism depth escalates through chapters
- [ ] Cost intensity rises through midpoint
- [ ] Identity stage progresses monotonically
- [ ] No 3 consecutive high-intensity chapters without relief
- [ ] Multi-brand registry generates 1008 valid plans
- [ ] High-cost chapters (≥4) drive identity movement in same or next chapter
- [ ] Each book uses ≥2 distinct engines (where topic allows)
- [ ] No scene intensity exceeds its chapter's emotional_intensity
- [ ] Exercise cadence_role matches chapter identity_stage (no blocked combos)
- [ ] Atom semantic uniqueness check passes (no variant pair > 0.92 similarity)
- [ ] All scenes have YAML wrappers with v4_role, identity_stage, cost, and callback metadata
- [ ] Scene integration SOP followed — writer prose unmodified by integrator
- [ ] At least 2 atoms mined per scene and role-typed
- [ ] No orphan callbacks (every setup has a return)
- [ ] Epigraph mechanism lines extracted from scenes, not confused with atom roles
- [ ] All atoms pass role purity gate (no body lexemes in recognition, no cognitive framing in embodiment)
- [ ] All atoms pass person compliance gate (no first-person pronouns)
- [ ] Persona registry has full psychographic profile + language block for every active persona
- [ ] Topic registry has per_persona_framing for every active persona × topic
- [ ] Location overlays exist for every active location with transit, neighborhoods, sensory, seasonal
- [ ] Cultural overlays exist for every persona × location combination in tier 1 mining priority
- [ ] Mining priority matrix generated and tier 1 combos at READY coverage

If a dev says "it mostly works" — **it is not done.**

---

## 28. Version Control

Once V4 passes all acceptance criteria:

1. Tag the repo: `omega-v4.0.0`
2. Freeze this document
3. All future work happens as: `docs/PROPOSALS/V4_1_<idea>.md`
4. No silent evolution. Ever.

---

**END OF SPECIFICATION**
