"""
Gate 2: Cost Gradient. Dev Spec §2.3.
Enforce escalating emotional cost. Narratives need increasing stakes, not flat tension.
"""
from __future__ import annotations

from typing import Any

from phoenix_v4.qa._narrative_plan_utils import (
    get_chapter_slot_sequence,
    iter_chapter_slot_atom_ids,
)
from phoenix_v4.qa.validate_compiled_plan import ValidationResult


def _avg_cost_per_chapter(
    plan: Any,
    atom_metadata: dict[str, dict[str, Any]],
    slot_types: set[str],
) -> list[float]:
    """Average cost_intensity per chapter from atoms in given slot types (e.g. STORY, SCENE)."""
    css = get_chapter_slot_sequence(plan)
    n_ch = len(css)
    sums: list[list[int]] = [[] for _ in range(n_ch)]
    for ch, _si, slot_type, aid in iter_chapter_slot_atom_ids(plan):
        if ch >= n_ch or (slot_type or "").upper() not in slot_types:
            continue
        if "placeholder:" in aid or "silence:" in aid:
            continue
        ci = (atom_metadata.get(aid) or {}).get("cost_intensity", 2)
        try:
            ci = int(ci)
        except (TypeError, ValueError):
            ci = 2
        if 1 <= ci <= 5 and ch < len(sums):
            sums[ch].append(ci)
    return [
        sum(v) / len(v) if v else 2.0
        for v in sums
    ]


def validate_cost_gradient(
    plan: Any,
    atom_metadata: dict[str, dict[str, Any]],
) -> ValidationResult:
    """
    Returns ValidationResult(valid, errors, warnings).
    STORY + SCENE atoms contribute to avg cost per chapter.
    Fail: highest cost before midpoint, no high-intensity (>=4) before identity shift, cost drops to 1 in final third,
    average cost across book < 2.5.
    """
    errors: list[str] = []
    warnings: list[str] = []
    avg_cost = _avg_cost_per_chapter(plan, atom_metadata, {"STORY", "SCENE"})
    n_ch = len(avg_cost)
    if n_ch == 0:
        return ValidationResult(valid=True, errors=[], warnings=["No chapters; cost gradient gate skipped."])

    mid = n_ch // 2
    peak_idx = max(range(n_ch), key=lambda i: avg_cost[i], default=0)
    if peak_idx < mid and n_ch >= 3:
        errors.append(
            f"Cost gradient: highest cost occurs at chapter {peak_idx + 1} (before midpoint {mid + 1}). "
            "Peak should be at or after midpoint."
        )

    # No high-intensity (>=4) before identity shift chapter
    # We don't have identity_stage per chapter here; use "second half" as proxy: at least one ch with avg >= 4 in second half
    second_half = range(mid, n_ch)
    has_high_second_half = any(avg_cost[i] >= 4 for i in second_half)
    if not has_high_second_half and n_ch >= 4:
        errors.append("Cost gradient: no chapter with average cost_intensity >= 4 in second half of book.")

    # Cost drops to 1 in final third
    final_third_start = 2 * n_ch // 3
    for i in range(final_third_start, n_ch):
        if i < len(avg_cost) and avg_cost[i] < 2:
            errors.append(
                f"Cost gradient: chapter {i + 1} has average cost {avg_cost[i]:.1f}; "
                "final third should not drop below 2 (resolution without erasing cost history)."
            )

    book_avg = sum(avg_cost) / len(avg_cost) if avg_cost else 0
    if book_avg < 2.5 and n_ch >= 3:
        errors.append(f"Cost gradient: average cost across book is {book_avg:.1f}; minimum 2.5 required.")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
