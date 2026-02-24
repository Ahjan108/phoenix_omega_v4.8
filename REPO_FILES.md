# Repo file list (with descriptions)

**System architecture (sole authority):** [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) — Arc-First Reset Canonical Dev Spec v1.1. Arc mandatory; validators structural only; no quality-simulation layers. Older and superseded docs are in `archive/`.

---

## Root

| File | Description |
|------|-------------|
| **ONBOARDING.md** | Onboarding for writers/content leads; points to canonical spec and (when added) `docs/writing/`. |
| **REBUILD_README.txt** | Rebuild pipeline: story-atom roles, cadence, exercise schema, approval, forbidden resolution. |
| **PHOENIX_V4_5_COMPLETE_FORMAT_SPEC.docx** | Human-reference format portfolio (14 formats, tiers); simulation uses `simulation/config/v4_5_formats.yaml`. |
| **persona_topic_variables.schema.yaml** | Schema for persona/topic variables used in assembly or mining. |
| **phoenix_rebuild_spec.txt** | Rebuild/spec notes. |
| **v4_system_up_spec.txt** | V4 system update notes. |
| **brand_registry.txt** | Brand/positioning registry. |
| **c_authors.txt** | Author list or constraints. |
| **c_rollout_scale.txt** | Rollout scale notes. |
| **c_somatic_exercise_apps.txt** | Somatic exercise app list/constraints. |
| **chat_system_reqs.txt** | Chat system requirements. |
| **exercise_yaml_helper.txt** | Helper notes for exercise YAML. |
| **somatic_exercises.txt** | Somatic exercise list/descriptions. |
| **story_stakes.txt** | Story stakes reference. |
| **unified_personas.txt** | Unified persona definitions. |
| **revenue_dashboard.jsx** | Standalone React/Recharts revenue dashboard (one-off; not part of Phoenix pipeline). |

---

## config/

V4 topic and engine configuration at repo root. Used by bindings/skins and pipeline.

| File | Description |
|------|-------------|
| **config/topic_engine_bindings.yaml** | Which engines/roles are allowed per topic (anxiety, boundaries, financial_stress, courage, compassion_fatigue, depression, self_worth, grief). |
| **config/topic_skins.yaml** | Topic vocabulary guard: prohibited terms, suffixes per role, topic overrides. |

