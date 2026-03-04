# GitHub governance incident runbook

**Purpose:** Detect, respond, and recover from governance drift or failure.  
**Owner:** CODEOWNERS for [GITHUB_GOVERNANCE.md](GITHUB_GOVERNANCE.md) and workflows.

---

## 1. How to detect drift/failure

- **Governance check fails in CI** (`.github/workflows/github-governance-check.yml`).
- **PR blocked** by required checks that cannot run (e.g. only path-filtered checks required).
- **Ruleset changed:** e.g. ruleset targets all branches again, or PR requirement disabled.
- **Required checks missing or wrong** vs [config/governance/required_checks.yaml](../config/governance/required_checks.yaml).
- **Bypass script or token file** committed (verifier fails).

---

## 2. Who owns fix approval

- **CODEOWNERS** for `.github/workflows/*`, `scripts/ci/verify_github_governance.py`, `config/governance/`, and governance docs must approve changes to those paths.
- **Ruleset changes:** Org or repo admin (whoever can edit rulesets in GitHub). No one should merge a PR that weakens ruleset scope or required checks without approval.

---

## 3. Rollback steps for bad rules/workflow changes

1. **Revert the change:** Revert the commit(s) that changed the workflow or ruleset (via PR to main).
2. **Ruleset only (no code):** In GitHub Settings → Rules → Rulesets, edit the ruleset and restore target to `refs/heads/main` only; ensure PR required and required checks are correct.
3. **Restore from evidence:** If you have a ruleset snapshot in `artifacts/governance/`, use it as reference to reapply correct settings via API or UI.
4. **Re-run verifier:** `python scripts/ci/verify_github_governance.py --mode local` (and `--mode api` if token available). Confirm pass before closing incident.

---

## 4. Communication template

**Subject:** [Governance] &lt;short description&gt;

- **What broke:** (e.g. governance check failing, ruleset targeting all branches)
- **Impact:** (e.g. PRs blocked, or first push to feature branch blocked)
- **Who's fixing:** (role or handle)
- **ETA:** (e.g. revert in 1 hour, ruleset fix in 2 hours)
- **Actions:** (revert, ruleset edit, evidence update)

---

## 5. Postmortem checklist

- [ ] Root cause (config change, mistaken ruleset edit, etc.).
- [ ] What we're changing (process, docs, automation) to prevent recurrence.
- [ ] Evidence and runbook updated (e.g. new snapshot in `artifacts/governance/`, this runbook).
- [ ] Communication sent per template above (if applicable).
