# Phoenix Omega — Data Dictionary

**Purpose:** Single reference for data structures, schemas, and all functions across the repo.  
**Authority:** Derived from specs (OMEGA_LAYER_CONTRACTS, PHOENIX_ARC_FIRST_CANONICAL_SPEC), code, and config.

---

## 1. System architecture (high level)

- **Sole system authority:** [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) — Arc-First; arc mandatory; validators structural only.
- **Pipeline:** Stage 1 (Catalog/BookSpec) → Stage 2 (FormatPlan) → Stage 3 (CompiledBook) → Stage 6 (render). Arc required for compile.
- **Handoff contracts:** [specs/OMEGA_LAYER_CONTRACTS.md](../specs/OMEGA_LAYER_CONTRACTS.md).

---

## 2. Core data structures

### 2.1 BookSpec (Stage 1 output)

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | string | Topic slug (e.g. self_worth, shame). |
| `persona_id` | string | Persona slug (e.g. nyc_executives, gen_z_professionals). |
| `series_id` | string \| null | Series slug if part of series. |
| `installment_number` | int \| null | 1..N within series. |
| `teacher_id` | string | Teacher slug. |
| `brand_id` | string | Brand slug. |
| `angle_id` | string | Angle within series/domain (required). |
| `domain_id` | string | Domain slug (e.g. anxiety_cluster). |
| `seed` | string | Determinism seed. |
| `locale` | string | e.g. en-US. |
| `territory` | string | e.g. US. |
| `teacher_mode` | bool | When true, Stage 3 uses teacher_banks. |
| `author_id` | string \| null | Pen-name author. |
| `author_positioning_profile` | string \| null | Trust posture (Writer Spec §24). |
| `narrator_id` | string \| null | Narrator slug (Writer Spec §23.5). |
| `atoms_model` | "legacy" \| "cluster" \| null | Atoms layout. |
| `program_id` | string \| null | Editorial program. |
| `worldview_id` | string \| null | Intellectual lens. |
| `concept_id` | string \| null | Topic expansion composite. |
| `depth_level` | string \| null | intro \| practical \| advanced. |
| `series_key` | string \| null | imprint\|universe\|family\|series. |
| `similarity_score` | number \| null | Near-duplicate risk. |
| `metadata_style_id` | string \| null | METADATA_LIBRARY link. |
| `release_wave_id` | string \| null | Wave/week schedule. |
| `advisory_status` | string \| null | info \| warn \| critical. |
| `human_decision` | string \| null | approve \| hold \| override. |
| `companion_workbook_type` | string \| null | full \| light_guide \| null. |

**Source:** `phoenix_v4/planning/catalog_planner.BookSpec`, `CatalogPlanner.produce_single` / `produce_wave`.

---

### 2.2 FormatPlan (Stage 2 output)

| Field | Type | Description |
|-------|------|-------------|
| `format_structural_id` | string | F001–F015. |
| `format_runtime_id` | string | standard_book, deep_book_4h, etc. |
| `tier` | string | A \| B \| C. |
| `blueprint_variant` | string | linear \| wave \| scaffold \| rupture. |
| `chapter_count` | int | Target chapters. |
| `word_target_range` | [int, int] | [min, max] words. |
| `slot_definitions` | List[List[string]] | Slot types per chapter (required for Stage 3). |
| `book_size` | string \| null | short \| medium \| long. |
| `emotional_curve_profile` | string \| null | e.g. cool_warm_hot_land. |
| `rationale` | object \| null | rules_fired, inputs_digest. |

**Source:** `phoenix_v4/planning/format_selector.FormatPlan`, `FormatSelector.select_format`.

---

### 2.3 CompiledBook (Stage 3 output)

