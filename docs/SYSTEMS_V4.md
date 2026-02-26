# Phoenix V4 — Canonical Systems Document

**Purpose:** Single canonical description of the whole V4 system.  
**Audience:** Engineers, QA, content governance, release.  
**Last updated:** 2026-02-25  
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
| **Teacher Mode** | [TEACHER_MODE_MASTER_SPEC.md](../specs/TEACHER_MODE_MASTER_SPEC.md), [TEACHER_MODE_INVARIANTS.md](../TEACHER_MODE_INVARIANTS.md), [TEACHER_MODE_V4_CANONICAL_SPEC.md](../specs/TEACHER_MODE_V4_CANONICAL_SPEC.md) | Strict-by-default, coverage gate, EXERCISE fallback, TDEL, CI. Full system reference: [docs/TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md). |
| **Release gates** | [V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md) | 17 conditions; run `scripts/run_production_readiness_gates.py` + simulation; jsonschema required (Gate 17/17b). |
| **24-brand governance** | [PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md](PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md), [PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md](PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md) | Governance architecture (3-layer, 22 controls) and minimum governance core (12 controls GOV-01..GOV-12); survival layer for scale. |

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
   Produces **FormatPlan** (format_structural_id, format_runtime_id, chapter_count, slot_definitions, tier, blueprint_variant, **book_size**). Arc-First: chapter_count and slot_definitions are aligned to the arc. `book_size` is derived from chapter_count (`short <= 6`, `medium <= 10`, else `long`) and is consumed by Stage 3 chapter-planner quotas.

3. **Stage 3 — Assembly**  
   `phoenix_v4/planning/assembly_compiler.py`  
   Consumes BookSpec + FormatPlan + **Arc**; outputs **CompiledBook** (plan_hash, chapter_slot_sequence, atom_ids, dominant_band_sequence, arc_id, emotional_temperature_sequence, reflection_strategy_sequence, **chapter_archetypes, chapter_exercise_modes, chapter_reflection_weights, chapter_story_depths, chapter_planner_warnings**). Reads atoms from canonical pools or, in Teacher Mode, from `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms/`. **EXERCISE backstop:** When `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` is missing or empty (and not Teacher Mode with teacher pool), EXERCISE pool is filled from the practice library via `phoenix_v4/planning/practice_selector.get_backstop_pool()` (config: `config/practice/selection_rules.yaml`).

4. **Stage 6 — Book renderer**  
   `phoenix_v4/rendering/` (prose_resolver, book_renderer)  
   Consumes **CompiledBook**; outputs **prose (manuscript/QA)**. Resolves atom_id → prose from atoms/, compression_atoms, teacher_banks (when teacher_mode), and **practice library** (when atom_id is a practice_id, e.g. lib34_*, ab37_*, via `practice_selector.get_practice_prose_map()`). **QA:** `scripts/render_plan_to_txt.py` (uses Stage 6; `--allow-placeholders`, `--on-missing`). **Pipeline:** `run_pipeline.py --render-book` writes `artifacts/rendered/<plan_id>/book.txt`. See [docs/V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md) §1 (Stage 6) and §3.7 (Teacher Mode knobs).

**Entrypoint:** `scripts/run_pipeline.py` (--topic, --persona, --arc required; optional --teacher, --author, --narrator, --angle).

**Full catalog orchestrator:** `scripts/generate_full_catalog.py` runs the full 24-brand catalog pipeline in one command: (1) teacher portfolio allocation (`teacher_portfolio_planner.allocate_wave`), (2) BookSpec per allocation (`catalog_planner.produce_single`), (3) per-book compile via `run_pipeline` (Stage 1→2→3), (4) optional wave selection (`wave_orchestrator`). Use **`--plan-only`** to produce only BookSpecs (no compile/assembly): e.g. `--max-books 108 --plan-only` writes 108 `.spec.json` files to the candidates dir. Use `--brand <id>` and `--max-books 10` with `--skip-wave-selection` for the **First 10 Books** evaluation (one brand, 10 books, no wave). See [docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) and [docs/PLANNING_STATUS.md](./PLANNING_STATUS.md). When --author is omitted, author_id is resolved from config/brand_author_assignments.yaml (default_author per brand). When --narrator is omitted, narrator_id is resolved from config/brand_narrator_assignments.yaml (default_narrator per brand); Writer Spec §23.5. Teacher/persona/engine compatibility is enforced via `config/catalog_planning/teacher_persona_matrix.yaml` and `phoenix_v4/planning/teacher_matrix.py` when `--teacher` is set. **Environment:** Run with the project venv so PyYAML is available (e.g. `PYTHONPATH=. .venv/bin/python scripts/run_pipeline.py ...`). See [docs/SYSTEMS_AUDIT.md](./SYSTEMS_AUDIT.md) for full function audit.

**Angle Integration (V4.7):** When `angle_id` is set (e.g. `--angle WRONG_PROBLEM`), the **Angle Integration Layer** applies: (1) **Arc variant** — if `config/angles/angle_registry.yaml` defines `arc_path` for that angle, the pipeline uses that arc instead of `--arc`; Arc-First remains authority. (2) **Chapter 1 framing bias** — Stage 3 slot resolver ranks candidates for chapter 1 by `framing_mode` (debunk, framework, reveal, leverage) and optional atom metadata `angle_affinity`; no new pools. (3) **Integration reinforcement** — if the angle has `integration_reinforcement_type`, validation can require (or warn) that the final chapter includes an INTEGRATION atom with matching `reinforcement_type`. (4) **CTSS** — `angle_id` is included in the similarity fingerprint (weight 0.05). (5) **Wave density** — `scripts/ci/check_wave_density.py` FAILs if ≥50% of plans in the wave share the same `angle_id` (non-null only). Config: `config/angles/angle_registry.yaml`; resolver: `phoenix_v4/planning/angle_resolver.py`; bias scoring: `phoenix_v4/planning/angle_bias.py`.

