"""
Gate 1: Mechanism Escalation. Dev Spec §2.2.
Enforce that mechanism_depth increases across the arc. Books must not feel flat in insight.
"""
from __future__ import annotations

from typing import Any

from phoenix_v4.qa._narrative_plan_utils import get_story_atom_ids_by_chapter
from phoenix_v4.qa.validate_compiled_plan import ValidationResult


def validate_mechanism_escalation(
    plan: Any,
    atom_metadata: dict[str, dict[str, Any]],
) -> ValidationResult:
    """
    Returns ValidationResult(valid, errors, warnings).
    Phase rules: Early (1 to N//3) >= 1; Mid (N//3+1 to 2*N//3) >= 2; Late (2*N//3+1 to N) >= 3,
    with at least one depth=4 in final third. No plateau after midpoint, no decrease in late-stage.
    """
    errors: list[str] = []
    warnings: list[str] = []
    by_ch = get_story_atom_ids_by_chapter(plan)
    n_ch = len(by_ch)
    if n_ch == 0:
        return ValidationResult(valid=True, errors=[], warnings=["No STORY chapters; mechanism gate skipped."])

    def depth(aid: str) -> int:
        return int((atom_metadata.get(aid) or {}).get("mechanism_depth", 1))

    max_depth_per_chapter = [
        max((depth(aid) for aid in ch_atoms), default=1)
        for ch_atoms in by_ch
    ]
    early_end = max(1, n_ch // 3)
    mid_end = max(early_end + 1, 2 * n_ch // 3)
    late_start = mid_end

    # Early: >= 1
    for i in range(0, early_end):
        if i < len(max_depth_per_chapter) and max_depth_per_chapter[i] < 1:
            errors.append(f"Chapter {i + 1} (early): max mechanism_depth must be >= 1, got {max_depth_per_chapter[i]}.")

    # Mid: >= 2
    for i in range(early_end, mid_end):
        if i < len(max_depth_per_chapter) and max_depth_per_chapter[i] < 2:
            errors.append(f"Chapter {i + 1} (mid): max mechanism_depth must be >= 2 (behavioral), got {max_depth_per_chapter[i]}.")

    # Late: >= 3 and at least one depth=4 in final third
    final_third_start = 2 * n_ch // 3
    has_identity_in_final_third = any(
        i < len(max_depth_per_chapter) and max_depth_per_chapter[i] >= 4
        for i in range(final_third_start, n_ch)
    )
    if not has_identity_in_final_third and final_third_start < n_ch:
        errors.append("Final third of book must contain at least one mechanism_depth=4 (identity-level) atom.")

    for i in range(late_start, n_ch):
        if i < len(max_depth_per_chapter) and max_depth_per_chapter[i] < 3:
            errors.append(f"Chapter {i + 1} (late): max mechanism_depth must be >= 3 (nervous_system), got {max_depth_per_chapter[i]}.")

    # Depth plateaus (no increase) after midpoint
    for i in range(mid_end, n_ch - 1):
        if i + 1 >= len(max_depth_per_chapter):
            break
        if max_depth_per_chapter[i + 1] <= max_depth_per_chapter[i] and max_depth_per_chapter[i] < 4:
            warnings.append(f"Chapter {i + 2}: mechanism_depth does not increase from chapter {i + 1} (plateau).")

    # Depth decreases in late-stage
    for i in range(late_start, n_ch - 1):
        if i + 1 >= len(max_depth_per_chapter):
            break
        if max_depth_per_chapter[i + 1] < max_depth_per_chapter[i]:
            errors.append(
                f"Chapter {i + 2}: mechanism_depth decreased from {max_depth_per_chapter[i]} to {max_depth_per_chapter[i + 1]} (late-stage regression)."
            )

    # Max depth across entire book < 3
    global_max = max(max_depth_per_chapter, default=0)
    if global_max < 3 and n_ch >= 3:
        errors.append(f"Max mechanism_depth across book is {global_max}; minimum 3 required for books with 3+ chapters.")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