| Field | Type | Description |
|-------|------|-------------|
| `plan_hash` | string | Deterministic hash of compiled plan. |
| `chapter_slot_sequence` | list | Slot types per chapter. |
| `atom_ids` | list | Ordered atom IDs per chapter/slot. |
| `dominant_band_sequence` | list \| null | Max BAND per chapter (STORY). |
| `arc_id` | string \| null | Arc identifier. |
| `emotional_temperature_sequence` | list \| null | Per-chapter temperature. |
| `reflection_strategy_sequence` | list \| null | From arc. |
| `exercise_chapters` | list \| null | Chapter indices with EXERCISE. |
| `slot_sig` | string \| null | Slot layout signature. |
| `freebie_bundle` | list \| null | Freebie IDs (set after Stage 3). |
| `cta_template_id` | string \| null | CTA template key. |
| `freebie_slug` | string \| null | URL slug. |
| `author_positioning_profile` | string \| null | Writer Spec §24. |
| `positioning_signature_hash` | string \| null | sha256(profile + plan_hash). |
| `compression_atom_ids` | list \| null | One per chapter when COMPRESSION slot. |
| `compression_sig` | string \| null | Placement + length signature. |
| `compression_pos_sig` | string \| null | Chapter indices with compression. |
| `compression_len_vec` | list \| null | S/M/L per chapter. |
| `emotional_role_sequence` | list \| null | Per-chapter role. |
| `emotional_role_sig` | string \| null | Compact e.g. r-d-f-s-i. |
| `atom_sources` | list \| null | teacher_native \| teacher_synthetic \| practice_fallback. |
| `chapter_archetypes` | list \| null | Chapter archetype IDs. |
| `chapter_exercise_modes` | list \| null | none \| micro \| full. |
| `chapter_reflection_weights` | list \| null | light \| standard \| heavy. |
| `chapter_story_depths` | list \| null | light \| standard \| deep. |
| `chapter_planner_warnings` | list \| null | Non-fatal policy warnings. |
| `chapter_bestseller_structures` | list \| null | Narrative shape per chapter. |
| `ending_signature` | string \| null | Final INTEGRATION + carry_line hash. |
| `carry_line` | string \| null | Chosen carry line (TTS). |
| `chapter_thesis` | dict[int, str] \| null | Keys 1..chapter_count. |
| `motif_injections` | list \| null | [{chapter_index, slot_index, phrase}]. |
| `reframe_injections` | list \| null | [{chapter_index, slot_index, line_type, text}]. |

**Source:** `phoenix_v4/planning/assembly_compiler.CompiledBook`, `compile_plan()`.

---

### 2.4 ArcBlueprint (Master Arc)

| Field | Type | Description |
|-------|------|-------------|
| `persona` | string | Persona slug. |
| `topic` | string | Topic slug. |
| `engine` | string | Engine ID. |
| `format` | string | Format ID (e.g. F006). |
| `chapter_count` | int | Target chapters. |
| `emotional_curve` | list | BAND per chapter (1–5). |
| `reflection_strategy_sequence` | list \| null | Per-chapter strategy. |
| `arc_id` | string \| null | Arc identifier. |
| (other) | — | See arc YAML schema. |

**Source:** `phoenix_v4/planning/arc_loader.ArcBlueprint`, `load_arc()`.

---

### 2.5 Persona × topic variables (template hydration)

Schema: **persona_topic_variables.schema.yaml** (root). Defines:

- **global:** persona (id, name, authority_tolerance, language_register, attention_span), topic (id, book_title, book_subtitle), core (core_sentence, current_emotional_state, desired_state, core_action, life_domain).
- **chapter_1 … chapter_12:** required_variables per chapter (e.g. time_duration, sentence_variations, moments, cost_examples for ch1; exercise slots and integration bridges where allowed).
- **validation:** global_rules, chapter_specific, safety_rules, integration_bridge_test (coexistence test).

---

## 3. Pipeline entry points and system functions

### 3.1 Main pipeline

