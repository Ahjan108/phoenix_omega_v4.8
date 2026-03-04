# Governance evidence

Store here (or link from here):

- **Branch protection evidence:** Ruleset JSON export, workflow run URLs (machine-readable).
- **Rollback drill evidence:** Log or short doc showing rollback was exercised.
- **Release evidence bundles:** Per-release folder with run URLs, ruleset snapshot, signed go/no-go (see [docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md](../../docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md)).

**Evidence pack (governance 100% item 9):** 3 consecutive green main runs, branch protection evidence captured, rollback drill evidence captured, signed go/no-go checklist. Complete after this PR is merged.

---

## Governance 100% completion checklist (user-side)

Governance 100% is **not complete** until these 5 steps are done:

| # | Step | Done? |
|---|------|--------|
| 1 | Open PR and paste `.pr-body-governance-100.md` into the PR description | |
| 2 | Revoke exposed PAT(s) immediately (GitHub → Settings → Developer settings → Personal access tokens) | |
| 3 | Delete local token files (`.github_token`, `github_access_token.rtf`) and confirm they are not tracked | |
| 4 | Merge PR after required checks pass | |
| 5 | Complete evidence pack: 3 green main runs, branch-protection proof, rollback drill proof, signed go/no-go | |

Once all 5 are done, you can claim **100% GitHub governance/ship guardrails**.
