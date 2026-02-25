# V4.5 Is Production-Ready When These 17 Conditions Are True

No fluff. No telemetry. No repair logic. Only release-critical gates.

**Authority:** [PHOENIX_V4_5_WRITER_SPEC.md](./PHOENIX_V4_5_WRITER_SPEC.md) · [PHOENIX_V4_CANONICAL_SPEC.md](./PHOENIX_V4_CANONICAL_SPEC.md) · `phoenix_v4/qa/emotional_governance_rules.yaml` · `config/` (topic_engine_bindings, topic_skins) · `registry/` (section packs) · `atoms/` (canonical story atoms)

**Run automatable checks:** From repo root, `python scripts/run_production_readiness_gates.py`. Then run `python simulation/run_simulation.py --n 10 --phase2 --phase3` for release simulation (Gate 12). **CI must have `jsonschema` installed;** Gate 17 and 17b enforce this and ops artifact validation (see [scripts/ci/README.md](../scripts/ci/README.md)).

---

## 1. Canonical Spec Is Single Source of Truth

- [PHOENIX_V4_5_WRITER_SPEC.md](./PHOENIX_V4_5_WRITER_SPEC.md) (or merged master spec) is the only writing authority.
- No parallel Somatic spec.
- No duplicate rule blocks.
- Section 16 exists (Emotional QA & Drift Governance).

**If multiple specs define writing behavior → Not ready.**

---

## 2. SOURCE_OF_TRUTH Coverage Is Complete

For every **persona × topic × role**:

- Minimum K-table variant counts met
- No empty pools
- No role gaps
- No untagged atoms

**If any slot cannot be filled deterministically → Not ready.**

*Ref:* Canonical Spec Part 3 (K-tables, capability check); `phoenix_v4/planning/`, coverage_checker.

---

## 3. K-Table Thresholds Are Enforced

Numeric sufficiency rules exist and are validated:

- Per-role minimums
- Per-slot minimums
- Per-persona minimums

CI fails if under threshold.

**If thresholds are descriptive only (not enforced) → Not ready.**

*Ref:* Canonical Spec §3.1, §4.3; format policies, `k_tables/`; `phoenix_v4/planning/coverage_checker.py`.

---

## 4. Assembly Is Deterministic

Given the same **persona + topic + format + seed** → identical structure.

- No randomness without seed control.
- No freestyle writing during assembly.

**If output varies without seed change → Not ready.**

*Ref:* Canonical Spec Part 3 (plan compiler determinism).

---

## 5. Emotional QA (Section 16) Passes

Each assembled book satisfies:

- ≥ 1 volatile chapter
- ≥ 3 escalation verbs (high temp)
- ≥ 2 sensory markers (high temp)
- ≥ 1 reaction marker when actions present
- Cognitive/body ratio ≤ 5

If any fail → block export.

**If emotional QA is advisory only → Not ready.**

*Ref:* Writer Spec §16; `phoenix_v4/qa/emotional_governance_rules.yaml`; simulation Phase 3.

---

## 6. TTS Rhythm Governance Passes

Per chapter:

- ≤ 2 question marks
- ≤ 30% long sentences (> 18 words)
- Sentence distribution balanced
- No monotone paragraph runs

**If robotic flattening occurs unchecked → Not ready.**

*Ref:* Writer Spec §3, §12; emotional_governance_rules.yaml (tts_rhythm).

---

## 7. Drift Detection Passes (Book-Level)

- No 3 same-temperature chapters in a row
- No reassurance phrase in > 60% of chapters
- Carry lines unique within teacher/topic/persona stack
- Metaphor family ≤ 40% in rolling 10-book window

**If sameness creeps across stack → Not ready.**

*Ref:* Writer Spec §13, §16; emotional_governance_rules.yaml (book_level); simulation Phase 2.

---

## 8. Structural Similarity Limits Pass

Across release batch:

- ≤ 20% structural overlap
- ≤ 15% story-body overlap
- ≥ 3 distinct emotional waveform shapes per 10-book window

**If books feel templated → Not ready.**

*Ref:* Writer Spec §16.6; emotional_governance_rules.yaml (catalog_level).

---

## 9. Persona Hydration Is Enforced

Each book contains:

- Persona-specific surface nouns
- Location overlays where defined
- Vocabulary steering via config/topic_skins.yaml (or overlays)

**If generic voice leaks across personas → Not ready.**

*Ref:* Writer Spec §17, §18; Canonical Spec; story_bank location_variables, cultural_overlays.

---

## 10. No Forbidden Resolution Language

Across entire book: no resolution or closure promises.

Examples of forbidden: “You are healed,” “You will overcome,” “This ends here,” “Everything changes now,” and any closure promise.

**If resolution creeps in → Not ready.**

*Ref:* Writer Spec §11; Canonical Spec §4.4 (forbidden content).

---

