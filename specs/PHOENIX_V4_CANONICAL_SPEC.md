# Phoenix Omega V4 — Canonical Spec

**Reference canonical for taxonomy and contracts.** For system architecture authority, use `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` (as indexed in `specs/README.md` and `docs/SYSTEMS_V4.md`).

**Version:** 2.0 (consolidated)  
**Date:** February 2026

---

## Part 0 — Authority & How to Use This Spec

- **Authority boundary:** This document remains authoritative for the sections it defines (taxonomy, contracts, governance reference), while Arc-First Canonical is the governing architecture authority.
- **Content model** = Part 1 (6 section types, atom schema). **Structure** = Part 2 (tiers, formats, beat maps). **Assembly** = Part 3 (plan compiler, K-tables). **Governance** = Part 4 (approval, CI). **Layout** = Part 5.
- **Source material** (canonical books, `content/` master scripts, existing atom pools) is content to mine and validate against — not a separate spec layer.
- **Any change to:** atom schema, story roles, emotional_intensity_band behavior, or Stage 3 MUST/MUST NOT rules **requires a spec version bump and migration note.**

---

## Part 1 — Content Model

### 1.1 The Six Section Types

Every therapeutic content unit is one of six types. The old 3-type taxonomy (story, exercise, scene) is **replaced** by this.

| Type | Purpose | Author voice vs character |
|------|---------|---------------------------|
| **HOOK** | Chapter opening; names pattern or state | Author voice |
| **SCENE** | Sensory/contextual moment (entry, transition, or closing *scene*) | Sensory only |
| **STORY** | Character-driven vignette; one of 5 roles | Character |
| **REFLECTION** | Teaching prose (mechanism, reframe, pattern naming, core thesis) | Author voice |
| **EXERCISE** | Guided practice | Second person, instructional |
| **INTEGRATION** | Closing synthesis; no resolution promise | Author voice |

- **STORY** keeps five **roles**: recognition, embodiment, pattern, mechanism_proof, agency_glimmer. Teaching prose that explains “why” is **REFLECTION**, not story. Chapter openings that name a pattern/state are **HOOK**, not story. Final synthesis is **INTEGRATION**, not scene.
- **atom_size**: `full` | `micro`. Tier A uses full atoms; Tier B/C use micro where required (see Part 2).

### 1.2 Atom Schema (V4)

**Universal fields (all atoms):**

```yaml
atom_id: "<type_prefix>_<persona_topic_slug>_<seq>"
atom_category: hook | scene | story | reflection | exercise | integration
atom_size: full | micro
version: 1
deprecated: false
persona: <persona_id>
topic: <topic_id>
teacher_id: "<teacher_id>"
body: |
  <prose or guided instruction>
word_count: <integer>
approval:
  status: approved | provisional
  approved_by: <human>
  approved_at: <UTC ISO 8601>
  promotion_reason: manual | auto_confident
provenance:
  source_seed: "<id>"
  teacher_doctrine: "<id>"
  mined_at: <UTC ISO 8601>
```

**Type-specific fields:**

| Type | Extra fields | Full words | Micro words |
|------|--------------|------------|-------------|
| HOOK | hook_type or variant_family (F1–F5) | 150–350 | 40–100 |
| SCENE | scene_type: entry \| transition \| closing | 150–300 | 40–80 |
| STORY | role, arc_type, stake_domain, **emotional_intensity_band** (1–5) | 60–150 | 30–80 |
| REFLECTION | reflection_type: mechanism_explanation \| reframe \| pattern_naming \| core_thesis | 200–500 | 60–150 |
| EXERCISE | exercise_type, exercise_tier (1\|2\|3), cadence_role | 100–300 | 60–120 |
| INTEGRATION | — | 100–200 | 30–60 |

**STORY-only: emotional_intensity_band** — Integer 1–5. Required for every STORY atom. Lint must reject STORY atoms missing this field. Used by the plan compiler for emotional curve diversity (see Part 3). Band meanings:

