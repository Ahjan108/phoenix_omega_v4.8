# Changelog

All notable release and governance changes are documented here.  
Release evidence and go/no-go checklists: see [docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md](docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md) and `artifacts/governance/`.

---

## [Unreleased]

### Governance and guardrails

- GitHub governance 100% guardrails: source-of-truth docs, verifier script, governance CI workflow, preflight script, CODEOWNERS, PR template, release docs, incident runbook.
- Required-checks policy in `config/governance/required_checks.yaml`.
- Token hygiene: no tokens in repo; use GITHUB_TOKEN or gh auth only for scripts.