| Entry | Path | Role |
|-------|------|------|
| Full pipeline | `scripts/run_pipeline.py` | Stage 1 → 2 → 3; arc required; optional freebie gen, render, EI V2. |
| Production gates | `scripts/run_production_readiness_gates.py` | V4.5 production readiness (14 conditions). |
| Validate golden plan | `scripts/validate_golden_plan.py` | Validates compiled plan JSON vs Stage 3 contract. |
| Book_001 readiness | `scripts/validate_book_001_readiness.py` | Pre/post compile checks (STORY, BAND, emotional curve). |
| Render plan to txt | `scripts/render_plan_to_txt.py` | Resolves atom_ids to prose; outputs QA .txt. |
| Generate arcs batch | `scripts/generate_arcs_from_backlog.py` | Batch arc generation from backlog/bindings. |

### 3.2 Dashboard and UI

| Entry | Path | Role |
|-------|------|------|
| Executive dashboard | `dashboard.py` | Streamlit; tabs: GitHub, Pearl News, Pipeline, EI v2/Marketing, System. |
| Revenue dashboard | `revenue_dashboard.jsx` | Standalone React/Recharts (one-off). |

### 3.3 Pearl News pipeline

| Entry | Path | Role |
|-------|------|------|
| Article pipeline | `pearl_news/pipeline/run_article_pipeline.py` | Assemble → expand (LLM) → validate → select image. |
| Post to WordPress | `pearl_news_post_to_wp.py` (root), `scripts/pearl_news_post_to_wp.py` | Publish article. |

### 3.4 Video pipeline

| Entry | Path | Role |
|-------|------|------|
| Video pipeline | `scripts/video/run_pipeline.py` | Full video pipeline run. |
| Render | `scripts/video/run_render.py` | Render clips (ffmpeg, captions, concat). |
| TTS narration | `scripts/video/run_tts_narration.py` | ElevenLabs TTS. |
| Shot planner | `scripts/video/run_shot_planner.py` | Shot planning from script segments. |
| Timeline builder | `scripts/video/run_timeline_builder.py` | Build timeline from shot plan. |
| QC | `scripts/video/run_qc.py` | Quality checks. |
| Asset resolver | `scripts/video/run_asset_resolver.py` | Resolve assets for shots. |
| Segment scene extraction | `scripts/video/run_segment_scene_extraction.py` | LLM scene extraction. |
| Flux bank build | `scripts/video/run_flux_bank_build.py` | Flux image bank. |
| Flux per-segment build | `scripts/video/run_flux_per_segment_build.py` | Per-segment Flux. |
| Distribution writer | `scripts/video/distribution_writer.py` | Upload/distribute to R2. |

### 3.5 Phoenix recommender

| Entry | Path | Role |
|-------|------|------|
| CLI | `phoenix_recommender/cli.py` | Score/rank candidates, explain. |
| __main__ | `phoenix_recommender/__main__.py` | Package entry. |

### 3.6 Admin portal (services)

| Entry | Path | Role |
|-------|------|------|
| App | `services/admin_portal/app.py` | Routes: admin packets page, login redirect, root. |
| API | `services/admin_portal/routes_packets.py` | api_me, api_packets, api_mint_signed_url, api_audit_recent. |

### 3.7 Simulation

| Entry | Path | Role |
|-------|------|------|
| Run simulation | `simulation/run_simulation.py` | Phase 1 (structure), optional Phase 2/3. |

---

## 4. Function index by module

