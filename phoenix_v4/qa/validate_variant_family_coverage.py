"""
Structural Variation V4: F1–F5 variant family coverage for HOOK, SCENE, REFLECTION, INTEGRATION.
If section type is coverage-required, at least one atom from each family F1..F5 must be present (when atoms have metadata).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union

REQUIRED_FAMILIES = {"F1", "F2", "F3", "F4", "F5"}
COVERAGE_REQUIRED_SLOT_TYPES = {"HOOK", "SCENE", "REFLECTION", "INTEGRATION"}


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


def validate_variant_family_coverage(
    plan: Union[dict, Any],
    atom_metadata_by_id: Optional[dict[str, dict[str, Any]]] = None,
) -> ValidationResult:
    """
    When atom_metadata_by_id is provided, for each coverage-required slot type (HOOK, SCENE, REFLECTION, INTEGRATION),
    check that the atoms used for that slot type include at least one from each variant family F1–F5.
    atom_metadata_by_id: dict atom_id -> { variant_family: "F1" | "F2" | ... }.
    If atom_metadata_by_id is None or empty, skip (no error).
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not atom_metadata_by_id:
        return ValidationResult(valid=True, errors=[], warnings=[])

    if hasattr(plan, "get"):
        plan_dict = plan
    else:
        plan_dict = getattr(plan, "__dict__", {})

    atom_ids = plan_dict.get("atom_ids") or []
    chapter_slot_sequence = plan_dict.get("chapter_slot_sequence") or []
    if not atom_ids or not chapter_slot_sequence:
        return ValidationResult(valid=True, errors=[], warnings=[])

    # Build flat list of (slot_type, atom_id) in order
    flat: list[tuple[str, str]] = []
    idx = 0
    for ch_slots in chapter_slot_sequence:
        for slot_type in ch_slots:
            if idx < len(atom_ids):
                aid = atom_ids[idx]
                if not (aid or "").startswith("placeholder:") and not (aid or "").startswith("silence:"):
                    flat.append((slot_type, aid))
                idx += 1
        if idx >= len(atom_ids):
            break

    # Per slot type, collect atom_ids and their variant_family
    by_slot: dict[str, set[str]] = {st: set() for st in COVERAGE_REQUIRED_SLOT_TYPES}
    for slot_type, aid in flat:
        if slot_type not in COVERAGE_REQUIRED_SLOT_TYPES:
            continue
        meta = atom_metadata_by_id.get(aid) or {}
        fam = meta.get("variant_family") or meta.get("variant_family_id")
        if fam:
            by_slot[slot_type].add(str(fam).upper())

    for slot_type in COVERAGE_REQUIRED_SLOT_TYPES:
        found = by_slot[slot_type]
        missing = REQUIRED_FAMILIES - found
        if not found:
            continue
        if missing:
            errors.append(
                f"Variant family coverage: slot type {slot_type} is missing families {sorted(missing)}. "
                f"Required: F1–F5; found: {sorted(found) or 'none'}."
            )

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
