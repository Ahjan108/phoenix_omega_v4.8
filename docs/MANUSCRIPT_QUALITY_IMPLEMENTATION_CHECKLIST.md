# Manuscript Quality — Implementation Checklist

**Purpose:** Actionable checklist from editor feedback (Gen Alpha anxiety manuscript). Tied to pipeline surfaces, CI, and release gates.

**Feature = complete.** Tier 0 contract, canary gate, and trend dashboard are implemented. **Production 100%** requires the full operational checklist: CI/release gates on `main`, branch protection, smoke runs, evidence, rollback proof. See [PRODUCTION_READINESS_GO_NO_GO.md](./PRODUCTION_READINESS_GO_NO_GO.md), [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md).

**Document all:** [docs/DOCS_INDEX.md](./DOCS_INDEX.md) § Manuscript quality (Tier 0 contract).

---

## Tier 0: System Contract (CI / Pre-Export)

Hard fail rules before generation/export. Config: [config/quality/tier0_book_output_contract.yaml](../config/quality/tier0_book_output_contract.yaml). Check: [scripts/ci/check_book_output_tier0_contract.py](../scripts/ci/check_book_output_tier0_contract.py).

---

## Trend Dashboard (Observability Add-On)

**Not a production gate.** Violations-over-time dashboard for observability. Script: [scripts/ci/tier0_trend.py](../scripts/ci/tier0_trend.py). Storage: `artifacts/tier0_reports/`. Canary auto-appends.

---

## Production 100%

Production readiness = full go-live gates (release-gates CI, branch protection, smoke runs, evidence, rollback proof). Tier 0 + trend are feature add-ons; they do not substitute for the operational checklist.
