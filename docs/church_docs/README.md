# Church–Brand Linkage

**Authority:** Cooperative Church Compliance YAML Schema. Church records are the canonical source for legal identity, board, financial profile, and compliance calendar.

## Brand → Church Mapping

| brand_id      | Church record (canonical source) | Notes |
|---------------|----------------------------------|-------|
| norcal_dharma | [docs/norcal_dharma.yaml](../norcal_dharma.yaml) | Church #1. Theravada self-help audiobooks. Distribution/payout brand only; no teacher, no Teacher Mode, no wave allocation. |

**Display name:** Read `church.short_name` from the church YAML at runtime (e.g. "NorCal Dharma"). Do not duplicate in brand config.

**Ops smoke:** Run `python scripts/ops/smoke_church_brand_resolution.py` to verify brand_id → church.short_name resolution across all church brands.
