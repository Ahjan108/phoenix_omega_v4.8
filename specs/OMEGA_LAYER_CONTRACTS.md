# Omega Layer Contracts — Handoff Schemas

**Authority:** Plan "Analyze Intake to SYSTEMS_DOCUMENTATION and V4.5 Specs" (Section 0).  
**Purpose:** Stable API contracts between Stage 1 (Catalog Planning), Stage 2 (Format Selection), and Stage 3 (Assembly). Prevents "just add one more field" drift.

---

## Stage 1 → Stage 2: BookSpec

Produced by the catalog planner. Consumed by the format selector.

**Required fields (Stage 2 needs these):**

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | string | Topic slug (e.g. relationship_anxiety, shame). |
| `persona_id` | string | Persona slug (e.g. nyc_exec, gen_z). |
| `series_id` | string \| null | Series slug if part of a series; null for standalone. |
| `installment_number` | int \| null | 1..N within series; null for standalone. |

**Identity fields (passed through to Stage 3):**

| Field | Type | Description |
|-------|------|-------------|
| `teacher_id` | string | Teacher slug. |
| `teacher_mode` | boolean | When true, Stage 3 uses SOURCE_OF_TRUTH/teacher_banks/\<teacher_id\>/approved_atoms/ for pools (Teacher Mode V4). |
| `brand_id` | string | Brand slug. |
| `angle_id` | string | Angle slug within series/domain. |
| `domain_id` | string | Domain slug (e.g. anxiety_cluster). |
| `seed` | string | Determinism seed (e.g. sha256). |
| `author_id` | string \| null | Optional. Pen-name author slug; when set, `author_positioning_profile` is required and resolved from author_registry. |
| `author_positioning_profile` | string \| null | Optional. Trust posture profile (e.g. somatic_companion, research_guide). When `author_id` present, must match registry; when absent, may be set from default_by_brand. Writer Spec §24. |
| `narrator_id` | string \| null | Optional. Narrator slug; when set, validated against config/narrators/narrator_registry.yaml (brand_compatibility, status). Resolved from config/brand_narrator_assignments.yaml when not supplied. Writer Spec §23.5. |

**Failure behavior:** Stage 1 must not emit a BookSpec with missing required fields. If a field is optional by policy (e.g. series_id for standalone books), use null. Stage 2 rejects invalid or missing required fields with a hard fail (no silent default).

---

## Stage 2 → Stage 3: FormatPlan

Produced by the format selector. Consumed by the assembly compiler (Stage 3).

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `format_structural_id` | string | F001–F015 (beat map family, slot semantics). Canonical Part 2. |
| `format_runtime_id` | string | standard_book \| deep_book_4h \| micro_book_15 \| etc. (V4.5 duration class). |
| `tier` | string | A \| B \| C. |
| `blueprint_variant` | string | linear \| wave \| scaffold \| rupture. |
| `chapter_count` | int | Target chapter count. |
| `word_target_range` | [int, int] | [min, max] words. |
| `slot_definitions` | List[List[string]] | **Required for Stage 3.** Ordered slot types per chapter (e.g. one row per chapter). Stage 3 MUST NOT infer; format selector must supply from format policy. |

**Optional but recommended:**

| Field | Type | Description |
|-------|------|-------------|
| `emotional_curve_profile` | string \| null | e.g. cool_warm_hot_land, spike, descent. |
| `rationale` | object \| null | rules_fired, inputs_digest (for debugging). |

**Failure behavior:** Stage 2 must validate FormatPlan before handoff: structural format exists (F001–F015), runtime format exists (V4.5 list), tier compatible with structural format, chapter_count within runtime bounds, blueprint allowed for tier. If invalid → hard fail. Stage 3 rejects plans that fail capability check (K-table) or emotional curve diversity rules; no silent fallback.

---

## Stage 3 output: CompiledBook (minimal metadata)

Produced by the assembly compiler. Used for QA, release gates, and golden fixtures.

**Minimal metadata (for contracts):**

| Field | Type | Description |
|-------|------|-------------|
| `plan_hash` | string | Deterministic hash of the compiled plan (input + structure). |
| `chapter_slot_sequence` | list | Ordered slot types per chapter (e.g. HOOK, SCENE, STORY, …). |
| `atom_ids` | list | Ordered atom IDs selected (per chapter/slot). |
| `dominant_band_sequence` | list \| null | Dominant emotional_intensity_band per chapter (STORY). |

**Freebie fields (set after Stage 3 by freebie planner):** [PHOENIX_FREEBIE_SYSTEM_SPEC.md](./PHOENIX_FREEBIE_SYSTEM_SPEC.md)

| Field | Type | Description |
|-------|------|-------------|
| `freebie_bundle` | list \| null | List of freebie_ids attached to this book. |
| `freebie_bundle_with_formats` | list \| null | List of `{freebie_id, formats}` (e.g. `[{freebie_id: "breath_timer_v1", formats: ["html", "pdf"]}]`). From registry output_formats; no epub for somatic/assessment. |
| `cta_template_id` | string \| null | CTA template key (e.g. tool_forward). |
| `freebie_slug` | string \| null | Deterministic URL slug: {topic}-{persona}-{primary_freebie}. |

**Author positioning (Writer Spec §24):**

| Field | Type | Description |
|-------|------|-------------|
| `author_positioning_profile` | string \| null | Trust posture profile key (e.g. somatic_companion, research_guide). |
| `positioning_signature_hash` | string \| null | sha256(profile + plan_hash); used for catalog similarity and drift dashboard. |

**Compression slot (DEV SPEC 2; when format includes COMPRESSION):**

