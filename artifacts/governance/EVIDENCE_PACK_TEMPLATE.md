# Governance 100% evidence pack

Fill in the placeholders below. When all sections are complete, governance 100% is satisfied.

---

## Do this (5 steps)

1. **Revoke exposed token** — GitHub → Settings → Developer settings → Personal access tokens → revoke the token you pasted. Create a new token.
2. **Fix ruleset** — [Repo Rules](https://github.com/Ahjan108/phoenix_omega_v4.8/settings/rules) → open **Protect main** → turn on **Require a pull request before merging** → Save.
3. **Re-run API check** (same line, no placeholders; use your new token). You need all PASS, no FAIL:
   ```bash
   GITHUB_TOKEN=YOUR_NEW_TOKEN python3 scripts/ci/verify_github_governance.py --mode api
   ```
4. **Fill this template** — §1 date + checkbox after API PASS; §2 three green main run URLs; §3 branch protection evidence path; §4 rollback drill path/summary; §5 check after sign-off done.
5. **Fill sign-off** — [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](../../docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md) → Sign-off table (Role, Name, Date).

After these 5 are done, you can claim **100% governance/ship guardrails**.

---

## 1. API governance check (run once)

Run with your new token in env (not from a file). Same line, no placeholders:

```bash
GITHUB_TOKEN=YOUR_NEW_TOKEN python3 scripts/ci/verify_github_governance.py --mode api
```

- [x] Run completed: PASS (no FAIL lines)
- Date run: 2026-03-03

---

## 2. Three consecutive green main runs

Paste the workflow run URLs for 3 consecutive successful runs on `main` (e.g. from Actions tab, open each run, copy URL).

| # | Run URL | Date |
|---|--------|------|
| 1 | https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/22651440138 | 2026-03-04 |
| 2 | https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/22651408080 | 2026-03-04 |
| 3 | https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/22651194528 | 2026-03-04 |

Replace `PASTE_RUN_ID_1` etc. with the run ID from each green main run (Actions → open run → copy from URL).

- [x] All three URLs pasted and runs are green

---

## 3. Branch protection evidence

Store one of:

- **Option A:** Path to ruleset JSON export (e.g. from GitHub API or UI export), or
- **Option B:** Screenshot filename stored in this folder or linked below.

Path or filename: artifacts/governance/branch_protection_evidence.png

- [x] Branch protection evidence captured

---

## 4. Rollback drill proof

Short description or log showing rollback was exercised (e.g. reverted a commit on main, or ran rollback procedure).

Path or inline summary: artifacts/governance/rollback_drill_2026-03-03.md

- [x] Rollback drill evidence captured

---

## 5. Signed go/no-go

Sign-off is in [docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md](../../docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md) § Sign-off.

- [x] Sign-off table filled (Role, Name, Date) in that doc

---

## Done

When all checkboxes above are checked and placeholders filled, **100% GitHub governance/ship guardrails** is complete.
