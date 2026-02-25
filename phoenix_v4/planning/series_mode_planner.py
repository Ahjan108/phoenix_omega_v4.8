"""
Series Roadmap Planner (P0).

Produces per-installment roadmap: installment_number, search_intent_id (unique in series),
primary_mechanism_id, journey_shape_id, band_curve_id, book_structure_id, duration_class.
Deterministic by seed; search_intent_id is unique across installments in the series.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_SOT = REPO_ROOT / "config" / "source_of_truth"
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _digest(seed: str, series_id: str, topic_id: str, persona_id: str, installment: int, slot: str) -> bytes:
    """Deterministic digest for weighted selection per installment/slot."""
    payload = f"{seed}|{series_id}|{topic_id}|{persona_id}|{installment}|{slot}"
    return hashlib.sha256(payload.encode("utf-8")).digest()


def _weighted_select(candidates: list[str], digest: bytes) -> str:
    if not candidates:
        return ""
    idx = int.from_bytes(digest[:4], "big") % len(candidates)
    return candidates[idx]


def plan_series_roadmap(
    series_id: str,
    topic_id: str,
    persona_id: str,
    num_installments: int,
    seed: str = "default_seed",
    config_root: Optional[Path] = None,
    catalog_config: Optional[Path] = None,
) -> list[dict[str, Any]]:
    """
    Return one roadmap row per installment (1..num_installments). Each row includes:
    installment_number, search_intent_id, primary_mechanism_id, journey_shape_id,
    band_curve_id, book_structure_id, duration_class.
    search_intent_id is unique across installments (deterministic assignment from registry).
    """
    config_root = config_root or CONFIG_SOT
    catalog_config = catalog_config or CONFIG_CATALOG

    roadmap_reg = _load_yaml(catalog_config / "series_roadmap_registry.yaml")
    structures = _load_yaml(config_root / "book_structure_archetypes.yaml")
    journey = _load_yaml(config_root / "journey_shapes.yaml")

    search_intent_ids = roadmap_reg.get("search_intent_ids") or ["problem_solving", "life_transition", "behavioral_change"]
    primary_mechanism_ids = roadmap_reg.get("primary_mechanism_ids") or ["nervous_system_safety", "shame_reduction"]
    band_curve_ids = roadmap_reg.get("band_curve_ids") or ["gentle_rise", "two_peak", "steady_build"]
    duration_classes = roadmap_reg.get("duration_classes") or ["short", "mid", "full"]

    arch_list = list((structures.get("archetypes") or {}).keys())
    journey_list = list((journey.get("shapes") or {}).keys())
    if not arch_list:
        arch_list = ["linear_transformation"]
    if not journey_list:
        journey_list = ["recognition_to_agency"]

    # Assign unique search_intent_id per installment: deterministic permutation of registry
    # so each installment gets a distinct id from the list (cycle if num_installments > len(list))
    series_digest = _digest(seed, series_id, topic_id, persona_id, 0, "search_intent_perm")
    perm_start = int.from_bytes(series_digest[:4], "big") % max(1, len(search_intent_ids))
    assigned_intents: list[str] = []
    for i in range(num_installments):
        idx = (perm_start + i) % len(search_intent_ids)
        assigned_intents.append(search_intent_ids[idx])

    rows: list[dict[str, Any]] = []
    for inst in range(1, num_installments + 1):
        row = {
            "installment_number": inst,
            "search_intent_id": assigned_intents[inst - 1],
            "primary_mechanism_id": _weighted_select(
                primary_mechanism_ids,
                _digest(seed, series_id, topic_id, persona_id, inst, "primary_mechanism"),
            ),
            "journey_shape_id": _weighted_select(
                journey_list,
                _digest(seed, series_id, topic_id, persona_id, inst, "journey_shape"),
            ),
            "band_curve_id": _weighted_select(
                band_curve_ids,
                _digest(seed, series_id, topic_id, persona_id, inst, "band_curve"),
            ),
            "book_structure_id": _weighted_select(
                arch_list,
                _digest(seed, series_id, topic_id, persona_id, inst, "book_structure"),
            ),
            "duration_class": _weighted_select(
                duration_classes,
                _digest(seed, series_id, topic_id, persona_id, inst, "duration_class"),
            ),
        }
        rows.append(row)
    return rows
