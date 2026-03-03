"""
CI Gate #49: locale_territory_consistency.
Runs before any distribution step. Authority: del_location_plan/locale_strategy.md.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Tuple

if TYPE_CHECKING:
    from phoenix_v4.planning.catalog_planner import BookSpec

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_LOCALIZATION = REPO_ROOT / "config" / "localization"
LOCALE_REGISTRY_PATH = CONFIG_LOCALIZATION / "locale_registry.yaml"

# Expected territory per locale (for storefront routing consistency)
_LOCALE_TO_TERRITORY = {
    "en-US": "US",
    "zh-CN": "CN",
    "zh-TW": "TW",
    "zh-HK": "HK",
    "zh-SG": "SG",
    "ja-JP": "JP",
    "ko-KR": "KR",
    "es-US": "US",
    "es-ES": "ES",
    "fr-FR": "FR",
    "de-DE": "DE",
    "hu-HU": "HU",
}


def _load_locale_registry(path: Optional[Path] = None) -> dict[str, Any]:
    p = path or LOCALE_REGISTRY_PATH
    if not p.exists():
        return {}
    try:
        import yaml
        with open(p) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def gate_49_locale_territory_consistency(
    book_spec: "BookSpec",
    locale_registry_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """CI Gate #49: locale and territory consistency before distribution.

    Enforces:
    - locale is a valid key in locale_registry.yaml
    - territory matches the locale's expected territory (when rule enabled)
    - Prevents zh-TW in US storefronts, en-US in TW storefronts, etc.

    Returns:
        (True, "OK") if pass, (False, reason) if fail.
    """
    locale_reg = _load_locale_registry(locale_registry_path)
    locales = locale_reg.get("locales") or {}

    if not locales:
        # No registry present: allow any locale/territory (backward compat)
        return True, "OK"

    locale = getattr(book_spec, "locale", "en-US")
    territory = getattr(book_spec, "territory", "US")

    if locale not in locales:
        return False, f"Unknown locale: {locale}. Add it to locale_registry.yaml before distribution."

    rules = locale_reg.get("distribution_rules") or {}
    if not rules.get("locale_mismatch_is_ci_failure", True):
        return True, "OK"

    expected_territory = _LOCALE_TO_TERRITORY.get(locale)
    if expected_territory and territory != expected_territory:
        return False, (
            f"Locale {locale} expects territory {expected_territory}, got {territory}. "
            "This would route the book to wrong storefronts."
        )

    # hu-HU: flag for ElevenLabs (no Google Neural2) — could add a specific check here
    return True, "OK"
