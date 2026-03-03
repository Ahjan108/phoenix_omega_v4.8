"""
Engine–arc compatibility check (Arc-First Canonical Spec v1.1).
Structural only: resolution_type, peak intensity, identity_shift. No prose inspection.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from phoenix_v4.planning.arc_loader import ArcBlueprint
    from phoenix_v4.planning.engine_loader import EngineDefinition


def validate_engine_resolution(
    arc: "ArcBlueprint",
    engine: "EngineDefinition",
) -> list[str]:
    """
    Verify arc complies with engine. Returns list of errors; empty if valid.
    Checks: resolution_type in allowed; arc peak <= engine.peak_intensity_limit;
    identity_shift only if engine.identity_shift_allowed.
    """
    errors: list[str] = []

    if arc.resolution_type not in engine.allowed_resolution_types:
        errors.append(
            f"Arc resolution_type {arc.resolution_type!r} not in engine {engine.engine_id} "
            f"allowed_resolution_types {engine.allowed_resolution_types}"
        )

    if arc.resolution_type == "identity_shift" and not engine.identity_shift_allowed:
        errors.append(
            f"Arc has resolution_type identity_shift but engine {engine.engine_id} has identity_shift_allowed=false"
        )

    arc_peak = max(arc.emotional_curve) if arc.emotional_curve else 0
    if arc_peak > engine.peak_intensity_limit:
        errors.append(
            f"Arc emotional_curve peak {arc_peak} exceeds engine {engine.engine_id} peak_intensity_limit {engine.peak_intensity_limit}"
        )

    return errors
