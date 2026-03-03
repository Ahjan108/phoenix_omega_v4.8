# Phoenix Teacher Mode V4 Spec

## Knowledge-Base Sourced, Gap-Filled, Arc-First Compatible (v1.0)

**Status:** Canonical (dev implementation authority for Teacher Mode)  
**Subordinate to:** [PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](./PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) — Arc-First remains sole system architecture.  
**Contracts:** [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md) for BookSpec/FormatPlan/CompiledBook.  
**Audience:** Senior devs, content governance

---

## 0. Purpose

Enable **Teacher Mode V4 books** where:

- A **real teacher's teachings** (files in `teacher_banks/[teacher_id]/`) are the *source of truth*.
- The **author voice** frames and applies the teacher's teachings to the book **topic + persona**.
- Books are compiled via the **regular V4 pipeline** (Stage 1/2/3), but the **content atoms are teacher-scoped**.
- Large gaps will exist; the system must **fill missing STORY/EXERCISE coverage** by generating **new candidate atoms** derived from teacher materials, then promoting through governance.

Teacher Mode must **not**:

- Insert raw teacher text directly into runtime content
- "Summarize the teacher" at runtime
- Create new meaning without governance
- Add prose scoring, tone heuristics, or entropy metrics

---

## 1. Definitions

### 1.1 Teacher Mode Book

A V4 book with:

- `teacher_mode: true`
- `teacher_id: <teacher_name>`
- Teacher-scoped atom pools as primary sources for STORY + EXERCISE (and optionally other roles)

### 1.2 Teacher Knowledge Base (KB)

An offline index over teacher files enabling:

- retrieval of supporting passages
- source anchoring for generated atoms
- auditability (provenance)

Runtime does **not** query KB.

---

## 2. Architecture Overview

### 2.1 Existing pipeline (unchanged)

- Stage 1: catalog planner produces `BookSpec`
- Stage 2: selects `FormatPlan`
- Stage 3: compiles `CompiledBook` via slot resolver
- Arc-First compiler requires `--arc` (no arc = no compile)

### 2.2 Teacher Mode inserts an offline "gap-fill" layer

**New flow:**

1. **Plan** (BookSpec exists; teacher selected)
2. **Preflight**: compute required coverage from `arc` + `format` (+ band requirements)
3. **Check teacher atom pool coverage**
4. If gaps: run **Teacher Gap-Fill Pipeline** (offline)
5. Promote to **teacher approved atoms**
6. Re-run compile (now coverage should exist)

Key rule:

> The compiler does not "create" content.  
> It fails on gaps unless an offline gap-fill step has already generated + approved atoms.

---

## 3. Repo Topology Additions

Add teacher content under SOURCE_OF_TRUTH:

```text
SOURCE_OF_TRUTH/
  teacher_banks/
    <teacher_id>/
      raw/                      # teacher files (pdf, md, txt, docx, transcripts)
      kb/                       # built indexes (vector + metadata)
      doctrine/                 # teacher doctrine constraints + glossary
      candidate_atoms/          # generated but not runtime-visible
      approved_atoms/           # runtime-visible teacher atoms
        HOOK/
        SCENE/
        STORY/
        EXERCISE/
        INTEGRATION/
      artifacts/
        mining_runs/
        gap_reports/
        approval_logs/
```

Notes:

- This mirrors the existing governance model (human seeds → candidate → approved), but scoped per teacher.
- `raw/` is never read by runtime.

---

## 4. Teacher Mode Configuration

### 4.1 Teacher registry

Add:

`config/teachers/teacher_registry.yaml`

Example:

```yaml
teachers:
  ajahn_x:
    display_name: "Ajahn X"
    kb_id: "ajahn_x"
    doctrine_profile: "theravada_minimalist"
    allowed_topics: [anxiety, shame, self_worth]
    disallowed_topics: [manifestation, get_rich_quick]
    allowed_engines: [shame, anxiety]
    allowed_resolution_types: [open_loop, internal_shift_only]
    identity_shift_allowed: false
    preferred_formats: [F006, standard_book]
    teacher_mode_defaults:
      require_teacher_story: true
      require_teacher_exercise: true
      allow_generic_fallback_for_scene: true
```

### 4.2 Teacher doctrine constraints

Stored per teacher:

`SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/doctrine.yaml`

Contains:

- forbidden claims
- tone boundaries
- glossary / canonical phrases
- prohibited outcomes
- exercise safety notes (especially for trauma-related material)

This doctrine is used in **offline linting only** (not runtime).

---

## 5. BookSpec Extensions

Extend Stage 1 output schema (see [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md)):

```yaml
teacher_mode: boolean
teacher_id: string | null
teacher_kb_id: string | null
teacher_doctrine_profile: string | null
```

Rules:

