# Phoenix V4 — Canonical Systems Document

**Purpose:** Single canonical description of the whole V4 system.  
**Audience:** Engineers, QA, content governance, release.  
**Last updated:** 2026-02-22  
**Authority:** This doc is the one systems-level overview; architecture authority remains [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md).

**What’s still to do to finish the whole system:** [§ Remaining to finish](#remaining-to-finish-whole-system) below and [docs/PLANNING_STATUS.md](./PLANNING_STATUS.md).

---

## 1. Product identity

Phoenix is a **deterministic therapeutic audio operating system** that produces emotionally coherent, engine-pure journeys at scale. It is not a text generator; it is a **meaning-preserving assembly engine** with a business orchestration layer.

- **Optimize for:** emotional coherence, psychological precision, engine purity, persona alignment, deterministic reproducibility.
- **No:** literary nonfiction simulator, bestseller generator, emergent author system.

---

## 2. Architecture authority

| Layer | Authority | Role |
|-------|------------|------|
| **System architecture** | [PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) | Sole governing architecture. Arc mandatory; no arc = no compile. |
| **Content / writer rules** | [PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) | Prose, TTS, Six Atom Types, emotional QA, governance; **§23** Identity & Audiobook (pen-name authors, narrator pre-intro, persona specificity). **Writer comms (what to write for 100%):** [WRITER_COMMS_SYSTEMS_100.md](WRITER_COMMS_SYSTEMS_100.md). |
| **Stage handoffs** | [OMEGA_LAYER_CONTRACTS.md](../specs/OMEGA_LAYER_CONTRACTS.md) | BookSpec, FormatPlan, CompiledBook schemas and config locations. |
| **Teacher Mode** | [TEACHER_MODE_V4_CANONICAL_SPEC.md](../specs/TEACHER_MODE_V4_CANONICAL_SPEC.md) | Teacher banks, KB gap-fill, approval, Arc-First compatible. |
| **Release gates** | [V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md) | 15 conditions; run `scripts/run_production_readiness_gates.py` + simulation. |

---

## 3. Three-layer model

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 0 — TEACHER DOCTRINE (human-governed, offline)   │
│  Doctrine synthesis → approval → locked doctrine →       │
│  seed generation. Defines meaning only.                 │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 1 — CONTENT INTEGRITY (deterministic, enforced)   │
│  Mining → atoms → plan compiler → assembly →            │
│  validation → CI. No quality simulation; structural     │
│  and cohesion gates only.                               │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 2 — OMEGA (business logic, no content change)    │
│  Brand matrix, SKU planning, release waves,              │
│  platform similarity, upload. Composes plans only.     │
└─────────────────────────────────────────────────────────┘
```

- **Layer 0** defines meaning; only humans approve doctrine.
- **Layer 1** enforces structure; fails instead of degrading; no prose scoring in validators.
- **Layer 2** composes plans; never modifies atom content.

---

## 4. Core pipeline (Arc-First)

Every compile requires an **arc file**. No arc = no compile.

1. **Stage 1 — Catalog planning**  
   `phoenix_v4/planning/catalog_planner.py`  
   Produces **BookSpec** (topic_id, persona_id, teacher_id, brand_id, angle_id, series_id, installment_number, seed). Teacher and brand are **caller-supplied**; planner does not assign them.

2. **Stage 2 — Format selection**  
   `phoenix_v4/planning/format_selector.py`  
   Produces **FormatPlan** (format_structural_id, format_runtime_id, chapter_count, slot_definitions, tier, blueprint_variant). Arc-First: chapter_count and slot_definitions are aligned to the arc.

3. **Stage 3 — Assembly**  
   `phoenix_v4/planning/assembly_compiler.py`  
   Consumes BookSpec + FormatPlan + **Arc**; outputs **CompiledBook** (plan_hash, chapter_slot_sequence, atom_ids, dominant_band_sequence, arc_id, emotional_temperature_sequence, reflection_strategy_sequence). Reads atoms from canonical pools or, in Teacher Mode, from `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms/`.

4. **Stage 6 — Book renderer**  
   `phoenix_v4/rendering/` (prose_resolver, book_renderer)  
   Consumes **CompiledBook**; outputs **prose (manuscript/QA)**. Resolves atom_id → prose from atoms/, compression_atoms, teacher_banks (when teacher_mode). **QA:** `scripts/render_plan_to_txt.py` (uses Stage 6; `--allow-placeholders`, `--on-missing`). **Pipeline:** `run_pipeline.py --render-book` writes `artifacts/rendered/<plan_id>/book.txt`. See [docs/V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md) §1 (Stage 6) and §3.7 (Teacher Mode knobs).

**Entrypoint:** `scripts/run_pipeline.py` (--topic, --persona, --arc required; optional --teacher, --author, --narrator, --angle). When --author is omitted, author_id is resolved from config/brand_author_assignments.yaml (default_author per brand). When --narrator is omitted, narrator_id is resolved from config/brand_narrator_assignments.yaml (default_narrator per brand); Writer Spec §23.5. Teacher/persona/engine compatibility is enforced via `config/catalog_planning/teacher_persona_matrix.yaml` and `phoenix_v4/planning/teacher_matrix.py` when `--teacher` is set. **Environment:** Run with the project venv so PyYAML is available (e.g. `PYTHONPATH=. .venv/bin/python scripts/run_pipeline.py ...`). See [docs/SYSTEMS_AUDIT.md](./SYSTEMS_AUDIT.md) for full function audit.

**Angle Integration (V4.7):** When `angle_id` is set (e.g. `--angle WRONG_PROBLEM`), the **Angle Integration Layer** applies: (1) **Arc variant** — if `config/angles/angle_registry.yaml` defines `arc_path` for that angle, the pipeline uses that arc instead of `--arc`; Arc-First remains authority. (2) **Chapter 1 framing bias** — Stage 3 slot resolver ranks candidates for chapter 1 by `framing_mode` (debunk, framework, reveal, leverage) and optional atom metadata `angle_affinity`; no new pools. (3) **Integration reinforcement** — if the angle has `integration_reinforcement_type`, validation can require (or warn) that the final chapter includes an INTEGRATION atom with matching `reinforcement_type`. (4) **CTSS** — `angle_id` is included in the similarity fingerprint (weight 0.05). (5) **Wave density** — `scripts/ci/check_wave_density.py` FAILs if ≥50% of plans in the wave share the same `angle_id` (non-null only). Config: `config/angles/angle_registry.yaml`; resolver: `phoenix_v4/planning/angle_resolver.py`; bias scoring: `phoenix_v4/planning/angle_bias.py`.

**Structural Variation V4 (anti-cluster storytelling):** Deterministic variation knobs reduce template similarity across books. (1) **Config:** `config/source_of_truth/` — `book_structure_archetypes.yaml`, `journey_shapes.yaml`, `chapter_archetypes.yaml`, `section_reorder_modes.yaml`, `recurring_motif_bank.yaml`, `reframe_line_bank.yaml`. (2) **Planner:** After Stage 2, `phoenix_v4/planning/variation_selector.py` selects `book_structure_id`, `journey_shape_id`, `motif_id`, `section_reorder_mode`, `reframe_profile_id`, `chapter_archetypes` (with anti-cluster penalties from wave index). (3) **Schema:** `phoenix_v4/planning/schema_v4.py` — `variation_signature` = SHA256 of knobs; backward compat defaults for missing fields. (4) **Assembly:** Stage 3 applies role-safe section reorder (per `section_reorder_mode`), and computes `motif_injections` / `reframe_injections` for downstream renderer. (5) **Index/CTSS:** Plan output and `artifacts/freebies/index.jsonl` rows include variation knobs; `scripts/ci/update_similarity_index.py` and `check_platform_similarity.py` include `variation_signature` in fingerprint. (6) **QA:** `phoenix_v4/qa/validate_variation_signature.py`, `validate_motif_saturation.py`, `validate_reframe_diversity.py`, `validate_section_reorder_safety.py`, `validate_journey_shape_coverage.py`, `validate_variant_family_coverage.py`. (7) **Reporting:** `scripts/ci/report_variation_knobs.py` writes `artifacts/reports/variation_report.json` (variation_knob_distribution, collision placeholders).

---

## 5. Teacher Mode flow

- **Source of truth:** `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/` (raw, kb, doctrine, candidate_atoms, approved_atoms by slot type).
- **Offline pipeline:** build KB → mine_kb_to_atoms → assign band → identify_core_teachings → (optional) expand_story_atoms → **normalize_story_atoms** → **normalize_exercise_atoms** → review → approval → compile. **Gap-fill:** `tools/teacher_mining/gap_fill.py` generates candidate atoms from gap report; optional **--kb-dir** (e.g. SOURCE_OF_TRUTH/teacher_banks/&lt;teacher&gt;/kb) fills candidate body from KB (index.json or *.txt), prefix [KB draft — review and edit before approval]; report includes kb_driven, kb_docs_used.
- **Normalization (deterministic, no LLM):**  
  STORY: structure_family, min 120 words, 3 paragraphs, author_intro_style_id / author_outro_style_id (IDs only).  
  EXERCISE: exercise_family (E1_BREATH, …), min 90 words, setup/instruction/close, exercise_intro_style_id / exercise_outro_style_id.
- **Teacher/persona compatibility:** Enforced at pipeline entry via `teacher_persona_matrix.yaml` (allowed_personas, allowed_engines, preferred_locales); invalid combinations raise before Stage 1.

---

## 6. CI and release gates

**Pipeline order:** compile → structural_entropy_check → dupe_eval → update_similarity_index → publish.

- **Structural entropy** (`scripts/ci/check_structural_entropy.py`): FAIL if STORY &lt; 120w, EXERCISE &lt; 90w, missing atom, story family dominance &gt; 70%, body contains `[EXPANDED]`, (teacher-mode) chapter missing exercise or teacher anchor (STORY with teacher_id or &gt;60w), same intro/outro style ID &gt; 3 consecutive chapters, or unique intro style IDs &lt; 3. **DEV SPEC 3:** FAIL if missing emotional_role_sequence (unless --allow-missing-role-seq), length mismatch, last≠integration, &gt;2 consecutive same role. Inputs: compiled plan, optional BookSpec, optional `--atoms-dir`, `--teacher-mode`, `--allow-missing-role-seq`.
- **Author positioning** (`scripts/ci/check_author_positioning.py`): FAIL if author_id present but positioning_profile missing or mismatches registry; FAIL if profile-forbidden language (e.g. research_guide first_person &gt; 8%, somatic_companion command_language over threshold, slang/mystical when forbidden). Inputs: `--plan`, optional `--book-spec`, optional `--atoms-dir`.
- **Platform similarity (extended CTSS)** (`scripts/ci/check_platform_similarity.py`): Pre-publish structural similarity gate. CTSS includes arc, band_seq, slot_sig, exercise_chapters, story_fam_vec, ex_fam_vec, tps, compression, **role_seq** (DEV SPEC 3; weight 0.06). Index: `artifacts/catalog_similarity/index.jsonl`; append via `scripts/ci/update_similarity_index.py`. Backward-compatible with index rows missing new fields.
- **Wave density** (`scripts/ci/check_wave_density.py`): FAIL wave if ≥30% same arc_id, ≥40% identical band_seq, ≥50% identical slot_sig, ≥60% identical exercise placement, **≥40% identical emotional_role_sig** (DEV SPEC 3). Requires `--plans-dir`; plans must have arc_id, emotional_temperature_sequence, slot_sig, exercise_chapters (Stage 3 output).
- **Production readiness:** 15 conditions in [V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md); run `scripts/run_production_readiness_gates.py` and simulation.
- **Brand archetype registry** (`phoenix_v4/qa/validate_brand_archetype_registry.py`): FAIL if registry YAML violates structural rules (unique brand_id/admin_id, duration sum 1.0, mid_form cap, unique lead_voice, no 100% style_pool overlap). Run: `PYTHONPATH=. python3 phoenix_v4/qa/validate_brand_archetype_registry.py`. Authority: [BRAND_ARCHETYPE_VALIDATOR_SPEC.md](../specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md).

**Observability and scale:** Structural drift dashboard (`scripts/obs/build_structural_drift_dashboard.py`) writes `artifacts/drift/summary.json` and `report.html` (includes **emotional role** distribution, top role signatures, role×band counts; DEV SPEC 3). Monte Carlo CTSS risk (`simulation/run_monte_carlo_ctss.py`) simulates duplication risk vs index. Wave orchestrator (`phoenix_v4/planning/wave_orchestrator.py`) selects a balanced wave from candidates (arc/band/slot/ex diversity, density constraints).

---

## 7. Freebie and asset pipeline (V4 Immersion)

- **Canonical sources:** `config/catalog_planning/canonical_topics.yaml` and `canonical_personas.yaml`; validated by `scripts/validate_canonical_sources.py` against topic_engine_bindings and identity_aliases.
- **Asset planning:** `scripts/plan_freebie_assets.py` — catalog mode (`--catalog <yaml>`) or canonical mode (`--topics`, `--personas`); writes `artifacts/asset_planning/manifest.jsonl`.
- **Asset creation:** `scripts/create_freebie_assets.py` — reads manifest; generates HTML/PDF/EPUB/MP3 into format-first store `store/{format}/{topic}/{persona}/{freebie_id}.{ext}`.
- **Validation:** `scripts/validate_asset_store.py` — manifest vs store; optional `--rules config/validation.yaml`.
- **Book pipeline:** After Stage 3, freebie planner sets `freebie_bundle` and `freebie_bundle_with_formats`. `generate_freebies_for_book` (in `freebie_renderer`) resolves from asset store when `--asset-store` is set, else renders; `--publish-dir` writes outputs to `publish_dir/{slug}/`. CLI: `run_pipeline.py --formats html,pdf,epub,mp3 --skip-audio --publish-dir <dir> --asset-store <store_root>`.
- **Main book prose (Stage 6):** Optional `--render-book` renders CompiledBook → manuscript/QA .txt via `phoenix_v4/rendering` (prose_resolver + TxtWriter). Output: `artifacts/rendered/<plan_id>/book.txt`. QA path: `scripts/render_plan_to_txt.py <plan.json> -o <out.txt>` (same Stage 6 API; supports `--allow-placeholders`, `--on-missing`, `--atoms-root`).
- **Tier bundles:** `config/freebies/tier_bundles.yaml` (Good/Better/Best). **Asset lifecycle:** `config/asset_lifecycle.yaml` (regenerate_when, auto_prune). See [PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md) §8–§11.

---

## 8. Systems test (rigorous)

A single **systems test** exercises pipeline, config, resolvers, freebies, asset pipeline, CI/QA, and contracts; records failures in a structured report; and supports learn/fix/enhance.

- **Entry point:** `python3 scripts/systems_test/run_systems_test.py --all` (or `--phase 1` … `--phase 7`). Use the project venv so PyYAML is available (e.g. `.venv/bin/python` or `source .venv/bin/activate`).
- **Output:** `artifacts/systems_test/report_<timestamp>.json` (machine-readable) and `report_<timestamp>.md` (summary + per-failure). Optional: `--output-dir <dir>`, `--strict` (exit 1 if any check failed).
- **Phases:** 1 — Config and schema validity. 2 — Resolvers (teacher, author, narrator, canonical). 3 — Full pipeline per arc + validators (validate_compiled_plan, validate_arc_alignment, validate_engine_resolution). 4 — Freebie planner and renderer. 5 — Asset pipeline (validate_canonical_sources, plan_freebie_assets, create_freebie_assets, validate_asset_store). 6 — CI/QA (structural entropy, author positioning, platform similarity, brand archetype, Gate #49, production gates, simulation). 7 — Contract/schema compliance (CompiledBook shape, freebie_bundle_with_formats).
- **Learn:** Each failure has a **category** (e.g. config_missing, resolver_fail, pipeline_fail, validator_fail, contract_violation) and **suggested_fix** in the report.
- **Fix:** No automatic edits; use suggested_fix and fix config or code. Optional: `validate_canonical_sources.py --fix` (if implemented) to sync canonical from bindings/aliases.
- **Enhance:** For every failed check, add a regression assertion (in the harness or in `tests/`) so the same failure cannot recur. Report lists failures for follow-up.

Requires PyYAML for config and arc loading. See plan: Rigorous systems test (learn, fix, enhance).

---

## 9. Config and key paths

| Purpose | Location |
|--------|----------|
| Catalog planning | config/catalog_planning/ (domain_definitions, series_templates, capacity_constraints, **brand_archetype_registry.yaml** v1.1, 24 archetypes) |
| Teacher/persona matrix | config/catalog_planning/teacher_persona_matrix.yaml |
| Identity aliases | config/identity_aliases.yaml (persona_aliases, topic_aliases) |
| Format selection | config/format_selection/ (format_registry, selection_rules) |
| Master arcs | config/source_of_truth/master_arcs/; emotional_role_sequence required (DEV SPEC 3). Role→slot: config/format_selection/emotional_role_slot_requirements.yaml. |
| **Structural Variation V4** | config/source_of_truth/ (book_structure_archetypes, journey_shapes, chapter_archetypes, section_reorder_modes, recurring_motif_bank, reframe_line_bank). Plan fields: book_structure_id, journey_shape_id, motif_id, section_reorder_mode, reframe_profile_id, chapter_archetypes, variation_signature. Selector: phoenix_v4/planning/variation_selector.py; schema: phoenix_v4/planning/schema_v4.py. Report: scripts/ci/report_variation_knobs.py → artifacts/reports/variation_report.json. |
| Engines | config/source_of_truth/engines/ |
| Teacher banks | SOURCE_OF_TRUTH/teacher_banks/&lt;teacher_id&gt;/ |
| **Exercise registry (V4 somatic)** | **SOURCE_OF_TRUTH/exercises_v4/** (registry.yaml, 11 types; candidate/_stubs/, approved/; slot_07_practice + selection rules) |
| **Somatic assembly blueprint** | **docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml** (10-slot contract, exercise cadence, emotional curve; structure only) |
| **Compression atoms (slot_08_compression)** | **SOURCE_OF_TRUTH/compression_atoms/** approved/\<persona\>/\<topic\>/*.yaml; 40–120w, one insight; formats may include COMPRESSION via slot_template (e.g. F006). CI: structural entropy, CTSS, wave density. DEV SPEC 2. |
| **Freebies (V4 Immersion)** | config/freebies/ (registry, selection_rules, **tier_bundles.yaml**, **audio_scripts.yaml**); **config/catalog_planning/canonical_topics.yaml**, **canonical_personas.yaml**; **config/tts/engines.yaml** (TTS engine + voice mapping); **config/validation.yaml**, **config/asset_lifecycle.yaml**. Scripts: **validate_canonical_sources.py**, **plan_freebie_assets.py**, **create_freebie_assets.py**, **validate_asset_store.py**. Asset store: **artifacts/freebie_assets/store/{format}/{topic}/{persona}/{freebie_id}.{ext}**; manifest: **artifacts/asset_planning/manifest.jsonl**. Pipeline: **--formats**, **--skip-audio**, **--publish-dir**, **--asset-store**. |
| **Author assets (pen-name)** | docs/authoring/AUTHOR_ASSET_WORKBOOK.md; assets/authors/&lt;author_id&gt;/ (bio, why_this_book, authority_position, audiobook_pre_intro) or **assets_path** in author_registry (directory or single multi-doc YAML). Pipeline: `phoenix_v4/planning/author_asset_loader.py` loads when author_id set; fails if any required asset missing (§23.9). Freebie templates: placeholders `{{author_bio}}`, `{{author_why_this_book}}`, `{{author_pen_name}}`, `{{author_audiobook_pre_intro}}`. |
| **Author registry** | config/author_registry.yaml — author_id → brand_id, persona_ids, topic_ids, **positioning_profile** (mandatory), optional **assets_path** (dir or file). Pipeline resolves author from registry; atoms stay persona/topic keyed. Teacher resolution: brand_teacher_assignments. |
| **Brand → author assignment** | config/brand_author_assignments.yaml — default_author per brand_id (optional topic_ids, persona_ids, series_ids). Resolved by `phoenix_v4/planning/author_brand_resolver.py` when run_pipeline does not receive --author. |
| **Author positioning profiles** | config/authoring/author_positioning_profiles.yaml — trust posture profiles (somatic_companion, research_guide, elder_stabilizer); default_by_brand for books without author_id. Enforced in Writer Spec §24 and scripts/ci/check_author_positioning.py. |
| **Persona-depth (atoms)** | docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md (micro-stakes, promotion workflow) |
| **Author registry** | config/author_registry.yaml — author_id, pen_name, brand_id, persona_ids, topic_ids, positioning_profile, assets_path (Writer Spec §23). |
| **Narrator registry** | config/narrators/narrator_registry.yaml — narrator_id, display_name, brand_compatibility, status; Writer Spec §23.5. Default from config/brand_narrator_assignments.yaml via narrator_brand_resolver. |
| **Brand → narrator assignment** | config/brand_narrator_assignments.yaml — default_narrator per brand_id; phoenix_v4/planning/narrator_brand_resolver.py. |
| **Stage 6 (book renderer)** | phoenix_v4/rendering/ (prose_resolver, book_renderer). QA: scripts/render_plan_to_txt.py. Pipeline: run_pipeline.py --render-book, --render-formats txt, --render-dir. Output: artifacts/rendered/\<plan_id\>/book.txt. See [V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md). |
| Emotional governance (QA) | phoenix_v4/qa/emotional_governance_rules.yaml |
| Similarity index | artifacts/catalog_similarity/index.jsonl |

---

## 10. Remaining to finish whole system

Planning and implementation are **not 100%** until the following are addressed. Details: [docs/PLANNING_STATUS.md](./PLANNING_STATUS.md).

| Area | Current state | Still to do |
|------|----------------|-------------|
| **Author/teacher assignment** | **Implemented.** Teachers: brand_teacher_assignments.yaml + teacher_brand_resolver. **Pen-name authors:** config/author_registry.yaml (luna_hart, kai_nakamura, marcus_cole, diane_reyes); config/brand_author_assignments.yaml + author_brand_resolver (default_author from brand when --author not supplied); author_asset_loader loads bio/why_this_book/authority_position/audiobook_pre_intro from assets/authors/ or registry assets_path; pipeline fails on missing assets (§23.9); compiled plan includes author_assets; freebie_renderer supports {{author_bio}}, {{author_why_this_book}}, {{author_pen_name}}, {{author_audiobook_pre_intro}}. | — |
| **Coverage enforcement** | **Implemented.** phoenix_v4/planning/coverage_checker.py; wired in production readiness gate 2b. | — |
| **Gate #49 (locale/territory)** | **Wired.** scripts/distribution/pre_export_check.py runs Gate #49 before export. | — |
| **Freebies** | **Implemented.** Deterministic freebie planner (post–Stage 3), registry, selection rules, density CI, CTSS; pipeline maintains plan rows in artifacts/freebies/index.jsonl (one row per book_id) and renderer writes artifact logs to artifacts/freebies/artifacts_index.jsonl; **V4 Immersion Ecosystem:** canonical topics/personas, asset pipeline (plan_freebie_assets, create_freebie_assets, validate_asset_store), multi-format store, publish_dir, tier_bundles, pipeline flags (--formats, --skip-audio, --publish-dir, --asset-store). | — |
| **Narrators** | **Implemented.** config/narrators/narrator_registry.yaml; BookSpec and compiled plan carry narrator_id; run_pipeline --narrator; default from brand when not supplied (narrator_brand_resolver). Writer Spec §23.5. | — |
| **Teacher Mode Phase 2/3** | **Implemented.** Normalization, entropy CI, platform similarity, teacher matrix; report_teacher_gaps, gap_fill.py (stubs + optional --kb-dir for KB-driven body from teacher KB), approve_atoms.py for gap-fill and approval workflows. | — |
| **Final book renderer (Stage 6)** | **Implemented.** phoenix_v4/rendering: prose_resolver (atom_id → prose from atoms/, compression_atoms, teacher_banks), book_renderer (TxtWriter, render_book). QA: scripts/render_plan_to_txt.py uses Stage 6. Pipeline: --render-book, --render-formats txt, --render-dir; outputs artifacts/rendered/\<plan_id\>/book.txt. Edge cases: placeholders/silence, missing atoms, persona/topic from plan or inferred. See [V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md) §1 and §3.7. | — |

Each spec that is part of the system has a **Still to do** section pointing here and to PLANNING_STATUS.

---

## 11. Doc map

| Doc | Role |
|-----|------|
| **docs/SYSTEMS_V4.md** (this doc) | Canonical systems overview; whole V4 system in one place. |
| **docs/PLANNING_STATUS.md** | Doc status table, 100% planning gaps, freebies/authors/narrators. |
| **docs/V4_FEATURES_SCALE_AND_KNOBS.md** | Single reference: all V4 features, scale/anti-spam, Teacher Mode subsection, Stage 6, and every knob (CLI, config, thresholds). |
| **specs/README.md** | Spec index; links to Arc-First, Writer Spec, Omega contracts, Teacher Mode, checklist. |
| **specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md** | Sole architecture authority; arc, engine, pools; validators structural only. |
| **specs/PHOENIX_V4_5_WRITER_SPEC.md** | Writer/content authority; TTS, Six Atom Types, emotional QA; **§23** Identity & Audiobook Governance. |
| **specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md** | CI rules for brand archetype registry (structural, vocabulary, voice, pricing). |
| **specs/OMEGA_LAYER_CONTRACTS.md** | Stage 1→2→3 handoff schemas and config references. |
| **specs/TEACHER_MODE_V4_CANONICAL_SPEC.md** | Teacher Mode implementation authority. |
| **specs/TEACHER_MODE_NORMALIZATION_SPEC.md** | Normalization pipeline and entropy CI. |
| **specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md** | 15 release conditions. |
| **docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml** | Somatic book assembly: 10-slot contract, exercise cadence, emotional curve template (structure only). |
| **docs/authoring/AUTHOR_ASSET_WORKBOOK.md** | Operational: pen-name author assets (bio, why_this_book, authority_position, audiobook_pre_intro). |
| **docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md** | Operational: persona-specific micro-stakes, promotion workflow (provisional_template → confirmed). |
| **SOURCE_OF_TRUTH/exercises_v4/README.md** | Exercise registry (11 types), candidate/approved layout, slot_07_practice integration. |

Older multi-doc and talp/SYSTEMS_DOCUMENTATION.md remain for reference; **this doc (docs/SYSTEMS_V4.md) is the single canonical systems description for V4.**