**Chapter Planner policy layer (V4.8):** Before Stage 3 slot resolution, `phoenix_v4/planning/chapter_planner.py` applies deterministic chapter policy from `config/source_of_truth/chapter_planner_policies.yaml`. Execution order is strict: (1) candidate generation by `arc_role` (introduce/deepen/challenge/resolve), (2) hard filtering by quotas and transition compatibility, (3) novelty scoring, (4) deterministic tie-break selection. Policy controls per chapter: archetype id, `exercise_mode` (none/micro/full), `reflection_weight` (light/standard/heavy), `story_depth` (light/standard/deep), and slot presence (`require`/`optional`/`forbid`). Role-distribution checks emit warnings (or can fail if enforced). `run_pipeline.py` writes these effective chapter fields into output JSON.

**Controlled Intro/Conclusion Variation:** When `config/source_of_truth/intro_ending_variation.yaml` has `intro_ending_variation_enabled: true`, pre-intro blocks (narrator_intro, book_title_line, why_this_book, transition_line, etc.) can be chosen from per-brand pattern banks (`config/source_of_truth/pre_intro/banks.yaml`); stable blocks (author_intro, author_background) stay from author YAML. Deterministic selection (same algorithm as slot_resolver); pre_intro_signature and ending_signature (final INTEGRATION + carry line) are capped per brand/quarter (15% intro, 20% ending) with duplicate gate; opening_style_id and integration_ending_style_id apply soft ranking bias for chapter 0 and final chapter. **Spec:** [specs/INTRO_CONCLUSION_VARIATION_SPEC.md](../specs/INTRO_CONCLUSION_VARIATION_SPEC.md). **Single reference for book title, series, author, narrator intro (AI voice), and first/last chapter behavior:** [docs/INTRO_AND_CONCLUSION_SYSTEM.md](INTRO_AND_CONCLUSION_SYSTEM.md). See AUTHOR_ASSET_WORKBOOK (stable vs dynamic blocks) and tests/test_intro_ending_variation.py.

**Structural Variation V4 (anti-cluster storytelling):** Deterministic variation knobs reduce template similarity across books. (1) **Config:** `config/source_of_truth/` — `book_structure_archetypes.yaml`, `journey_shapes.yaml`, `chapter_archetypes.yaml`, `section_reorder_modes.yaml`, `recurring_motif_bank.yaml`, `reframe_line_bank.yaml`. (2) **Planner:** After Stage 2, `phoenix_v4/planning/variation_selector.py` selects `book_structure_id`, `journey_shape_id`, `motif_id`, `section_reorder_mode`, `reframe_profile_id`, `chapter_archetypes` (with anti-cluster penalties from wave index). (3) **Schema:** `phoenix_v4/planning/schema_v4.py` — `variation_signature` = SHA256 of knobs; backward compat defaults for missing fields. (4) **Assembly:** Stage 3 applies role-safe section reorder (per `section_reorder_mode`), and computes `motif_injections` / `reframe_injections` for downstream renderer. (5) **Index/CTSS:** Plan output and `artifacts/freebies/index.jsonl` rows include variation knobs; `scripts/ci/update_similarity_index.py` and `check_platform_similarity.py` include `variation_signature` in fingerprint. (6) **QA:** `phoenix_v4/qa/validate_variation_signature.py`, `validate_motif_saturation.py`, `validate_reframe_diversity.py`, `validate_section_reorder_safety.py`, `validate_journey_shape_coverage.py`, `validate_variant_family_coverage.py`. (7) **Reporting:** `scripts/ci/report_variation_knobs.py` writes `artifacts/reports/variation_report.json` (variation_knob_distribution, collision placeholders).

---

## 5. Teacher Mode flow

**Authority:** [TEACHER_MODE_MASTER_SPEC.md](../specs/TEACHER_MODE_MASTER_SPEC.md), [TEACHER_MODE_INVARIANTS.md](../TEACHER_MODE_INVARIANTS.md). **Full system reference (modules, scripts, config, artifacts):** [docs/TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md).