- If `teacher_mode=true`, `teacher_id` is required.
- `teacher_kb_id` resolves from teacher_registry.

Planner behavior:

- catalog_planner does not "decide teacher" today; caller/allocator must supply.
- Add a new optional planner wrapper: `teacher_allocator.py` (§8).

---

## 6. Teacher Atom Schema Additions

Teacher atoms must include provenance metadata (offline + audit); runtime ignores it.

Add optional fields to atom YAML:

```yaml
teacher:
  teacher_id: ajahn_x
  source_refs:
    - doc_id: "raw/teachings_2019_retreat_01.txt"
      span: [1250, 1680]       # byte offsets or line range
      quote_hash: "sha256:..."
  synthesis_method: "kb_gap_fill_v1"
  doctrine_checks:
    - "no_false_reassurance"
    - "no_identity_shift"
```

Rules:

- `teacher.teacher_id` required for atoms in teacher_banks approved pools.
- `source_refs` required for any atom produced by gap-fill generator (not required for manually authored atoms).

---

## 7. Compile Semantics (Stage 3) for Teacher Mode

### 7.1 Pool selection precedence

When `teacher_mode=true`, slot resolver uses:

1. `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms/…`
2. Optional fallback pool (only if explicitly enabled by teacher_mode_defaults or per-run flag):
   - base approved atoms (persona/topic)
   - never fallback for STORY/EXERCISE if `require_teacher_story` / `require_teacher_exercise` = true

### 7.2 Band filtering remains primary for STORY

Arc-first band requirement remains unchanged:

- `required_band_by_chapter` filters STORY pool before selection.

### 7.3 Failure mode (default)

If any required slot lacks atoms after applying all allowed pools:

- compile fails with a **Gap Report** (§9).

No runtime generation.

---

## 8. Teacher Allocation Layer (Planning)

Add new module:

`phoenix_v4/planning/teacher_allocator.py`

**Purpose:**

- assign `teacher_id` for teacher_mode books
- ensure compatibility before compile

**Inputs:**

- domain_id, topic_id, persona_id, engine_id, format_id, arc_id (or arc file)
- desired brand_id (optional)

**Checks:**

- teacher allowed_topics / allowed_engines / allowed_resolution_types
- format compatibility
- doctrine profile exists
- KB exists (or can be built)
- minimum coverage (optional pre-check)

**Output:**

- teacher_id

**Deterministic selection:**

- based on seed + stable ordering.

---

## 9. Gap Reporting (New)

Add:

`phoenix_v4/qa/report_teacher_gaps.py`

**Given:**

- BookSpec + arc + format plan + teacher_id

**Compute:**

- required counts by role
- required STORY bands by chapter
- required EXERCISE count by chapter/slots (format-defined)

**Output JSON:**

```json
{
  "teacher_id": "ajahn_x",
  "topic": "self_worth",
  "persona": "nyc_executives",
  "format_id": "F006",
  "arc_id": "nyc_executives__self_worth__shame__F006",
  "gaps": {
    "STORY": {
      "band_3": 4,
      "band_4": 2
    },
    "EXERCISE": {
      "total_missing": 3,
      "by_type": {"somatic": 2, "reflection": 1}
    }
  }
}
```

This is the contract input to the gap-fill generator.

---

## 10. Teacher Gap-Fill Pipeline (Offline, Controlled)

### 10.1 Overview

Add tool:

`tools/teacher_mining/gap_fill.py`

**Goal:** fill missing STORY and EXERCISE coverage by generating **candidate atoms** grounded in teacher KB.

### 10.2 Pipeline steps

1. **Ensure KB exists** — build if missing: `tools/teacher_mining/build_kb.py`
2. **Load Gap Report**
3. For each missing item (e.g. STORY band 3):
   - Retrieve top-k supporting passages from KB using queries derived from: topic, engine, persona pressure themes (if available), band intent ("escalation", "cost-adjacent", etc.)
4. Generate **candidate atom** with:
   - required role purity
   - required band
   - no reassurance
   - teacher doctrine constraints
   - provenance `source_refs`
5. Run: lint (existing), cadence (existing), similarity checks vs existing teacher approved atoms, doctrine checks (new, structural + keyword boundary checks)
6. Write candidate atoms to: `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/candidate_atoms/...`
7. Produce a **Gap-Fill Run Report** in artifacts.

### 10.3 Output constraints

- **Deterministic generation:** seed derived from (teacher_id, topic, persona, role, band, index)
- **Hard cap:** max 2 repair attempts (same rule as seed mining)
- **Never auto-promote** in sensitive families (teacher doctrine may add more)

---

## 11. Approval & Promotion (Teacher Scoped)

Reuse approval tool pattern with a teacher scope:

`tools/approval/approve_atoms.py --teacher ajahn_x ...`

