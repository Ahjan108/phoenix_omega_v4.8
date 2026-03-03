# V4 System: Features, Scale Parts, Anti-Spam Assurance, and Knobs

**Purpose:** Single reference for (1) all V4 features, (2) scale-related components and anti-spam assurance, (3) every configurable knob (config, thresholds, CLI).  
**Authority:** Backed by [docs/SYSTEMS_V4.md](SYSTEMS_V4.md), [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md), and the scripts/config listed below.

---

## 1. All V4 Features

### Pipeline and assembly
- **Stage 1 — Catalog planning** — BookSpec (topic_id, persona_id, teacher_id, brand_id, angle_id, series_id, installment_number, seed).
- **Stage 2 — Format selection** — FormatPlan (format_structural_id, format_runtime_id, chapter_count, slot_definitions, tier, blueprint_variant, **book_size**). Arc-First alignment.
- **Stage 3 — Assembly** — CompiledBook (plan_hash, chapter_slot_sequence, atom_ids, dominant_band_sequence, arc_id, emotional_temperature_sequence, emotional_role_sequence, slot_sig, exercise_chapters, freebie_bundle, freebie_bundle_with_formats, **chapter_archetypes, chapter_exercise_modes, chapter_reflection_weights, chapter_story_depths, chapter_planner_warnings**, etc.).
- **Stage 6 — Book renderer** — Renders CompiledBook → prose output (manuscript/QA). `phoenix_v4.rendering`: prose_resolver (atom_id → prose from atoms/, compression_atoms, teacher_banks, **practice library** for practice_id e.g. lib34_*, ab37_*), book_renderer (TxtWriter, render_book). QA: `scripts/render_plan_to_txt.py` uses Stage 6. Pipeline: `--render-book`, `--render-formats txt`, `--render-dir`; outputs to `artifacts/rendered/<plan_id>/book.txt`. Edge cases: placeholders/silence → [Placeholder/Silence: TYPE]; missing atoms → fail or [Missing: atom_id]; persona/topic from plan or inferred from first STORY atom_id via topic_engine_bindings.
- **Arc-First** — Arc required; no arc = no compile. Arc defines chapter_count, emotional_curve, emotional_role_sequence, slot alignment.
- **Chapter Planner (V4.8)** — Deterministic policy layer in Stage 3 (`phoenix_v4/planning/chapter_planner.py`) loaded from `config/source_of_truth/chapter_planner_policies.yaml`: candidate generation by arc role, hard quota/transition filter first, novelty scoring second, deterministic select. Applies chapter `exercise_mode` (`none|micro|full`), `reflection_weight`, `story_depth`, and slot policy overrides.
- **Angle Integration (V4.7)** — When `angle_id` is set: arc variant from `config/angles/angle_registry.yaml` (optional `arc_path`); chapter 1 framing bias by `framing_mode` (debunk, framework, reveal, leverage); integration reinforcement validation (optional `reinforcement_type` on INTEGRATION atoms); CTSS includes `angle_id` (weight 0.05); wave density FAIL if ≥50% same angle_id. Config: `config/angles/angle_registry.yaml`; `phoenix_v4/planning/angle_resolver.py`, `angle_bias.py`.
- **Alias resolution** — topic/persona aliases → canonical (identity_aliases.yaml).
- **Teacher / author / narrator resolution** — teacher_brand_resolver, author_brand_resolver, narrator_brand_resolver; defaults from brand_teacher_assignments, brand_author_assignments, brand_narrator_assignments.
- **Post-compile validators** — validate_compiled_plan, validate_arc_alignment, validate_engine_resolution.