| Band | Emotional energy |
|------|------------------|
| 1 | mild discomfort |
| 2 | tension |
| 3 | strain |
| 4 | breaking point |
| 5 | crisis / rupture |

**Rules for all atoms:** Open ending; no resolution lexemes; no medical advice; no location proper nouns in body. Forbidden resolution list applies to every category.

---

## Part 2 — Structure: Tiers, Formats, Beat Maps

### 2.1 Three Tiers

| Tier | Chapter size | Beat map system | Section types |
|------|--------------|-----------------|---------------|
| **A** | 800–2,000+ words | 12 full beat maps; compiler selects per chapter | All 6 (full) |
| **B** | 150–500 words | 8 micro beat maps (3–5 slots) | All 6 (micro variants) |
| **C** | Under 200 words | Fixed slot sequence per format | Subset 3–4 types |

### 2.2 Fifteen Formats (F001–F015)

**Tier A (full beat maps):** Standard Book, F004 Somatic Body Journey, F006 Nervous System Ladder, F007 Shadow Work, F009 Parts Work (IFS), F010 Energy Management, F011 Relationship Repair, F014 Archetype Transformation.

**Tier B (micro beat maps):** F001 90-Day Transformation, F002 Daily (30/365), F003 7-Day Challenge, F008 Micro-Habits, F013 (phase-appropriate micro).

**Tier C (fixed sequences):** F005 Rescue Kit, F012, F015.

Each format has a **format policy** (chapter bounds, word targets, slot semantics) and a **K-table** (minimum pool depth per slot type). Structural fingerprint includes **format_id** so two books with the same beat map sequence but different formats do not collide.

**V4.5 formats (14):** deep_book_6h/5h/4h, extended_book_3h/2h, standard_book, short_book_45/30, micro_book_20/15, capsule_10/5, reset_2/90s. Config: `simulation/config/v4_5_formats.yaml`. These are **runtime format** (duration/chapter count); orthogonal to **structural format** (F001–F015 beat map family). Structural fingerprint uses both where applicable.

**Emotional temperature curves:** Per-format sequences (cool → warm → hot → land) and volatility/landing requirements. Config: `simulation/config/emotional_temperature_curves.yaml`.

**Format policy pattern (example):** Each format has a policy (e.g. in phoenix_v4/policy/format_policies/). One full pattern:

- **format_id** (e.g. F005)
- **structure:** chapter_count range, slot_definitions (category, role, description per slot)
- **k_table_requirements:** minimum atoms per slot type (story_recognition, exercise_daily_practice, scene_*, etc.)
- **duplication_thresholds:** sentence_hash, paragraph_hash, practice_similarity (format-specific)
- **blueprint_variants:** linear, wave, scaffold (and optionally rupture for advanced); rotation is a planning concept

K-table and slot semantics are authoritative here; SYSTEMS_DOCUMENTATION may reference but not redefine.

### 2.3 Beat Maps

- **Tier A:** 12 full beat maps; each defines a sequence of slots (HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION) with 7–10 slots per chapter. Plan compiler selects beat map per chapter based on persona × topic profile.
- **Tier B:** 8 micro beat maps; 3–5 slots per chapter; micro atom word counts.
- **Tier C:** Fixed slot sequence per format; no beat map variance.

**Variant families (F1–F5):** Used for HOOK and author-voice selection/affinity per format or brand. Atoms may carry `variant_family: F1` (etc.) in metadata.

### 2.4 Slot Remap (Legacy → V4)

Old slot labels that were “story” or “scene” are remapped so that:

- Mechanism explanation / “why it works” → **REFLECTION** (not story).
- Chapter opening that names state/archetype → **HOOK** (not story).
- Closing synthesis / gratitude / wrap-up → **INTEGRATION** (not scene/closing).

Character-driven stories and sensory scenes stay **STORY** and **SCENE** respectively.

