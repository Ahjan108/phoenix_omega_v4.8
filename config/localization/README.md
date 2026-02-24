# Localization config

- **locale_registry.yaml** — Canonical locale definitions (language, script, TTS provider, storefront IDs). Single source of truth for locale codes. Add new locales here first.
- **brand_registry_locale_extension.yaml** — Per-brand `locale` and `territory`. One brand = one locale. Books inherit locale/territory from their brand.

**Strategy:** See `del_location_plan/locale_strategy.md` (architecture: one brand = one locale; rollout phases; distribution routing; CI gate #49).

**Usage:** `CatalogPlanner` loads these when resolving `locale` and `territory` for `BookSpec`. If a brand is not in the extension, defaults are `en-US` / `US`. Gate #49: `phoenix_v4/qa/locale_territory_gate.gate_49_locale_territory_consistency(book_spec)` runs before distribution.
