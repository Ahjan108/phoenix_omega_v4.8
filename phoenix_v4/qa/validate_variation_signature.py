"""
Structural Variation V4: verify variation_signature presence and deterministic recomputation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


def validate_variation_signature(plan: Union[dict, Any]) -> ValidationResult:
    """
    Verifies plan has variation_signature and that it matches recomputation from knobs.
    Backward compat: if plan lacks variation fields, recompute with defaults and warn.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if hasattr(plan, "get"):
        plan_dict = plan
    else:
        plan_dict = getattr(plan, "__dict__", {}) or {}

    stored = plan_dict.get("variation_signature") or ""
    if not stored:
        errors.append("Plan missing variation_signature (required for V4 variation system).")
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    try:
        from phoenix_v4.planning.schema_v4 import get_plan_variation_signature
        recomputed = get_plan_variation_signature(plan_dict)
        if recomputed != stored:
            errors.append(
                f"variation_signature mismatch: stored {stored!r} vs recomputed {recomputed!r}. "
                "Plan may have been edited or schema changed."
            )
    except Exception as e:
        errors.append(f"Failed to recompute variation_signature: {e}")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
