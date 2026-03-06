# Auto-merge policy for low-risk agent PRs

**Purpose:** Define when and how PRs from the observability agent (or other automated fixes) may be auto-merged after required checks pass.  
**Authority:** Extends [GITHUB_GOVERNANCE.md](GITHUB_GOVERNANCE.md) and [BRANCH_PROTECTION_REQUIREMENTS.md](BRANCH_PROTECTION_REQUIREMENTS.md).  
**Related:** [PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md](PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md), [GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md](GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md).

---

## 1. Scope

Auto-merge applies only to **low-risk** PRs that:

- Are opened by the observability agent (`agent_open_fix_pr.py`) or another approved bot actor.
- Touch **only** allowed paths (see below).
- Pass **all** required status checks for `main` (e.g. **Core tests**).
- Are labeled `bot-fix` (or as configured in the merge workflow).

---

## 2. Allowed paths for auto-merge

PRs that modify **only** the following are eligible:

| Path pattern | Purpose |
|--------------|---------|
| `requirements*.txt` | Add missing test/runtime dependencies (allowlist in agent). |
| `config/governance/*` | Governance config only when changed by an approved automation. |
| `docs/*` (specific allowlist) | e.g. "Last updated" timestamps from governance scripts; no prose. |

**Not allowed:** `phoenix_v4/**`, `atoms/**`, `scripts/**` (except scripts that only update allowlisted docs), content, or any path that affects pipeline or content generation. When in doubt, require human review.

---

## 3. Required checks

Before any auto-merge:

- **Core tests** must be required on `main` and must have passed on the PR.
- No bypass: branch protection must enforce required checks. The auto-merge workflow only calls `gh pr merge` when the PR is in a mergeable state (checks green, no conflicts).

---

## 4. Guardrails

- **One PR at a time:** The agent opens one fix PR per run (e.g. one dependency add). Avoid merging multiple agent PRs without intermediate verification.
- **Rollback:** If an auto-merged PR causes regressions, revert via normal PR process; update agent allowlist or fix recipes to prevent recurrence.
- **Audit:** Operations board (`artifacts/observability/operations_board.jsonl`) records `pr_url` and `merged` for traceability.

---

## 5. Enabling auto-merge

1. **Optional workflow:** [.github/workflows/auto-merge-bot-fix.yml](../.github/workflows/auto-merge-bot-fix.yml) runs on `pull_request` when label `bot-fix` is added. It merges the PR if the branch is up to date with `main` and required checks have passed.
2. **Permissions:** The workflow needs `contents: write` and `pull-requests: write`. Use the default `GITHUB_TOKEN` or a GitHub App with minimal scope.
3. **Label:** Add the label `bot-fix` to agent-created PRs (agent can set it via `gh pr edit --add-label bot-fix` when creating the PR, or a maintainer adds it after spot-check).

---

## 6. Runbook reference

- **Detect:** Agent PRs appear from `fix/deps-*` branches; operations board shows `pr_opened`.
- **Approve:** If you want auto-merge, add label `bot-fix`; the workflow will merge when green. If you want human review, leave unlabeled and merge manually.
- **Rollback:** Revert the merge commit via PR; document in [GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md](GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md) if the failure was due to governance or automation.

---

## 7. Summary

| Item | Value |
|------|--------|
| **Eligible actor** | Observability agent (or other approved bot) |
| **Label** | `bot-fix` |
| **Path restriction** | requirements*.txt, allowlisted config/docs only |
| **Required checks** | Core tests (and any other branch protection checks) |
| **Workflow** | `.github/workflows/auto-merge-bot-fix.yml` (optional) |