### Content and atoms
- **Six atom types** — HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION (Writer Spec §4).
- **Practice library (EXERCISE backstop)** — When `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` is missing or empty (and not Teacher Mode with teacher pool), Stage 3 fills EXERCISE pool from **SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl** via `phoenix_v4/planning/practice_selector.get_backstop_pool()`. Store is built from 9×34 library_34 JSONs (sensory_grounding, meditations, affirmations, etc.) + optional ab_tady_37; pipeline: ingest → normalize → validate (scripts under `scripts/practice/`). Config: `config/practice/selection_rules.yaml` (EXERCISE_BACKSTOP), `config/practice/validation.yaml`. Stage 6 resolves prose for atom_ids that are practice_ids (lib34_*, ab37_*) from the store. Schema: specs/PRACTICE_ITEM_SCHEMA.md; teacher fallback (doctrine wrapper): docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md. Safety lint: phoenix_v4/qa/practice_safety_lint.py.
- **Compression slot (slot_08_compression)** — Optional per format (e.g. F006); COMPRESSION atoms 40–120w, one insight; CTSS and wave density include compression.
- **Emotional role taxonomy** — recognition, destabilization, reframe, stabilization, integration; arc and format role→slot requirements.
- **STORY emotional_intensity_band** — 1–5 required per STORY; diversity enforced (≥3 bands per book, ≤3 consecutive same band).

### Teacher Mode
- **What it is** — When `--teacher` is set (or BookSpec has teacher_id and teacher_mode), Stage 3 and Stage 6 use **teacher-scoped atom pools** instead of canonical `atoms/<persona>/<topic>/`. One teacher_id per book; plan carries `teacher_id` and `teacher_mode`; CTSS includes teacher presence (tps weight).
- **Source of truth** — `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/`: raw, kb, doctrine, candidate_atoms, **approved_atoms** (by slot type: STORY, REFLECTION, EXERCISE, etc.). Approved atoms are YAML (atom_id, body, band/semantic_family as needed). Doctrine: `doctrine/core_teachings.yaml`, forbidden claims, tone, glossary.
- **Pipeline** — `run_pipeline.py --teacher <id>`; teacher_id resolved from `brand_teacher_assignments.yaml` when omitted (per brand). **Teacher/persona compatibility** enforced at entry via `teacher_persona_matrix.yaml` (allowed_personas, allowed_engines, preferred_locales); invalid (persona, engine) raises before Stage 1. Stage 3 loads pools from `teacher_banks/<teacher_id>/approved_atoms/<slot_type>/*.yaml` when teacher_mode; Stage 6 prose_resolver loads prose from same when plan has teacher_mode/teacher_id.
- **Offline workflow** — Build KB → mine to candidate_atoms → assign band → core_teachings → normalize_story_atoms / normalize_exercise_atoms → review → approval → compile. **Gap-fill:** `tools/teacher_mining/gap_fill.py` (optional `--kb-dir` for KB-driven body). Approve: approve_atoms, report_teacher_gaps.
- **Config** — `config/catalog_planning/teacher_persona_matrix.yaml` (per-teacher allowed_personas, allowed_engines); `config/catalog_planning/brand_teacher_assignments.yaml` (default teacher per brand); `config/catalog_planning/brand_teacher_matrix.yaml` (teachers per brand, max_books, teacher_constraints); `config/teachers/teacher_registry.yaml` (per-teacher allowed_topics, allowed_engines, teacher_mode_defaults e.g. require_teacher_story, require_teacher_exercise).
- **CI / QA** — `check_structural_entropy.py --teacher-mode`: teacher-mode-only checks (e.g. chapter missing exercise or teacher anchor, STORY with teacher_id or >60w). Platform similarity (CTSS) includes teacher presence (tps) in fingerprint; same teacher + same arc + same band_seq → high block risk.

### Identity and governance
- **Pen-name authors** — author_registry.yaml, positioning_profile, author assets (bio, why_this_book, authority_position, audiobook_pre_intro).
- **Author positioning profiles** — somatic_companion, research_guide, elder_stabilizer; trust posture, vulnerability_band, allowed/forbidden language; CI check_author_positioning.
- **Narrators** — narrator_registry, brand_narrator_assignments, narrator_id in BookSpec and CompiledBook.
- **Brand archetype registry** — Structural validation (brand_archetype_registry.yaml); validate_brand_archetype_registry.py.

