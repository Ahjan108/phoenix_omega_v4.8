# Branch Protection Requirements

**Purpose:** Required status checks for `main`/`master` branch protection.  
**Authority:** [GITHUB_GOVERNANCE.md](GITHUB_GOVERNANCE.md) (source of truth); [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md).

---

## Required status checks

For 100% production confidence, configure branch protection on `main` (or `master`) to require:

| Check | Workflow | Purpose |
|-------|----------|---------|
| **Core tests** | `core-tests.yml` | Fast pytest + production readiness gates |
| **Release gates** | `release-gates.yml` | Release and production readiness workflow checks |
| **EI V2 gates** | `ei-v2-gates.yml` | EI V2 tests, eval, calibration, promotion checks |
| **Change impact** | `change-impact.yml` | Change observation + impact analysis evidence |

These four are required for d2/d3/d5/d6 go-live.

---

## How to configure

1. Go to **Settings → Branches → Branch protection rules** for `main`.
2. Enable **Require status checks to pass before merging**.
3. Add required checks:
   - **Core tests**
   - **Release gates**
   - **EI V2 gates**
   - **Change impact**
4. Save the rule and verify a test PR shows all four checks as required.

---

## Failure visibility (recommended)

For immediate visibility when CI breaks:

1. Enable workflow issue alerts via `.github/workflows/production-alerts.yml` (already in repo).
2. Enable GitHub email notifications:
   - GitHub **Settings → Notifications**
   - Turn on **Email** for Actions/workflow failures.
   - Set repo watch to **Custom → Actions** for this repo.
3. Keep `production-observability.yml` scheduled; it writes:
   - `artifacts/observability/evidence_log.jsonl`
   - `artifacts/observability/elevated_failures.jsonl`

This gives both inbox visibility (email) and in-repo tracking (issues + artifacts).

---

## Auto-merge (optional)

For low-risk agent PRs (e.g. dependency fixes from the observability agent), see [AUTO_MERGE_POLICY.md](AUTO_MERGE_POLICY.md). PRs labeled `bot-fix` that pass required checks may be auto-merged via `.github/workflows/auto-merge-bot-fix.yml`.