### 4.1 phoenix_v4/planning

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **arc_loader** | `ArcBlueprint` | Dataclass for master arc. |
| | `load_arc(arc_path, arcs_root)` | Load and validate arc YAML. |
| | `validate_arc_schema(arc)` | Validate arc dict; return errors. |
| | `validate_arc_format_role_compat(arc, format_plan)` | Arc/format role compatibility. |
| | `resolve_arc_path`, `load_or_generate_arc` | Resolve or load/generate arc. |
| **assembly_compiler** | `CompiledBook` | Stage 3 output dataclass. |
| | `compile_plan(book_spec, format_plan_dict, arc_path, …)` | Compile BookSpec + FormatPlan + Arc → CompiledBook. |
| | `validate_canonical_atom_file(path)` | Validate CANONICAL.txt schema. |
| | `_compute_exercise_chapters`, `_compute_slot_signature` | Derived fields. |
| | `_parse_canonical_txt`, `_parse_band_from_metadata`, `_parse_narrative_metadata` | Parse atom files. |
| | `_load_story_atoms_for_persona_topic`, `_deterministic_select` | Pool load and select. |
| | `_apply_section_reorder`, `_compute_motif_reframe_injections` | Variation. |
| **catalog_planner** | `AtomsModel` | Enum: legacy, cluster. |
| | `BookSpec` | Stage 1 output dataclass. |
| | `CatalogPlanner` | Produces BookSpec from config. |
| | `book_spec_digest(spec)` | Digest string for BookSpec. |
| **format_selector** | `FormatPlan` | Stage 2 output dataclass. |
| | `FormatSelector` | (topic, persona, installment, series) → FormatPlan. |
| | `inputs_digest(...)` | Hash of Stage 2 inputs. |
| | `resolve_arc_from_angle(book_spec, default_arc_path)` | Resolve arc from angle. |
| **pool_index** | `AtomEntry` | Single atom entry. |
| | `PoolIndex` | get_pool(slot_type, persona, topic); STORY from engine dir. |
| **slot_resolver** | `ResolverContext` | Context for slot resolution. |
| | `resolve_slot(context, slot_type, selector_key, …)` | Deterministic slot selection. |
| **arc_loader** (cont.) | `_auto_generate_arc` | Auto-generate arc when missing. |
| **author_brand_resolver** | `resolve_author_from_brand(...)` | Default author from brand. |
| **author_asset_loader** | `load_author_assets(author_id, repo_root)` | Load bio, why_this_book, authority_position, audiobook_pre_intro. |
| | `load_author_registry`, `render_audiobook_pre_intro` | Registry and pre-intro render. |
| **narrator_brand_resolver** | `resolve_narrator_from_brand(brand_id)` | Default narrator from brand. |
| | `validate_narrator_for_book(narrator_id, brand_id, …)` | Validate narrator for book. |
| **teacher_brand_resolver** | `resolve_teacher_brand(topic_id, persona_id, series_id)` | (teacher_id, brand_id). |
| **teacher_matrix** | `load_teacher_matrix(path)` | Load teacher matrix YAML. |
| | `validate_teacher_assignment(matrix, teacher_id, persona_id, …)` | Validate assignment. |
| **engine_loader** | `EngineDefinition` | Engine definition dataclass. |
| | `load_engine(engine_id, engines_root)` | Load engine YAML. |
| **capability_check** | `CapabilityResult` | Result of capability check. |
| | `capability_check(book_spec, format_plan_dict, pool_index, mode)` | K-table, pool counts, achievable chapters. |
| **variation_selector** | `select_variation_knobs(...)` | Deterministic variation knobs (book_structure_id, journey_shape_id, motif_id, etc.). |
| **freebie_planner** | `plan_freebies(book_spec, format_plan_dict, compiled, arc, …)` | Freebie bundle, cta_template_id, slug. |
| | `get_freebie_bundle_with_formats(...)` | Bundle with format list. |
| **pre_intro_resolver** | `resolve_pre_intro_blocks(author_assets, brand_id, selector_key, …)` | Resolve pre-intro blocks from pattern banks. |
| | `compute_pre_intro_signature(full_pre_intro_text)` | Signature for cap/duplicate. |
| **intro_ending_caps** | `get_quarter_for_brand(brand_id)` | Quarter for brand. |
| | `load_intro_ending_config`, `load_signature_index` | Config and signature index. |
| | `check_intro_cap_and_duplicate`, `check_ending_cap_and_duplicate` | Cap/duplicate gates. |
| **intro_ending_selector** | `select_opening_style_id`, `select_integration_ending_style_id`, `select_carry_line_style_id`, `select_carry_line` | Style/carry line selection. |
| **angle_resolver** | `load_angle_registry`, `get_angle_context(angle_id)`, `resolve_arc_path(angle_id, default_arc_path, repo_root)` | Angle registry and arc path. |
| **atoms_model_loader** | `atoms_model_for_persona(persona_id)`, `is_legacy_persona(persona_id)` | Legacy vs cluster. |
| **author_cover_art_resolver** | `resolve_author_cover_art(cover_author_id, repo_root)` | Cover art base, style hint, palette. |
| **chapter_planner** | `plan_chapters(...)` | Chapter-level slot policies, archetypes, bestseller structures. |
| | `assign_bestseller_structures(chapter_count, selector_key_prefix)` | Bestseller structure IDs. |
| **practice_selector** | `get_backstop_pool(...)`, `get_practice_prose_map(store_path)` | EXERCISE backstop from practice library. |
| **ei_planning_advisory** | `run_ei_planning_advisory(...)` | EI planning advisory report (scores, boost/cut, series recs). |
| **content_quality_signals** | `load_content_quality_signals_from_file`, `signals_by_tuple_key` | Content quality signals. |
| **outcome_ingestion** | `load_historical_outcomes_from_file`, `historical_outcomes_by_key` | Historical outcomes. |
| **teacher_portfolio_planner** | `allocate_wave(...)`, `resolve_program_id`, `resolve_worldview_id`, `get_composite_score_and_band` | Teacher allocation, program/worldview. |
| **trust_metrics** | `compute_trust_metrics`, `is_trust_eligible` | Trust metrics. |
| **ei_planning_contracts** | `planning_tuple_key`, `planning_tuple_key_from_candidate`, `planning_tuple_key_from_outcome_row` | Tuple keys. |
| | `validate_historical_outcome_row`, `validate_content_quality_signal_row` | Row validation. |
| **schema_v4** | `apply_variation_defaults`, `get_plan_variation_signature` | Variation defaults and signature. |
| **wave_orchestrator** | `orchestrate(wave, …)`, `wave_ok`, `penalty` | Wave-level orchestration. |
| **series_mode_planner** | `plan_series_roadmap(...)` | Series roadmap. |
| **coverage_checker** | `run_coverage_check(atoms_root, …)` | Coverage check. |
| **angle_bias** | `score_atom`, `score_ending_atom` | Angle-based scoring. |

