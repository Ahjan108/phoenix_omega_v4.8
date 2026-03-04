# Phoenix Marketing Research — Scaffold Templates
## Ready to populate from deep research results

### Files in this package

| File | Prompt | Target config | Status |
|------|--------|---------------|--------|
| `01_gtm_identity_patch.yaml` | 1. Per-brand GTM | `brand_archetype_registry.yaml` → gtm_identity, discovery_contract | ⬜ Awaiting research |
| `02_emotional_vocabulary_patch.yaml` | 2. Controlled vocabulary | `brand_archetype_registry.yaml` → emotional_vocabulary, global_constraints | ⬜ Awaiting research |
| `03_consumer_language_by_topic.yaml` | 3. Consumer vs. clinical | `config/marketing/consumer_language_by_topic.yaml` | ✓ Populated (14 topics). Spec: [specs/TITLE_ENGINE_MARKETING_CONFIG_SPEC.md](../specs/TITLE_ENGINE_MARKETING_CONFIG_SPEC.md) |
| `04_invisible_scripts.yaml` | 4. Persona × topic scripts | `config/marketing/invisible_scripts_by_persona_topic.yaml` | ✓ Populated (140 entries, 10×14). Spec: [specs/TITLE_ENGINE_MARKETING_CONFIG_SPEC.md](../specs/TITLE_ENGINE_MARKETING_CONFIG_SPEC.md) |
| `05_duration_bands_patch.yaml` | 5. Duration bands | `brand_archetype_registry.yaml` → duration_strategy | ⬜ Awaiting research |
| `06_cover_design_patch.yaml` | 6. Cover design | `brand_archetype_registry.yaml` → cover_art_identity | ⬜ Awaiting research |
| `07_pricing_topology_patch.yaml` | 7. Pricing | `brand_archetype_registry.yaml` → pricing_posture | ⬜ Awaiting research |

### Merge workflow

1. Deep research completes → populate each scaffold with findings
2. Run per-file validation:
   - YAML parses cleanly
   - Required fields present
   - Types correct
   - Provenance block complete
3. Run `validate_brand_archetype_registry.py` for registry patches (01, 02, 05, 06, 07)
4. Check no canonical spec contradictions (persona IDs, topic IDs, brand IDs)
5. A/B sanity test: generate 10–20 sample titles with new config
6. Marketing + Ops sign-off
7. Merge into config

### Merge checklist (copy per prompt)

```
[ ] Provenance block attached (date, model, sources, confidence, reviewer)
[ ] Schema validation passed
[ ] No canonical spec contradiction
[ ] A/B sanity test passed (if applicable)
[ ] Marketing sign-off
[ ] Ops sign-off
```

### Constraints enforced

- brand_id, admin_id: NEVER modified
- 24 brands: fixed, no add/remove
- duration_strategy: micro + mid + deep must = 1.0
- duration_strategy: mid_form ≤ max_mid_form_ratio
- pricing_posture: discount_ratio ≥ 0.20
- cover_art_identity: no 100% style_pool overlap between brands
- canonical IDs (personas, topics): NEVER modified
