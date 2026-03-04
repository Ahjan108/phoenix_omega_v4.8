# ML Editorial loop — safety and governance

**Purpose:** Kill switch, allowlist, audit log, rollback, and calibration gate for the ML Editorial + Marketing Intelligence loop.  
**Authority:** [ML_EDITORIAL_MARKET_LOOP_SPEC.md](ML_EDITORIAL_MARKET_LOOP_SPEC.md) §9.

---

## 1. Global kill switch

- **Config:** `config/ml_editorial/ml_editorial_config.yaml` → `ml_actions_enabled: false`.
- **Effect:** When `false`, no automated writes to allowlisted paths and no PR/task creation. Scripts may still run and write to `artifacts/ml_editorial/` (read-only from automation’s perspective: scoring and recommendations only).
- **Override:** Set to `true` only after governance and product owner approve.

---

## 2. Allowlist for automated writes

- **Config:** `config/ml_editorial/ml_editorial_config.yaml` → `automation.allowlist_paths`.
- **Default:** `config/ml_editorial/`, `artifacts/ml_editorial/`.
- **Rule:** Any script that writes or modifies repo files on behalf of the loop must only touch paths under the allowlist. No prose or content outside allowlist.

---

## 3. Audit log

- **Path:** `artifacts/ml_editorial/audit_log.jsonl` (or `automation.audit_log_path` in config).
- **Fields:** `action`, `outcome`, `ts`, `detail`.
- **When:** Every weekly run and every automated action (e.g. each of the five stages) appends a row. Every model-driven decision that results in a write or PR must be logged.

---

## 4. Rollback

- **Procedure:** Revert commits that applied ML-driven changes; if config was changed by automation, restore from version control. Restore `artifacts/ml_editorial/` from backup or regenerate from source if needed.
- **Script:** No dedicated rollback script in v1; document the procedure in this doc and in the runbook. Optional: add `scripts/ml_editorial/rollback_ml_changes.sh` that reverts last N commits touching allowlist paths.

---

## 5. Calibration gate

- **Config:** `config/ml_editorial/kpi_targets.yaml` → `calibration.max_drift_*`.
- **Rule:** Block rollout (or disable `ml_actions_enabled`) if score drift exceeds locked thresholds (e.g. section quality drift ≤ 0.15, reader-fit drift ≤ 0.12). Compare before/after on a fixed eval set when changing models or thresholds.
- **Owner:** Same pattern as EI V2 marketing calibration; gate must pass before re-enabling auto-apply.

---

## 6. Human-in-the-loop

- **Auto-apply:** Only low-risk changes (metadata, non-core prose patches) per allowlist.
- **Review required:** High-impact prose rewrites; any output with confidence below configured floor; any run where calibration gate would fail.
- **Every auto-change:** Must include rationale, expected_gain, and rollback path in artifact and PR description.
