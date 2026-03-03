"""
Gate 5: Macro-Cadence Wave. Dev Spec §2.6.
Enforce emotional rhythm at chapter level. No 3 consecutive intensity=5; regulation after high intensity.
"""
from __future__ import annotations

from typing import Any

from phoenix_v4.qa._narrative_plan_utils import (
    get_chapter_count,
    get_emotional_curve,
    get_exercise_chapters,
)
from phoenix_v4.qa.validate_compiled_plan import ValidationResult


def _regulation_support_per_chapter(plan: Any) -> list[str]:
    """
    Per spec: chapter has EXERCISE slot -> medium; downregulation/grounding/breath type -> high; else low.
    We don't have exercise type per chapter here; use exercise_chapters presence as medium, and assume high if we had type.
    Simplified: chapter in exercise_chapters -> medium (spec says high for downregulation/grounding/breath).
    """
    n_ch = get_chapter_count(plan)
    ex_chapters = set(get_exercise_chapters(plan))
    return [
        "medium" if ch in ex_chapters else "low"
        for ch in range(n_ch)
    ]


def _regulation_ord(s: str) -> int:
    return {"low": 0, "medium": 1, "high": 2}.get(s, 0)


def validate_macro_cadence(
    plan: Any,
    arc: dict | Any = None,
) -> ValidationResult:
    """
    Returns ValidationResult(valid, errors, warnings).
    Rules: no 3 consecutive intensity=5; every intensity 4/5 within 2 ch of regulation >= medium;
    at least one regulation_support=high in second half (we use medium as proxy); no monotonic intensity increase with zero dip.
    """
    errors: list[str] = []
    warnings: list[str] = []
    n_ch = get_chapter_count(plan)
    if n_ch == 0:
        return ValidationResult(valid=True, errors=[], warnings=["No chapters; macro-cadence gate skipped."])

    intensity = get_emotional_curve(plan, arc)
    if len(intensity) < n_ch:
        intensity = intensity + [2] * (n_ch - len(intensity))
    regulation = _regulation_support_per_chapter(plan)

    # No 3 consecutive intensity=5
    for i in range(n_ch - 2):
        if intensity[i] >= 5 and intensity[i + 1] >= 5 and intensity[i + 2] >= 5:
            errors.append(
                f"Macro-cadence: chapters {i + 1}-{i + 3} are all intensity 5 (burnout risk). "
                "No more than 2 consecutive high-intensity chapters."
            )

    # Every intensity 4 or 5 followed within 2 chapters by regulation >= medium
    for i in range(n_ch):
        if intensity[i] < 4:
            continue
        found = False
        for j in range(i + 1, min(i + 3, n_ch)):
            if _regulation_ord(regulation[j]) >= 1:
                found = True
                break
        if not found:
            errors.append(
                f"Macro-cadence: chapter {i + 1} has intensity {intensity[i]}; "
                "must be followed within 2 chapters by at least medium regulation."
            )

    # At least one regulation_support high (or medium) in second half
    second_half = range(n_ch // 2, n_ch)
    if not any(_regulation_ord(regulation[i]) >= 1 for i in second_half):
        errors.append("Macro-cadence: second half of book must have at least one chapter with regulation_support >= medium.")

    # Monotonic intensity increase with zero dip after midpoint
    mid = n_ch // 2
    after_mid = intensity[mid:]
    dips = sum(1 for j in range(1, len(after_mid)) if after_mid[j] < after_mid[j - 1])
    if dips == 0 and len(after_mid) >= 2 and max(intensity) >= 4:
        warnings.append("Macro-cadence: intensity does not dip after midpoint; consider at least one relief chapter.")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
