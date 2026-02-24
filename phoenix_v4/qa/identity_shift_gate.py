"""
Gate 4: Identity Shift. Dev Spec §2.5.
Enforce monotonic identity progression. No regression; self_claim in final quarter.
"""
from __future__ import annotations

from typing import Any

from phoenix_v4.qa._narrative_plan_utils import get_story_atom_ids_by_chapter
from phoenix_v4.qa.validate_compiled_plan import ValidationResult

STAGE_ORD = {
    "pre_awareness": 0,
    "destabilization": 1,
    "experimentation": 2,
    "self_claim": 3,
}


def validate_identity_shift(
    plan: Any,
    atom_metadata: dict[str, dict[str, Any]],
) -> ValidationResult:
    """
    Returns ValidationResult(valid, errors, warnings).
    Identity stage progression must be monotonic. Final chapter should have at least one self_claim.
    No self_claim before midpoint; no experimentation before final quarter.
    """
    errors: list[str] = []
    warnings: list[str] = []
    by_ch = get_story_atom_ids_by_chapter(plan)
    n_ch = len(by_ch)
    if n_ch == 0:
        return ValidationResult(valid=True, errors=[], warnings=["No STORY chapters; identity shift gate skipped."])

    def stage_ord(aid: str) -> int:
        s = (atom_metadata.get(aid) or {}).get("identity_stage") or "pre_awareness"
        return STAGE_ORD.get(s, 0)

    max_stage_per_chapter = [
        max((stage_ord(aid) for aid in ch_atoms), default=0)
        for ch_atoms in by_ch
    ]

    # Monotonic: no regression
    for i in range(len(max_stage_per_chapter) - 1):
        if max_stage_per_chapter[i + 1] < max_stage_per_chapter[i]:
            errors.append(
                f"Identity shift: chapter {i + 2} has max stage {max_stage_per_chapter[i + 1]} "
                f"after chapter {i + 1} with {max_stage_per_chapter[i]} (regression)."
            )

    # Experimentation before final quarter
    final_quarter_start = 3 * n_ch // 4
    has_experimentation_before_final = any(
        max_stage_per_chapter[i] >= 2 for i in range(0, final_quarter_start)
    )
    if not has_experimentation_before_final and n_ch >= 4:
        errors.append("Identity shift: no experimentation stage before final quarter of book.")

    # Final chapter must have at least one self_claim (stage 3)
    if n_ch >= 1 and max_stage_per_chapter[-1] < 3:
        errors.append("Identity shift: final chapter must contain at least one self_claim atom.")

    # Self_claim before midpoint = too early
    mid = n_ch // 2
    for i in range(0, mid):
        if max_stage_per_chapter[i] >= 3:
            errors.append(
                f"Identity shift: self_claim appears in chapter {i + 1} (before midpoint); "
                "identity shift should occur in second half."
            )
            break

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
