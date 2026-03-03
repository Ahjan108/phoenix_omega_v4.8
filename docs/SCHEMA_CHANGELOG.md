# Schema Changelog

All changes to ops and wave optimizer JSON schemas must be recorded here. Any change requires:

1. **Version bump** in the schema (e.g. `const: "1.0"` → `const: "1.1"`)
2. **Registry update** in `config/ops_schema_registry.yaml` (`current_version`, and schema_path if renamed)
3. **Migration note** in this file

---

## 2026-03-03

### Added

- **Distribution-only church brand policy** (ADR-002) — Church brands (e.g. norcal_dharma) are identity/distribution only: teacher_id=default_teacher, excluded from brand_teacher_matrix, display name from church YAML. CI: `check_church_yaml_no_sensitive_tokens.py`, `check_norcal_dharma_no_matrix.py`, `check_norcal_dharma_export.py`. Ops smoke: `scripts/ops/smoke_church_brand_resolution.py`.

---

## 2026-02-25

### Added

- **wave_candidates.schema.json** (1.0) — Contract for `wave_candidates_*.json`. Required: schema_version, wave_id (pattern `YYYY-Www`), generated_at_utc, candidates[]. Candidate items: candidate_id, tuple_id, brand_id, persona_id, topic_id, engine_id, arc_id, slot_sig, band_sig (pattern `[1-5]-...`), variation_signature, teacher_mode, risk (enum), candidate_sort_key.
- **wave_optimizer_solution.schema.json** (1.0) — Contract for `wave_optimizer_solution_*.json`. Required: schema_version, wave_id, status (SOLVED | SOLVED_WITH_WARN), target_size, selected_count. Optional: selected / selected_candidates, selected_items, objective_breakdown, constraint_summary.
- **wave_optimizer_infeasible.schema.json** (1.0) — Contract for `wave_optimizer_infeasible_*.json`. Required: schema_version, wave_id, status (INFEASIBLE), target_size, candidate_count, blocking_reasons[]. Each reason: required `code`; optional description, details, and solver-specific fields (eligible_count, needed, exclusion_breakdown, selected_so_far, note).
- **config/ops_schema_registry.yaml** — Central registry for ops artifact types, schema paths, and artifact patterns. Used by `scripts/ci/validate_ops_artifacts.py`.
- **config/wave_optimizer_blocking_codes.yaml** — Canonical blocking reason codes and Slack/Jira routing. Machine-parseable; no free-text ambiguity.
- **scripts/ci/validate_ops_artifacts.py** — CI validator: all ops JSON matching a registry pattern is validated against the corresponding JSON Schema (Draft 2020-12).
- **scripts/ci/validate_ops_registry_consistency.py** — CI check: schema files exist for each registry entry; artifacts matching a pattern have a schema.

### Existing (no change)

- **book_quality_summary_v1.schema.json** (1.0) — Creative Quality Gate v1 output. Already present; added to ops_schema_registry.
