# ADR-002: Distribution-only church brand policy

**Status:** accepted  
**Date:** 2026-03-03  
**Deciders:** platform, ops  
**Related:** docs/church_docs/README.md, docs/norcal_dharma.yaml

---

## Context

Church brands (e.g. NorCal Dharma) are identity/distribution brands for payouts and catalog presence. They must not be teacher brands: no books authored "by" the church, no Teacher Mode content, no wave allocation.

---

## Decision

**Distribution-only church brand policy:** Church brands in `brand_registry.yaml` are identity-only. They:
- Use `teacher_id: default_teacher` (no Teacher Mode, no teacher-bank atoms)
- Are excluded from `brand_teacher_matrix_*.yaml` (no wave allocation)
- Resolve display name from church YAML (`church.short_name`) at runtime
- Are validated pre-export: norcal_dharma rows cannot carry `teacher_id != default_teacher`

---

## Consequences

- CI: `check_norcal_dharma_no_matrix.py`, `check_norcal_dharma_export.py`
- Church loader: `phoenix_v4.ops.church_loader` fails fast when church YAML missing/invalid
- Runbook: docs/church_docs/RUNBOOK_BRAND_TO_CHURCH.md