- **Source of truth:** `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/` (raw, kb, doctrine, approved_atoms by slot type; synthetic_atoms pending/staging/rejected; reports).
- **Strict by default:** When `teacher_mode=true`, `require_full_resolution=True`; no placeholders. Resolver raises `TeacherCoverageError` when no candidates (never returns None).
- **Pre-compile coverage gate (mandatory):** After arc + format expanded, before Stage 3: `phoenix_v4.teacher.coverage_gate.run_coverage_gate(...)` validates teacher atom inventory vs required slots (all slot types; STORY by band). If insufficient → write `artifacts/teacher_coverage_report.json`, raise `TeacherCoverageError`. EXERCISE: when `teacher_exercise_fallback` enabled and teacher pool > 0 but &lt; required, gate passes with fallback_required; otherwise fail.
- **Three-way taxonomy:** Every resolved slot has `atom_source`: `teacher_native` | `teacher_synthetic` | `practice_fallback`. CompiledBook and plan output include `atom_sources`. Teacher-sourced (native + synthetic) ≥ 70% of book; native ≥ 60%. CI recomputes from slots (never trust stored counts).
- **Controlled EXERCISE fallback:** Config `config/teachers/<teacher_id>.yaml` (`teacher_exercise_fallback`, `exercise_wrapper`). When teacher EXERCISE pool non-empty and smaller than required, pool_index merges with practice library (teacher first); deterministic sort by `(atom_source_priority, stable_hash(atom_id))`. Renderer applies intro/close wrapper only when `atom_source == practice_fallback` (deterministic template choice by hash of book_id, chapter, slot). **Validator:** `phoenix_v4/qa/validate_teacher_exercise_share.py` — teacher EXERCISE share ≥ 60% when fallback used.
- **TDEL (offline synthetic gap-fill):** Doctrine fingerprint (`phoenix_v4/teacher/doctrine_fingerprint.py`); doctrine schema allowlist (Gate N): `scripts/ci/check_doctrine_schema.py`; drift: `scripts/ci/check_doctrine_drift.py`. Scripts: `generate_teacher_gap_atoms.py`, `validate_and_stage_synthetic_atoms.py`, `promote_approved_synthetic_atoms.py`. Synthetic atoms: `source: synthetic_doctrine_expansion`; promotion only via approval manifest.
- **CI:** `check_teacher_synthetic_governance.py` (recompute from slots; ratio caps, Gate B band diversity, Gate O no reuse), `check_teacher_readiness.py` (min pool), `check_doctrine_schema.py`, `check_doctrine_drift.py`. Artifacts: `teacher_coverage_report.json`, `teacher_synthetic_report.json`.
- **Doctrine version pinning (§3.12):** When any synthetic present, plan must include `teacher_doctrine_version`; pipeline loads doctrine from teacher bank and emits `teacher_doctrine_version`, `doctrine_fingerprint` when doctrine.yaml exists.
- **Offline pipeline (unchanged):** build KB → mine_kb_to_atoms → assign band → identify_core_teachings → (optional) expand_story_atoms → **normalize_story_atoms** → **normalize_exercise_atoms** → review → approval → compile. **Gap-fill:** `tools/teacher_mining/gap_fill.py`; optional **--kb-dir** for KB-driven body; report includes kb_driven, kb_docs_used.
- **Normalization (deterministic, no LLM):** STORY: structure_family, min 120 words, 3 paragraphs, author_intro_style_id / author_outro_style_id (IDs only). EXERCISE: exercise_family (E1_BREATH, …), min 90 words, setup/instruction/close, exercise_intro_style_id / exercise_outro_style_id.
- **Teacher/persona compatibility:** Enforced at pipeline entry via `teacher_persona_matrix.yaml` (allowed_personas, allowed_engines, preferred_locales); invalid combinations raise before Stage 1. **Portfolio:** `teacher_portfolio_planner.allocate_wave(..., min_exercise_coverage=0, min_story_coverage=0)` excludes teachers below coverage threshold.

---

## 6. CI and release gates

**Pipeline order:** compile → structural_entropy_check → dupe_eval → update_similarity_index → publish.

**Pre-publish gate order (canonical):** (1) structural entropy, (2) platform similarity, (3) prose duplication, (4) wave density, (4a) delivery gate — book output no placeholders ([PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md) §10.6; `scripts/ci/check_book_output_no_placeholders.py`), (5) update_similarity_index last and only when prior gates all pass. All gates 1–4 are always run for full diagnostics; index update is the only state mutation. Single entrypoint: `scripts/ci/run_prepublish_gates.py`. **Release entrypoint:** `scripts/release/prepare_wave_for_export.py` (by wave-id or plans-dir + wave-rendered-dir); calls the gate runner. **The only path to export is via `scripts/release/` entrypoints** (e.g. `prepare_wave_for_export.py` or `export_wave.py`). Automation must call release-layer scripts only, not `scripts/ci/run_prepublish_gates.py` directly for export. Do not add alternate upload paths that skip gates. Must not export on non-zero exit. **Weekly schedule:** `scripts/release/generate_weekly_schedule.py` output JSON includes top-level `effective_platform_cap` and `platform_validation` so consumers can see the cap basis; see [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md).

- **Structural entropy** (`scripts/ci/check_structural_entropy.py`): FAIL if STORY &lt; 120w, EXERCISE &lt; 90w, missing atom, story family dominance &gt; 70%, body contains `[EXPANDED]`, (teacher-mode) chapter missing exercise or teacher anchor (STORY with teacher_id or &gt;60w), same intro/outro style ID &gt; 3 consecutive chapters, or unique intro style IDs &lt; 3. **DEV SPEC 3:** FAIL if missing emotional_role_sequence (unless --allow-missing-role-seq), length mismatch, last≠integration, &gt;2 consecutive same role. Inputs: compiled plan, optional BookSpec, optional `--atoms-dir`, `--teacher-mode`, `--allow-missing-role-seq`.
- **Author positioning** (`scripts/ci/check_author_positioning.py`): FAIL if author_id present but positioning_profile missing or mismatches registry; FAIL if profile-forbidden language (e.g. research_guide first_person &gt; 8%, somatic_companion command_language over threshold, slang/mystical when forbidden). Inputs: `--plan`, optional `--book-spec`, optional `--atoms-dir`.
- **Platform similarity (extended CTSS)** (`scripts/ci/check_platform_similarity.py`): Pre-publish structural similarity gate. CTSS includes arc, band_seq, slot_sig, exercise_chapters, story_fam_vec, ex_fam_vec, tps, compression, **role_seq** (DEV SPEC 3; weight 0.06). Index: `artifacts/catalog_similarity/index.jsonl`; append via `scripts/ci/update_similarity_index.py`. Backward-compatible with index rows missing new fields.
- **Wave density** (`scripts/ci/check_wave_density.py`): FAIL wave if ≥30% same arc_id, ≥40% identical band_seq, ≥50% identical slot_sig, ≥60% identical exercise placement, **≥40% identical emotional_role_sig** (DEV SPEC 3). Requires `--plans-dir`; plans must have arc_id, emotional_temperature_sequence, slot_sig, exercise_chapters (Stage 3 output).
- **Production readiness:** 15 conditions in [V4_5_PRODUCTION_READINESS_CHECKLIST.md](../specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md); run `scripts/run_production_readiness_gates.py` and simulation.
- **Brand archetype registry** (`phoenix_v4/qa/validate_brand_archetype_registry.py`): FAIL if registry YAML violates structural rules (unique brand_id/admin_id, duration sum 1.0, mid_form cap, unique lead_voice, no 100% style_pool overlap). Run: `PYTHONPATH=. python3 phoenix_v4/qa/validate_brand_archetype_registry.py`. Authority: [BRAND_ARCHETYPE_VALIDATOR_SPEC.md](../specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md).
- **Teacher Mode CI:** `scripts/ci/check_teacher_synthetic_governance.py` (ratio caps, no placeholders, Gate B/O; recompute from atom_sources); `scripts/ci/check_teacher_readiness.py` (min EXERCISE/HOOK/REFLECTION/INTEGRATION per teacher); `scripts/ci/check_doctrine_schema.py` (Gate N: doctrine allowlist); `scripts/ci/check_doctrine_drift.py` (fingerprint vs registry). See [TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md).