| Field | Type | Description |
|-------|------|-------------|
| `compression_atom_ids` | list \| null | One atom_id per chapter (length = chapter_count); empty string where no slot. |
| `compression_sig` | string \| null | Stable signature of placement + length bins (S/M/L). |
| `compression_pos_sig` | string \| null | Comma-separated chapter indices that have compression (for CTSS). |
| `compression_len_vec` | list \| null | Length bin per chapter (S/M/L or ""); for CTSS and wave density. |

**Emotional role taxonomy (DEV SPEC 3; from arc):**

| Field | Type | Description |
|-------|------|-------------|
| `emotional_role_sequence` | list \| null | One role per chapter (recognition, destabilization, reframe, stabilization, integration). |
| `emotional_role_sig` | string \| null | Compact signature e.g. r-d-f-s-i for CTSS and wave density. |

**Golden fixtures:** Phase 1 deliverable is (input → plan_hash → chapter_slot_sequence → atom_ids). Same input must produce same plan_hash and same sequences.

---

## Post–Stage 3: Book rendering (Stage 6)

**CompiledBook** is consumed by **Stage 6 (book renderer)** to produce manuscript/QA prose output. Stage 6 is not a handoff contract; it reads the same CompiledBook (and optional BookSpec fields on the plan) and resolves each `atom_id` to prose from atoms/, compression_atoms, or teacher_banks (when teacher_mode).

- **Implementation:** `phoenix_v4/rendering/` (prose_resolver, book_renderer). QA: `scripts/render_plan_to_txt.py`. Pipeline: `run_pipeline.py --render-book`, `--render-formats txt`, `--render-dir`. Output: `artifacts/rendered/<plan_id>/book.txt`.
- **Authority:** [../docs/V4_FEATURES_SCALE_AND_KNOBS.md](../docs/V4_FEATURES_SCALE_AND_KNOBS.md) §1 (Stage 6) and §3.7 (Teacher Mode knobs).

---

## Strict vs non-strict failure behavior

| Stage | Strict (hard fail) | Non-strict (warn / reduce) |
|-------|--------------------|----------------------------|
| Stage 1 | Missing required BookSpec fields; invalid domain/series/angle. | Capacity warnings; diversity suggestions. |
| Stage 2 | Invalid FormatPlan (unknown format, tier mismatch, chapter_count out of bounds). | — |
| Stage 3 | Capability check fail (K-table); emotional curve diversity fail (flatline/plateau); FMT fail for full books (V4.6). | Relaxed mode may reduce chapter count if pool insufficient (configurable). |

---

## Config locations (reference)

- **Stage 1:** config/catalog_planning/ — domain_definitions.yaml, series_templates.yaml, capacity_constraints.yaml, **brand_archetype_registry.yaml** (v1.1, 24 archetypes), teacher_persona_matrix.yaml, **brand_teacher_assignments.yaml** (teacher/brand resolution when not caller-supplied).
- **Stage 2:** config/format_selection/ — format_registry.yaml, selection_rules.yaml.
- **Stage 3:** config/ (existing) — topic_engine_bindings.yaml, topic_skins.yaml. **Identity:** config/identity_aliases.yaml (persona_aliases, topic_aliases). Alias resolution is done before Stage 3; compiler receives only canonical IDs.
- **Exercise layer (somatic / slot_07_practice):** SOURCE_OF_TRUTH/exercises_v4/registry.yaml (11 types, slot policies, selection rules); approved exercises from SOURCE_OF_TRUTH/exercises_v4/approved/. Optional assembly blueprint: docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml (10-slot contract, exercise cadence, emotional curve).
- **Identity binding (Writer Spec §23):** **Pen-name authors — implemented.** config/author_registry.yaml (author_id, positioning_profile, optional assets_path); config/brand_author_assignments.yaml (default_author per brand); phoenix_v4/planning/author_brand_resolver.py (resolve author from brand when --author not supplied); phoenix_v4/planning/author_asset_loader.py (load bio, why_this_book, authority_position, audiobook_pre_intro from assets/authors/ or registry assets_path). Pipeline loads author assets when author_id set and fails if any required asset missing (§23.9); BookSpec and compiled plan carry author_assets. Freebie templates: {{author_bio}}, {{author_why_this_book}}, {{author_pen_name}}, {{author_audiobook_pre_intro}}. **Narrators — implemented.** config/narrators/narrator_registry.yaml; config/brand_narrator_assignments.yaml; phoenix_v4/planning/narrator_brand_resolver.py (default_narrator from brand); BookSpec and compiled plan carry narrator_id; run_pipeline --narrator; validation (brand_compatibility, status, disallowed_topics).
- **Author positioning (Writer Spec §24):** config/authoring/author_positioning_profiles.yaml (profiles, default_by_brand); config/author_registry.yaml (positioning_profile per author).
- **Freebies (V4 Immersion):** config/freebies/ (freebie_registry.yaml, freebie_selection_rules.yaml, tier_bundles.yaml, audio_scripts.yaml); config/catalog_planning/canonical_topics.yaml, canonical_personas.yaml; config/tts/engines.yaml; config/validation.yaml; config/asset_lifecycle.yaml.

SYSTEMS_DOCUMENTATION describes strategy and references these configs. Canonical Spec Part 2 owns format IDs and slot semantics.

---

## Still to do (whole system)

Handoff contracts are stable. Author (pen-name) resolution, narrator resolution, freebie index append in pipeline, and KB-driven gap-fill (--kb-dir) are implemented. What remains to finish the whole system is in the canonical systems doc and planning status:

- [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md) — § Remaining to finish whole system
- [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md)