### 4.2 phoenix_v4/rendering

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **prose_resolver** | `PlanContext`, `RenderResult` | Context and result. |
| | `resolve_prose_for_plan(plan, …)` | Resolve atom_ids to prose map (atoms, compression, teacher). |
| **book_renderer** | `render_book(plan, output_dir, formats, …)` | Render plan to txt (and other formats). |
| | `TxtWriter` | Writes .txt output. |
| | `clean_for_delivery`, `delivery_contract_gate`, `word_count_gate`, `chapter_flow_gate_report` | Delivery and gates. |
| **rewrite_overlay** | `compute_plan_hash(plan)`, `build_rewrite_overlay(plan, recs_path, …)` | ML rewrite overlay. |

### 4.3 phoenix_v4/qa

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **validate_compiled_plan** | `validate_compiled_plan(compiled, format_plan, …)` | Structure validation (no duplicate atom IDs, emotional curve, slot parity). |
| **validate_arc_alignment** | `validate_arc_alignment(compiled, arc)` | Plan vs arc (BAND, reflection, resolution). |
| **validate_engine_resolution** | `validate_engine_resolution(arc, engine_def)` | Arc vs engine (allowed_resolution_types, peak_intensity_limit). |
| **validate_pre_intro** | `validate_pre_intro(resolved_blocks, author_id)` | Pre-intro block validation. |
| **book_pass_gate** | `validate_book_pass(plan_for_gate, atom_meta, prose_map)` | Narrative progression, claim quality. |
| **validate_teacher_exercise_share** | `validate_teacher_exercise_share(...)` | Teacher exercise share ≥ 60% when fallback. |
| **atom_metadata_loader** | `load_atom_metadata(atoms_root, persona, topic)` | Load atom metadata. |

