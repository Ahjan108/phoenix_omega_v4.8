# Rollback Runbooks Index

**Purpose:** Single index of rollback and DR runbooks that must stay current with code, workflows, and release policy.

## Runbooks

- [DISASTER_RECOVERY_DRILL_CHECKLIST.md](./DISASTER_RECOVERY_DRILL_CHECKLIST.md) — DR drill steps and evidence template.
- [audiobook_operator_runbook.md](./audiobook_operator_runbook.md) — Audiobook operations and recovery handling.
- [scripts/release/audiobook_rollback.sh](../scripts/release/audiobook_rollback.sh) — Automated audiobook rollback helper.
- [scripts/release/rollback_smoke.sh](../scripts/release/rollback_smoke.sh) — Post-rollback smoke verification.
- [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md) — Release-time checklist including rollback evidence.

## Keep-current policy

- Review this index **monthly** and on every release cycle.
- If a rollback script/doc changes path or behavior, update this index in the same PR.
- Rollback smoke evidence must be attached to release evidence artifacts.
- Monthly baseline tags should reference the current rollback docs (see [RELEASE_POLICY.md](./RELEASE_POLICY.md)).
