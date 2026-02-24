# DupEval — Platform Duplication Evaluation Spec

**Purpose:** Pre-publish structural similarity gate to prevent near-identical arc clones, teacher×persona skin swaps, template reuse, and catalog farm flags.  
**Authority:** This spec; implementation: `scripts/ci/check_platform_similarity.py` (extended CTSS), `scripts/ci/check_wave_density.py`, `scripts/ci/update_similarity_index.py`. See also [COMPILED_PLAN_SCHEMA_CONTRACT.md](./COMPILED_PLAN_SCHEMA_CONTRACT.md) for CI schema requirements.  
**Pipeline order:** compile → structural_entropy_check → **check_platform_similarity** → update_similarity_index → publish.

DupEval does **not** compare prose, use embeddings, or do NLP. It compares **structural fingerprints only**.

---

## 1. Layers (extended CTSS implementation)

Current implementation uses a single **extended CTSS** (no separate TSS/MSS in index). Fingerprint row: book_id, teacher_id, arc_id, band_seq (list), slot_sig, exercise_chapters, story_fam_vec, ex_fam_vec, tps (teacher presence sequence), engine_id, format_id.

| Component | Weight |
|-----------|--------|
| arc match | 0.22 |
| band sequence (LCS ratio) | 0.20 |
| slot_sig match | 0.12 |
| exercise placement (Jaccard) | 0.14 |
| story_fam_vec (norm L1 sim) | 0.10 |
| ex_fam_vec (norm L1 sim) | 0.10 |
| tps (norm L1 sim) | 0.12 |

Story/exercise family vectors come from plan when per-slot `structure_family` / `exercise_family` are embedded; otherwise empty. TPS = per-chapter bucket (0/1/2/3) of teacher-tagged slots.

---

## 2. Band sequence extraction priority

Standardized (same for index and comparison):

1. `emotional_temperature_sequence`
2. `required_band_by_chapter`
3. `emotional_band_sequence`
4. `dominant_band_sequence`
5. Per-chapter fallback from plan chapters

---

## 3. Thresholds

Extended CTSS script (`check_platform_similarity.py`) uses a single **--block** (default 0.78) and **--review** (default 0.65). Optional future: same/different teacher thresholds.

| Context | Block (FAIL) | Review (WARN) |
|---------|--------------|---------------|
| (current) | ≥ --block | --review to --block |
| Different teacher (optional) | ≥ 0.75 | 0.65 – 0.75 |
| Same teacher (optional) | ≥ 0.85 | 0.72 – 0.85 |
| Same teacher + same arc (optional) | ≥ 0.70 | — |

**Strategic rule:** Same teacher + same arc + same band sequence → always block (catalog farm risk).

---

## 4. Wave density check

Run on release wave (batch). FAIL if:

- > 30% of books share same `arc_id`
- > 40% share identical `band_seq`
- > 50% share identical `slot_sig`
- > 60% share identical exercise placement pattern

Script: `scripts/ci/check_wave_density.py` (--plans-dir, --plan-list, or --index).

---

## 5. Index storage

Path: `artifacts/catalog_similarity/index.jsonl`.

Each line is a JSON object with: book_id, teacher_id, arc_id, band_seq (list), slot_sig, exercise_chapters, story_fam_vec, ex_fam_vec, tps, engine_id, format_id.

Append: `scripts/ci/update_similarity_index.py --plan <path> --index <path> [--teacher-id <id>]`.

---

## 6. Interaction with structural entropy

- Structural entropy enforces story family dominance (FAIL if one story structure_family > 70%), `[EXPANDED]` forbidden in body, teacher anchor = STORY with teacher_id or atom with teacher_id and >60 words, and intro style diversity (WARN if < 3 distinct intro style IDs).
- DupEval uses the same family distributions in CTSS so that index and new plan are comparable.

---

## 7. Run pipeline

After compile, `run_pipeline.py` enforces `peak_intensity_limit` from `config/catalog_planning/teacher_persona_matrix.yaml` (max(band_sequence) ≤ peak_intensity_limit) when `--teacher` is set.