### 2.5 K-table capacity / velocity (summary)

Rough production load by format class; used for capacity planning and Stage 1 feasibility. Exact thresholds live in per-format K-tables.

| Format class | Story (approx) | Exercise (approx) | Scene (approx) | Velocity tier |
|--------------|----------------|-------------------|----------------|---------------|
| F003 / standard_book 12ch | 24+ | 12+ | 12+ | Medium |
| F006 deep 8-12ch | 16-24 | 8-12 | 8-12 | High |
| F005 micro 3-6ch | 6-12 | 3-6 | 3-6 | Low |
| F001 90-day | 90+ | 90+ | 90+ | Very high |

Production strategy: prioritize F003-F006 for scale; Golden Phoenix for provisional atoms; human approval as rate limiter. SYSTEMS_DOCUMENTATION may define velocity modeling; K-table thresholds and slot semantics remain in Canonical.

---

## Part 3 — Assembly

### 3.0 Stage 3 Assembly Compiler Contract (Frozen)

The Stage 3 assembly compiler deterministically produces a **CompiledBook** from a canonical **BookSpec** and **FormatPlan**. No inference, no aliasing, no planning inside the compiler.

**Identity alias rule:** Persona and topic aliases (e.g. nyc_exec, relationship_anxiety) are resolved to canonical atoms dir names **before** Stage 3 only (e.g. via config/identity_aliases.yaml in the pipeline). Stage 3 receives only canonical topic_id and persona_id; it must not perform alias resolution.

**Slot authority rule:** slot_definitions are required on FormatPlan and supplied by Stage 2 (format policy). Stage 3 cannot default or infer slot types; it must use format_plan.slot_definitions exactly.

**Input contract**

| Source | Field | Type | Rule |
|--------|--------|------|------|
| book_spec | topic_id | string | **Canonical** only (atoms dir name). No alias resolution inside Stage 3. |
| book_spec | persona_id | string | **Canonical** only (atoms dir name). No alias resolution inside Stage 3. |
| book_spec | teacher_id, brand_id, series_id, installment_number, angle_id, domain_id, seed | as in OMEGA_LAYER_CONTRACTS | Pass-through; compiler does not modify. |
| format_plan | format_structural_id | string | F001–F015. |
| format_plan | format_runtime_id | string | V4.5 duration class. |
| format_plan | blueprint_variant | string | linear \| wave \| scaffold \| rupture. |
| format_plan | chapter_count | int | Target chapter count. |
| format_plan | **slot_definitions** | List[List[string]] | **Required.** Ordered slot types per chapter (e.g. [["HOOK","SCENE","STORY","REFLECTION","EXERCISE","INTEGRATION"], …]). Stage 3 MUST NOT infer or default slot types. |

**Absolute rules**

- Stage 3 MUST NOT infer persona mappings, topic mappings, or format slots. It MUST NOT override format_plan.slot_definitions.
- Stage 3 MUST load atoms from the canonical path only (see §5.3 Atom File Canonical Schema). It MUST respect slot_definitions exactly. It MUST use topic_engine_bindings.yaml for allowed_engines per topic. It MUST use seed for deterministic selection. It MUST produce a stable plan_hash.

**Output contract (CompiledBook)**

| Field | Type | Rule |
|-------|------|------|
| plan_hash | string | SHA256(book_spec_digest + format_plan_digest + sorted(atom_ids)). Deterministic. |
| chapter_slot_sequence | List[List[string]] | Exactly format_plan.slot_definitions repeated per chapter (or one row per chapter). |
| atom_ids | List[string] | One ID per slot, in order. Placeholder IDs allowed for non-STORY slots when pool absent. |
| dominant_band_sequence | List[int \| null] | Dominant emotional_intensity_band per chapter (STORY). If no STORY slots exist in a chapter, dominant band is null for that chapter. |

Stage 3 loads atoms from canonical paths in production; tests may override atoms_root for fixtures.

