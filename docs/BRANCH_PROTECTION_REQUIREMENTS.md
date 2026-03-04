# Branch Protection Requirements

**Purpose:** Required status checks for `main`/`master` branch protection.  
**Authority:** [GITHUB_GOVERNANCE.md](GITHUB_GOVERNANCE.md) (source of truth); [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md).

---

## Required status checks

For 100% production confidence, configure branch protection on `main` (or `master`) to require:

| Check | Workflow | Purpose |
|-------|----------|---------|
| **Core tests** | `core-tests.yml` | Fast pytest + production readiness gates |
| **Teacher gates** | `teacher-gates.yml` | Teacher Mode (when teacher paths change) |
| **Brand guards** | `brand-guards.yml` | NorCal Dharma (when brand paths change) |
| **Pearl News gates** | `pearl_news_gates.yml` | Pearl News (when pearl_news paths change) |

**Minimum:** At least **Core tests** must be required. Without it, core pipeline changes can merge with zero CI.

---

## How to configure

1. Go to **Settings → Branches → Branch protection rules** for `main`.
2. Enable **Require status checks to pass before merging**.
3. Add **Core tests** as a required check.
4. Add **Teacher gates**, **Brand guards**, **Pearl News gates** if those workflows run on the PR (path-triggered workflows may not run if they don't match changed paths; in that case they may show as "skipped" and not block — consider requiring them only when they run, or use a workflow that always runs).

**Note:** Path-triggered workflows (teacher-gates, brand-guards, pearl_news_gates) only run when their paths change. For PRs that touch only core code, only **Core tests** will run. Ensure **Core tests** is always required.

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
