# Release production readiness checklist

**Purpose:** Step-by-step checklist before release.  
**Go/no-go:** [PRODUCTION_READINESS_GO_NO_GO.md](PRODUCTION_READINESS_GO_NO_GO.md).

---

## Pre-release

- [ ] `main` has 3 consecutive green runs (required checks).
- [ ] Branch protection evidence captured (ruleset JSON or export in `artifacts/governance/`).
- [ ] Rollback drill completed and evidence stored.
- [ ] Governance verifier passing: `python scripts/ci/verify_github_governance.py --mode local` (and `--mode api` if token available).

## Merge / release

- [ ] All PRs merged via PR (no direct push to main).
- [ ] Required checks green at merge time.

## Post-release

- [ ] Evidence bundle updated: run URLs, ruleset snapshot, rollback proof, signed go/no-go.
- [ ] CHANGELOG or release notes updated.

## Sign-off

| Role   | Name | Date |
|--------|------|------|
| (e.g. Tech lead) |      |      |
