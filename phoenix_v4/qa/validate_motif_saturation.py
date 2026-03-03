"""
Structural Variation V4: enforce motif injection ceilings and spacing.
Max 2 per chapter, max 12 per book, min word distance 250 (we use slot distance as proxy).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


MIN_SLOT_DISTANCE = 2  # proxy for ~250 words between motif injections
MAX_MOTIF_PER_CHAPTER = 2
MAX_MOTIF_PER_BOOK = 12


def validate_motif_saturation(plan: Union[dict, Any]) -> ValidationResult:
    """
    If plan has motif_injections, fail when over saturation (per chapter or per book or too close).
    """
    errors: list[str] = []
    warnings: list[str] = []

    if hasattr(plan, "get"):
        plan_dict = plan
    else:
        plan_dict = getattr(plan, "__dict__", {})

    injections = plan_dict.get("motif_injections") or []
    if not injections:
        return ValidationResult(valid=True, errors=[], warnings=[])

    by_chapter: dict[int, int] = {}
    for inj in injections:
        ch = inj.get("chapter_index", 0)
        by_chapter[ch] = by_chapter.get(ch, 0) + 1
    for ch, count in by_chapter.items():
        if count > MAX_MOTIF_PER_CHAPTER:
            errors.append(f"Motif saturation: chapter {ch} has {count} motif injections (max {MAX_MOTIF_PER_CHAPTER}).")

    if len(injections) > MAX_MOTIF_PER_BOOK:
        errors.append(f"Motif saturation: {len(injections)} motif injections (max {MAX_MOTIF_PER_BOOK} per book).")

    # Slot distance: flatten (chapter, slot) to a linear index and check gap
    chapter_slot_sequence = plan_dict.get("chapter_slot_sequence") or []
    slot_count_per_ch = [len(row) for row in chapter_slot_sequence]
    for i in range(1, len(injections)):
        prev = injections[i - 1]
        curr = injections[i]
        prev_linear = sum(slot_count_per_ch[: prev.get("chapter_index", 0)]) + prev.get("slot_index", 0)
        curr_linear = sum(slot_count_per_ch[: curr.get("chapter_index", 0)]) + curr.get("slot_index", 0)
        if curr_linear - prev_linear < MIN_SLOT_DISTANCE:
            errors.append(
                f"Motif spacing: injections at ({prev.get('chapter_index')},{prev.get('slot_index')}) and "
                f"({curr.get('chapter_index')},{curr.get('slot_index')}) are too close (min slot distance {MIN_SLOT_DISTANCE})."
            )

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