### Freebies and immersion
- **Freebie planner** — Deterministic post–Stage 3; freebie_bundle, freebie_bundle_with_formats, cta_template_id, freebie_slug.
- **Freebie registry and selection rules** — Types, output_formats, selection by duration/topic/persona; tier_bundles (Good/Better/Best).
- **Density gate** — validate_freebie_density (identical bundle/CTA/slug thresholds).
- **CTSS freebie/CTA components** — freebie_bundle_signature, cta_signature in similarity index.
- **Asset pipeline** — Canonical topics/personas; plan_freebie_assets (catalog or canonical); create_freebie_assets (HTML/PDF/EPUB/MP3); validate_asset_store; format-first store.
- **Pipeline freebie generation** — generate_freebies_for_book; --formats, --skip-audio, --publish-dir, --asset-store; maintain plan rows in artifacts/freebies/index.jsonl and artifact logs in artifacts/freebies/artifacts_index.jsonl.

### CI and QA
- **Structural entropy** — check_structural_entropy (min word counts, story/exercise family dominance, emotional_role_sequence, compression word count and family diversity).
- **Author positioning CI** — check_author_positioning (profile language bands, first-person/command density).
- **Platform similarity (CTSS)** — check_platform_similarity; block/review thresholds; index append via update_similarity_index.
- **Wave density** — check_wave_density (arc_id, band_seq, slot_sig, exercise placement, emotional_role_sig, compression, angle_id ≥50% same = FAIL).
- **Emotional governance** — emotional_governance_rules.yaml (chapter-level, TTS rhythm, book-level, catalog-level, failure_protocol).
- **Gate #49** — pre_export_check (locale/territory for distribution).
- **Production readiness gates** — run_production_readiness_gates.py (15 + optional freebie gate 16).
- **Systems test** — run_systems_test.py (phases 1–7: config, resolvers, pipeline, freebies, asset pipeline, CI/QA, contracts).

### Observability and simulation
- **Structural drift dashboard** — build_structural_drift_dashboard.py (artifacts/drift/; role distribution, signatures).
- **Monte Carlo CTSS** — run_monte_carlo_ctss.py (duplication risk vs index).
- **Wave orchestrator** — wave_orchestrator.py (balanced wave from candidates; arc/band/slot/ex diversity).
- **Simulation** — run_simulation.py (--n, --phase2, --phase3). Simulation is **synthetic validation** (readiness tooling); for **production 100%** you still need real canaries, CI gate on analyzer, evidence on main, and release smoke + rollback proof — see [docs/RIGOROUS_SYSTEM_TEST.md](RIGOROUS_SYSTEM_TEST.md).

### Config and contracts
- **Topic/engine bindings** — topic_engine_bindings.yaml (allowed_engines per topic).
- **Identity aliases** — identity_aliases.yaml (persona_aliases, topic_aliases).
- **Format selection** — format_registry.yaml, selection_rules.yaml, emotional_role_slot_requirements.yaml.
- **Master arcs** — config/source_of_truth/master_arcs/; engines config/source_of_truth/engines/.
- **OMEGA / Compiled plan schema** — BookSpec, FormatPlan, CompiledBook contracts; COMPILED_PLAN_SCHEMA_CONTRACT.md.

---

## 2. Scale Parts and Anti-Spam Assurance

### What “scale” means here
- **Catalog scale** — Many books (personas × topics × arcs × formats); same atom pools reused; structural variety and drift control matter.
- **Wave scale** — Batches of books released together; no wave may look like “the same book” repeated (same arc, same band sequence, same slot signature, same freebie bundle).
- **Similarity and entropy** — Structural fingerprints (arc, band sequence, slot_sig, exercise placement, story/exercise family vectors, freebie/CTA, emotional role sequence, compression) are indexed and compared so we never publish near-duplicates or farm-like runs.

