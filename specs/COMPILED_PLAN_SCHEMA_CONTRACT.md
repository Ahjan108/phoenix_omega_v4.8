# Compiled Plan Schema Contract (CI compatibility)

**Purpose:** Minimum schema guarantees so entropy, similarity, and wave-density CI scripts stay stable across plan schema drift.  
**Authority:** Stage 3 output is defined in [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md). This doc adds **CI-facing** requirements and recommendations.

---

## 1. Stage 3 emitted fields (systems doc)

Stage 3 (assembly compiler) emits **CompiledBook** with at least:

- `plan_hash`
- `chapter_slot_sequence`
- `atom_ids`
- `dominant_band_sequence`
- `arc_id` (when arc used)
- `emotional_temperature_sequence` (when available)
- `reflection_strategy_sequence` (when available)
- `chapter_archetypes` (effective per-chapter archetypes from Stage 3 policy layer)
- `chapter_exercise_modes` (none/micro/full per chapter)
- `chapter_reflection_weights` (light/standard/heavy per chapter)
- `chapter_story_depths` (light/standard/deep per chapter)
- `chapter_planner_warnings` (non-fatal policy warnings)

Pipeline (run_pipeline) attaches after Stage 3: **freebie fields** — `freebie_bundle`, `freebie_bundle_with_formats` (list of `{freebie_id, formats}`), `cta_template_id`, `freebie_slug`; **identity** — `narrator_id` (from BookSpec; resolved from brand when not supplied). **Intro/ending variation (when enabled):** `pre_intro_signature`, `ending_signature`, `opening_style_id`, `integration_ending_style_id`, `carry_line_style_id`, `carry_line`; resolved pre-intro blocks live in `author_assets["audiobook_pre_intro"]`. See [INTRO_CONCLUSION_VARIATION_SPEC.md](./INTRO_CONCLUSION_VARIATION_SPEC.md). Pipeline also appends to artifacts/freebies/index.jsonl when writing a plan and to artifacts/pre_intro_signatures.jsonl when intro/ending variation is enabled. See [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md) and [PHOENIX_FREEBIE_SYSTEM_SPEC.md](./PHOENIX_FREEBIE_SYSTEM_SPEC.md).

**Stage 6 (book renderer)** consumes the compiled plan for manuscript/QA output: `phoenix_v4/rendering` resolves `atom_ids` to prose from atoms/, compression_atoms, teacher_banks; QA script `scripts/render_plan_to_txt.py` and pipeline `--render-book` use Stage 6. See [../docs/V4_FEATURES_SCALE_AND_KNOBS.md](../docs/V4_FEATURES_SCALE_AND_KNOBS.md).

---

## 2. What CI scripts need (minimum contract)

| Needed by              | Field(s)                                                                 | Required? | Notes |
|------------------------|---------------------------------------------------------------------------|----------|-------|
| Similarity             | `arc_id`                                                                 | ✅        | string |
| Similarity + Wave      | One of: `emotional_temperature_sequence` / `required_band_by_chapter` / `dominant_band_sequence` | ✅ | At least one reliably present |
| Similarity + Wave + Entropy | `chapter_slot_sequence`                                            | ✅        | Must be scannable for slot types (list of chapters; each chapter list of slot types or slot objects) |
| Similarity             | `format_id` or `format_structural_id` or `structural_format`             | ✅        | For slot_sig |
| Similarity (extended)  | Per-slot `structure_family` for STORY                                    | ✅ if family sim desired | Best: embed at compile time |
| Similarity (extended)  | Per-slot `exercise_family` for EXERCISE                                 | ✅ if family sim desired | Same |
| Similarity (extended)  | Per-slot `teacher_id` or `teacher.teacher_id`                            | ✅ if TPS desired | Otherwise TPS stays all-zero |
| Entropy (dominance)    | Per-slot `structure_family` (or from atoms when atoms_dir provided)      | ✅        | For dominance share |
| Entropy (intro dist)   | `author_intro_style_id` (per-slot or per-chapter when embedded)          | ✅ for WARN | For intro style distribution |

---

## 3. Critical compatibility guarantee

**`chapter_slot_sequence`** must be an array of chapters; each chapter must expose a list of slots; each slot must carry a **slot type** (e.g. `slot_type` or `type`).

- Current shape: list of lists of strings, e.g. `[["HOOK","SCENE","STORY",...], ...]`. Each inner list = one chapter; each string = slot type.
- Richer shape (for family/TPS): list of lists of objects, e.g. `[[{"slot_type":"STORY","structure_family":"NARRATIVE"}, ...], ...]`. CI can then read `structure_family`, `exercise_family`, `teacher_id` from the plan without loading atoms.

That keeps entropy, similarity, and wave scripts stable against plan schema drift.

---

## 4. Stage 3 derived fields (implemented)

Stage 3 (assembly compiler) **emits** these derived structural fields:

| Field                           | Type      | Description |
|---------------------------------|-----------|-------------|
| `slot_sig`                      | string    | Stable hash of slot layout: format_id + sha256(chapter_slot_sequence). |
| `exercise_chapters`            | list[int] | Chapter indices (0-based) that contain an EXERCISE slot. |
| `emotional_temperature_sequence` | list     | From arc when present; else dominant_band_sequence as strings. Required for wave density. |

Pipeline output (run_pipeline) includes `plan_id`, `format_id`, `engine_id`, `exercise_chapters`, `slot_sig`, and `emotional_temperature_sequence` so CI and wave density use them with no fallback extraction.

Pipeline output also includes chapter policy fields (`chapter_archetypes`, `chapter_exercise_modes`, `chapter_reflection_weights`, `chapter_story_depths`, `chapter_planner_warnings`) and preserves variation selector archetypes as `variation_chapter_archetypes` for diagnostics.