### 4.4 phoenix_v4/gates

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **check_tuple_viability** | `TupleViabilityResult` | status, errors. |
| | `check_tuple_viability(persona, topic, engine, format_id, …)` | Hard entry gate before Stage 1. |
| **check_creative_quality_v1** | `evaluate_book`, `evaluate_arc_motion`, `evaluate_transformation_density`, etc. | Creative quality metrics. |

### 4.5 phoenix_v4/teacher

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **teacher_config** | `load_teacher_config(teacher_id)` | Load teacher config. |
| **doctrine_fingerprint** | `fingerprint_doctrine(obj)`, `load_doctrine_yaml(path)`, `canonicalize_doctrine` | Doctrine fingerprint for CI. |
| **coverage_gate** | `run_coverage_gate(book_spec, format_plan_dict, arc, …)` | Teacher coverage gate (required slots). |
| | `compute_required_slots`, `compute_available_teacher_atoms`, `make_gap_report` | Coverage helpers. |

### 4.6 phoenix_v4/quality (ei_v2, etc.)

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **ei_v2/hybrid_selector** | `hybrid_select(...)` | V1+V2 hybrid slot selection. |
| **ei_v2/tts_readability** | `score_tts_readability(text, …)` | TTS readability score. |
| **ei_v2/semantic_dedup** | `detect_semantic_duplicates(candidates, …)` | Semantic duplicate detection. |
| **ei_v2/safety_classifier** | `classify_safety(text, …)` | Safety classification. |
| **ei_v2/research_lexicons** | `get_research_signals(...)` | Research signals. |
| **ei_v2/marketing_lexicons** | (cache, validation, load) | Marketing lexicons. |
| **ei_v2/research_sales_features** | `get_research_sales_features(...)` | Research/sales features. |
| **transformation_heatmap** | `run_heatmap_from_path`, `compute_signals`, `ending_check` | Transformation heatmap. |
| **memorable_line_detector** | `detect_lines(chapters, …)`, `run_memorable_from_path` | Memorable line detection. |
| **quality_bundle_builder** | `run_transformation`, `run_memorable_lines`, `run_marketing_assets`, `compute_csi`, `write_bundle` | Quality bundle. |
| **story_atom_lint** | `lint_story`, `lint_canonical_file` | Story atom lint. |
| **teacher_integrity** | `compute_teacher_integrity_penalty` | Teacher integrity penalty. |

### 4.7 phoenix_v4/ops

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **church_loader** | `load_church(brand_id)`, `get_church_display_name(brand_id)` | Church/brand loader. |

### 4.8 pearl_prime

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **modular_format_freeze** | `FreezeSettings`, `load_freeze_settings(path)` | V4 freeze settings. |
| | `allowed_output_formats(settings)`, `require_valid_output_format(id, settings)` | Output format validation. |
| | `apply_output_format_to_plan(format_plan_dict, output_format_id, …)` | Apply modular output format to plan. |

### 4.9 pearl_news (pipeline, publish, research_kb)

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **pipeline/article_assembler** | `assemble_articles(...)` | Assemble articles from config/templates. |
| **pipeline/llm_expand** | `expand_article_with_llm(...)`, `run_expansion(...)` | LLM expansion (commentary, explainer, youth feature, etc.). |
| **pipeline/template_selector** | `select_templates(...)` | Template selection. |
| **pipeline/topic_sdg_classifier** | `classify_sdgs(text, …)` | SDG classification. |
| **pipeline/news_action_resolver** | `select_exercise_from_bank`, `resolve_news_actions`, `render_news_action_block` | Exercise selection and news actions. |
| **pipeline/quality_gates** | `run_quality_gates(...)` | Quality gates on article. |
| **pipeline/run_article_pipeline** | `main()` | Full article pipeline. |
| **pipeline/feed_ingest** | `load_feed_config`, `ingest_feeds` | Feed config and ingest. |
| **pipeline/teacher_resolver** | `resolve_teacher`, `format_teacher_atoms_for_prompt` | Teacher resolution. |
| **publish/wordpress_client** | `post_article(...)` | WordPress publish. |
| **research_kb/retrieval** | `query_kb`, `get_research_excerpt`, `get_all_entries_for_ei_v2` | KB query and excerpt. |

