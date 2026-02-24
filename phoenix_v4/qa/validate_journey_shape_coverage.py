"""
Structural Variation V4: journey shape and arc/format compatibility.
Wave-level diversity: minimum unique counts for key knobs.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_SOT = REPO_ROOT / "config" / "source_of_truth"


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_journey_shape_coverage(
    plan: Union[dict, Any],
    config_root: Optional[Path] = None,
) -> ValidationResult:
    """
    Checks journey_shape_id is in config and chapter_count is within shape's chapter_count_range.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if hasattr(plan, "get"):
        plan_dict = plan
    else:
        plan_dict = getattr(plan, "__dict__", {})

    journey_shape_id = plan_dict.get("journey_shape_id") or ""
    chapter_slot_sequence = plan_dict.get("chapter_slot_sequence") or []
    chapter_count = len(chapter_slot_sequence)
    if not journey_shape_id:
        return ValidationResult(valid=True, errors=[], warnings=warnings)

    config_root = config_root or CONFIG_SOT
    journey_cfg = _load_yaml(config_root / "journey_shapes.yaml")
    shapes = journey_cfg.get("shapes") or {}
    shape = shapes.get(journey_shape_id)
    if not shape:
        errors.append(f"journey_shape_id {journey_shape_id!r} not found in journey_shapes.yaml.")
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    rng = shape.get("chapter_count_range") or [0, 99]
    if len(rng) >= 2 and not (rng[0] <= chapter_count <= rng[1]):
        errors.append(
            f"journey_shape {journey_shape_id} chapter_count_range {rng} does not include plan chapter_count {chapter_count}."
        )

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_wave_knob_diversity(wave_plans: list[Union[dict, Any]]) -> ValidationResult:
    """
    Wave-level: fail if dominant share for (journey_shape_id, reframe_profile_id) exceeds threshold.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not wave_plans:
        return ValidationResult(valid=True, errors=[], warnings=[])

    pairs: list[str] = []
    for p in wave_plans:
        d = p if isinstance(p, dict) else getattr(p, "__dict__", {})
        j = d.get("journey_shape_id") or ""
        r = d.get("reframe_profile_id") or ""
        pairs.append(f"{j}|{r}")

    from collections import Counter
    counts = Counter(pairs)
    total = len(pairs)
    threshold = 0.5
    for pair, count in counts.most_common(1):
        if total > 0 and count / total > threshold:
            errors.append(
                f"Wave diversity: (journey_shape_id, reframe_profile_id) pair {pair!r} "
                f"appears in {count}/{total} plans ({100*count/total:.0f}%); max share {100*threshold:.0f}%."
            )
    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