**Observability and scale:** Structural drift dashboard (`scripts/obs/build_structural_drift_dashboard.py`) writes `artifacts/drift/summary.json` and `report.html` (includes **emotional role** distribution, top role signatures, role×band counts; DEV SPEC 3). Monte Carlo CTSS risk (`simulation/run_monte_carlo_ctss.py`) simulates duplication risk vs index. Wave orchestrator (`phoenix_v4/planning/wave_orchestrator.py`) selects a balanced wave from candidates (arc/band/slot/ex diversity, density constraints).

**Phase 13-C — Deterministic Constraint Solver Wave Optimizer (DWO-CS):** Fully deterministic wave selection: satisfies hard constraints (weekly caps, cross-brand no arc overlap when CBDI convergent, brand-identity new-arc cap when BISI drift critical) and maximizes a deterministic objective. No randomness; no ML. Module: `phoenix_v4/ops/wave_optimizer_constraint_solver.py`. Config: `config/wave_optimizer_constraint_solver.yaml`. **Wave build pipeline order:** (1) Generate candidate set (e.g. wave_candidates_{wave_id}.json), (2) Run DWO-CS (`wave_optimizer_constraint_solver.py`), (3) Run Phase 6 `check_release_wave.py` as final verification, (4) Export wave. Outputs: `wave_optimizer_solution_{wave_id}.json`/.md or `wave_optimizer_infeasible_{wave_id}.json` with blocking reasons. Exit: 0 SOLVED, 1 INFEASIBLE, 2 SOLVED_WITH_WARN. **Schemas & blocking codes:** `schemas/wave_candidates.schema.json`, `wave_optimizer_solution.schema.json`, `wave_optimizer_infeasible.schema.json`; canonical codes and Slack/Jira routing in `config/wave_optimizer_blocking_codes.yaml`. See [docs/PHASE_13_C_WAVE_OPTIMIZER.md](./PHASE_13_C_WAVE_OPTIMIZER.md) and [phoenix_v4/ops/README.md](../phoenix_v4/ops/README.md).

- **Creative Quality Gate v1 (post-compile):** Read-only gate on **compiled book** prose (after Stage 3 compile, before release-wave). Module: `phoenix_v4/gates/check_creative_quality_v1.py`. Config: `config/creative_quality_v1.yaml`. Measures five deterministic signals: arc emotional motion, transformation density, specificity, ending strength, lexical rhythm. No LLM; regex/structural heuristics only. Output: `artifacts/ops/book_quality_summary_{book_id}_{date}.json`; exit 0 PASS, 2 WARN, 1 FAIL. Schema: `schemas/book_quality_summary_v1.schema.json`. See [docs/CREATIVE_QUALITY_GATE_V1.md](./CREATIVE_QUALITY_GATE_V1.md).

**Human-quality checkpoint and creative QA (standalone, not CI):** Content quality is validated manually and via standalone tools; these are **not** part of governance or release gates. **(1) Human checkpoint docs:** [CREATIVE_QUALITY_VALIDATION_CHECKLIST.md](./CREATIVE_QUALITY_VALIDATION_CHECKLIST.md) (arc, story, exercise, voice, ending); [FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](./FIRST_10_BOOKS_EVALUATION_PROTOCOL.md) (compile 10 from one brand → blind listen → 5-axis score → pattern analysis); [SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md](./SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md) (per-chapter Recognition/Reframe/Relief/Challenge/Identity). **(2) Upstream quality docs:** [HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md](./HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md) (STORY atom specificity, cost, conflict, insight pivot, echo; pass/fail if lacks 2 of 5); [NARRATIVE_TENSION_VALIDATOR.md](./NARRATIVE_TENSION_VALIDATOR.md) (tension slope, “where does rupture happen?”); [INSIGHT_DENSITY_ANALYZER.md](./INSIGHT_DENSITY_ANALYZER.md) (reframes per 1k words). **(3) Standalone quality tools** (`phoenix_v4/quality/`): **story_atom_lint.py** — deterministic lint on STORY atoms (specificity, conflict, cost, pivot); parses CANONICAL.txt per-atom (`## ROLE vNN --- metadata --- body`); PASS/WARN/FAIL; writes ops artifact `story_atom_lint_summary_*.json` (schema story_atom_lint_v1). **transformation_heatmap.py** — per-chapter recognition/reframe/relief/identity_shift and ending strength (--file or --plan). **memorable_line_detector.py** — highlight-density candidates (--file or --plan). **marketing_assets_from_lines.py** — turns memorable-line JSON into quotes, pin_captions, landing_hooks, trailer_lines, email_subjects. **quality_bundle_builder.py** — single artifact per book: runs heatmap + memorable + marketing in-process, computes CSI (Creative Strength Index), writes schema-validated `book_quality_bundle_<book_id>_<date>.json`; exit 0/1/2. **Base:** `phoenix_v4/quality/base.py` — exit contract (0 PASS, 1 FAIL, 2 WARN), `AtomBlock`, `parse_canonical_blocks`, `exit_with_status`. Run manually or in review; see [phoenix_v4/quality/README.md](../phoenix_v4/quality/README.md).