**config/catalog_planning/** — Stage 1 (catalog planner): domain_definitions.yaml, series_templates.yaml, capacity_constraints.yaml, **brand_archetype_registry.yaml** (v1.1, 24 archetypes), teacher_persona_matrix.yaml, **brand_teacher_assignments.yaml** (teacher/brand when not supplied). See specs/OMEGA_LAYER_CONTRACTS.md. **config/author_registry.yaml** — Pen-name authors (author_id, positioning_profile, assets_path); Writer Spec §23–§24. **config/brand_author_assignments.yaml** — default_author per brand when --author not supplied; resolved by phoenix_v4/planning/author_brand_resolver.py. **config/narrators/narrator_registry.yaml** — Narrator registry (Writer Spec §23.5). **config/brand_narrator_assignments.yaml** — default_narrator per brand; phoenix_v4/planning/narrator_brand_resolver.py.

**config/teachers/** — Teacher Mode V4: teacher_registry.yaml (one entry per teacher; allowed_topics, allowed_engines, teacher_mode_defaults). See specs/TEACHER_MODE_V4_CANONICAL_SPEC.md and config/teachers/README.md.

**SOURCE_OF_TRUTH/teacher_banks/** — Per-teacher raw, kb, doctrine, candidate_atoms, approved_atoms (Teacher Mode V4). **ahjan:** intake from intake_teacher/; run `scripts/intake_teacher_ahjan.py` and `tools/teacher_mining/build_kb.py --teacher ahjan`. **tools/teacher_mining/gap_fill.py** — Gap-fill from gaps JSON (report_teacher_gaps); optional **--kb-dir** for KB-driven candidate body (index.json documents[].text or *.txt); body prefixed with [KB draft — review and edit before approval]; report includes kb_driven, kb_docs_used.

**SOURCE_OF_TRUTH/exercises_v4/** — V4 somatic exercise registry: registry.yaml (11 types, slot_07_practice, selection rules), candidate/_stubs/ (minimal stubs per type), approved/ (runtime source). See SOURCE_OF_TRUTH/exercises_v4/README.md and exercise_yaml_helper.txt.

**config/format_selection/** — Stage 2 (format selector): format_registry.yaml (structural F001–F015 + runtime classes, default_slot_definitions), selection_rules.yaml (topic complexity, persona constraints, blueprint rotation). **config/format_selection/k_tables/** — K-tables per format (e.g. F006.yaml): k_min per slot type for capability check and achievable chapter count. **config/identity_aliases.yaml** — persona_aliases and topic_aliases; resolve to canonical (atoms dir names) before Stage 3. Pipeline resolves; Stage 3 does not. **config/source_of_truth/master_arcs/** — Arc-First: Master Arc YAMLs (persona__topic__engine__format.yaml). **config/source_of_truth/engines/** — Engine definition YAMLs (allowed_resolution_types, peak_intensity_limit, etc.); see specs/ENGINE_DEFINITION_SCHEMA.md.

---

## phoenix_v4/

V4 plan/QA code. **Stage 1:** `phoenix_v4/planning/catalog_planner.py` — BookSpec from config/catalog_planning/ (produce_single, produce_wave). **Author resolution:** `phoenix_v4/planning/author_brand_resolver.py` — resolve default_author from config/brand_author_assignments.yaml when --author not supplied; `phoenix_v4/planning/author_asset_loader.py` — load bio, why_this_book, authority_position, audiobook_pre_intro from assets/authors/ or registry assets_path; pipeline fails if assets missing (§23.9). **Narrator resolution:** `phoenix_v4/planning/narrator_brand_resolver.py` — resolve default_narrator from config/brand_narrator_assignments.yaml; validate_narrator_for_book for brand/topic/status. **Stage 2:** `phoenix_v4/planning/format_selector.py` — deterministic (topic, persona, installment, series) → FormatPlan. CLI: `python3 -m phoenix_v4.planning.format_selector --topic <id> --persona <id> [--installment N] [--out plan.json]`. Config: config/format_selection/. **Stage 3 (Plan Compiler):** `phoenix_v4/planning/assembly_compiler.py` — FormatPlan + BookSpec + **Arc** → CompiledBook (Arc-First: arc required; no arc = no compile). Uses PoolIndex and slot_resolver; filters STORY by arc emotional_curve BAND. **phoenix_v4/planning/arc_loader.py** — load and validate arc YAML (structural only). **phoenix_v4/planning/engine_loader.py** — load engine definition YAML. **phoenix_v4/qa/validate_arc_alignment.py** — plan vs arc (BAND, reflection strategy, cost chapter, resolution_type). **phoenix_v4/qa/validate_engine_resolution.py** — arc vs engine (allowed_resolution_types, peak_intensity_limit, identity_shift). **phoenix_v4/planning/capability_check.py** — K-table load, pool counts, achievable chapter count, strict/relaxed mode. **phoenix_v4/planning/pool_index.py** — get_pool(slot_type, persona, topic) for all slot types; STORY from atoms/…/engine/CANONICAL.txt, others from atoms/…/\<slot_type\>/CANONICAL.txt when present. **phoenix_v4/planning/slot_resolver.py** — resolve_slot (SHA256 selector key, no reuse). **phoenix_v4/qa/validate_compiled_plan.py** — validate_compiled_plan(plan, format_plan): no duplicate atom IDs, emotional curve (≥6 chapters), slot sequence parity with slot_definitions. **phoenix_v4/qa/validate_brand_archetype_registry.py** — CI gate: validate config/catalog_planning/brand_archetype_registry.yaml (structural rules per specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md). Run: `PYTHONPATH=. python3 phoenix_v4/qa/validate_brand_archetype_registry.py`. Tests: `tests/test_format_selector.py`. Emotional curve golden: `tests/golden/emotional_curve_fixture.yaml` and test-only atoms under `tests/fixtures/atoms`; `tests/test_emotional_curve_golden.py`. **QA:** phoenix_v4/qa/emotional_governance_rules.yaml.

---

## registry/

Section and pack registries (e.g. grief section pack). Pipeline can point `SECTIONS_REGISTRY_FILE` here.

| File | Description |
|------|-------------|
| **registry/registry_grief.yaml** | Grief pack — rewritten section variants for grief/loss topic. |

---

## atoms/

Canonical story atoms by persona, topic, and engine. Path: `atoms/<persona>/<topic>/<engine>/CANONICAL.txt`. Personas: educators, nyc_executives, healthcare_rns, gen_alpha_students, gen_z_professionals. Used for assembly and coverage.

---

## get_these/

Staging folder; contents have been moved to **config/**, **registry/**, and **atoms/**. See `get_these/README.md` for the mapping. New drops can go here, then be ingested into the same layout.

---

## talp/

**Staging for mining.** Source material (TE_*, CP_*, gen_alpha_*_complete.txt, plus GEN_ALPHA_COMPLETE_SUMMARY.md and a legacy SYSTEMS_DOCUMENTATION.md) before mining into atoms. Not ingested as-is; pipeline: mine → atoms → lint → candidate → approval. See `talp/README.md`.

**talp/analyze_intake/extracted_docx/** — Phase 1: .docx extracted to markdown (TTS_PROSE_GUIDE, EMOTIONAL_IMPACT_SPEC, SOMATIC_WRITER_SPEC) for diff and merge into Writer Spec. See extracted_docx/README.md.

---

## old_chats/

Exported/saved HTML (UUID-named). Kept for reference; not part of the Phoenix pipeline. See `old_chats/README.md`.

---

## .zencoder/

| File | Description |
|------|-------------|
| **.zencoder/rules/repo.md** | Repo-level rules for Zencoder/tooling. |

---

## archive/

Superseded docs; reference only. Do not use for implementation.

| File | Description |
|------|-------------|
| **archive/README.md** | Explains archive; points to canonical spec. |
| **archive/PHOENIX_OMEGA_V4_COMPLETE_SPEC (1).md** | Old complete spec; superseded by `specs/PHOENIX_V4_CANONICAL_SPEC.md`. |
| **archive/SYSTEMS_DOCUMENTATION (3).md** | Old systems doc; superseded. |
| **archive/V4_SPEC_RECONCILIATION.md** | Old reconciliation; folded into canonical spec. |
| **archive/SCENE_INJECTION_ARCHITECTURE.md** | Legacy scene-socket spec; SCENE rules now in Writer Spec §4.2 and Canonical Spec. |
| **archive/specs_originals/*.docx** | Original .docx exports (Beat Map, Format Portfolio, Infrastructure, Reconciliation). |

---

## scripts/

| File | Description |
|------|-------------|
| **scripts/run_production_readiness_gates.py** | Runs V4.5 Production Readiness (14 conditions): spec/config/registry/atoms existence, governance YAML structure, FMT spec. From repo root: `python scripts/run_production_readiness_gates.py`. Follow with `simulation/run_simulation.py --n 10 --phase2 --phase3` for Gate 12. |
| **scripts/validate_golden_plan.py** | Validates compiled plan JSON against Stage 3 contract (plan_hash, chapter_slot_sequence, atom_ids). Usage: `python scripts/validate_golden_plan.py [path/to/plan.json]`. See `artifacts/golden_plans/README.md`. |
| *Stage 2 CLI* | Format selector: `python3 -m phoenix_v4.planning.format_selector --topic <id> --persona <id> [--installment N] [--out plan.json]`. See phoenix_v4/planning/format_selector.py. |
| **scripts/run_pipeline.py** | Full pipeline: Stage 1 (catalog) → Stage 2 (format selector) → Stage 3 (assembly compiler). `python scripts/run_pipeline.py --topic <id> --persona <id> [--out path.plan.json]` or `--input example_input_stage2.yaml`. |
| **scripts/validate_book_001_readiness.py** | Book_001 readiness: pre-compile (STORY count, BAND presence/diversity, duplicate IDs) and post-compile emotional curve (`--plan <path>`: ≥3 distinct BAND, no >3 consecutive same). See docs/BOOK_001_READINESS_CHECKLIST.md. |
| **scripts/render_plan_to_txt.py** | Renders a compiled plan JSON to a single .txt for QA: resolves STORY atom_ids to prose from CANONICAL.txt; other slots as placeholders. `python scripts/render_plan_to_txt.py <plan.json> -o <out.txt>`. Outputs typically in `artifacts/books_qa/`. |

---

## artifacts/

Simulation outputs (generated).

| File | Description |
|------|-------------|
| **artifacts/simulation_1k.json** | Phase 1 simulation results (1k books). |
| **artifacts/simulation_1k_phase2.json** | Phase 1+2 results. |
| **artifacts/simulation_1k_phase3.json** | Phase 1+2+3 results. |
| **artifacts/golden_plans/** | Stage 3 API freeze: example_input.yaml, example_input_stage2.yaml, example_format_plan.json (Stage 2 output), optional *.plan.json from plan compiler. Same input → same plan_hash/sequences. Validate with `scripts/validate_golden_plan.py`. See golden_plans/README.md. |
| **artifacts/book_001.plan.json**, **book_002.plan.json**, **book_003.plan.json** | Compiled 12-chapter plans (nyc_executives × self_worth, seeds book001/book002/book003). All pass emotional curve validation. See artifacts/THREE_BOOK_STRESS_TEST.md. |
| **artifacts/books_qa/** | QA book text files: one .txt per plan, STORY prose resolved from CANONICAL.txt; produced by `scripts/render_plan_to_txt.py`. |
| **artifacts/THREE_BOOK_STRESS_TEST.md** | Summary: compile status, STORY overlap, BAND curves, and next steps (Book_004/005, second persona) for the nyc_executives × self_worth lane. |

---

## content/

Master scripts and long-form content; **mining source only** (plan: move to `source_material/`). Not ingested as-is; mined into HOOK, REFLECTION, EXERCISE, INTEGRATION, SCENE atoms.

| Pattern | Description |
|---------|-------------|
| **content/01_*.md … 11_*.md** | Numbered topic scripts (e.g. introduction, awareness, decompression, action, perspective, tribe, digital wellness, work/money, conclusion). |
| **content/02_*.md … 07_*.md** | Persona/topic scripts (e.g. burnout_tech, cofounder_founders, politics_mgmt, layoff_fear_mgmt). |
| **content/CP_01 … CP_11** | Creative professional series. |
| **content/FR_01 … FR_08** | First responder series. |
| **content/GEN_ALPHA_*.md, gen_alpha_*.txt** | Gen Alpha summaries/complete scripts. |
| **content/HN_01 … HN_08** | Healthcare worker series. |
| **content/PT_01 … PT_08** | Physical therapy series. |
| **content/TE_01 … TE_08** | Teacher series. |

---

## simulation/

Phase 1 (structure), Phase 2 (waveform/arc/drift), Phase 3 (content/emotional force). Run: `python run_simulation.py [--phase2] [--phase3]`.

| File | Description |
|------|-------------|
| **simulation/README.md** | How to run; formats/tiers; Phase 1/2/3 summary. |
| **simulation/SIMULATION_PHASE2_SCOPE.md** | Phase 2 scope: waveform, arc, drift. |
| **simulation/PHASE3_MVP.md** | Phase 3 MVP: volatility, cognitive balance, consequence, reassurance. |
| **simulation/run_simulation.py** | CLI; generates requests, runs Phase 1 (optional 2/3), writes artifacts. Use `--use-format-selector` to derive format from Stage 2 (topic+persona+installment). |
| **simulation/simulator.py** | Plan compiler, format config loader, Phase 1 validation matrix. |
| **simulation/phase2.py** | Synthetic metadata, waveform/arc/drift validation. |
| **simulation/phase3_mvp.py** | Content heuristics on chapter text (four engines). |
| **simulation/config/v4_5_formats.yaml** | Format definitions (chapters, parts, slots, tier). |
| **simulation/config/validation_matrix.yaml** | Tier rules (misfire, silence, interrupt, flinch, volatility quotas, etc.). |
| **simulation/config/emotional_temperature_curves.yaml** | Per-format temperature curves (cool/warm/hot/land) and volatility/landing requirements. |
| **simulation/requirements.txt** | Python deps for simulation. |

---

## somatic_exercise_freebee_apps/

Standalone HTML apps for somatic/breathing exercises (e.g. 478, box breathing, coherence). **app** vs **ex** naming; used as freebie/embed assets.

| Pattern | Description |
|---------|-------------|
| **app*.html** | App-style exercise UIs. |
| **ex*.html** | Exercise-style UIs. |

---

## specs/

| File | Description |
|------|-------------|
| **specs/README.md** | Spec index; Arc-First Canonical is sole system authority. |
| **specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md** | **CANONICAL (v1.1):** Arc-First Reset — arc mandatory, engine overlay, atom pools; structural validators only; migration rule; repo action diff. Sole governing architecture. |
| **specs/PHOENIX_V4_CANONICAL_SPEC.md** | Reference: atom taxonomy, formats, beat maps; superseded for system architecture by Arc-First Canonical. |
| **specs/PHOENIX_V4_5_WRITER_SPEC.md** | **Writer spec (TTS-locked):** prose, Six Atom Types, emotional QA, governance, tests; **§23** Identity & Audiobook Governance. |
| **specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md** | CI rules for brand archetype registry (structural, vocabulary, voice, pricing); fail at plan time. |
| **specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md** | Go/no-go: 15 conditions for V4.5 production-ready. |
| **specs/V4_6_BINGE_OPTIMIZATION_LAYER.md** | Forward Momentum Trigger (FMT); full books end with open hook for binge/continuation. |
| **specs/WRITER_DEV_SPEC_PHASE_2.md** | Coverage-aligned inventory expansion; coverage_report, exercise_coverage, compile_strict; writer production rules. |
| **specs/OMEGA_LAYER_CONTRACTS.md** | Stage 1→2→3 handoff schemas (BookSpec, FormatPlan, CompiledBook); config locations. |
| **specs/TEACHER_MODE_V4_CANONICAL_SPEC.md** | Teacher Mode V4 dev spec: teacher_banks, KB gap-fill (offline), Arc-First compatible; pool precedence, gap report, approval. |
| **specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md** | Content team workflow for Teacher Mode: onboard teacher, build KB, report gaps, gap-fill, approve, compile. |

---

## docs/

| File | Description |
|------|-------------|
| **docs/PLANNING_STATUS.md** | System-wide doc status; what's left for 100% planning; freebies/authors/narrators planning summary. Linked from specs/README and talp/SYSTEMS_DOCUMENTATION. |
| **docs/BOOK_001_*** | Book_001 assembly contract, freeze, readiness checklist, post-mortem, writer brief. |
| **docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml** | Somatic book assembly: 10-slot contract, exercise cadence, emotional curve template; structure only. |
| **docs/authoring/AUTHOR_ASSET_WORKBOOK.md** | Pen-name author assets (bio, why_this_book, authority_position, audiobook_pre_intro); Writer Spec §23; pipeline loads via author_asset_loader; freebie placeholders. |
| **assets/authors/README.md** | Author asset directory layout and template placeholders; pipeline loads from here or registry assets_path. |
| **docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md** | Persona micro-stakes, environmental cues, promotion (provisional_template → confirmed). |

---

## Removed during cleanup

- **Root zip archives** (`files.zip`, `files (1).zip` … `files (12).zip`, `filesa.zip`, `files (1)a.zip`, `files (2)a.zip`) — redundant/versioned bundles.
- **content/files (6).zip, (7).zip, (8).zip** — same; removed from content.