- Moves: teacher candidate → teacher approved
- Adds approval metadata
- No rewriting

---

## 12. Exercise Handling (Teacher Mode)

Teacher files may contain: explicit exercises, implicit practices embedded in talks, repeated motifs.

Gap-fill generator must produce EXERCISE atoms that:

- are safe
- align with doctrine
- fit format slot constraints
- include provenance refs

Add exercise categories (if not already): breath, somatic scan, journaling prompt, behavioral experiment, reflection practice.

**No medical claims. No guaranteed outcomes.**

---

## 13. CI / QA Gates (Teacher Mode)

### 13.1 Must-pass gates

- Teacher-mode compiled books must not include non-teacher STORY/EXERCISE if `require_teacher_*` = true
- All teacher approved atoms must include `teacher.teacher_id`
- Any gap-fill-generated atom must include `source_refs`

### 13.2 Must-not gates

- Runtime must never read `teacher_banks/<teacher>/raw` or `kb`
- No prose scoring validators added
- No dynamic range / entropy / volatility logic added (still banned)

---

## 14. Operational CLI

### 14.1 Build teacher KB

```bash
python3 tools/teacher_mining/build_kb.py --teacher ajahn_x
```

### 14.2 Report gaps for a planned book

```bash
python3 phoenix_v4/qa/report_teacher_gaps.py \
  --plan artifacts/plan.json \
  --arc config/source_of_truth/master_arcs/...yaml \
  --teacher ajahn_x \
  --out artifacts/gaps.json
```

### 14.3 Fill gaps

```bash
python3 tools/teacher_mining/gap_fill.py \
  --teacher ajahn_x \
  --gaps artifacts/gaps.json \
  --out SOURCE_OF_TRUTH/teacher_banks/ajahn_x/candidate_atoms
```

### 14.4 Approve

```bash
python3 tools/approval/approve_atoms.py --teacher ajahn_x list
python3 tools/approval/approve_atoms.py --teacher ajahn_x approve <atom_id>
```

### 14.5 Compile (unchanged; teacher passed in BookSpec)

```bash
python3 scripts/run_pipeline.py \
  --topic self_worth --persona nyc_executives --structural-format F006 \
  --arc config/source_of_truth/master_arcs/...yaml \
  --teacher ajahn_x --teacher-mode \
  --out artifacts/teacher_mode.plan.json
```

---

## 15. Default Policy: Where "Intelligence" Lives

To avoid corrupting Phoenix's architecture:

**Intelligence lives here:**

- Offline mining + gap-fill tools
- Candidate generation + repair loop
- Human approval
- Coverage reporting

**Intelligence must never live here:**

- Runtime assembly
- Slot resolver
- Validators (beyond structural checks)

---

## 16. Minimal Implementation Plan

### Phase 1 (MVP)

- teacher_banks directory structure
- teacher registry + doctrine profile loader
- teacher_mode BookSpec flags
- teacher pool selection precedence in slot_resolver
- gap report tool
- KB builder (simple)
- gap_fill generator producing candidate STORY + EXERCISE atoms with provenance
- approval tool teacher-scoped

### Phase 2 (Hardening)

- doctrine checks library
- teacher-specific no-auto-promotion list
- coverage dashboard by teacher/topic/persona/band
- seed-determinism tests

### Phase 3 (Scale)

- teacher allocation planning across waves
- multi-teacher brand strategies
- long-term drift prevention (source quote hashing)

---

## 17. Related Specs

- **[TEACHER_MODE_STRUCTURAL_SPEC.md](./TEACHER_MODE_STRUCTURAL_SPEC.md)** — Pre-Intro template, author voice rules, Teacher Presence Score (TPS).
- **[TEACHER_INTEGRITY_SPEC.md](./TEACHER_INTEGRITY_SPEC.md)** — Cross-series guardrails: doctrine, vocabulary, exercise identity, TPS distribution.
- **[TEACHER_PORTFOLIO_PLANNING_SPEC.md](./TEACHER_PORTFOLIO_PLANNING_SPEC.md)** — Brand × teacher matrix, release velocity, anti-spam (platform safety).

---

## 18. Non-Goals

Teacher Mode does **not**:

- auto-publish without human approval
- inject raw quotes verbatim into runtime
- invent new teacher doctrine
- validate "correctness" via prose scoring
- replace arc-first architecture

---

## 19. Still to do (whole system)

Normalization, structural entropy CI, platform similarity gate, and teacher_persona_matrix validation are implemented. Remaining for Teacher Mode and the whole system:

- Complete gap-fill automation and approval workflows per this spec (Phase 2/3).
- Any system-wide items (coverage enforcement, Gate #49, optional freebie/narrator) are in the canonical systems doc and planning status.

- **Canonical systems doc:** [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md) — § Remaining to finish whole system.
- **Planning status:** [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md).
