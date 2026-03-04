# Production readiness go/no-go

**Purpose:** Criteria and process for production go/no-go decisions.  
**Evidence:** See [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](RELEASE_PRODUCTION_READINESS_CHECKLIST.md) and `artifacts/governance/`.

---

## Go criteria

- CI green: required checks (e.g. Core tests, any path-filtered that run) passing on `main`.
- Branch protection: ruleset targets main only; PR required; required status checks; force push blocked.
- Rollback drill evidence on file.
- Signed go/no-go checklist completed (names, roles, date).

---

## No-go criteria

- Any required check failing on main.
- Ruleset or required checks misconfigured (e.g. targeting all branches).
- No rollback drill evidence or unsigned checklist.

---

## Who signs

- Define per org/repo: e.g. tech lead, release manager, or delegated owner. Record in checklist.

---

## How to record

- Complete [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](RELEASE_PRODUCTION_READINESS_CHECKLIST.md).
- Store signed checklist and evidence (run URLs, ruleset snapshot) in `artifacts/governance/` or linked location.
- Reference in release notes or CHANGELOG.
