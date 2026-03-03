# Golden plans (Stage 3 API freeze)

**Purpose:** Phase 1 deliverable. Same compiler input must produce the same plan hash and same chapter/atom sequences. Golden plans lock the Stage 3 API and make "stabilize" measurable.

**Contract (see specs/OMEGA_LAYER_CONTRACTS.md):**

- **Input:** teacher_id, persona_id, topic_id, format_id (structural + runtime optional), seed
- **Output (minimal):** plan_hash, chapter_slot_sequence, atom_ids [, dominant_band_sequence]

**Directory layout:**

- `example_input.yaml` — One canonical input (frozen Stage 3 API). Use as template for new fixtures.
- `example_input_stage2.yaml` — Stage 2 input (topic_id, persona_id, installment_number). No format_id; FormatPlan is produced by the format selector.
- `example_format_plan.json` — FormatPlan from Stage 2 for `example_input_stage2.yaml`. Generate with: `python3 -m phoenix_v4.planning.format_selector --topic relationship_anxiety --persona nyc_exec --installment 1 --out artifacts/golden_plans/example_format_plan.json`.
- `example.plan.json` — Placeholder showing required contract shape (plan_hash, chapter_slot_sequence, atom_ids). Replace with real compiler output.
- `*.plan.json` — Compiled plan output (when plan compiler writes here). Name by input digest or book_id.
- `*.expected.json` — Optional: expected plan_hash and sequences for determinism regression.

**Stage 2 → Stage 3 path:** For input that omits format (topic + persona + installment only): run the format selector on `example_input_stage2.yaml` (or equivalent) to get a FormatPlan; pass that plan (format_structural_id, format_runtime_id, tier, blueprint_variant, target_chapter_count, word_target_range) into the Stage 3 compiler. Same Stage 2 input must always produce the same FormatPlan (determinism).

**How to add a golden plan:**

1. Run the plan compiler with input from `example_input.yaml` (or equivalent), or from Stage 2: use `example_format_plan.json` + identity fields as compiler input.
2. Write output to `artifacts/golden_plans/<book_id>.plan.json` with keys: `plan_hash`, `chapter_slot_sequence`, `atom_ids`, and optionally `dominant_band_sequence`.
3. Run `python scripts/validate_golden_plan.py artifacts/golden_plans/<book_id>.plan.json` to validate shape.
4. For determinism: run compiler twice with same input; both outputs must have identical plan_hash and sequences.

**Validation script:** `scripts/validate_golden_plan.py` — checks required fields and types; optional comparison to .expected.json.