**Authority:** This contract is the only definition of Stage 3 input/output. Implementation must not add inference or aliasing.

---

### 3.1 Plan Compiler

**Inputs:** teacher, persona, topic, format_id, overlay (optional).

**Pipeline:**

1. **Capability check** — Load K-table for format_id. Query approved atoms for (teacher, persona, topic). Count per slot type. If any slot count < k_min → fail (strict) or reduce chapter count (relaxed).
2. **Achievable chapter count** — `achievable_chapters = min(chapter_count.max, min(pool_size per slot), floor(exercises / exercises_per_chapter_avg))`.
3. **Chapter planning** — For each chapter: select beat map (Tier A) or use format’s micro/fixed sequence (Tier B/C). For each slot, query eligible atoms (matching category/role/type, not used in this book, not deprecated). Select deterministically (quality-ranked + tiebreaker).
4. **Inter-chapter validation** — No atom reuse in book; transition/scene variety rules; exercise placement rules. **Emotional curve diversity (STORY atoms only):** Chapter dominant band = max(`emotional_intensity_band` among STORY atoms in that chapter). (A) At least 3 distinct `emotional_intensity_band` values across the book (no flatline). (B) No more than 3 consecutive chapters with the same dominant intensity band (no repeated plateau). If a plan violates (A) or (B), reject and reselect before finalization; no scoring, just exclusion rules.
5. **Plan output** — Deterministic plan (e.g. plan.yaml) to artifacts/plan_compiler/compiled_plans/; sealed with hash.

**Determinism:** Same inputs + same pool → same plan. Selection uses scoring (persona_fit, topic_fit, novelty, arc_coherence, duplication_penalty, overuse_penalty) then deterministic tiebreaker. No randomness.

### 3.2 K-Tables

- One **K-table per format** (not one global). Defines k_min (and optionally k_recommended) per atom type/slot for (teacher, persona, topic).
- Covers **full and micro** pools where the format uses both. format_id is part of the structural fingerprint for duplication.

### 3.3 Duplication & Cross-Format Sharing

- **No reuse within a book** — each atom used at most once per compiled plan.
- **Structural fingerprint** includes format_id; same beat map sequence in different formats does not count as duplicate.
- **Cross-format sharing:** Atoms may be shared across formats only when they pass lint for both (e.g. word count in range for both full and micro). Format-specific duplication thresholds apply.

### 3.4 Emotional Curve Observability (No New CI Gate)

Extend the entropy / diversity tracker to record **intensity_distribution_per_wave**: for each compiled book, the sequence of dominant band per chapter (e.g. 2→3→2→4→3→…), where chapter dominant band = max(`emotional_intensity_band` among STORY atoms in that chapter). Wave shape comparison uses exact ordered dominant band sequences. If >60% of books in a wave share the same dominant band shape (e.g. mostly 2→3→2), emit a **warning** only. Do not fail the build. Use the metric to guide future mining (e.g. add more high-band or low-band atoms where the catalog clusters). This prevents “emotional pacing sameness” at scale without adding CI gates or scoring complexity. **Implementation split:** Senior dev: compiler tracking of intensity bands, plateau exclusion logic (rules A and B), wave-level intensity histogram. Mid-level dev: atom schema and registry YAML updates, lint rule for emotional_intensity_band (see phoenix_v4/qa/emotional_governance_rules.yaml), mining prompts to include band.

---

## Part 4 — Governance

### 4.1 Candidate vs Approved