### 4.10 scripts (selected)

| Script / Module | Key functions |
|-----------------|---------------|
| **run_pipeline.py** | `main()`, `resolve_to_canonical(aliases_path, topic_id, persona_id)`, `_upsert_plan_index_row` |
| **run_production_readiness_gates.py** | `gate(...)`, `main()` |
| **video/run_render.py** | `_render_clip`, `_concat_clips`, `_mix_narration_and_music`, `main` |
| **video/run_tts_narration.py** | `run_tts`, `_synthesize`, `main` |
| **video/run_shot_planner.py** | `run_shot_planner(script_segments, content_type)` |
| **video/run_timeline_builder.py** | `build_timeline(shot_plan, resolved, aspect_ratio)` |
| **video/run_qc.py** | `run_qc(...)` |
| **video/run_asset_resolver.py** | `run_asset_resolver(...)` |
| **video/run_segment_scene_extraction.py** | `run_extraction(...)` |
| **video/distribution_writer.py** | `_upload_batch`, `_write_daily_batch`, `main` |
| **video/write_metadata.py** | `_build_platform_metadata`, `main` |
| **release/export_brand_packets.py** | `_plan_to_manifest_row`, `_release_day_for_brand`, `main` |
| **release/notify_brand_admins.py** | `_send_email`, `_send_slack`, `main` |
| **release/sync_packets_to_portal_index.py** | `main` |
| **release/upload_brand_packets_r2.py** | `main` |
| **queue_orchestrator/queue_master.py** | `load_yaml`, `get_redis`, `main` |
| **queue_orchestrator/worker.py** | `run_job`, `main` |
| **queue_orchestrator/requeue_stale.py** | `main` |
| **audit/run_truth_audit.py** | `get_repo_state`, `write_*` (missing, drift, ledger, report), `main` |
| **audit/validate_truth_artifacts.py** | `get_current_main_sha`, `validate_report`, `validate_csv`, `main` |
| **ci/check_platform_similarity.py** | `plan_id`, `teacher_id`, `arc_id`, `slot_signature`, jaccard/LCS helpers, `main` |
| **ci/update_similarity_index.py** | `append_to_index(plan, index_path, …)` |
| **ci/run_prepublish_gates.py** | `main` |
| **localization/run_locale_batches.py** | `worker_teacher_shard`, `worker_validate`, `main` |

### 4.11 tools

| Module | Key functions |
|--------|----------------|
| **arc_generator** | `generate_arc(...)` | Generate arc from template. |
| **teacher_mining/build_kb.py** | `build_index(teacher_id, …)` | Build KB index. |
| **teacher_mining/gap_fill.py** | `run_gap_fill(...)` | Gap-fill from gaps JSON. |
| **teacher_mining/mine_kb_to_atoms.py** | `mine(...)` | Mine KB to candidate atoms. |
| **teacher_mining/intake_normalize.py** | `run_intake(...)` | Intake and normalize. |
| **teacher_mining/normalize_story_atoms.py** | `normalize_story`, `run_normalization` | Normalize story atoms. |
| **teacher_mining/normalize_exercise_atoms.py** | `normalize_exercise`, `run_normalization` | Normalize exercise atoms. |
| **teacher_mining/expand_story_atoms.py** | `expand_atom`, `run_expansion` | Expand story atoms. |
| **teacher_mining/identify_core_teachings.py** | `run_identification`, `write_core_teachings_yaml` | Core teachings. |
| **approval/approve_atoms.py** | `approve_atom`, `list_candidates`, `find_candidate` | Approve teacher atoms. |
| **exercise_approval/exercise_approve.py** | `cmd_approve`, `cmd_reject` | Exercise approve/reject. |
| **phoenix_v4/tools/generate_html_freebie.py** | `generate_html_freebie(...)` | Generate HTML freebie. |

