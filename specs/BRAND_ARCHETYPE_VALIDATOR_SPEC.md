# Brand Archetype Registry Validator Spec

**Purpose:** CI enforcement rules for the canonical brand archetype registry.  
**Authority:** Doctrine-locked; these must **fail** planning/CI, not warn.  
**Registry:** `config/catalog_planning/brand_archetype_registry.yaml` (schema v1.1)

---

## 1. Structural validators

| Rule | Fail when |
|------|-----------|
| `brand_id` unique | Any duplicate `brand_id` across `brand_archetypes`. |
| `admin_id` unique | Any duplicate `admin_id` across `brand_archetypes`. |
| Persona + moment unique | Any duplicate `(gtm_identity.persona, gtm_identity.primary_moment)` across brands. |
| Duration sums to 1.0 | For any brand, `duration_strategy.micro_sessions + duration_strategy.deep_dives + duration_strategy.mid_form != 1.0`. |
| Mid-form cap | Any brand has `duration_strategy.mid_form > global_constraints.max_mid_form_ratio` (default 0.25). |
| Lead voice exclusive | Any `voice_identity.lead_voice` value appears as `lead_voice` in more than one brand. |
| Cover art separation | Any brand’s `cover_art_identity.style_pool` overlaps 100% with another brand’s `style_pool` (same set of styles). |
| Required fields | Any brand is missing a top-level key listed in `global_constraints.required_fields`. |

---

## 2. Vocabulary validators

| Rule | Fail when |
|------|-----------|
| Emotional tokens tracked | (Planning phase: emotional token usage is aggregated across plans; validator may only check that brand-level `emotional_vocabulary` structure is present and that tokens are within allowed sets.) |
| Per-brand quotas | Any brand uses an emotional token beyond its per-brand quota (e.g. `quota_exceptions.reset.per_brand_max`). |
| Global emotional caps | At planning phase, global usage of a token (e.g. `reset`, `clarity`, `calm`) exceeds `global_constraints.emotional_token_global_caps`. |
| Forbidden title tokens | Any title pattern or title-related field contains a token in `global_constraints.forbidden_title_tokens` (e.g. `guaranteed`, `instant`, `cure`). |

*Note:* Registry validation alone can enforce structure and forbidden tokens in registry-defined title patterns. Full global emotional caps require a separate planning-phase validator that sees all BookPlans.

---

## 3. Voice validators

| Rule | Fail when |
|------|-----------|
| Per-voice per-brand cap | Any voice is used in more than 25 books for a single brand (requires catalog/plan context). |
| Per-voice global cap | Any voice is used in more than 60 books globally (requires catalog/plan context). |
| Lead voice share | Lead voice usage is not between 30% and 50% of that brand’s catalog (requires catalog/plan context). |

*Note:* Registry validation can only check that `lead_voice` is unique across brands and that voice identifiers are present. The 25/60/30–50% rules are enforced at **planning time** when a catalog or BookPlan set is available.

---

## 4. Pricing validators

| Rule | Fail when |
|------|-----------|
| Discount ratio | Fewer than 20% of a brand’s catalog is discounted (requires catalog/plan context). |
| Discount clustering | More than 2 consecutive release weeks have discounted books only (requires release calendar). |
| Google Play ≤ external | For any product, Google Play price &gt; external platform price (requires pricing feed). |
| Deep dive bundle anchor | Deep dive product does not anchor bundle pricing where bundles exist (requires bundle definition). |

*Note:* Registry validation can only check that each brand has `pricing_posture` with `discount_ratio: 0.20` (or equivalent). The remaining pricing rules are enforced at **planning/release** when catalog and pricing data exist.

---

## 5. CI gate behavior

- **Registry-only validator (this spec):**  
  Run on the registry YAML only. Fail on: structural violations, missing required fields, duplicate lead_voice, 100% style_pool overlap, duration sum ≠ 1.0, mid_form &gt; max, and forbidden title tokens in any registry-defined title pattern.

- **Planning-phase validators (separate):**  
  Run when BookPlans or catalog are available. Enforce: global emotional caps, per-voice 25/60 and lead 30–50%, discount 20% and no &gt;2 consecutive discounted weeks, Google Play ≤ external, deep dive bundle anchor.

---

## 6. Tooling

```bash
# Validate registry (structural + registry-level vocabulary)
PYTHONPATH=. python3 phoenix_v4/qa/validate_brand_archetype_registry.py
```

Exit code: **0** if all registry checks pass; **1** if any check fails. No warnings-only mode; violations must fail CI.