- **candidate_atoms/** — Lint-clean, not runtime-visible. Require human approval.
- **approved_atoms/** — Only source for plan compiler. CI enforces: runtime must not read from candidate; only approved atoms participate in compilation.

Approval tool: moves files and updates metadata only; does not rewrite content.

### 4.2 Pipelines (Offline)

- **Story:** human_seeds → segment → role_extract → rewrite_as_atom → lint → doctrine/safety/similarity → candidate → approval → approved.
- **Exercise:** teacher_doctrine / packs → segment → rewrite_as_exercise_atom → lint → candidate → approval → approved.
- **Scene:** seeds/doctrine → scene_extract → rewrite_as_scene_atom → lint → candidate → approval → approved.

All pipelines: offline, deterministic, fail-fast.

### 4.3 CI Gates (1–68)

**Gates 1–39 (infrastructure):** Plan compiler capability check; no atom reuse in plan; role ordering; exercise placement; scene bracketing; doctrine compliance; approved_atoms-only at runtime; coverage reports; build manifests; semantic uniqueness; cadence; forbidden resolution; location leakage; writer trust; etc. (Details in archived Systems Doc §23 / infrastructure sections if needed.)

**Gates 40–54 (beat maps & 6-type):** Beat map selection valid for format; slot types match 6-type taxonomy; variant_family valid; K-table slot types aligned with beat map; etc.

**Gates 55–68 (formats & micro):** Every micro atom has atom_size: micro and passes micro word count lint. Tier B plans reference only micro atoms; Tier A only full. Tier C fixed sequence per format. F001/F002/F003/F005/F006/F009/F013 format-specific rules (e.g. F001 progressive exercise tier; F002 standalone chapter; F005 crisis resource metadata). Cross-format sharing respects word count ranges. format_id in fingerprint. Clinical advisor approval flag where required (e.g. F004, F006, F009, F013).

**V4.5/V4.6 additional gates:** Volatility quotas by tier (volatility_scenes_min, visible_consequence_min, action_despite_pattern_min, silence_beats_min) — config: `simulation/config/validation_matrix.yaml`. Emotional QA (escalation, sensory, reaction, cognitive/body) — config: `phoenix_v4/qa/emotional_governance_rules.yaml`. Forward Momentum Trigger (FMT) for full books — final integration must satisfy one of: unresolved mechanism, identity tension, social cliff, curiosity hook. See `specs/V4_6_BINGE_OPTIMIZATION_LAYER.md`.

### 4.4 Forbidden Content (All Atoms)

- Forbidden resolution lexemes and phrases (e.g. “heal,” “gets better,” “you’ve got this”) — substring match, hard fail.
- Open ending: no future certainty, no reassurance, no outcome language.
- No medical advice. No location proper nouns in body.

---

## Part 5 — Directory Layout & Reference

### 5.1 Repo-Root: config/, registry/, atoms/

At repo root, the following hold **topic config**, **section registries**, and **canonical story atoms** (intake from content drops). Pipeline and plan compiler reference these.

| Path | Purpose |
|------|---------|
| **config/** | Topic-level gates and vocabulary. **topic_engine_bindings.yaml** — which engines/roles are allowed per topic (anxiety, boundaries, financial_stress, courage, compassion_fatigue, depression, self_worth, grief). **topic_skins.yaml** — prohibited terms, role suffixes (≤30 words), topic overrides. Hard gate: bindings restrict engine choice per topic; skins enforce vocabulary. |
| **registry/** | Section and pack registries. **registry_grief.yaml** — grief section pack (rewritten section variants for grief/loss). Pipeline may set `SECTIONS_REGISTRY_FILE` to a file here. Other section packs (e.g. anxiety, boundaries) may live under registry/ or SOURCE_OF_TRUTH. |
| **atoms/** | Canonical story atoms by persona, topic, engine. Path: **atoms/\<persona\>/\<topic\>/\<engine\>/CANONICAL.txt**. Personas include educators, nyc_executives, healthcare_rns, gen_alpha_students, gen_z_professionals. Used for assembly, coverage, and plan-compiler capability checks. New drops can be staged in **get_these/** then ingested into this layout (see get_these/README.md). **Path and role consistency:** This path is the single canonical story-atom layout. Role schema is **five roles** (recognition, embodiment, pattern, mechanism_proof, agency_glimmer). Where legacy or external systems use 4-role or other schemas, document the mapping in reconciliation/gap closure; this spec uses 5 roles only. |

**Staging:** **get_these/** is the staging folder for new YAML and canonical atom files. After ingestion, content is moved into config/, registry/, and atoms/; get_these/ is cleared (see REPO_FILES.md and get_these/README.md).

### 5.3 Atom File Canonical Schema (Frozen)

**Canonical path:** `atoms/<persona_id>/<topic_id>/<engine_id>/CANONICAL.txt`. No alternative paths. persona_id and topic_id are **canonical** (atoms directory names); alias resolution is done before Stage 3 only (see config/identity_aliases.yaml).

**Section types vs story roles:** The six **section types** (slots) are HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION. **INTEGRATION** is a slot type (closing synthesis, author voice), not a story role. INTEGRATION slots are filled by integration-type atoms or placeholders, not from CANONICAL.txt story atoms. Story roles apply only to **STORY** slots.

**CANONICAL.txt block format (story atoms).** Each atom block:

- Header line: `## ROLE vNN` where ROLE is one of the frozen story roles (see below), NN is a version or sequence number (e.g. 01, 02).
- Delimiter line: `---`
- Optional metadata line: `path: <path>` (legacy or provenance).
- Optional metadata: `ID: <atom_id>`, `BAND: <1-5>` (emotional_intensity_band for STORY). If absent, compiler may derive atom_id from path/persona/topic/engine/role/vNN and use default BAND 3 (see BAND default rule below).
- Delimiter: `---`
- Prose body (to end of block or next `##`).

**Frozen story roles (CANONICAL.txt):** RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT. These four are the current frozen set for CANONICAL.txt. Part 1 defines five story roles (recognition, embodiment, pattern, mechanism_proof, agency_glimmer); legacy or file-based atoms may use the four above, with pattern and agency_glimmer mappable externally or added to the file format later. Compiler accepts only the frozen set; mapping from other role names is external.

**Parser rules:** Compiler must fail fast on: duplicate atom ID within file; unknown role not in frozen set; malformed header (missing role or version). Missing BAND defaults to 3 for STORY slots.

**BAND default (CANONICAL.txt only):** When BAND is absent in a block, the compiler uses default 3. This is explicitly permitted for the CANONICAL.txt file format. It affects emotional band distribution (e.g. more mid-band); emotional curve diversity rules (Part 3 — at least 3 distinct bands per book, no 3-chapter plateau) still apply to the compiled plan, and wave-level observability (Part 3.4) may warn if shapes cluster. In the full atom schema (Part 1) and QA (emotional_governance_rules.yaml), emotional_intensity_band is required for story atoms; the default is a file-format exception until atoms are promoted to the full schema or BAND is added to files.

**Pool BAND distribution (recommended):** For 8–12 chapter books, a 20-atom pool per engine should span BAND 1–5 so that curve enforcement (≥3 distinct bands, no more than 3 consecutive chapters with same dominant band) is achievable across different seeds. Recommended distribution per 20-atom pool: BAND 1:1, 2:4, 3:7, 4:5, 5:3. See docs/BOOK_001_READINESS_CHECKLIST.md and artifacts/THREE_BOOK_STRESS_TEST.md.

**Long-term BAND default policy (Migration policy — pending decision)**  
The project will choose one of the following after migration; no code or schema change until then.

- **Option A (cleaner long-term):** Require BAND in every CANONICAL.txt block; remove the default after migration. Add a short "Migration" note in §5.3: once all blocks include BAND, the default may be removed; spec version bump required.
- **Option B (keep exception):** Keep the default and require metadata for observability: e.g. in compiler output or atom metadata, add `band_source: explicit | defaulted` (implementation later; document the decision and the future field in the spec).

**Atom ID:** If block has `ID: <id>`, use it. Otherwise compiler may derive from `persona_id_topic_id_engine_id_ROLE_vNN`. Stable derivation is required for determinism.

### 5.2 Canonical Paths (SOURCE_OF_TRUTH & phoenix_v4)

```
SOURCE_OF_TRUTH/
  teacher_doctrine/<teacher_id>/
  human_seeds/   (offline mining only)
  candidate_atoms/
    story | exercise | scene (or per 6-type: hook, scene, story, reflection, exercise, integration)
      <persona>/<topic>/<role_or_type>/
  approved_atoms/   # ONLY runtime input; same tree
  data/
    story_arc_registry.yaml
    story_bank/ (pressure_themes, location_variables, etc.)
  registry/
    personas.yaml
    teachers.yaml
    exercise_registry.yaml
    scene_registry.yaml
    ...
phoenix_v4/
  policy/
    format_policies/   # per format_id (F001–F015)
    k_tables/          # per format_id
    injection_scoring.yaml
    ...
  qa/
    emotional_governance_rules.yaml   # TTS rhythm, cognitive/body, reassurance, drift
  planning/
    compile_format_plan.py
    coverage_checker.py
    ...
artifacts/
  plan_compiler/
    compiled_plans/
    capability_reports/
    selection_traces/
  approval_logs/
  semantic_index/
  ...
```

(Exact tree may use 6-type subdirs under approved_atoms/candidate_atoms as needed; policy and K-tables are per format_id.)

### 5.3 Catalog Planning

Plan compiler inputs include **catalog context:** domain → series → angle (and teacher, persona, topic). Used for planning and variety; not for atom taxonomy.

The **domain → series → angle** hierarchy lives in **config/catalog_planning/**: domain_definitions.yaml, series_templates.yaml, capacity_constraints.yaml. Stage 1 (catalog planner) reads these; SYSTEMS_DOCUMENTATION describes strategy and references them. **Blueprint rotation** (linear, wave, scaffold, rupture) is a compiler/planning concept; variants rotate per format to avoid structural sameness. Format selection policy: **config/format_selection/** (format_registry.yaml, selection_rules.yaml). See [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md) for handoff schemas.

### 5.4 Brand × Section Type

Author-voice types (HOOK, REFLECTION, INTEGRATION) are governed by **brand voice profile** per format. Brand affinity mapping defines tone for each (e.g. zen_daily vs resilience_path vs depth_work). Exercise and STORY adapt via persona/cultural overlay.

---

## Summary

| Topic | Where in this spec |
|-------|--------------------|
| What is an atom? | Part 1 — 6 types, atom_size, schema |
| How are chapters built? | Part 2 — tiers, formats, beat maps |
| How does compilation work? | Part 3 — plan compiler, K-tables, duplication, emotional curve diversity (§3.1 step 4, §3.4) |
| How is quality enforced? | Part 4 — approval, pipelines, CI 1–68, forbidden content |
| Emotional curve diversity? | Part 1 — STORY emotional_intensity_band (1–5); Part 3 — compiler rules (no flatline, no plateau), observability only |
| Where do files live? | Part 5 — repo-root config/registry/atoms, directory layout, catalog, brand |

**Related specs:** [PHOENIX_V4_5_WRITER_SPEC.md](./PHOENIX_V4_5_WRITER_SPEC.md) (prose, TTS, emotional QA). [V4_6_BINGE_OPTIMIZATION_LAYER.md](./V4_6_BINGE_OPTIMIZATION_LAYER.md) (Forward Momentum Trigger for full books). [V4_5_PRODUCTION_READINESS_CHECKLIST.md](./V4_5_PRODUCTION_READINESS_CHECKLIST.md) (release gates). [WRITER_DEV_SPEC_PHASE_2.md](./WRITER_DEV_SPEC_PHASE_2.md) (coverage-aligned inventory expansion, dev tooling).

**Runtime assembles. Humans govern. The system never degrades.**

**Still to do (whole system):** This spec is reference; architecture authority is Arc-First Canonical. What remains to finish the whole system is in the canonical systems doc and planning status: [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md) § Remaining to finish whole system, [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md).
