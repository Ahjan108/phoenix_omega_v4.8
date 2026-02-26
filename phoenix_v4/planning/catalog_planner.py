"""
Stage 1 Catalog Planner.
Produces BookSpec from config/catalog_planning/ (domain_definitions, series_templates, capacity_constraints).
Contract: specs/OMEGA_LAYER_CONTRACTS.md — BookSpec required and identity fields.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class AtomsModel(str, Enum):
    """Legacy vs cluster atoms layout. Policy: legacy_personas → legacy; else cluster."""
    LEGACY = "legacy"
    CLUSTER = "cluster"

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
CONFIG_LOCALIZATION = REPO_ROOT / "config" / "localization"
CONFIG_AUTHORING = REPO_ROOT / "config" / "authoring"


@dataclass
class BookSpec:
    """Stage 1 output. Stage 2 consumes required; identity passed through to Stage 3.
    author_id / author_positioning_profile: Layer 2 Identity (Writer Spec §24).
    If author_id present, author_positioning_profile is required and must match registry."""
    topic_id: str
    persona_id: str
    series_id: Optional[str]
    installment_number: Optional[int]
    teacher_id: str
    brand_id: str
    angle_id: str
    domain_id: str
    seed: str
    locale: str = "en-US"
    territory: str = "US"
    teacher_mode: bool = False
    author_id: Optional[str] = None
    author_positioning_profile: Optional[str] = None
    narrator_id: Optional[str] = None
    atoms_model: Optional[AtomsModel] = None

    def to_dict(self) -> dict[str, Any]:
        out = {
            "topic_id": self.topic_id,
            "persona_id": self.persona_id,
            "series_id": self.series_id,
            "installment_number": self.installment_number,
            "teacher_id": self.teacher_id,
            "brand_id": self.brand_id,
            "angle_id": self.angle_id,
            "domain_id": self.domain_id,
            "seed": self.seed,
            "locale": self.locale,
            "territory": self.territory,
            "teacher_mode": self.teacher_mode,
        }
        if self.author_id is not None:
            out["author_id"] = self.author_id
        if self.author_positioning_profile is not None:
            out["author_positioning_profile"] = self.author_positioning_profile
        if self.narrator_id is not None:
            out["narrator_id"] = self.narrator_id
        if self.atoms_model is not None:
            out["atoms_model"] = self.atoms_model.value
        return out


class CatalogPlanner:
    """Produces BookSpec(s) from catalog config. Deterministic when seed is fixed."""

    def __init__(
        self,
        domain_path: Optional[Path] = None,
        series_path: Optional[Path] = None,
        capacity_path: Optional[Path] = None,
        brands_path: Optional[Path] = None,
        locale_registry_path: Optional[Path] = None,
        author_registry_path: Optional[Path] = None,
        positioning_profiles_path: Optional[Path] = None,
    ):
        domain_path = domain_path or (CONFIG_CATALOG / "domain_definitions.yaml")
        series_path = series_path or (CONFIG_CATALOG / "series_templates.yaml")
        capacity_path = capacity_path or (CONFIG_CATALOG / "capacity_constraints.yaml")
        brands_path = brands_path or (CONFIG_LOCALIZATION / "brand_registry_locale_extension.yaml")
        locale_registry_path = locale_registry_path or (CONFIG_LOCALIZATION / "locale_registry.yaml")
        author_registry_path = author_registry_path or (REPO_ROOT / "config" / "author_registry.yaml")
        positioning_profiles_path = positioning_profiles_path or (CONFIG_AUTHORING / "author_positioning_profiles.yaml")
        self._domains = self._load_yaml(domain_path)
        self._series = self._load_yaml(series_path)
        self._capacity = self._load_yaml(capacity_path)
        brands_data = self._load_yaml(brands_path)
        self._brands = brands_data.get("brands") or {}
        self._locale_registry_path = locale_registry_path
        self._locale_registry: Optional[dict] = None
        self._author_registry_path = author_registry_path
        self._positioning_profiles_path = positioning_profiles_path
        self._author_registry: Optional[dict] = None
        self._positioning_profiles: Optional[dict] = None

    @staticmethod
    def _load_yaml(p: Path) -> dict:
        if not p.exists() or yaml is None:
            return {}
        with open(p) as f:
            return yaml.safe_load(f) or {}

    def _load_locale_registry(self) -> dict:
        if self._locale_registry is not None:
            return self._locale_registry
        self._locale_registry = self._load_yaml(self._locale_registry_path)
        return self._locale_registry

    def _load_author_registry(self) -> dict:
        if self._author_registry is not None:
            return self._author_registry
        self._author_registry = self._load_yaml(self._author_registry_path)
        return self._author_registry

    def _load_positioning_profiles(self) -> dict:
        if self._positioning_profiles is not None:
            return self._positioning_profiles
        self._positioning_profiles = self._load_yaml(self._positioning_profiles_path)
        return self._positioning_profiles

    def _resolve_author_positioning(
        self,
        author_id: Optional[str],
        brand_id: str,
        caller_positioning: Optional[str],
    ) -> Optional[str]:
        """Resolve author_positioning_profile. FAIL if author_id present but mismatch or missing."""
        profiles = self._load_positioning_profiles()
        profile_keys = set((profiles.get("profiles") or {}).keys())
        default_by_brand = (profiles.get("default_by_brand") or {})
        if author_id:
            authors = (self._load_author_registry().get("authors") or {})
            author_cfg = authors.get(author_id)
            if not author_cfg:
                raise ValueError(f"author_id '{author_id}' not found in author_registry.yaml")
            registry_profile = author_cfg.get("positioning_profile")
            if not registry_profile:
                raise ValueError(
                    f"author_id '{author_id}' has no positioning_profile in author_registry.yaml. "
                    "Required by Writer Spec §24."
                )
            if registry_profile not in profile_keys:
                raise ValueError(
                    f"author_id '{author_id}' positioning_profile '{registry_profile}' not found in "
                    "config/authoring/author_positioning_profiles.yaml"
                )
            if caller_positioning is not None and caller_positioning != registry_profile:
                raise ValueError(
                    f"BookSpec author_positioning_profile '{caller_positioning}' does not match "
                    f"author_registry for author_id '{author_id}' (expected '{registry_profile}')."
                )
            return registry_profile
        # No author_id: use default_by_brand for this brand when available
        return default_by_brand.get(brand_id)

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
        locale: Optional[str] = None,
        territory: Optional[str] = None,
        teacher_mode: bool = False,
        author_id: Optional[str] = None,
        author_positioning_profile: Optional[str] = None,
        narrator_id: Optional[str] = None,
        atoms_model: Optional[AtomsModel] = None,
    ) -> BookSpec:
        """Produce one BookSpec. Required: topic_id, persona_id.

        atoms_model: optional; caller sets (e.g. from legacy_personas). Planner does not infer.
        locale resolution: 1) caller-supplied 2) brand_registry[brand_id].locale 3) en-US.
        territory resolution: 1) caller-supplied 2) brand_registry[brand_id].territory 3) US.
        teacher_mode: when True, Stage 3 uses teacher_banks/<teacher_id>/approved_atoms/ for pools.
        author_id: when set, author_positioning_profile is resolved from author_registry (mandatory there).
        author_positioning_profile: if supplied with author_id, must match registry or Stage 1 fails.
        narrator_id: optional; when set, validated against narrator_registry (Writer Spec §23.5).
        """
        if not topic_id or not persona_id:
            raise ValueError("BookSpec requires topic_id and persona_id")
        positioning = self._resolve_author_positioning(author_id, brand_id, author_positioning_profile)

        series_cfg = self._series.get("series") or {}
        brand_cfg = self._brands.get(brand_id) or {}

        # Locale and territory from brand when not supplied
        if locale is None:
            locale = brand_cfg.get("locale") or "en-US"
        if territory is None:
            territory = brand_cfg.get("territory") or "US"

        # Validate locale exists in registry when registry is present
        if self._locale_registry_path and self._locale_registry_path.exists():
            locale_reg = self._load_locale_registry()
            locales = locale_reg.get("locales") or {}
            if locale not in locales:
                raise ValueError(
                    f"locale '{locale}' not found in locale_registry.yaml. "
                    "Add it there before using it in a BookSpec."
                )

        # Path 1: Series-based angle resolution
        if series_id and not angle_id:
            s = series_cfg.get(series_id) or {}
            angles = s.get("angles") or []
            if angles:
                angle_id = angles[0]

        # Path 2: Series-based domain resolution
        if series_id and not domain_id:
            s = series_cfg.get(series_id) or {}
            domain_id = s.get("domain") or domain_id

        # Path 3: Derive angle from topic + persona when series absent
        if not angle_id:
            angle_id = self._derive_angle(topic_id, persona_id, series_cfg)

        if not domain_id:
            domain_id = self._topic_to_domain(topic_id)

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
            locale=locale,
            territory=territory,
            teacher_mode=teacher_mode,
            author_id=author_id,
            author_positioning_profile=positioning,
            narrator_id=narrator_id,
            atoms_model=atoms_model,
        )

    def _derive_angle(
        self,
        topic_id: str,
        persona_id: str,
        series_cfg: dict,
    ) -> str:
        """Derive a real angle from topic_id + persona_id.

        Strategy:
        1. Find series in config whose domain maps to this topic_id.
        2. Among those, prefer series with persona_affinity.high containing persona_id.
        3. Return first angle from the best-matched series.
        4. If nothing matches, return topic_id + "_general" (still better than "default_angle").
        """
        topic_to_domain = {
            "relationship_anxiety": "anxiety_cluster",
            "grief": "grief_cluster",
            "shame": "shame_cluster",
            "self_worth": "shame_cluster",
        }
        target_domain = topic_to_domain.get(topic_id)

        best_series = None
        best_score = -1

        for series_id, s_cfg in series_cfg.items():
            angles = s_cfg.get("angles") or []
            if not angles:
                continue

            series_domain = s_cfg.get("domain")
            if target_domain and series_domain != target_domain:
                continue

            affinity = s_cfg.get("persona_affinity") or {}
            high = affinity.get("high") or []
            medium = affinity.get("medium") or []

            if persona_id in high:
                score = 2
            elif persona_id in medium:
                score = 1
            else:
                score = 0

            if score > best_score:
                best_score = score
                best_series = s_cfg

        if best_series:
            angles = best_series.get("angles") or []
            if angles:
                return angles[0]

        return f"{topic_id}_general"

    def _topic_to_domain(self, topic_id: str) -> str:
        """Map topic_id to domain_id. Inverse of _domain_to_topic."""
        m = {
            "relationship_anxiety": "anxiety_cluster",
            "grief": "grief_cluster",
            "shame": "shame_cluster",
            "self_worth": "shame_cluster",
        }
        return m.get(topic_id, "default_domain")

    def produce_wave(
        self,
        n: int,
        seed: str = "wave_seed",
        teacher_id: str = "default_teacher",
        brand_id: str = "phoenix",
        locale: Optional[str] = None,
        territory: Optional[str] = None,
        teacher_mode: bool = False,
    ) -> list[BookSpec]:
        """Produce n BookSpecs from series/angles. Deterministic given n and seed.
        locale/territory default from brand config when not supplied.
        teacher_mode: when True, Stage 3 uses teacher_banks/<teacher_id>/approved_atoms/.
        """
        series_cfg = self._series.get("series") or {}
        if not series_cfg:
            return []
        brand_cfg = self._brands.get(brand_id) or {}
        wave_locale = locale or brand_cfg.get("locale") or "en-US"
        wave_territory = territory or brand_cfg.get("territory") or "US"
        series_ids = list(series_cfg.keys())
        h = hashlib.sha256(f"{seed}:{n}".encode()).digest()
        specs: list[BookSpec] = []
        for i in range(n):
            s_idx = (int.from_bytes(h[:4], "big") + i) % len(series_ids)
            series_id = series_ids[s_idx]
            s = series_cfg[series_id]
            angles = s.get("angles") or ["default_angle"]
            a_idx = (int.from_bytes(h[4:8], "big") + i) % len(angles)
            angle_id = angles[a_idx]
            domain_id = s.get("domain") or "default_domain"
            persona_affinity = s.get("persona_affinity") or {}
            high = persona_affinity.get("high") or ["nyc_exec"]
            persona_id = high[i % len(high)]
            topic_id = self._domain_to_topic(domain_id)
            inst = (i // (len(angles) * max(len(high), 1))) + 1
            spec_seed = hashlib.sha256(f"{seed}:{i}:{series_id}:{angle_id}".encode()).hexdigest()[:24]
            positioning = self._resolve_author_positioning(None, brand_id, None)
            specs.append(BookSpec(
                topic_id=topic_id,
                persona_id=persona_id,
                series_id=series_id,
                installment_number=inst,
                teacher_id=teacher_id,
                brand_id=brand_id,
                angle_id=angle_id,
                domain_id=domain_id,
                seed=spec_seed,
                locale=wave_locale,
                territory=wave_territory,
                teacher_mode=teacher_mode,
                author_id=None,
                author_positioning_profile=positioning,
            ))
        return specs

    def _domain_to_topic(self, domain_id: str) -> str:
        """Map domain to a topic slug used by Stage 2 / atoms."""
        m = {
            "anxiety_cluster": "relationship_anxiety",
            "grief_cluster": "grief",
            "shame_cluster": "shame",
        }
        return m.get(domain_id, "relationship_anxiety")


def book_spec_digest(spec: BookSpec) -> str:
    """Stable digest for determinism checks."""
    payload = json.dumps(spec.to_dict(), sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
