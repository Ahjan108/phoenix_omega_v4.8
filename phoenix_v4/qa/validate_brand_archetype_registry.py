#!/usr/bin/env python3
"""
Brand Archetype Registry validator (CI gate).

Enforces: schema v1.1, structural rules, and registry-level vocabulary/voice rules.
Authority: specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md.
Exit 1 on any failure.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


REQUIRED_FIELDS = [
    "brand_id",
    "admin_id",
    "gtm_identity",
    "discovery_contract",
    "structural_signature",
    "duration_strategy",
    "emotional_vocabulary",
    "voice_identity",
    "cover_art_identity",
    "pricing_posture",
]

DURATION_KEYS = ("micro_sessions", "deep_dives", "mid_form")


def _load_registry(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Registry must be a YAML mapping, got {type(data)}")
    return data


def _get_brands(data: dict) -> list[dict]:
    brands = data.get("brand_archetypes")
    if brands is None:
        return []
    if not isinstance(brands, list):
        return []
    return [b for b in brands if isinstance(b, dict)]


def _persona_moment(b: dict) -> tuple[str, str]:
    gtm = b.get("gtm_identity") or {}
    persona = gtm.get("persona")
    moment = gtm.get("primary_moment")
    return (str(persona) if persona is not None else "", str(moment) if moment is not None else "")


def _duration_sum(b: dict) -> float:
    ds = b.get("duration_strategy") or {}
    return sum(float(ds.get(k) or 0) for k in DURATION_KEYS)


def _mid_form(b: dict) -> float:
    ds = b.get("duration_strategy") or {}
    return float(ds.get("mid_form") or 0)


def _style_pool_set(b: dict) -> frozenset:
    cov = b.get("cover_art_identity") or {}
    pool = cov.get("style_pool")
    if isinstance(pool, list):
        return frozenset(str(x) for x in pool)
    return frozenset()


def _lead_voice(b: dict) -> str | None:
    vi = b.get("voice_identity") or {}
    lead = vi.get("lead_voice")
    return str(lead) if lead is not None else None


def validate_registry(data: dict) -> list[str]:
    errors: list[str] = []
    constraints = data.get("global_constraints") or {}
    max_mid = float(constraints.get("max_mid_form_ratio") or 0.25)
    required = list(constraints.get("required_fields") or REQUIRED_FIELDS)
    forbidden_tokens = set(constraints.get("forbidden_title_tokens") or [])

    brands = _get_brands(data)
    if not brands:
        errors.append("Registry has no brand_archetypes (or not a list of maps).")
        return errors

    brand_ids: list[str] = []
    admin_ids: list[str] = []
    persona_moments: list[tuple[str, str]] = []
    lead_voices: list[str] = []
    style_pools: list[frozenset] = []

    for i, b in enumerate(brands):
        bid = b.get("brand_id")
        aid = b.get("admin_id")
        if bid is not None:
            brand_ids.append(str(bid))
        if aid is not None:
            admin_ids.append(str(aid))

        for key in required:
            if key not in b or b[key] is None:
                errors.append(f"Brand index {i} (brand_id={bid!r}): missing required field {key!r}.")

        dur_sum = _duration_sum(b)
        if abs(dur_sum - 1.0) > 1e-6:
            errors.append(f"Brand {bid!r}: duration_strategy sum is {dur_sum}, must be 1.0.")

        mid = _mid_form(b)
        if mid > max_mid:
            errors.append(f"Brand {bid!r}: mid_form {mid} > max_mid_form_ratio {max_mid}.")

        persona_moments.append(_persona_moment(b))
        lead_voices.append(_lead_voice(b) or "")
        style_pools.append(_style_pool_set(b))

    # Uniqueness
    if len(brand_ids) != len(set(brand_ids)):
        seen: set[str] = set()
        for bid in brand_ids:
            if bid in seen:
                errors.append(f"Duplicate brand_id: {bid!r}.")
            seen.add(bid)

    if len(admin_ids) != len(set(admin_ids)):
        seen = set()
        for aid in admin_ids:
            if aid in seen:
                errors.append(f"Duplicate admin_id: {aid!r}.")
            seen.add(aid)

    pm_counts = Counter(persona_moments)
    for pm, count in pm_counts.items():
        if count > 1:
            errors.append(f"Duplicate (persona, primary_moment) across brands: {pm!r}.")

    # Lead voice may not be reused as lead_voice in another brand
    lead_nonempty = [v for v in lead_voices if v]
    if len(lead_nonempty) != len(set(lead_nonempty)):
        c = Counter(lead_nonempty)
        for voice, count in c.items():
            if count > 1:
                errors.append(f"lead_voice reused: {voice!r}.")

    # style_pool may not overlap 100% with another brand
    for i, si in enumerate(style_pools):
        if not si:
            continue
        for j, sj in enumerate(style_pools):
            if i != j and si == sj:
                errors.append(
                    f"Brand {brands[i].get('brand_id')!r} and {brands[j].get('brand_id')!r} "
                    "have identical cover_art_identity.style_pool."
                )
                break

    # Forbidden title tokens: if registry had title_pattern or similar, check here.
    # Spec says "forbidden tokens may never appear in title pattern"; no title field in current schema, so skip unless we add one.

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate brand archetype registry (CI gate).")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent / "config" / "catalog_planning" / "brand_archetype_registry.yaml",
        help="Path to brand_archetype_registry.yaml",
    )
    args = parser.parse_args()
    if not args.registry.exists():
        print(f"Registry not found: {args.registry}", file=sys.stderr)
        return 1
    try:
        data = _load_registry(args.registry)
    except Exception as e:
        print(f"Failed to load registry: {e}", file=sys.stderr)
        return 1
    errors = validate_registry(data)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