### Scale-related components
| Component | Role |
|-----------|------|
| **Canonical topics/personas** | **Source of truth:** [unified_personas.md](../unified_personas.md) (10 active personas, 12 active topics). canonical_topics.yaml, canonical_personas.yaml must align with it; validated against topic_engine_bindings and identity_aliases. |
| **Similarity index** | artifacts/catalog_similarity/index.jsonl — one row per compiled plan; CTSS fingerprint (arc, band_seq, slot_sig, exercise_chapters, story_fam_vec, ex_fam_vec, tps, freebie/CTA, role_seq, compression). Append on each plan via update_similarity_index. |
| **Wave density check** | Runs over a batch (--plans-dir or index). FAILs if too many books share same arc_id, band_seq, slot_sig, exercise placement, or emotional_role_sig (and optionally compression). Prevents “same book N times” in one wave. |
| **Freebie density gate** | Over artifacts/freebies/index.jsonl (plan rows, deduped by book_id). FAILs if identical freebie_bundle ratio ≥40%, identical CTA ≥50%, identical slug pattern ≥60%. Thresholds configurable via config/freebies/cta_anti_spam.yaml (density_thresholds). Prevents every book in a wave from offering the same freebie bundle/CTA/slug. |
| **CTA signature index + caps** | artifacts/freebies/cta_signature_index.jsonl (optional); config/freebies/cta_anti_spam.yaml (max_same_cta_signature_per_brand_per_quarter). phoenix_v4/qa/cta_signature_caps.py — FAIL when same CTA wording exceeds cap per brand/quarter. |
| **In-book CTA insertion point** | Spec §10.5: single back-matter insertion (after final integration); pipeline must inject CTA text + URL from plan (cta_template_id, freebie_slug). No CTA in body chapters. |
| **Delivery gate (no placeholders)** | scripts/ci/check_book_output_no_placeholders.py — FAIL if {{...}}, [Placeholder: ...], [Silence: ...] appear in rendered book output. Wired in run_prepublish_gates (§10.6). |
| **Wave CTA diversity** | check_release_wave: weekly_caps max_same_cta_style, max_same_slug_pattern; anti_homogeneity weights cta_diversity, slug_diversity. config/release_wave_controls.yaml. |
| **Structural entropy** | Per-book: story family dominance, exercise family concentration, compression family diversity; min word counts; emotional_role_sequence rules. Prevents one structure or one family dominating a single book. |
| **Emotional governance (catalog)** | Catalog-level: structural_similarity, waveform_entropy, reflection_density (rolling windows). Prevents catalog-wide flattening or clone runs. |
| **Wave orchestrator** | Selects a balanced wave from candidates using arc/band/slot/ex (and density) constraints so the chosen set is diverse by construction. |
| **Drift dashboard** | Observability only; reports role distribution, top signatures, role×band counts so editorial can see over-production of e.g. one role or one arc. |

### Anti-spam assurance (summary)
- **No duplicate books** — Platform similarity (CTSS) blocks or flags plans that are too close to existing index rows (block ≥0.78, review ≥0.65 by default). Same teacher + same arc + same band_seq → high risk, block.
- **No duplicate waves** — Wave density fails the wave if ≥30% same arc, ≥40% same band_seq, ≥50% same slot_sig, ≥60% same exercise placement, ≥40% same emotional_role_sig (and compression rules if used). So a wave cannot be “same structure, different topic” repeated.
- **No freebie spam** — Freebie density fails if bundle/CTA/slug patterns are too identical across the wave (40/50/60%). Reseed (slug suffix) can vary slug when wave_index is provided.
- **No single-family dominance** — Structural entropy fails if one story structure_family >70% or one exercise family >60% in a book; compression family >70% fails. Emotional governance caps reassurance phrases, metaphor family, carry line collision.
- **No catalog flattening** — emotional_governance_rules catalog_level: structural_similarity, waveform_entropy, reflection_density (rolling windows). Failure protocol: atom quarantine, chapter block, book block, catalog freeze.

Together, these give **structural anti-spam**: we never ship waves of near-identical books, same freebie bundle everywhere, or catalog collapse to a single “shape.”

---

## 3. All Knobs for Changes

### 3.1 Pipeline CLI (`scripts/run_pipeline.py`)

