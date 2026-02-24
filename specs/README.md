# Phoenix Specs

**Canonical systems doc (whole V4 in one place):** [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md) — single description of the full V4 system, pipeline, Teacher Mode, CI, and **what’s still to do to finish the whole system**.

**System architecture (sole authority):** [PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](./PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) — Arc-First Reset Canonical Dev Spec v1.1. This is the only governing architecture. All compiles require an arc; validators are structural only; no quality-simulation layers. Supersedes prior V4/V4.6 canonical and experiential governance docs.

**Planning status (all docs, 100% planning gaps, freebies/authors/narrators):** [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md)

**Still to do (whole system):** See [../docs/SYSTEMS_V4.md § Remaining to finish](../docs/SYSTEMS_V4.md#remaining-to-finish-whole-system) and [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md). Each spec below that is part of the system includes a *Still to do* section pointing to those docs.

**System audit (all functions working):** [../docs/SYSTEMS_AUDIT.md](../docs/SYSTEMS_AUDIT.md) — entry points, pipeline, CI/QA, tools; environment (venv/PyYAML); gate 16 (freebie density) data note.

| Spec | Audience | Purpose |
|------|----------|---------|
| [PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](./PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) | **Developers** | **CANONICAL.** Arc mandatory, engine overlay, atom pools; arc validation (structural only); migration rule; repo action diff (delete/modify/add). |
| [PHOENIX_V4_5_WRITER_SPEC.md](./PHOENIX_V4_5_WRITER_SPEC.md) | **Writers** | Prose, TTS rules, Six Atom Types, emotional force, governance, tests; **§23** Identity & Audiobook (pen-name authors, narrator pre-intro, persona specificity). Content rules; structure follows Arc-First Canonical. |
| [PHOENIX_V4_CANONICAL_SPEC.md](./PHOENIX_V4_CANONICAL_SPEC.md) | **Reference** | Superseded for system architecture by Arc-First Canonical. Retained for atom taxonomy, format/slot reference until fully migrated. |
| [V4_5_PRODUCTION_READINESS_CHECKLIST.md](./V4_5_PRODUCTION_READINESS_CHECKLIST.md) | **Release** | Go/no-go conditions before production. |
| [V4_6_BINGE_OPTIMIZATION_LAYER.md](./V4_6_BINGE_OPTIMIZATION_LAYER.md) | **System** | Forward Momentum Trigger (FMT); binge/continuation. |
| [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md) | **Developers** | Stage 1→2→3 handoff schemas (BookSpec, FormatPlan, CompiledBook); config locations. |
| [WRITER_DEV_SPEC_PHASE_2.md](./WRITER_DEV_SPEC_PHASE_2.md) | **Dev** | Coverage, compile_strict; writer production rules. |
| [ARC_AUTHORING_PLAYBOOK.md](./ARC_AUTHORING_PLAYBOOK.md) | **Arc authors** | How to design arcs that don't break the system; design sequence, failure modes, scale strategy. |
| [ENGINE_DEFINITION_SCHEMA.md](./ENGINE_DEFINITION_SCHEMA.md) | **Dev / config** | Engine YAML structure; allowed_resolution_types, engine–arc compatibility; prevents resolution conflicts. |
| [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](./PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) | **Dev / Writers** | Narrative Depth Layer v1.0: invisible_script HOOK, belief_flip STORY pattern, SCENE micro-failure, milestone_type INTEGRATION, arc quality test. Additive and advisory only; subordinate to Arc-First Canonical. |
| [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md) | **Developers** | Teacher Mode V4: teacher_banks, KB-sourced gap-fill (offline), Arc-First compatible; BookSpec extensions, pool precedence, gap report, approval. Subordinate to Arc-First Canonical. |
| [TEACHER_MODE_NORMALIZATION_SPEC.md](./TEACHER_MODE_NORMALIZATION_SPEC.md) | **Dev / Pipeline** | Normalization (STORY/EXERCISE), structural entropy CI, platform similarity gate, style IDs. |
| [DUPE_EVAL_SPEC.md](./DUPE_EVAL_SPEC.md) | **Dev / Release** | DupEval: pre-publish structural similarity (CTSS/TSS/MSS), thresholds, wave density, index. |
| [COMPILED_PLAN_SCHEMA_CONTRACT.md](./COMPILED_PLAN_SCHEMA_CONTRACT.md) | **Dev / CI** | Minimum compiled plan schema for entropy, similarity, wave CI; recommendation to emit slot_sig and exercise_chapters. |
| [PRACTICE_ITEM_SCHEMA.md](./PRACTICE_ITEM_SCHEMA.md) | **Dev / Pipeline** | Practice item schema, store layout (SOURCE_OF_TRUTH/practice_library), EXERCISE backstop, teacher fallback reference. |
| [TEACHER_MODE_AUTHORING_PLAYBOOK.md](./TEACHER_MODE_AUTHORING_PLAYBOOK.md) | **Content / Ops** | Content team workflow: onboard teacher, build KB, report gaps, gap-fill, approve, compile. |
| [BRAND_ARCHETYPE_VALIDATOR_SPEC.md](./BRAND_ARCHETYPE_VALIDATOR_SPEC.md) | **Dev / CI** | CI rules for brand archetype registry: structural, vocabulary, voice, pricing; fail at plan time. |
| [PHOENIX_FREEBIE_SYSTEM_SPEC.md](./PHOENIX_FREEBIE_SYSTEM_SPEC.md) | **Dev / Pipeline** | Freebie planning & attachment + **V4 Immersion Ecosystem:** registry (all immersion types, video/MP4 deferred), deterministic planner (post–Stage 3), CTAs, density gate, CTSS; pipeline maintains plan rows in artifacts/freebies/index.jsonl and renderer logs artifacts in artifacts/freebies/artifacts_index.jsonl; canonical topics/personas, asset pipeline (plan_freebie_assets, create_freebie_assets, validate_asset_store), multi-format store, publish_dir, tier_bundles. |

**Unified Personas (catalog source of truth):** [../unified_personas.md](../unified_personas.md) — single source of truth for **active** personas (10) and **active** topics (12). Pipeline, config, and catalog planning use only persona/topic IDs listed there. Legacy IDs (e.g. nyc_executives, educators) are inactive. Design foundation (mechanism, arc roles, scaling) is in Part 0; Part 1–2 are persona registry and topic registry; Parts 3–6 are catalog math, template requirements, consumer language map, production sequence. **Config:** `config/catalog_planning/canonical_personas.yaml` and `canonical_topics.yaml` should align with unified_personas.md; validated by `scripts/validate_canonical_sources.py`.

**Operational docs (content team / assembly):** [../docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml](../docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml) (somatic book 10-slot contract, exercise cadence, emotional curve); [../docs/authoring/AUTHOR_ASSET_WORKBOOK.md](../docs/authoring/AUTHOR_ASSET_WORKBOOK.md) (pen-name author assets); [../docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md](../docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md) (persona micro-stakes, promotion workflow). **Exercise registry:** [../SOURCE_OF_TRUTH/exercises_v4/README.md](../SOURCE_OF_TRUTH/exercises_v4/README.md) (11 types, registry.yaml, candidate/approved). **Practice library:** [../SOURCE_OF_TRUTH/practice_library/README.md](../SOURCE_OF_TRUTH/practice_library/README.md) (inbox → ingest → normalize → validate; EXERCISE backstop); [../docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md](../docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md) (teacher fallback with doctrine wrapper).

**Writers:** Use the Writer Spec for content. Structure and compile rules are defined by the Arc-First Canonical Spec.

**Developers:** Use [PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](./PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) as sole system authority; Writer Spec for content rules.

**Release:** Before batch release, confirm all 15 conditions in the Production Readiness Checklist. No telemetry, no repair logic—only release-critical gates.

**Omega layer contracts (Stage 1/2/3 handoffs):** [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md) — BookSpec, FormatPlan, and CompiledBook metadata schemas. **Implementation:** Stage 1 `phoenix_v4/planning/catalog_planner.py`, Stage 2 `phoenix_v4/planning/format_selector.py`, Stage 3 `phoenix_v4/planning/assembly_compiler.py`; full pipeline `scripts/run_pipeline.py`. **Stage 6 (book renderer):** `phoenix_v4/rendering/` (prose_resolver, book_renderer) consumes CompiledBook and produces manuscript/QA .txt; QA: `scripts/render_plan_to_txt.py`; pipeline: `run_pipeline.py --render-book`, `--render-formats txt`, `--render-dir`. See [../docs/V4_FEATURES_SCALE_AND_KNOBS.md](../docs/V4_FEATURES_SCALE_AND_KNOBS.md). **Author (pen-name):** `author_brand_resolver.py`, `author_asset_loader.py`; config: `author_registry.yaml`, `brand_author_assignments.yaml`; pipeline loads author assets when author_id set and fails on missing (§23.9); compiled plan includes author_assets; freebie placeholders. **Narrator (Writer Spec §23.5):** `narrator_brand_resolver.py`; config: `narrators/narrator_registry.yaml`, `brand_narrator_assignments.yaml`; BookSpec and compiled plan carry narrator_id; run_pipeline --narrator (default from brand when omitted).

Machine-readable QA rules: `phoenix_v4/qa/emotional_governance_rules.yaml`

Older multi-doc and docx sources are in repo root `archive/` and `archive/specs_originals/` for reference only.