## 11. CI Failure Protocol Is Active

On violation:

- Atom → quarantined
- Chapter → assembly blocked
- Book → export blocked
- Stack → release frozen

**If rules can be bypassed manually → Not ready.**

*Ref:* Writer Spec §16.7; emotional_governance_rules.yaml (failure_protocol).

---

## 12. Release Simulation Passes

Before batch release:

- Coverage report clean
- Emotional QA clean
- Similarity report clean
- Waveform entropy clean
- No WARN stacking across same vector

**If you cannot simulate before publish → Not ready.**

*Ref:* `simulation/run_simulation.py` (Phase 1, 2, 3); artifacts.

---

## 13. Forward Momentum Trigger (FMT) Enforced for Full-Book Formats

For every **full-book** format (deep_book, extended_book, standard_book, etc.):

- Final integration satisfies at least one FMT type: unresolved mechanism, identity tension, social cliff, curiosity hook.
- No full book may end with complete closure; binge/continuation hook is required.

**If full books close without FMT → Not ready.**

*Ref:* Writer Spec §8; Canonical Spec Part 4 (FMT gate); [V4_6_BINGE_OPTIMIZATION_LAYER.md](./V4_6_BINGE_OPTIMIZATION_LAYER.md).

---

## 14. Repo-Root config / registry / atoms Integrity Validated

Before release:

- **config/** — `topic_engine_bindings.yaml` and `topic_skins.yaml` present and valid for all in-scope topics.
- **registry/** — Section packs (e.g. registry_grief.yaml) present where required; pipeline can resolve `SECTIONS_REGISTRY_FILE`.
- **atoms/** — Canonical story atoms under `atoms/<persona>/<topic>/<engine>/` meet coverage expectations for the release batch; no missing persona/topic/engine paths that the plan compiler expects.

**If config/registry/atoms are missing or incomplete for release scope → Not ready.**

*Ref:* Canonical Spec Part 5 (§5.1); REPO_FILES.md; get_these/README.md.

---

## 15. Full Pipeline (Stage 1→2→3) Runnable

- **Stage 1** (catalog planner) produces BookSpec from `config/catalog_planning/`.
- **Stage 2** (format selector) produces FormatPlan from topic/persona/installment.
- **Stage 3** (assembly compiler) reads `atoms/`, produces CompiledBook (plan_hash, chapter_slot_sequence, atom_ids).

Run: `python scripts/run_pipeline.py --topic relationship_anxiety --persona nyc_exec --out artifacts/golden_plans/out.plan.json`. Gate script runs this and validates output.

**If pipeline script or any stage module is missing or fails → Not ready.**

*Ref:* specs/OMEGA_LAYER_CONTRACTS.md; phoenix_v4/planning/catalog_planner.py, format_selector.py, assembly_compiler.py; scripts/run_pipeline.py.

---

## 16. Freebie Density (Phase 3, when using freebies)

When releasing a wave that includes freebie attachment:

- Run freebie density gate on the wave so no more than 40% identical bundle, 50% identical CTA, 60% identical slug pattern.

Run: `PYTHONPATH=. python3 phoenix_v4/qa/validate_freebie_density.py --index artifacts/freebies/index.jsonl` (or `--plans-dir <dir>` with compiled plan JSONs). Production readiness script runs this when index has ≥2 rows (skipped only when index is missing or has 0–1 rows).

**If wave exceeds freebie density thresholds → Not ready for release.**

*Ref:* specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md §10; phoenix_v4/qa/validate_freebie_density.py.

---

## 17. jsonschema required and ops artifact validation (non-optional)

- **jsonschema** must be installed in the environment (e.g. `pip install jsonschema` or `pip install -r requirements.txt`). Gate 17 fails if `import jsonschema` raises.
- When `artifacts/ops` or `artifacts/waves` exists, **Gate 17b** runs `scripts/ci/validate_ops_artifacts.py`; schema validation must pass. Ops validation cannot be skipped in CI.

**If jsonschema is missing or ops validation is skipped → Not ready.**

*Ref:* [scripts/ci/README.md](../scripts/ci/README.md); `scripts/run_production_readiness_gates.py` (Gate 17, 17b); `scripts/ci/validate_ops_artifacts.py`.

---

## When All 17 Are True

You have:

- Deterministic assembly
- Emotional force enforcement
- TTS-safe rhythm
- Drift resistance
- Catalog-level uniqueness
- No repair dependency
- **FMT enforced for full books (binge layer)**
- **Repo-root config, registry, and atoms integrity**
- Industrial publishing integrity

That is production-grade.

---

## Still to do (whole system)

These 17 conditions are the release gate. What remains to *finish the whole system* (e.g. coverage enforcement wired in CI, Gate #49 in distribution pipeline, optional freebie/narrator planning) is in the canonical systems doc and planning status:

- [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md) — § Remaining to finish whole system
- [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md)
