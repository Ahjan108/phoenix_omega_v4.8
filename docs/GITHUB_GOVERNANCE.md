# GitHub governance (source of truth)

**Purpose:** Single source of truth for repo rulesets, required checks, branch flow, and token hygiene.  
**Verifier:** [scripts/ci/verify_github_governance.py](../scripts/ci/verify_github_governance.py) (reads [config/governance/required_checks.yaml](../config/governance/required_checks.yaml)).

---

## Rulesets

- **One ruleset** for `refs/heads/main` only (or default branch). Do **not** target all branches.
- **Enable:** Require pull request before merging, require status checks to pass, block force pushes.
- **Do not** require status checks on feature-branch push (causes deadlock on first push).

---

## Required checks

- **At least one always-on** required check (e.g. **Core tests**). See [config/governance/required_checks.yaml](../config/governance/required_checks.yaml).
- Path-filtered workflows (EI V2, Teacher gates, etc.) must **not** be the only required checks; every PR must have at least one runnable check.
- Policy is versioned in config; the verifier enforces it.

---

## Branch / PR flow

- Branch from `origin/main` only. No orphan branches.
- Naming: `codex/<topic>` recommended.
- Push branch → open PR to `main` → merge only when required checks are green.
- **Preflight:** Run `scripts/ci/preflight_push.sh` before push to block direct push to main and orphan branches.

---

## Security and tokens

- **No tokens in repo.** No `.github_token`, no token `.rtf` files. Use repo/org secrets or OS keychain.
- **Revoke** any token ever pasted in chat or logs immediately.
- Token rotation: document cadence and emergency revoke in org/repo runbooks. Prefer short-lived tokens or GitHub App over long-lived PAT for normal flow.

---

## Related docs

- [BRANCH_PROTECTION_REQUIREMENTS.md](BRANCH_PROTECTION_REQUIREMENTS.md) — Required checks and configuration.
- [GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md](GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md) — Incident response.
- [GITHUB_GOVERNANCE_PLAN.md](GITHUB_GOVERNANCE_PLAN.md) — Full plan and checklist.
