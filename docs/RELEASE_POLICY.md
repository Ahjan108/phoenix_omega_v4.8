# Release Policy and Freeze

**Purpose:** Enforce process so gates cannot be bypassed by process drift.  
**Authority:** [PRODUCTION_100_PLAN.md](./PRODUCTION_100_PLAN.md), [BRANCH_PROTECTION_REQUIREMENTS.md](./BRANCH_PROTECTION_REQUIREMENTS.md).

---

## Freeze policy (before shipping)

1. **`release/*` branch only** — No direct pushes to `main` for release. All release work on a release branch (e.g. `release/2026-03`, `release/v1.0`).
2. **Required checks must pass on that branch** — Same required status checks as for `main` must pass on the release branch before merge or tag.
3. **Only tagged releases (`vX.Y.Z`) can ship** — Production build from a tag. No untagged commit is considered shipped.

---

## Workflow

1. Cut `release/<name>` from `main` when starting a release cycle.
2. Do release work on `release/<name>`.
3. Open PR to `main` (or merge after checks pass).
4. When all required checks are green and release checklist is signed: tag `vX.Y.Z`, push tag.
5. Build/ship from the tag only.

---

Without this policy, releases can drift (direct pushes to `main`, untagged “release” commits). The freeze makes the release path explicit and auditable.
