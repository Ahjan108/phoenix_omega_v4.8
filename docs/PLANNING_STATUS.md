# Phoenix — System-Wide Planning Status

**Last updated:** 2026-02-25  
**Purpose:** Single place for doc status, planning completeness, and what’s left for 100% planning.

**Canonical systems doc (whole V4 in one place):** [docs/SYSTEMS_V4.md](./SYSTEMS_V4.md)

**Active personas and topics (catalog source of truth):** [unified_personas.md](../unified_personas.md) — 10 active personas, 12 active topics; config/catalog_planning/canonical_*.yaml must align.

---

## 1. Doc status across the system

| Doc / area | Status | Notes |
|------------|--------|------|
| **docs/SYSTEMS_V4.md** | **Canonical** | Single canonical systems document; whole V4 system description; remaining work summary. |
| **specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md** | **Canonical** | Sole system architecture; arc mandatory; supersedes V4/V4.6 for structure. |
| **specs/PHOENIX_V4_5_WRITER_SPEC.md** | **Canonical** | Single writer authority; TTS, Six Atom Types, §§1–22 + **§23 Identity & Audiobook Governance**, §24 Author Positioning, §25 Compression. **Writer comms (deliverables for 100%):** [docs/WRITER_COMMS_SYSTEMS_100.md](../docs/WRITER_COMMS_SYSTEMS_100.md). |
| **specs/PHOENIX_V4_CANONICAL_SPEC.md** | **Reference** | Superseded for architecture by Arc-First; retained for atom/format/slot reference. |
| **specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md** | **Active** | 15 release conditions; run `scripts/run_production_readiness_gates.py` + simulation. |
| **specs/V4_6_BINGE_OPTIMIZATION_LAYER.md** | **Active** | FMT (Forward Momentum Trigger); emotional curves; volatility quotas. |
| **specs/OMEGA_LAYER_CONTRACTS.md** | **Active** | Stage 1→2→3 (BookSpec, FormatPlan, CompiledBook); config locations. |
| **config/source_of_truth/chapter_planner_policies.yaml** | **Active** | Chapter planner policy layer: role distribution targets, book-size quotas, transition constraints, slot policy weights (exercise/reflection/story depth). |
| **specs/WRITER_DEV_SPEC_PHASE_2.md** | **Active** | Coverage, compile_strict; writer production rules. |
| **specs/ARC_AUTHORING_PLAYBOOK.md** | **Active** | Arc authors; design sequence, failure modes, scale. |
| **specs/ENGINE_DEFINITION_SCHEMA.md** | **Active** | Engine YAML; resolution types; engine–arc compatibility. |
| **specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md** | **Advisory** | Narrative Depth Layer; subordinate to Arc-First Canonical. |
| **specs/TEACHER_MODE_MASTER_SPEC.md** | **Active** | Teacher Mode: strict-by-default, coverage gate, EXERCISE fallback, TDEL, CI; single canonical summary. |
| **TEACHER_MODE_INVARIANTS.md** (repo root) | **Active** | Non-negotiable invariants when teacher_mode=true. |
| **docs/TEACHER_MODE_SYSTEM_REFERENCE.md** | **Active** | Full system reference: modules, scripts, config, artifacts. |
| **specs/TEACHER_MODE_V4_CANONICAL_SPEC.md** | **Active** | Teacher Mode V4: teacher_banks, KB gap-fill (offline), Arc-First compatible; dev implementation authority. |
| **specs/TEACHER_MODE_NORMALIZATION_SPEC.md** | **Active** | Normalization pipeline; structural entropy CI; platform similarity; style IDs. |
| **specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md** | **Active** | Content team workflow for Teacher Mode (onboard, KB, gaps, approve, compile). |
| **specs/README.md** | **Active** | Spec index; authority and run instructions; links to SYSTEMS_V4. |
| **talp/SYSTEMS_DOCUMENTATION.md** | **Reference** | Legacy full system rebuild spec; Layer 0–2; superseded for canonical overview by docs/SYSTEMS_V4.md. |
| **unified_personas.md** (repo root) | **Canonical** | Source of truth for active personas (10) and topics (12); full catalog metadata, design foundation, catalog math, template requirements, consumer language map, production sequence. canonical_personas.yaml / canonical_topics.yaml must align. |
| **config/catalog_planning/** | **Active** | domain_definitions, series_templates, capacity_constraints, teacher_persona_matrix.yaml, **brand_archetype_registry.yaml** (v1.1, 24 archetypes); **canonical_personas.yaml**, **canonical_topics.yaml** (align with unified_personas.md). |
| **config/localization/** | **Active** | locale_registry, brand_registry_locale_extension; BookSpec locale/territory. |
| **config/teachers/** | **Active** | teacher_registry.yaml (Teacher Mode); **per-teacher &lt;teacher_id&gt;.yaml** (teacher_exercise_fallback, exercise_wrapper, teacher_quality_profile); example master_feng.yaml. See docs/TEACHER_MODE_SYSTEM_REFERENCE.md. |
| **specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md** | **Active** | CI rules for brand archetype registry (structural, vocabulary, voice, pricing); fail at plan time. |
| **phoenix_v4/qa/emotional_governance_rules.yaml** | **Active** | Machine-readable emotional/drift/TTS CI rules. |
| **phoenix_v4/qa/validate_brand_archetype_registry.py** | **Active** | CI gate: validate registry YAML (run `PYTHONPATH=. python3 phoenix_v4/qa/validate_brand_archetype_registry.py`). |
| **specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md** | **Active** | Freebie pipeline + **V4 Immersion Ecosystem:** registry, planner, density gate, CTSS; canonical topics/personas, asset pipeline (plan_freebie_assets, create_freebie_assets, validate_asset_store), multi-format store, publish_dir, tier_bundles, TTS/validation/asset_lifecycle config. |
| **docs/authoring/AUTHOR_ASSET_WORKBOOK.md** | **Active** | Operational: pen-name author assets (bio, why_this_book, authority_position, audiobook_pre_intro); content team. |
| **docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md** | **Active** | Operational: persona-specific micro-stakes, environmental cues, promotion workflow (provisional_template → confirmed). |
| **simulation/config/** | **Active** | v4_5_formats, emotional_temperature_curves, validation_matrix (volatility tiers). |
| **SOURCE_OF_TRUTH/exercises_v4/** | **Active** | registry.yaml (11 types), candidate/_stubs/, approved/; slot_07_practice + selection rules. |
| **docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml** | **Active** | Somatic book assembly: 10-slot contract, exercise cadence, emotional curve template; structure only, no prose. |
| **docs/CREATIVE_QUALITY_GATE_V1.md** | **Active** | Creative Quality Gate v1: post-compile read-only gate; five deterministic signals (arc motion, transformation, specificity, ending, rhythm); config creative_quality_v1.yaml; phoenix_v4/gates/check_creative_quality_v1.py; output book_quality_summary_*.json. |
| **scripts/generate_full_catalog.py** | **Active** | Full catalog orchestrator: portfolio → BookSpec → compile → wave selection. Use `--plan-only` to produce only BookSpecs (no compile/assembly), e.g. `--max-books 108 --plan-only`. Use `--brand` + `--max-books 10` + `--skip-wave-selection` for First 10 Books evaluation. |
| **docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md** | **Active** | Human-quality checklist (arc, story, exercise, voice, ending); use after each compile. |
| **docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md** | **Active** | Evaluate 10 books from one brand: compile → blind listen → 5-axis score → pattern analysis. |
| **docs/SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md** | **Active** | Manual impact check: each chapter ≥2 of Recognition/Reframe/Relief/Challenge/Identity. |
| **docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md** | **Active** | Upstream: STORY atom rubric (specificity, cost, conflict, insight pivot, echo). Pass/fail if lacks 2 of 5; highest ROI. |
| **docs/NARRATIVE_TENSION_VALIDATOR.md** | **Active** | Upstream: tension slope (rise/break/resolve vs oscillate/plateau); chapter-level tension questions; “where does rupture happen?” |
| **docs/INSIGHT_DENSITY_ANALYZER.md** | **Active** | Upstream: insight density = reframes per 1k words; target 1 per 800–1,200 words; what counts vs encouragement/affirmation. |
| **phoenix_v4/quality/** | **Active** | Standalone creative QA: **story_atom_lint.py** (per-atom CANONICAL parsing, ops artifact story_atom_lint_summary_*), **transformation_heatmap.py**, **memorable_line_detector.py**, **marketing_assets_from_lines.py**, **quality_bundle_builder.py** (CSI, book_quality_bundle_*.json). **base.py**: exit 0/1/2, AtomBlock, parse_canonical_blocks. See phoenix_v4/quality/README.md. |
| **phoenix_v4/ops/** (quality + registry) | **Active** | **wave_candidates_enricher.py** (enrich candidates from book_quality_bundle); **quality_objective.py** (normalize_quality, wave quality stats, objective terms); wave_optimizer_constraint_solver quality constraints + objective weights; **update_memorable_line_registry.py** (emits stdout JSON `{"appended": N}`; registry JSONL/snapshot written only when bundle has tracked good/great lines), **check_memorable_line_registry.py**; **catalog_health_dashboard_builder.py**; **quality_bundle_postprocessor.py** (duplication_safety). **Golden path:** `scripts/run_golden_quality_path.py` (bundle → update_registry → enricher → solver → check_registry; parses `{"appended": N}`, fails if missing). **Regression tests:** `tests/test_quality_regression.py` (malformed CANONICAL, missing chapter text, duplicate memorable-line collision). Config: config/quality/memorable_line_registry_policy.yaml. See phoenix_v4/ops/README.md. |
| **docs/SCHEMA_CHANGELOG.md** | **Active** | Ops and wave JSON schema version history; migration notes; required on any schema change. |
| **config/ops_schema_registry.yaml** | **Active** | Ops artifact type → schema_path, artifact_pattern, current_version; includes book_quality_bundle, wave_candidates_enriched, memorable_line_registry_snapshot, memorable_line_registry_violations, catalog_health_summary; used by scripts/ci/validate_ops_artifacts.py (scans artifacts/ops and artifacts/waves). |
| **config/wave_optimizer_blocking_codes.yaml** | **Active** | Canonical wave optimizer blocking reason codes and Slack/Jira routing; machine-parseable. |
| **schemas/** (ops + wave) | **Active** | JSON Schema (Draft 2020-12/7): wave_candidates, wave_optimizer_solution, wave_optimizer_infeasible, book_quality_summary_v1, **book_quality_bundle_v1**, **wave_candidates_enriched_v1**, story_atom_lint_v1, book_transformation_summary_v1, memorable_line_summary_v1, **memorable_line_registry_snapshot_v1**, **memorable_line_registry_violations_v1**, **catalog_health_summary_v1**. |
| **docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md** | **Active** | Tuple viability gate (Phase 1) and coverage health report (Phase 2); tuple universe from catalog so NO_ARC appears for missing arcs; paths, risk model, config. Replaces cursor_smart_planner.md. |

---

## 2. What is left to do for 100% planning

Planning is **not 100%** until the following are specified and, where applicable, implemented:

| Gap | Current state | Needed for 100% |
|-----|----------------|-----------------|
| **Author/teacher assignment** | **Implemented.** Teachers: `config/catalog_planning/brand_teacher_assignments.yaml` + `phoenix_v4/planning/teacher_brand_resolver.py`; `run_pipeline.py` resolves (teacher_id, brand_id) when not supplied. **Pen-name authors:** `config/author_registry.yaml`, `config/brand_author_assignments.yaml` + `phoenix_v4/planning/author_brand_resolver.py` (default_author from brand); `phoenix_v4/planning/author_asset_loader.py` loads author assets when author_id set; pipeline fails on missing assets (Writer Spec §23.9); compiled plan includes author_assets; freebie templates support author placeholders. | — |
| **Freebies** | **Freebie pipeline + V4 Immersion Ecosystem implemented.** See [specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md): deterministic planner, registry, selection rules, CI density gate, CTSS; **canonical topics/personas**, asset pipeline (plan_freebie_assets, create_freebie_assets, validate_asset_store), multi-format store, publish_dir, tier_bundles. Pipeline appends to artifacts/freebies/index.jsonl when writing a plan. Companion (§34) remains **companion marketing** (descriptions, bios, metadata). | — |
| **Narrators** | **Implemented.** config/narrators/narrator_registry.yaml; config/brand_narrator_assignments.yaml; phoenix_v4/planning/narrator_brand_resolver.py; BookSpec and compiled plan carry narrator_id; run_pipeline --narrator and default from brand. Writer Spec §23.5. | — |
| **Coverage enforcement in code** | **Implemented.** `phoenix_v4/planning/coverage_checker.py` runs capability_check over discovered (persona, topic); wired in `run_production_readiness_gates.py` gate 2b. | — |
| **Gate #49 in pipeline** | **Wired.** Gate exists; `scripts/distribution/pre_export_check.py` runs Gate #49 before export. Call it before platform export. | — |
| **Final book renderer (Stage 6)** | **Implemented.** `phoenix_v4/rendering/` (prose_resolver, book_renderer); QA script `scripts/render_plan_to_txt.py` uses Stage 6; pipeline `--render-book`, `--render-formats txt`, `--render-dir`. Output: manuscript/QA .txt at `artifacts/rendered/<plan_id>/book.txt`. See [V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md) §1 (Stage 6) and §3. | — |
| **Chapter planner policy layer** | **Implemented.** `phoenix_v4/planning/chapter_planner.py` runs before slot resolution in Stage 3; policy in `config/source_of_truth/chapter_planner_policies.yaml`; strict order: candidate generation → quota/transition filter → novelty score → deterministic select. Emits `chapter_archetypes`, `chapter_exercise_modes`, `chapter_reflection_weights`, `chapter_story_depths`, `chapter_planner_warnings`. | — |

Everything else needed for **deterministic assembly, emotional QA, TTS rhythm, drift protection, and release simulation** is specified and partially or fully implemented (Writer Spec §16, emotional_governance_rules.yaml, catalog planner with locale, simulation Phase 2/3, production readiness checklist).

---

## 3. Did we plan freebies? Authors? Narrators?

| Concept | Planned? | Where / how |
|--------|-----------|--------------|
| **Freebies** | **Yes (pipeline + V4 Immersion).** | **Planned and implemented:** [PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md) — freebie_registry, freebie_planner (post–Stage 3), deterministic CTAs, anti-spam density gate, CTSS; **V4 Immersion Ecosystem:** canonical_topics/personas, asset pipeline (plan_freebie_assets, create_freebie_assets, validate_asset_store), multi-format store (HTML/PDF/EPUB/MP3), publish_dir, tier_bundles, TTS/validation/asset_lifecycle config. Somatic freebie HTML apps remain assets; planner assigns which freebie(s) attach to which book. |
| **Authors (teachers)** | **Yes.** | **Planned and implemented:** BookSpec has `teacher_id`; assignment from `brand_teacher_assignments.yaml` via `teacher_brand_resolver` when caller does not supply; pipeline resolves (teacher_id, brand_id) before Stage 1. Teacher matrix validates allowed persona/engine. |
| **Authors (pen-name)** | **Yes.** | **Planned and implemented:** BookSpec has `author_id` and `author_positioning_profile`; assignment from `brand_author_assignments.yaml` via `author_brand_resolver` when --author not supplied; `author_asset_loader` loads bio, why_this_book, authority_position, audiobook_pre_intro from assets/authors/ or registry assets_path; pipeline fails if assets missing (§23.9); compiled plan includes author_assets; freebie_renderer placeholders: {{author_bio}}, {{author_why_this_book}}, {{author_pen_name}}, {{author_audiobook_pre_intro}}. |
| **Narrators** | **Yes.** | **Implemented:** narrator_registry.yaml, brand_narrator_assignments.yaml, narrator_brand_resolver; BookSpec narrator_id; run_pipeline --narrator and default from brand; validation (brand_compatibility, status, disallowed_topics). Writer Spec §23.5. |

---

## 4. Summary

- **Canonical systems doc:** [docs/SYSTEMS_V4.md](./SYSTEMS_V4.md) is the single place that describes the whole V4 system; all specs know what’s still to do via that doc and this one.
- **Doc status:** All core specs and configs have a clear status (canonical, reference, active, advisory); see table in §1.
- **100% planning:** All previously listed gaps are **implemented**: author/teacher assignment (brand_teacher_assignments + resolver), coverage enforcement (coverage_checker + gate 2b), Gate #49 (pre_export_check), Teacher Mode gap-fill and approval (report_teacher_gaps, gap_fill with optional --kb-dir, approve_atoms), narrator support (narrator_registry, brand_narrator_assignments, narrator_brand_resolver), freebie pipeline including index append and full immersion types.
- **Freebies:** Freebie pipeline and V4 Immersion Ecosystem are specified and implemented (deterministic planner, registry with all immersion types and templates, density gate, CTSS; pipeline appends to artifacts/freebies/index.jsonl when writing a plan; canonical sources, asset pipeline, multi-format store, publish_dir, tier_bundles); see specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md.
- **Authors (teachers):** Assignment from config when not supplied (teacher_brand_resolver + brand_teacher_assignments.yaml); teacher matrix validates allowed persona/engine.
- **Authors (pen-name):** Author resolution implemented: brand_author_assignments.yaml + author_brand_resolver; author_asset_loader; pipeline loads assets and fails on missing (§23.9); author_assets in plan output; freebie author placeholders.
- **Narrators:** Implemented: narrator_registry, brand_narrator_assignments, narrator_brand_resolver; pipeline --narrator and default from brand.

**Teacher Mode V4** is specified and implemented: dev spec, authoring playbook, normalization + entropy CI + platform similarity + teacher matrix; `phoenix_v4/qa/report_teacher_gaps.py`, `tools/teacher_mining/gap_fill.py` (stubs + optional **--kb-dir** for KB-driven body from teacher KB), `tools/approval/approve_atoms.py` for gap-fill and approval workflows.

---

## 5. Implementation status (remaining V4 dev tasks)

Summary of what was implemented for the remaining V4 dev tasks (including optional ones):

1. **Freebie index append** — Pipeline appends to `artifacts/freebies/index.jsonl` when writing a plan (plan rows). No separate code change; documented in SYSTEMS_V4 and this doc.
2. **Narrator support (Writer Spec §23.5)** — config/narrators/narrator_registry.yaml; config/brand_narrator_assignments.yaml; phoenix_v4/planning/narrator_brand_resolver.py (resolve_narrator_from_brand, validate_narrator_for_book); BookSpec narrator_id; run_pipeline --narrator (default from brand when omitted); narrator_id in compiled plan output. OMEGA_LAYER_CONTRACTS, SYSTEMS_V4, PLANNING_STATUS, REPO_FILES updated.
3. **KB-driven gap-fill (Teacher Mode optional)** — tools/teacher_mining/gap_fill.py: optional --kb-dir (path to teacher KB). When set: loads texts from kb_dir/index.json (documents[].text) or *.txt; for each candidate atom sets body from first 150 words of a KB doc (round-robin); body prefixed with [KB draft — review and edit before approval]; run report includes kb_driven, kb_docs_used; source label gap_fill_kb when KB used. SYSTEMS_V4 Teacher Mode row and REPO_FILES updated.
4. **V4 Immersion freebie types** — All immersion types in registry (journal_pdf, identity_sheet_pdf, thirty_day_tracker_pdf, environment_guide_pdf, emergency_kit_html, guided_audio, affirmations_audio, audio_journal_prompts, conversation_scripts_pdf, resistance_mapping_html, accountability_partner_pdf); templates in SOURCE_OF_TRUTH/freebies/templates/; tier_bundles updated; video/MP4 deferred. PHOENIX_FREEBIE_SYSTEM_SPEC §4 and registry updated.
5. **Doc updates** — Remaining-to-finish table in SYSTEMS_V4: Freebies, Narrators, Teacher Mode Phase 2/3 all show "Still to do: —". PLANNING_STATUS: Narrators and Freebies rows updated; §4 Summary and §5 (this section) added. OMEGA_LAYER_CONTRACTS: narrator_id in BookSpec; Still to do notes narrator and KB-driven gap-fill implemented. REPO_FILES: narrator config and narrator_brand_resolver; gap_fill.py --kb-dir.
6. **Stage 6 (book renderer)** — `phoenix_v4/rendering/`: prose_resolver (atom_id → prose from atoms/, compression_atoms, teacher_banks), book_renderer (TxtWriter, render_book). Refactored `scripts/render_plan_to_txt.py` to use Stage 6 API. Pipeline: `run_pipeline.py --render-book`, `--render-formats txt`, `--render-dir`. Teacher Mode subsection and knobs added to [V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md). SYSTEMS_V4, PLANNING_STATUS, specs/README, OMEGA_LAYER_CONTRACTS, COMPILED_PLAN_SCHEMA_CONTRACT, SYSTEMS_AUDIT, BOOK_001 docs updated to document Stage 6 and Teacher Mode knobs.
7. **Content coverage unblock (bindings + arcs + playbook)** — **Step 1:** Added 7 unified topics to `config/topic_engine_bindings.yaml` (overthinking, burnout, social_anxiety, financial_anxiety, imposter_syndrome, sleep_anxiety, somatic_healing); updated `config/catalog_planning/canonical_topics.yaml` so all binding topics are listed; `validate_canonical_sources.py` passes. **Step 2:** Added `scripts/generate_arcs_from_backlog.py` (batch arc generation from bindings or backlog CSV); updated `tools/arc_generator.py` with `_enforce_role_schema()` so generated arcs pass arc_loader validation (max 2 consecutive same role, ≥4 distinct roles when chapter_count≥6); generated 450 F006 arcs under `config/source_of_truth/master_arcs/` for unified personas × binding topics × allowed engines. **Step 3:** §6 Content coverage playbook in this doc (source of truth, order bindings → arcs → STORY pools, links to backlog report and CSV). REPO_FILES, SYSTEMS_V4, PHOENIX_V4_5_WRITER_SPEC, PHOENIX_V4_CANONICAL_SPEC, SYSTEMS_AUDIT updated.

**How to use:** Narrator: `run_pipeline.py ... --narrator default_narrator` or omit for brand default. KB-driven gap-fill: `python3 tools/teacher_mining/gap_fill.py --teacher <id> --gaps path/to/gaps.json --kb-dir SOURCE_OF_TRUTH/teacher_banks/<teacher>/kb`.

For release, use **specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md** (15 conditions) and **scripts/run_production_readiness_gates.py** plus simulation.

---

## 6. Content coverage playbook

**Source of truth for what’s missing:** The **backlog report** (and its CSV) is the operational source of truth. Use it to prioritize which persona×topic×engine combinations need arcs, STORY atoms, or band depth.

**Order of operations (do not start bulk content before Steps 1–2 are done):**

1. **Bindings** — Every unified topic must have an entry in `config/topic_engine_bindings.yaml`. Until then, NO_BINDING rows block.
2. **Arcs** — Generate arc YAMLs for every (persona, topic, engine, format) in scope (e.g. single canonical format F006). Use `tools/arc_generator.py` or `scripts/generate_arcs_from_backlog.py`. NO_ARC goes to 0 only when all in-scope tuples have an arc file for the chosen format policy.
3. **STORY pools by band** — Content team fills `atoms/<persona>/<topic>/<engine>/` for STORY, with band metadata. Use the report to see NO_STORY_POOL and BAND_THIN; re-run the report periodically as pools are filled.

**Artifacts:**

- **Report (unified scope):** [artifacts/reports/content_coverage_backlog_unified.md](../artifacts/reports/content_coverage_backlog_unified.md)
- **Full data CSV:** [artifacts/reports/content_coverage_backlog_unified.csv](../artifacts/reports/content_coverage_backlog_unified.csv)
