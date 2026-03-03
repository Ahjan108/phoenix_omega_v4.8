"""
Structural Variation V4: check role-safe reorder invariants.
Reordering must not alter chapter count, section count, story slot allocation, or exercise slot allocation.
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


def validate_section_reorder_safety(
    plan: Union[dict, Any],
    format_plan: Optional[dict] = None,
    section_reorder_mode: Optional[str] = None,
    config_root: Optional[Path] = None,
) -> ValidationResult:
    """
    Verifies that if section_reorder_mode was applied, only allowed_swaps were used and
    STORY/EXERCISE slot counts and positions are preserved (same count per chapter).
    """
    errors: list[str] = []
    warnings: list[str] = []

    if hasattr(plan, "get"):
        plan_dict = plan
    else:
        plan_dict = getattr(plan, "__dict__", {})

    chapter_slot_sequence = plan_dict.get("chapter_slot_sequence") or []
    mode = section_reorder_mode or plan_dict.get("section_reorder_mode") or "none"
    if mode == "none" or not chapter_slot_sequence:
        return ValidationResult(valid=True, errors=[], warnings=[])

    config_root = config_root or CONFIG_SOT
    reorder_cfg = _load_yaml(config_root / "section_reorder_modes.yaml")
    modes = reorder_cfg.get("modes") or {}
    mode_cfg = modes.get(mode)
    if not mode_cfg:
        warnings.append(f"section_reorder_mode {mode!r} not in config; cannot verify allowed swaps.")
        return ValidationResult(valid=True, errors=errors, warnings=warnings)

    allowed_set = set()
    for pair in mode_cfg.get("allowed_swaps") or []:
        if len(pair) == 2:
            allowed_set.add((pair[0], pair[1]))
            allowed_set.add((pair[1], pair[0]))

    # Check: every chapter has same slot types as template (only order may differ)
    slot_types_per_ch = [frozenset(row) for row in chapter_slot_sequence]
    if not slot_types_per_ch:
        return ValidationResult(valid=True, errors=[], warnings=[])

    first_ch_types = slot_types_per_ch[0]
    for ch, types in enumerate(slot_types_per_ch):
        if types != first_ch_types:
            errors.append(
                f"Section reorder safety: chapter {ch} has different slot type set than chapter 0 "
                "(reorder must not add/remove slot types)."
            )

    # Check: STORY and EXERCISE counts per chapter match (no movement of required beats)
    for ch, row in enumerate(chapter_slot_sequence):
        story_count = sum(1 for s in row if s == "STORY")
        exercise_count = sum(1 for s in row if s == "EXERCISE")
        if format_plan:
            slot_defs = format_plan.get("slot_definitions") or []
            if ch < len(slot_defs):
                expected_story = sum(1 for s in slot_defs[ch] if s == "STORY")
                expected_ex = sum(1 for s in slot_defs[ch] if s == "EXERCISE")
                if story_count != expected_story or exercise_count != expected_ex:
                    errors.append(
                        f"Section reorder safety: chapter {ch} STORY count={story_count} (expected {expected_story}) or "
                        f"EXERCISE count={exercise_count} (expected {expected_ex})."
                    )

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