| Flag | Effect |
|------|--------|
| `--topic` | Topic ID (required with --persona unless --input). |
| `--persona` | Persona ID. |
| `--installment` | Installment number (format selection). |
| `--series` | Series ID. |
| `--angle` | Angle ID. |
| `--seed` | Determinism seed (default: pipeline_seed_001). |
| `--runtime-format` | Force Stage 2 runtime (e.g. standard_book). |
| `--structural-format` | Force Stage 2 structural (e.g. F006). |
| `--input` | YAML with topic_id, persona_id, etc. (Stage 2 input). |
| `--arc` | **Required.** Path to master arc YAML. |
| `--teacher` | Teacher ID (Teacher Mode). |
| `--author` | Author ID (pen-name; from author_registry). |
| `--narrator` | Narrator ID (default from brand_narrator_assignments when omitted). |
| `--out` | Write CompiledBook JSON path. |
| `--generate-freebies` | Generate HTML freebie artifacts (default when --out). |
| `--no-generate-freebies` | Disable freebie generation when writing plan. |
| `--formats` | Comma-separated: html,pdf,epub,mp3 (freebie formats). |
| `--skip-audio` | Omit mp3 from freebie formats. |
| `--publish-dir` | Copy freebies here (e.g. public/free). |
| `--asset-store` | Asset store root for pre-created assets. |
| `--render-book` | Stage 6: render plan to prose (txt) after writing plan. |
| `--render-formats` | Comma-separated book output formats (default: txt). |
| `--render-dir` | Output dir for rendered book (default: artifacts/rendered/\<plan_id\>). |

### 3.2 Asset pipeline and observability CLI