**Quality → Wave integration:** **wave_candidates_enricher.py** (`phoenix_v4/ops/`) — augments wave candidates with quality metrics from `book_quality_bundle_*.json`; optional filters (--require-quality-pass, --min-ending-strength); output `*_candidates_enriched.json` (schema wave_candidates_enriched_v1). **quality_objective.py** — `normalize_quality`, `compute_wave_quality_stats`, quality objective terms for solver. **Wave optimizer** (Phase 13-C) applies quality constraints (exclude_quality_fail, min_ending_strength, min_csi_score, exclude_quality_missing) and adds quality terms to objective (quality_csi, quality_ending, quality_diversity, quality_low_endings_penalty); config: `config/wave_optimizer_constraint_solver.yaml` § constraints, § objective.weights; solution JSON includes `quality_summary`.

**Memorable line registry (duplication guard):** Tracks strong (good/great) memorable lines across catalog. **update_memorable_line_registry.py** — run after each bundle; only **appends and writes** when the bundle has at least one tracked memorable line (good/great); otherwise no-ops (registry JSONL and snapshot unchanged). Emits a **structured JSON signal** on stdout: `{"appended": N}` (N = lines appended); callers must use this signal, not log prose; missing signal should be treated as contract break (fail fast). **check_memorable_line_registry.py** — run before export (e.g. Gate #49); checks wave against snapshot; exit 0/1/2; report `memorable_line_registry_violations_<date>.json`. Config: `config/quality/memorable_line_registry_policy.yaml`. **quality_bundle_postprocessor.py** — adds `duplication_safety` (0–100) to bundle from snapshot; recomputes CSI with duplication_safety weight. **Catalog health dashboard:** `catalog_health_dashboard_builder.py` — aggregates ops artifacts into `catalog_health_summary_<date>.json` (quality, duplication risk, coverage, release readiness). Schemas: memorable_line_registry_snapshot_v1, memorable_line_registry_violations_v1, catalog_health_summary_v1. **Golden path:** `scripts/run_golden_quality_path.py` runs end-to-end: quality_bundle_builder → update_memorable_line_registry → wave_candidates_enricher → wave_optimizer_constraint_solver → check_memorable_line_registry; requires jsonschema; parses updater `{"appended": N}` and fails if signal missing. See [phoenix_v4/ops/README.md](../phoenix_v4/ops/README.md).

- **Ops schema CI:** All ops JSON artifacts are contract-bound. **Registry:** `config/ops_schema_registry.yaml` (artifact patterns → schema paths). **Validators:** `scripts/ci/validate_ops_artifacts.py` (validates each ops JSON against its schema; requires `jsonschema`; exit 1 if jsonschema missing — no silent skip), `scripts/ci/validate_ops_registry_consistency.py` (schema files exist, registry matches artifacts). **Gate 17/17b:** Production readiness gates require jsonschema (Gate 17) and run ops/waves schema validation when those dirs exist (Gate 17b); see [scripts/ci/README.md](../scripts/ci/README.md). **Regression tests:** `tests/test_quality_regression.py` — malformed CANONICAL.txt, missing chapter text in plan, duplicate memorable-line collision. Schema changes require version bump, registry update, and entry in [docs/SCHEMA_CHANGELOG.md](./SCHEMA_CHANGELOG.md).

- **100% atoms coverage sim test** (`tests/test_atoms_coverage_100_percent.py`): For every (persona, topic, engine) in the catalog (from `config/catalog_planning/canonical_personas.yaml` and `config/topic_engine_bindings.yaml`), requires `atoms/{persona}/{topic}/{engine}/CANONICAL.txt` to exist and be non-empty (at least one STORY atom). **BLOCKER:** test fails and prints missing paths if any tuple has no STORY pool. **Report only (RED):** pools below `min_story_pool_size` (from `config/gates.yaml`) are reported without failing. Run: `python3 tests/test_atoms_coverage_100_percent.py` or `pytest tests/test_atoms_coverage_100_percent.py -v`; exit 0 only when 100% coverage. Authority: [docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md](./TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md) §7.

---

## 7. Freebie and asset pipeline (V4 Immersion)

- **Canonical sources:** **Source of truth for active personas and topics:** [unified_personas.md](../unified_personas.md) (10 active personas, 12 active topics). Config files `config/catalog_planning/canonical_topics.yaml` and `canonical_personas.yaml` must align with unified_personas.md; validated by `scripts/validate_canonical_sources.py` against topic_engine_bindings and identity_aliases. **topic_engine_bindings.yaml** includes the unified 12 topics (overthinking, burnout, boundaries, self_worth, social_anxiety, financial_anxiety, imposter_syndrome, sleep_anxiety, depression, grief, compassion_fatigue, somatic_healing) plus legacy (anxiety, courage, financial_stress). **Content coverage:** Backlog report and CSV ([artifacts/reports/content_coverage_backlog_unified.md](../artifacts/reports/content_coverage_backlog_unified.md), .csv) are the operational source of truth; order bindings → arcs → STORY pools. Batch arc generation: `scripts/generate_arcs_from_backlog.py` (F006 or chosen format); arcs under config/source_of_truth/master_arcs/.
- **Asset planning:** `scripts/plan_freebie_assets.py` — catalog mode (`--catalog <yaml>`) or canonical mode (`--topics`, `--personas`); writes `artifacts/asset_planning/manifest.jsonl`.
- **Asset creation:** `scripts/create_freebie_assets.py` — reads manifest; generates HTML/PDF/EPUB/MP3 into format-first store `store/{format}/{topic}/{persona}/{freebie_id}.{ext}`.
- **Validation:** `scripts/validate_asset_store.py` — manifest vs store; optional `--rules config/validation.yaml`.
- **Book pipeline:** After Stage 3, freebie planner sets `freebie_bundle` and `freebie_bundle_with_formats`. `generate_freebies_for_book` (in `freebie_renderer`) resolves from asset store when `--asset-store` is set, else renders; `--publish-dir` writes outputs to `publish_dir/{slug}/`. CLI: `run_pipeline.py --formats html,pdf,epub,mp3 --skip-audio --publish-dir <dir> --asset-store <store_root>`.
- **Main book prose (Stage 6):** Optional `--render-book` renders CompiledBook → manuscript/QA .txt via `phoenix_v4/rendering` (prose_resolver + TxtWriter). Output: `artifacts/rendered/<plan_id>/book.txt`. QA path: `scripts/render_plan_to_txt.py <plan.json> -o <out.txt>` (same Stage 6 API; supports `--allow-placeholders`, `--on-missing`, `--atoms-root`).
- **Tier bundles:** `config/freebies/tier_bundles.yaml` (Good/Better/Best). **Asset lifecycle:** `config/asset_lifecycle.yaml` (regenerate_when, auto_prune). See [PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md) §8–§11.

**CTA and freebie anti-spam (spec §10, §10.5, §10.6):** The following are canonical; authority is [PHOENIX_FREEBIE_SYSTEM_SPEC.md](../specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md).

| Control | Purpose | Where |
|--------|---------|-------|
| **In-book CTA insertion point** | Single CTA in the book (not only on freebie page); prevents sprawl. | **Spec §10.5.** Insertion point: back matter (after final integration). Pipeline must inject rendered CTA + URL from plan (`cta_template_id`, `freebie_slug`). No raw placeholders in output. |
| **CTA signature index + caps** | Cap how often the same CTA wording is used per brand per quarter. | **Spec §10.** Config: `config/freebies/cta_anti_spam.yaml` (`max_same_cta_signature_per_brand_per_quarter`). Module: `phoenix_v4/qa/cta_signature_caps.py`. Optional index: `artifacts/freebies/cta_signature_index.jsonl`. |
| **Slug/CTA uniqueness thresholds** | Enforce wave-level limits on identical bundle/CTA/slug pattern; no over-reuse across the wave. | **Spec §10.** Config: `config/freebies/cta_anti_spam.yaml` → `density_thresholds`. Gate: `phoenix_v4/qa/validate_freebie_density.py` (loads thresholds from config when present). |
| **Delivery gate (no placeholders)** | Fail if placeholders or metadata leak into book output (e.g. `{{cta_text}}`, `{{slug}}`, `[Placeholder: ...]`). | **Spec §10.6.** Script: `scripts/ci/check_book_output_no_placeholders.py`. Wired in `scripts/ci/run_prepublish_gates.py` (step 4a). |
| **Wave CTA diversity** | Cap same CTA style and same slug pattern share in a release wave. | **Spec §10.** Config: `config/release_wave_controls.yaml` (`max_same_cta_style`, `max_same_slug_pattern`; anti_homogeneity weights `cta_diversity`, `slug_diversity`). Module: `phoenix_v4/ops/check_release_wave.py` (WavePlanRow: `cta_template_id`, `slug_pattern`; weekly_caps and anti_homogeneity). |

See [V4_FEATURES_SCALE_AND_KNOBS.md](V4_FEATURES_SCALE_AND_KNOBS.md) (freebie density gate, CTA signature caps, delivery gate, wave CTA diversity) and [scripts/ci/README.md](../scripts/ci/README.md) for gate order.

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
| **Chapter planner policies** | **config/source_of_truth/chapter_planner_policies.yaml** — book_size_by_chapters, role_distribution_targets, size-based quotas (`full_exercise_max`, `reflection_heavy_max`), archetype transition constraints, and per-archetype slot policy (`exercise_mode`, `reflection_weight`, `story_depth`). |
| Master arcs | config/source_of_truth/master_arcs/; emotional_role_sequence required (DEV SPEC 3). Role→slot: config/format_selection/emotional_role_slot_requirements.yaml. |
| **Structural Variation V4** | config/source_of_truth/ (book_structure_archetypes, journey_shapes, chapter_archetypes, section_reorder_modes, recurring_motif_bank, reframe_line_bank). Plan fields: book_structure_id, journey_shape_id, motif_id, section_reorder_mode, reframe_profile_id, chapter_archetypes, variation_signature. Selector: phoenix_v4/planning/variation_selector.py; schema: phoenix_v4/planning/schema_v4.py. Report: scripts/ci/report_variation_knobs.py → artifacts/reports/variation_report.json. |
| Engines | config/source_of_truth/engines/ |
| Teacher banks | SOURCE_OF_TRUTH/teacher_banks/&lt;teacher_id&gt;/ (approved_atoms/, doctrine/, synthetic_atoms/, reports/). |
| **Teacher per-teacher config** | **config/teachers/&lt;teacher_id&gt;.yaml** — teacher_exercise_fallback, exercise_wrapper (intro_templates, close_templates), teacher_quality_profile, fallback_exercise_share_min, teacher_total_share_min. Example: config/teachers/master_feng.yaml. See [TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md). |
| **Exercise registry (V4 somatic)** | **SOURCE_OF_TRUTH/exercises_v4/** (registry.yaml, 11 types; candidate/_stubs/, approved/; slot_07_practice + selection rules) |
| **Practice library (EXERCISE backstop)** | **SOURCE_OF_TRUTH/practice_library/** (inbox/, tmp/, store/practice_items.jsonl); **config/practice/selection_rules.yaml**, **validation.yaml**. Scripts: scripts/practice/ingest_practice_libraries, normalize_practice_items, validate_practice_store, extract_libraries_from_rtf. Runtime: phoenix_v4/planning/practice_selector.py (load_store, get_backstop_pool, get_practice_prose_map); pool_index uses backstop when EXERCISE canonical empty; prose_resolver resolves practice_id → text from store. QA: phoenix_v4/qa/practice_safety_lint.py. Schema: specs/PRACTICE_ITEM_SCHEMA.md; teacher fallback: docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md. |
| **Somatic assembly blueprint** | **docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml** (10-slot contract, exercise cadence, emotional curve; structure only) |
| **Compression atoms (slot_08_compression)** | **SOURCE_OF_TRUTH/compression_atoms/** approved/\<persona\>/\<topic\>/*.yaml; 40–120w, one insight; formats may include COMPRESSION via slot_template (e.g. F006). CI: structural entropy, CTSS, wave density. DEV SPEC 2. |
| **Active personas/topics (catalog)** | **[unified_personas.md](../unified_personas.md)** — source of truth (10 active personas, 12 active topics). **config/catalog_planning/canonical_personas.yaml**, **canonical_topics.yaml** must align; validate_canonical_sources.py. |
| **Freebies (V4 Immersion)** | config/freebies/ (registry, selection_rules, **tier_bundles.yaml**, **audio_scripts.yaml**); **config/catalog_planning/canonical_topics.yaml**, **canonical_personas.yaml** (align with unified_personas.md); **config/tts/engines.yaml** (TTS engine + voice mapping); **config/validation.yaml**, **config/asset_lifecycle.yaml**. Scripts: **validate_canonical_sources.py**, **plan_freebie_assets.py**, **create_freebie_assets.py**, **validate_asset_store.py**. Asset store: **artifacts/freebie_assets/store/{format}/{topic}/{persona}/{freebie_id}.{ext}**; manifest: **artifacts/asset_planning/manifest.jsonl**. Pipeline: **--formats**, **--skip-audio**, **--publish-dir**, **--asset-store**. |
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
| **Wave optimizer (Phase 13-C)** | **config/wave_optimizer_constraint_solver.yaml** — eligibility, hard_constraints.weekly_caps (Phase 6 parity), cross_brand, brand_identity, **constraints** (exclude_quality_fail, min_ending_strength, min_csi_score, exclude_quality_missing, max_low_ending_ratio), objective weights (**quality_csi**, **quality_ending**, **quality_diversity**, **quality_low_endings_penalty**), determinism. Module: phoenix_v4/ops/wave_optimizer_constraint_solver.py; quality_objective.py. Enricher: phoenix_v4/ops/wave_candidates_enricher.py (quality from bundles → enriched candidates). Outputs: artifacts/ops/wave_optimizer/wave_optimizer_solution_{wave_id}.json|.md (includes **quality_summary**) or wave_optimizer_infeasible_{wave_id}.json. |
| **Wave optimizer blocking codes** | **config/wave_optimizer_blocking_codes.yaml** — canonical blocking reason codes (INSUFFICIENT_ELIGIBLE_CANDIDATES, CROSS_BRAND_ARC_CONFLICT, etc.) and Slack/Jira routing; machine-parseable. |
| **Ops schema registry** | **config/ops_schema_registry.yaml** — artifact type → schema_path, artifact_pattern, current_version. Used by scripts/ci/validate_ops_artifacts.py. |
| **Creative Quality Gate v1** | **config/creative_quality_v1.yaml** — transformation min share, arc_motion (bands, rise/fall, flat warn), specificity, ending_strength, lexical_rhythm. Module: phoenix_v4/gates/check_creative_quality_v1.py. |
| **Full catalog orchestrator** | **scripts/generate_full_catalog.py** — portfolio → BookSpec → compile → wave selection; --brand, --max-books, --skip-wave-selection for First 10 Books. |
| **Standalone creative QA (quality)** | **phoenix_v4/quality/** — story_atom_lint (per-atom CANONICAL, ops artifact), transformation_heatmap, memorable_line_detector, marketing_assets_from_lines, **quality_bundle_builder** (CSI, book_quality_bundle_*.json); base.py (exit 0/1/2, AtomBlock). See phoenix_v4/quality/README.md. |
| **Quality/ops (registry, dashboard)** | **config/quality/memorable_line_registry_policy.yaml** — max_occurrences_global, max_occurrences_per_brand|per_wave, strength_levels_tracked, block_on_violation. **phoenix_v4/ops:** update_memorable_line_registry.py, check_memorable_line_registry.py, catalog_health_dashboard_builder.py, quality_bundle_postprocessor.py. Artifacts: memorable_line_registry_v1.jsonl, memorable_line_registry_snapshot_v1.json, memorable_line_registry_violations_*.json, catalog_health_summary_*.json. |
| **Ops JSON schemas** | **schemas/** — wave_candidates, wave_optimizer_solution, wave_optimizer_infeasible, book_quality_summary_v1, **book_quality_bundle_v1**, **wave_candidates_enriched_v1**, **memorable_line_registry_snapshot_v1**, **memorable_line_registry_violations_v1**, **catalog_health_summary_v1**, story_atom_lint_v1, book_transformation_summary_v1, memorable_line_summary_v1 (Draft 2020-12 / Draft 7). Registry: config/ops_schema_registry.yaml. |

---

## 10. Remaining to finish whole system

Planning and implementation are **not 100%** until the following are addressed. Details: [docs/PLANNING_STATUS.md](./PLANNING_STATUS.md).

| Area | Current state | Still to do |
|------|----------------|-------------|
| **Author/teacher assignment** | **Implemented.** Teachers: brand_teacher_assignments.yaml + teacher_brand_resolver. **Pen-name authors:** config/author_registry.yaml (luna_hart, kai_nakamura, marcus_cole, diane_reyes); config/brand_author_assignments.yaml + author_brand_resolver (default_author from brand when --author not supplied); author_asset_loader loads bio/why_this_book/authority_position/audiobook_pre_intro from assets/authors/ or registry assets_path; pipeline fails on missing assets (§23.9); compiled plan includes author_assets; freebie_renderer supports {{author_bio}}, {{author_why_this_book}}, {{author_pen_name}}, {{author_audiobook_pre_intro}}. | — |
| **Coverage enforcement** | **Implemented.** phoenix_v4/planning/coverage_checker.py; wired in production readiness gate 2b. **100% atoms sim test:** `tests/test_atoms_coverage_100_percent.py` asserts every (persona, topic, engine) has non-empty STORY pool for all books; run `python3 tests/test_atoms_coverage_100_percent.py` from repo root; see docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md §7. | — |
| **Gate #49 (locale/territory)** | **Wired.** scripts/distribution/pre_export_check.py runs Gate #49 before export. | — |
| **Freebies** | **Implemented.** Deterministic freebie planner (post–Stage 3), registry, selection rules, density CI, CTSS; pipeline maintains plan rows in artifacts/freebies/index.jsonl (one row per book_id) and renderer writes artifact logs to artifacts/freebies/artifacts_index.jsonl; **V4 Immersion Ecosystem:** canonical topics/personas, asset pipeline (plan_freebie_assets, create_freebie_assets, validate_asset_store), multi-format store, publish_dir, tier_bundles, pipeline flags (--formats, --skip-audio, --publish-dir, --asset-store). | — |
| **Narrators** | **Implemented.** config/narrators/narrator_registry.yaml; BookSpec and compiled plan carry narrator_id; run_pipeline --narrator; default from brand when not supplied (narrator_brand_resolver). Writer Spec §23.5. | — |
| **Teacher Mode (strict + fallback + TDEL)** | **Implemented.** Strict by default (require_full_resolution, resolver raise on no candidates); pre-compile coverage gate (coverage_gate.py, TeacherCoverageError, teacher_coverage_report.json); atom_sources (teacher_native | teacher_synthetic | practice_fallback); controlled EXERCISE fallback (config/teachers/&lt;id&gt;.yaml, pool merge, wrapper only for practice_fallback); validate_teacher_exercise_share (≥60% when fallback); doctrine fingerprint + check_doctrine_schema + check_doctrine_drift; check_teacher_synthetic_governance (recompute from slots, Gate B/O), check_teacher_readiness; TDEL scripts (generate_teacher_gap_atoms, validate_and_stage_synthetic_atoms, promote_approved_synthetic_atoms); portfolio coverage threshold. See [TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md). | — |
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
| **specs/TEACHER_MODE_MASTER_SPEC.md** | Teacher Mode strict-by-default, coverage gate, fallback, TDEL, CI (single canonical summary). |
| **TEACHER_MODE_INVARIANTS.md** (repo root) | Non-negotiable invariants when teacher_mode=true. |
| **docs/TEACHER_MODE_SYSTEM_REFERENCE.md** | Full system reference: modules, scripts, config, artifacts. |
| **specs/TEACHER_MODE_V4_CANONICAL_SPEC.md** | Teacher Mode implementation authority (banks, KB, Arc-First). |
| **specs/TEACHER_MODE_NORMALIZATION_SPEC.md** | Normalization pipeline and entropy CI. |
| **specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md** | 15 release conditions. |
| **docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml** | Somatic book assembly: 10-slot contract, exercise cadence, emotional curve template (structure only). |
| **docs/authoring/AUTHOR_ASSET_WORKBOOK.md** | Operational: pen-name author assets (bio, why_this_book, authority_position, audiobook_pre_intro). |
| **docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md** | Operational: persona-specific micro-stakes, promotion workflow (provisional_template → confirmed). |
| **SOURCE_OF_TRUTH/exercises_v4/README.md** | Exercise registry (11 types), candidate/approved layout, slot_07_practice integration. |
| **specs/PRACTICE_ITEM_SCHEMA.md** | Practice item schema, store layout, EXERCISE backstop and teacher fallback references. |
| **docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md** | Teacher fallback: when teacher has insufficient EXERCISE atoms, supplement from practice library with doctrine wrapper. |
| **SOURCE_OF_TRUTH/practice_library/README.md** | Practice library layout, pipeline (ingest → normalize → validate), usage (backstop, teacher fallback). |
| **docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md** | Tuple viability preflight gate (Phase 1) and weekly coverage health report (Phase 2); tuple universe from catalog (personas × bindings × formats); paths, risk model, NO_ARC for missing arcs; **§7** 100% atoms sim test (`tests/test_atoms_coverage_100_percent.py`). |
| **docs/PHASE_13_C_WAVE_OPTIMIZER.md** | Phase 13-C DWO-CS: contract, inputs/outputs, hard/soft constraints, solver, config, CLI, infeasibility diagnostics, schemas, blocking codes, tests, ops playbook. |
| **docs/CREATIVE_QUALITY_GATE_V1.md** | Creative Quality Gate v1: post-compile read-only gate; five signals (arc motion, transformation, specificity, ending, rhythm); CLI, config, output schema. |
| **scripts/generate_full_catalog.py** | Full catalog orchestrator: portfolio → BookSpec → compile → wave selection; First 10 Books mode (--brand, --max-books 10, --skip-wave-selection). |
| **docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md** | Human checklist: arc, story, exercise, voice, ending (use after compile). |
| **docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md** | Evaluate 10 books from one brand: compile → blind listen → 5-axis score → pattern analysis. |
| **docs/SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md** | Manual impact: each chapter ≥2 of Recognition/Reframe/Relief/Challenge/Identity. |
| **docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md** | Upstream STORY rubric: specificity, cost, conflict, insight pivot, echo; pass if lacks &lt;2 of 5. |
| **docs/NARRATIVE_TENSION_VALIDATOR.md** | Upstream: tension slope; “where does rupture happen?” |
| **docs/INSIGHT_DENSITY_ANALYZER.md** | Upstream: reframes per 1k words; target 1 per 800–1,200 words. |
| **phoenix_v4/quality/README.md** | Standalone creative QA: story_atom_lint, transformation_heatmap, memorable_line_detector, marketing_assets_from_lines (not CI). |
| **docs/SCHEMA_CHANGELOG.md** | Ops and wave JSON schema version history; migration notes; required on any schema change. |
| **phoenix_v4/ops/README.md** | Ops tooling index: Coverage Health, Phase 6 release wave, Phase 9–12, Phase 13-C DWO-CS (incl. quality constraints and objective), wave_candidates_enricher, memorable line registry (update + check), catalog health dashboard, quality_bundle_postprocessor, ops schema registry and CI validation, Creative Quality Gate v1. |

Older multi-doc and talp/SYSTEMS_DOCUMENTATION.md remain for reference; **this doc (docs/SYSTEMS_V4.md) is the single canonical systems description for V4.**
