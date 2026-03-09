# Branch Protection Requirements

**Purpose:** Required status checks for `main`/`master` branch protection.  
**Authority:** [GITHUB_GOVERNANCE.md](GITHUB_GOVERNANCE.md) (source of truth); [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md).

---

## Required status checks

For 100% production confidence, configure branch protection on `main` (or `master`) to require the following. Use **exact** check run names as emitted by workflows (see [config/governance/required_checks.yaml](../config/governance/required_checks.yaml)):

| Check | Workflow | Purpose |
|-------|----------|---------|
| **Core tests** | `core-tests.yml` | Fast pytest + production readiness gates |
| **Release gates** | `release-gates.yml` | Release and production readiness workflow checks |
| **EI V2 gates** | `ei-v2-gates.yml` | EI V2 tests, eval, calibration, promotion checks |
| **Change impact** | `change-impact.yml` | Change observation + impact analysis evidence |
| **truth-audit-gate** | `truth-audit-gate.yml` | PR-safe audit gate; ownership/config validation |
| **drift-gate** | `drift-gate.yml` | PR-safe drift gate; required paths + allowlist |

**Require PR for all changes to main.** **Do not allow force pushes.**

---

**CODEOWNERS:** Changes under `/.github/workflows/`, `/scripts/`, `/config/`, and `/docs/` require review from designated owners (see [.github/CODEOWNERS](../.github/CODEOWNERS)). All changes to `main` must go through a PR.

## How to configure

1. Go to **Settings → Branches → Branch protection rules** for `main`.
2. Enable **Require a pull request before merging** (no direct pushes to main).
3. Enable **Require status checks to pass before merging**.
4. Add required checks (use **exact** job names as shown in GitHub Actions; see [config/governance/required_checks.yaml](../config/governance/required_checks.yaml)):
   - **Core tests**
   - **Release gates**
   - **EI V2 gates**
   - **Change impact**
   - **truth-audit-gate**
   - **drift-gate**
5. Enable **Do not allow force pushes**.
6. (Recommended) Enable **Do not allow bypassing the above settings** so admins also follow the rules.
7. Save the rule and verify a test PR shows all six checks as required.

**Note:** Branch protection is configured in GitHub **Settings → Branches → Branch protection rules** for `main`. This repo cannot change it from code; apply the above steps manually.

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