| Script | Notable flags | Default / effect |
|--------|----------------|------------------|
| plan_freebie_assets.py | `--catalog`, `--topics`, `--personas`, `--out` | Catalog YAML or canonical topics+personas; out default artifacts/asset_planning/manifest.jsonl. |
| create_freebie_assets.py | `--manifest`, `--format`, `--store`, `--tts-config` | format=html,pdf; store default artifacts/freebie_assets/store. |
| validate_asset_store.py | `--store`, `--manifest`, `--rules` | Validate store against manifest. |
| update_similarity_index.py | `--plan`, `--index`, `--teacher-id` | Append one CTSS row to index. |
| build_structural_drift_dashboard.py | `--plans-dir`, `--plan-list`, `--index`, `--out-dir` | index default artifacts/catalog_similarity/index.jsonl; out-dir default artifacts/drift. |
| run_simulation.py | `--n`, `--phase2`, `--phase3` | Simulation runs. |
| pre_export_check.py (Gate #49) | `--plan` | Locale/territory consistency. |

### 3.3 CI / QA script flags

| Script | Notable flags | Default / effect |
|--------|----------------|------------------|
| check_structural_entropy.py | `--plan`, `--book-spec`, `--atoms-dir`, `--teacher-mode`, `--allow-missing-role-seq` | Plan path; allow legacy plans without emotional_role_sequence. |
| check_author_positioning.py | `--plan`, `--book-spec`, `--atoms-dir` | Plan (and optional spec/atoms). |
| check_platform_similarity.py | `--plan`, `--plans-dir`, `--index`, `--block`, `--review` | block=0.78, review=0.65. |
| check_wave_density.py | `--plans-dir`, `--plan-list`, `--index` | Batch of plans. |
| validate_freebie_density.py | `--index` (or plans-dir) | artifacts/freebies/index.jsonl; thresholds from config/freebies/cta_anti_spam.yaml when present. |
| cta_signature_caps.py | `--index`, `--config`, `--write-index` | CTA signature caps per brand/quarter; optional cta_signature_index.jsonl. |
| check_book_output_no_placeholders.py | `--wave-rendered-dir` or &lt;dir&gt; | Rendered book .txt; FAIL if placeholders/metadata leak (§10.6). |
| run_production_readiness_gates.py | (none) | Gate 16 runs when freebie index has ≥2 plan rows. Pre-publish: run_prepublish_gates includes delivery gate (book output no placeholders). |

### 3.4 Full catalog and standalone quality tools

| Script / module | Notable flags | Default / effect |
|-----------------|----------------|------------------|
| **scripts/generate_full_catalog.py** | `--max-books`, `--brand`, `--seed`, `--candidates-dir`, `--skip-wave-selection`, `--wave-size`, `--out-wave`, `--generate-freebies` | Full catalog: portfolio → BookSpec → compile → wave selection. First 10 Books: `--brand <id> --max-books 10 --skip-wave-selection`. |
| **phoenix_v4/quality/story_atom_lint.py** | `--path`, `--json-out`, `--fail-on` | Lint STORY atoms (specificity, conflict, cost, pivot); PASS/WARN/FAIL. File or directory of .txt/.md. |
| **phoenix_v4/quality/transformation_heatmap.py** | `--file` or `--plan`, `--json-out`, `--ascii`, `--last-n` | Per-chapter recognition/reframe/challenge/relief/identity_shift; ending strength. |
| **phoenix_v4/quality/memorable_line_detector.py** | `--file` or `--plan`, `--json-out`, `--min-score`, `--max-lines` | Highlight-density candidates; output includes highlight_density_per_1000_words. |
| **phoenix_v4/quality/marketing_assets_from_lines.py** | `--mem-lines`, `--brand`, `--topic`, `--persona`, `--out-dir`, `--top-n` | From memorable-line JSON: quotes.csv, pin_captions.txt, landing_page_hooks.txt, trailer_lines.txt, email_subject_lines.txt. |

These quality tools are **standalone** (run manually or in review); not part of CI. See [phoenix_v4/quality/README.md](../phoenix_v4/quality/README.md). Human checkpoint docs: [CREATIVE_QUALITY_VALIDATION_CHECKLIST.md](CREATIVE_QUALITY_VALIDATION_CHECKLIST.md), [FIRST_10_BOOKS_EVALUATION_PROTOCOL.md](FIRST_10_BOOKS_EVALUATION_PROTOCOL.md).

### 3.5 Thresholds in code (CI / QA)

| Source | Knob | Value | Meaning |
|--------|------|--------|---------|
| check_structural_entropy.py | MIN_STORY_WORDS | 120 | FAIL if STORY atom < 120w. |
| check_structural_entropy.py | MIN_EXERCISE_WORDS | 90 | FAIL if EXERCISE atom < 90w. |
| check_structural_entropy.py | MAX_STORY_FAMILY_SHARE | 0.70 | FAIL if one story structure_family > 70%. |
| check_structural_entropy.py | WARN_STORY_FAMILY_SHARE | 0.55 | WARN if > 55%. |
| check_structural_entropy.py | MAX_FAMILY_CONCENTRATION (ex) | 0.60 | FAIL if one exercise family > 60%. |
| check_structural_entropy.py | COMPRESSION family | 0.70 | FAIL if one compression_family > 70% of chapters. |
| check_structural_entropy.py | COMPRESSION word count | 40–120 | FAIL outside range. |
| check_wave_density.py | arc_id share | 0.30 | FAIL wave if ≥30% same arc_id. |
| check_wave_density.py | band_seq share | 0.40 | FAIL if ≥40% identical band_seq. |
| check_wave_density.py | slot_sig share | 0.50 | FAIL if ≥50% identical slot_sig. |
| check_wave_density.py | exercise placement | 0.60 | FAIL if ≥60% identical. |
| check_wave_density.py | emotional_role_sig | 0.40 | FAIL if ≥40% identical. |
| check_wave_density.py | compression pos+len | 0.50 each | FAIL if ≥50% identical on both. |
| validate_freebie_density.py | THRESHOLD_BUNDLE | 0.40 | FAIL if identical freebie_bundle ≥ 40%. |
| validate_freebie_density.py | THRESHOLD_CTA | 0.50 | FAIL if identical CTA ≥ 50%. |
| validate_freebie_density.py | THRESHOLD_SLUG | 0.60 | FAIL if identical slug pattern ≥ 60%. |
| check_platform_similarity.py | --block | 0.78 | FAIL if worst similarity ≥ block. |
| check_platform_similarity.py | --review | 0.65 | WARN if worst ≥ review. |
| check_author_positioning.py | research_guide first_person | 0.08 | FAIL if first_person_reflection > 8%. |
| check_author_positioning.py | somatic_companion command | 0.12 | FAIL if command_language density > 12%. |
| check_author_positioning.py | high vulnerability narrative | 0.30 | Personal narrative ≤ 30% of chapter. |

### 3.6 Emotional governance (phoenix_v4/qa/emotional_governance_rules.yaml)

| Layer | Knob | Value | Meaning |
|-------|------|--------|---------|
| chapter | escalation_verbs (high temp) | 3 | ≥3 required in high-temp chapter. |
| chapter | sensory_words | 2 | ≥2 required. |
| chapter | reaction_markers | 1 | Required if ≥2 action verbs. |
| chapter | cognitive_body_ratio | warn 3, fail 5 | cognitive_count/body_count. |
| tts_rhythm | long_warn_threshold | 18 | Words. |
| tts_rhythm | max_long_fail_percent | 0.30 | >30% sentences >18w → FAIL. |
| tts_rhythm | max_questions_per_chapter | 2 | >2 → FAIL. |
| book | misfire_tax / silence_beat / never_know | min 2 (standard), 1 (micro) | Per tag. |
| book | integration_modes | min 3 (standard), 2 (micro) | No consecutive same; STILL-HERE only final. |
| book | reassurance_cap | warn 40%, fail 60% | Phrase in chapters. |
| book | metaphor_family | rolling 10, max 40% | No family >40% in 10-book window. |
| catalog | structural_similarity | max 0.20 structural, 0.15 story | Overlap. |
| catalog | waveform_entropy | min 3 distinct curves in 10-book window | FAIL else. |
| catalog | reflection_density | max 2 consecutive same tier | FAIL else. |

### 3.7 Config YAML knobs (selection)

| File | Knob / area | Purpose |
|------|----------------|--------|
| config/freebies/freebie_selection_rules.yaml | min_duration_minutes, max_per_book | When to attach companion, assessment, etc. |
| config/freebies/freebie_selection_rules.yaml | identical_bundle_ratio_max: 0.40, identical_cta_ratio_max: 0.50, identical_slug_pattern_ratio_max: 0.60 | Density limits (can mirror validate_freebie_density). |
| config/format_selection/selection_rules.yaml | topic_complexity, installment_strategy, persona_constraints | Format selection (opener/deepening/rotation; forbidden_formats, preferred_runtime, max/min chapter_count). |
| config/format_selection/format_registry.yaml | structural_formats, runtime_formats, chapter_range, tier | Format definitions and word ranges. |
| config/source_of_truth/chapter_planner_policies.yaml | book_size_by_chapters, role_distribution_targets, quotas, archetypes.slot_policy, archetypes.allowed_next | Chapter planner policy: arc-role distribution bounds, book-size exercise/reflection caps, transition compatibility, and per-archetype slot presence/weights. |
| config/catalog_planning/capacity_constraints.yaml | max_books_per_topic_per_wave, min_story_atoms_per_topic_persona | Capacity. |
| config/catalog_planning/brand_teacher_matrix.yaml | teachers[], teacher_constraints (max_books_per_topic, max_books_per_persona) | Teachers per brand; diversity guardrails. Release pacing from config/release_velocity and generate_weekly_schedule.py (see docs/RELEASE_VELOCITY_AND_SCHEDULE.md). |
| config/catalog_planning/teacher_persona_matrix.yaml | teachers.*.allowed_personas, allowed_engines, preferred_locales | Teacher/persona/engine compatibility; invalid combo fails before Stage 1. |
| config/catalog_planning/brand_teacher_assignments.yaml | default teacher_id (and brand_id) per series/brand | Resolver when --teacher/--brand omitted. |
| config/teachers/teacher_registry.yaml | teachers.*.allowed_topics, allowed_engines, teacher_mode_defaults (require_teacher_story, require_teacher_exercise) | Per-teacher registry for pipeline and allocator. |
| config/catalog_planning/brand_archetype_registry.yaml | max_mid_form_ratio, duration_strategy, discount_ratio | Per-brand. |
| config/authoring/author_positioning_profiles.yaml | authority_type, trust_anchor_style, vulnerability_band, allowed_language, forbidden_language | Per profile (somatic_companion, research_guide, elder_stabilizer). |
| config/validation.yaml | duration_min_seconds, duration_max_seconds, file_size_min_mb | Asset validation (e.g. MP3). |
| config/tts/engines.yaml | engines, mapping (freebie_type → engine), voices | TTS for asset pipeline. |
| config/asset_lifecycle.yaml | regenerate_when (template_modified, tts_engine_upgraded, canonical_topics_changed), auto_prune | When to regenerate or prune assets. |

### 3.8 Teacher Mode knobs

| Where | Knob | Purpose |
|-------|------|--------|
| **Pipeline** | `--teacher` | Teacher ID for Teacher Mode; validated against teacher_persona_matrix (allowed_personas, allowed_engines). Default from brand_teacher_assignments when omitted. |
| **Plan output** | `teacher_id`, `teacher_mode` | Written to compiled plan when --teacher set; Stage 6 prose_resolver uses teacher_banks when teacher_mode. |
| **update_similarity_index.py** | `--teacher-id` | Teacher id for CTSS row (teacher presence / tps in fingerprint). |
| **check_structural_entropy.py** | `--teacher-mode`, `--atoms-dir` | Enable teacher-mode-only checks (chapter exercise/anchor, teacher STORY); atoms-dir can point at teacher_banks/\<id\>/approved_atoms. |
| **config/catalog_planning/teacher_persona_matrix.yaml** | teachers.*.allowed_personas, allowed_engines, preferred_locales | Per-teacher persona/engine compatibility; invalid combo raises before Stage 1. |
| **config/catalog_planning/brand_teacher_assignments.yaml** | default teacher_id per brand/series | Resolver uses when --teacher not supplied. |
| **config/catalog_planning/brand_teacher_matrix.yaml** | teachers[], teacher_constraints | Teachers per brand; diversity. Release pacing: config/release_velocity, generate_weekly_schedule.py. |
| **config/teachers/teacher_registry.yaml** | teachers.*.allowed_topics, allowed_engines, teacher_mode_defaults (require_teacher_story, require_teacher_exercise) | Per-teacher registry; pipeline and allocator read this. |
| **SOURCE_OF_TRUTH/teacher_banks/\<teacher_id\>/** | approved_atoms/\<slot_type\>/*.yaml, doctrine/, kb/ | Teacher-scoped atom pools and doctrine; Stage 3 and Stage 6 load from here when teacher_mode. |
| **CTSS (platform similarity)** | tps weight 0.11 | Teacher presence in fingerprint; same teacher + same arc + same band_seq → high block risk. |

### 3.9 CTSS weights (check_platform_similarity.py)

| Component | Weight | Note |
|-----------|--------|------|
| arc | 0.20 | Match arc_id. |
| band_seq | 0.12 | LCS-like. |
| slot_sig | 0.11 | Exact match. |
| exercise placement | 0.13 | Jaccard. |
| story_fam_vec | 0.07 | L1 sim. |
| ex_fam_vec | 0.07 | L1 sim. |
| tps | 0.11 | Teacher presence. |
| freebie_bundle | 0.04 | Signature. |
| cta | 0.04 | Signature. |
| compression_pos | 0.02 | DEV SPEC 2. |
| compression_len | 0.02 | DEV SPEC 2. |
| role_seq | 0.06 | DEV SPEC 3. |

(Total 1.0; adjust in code if you need to rebalance.)

### 3.10 Systems test

| Flag | Effect |
|------|--------|
| `--all` | Run all phases 1–7. |
| `--phase 1` … `--phase 7` | Run selected phases (repeatable). |
| `--output-dir` | Default artifacts/systems_test. |
| `--strict` | Exit 1 if any check failed. |

---

To change behavior: adjust the relevant config file or (for CI thresholds) the script constants/defaults above; then run systems test and production gates to confirm.
