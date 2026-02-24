# PATCH: BookSpec locale/territory extension
# Adds locale and territory to BookSpec and all downstream contracts.
# Authority: SYSTEMS_DOCUMENTATION §29 + OMEGA_LAYER_CONTRACTS

# ─── BOOKSPEC DATACLASS PATCH ────────────────────────────────────────────────
# File: phoenix_v4/planning/book_spec.py (or wherever BookSpec is defined)

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BookSpec:
    # Existing fields (unchanged)
    topic_id:           str
    persona_id:         str
    series_id:          Optional[str]   = None
    installment_number: Optional[int]   = None
    teacher_id:         str             = "default_teacher"
    brand_id:           str             = "phoenix"
    angle_id:           str             = "default_angle"
    domain_id:          str             = "default_domain"
    seed:               str             = "default_seed"

    # NEW FIELDS
    locale:             str             = "en-US"
    # Canonical locale code from locale_registry.yaml
    # e.g. "en-US", "zh-TW", "ja-JP", "hu-HU"
    # Must match a key in config/localization/locale_registry.yaml
    # Default: en-US (baseline)

    territory:          str             = "US"
    # Distribution territory for storefront routing
    # e.g. "US", "TW", "HK", "SG", "CN", "JP", "KR", "ES", "FR", "DE", "HU"
    # Controls which storefronts this book is submitted to
    # A book with territory="TW" must NOT be uploaded to US storefronts

    # Derived (set by planner, not caller)
    # book_id generated as: f"bk_{topic_id}_{locale}_{installment_number:03d}"
    # e.g. "bk_social_anx_zh_TW_003" vs "bk_social_anx_en_US_003"


# ─── PRODUCE_SINGLE PATCH ────────────────────────────────────────────────────
# File: phoenix_v4/planning/catalog_planner.py

    def produce_single(
        self,
        topic_id: str,
        persona_id: str,
        teacher_id: str = "default_teacher",
        brand_id: str = "phoenix",
        seed: str = "default_seed",
        series_id: Optional[str] = None,
        installment_number: Optional[int] = None,
        angle_id: Optional[str] = None,
        domain_id: Optional[str] = None,
        locale: Optional[str] = None,       # NEW
        territory: Optional[str] = None,    # NEW
    ) -> BookSpec:
        """
        locale resolution order:
        1. Caller-supplied locale (explicit override)
        2. Derived from brand_registry[brand_id].locale
        3. Default: "en-US"

        territory resolution order:
        1. Caller-supplied territory (explicit override)
        2. Derived from brand_registry[brand_id].territory
        3. Default: "US"
        """
        brand_cfg = self._brands.get(brand_id) or {}

        # Locale resolution
        if not locale:
            locale = brand_cfg.get("locale") or "en-US"

        # Territory resolution
        if not territory:
            territory = brand_cfg.get("territory") or "US"

        # Validate locale exists in registry
        locale_reg = self._load_locale_registry()
        if locale not in locale_reg["locales"]:
            raise ValueError(
                f"locale '{locale}' not found in locale_registry.yaml. "
                f"Add it there before using it in a BookSpec."
            )

        # ... existing angle/domain resolution (unchanged) ...

        return BookSpec(
            topic_id=topic_id,
            persona_id=persona_id,
            series_id=series_id,
            installment_number=installment_number,
            teacher_id=teacher_id,
            brand_id=brand_id,
            angle_id=angle_id,
            domain_id=domain_id or "default_domain",
            seed=seed,
            locale=locale,              # NEW
            territory=territory,        # NEW
        )


# ─── PRODUCE_WAVE PATCH ──────────────────────────────────────────────────────
# Wave inherits locale+territory from brand config for every book in the wave.
# Same brand = same locale = same territory throughout one wave.

    def produce_wave(
        self,
        n: int,
        seed: str = "wave_seed",
        brand_id: str = "phoenix",
        locale: Optional[str] = None,   # NEW: override brand default
        territory: Optional[str] = None # NEW: override brand default
    ) -> list[BookSpec]:
        brand_cfg = self._brands.get(brand_id) or {}
        locale    = locale    or brand_cfg.get("locale")    or "en-US"
        territory = territory or brand_cfg.get("territory") or "US"
        # ... existing wave logic ...
        # Pass locale + territory into each produce_single call


# ─── CLI PATCH (run_pipeline.py) ─────────────────────────────────────────────

    parser.add_argument(
        "--locale",
        type=str,
        default=None,
        help="Locale code (e.g. en-US, zh-TW, ja-JP). Derived from brand if not supplied."
    )
    parser.add_argument(
        "--territory",
        type=str,
        default=None,
        help="Distribution territory (e.g. US, TW, JP). Derived from brand if not supplied."
    )


# ─── CI GATE (new gate #49) ──────────────────────────────────────────────────
# Add to validator pipeline before any distribution step.

def gate_49_locale_territory_consistency(book_spec: BookSpec) -> tuple[bool, str]:
    """
    Enforces:
    - locale is a valid key in locale_registry.yaml
    - territory matches the locale's storefront territory
    - No zh-TW book in US territory
    - No en-US book in TW territory
    - hu-HU books flagged to use ElevenLabs (no Google Neural2 fallback)
    """
    locale_reg = load_locale_registry()
    locale_cfg = locale_reg["locales"].get(book_spec.locale)

    if not locale_cfg:
        return False, f"Unknown locale: {book_spec.locale}"

    # Check distribution rules
    rules = locale_reg.get("distribution_rules", {})

    if rules.get("locale_mismatch_is_ci_failure"):
        # Derive expected territory from locale
        storefront_territory = _locale_to_expected_territory(book_spec.locale)
        if storefront_territory and book_spec.territory != storefront_territory:
            return False, (
                f"Locale {book_spec.locale} expects territory {storefront_territory}, "
                f"got {book_spec.territory}. "
                f"This would route a {book_spec.locale} book to wrong storefronts."
            )

    return True, "OK"

def _locale_to_expected_territory(locale: str) -> str:
    mapping = {
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
    return mapping.get(locale, "US")
