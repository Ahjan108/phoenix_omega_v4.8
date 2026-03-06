"""
Robust, intelligent tests: config sanity, registry consistency, parametrized locale/config checks.
Fast sanity and data-driven tests to catch regressions early. See docs/ROBUST_INTELLIGENT_TESTING.md.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

# Required keys per locale in locale_registry.locales
LOCALE_REGISTRY_REQUIRED_KEYS = frozenset({
    "language", "region", "script", "direction", "tts_locale_code",
    "catalog_language", "storefront_ids",
})
# Required keys per locale in content_roots.locales
CONTENT_ROOTS_REQUIRED_KEYS = frozenset({
    "atoms_root", "translation_source_locale", "translation_output_root",
    "population_status", "rollout_phase",
})
# EU catalogue locales (must appear in locale_groups.european)
EU_CATALOGUE_LOCALES = {"de-DE", "es-ES", "fr-FR", "it-IT", "hu-HU"}


@pytest.mark.sanity
@pytest.mark.intelligent
def test_locale_registry_content_roots_consistency(
    locale_registry: dict,
    content_roots: dict,
    all_locale_ids: list[str],
) -> None:
    """Every locale in locale_registry has a matching entry in content_roots_by_locale."""
    reg_locales = set((locale_registry.get("locales") or {}).keys())
    cr_locales = set((content_roots.get("locales") or {}).keys())
    missing_in_content_roots = reg_locales - cr_locales
    missing_in_registry = cr_locales - reg_locales
    assert not missing_in_content_roots, (
        f"Locales in locale_registry but not in content_roots_by_locale: {missing_in_content_roots}"
    )
    assert not missing_in_registry, (
        f"Locales in content_roots_by_locale but not in locale_registry: {missing_in_registry}"
    )


@pytest.mark.intelligent
def test_each_locale_has_required_registry_fields(locale_registry: dict) -> None:
    """Each locale in registry has required fields (single test, loop)."""
    locales = locale_registry.get("locales") or {}
    for locale_id, entry in locales.items():
        missing = LOCALE_REGISTRY_REQUIRED_KEYS - set(entry.keys())
        assert not missing, f"Locale {locale_id} missing keys: {missing}"


@pytest.mark.intelligent
def test_each_locale_has_required_content_roots_fields(content_roots: dict) -> None:
    """Each locale in content_roots has required fields."""
    locales = content_roots.get("locales") or {}
    for locale_id, entry in locales.items():
        missing = CONTENT_ROOTS_REQUIRED_KEYS - set(entry.keys())
        assert not missing, f"Content roots locale {locale_id} missing keys: {missing}"


@pytest.mark.sanity
@pytest.mark.intelligent
def test_eu_catalogue_locales_present(locale_registry: dict) -> None:
    """EU catalogue group includes de-DE, es-ES, fr-FR, it-IT, hu-HU."""
    groups = locale_registry.get("locale_groups") or {}
    european = set(groups.get("european") or [])
    for loc in EU_CATALOGUE_LOCALES:
        assert loc in european, f"EU catalogue locale {loc} missing from locale_groups.european"
    # All european group entries should be valid locales
    locales = set((locale_registry.get("locales") or {}).keys())
    for loc in european:
        assert loc in locales, f"locale_groups.european has unknown locale: {loc}"


@pytest.mark.sanity
def test_no_duplicate_locale_ids(locale_registry: dict) -> None:
    """Locale IDs in registry and in all_locales group are unique."""
    locales = locale_registry.get("locales") or {}
    ids_list = list(locales.keys())
    assert len(ids_list) == len(set(ids_list)), "Duplicate locale IDs in registry"
    groups = locale_registry.get("locale_groups") or {}
    all_locales = groups.get("all_locales") or []
    assert len(all_locales) == len(set(all_locales)), "Duplicate locale IDs in all_locales"


@pytest.mark.intelligent
def test_locale_groups_all_locales_subset_of_registry(locale_registry: dict) -> None:
    """Every ID in locale_groups.all_locales exists in locales."""
    locales = set((locale_registry.get("locales") or {}).keys())
    groups = locale_registry.get("locale_groups") or {}
    all_locales = set(groups.get("all_locales") or [])
    unknown = all_locales - locales
    assert not unknown, f"all_locales contains unknown locale IDs: {unknown}"


@pytest.mark.sanity
def test_critical_config_yamls_load(repo_root: Path) -> None:
    """Critical config YAMLs load without error."""
    critical = [
        repo_root / "config" / "localization" / "locale_registry.yaml",
        repo_root / "config" / "localization" / "content_roots_by_locale.yaml",
        repo_root / "config" / "format_selection" / "format_registry.yaml",
    ]
    for path in critical:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert data is not None, f"Empty YAML: {path}"


@pytest.mark.sanity
def test_marketing_config_structure(repo_root: Path) -> None:
    """Marketing config (consumer_language_by_topic) has expected top-level structure if present."""
    path = repo_root / "config" / "marketing" / "consumer_language_by_topic.yaml"
    if not path.exists():
        pytest.skip("consumer_language_by_topic.yaml not present")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data is not None
    # Expect topic IDs as keys; at least one topic
    if isinstance(data, dict):
        assert len(data) >= 1, "consumer_language_by_topic should have at least one topic"


@pytest.mark.intelligent
def test_tts_locale_code_matches_locale_id(locale_registry: dict) -> None:
    """Each locale's tts_locale_code matches its locale ID (en-US, zh-CN, etc.)."""
    locales = locale_registry.get("locales") or {}
    for locale_id, entry in locales.items():
        tts = entry.get("tts_locale_code")
        if tts is None:
            continue
        # Normalize: locale_id is like en-US, tts_locale_code should match
        assert tts == locale_id, (
            f"Locale {locale_id}: tts_locale_code {tts} should match locale ID"
        )
