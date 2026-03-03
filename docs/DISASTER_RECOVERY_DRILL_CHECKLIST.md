# Disaster Recovery Drill Checklist

**Purpose:** One executed DR drill with evidence is required for 100% production operational readiness.  
**Authority:** [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md), [RIGOROUS_SYSTEM_TEST.md](./RIGOROUS_SYSTEM_TEST.md).

---

## Requirement

For 100% production confidence, you need **one executed DR drill** with evidence:

1. Restore from backup
2. Rerun release gates
3. Verify artifacts/hash consistency
4. Signed timestamped report

Without this, you have good CI but **incomplete operational readiness**.

---

## DR Drill Steps

### 1. Pre-drill (record baseline)

- [ ] Record current `main` commit SHA: `________________`
- [ ] Record artifact hashes (e.g. `artifacts/rendered/*/book.txt`): `________________`
- [ ] Run `scripts/run_production_readiness_gates.py` — record exit code: `________________`
- [ ] Run `scripts/release/rollback_smoke.sh` — record exit code: `________________`

### 2. Simulate disaster

- [ ] Create isolated restore environment (e.g. new clone, or restore from backup to temp dir)
- [ ] Restore repo from backup to restore environment
- [ ] Verify restore completed: commit SHA matches or is known-good

### 3. Post-restore verification

- [ ] Run `scripts/run_production_readiness_gates.py` — must exit 0
- [ ] Run `scripts/release/rollback_smoke.sh` — must exit 0
- [ ] Run `pytest tests/ -m "not slow"` — must pass
- [ ] Verify artifact hashes match baseline (or document expected drift)

### 4. Evidence capture

- [ ] Run `scripts/observability/collect_signals.py` — capture snapshot
- [ ] Save `artifacts/release/rollback_smoke_evidence.json`
- [ ] Save `artifacts/observability/signal_snapshot_*.json`
- [ ] Complete signed timestamped report (template below)

### 5. Sign-off

- [ ] Signatory: `________________` Date: `________________`
- [ ] Report stored at: `artifacts/dr_drill/DR_DRILL_REPORT_YYYYMMDD.json`

---

## Evidence Template

```json
{
  "drill_date": "YYYY-MM-DD",
  "drill_timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "baseline_commit_sha": "...",
  "restore_commit_sha": "...",
  "production_gates_exit": 0,
  "rollback_smoke_exit": 0,
  "pytest_exit": 0,
  "artifact_hash_consistent": true,
  "signatory": "Name",
  "notes": "Optional notes"
}
```

---

## Rollback Procedure (reference)

1. Restore repo from backup (or revert to last known-good commit)
2. Run `scripts/run_production_readiness_gates.py`
3. Run `scripts/release/rollback_smoke.sh`
4. If both pass → operational
5. If either fails → escalate; do not release until fixed

---

## Frequency

- **Minimum:** One DR drill before first production release
- **Recommended:** Annual DR drill; after major infra changes
