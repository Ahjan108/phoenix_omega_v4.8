"""
Arc alignment validator (Arc-First Canonical Spec v1.1 §3.1).
Inputs: Compiled Plan (slot assignments) + Arc Blueprint. Does NOT inspect prose.
Verifies: chapter BAND matches emotional_curve; reflection strategy matches; cost chapter exists; resolution_type.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from phoenix_v4.planning.arc_loader import ArcBlueprint


def validate_arc_alignment(
    plan: Union[dict, Any],
    arc: Union["ArcBlueprint", dict[str, Any]],
) -> list[str]:
    """
    Verify compiled plan aligns with arc. Returns list of errors; empty if valid.
    Does not score intensity, evaluate prose, detect tone, or simulate variance.
    """
    errors: list[str] = []

    if hasattr(plan, "dominant_band_sequence"):
        dominant_band_sequence = list(plan.dominant_band_sequence or [])
        chapter_slot_sequence = getattr(plan, "chapter_slot_sequence", [])
    else:
        plan_dict = plan if isinstance(plan, dict) else {}
        dominant_band_sequence = list(plan_dict.get("dominant_band_sequence") or [])
        chapter_slot_sequence = list(plan_dict.get("chapter_slot_sequence") or [])

    arc_dict = arc.raw if hasattr(arc, "raw") else arc
    arc_chapter_count = arc_dict.get("chapter_count") if isinstance(arc_dict, dict) else getattr(arc, "chapter_count", 0)
    emotional_curve = arc_dict.get("emotional_curve") if isinstance(arc_dict, dict) else getattr(arc, "emotional_curve", [])
    reflection_strategy_sequence = arc_dict.get("reflection_strategy_sequence") if isinstance(arc_dict, dict) else getattr(arc, "reflection_strategy_sequence", [])
    cost_chapter_index = arc_dict.get("cost_chapter_index") if isinstance(arc_dict, dict) else getattr(arc, "cost_chapter_index", None)
    resolution_type = arc_dict.get("resolution_type") if isinstance(arc_dict, dict) else getattr(arc, "resolution_type", None)

    chapter_count = len(chapter_slot_sequence) if chapter_slot_sequence else arc_chapter_count
    if not chapter_count:
        errors.append("Plan has no chapter_slot_sequence and arc chapter_count missing")
        return errors

    # Chapter BAND matches emotional_curve
    if len(emotional_curve) != chapter_count:
        errors.append(
            f"Arc emotional_curve length ({len(emotional_curve)}) does not match chapter count ({chapter_count})"
        )
    else:
        for i, (plan_band, arc_band) in enumerate(zip(dominant_band_sequence, emotional_curve)):
            if plan_band is not None and plan_band != arc_band:
                errors.append(
                    f"Chapter {i + 1}: plan dominant_band_sequence[{i}]={plan_band} does not match arc emotional_curve[{i}]={arc_band}"
                )

    if len(dominant_band_sequence) != chapter_count:
        errors.append(
            f"Plan dominant_band_sequence length ({len(dominant_band_sequence)}) does not match chapter count ({chapter_count})"
        )

    # Reflection strategy sequence: plan may carry it from arc at compile time; if present, must match
    plan_ref_seq = None
    if hasattr(plan, "reflection_strategy_sequence"):
        plan_ref_seq = getattr(plan, "reflection_strategy_sequence", None)
    elif isinstance(plan, dict):
        plan_ref_seq = plan.get("reflection_strategy_sequence")
    if plan_ref_seq is not None and reflection_strategy_sequence:
        if list(plan_ref_seq) != list(reflection_strategy_sequence):
            errors.append("Plan reflection_strategy_sequence does not match arc reflection_strategy_sequence")

    # Cost chapter index exists and in range
    if cost_chapter_index is not None:
        if not (1 <= cost_chapter_index <= chapter_count):
            errors.append(
                f"Arc cost_chapter_index {cost_chapter_index} must be in 1..{chapter_count}"
            )
    else:
        errors.append("Arc missing cost_chapter_index")

    # Resolution type present (engine compatibility is validate_engine_resolution)
    if not resolution_type:
        errors.append("Arc missing resolution_type")

    return errors
