# Registry Integrity Checker — CLI Contract v1

This is the deterministic executable interface spec CI will depend on. No implementation code—interface and behavior only.

**Policy authority:** [docs/governance/registry_integrity_checker_v1.md](../docs/governance/registry_integrity_checker_v1.md) defines what must be validated; this document defines how to invoke it.

---

## 1. Command Structure

```
phoenix-registry <command> [options]
```

**Single responsibility:** Validate registry integrity and enforce root-of-trust guarantees before any pipeline step executes.

### Supported Commands

| Command       | Purpose                                                                 |
|---------------|-------------------------------------------------------------------------|
| check         | Validate registry against dependent specs and runtime artifacts         |
| report        | Generate full integrity report JSON                                    |
| hash          | Output canonical registry hash                                         |
| migrate-mode  | Run in non-failing staging mode                                        |

---

## 2. check Command

**Purpose:** Hard fail on any integrity violation.

**Usage:**

```bash
phoenix-registry check \
  --registry-dir ./registry \
  --spec-dir ./specs \
  --artifacts-dir ./artifacts \
  --catalog en_us_core
```

### Required Flags

| Flag              | Required | Description                                      |
|-------------------|----------|--------------------------------------------------|
| --registry-dir    | Yes      | Directory containing canonical registry files    |
| --spec-dir        | Yes      | Writer spec, scheduler spec, entropy spec        |
| --artifacts-dir   | No       | Build artifacts to validate                      |
| --catalog         | No       | Limit check to specific catalog_id               |

### Exit Codes

| Code | Meaning           |
|------|-------------------|
| 0    | PASS              |
| 1    | Hard failure      |
| 2    | Internal CLI error|

**CI rule:** `exit_code != 0` → block pipeline.

---

## 3. report Command

Produces the integrity report artifact.

**Usage:**

```bash
phoenix-registry report --output registry_integrity_report.json
```

### Output Schema

```json
{
  "status": "PASS",
  "timestamp": "ISO8601",
  "registry_hash": "sha256",
  "violations": [],
  "warnings": [],
  "validated_files": {
    "family_registry.yaml": "sha256",
    "brand_registry.yaml": "sha256"
  }
}
```

This artifact must be stored in CI logs.

---

## 4. hash Command

Outputs canonical registry hash.

**Usage:**

```bash
phoenix-registry hash --registry-dir ./registry
```

### Deterministic Hash Rules

Before hashing:

- Sort keys recursively
- Normalize whitespace
- Normalize Unicode
- Strip comments
- Enforce lowercase on keys
- Ensure stable YAML serialization

Then compute:

```
sha256(canonical_serialization)
```

This hash becomes:

- Entropy planner trust anchor
- Schema auto-sync trust anchor
- Runtime boot verification anchor

---

## 5. migrate-mode Command

Staging-only soft enforcement.

**Usage:**

```bash
phoenix-registry migrate-mode check
```

**Behavior:**

- Logs violations
- Does NOT exit 1
- Emits `"migration_mode": true` in report
- Never allowed in production branch

**CI must enforce:**

```yaml
if branch == main:
  forbid migrate-mode
```

---

## 6. Validation Categories (Executed by check)

| Category              | Checks                                                                 |
|------------------------|------------------------------------------------------------------------|
| A. Family Registry     | Unknown family_id referenced; duplicate family_id; deprecated ID in use; case mismatch; missing family in writer output |
| B. Brand Integrity     | Unknown brand_id; brand in wrong catalog; locale mismatch; missing archetype/emotional range entry |
| C. Catalog Isolation   | Cross-catalog references; shared wave_id; shared entropy pools; shared similarity scope |
| D. Divergence Integrity| Missing CBDI policy; duplicate divergence rule; brand missing divergence baseline |
| E. Drift Detection     | Registry file changed but hash mismatch not acknowledged; enum in spec but not in registry; registry entry removed but referenced; unexpected new family_id |

---

## 7. Internal Architecture (High-Level)

```
CLI Entry
 ├─ Load registry
 ├─ Canonicalize
 ├─ Compute hash
 ├─ Load dependent specs
 ├─ Validate references
 ├─ Validate cross-links
 ├─ Validate catalog isolation
 ├─ Emit report
 └─ Exit with code
```

No side effects. No schema rewriting. Pure validation.

---

## 8. CI Integration Example

**GitHub Actions:**

```yaml
- name: Registry Integrity Check
  run: |
    phoenix-registry check \
      --registry-dir ./registry \
      --spec-dir ./specs
```

If fail → pipeline stops before:

- Writer lint
- Assembly
- Entropy planning
- Wave scheduling

---

## 9. Deterministic Root-of-Trust Rule

Before schema auto-sync is allowed to run:

```
if registry_hash != last_ci_approved_hash:
    require manual review approval
```

Prevents silent registry edits from triggering automated enum rewrites.

---

## 10. After This Is Implemented

Next step is **Failure Scenario Suite**:

- 10 golden fail fixtures
- 5 golden pass fixtures
- One drift rename scenario
- One cross-catalog contamination scenario

Ensure `phoenix-registry check` behaves exactly as expected. Only after that passes reliably, design schema auto-sync.