### 4.12 phoenix_recommender

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **candidate_generator** | `generate_candidates()`, `load_canonical_personas`, `load_canonical_topics` | Generate candidates. |
| **feature_builder** | `build_feature_vector(candidate)`, `build_*_feature` (market_demand, coverage_gap, …) | Feature vector. |
| **scoring_model** | `score_candidate(...)`, `compute_score`, `load_scoring_config` | Score candidate. |
| **ranker** | `rank_candidates(scored_candidates, top_n)`, `apply_*_constraints` | Rank with constraints. |
| **recommendation_report** | `generate_reports(ranked_candidates, output_dir)` | JSON + Markdown reports. |
| **cli** | `main`, `score_all_candidates`, `print_ranking_summary`, `explain_candidate` | CLI. |

### 4.13 services/admin_portal

| Module | Function / Class | Description |
|--------|-------------------|-------------|
| **app** | `admin_packets_page`, `admin_login_redirect`, `root` | Page routes. |
| **routes_packets** | `api_me`, `api_packets`, `api_mint_signed_url`, `api_audit_recent` | API routes. |
| **models** | `get_conn`, `init_db`, `user_by_email`, `user_grants`, `packets_for_week`, `upsert_packet`, `insert_audit`, `recent_audit`, `ensure_user_and_grants` | DB access. |
| **auth** | `get_request_email` | Auth helper. |

---

## 5. Config and schema locations

| Purpose | Location |
|---------|----------|
| Stage 1 (catalog) | config/catalog_planning/ — domain_definitions.yaml, series_templates.yaml, capacity_constraints.yaml, brand_archetype_registry.yaml, teacher_persona_matrix.yaml, brand_teacher_assignments.yaml, brand_author_assignments.yaml |
| Stage 2 (format) | config/format_selection/ — format_registry.yaml, selection_rules.yaml, k_tables/ |
| Identity aliases | config/identity_aliases.yaml (persona_aliases, topic_aliases) |
| Topic/engine | config/topic_engine_bindings.yaml, config/topic_skins.yaml |
| Authors/narrators | config/author_registry.yaml, config/brand_author_assignments.yaml, config/narrators/narrator_registry.yaml, config/brand_narrator_assignments.yaml |
| Teachers | config/teachers/teacher_registry.yaml; SOURCE_OF_TRUTH/teacher_banks/ |
| Master arcs | config/source_of_truth/master_arcs/ |
| Engines | config/source_of_truth/engines/ |
| Exercises | SOURCE_OF_TRUTH/exercises_v4/registry.yaml, approved/; config/practice/selection_rules.yaml |
| Freebies | config/freebies/freebie_registry.yaml, freebie_selection_rules.yaml |
| Persona/topic variables | persona_topic_variables.schema.yaml (root) |
| Video | config/video/ (cross_video_dedup, brand_style_tokens, motion_policy, caption_policies, etc.) |

---

## 6. Slot types and atom roles

- **Story roles (frozen):** RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT (Canonical §5.3).
- **Slot types (examples):** HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION, COMPRESSION (format-dependent).
- **BAND:** 1–5 emotional intensity per STORY block (metadata in CANONICAL.txt).

---

## 7. Naming and conventions

- **plan_hash:** Deterministic hash of compiled plan (input + structure).
- **selector_key:** Deterministic key for pool selection (e.g. SHA256-based); no reuse within scope.
- **canonical IDs:** persona_id, topic_id as atoms dir names; alias resolution before Stage 3 (config/identity_aliases.yaml).
- **book_id / plan_id:** Typically same as plan_hash for compiled output.

---

*Generated from repo scan and specs. Update when adding new modules or changing contracts.*
