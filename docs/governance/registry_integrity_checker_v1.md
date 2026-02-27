# Registry Integrity Checker v1

This runs in CI before:

- Writer validation
- Assembly
- Entropy planner
- Wave release

It blocks drift at the root.

---

## 1. Purpose

Prevent:

- Enum drift across specs
- Missing family/template definitions
- Locale mismatch across catalogs
- Brand/family cross-reference errors
- Accidental rename breaking alignment gates

This checker validates **registry → dependent specs → runtime artifacts**.

---

## 2. Scope of Validation

### Authoritative Sources (Single Source of Truth)

- family_registry.yaml
- brand_registry.yaml
- brand_registry_locale_extension.yaml
- brand_teacher_matrix.yaml
- brand_teacher_matrix_zh.yaml
- cross_brand_divergence.yaml

These are authoritative.

Everything else must conform to them.

---

## 3. Validation Matrix

### A. Family Registry Checks

For every family_id in:

- writer spec output
- book specs
- entropy planner artifacts
- scheduler configs

Validate:

```yaml
family_id ∈ family_registry.yaml
```

Hard fail if:

- Missing
- Misspelled
- Deprecated
- Case mismatch

Optional:

- Enforce slug normalization (snake_case only)

---

### B. Brand ↔ Locale Consistency

For each:

```yaml
[catalog_id, brand_id, locale]
```

Validate:

- brand exists
- brand is permitted in that catalog
- locale matches brand's canonical locale binding
- zh brands do not appear in en_us_core
- en brands do not appear in zh catalogs

Hard fail on cross contamination.

---

### C. Brand ↔ Family Compatibility

If you enforce brand archetype constraints:

```yaml
brand_archetype_registry.yaml
```

Validate:

- brand is allowed to publish that family type
- emotional range supports family emotional band ceiling
- no forbidden family/brand pairing

---

### D. Cross-Brand Divergence Integrity

If cross_brand_divergence.yaml defines divergence floors:

Validate:

- Each active brand has CBDI baseline
- No brand is missing divergence policy
- No duplicate divergence rule keys

---

### E. Locale Partitioning Integrity

For each catalog_id:

- Confirm isolation
- No similarity pools reference external catalog_id
- No shared wave_id across catalogs

---

## 4. Drift Detection Rules

Detect and fail on:

- Registry key removed but still referenced
- Registry key renamed without migration file
- Duplicate registry IDs
- Enum mismatch between specs and registry
- Unexpected new family_id appearing in writer outputs

Optional: allow explicit migration mode:

```yaml
registry_migration_mode: true
```

Which logs warnings but does not fail (staging only).

---

## 5. CI Enforcement Contract

```yaml
registry_integrity_checker:
  fail_on:
    - unknown_family_id
    - unknown_brand_id
    - locale_mismatch
    - cross_catalog_contamination
    - missing_divergence_policy
    - orphaned_registry_key
    - duplicate_registry_key

  warn_on:
    - deprecated_family_id
    - missing_optional_archetype_data
```

---

## 6. Output Artifact

On CI run, produce:

**registry_integrity_report.json**

```json
{
  "status": "PASS | FAIL",
  "violations": [],
  "warnings": [],
  "registry_hash": "sha256(...)",
  "dependent_spec_hashes": {
    "writer_spec": "...",
    "entropy_spec": "...",
    "scheduler_spec": "..."
  }
}
```

Store registry hash to detect unexpected registry edits.

---

## 7. Runtime Protection (Optional but Recommended)

At system boot:

- Load registry
- Validate hashes against CI-approved hash
- Refuse production start if mismatch

Prevents hot-edit corruption.

---

## 8. Why This Must Come First

Without registry integrity:

- family_id drift silently breaks family alignment gates
- Scheduler may overproduce invalid combinations
- Entropy planner miscalculates N
- CBDI comparisons use wrong brand mappings
- Ximalaya and EN catalogs accidentally collide

Registry is your root of trust.

---

## 9. After This Is Locked

Next step:

### Schema Compiler Auto-Sync

It will:

- Auto-generate enum definitions from registry
- Inject into JSON schemas
- Update writer spec references
- Recompile scheduler constraints
- Rebuild OpenAPI contracts

But only after registry integrity is guaranteed.

---

## 10. Repo Mapping Note

This spec names `family_registry.yaml` and `brand_registry.yaml`. In this repo:

- **config/localization/brand_registry_locale_extension.yaml** — brands + locale/territory
- **config/catalog_planning/brand_archetype_registry.yaml** — brand archetypes
- **config/catalog_planning/brand_teacher_matrix.yaml**, **brand_teacher_matrix_zh.yaml** — teacher allocation
- **config/cross_brand_divergence.yaml** — CBDI policy
- **config/localization/locale_registry.yaml** — locale definitions

A dedicated `family_registry.yaml` may not exist yet; engine/topic bindings live in config (e.g. topic_engine_bindings.yaml and engine definitions). Implementation must either introduce a canonical family_registry.yaml or map "family" to existing config and document the mapping in the checker.

---

## Strategic Position

You are now operating at:

> "Prevent one renamed enum from invalidating 48 brands × 1,008 books."

This is the correct maturity level.

**Execution contract:** See [cli/phoenix_registry_cli_contract_v1.md](../../cli/phoenix_registry_cli_contract_v1.md) for the CLI interface (check, report, hash, migrate-mode).
