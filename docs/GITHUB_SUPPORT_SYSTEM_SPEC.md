# GitHub Support System Spec (v1)

## 1) Purpose

Prevent Git mistakes, deadlocks, and unclear instructions by standardizing:

- branch/PR workflow
- command delivery format
- recovery runbooks
- governance checks

---

## 2) Hard Rules (non-negotiable)

1. Never push directly to `main`.
2. Never use orphan branches for PR work.
3. Always branch from `origin/main`.
4. One PR = one scoped change set.
5. No token files in repo (`.github_token`, `.rtf`, etc.).
6. No bypass scripts for rulesets/checks.
7. Required checks must gate merge to `main`, not feature-branch push.

---

## 3) Dev Instruction Format (must follow)

Dev must always provide:

1. **State**: what branch you are on + what is wrong.
2. **Decision**: which path applies (A/B).
3. **Exact commands**: copy-paste safe, no comments inline.
4. **Expected output**: what success looks like.
5. **Rollback**: one recovery command path.

No mixed snippets, no "or" in same code block.

---

## 4) Command Delivery Standard

- One code block per path.
- No comment lines in command blocks.
- No multi-path block ("run A or B") in same block.
- If alternatives exist, label clearly:

**Path A (recommended):**

```bash
command_one
command_two
```

**Path B (if A fails):**

```bash
command_one
command_two
```

---

## 5) Standard Git Flow

```bash
git fetch origin
git checkout -b codex/<topic> origin/main
# make changes
git add -A
git commit -m "<type>: <scope>"
git push -u origin codex/<topic>
# open PR to main
```

---

## 6) Preflight (must run before push)

```bash
scripts/ci/preflight_push.sh
```

Checks:

- not on `main`
- branch has merge-base with `origin/main`
- branch name matches `codex/*`
- no token files staged

---

## 7) Recovery Runbooks (required)

Maintain short runbooks for:

1. Diverged `main`
2. Branch rejected by ruleset
3. PR cannot be created (no common history)
4. Required check deadlock
5. Accidental secret exposure

Each runbook must include:

- detect command
- fix commands
- verify command

For repo-specific workflows, required checks, and Qwen-Agent runner/secrets, see [GITHUB_OPERATIONS_FRAMEWORK.md](GITHUB_OPERATIONS_FRAMEWORK.md).

---

## 8) Governance Automation (required)

CI must run:

- `scripts/ci/verify_github_governance.py`
- on PR + push to `main`
- fail if:
  - ruleset not `main`-only
  - PR requirement missing
  - no always-on required check
  - bypass script found
  - token files found

---

## 9) Communication SLA for Dev

Dev must answer every Git support request with:

1. current repo state summary (3 lines max)
2. exact next 3 commands
3. verification command
4. stop condition ("done when X")

---

## 10) Definition of Done (GitHub support system)

Complete when all are true:

1. Governance docs exist and are linked.
2. Preflight script exists and is used.
3. Governance CI workflow exists and passing.
4. PR template + CODEOWNERS active.
5. Incident runbook exists.
6. Secret hygiene policy enforced.
7. Team follows command delivery standard.

---

## See also

- [GITHUB_GOVERNANCE.md](GITHUB_GOVERNANCE.md) — rulesets, required checks, branch flow.
- [GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md](GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md) — incident response.
- [.github/pull_request_template.md](../.github/pull_request_template.md) — PR checklist.
