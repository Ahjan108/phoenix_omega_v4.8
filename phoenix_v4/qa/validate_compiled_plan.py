"""
Part 3.1 / 3.3 compiled plan validator: no duplicate atom IDs, emotional curve, slot structure.
Validates against format_plan.slot_definitions (order and length). When chapter_count < 6, emits explicit skip message.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


def _validate_emotional_curve(
    dominant_band_sequence: list[int | None],
    chapter_count: int,
) -> tuple[list[str], list[str]]:
    """Returns (errors, diagnostics). When chapter_count < 6, add diagnostic 'Skipped: too few chapters'."""
    errors: list[str] = []
    diagnostics: list[str] = []
    if chapter_count < 6:
        diagnostics.append("Skipped: too few chapters for curve check (need >= 6).")
        return errors, diagnostics

    bands_in_sequence = [b for b in dominant_band_sequence if b is not None]
    distinct_bands = set(bands_in_sequence)
    if len(distinct_bands) < 3:
        errors.append(
            f"Emotional curve invalid: only {len(distinct_bands)} distinct BAND values found "
            f"(minimum 3 required for books >= 6 chapters)."
        )
    max_run = 1
    current_run = 1
    for i in range(1, len(dominant_band_sequence)):
        curr = dominant_band_sequence[i]
        prev = dominant_band_sequence[i - 1]
        if curr is not None and prev is not None and curr == prev:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    if max_run > 3:
        errors.append(
            f"Emotional curve invalid: {max_run} consecutive chapters with same BAND detected (maximum allowed is 3)."
        )
    return errors, diagnostics


def validate_compiled_plan(
    plan: Union[dict, Any],
    format_plan: dict | None = None,
    angle_context: Optional[dict] = None,
    integration_atom_metadata: Optional[dict] = None,
    enforce_integration_reinforcement: bool = False,
) -> ValidationResult:
    """
    Validate compiled plan: no duplicate atom IDs (excluding placeholders and silence slots), emotional curve (if >= 6 chapters),
    and full slot sequence parity with format_plan.slot_definitions.
    Angle Integration (V4.7): if angle_context has integration_reinforcement_type, final chapter must include an INTEGRATION
    atom with reinforcement_type == that value (when integration_atom_metadata provided). Otherwise WARN; set
    enforce_integration_reinforcement=True to FAIL.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if hasattr(plan, "atom_ids"):
        atom_ids = list(plan.atom_ids)
        chapter_slot_sequence = list(plan.chapter_slot_sequence)
        dominant_band_sequence = list(plan.dominant_band_sequence or [])
    else:
        atom_ids = list((plan or {}).get("atom_ids") or [])
        chapter_slot_sequence = list((plan or {}).get("chapter_slot_sequence") or [])
        dominant_band_sequence = list((plan or {}).get("dominant_band_sequence") or [])

    slot_definitions = (format_plan or {}).get("slot_definitions") or chapter_slot_sequence
    chapter_count = len(slot_definitions)

    # Structure: total atom_ids length = sum of slot counts per chapter
    total_slots = sum(len(row) for row in slot_definitions)
    if len(atom_ids) != total_slots:
        errors.append(
            f"Plan structure invalid: atom_ids length ({len(atom_ids)}) does not match total slot count ({total_slots})."
        )

    # Structure: each chapter's slot types must match slot_definitions[chapter_idx] in order
    idx = 0
    for ch, row in enumerate(slot_definitions):
        for si, expected_type in enumerate(row):
            if idx >= len(atom_ids):
                break
            aid = atom_ids[idx]
            if "placeholder:" in aid or "silence:" in aid:
                got_type = aid.split(":")[1] if ":" in aid else ""
                if got_type != expected_type:
                    kind = "silence" if "silence:" in aid else "placeholder"
                    errors.append(f"Chapter {ch} slot {si}: expected slot type {expected_type}, got {kind} {got_type}.")
            idx += 1

    # No duplicate atom IDs (excluding placeholders and silence slots)
    non_placeholder = [a for a in atom_ids if "placeholder:" not in a and "silence:" not in a]
    seen: set[str] = set()
    for a in non_placeholder:
        if a in seen:
            errors.append(f"Duplicate atom ID in plan: {a}.")
        seen.add(a)

    # Emotional curve
    curve_errors, curve_diag = _validate_emotional_curve(dominant_band_sequence, chapter_count)
    errors.extend(curve_errors)
    warnings.extend(curve_diag)

    # Placeholder / silence warning
    if non_placeholder and len(non_placeholder) < len(atom_ids):
        warnings.append("Plan contains placeholders or silence slots; 100% pipeline may require full resolution.")

    # Angle Integration (V4.7): integration reinforcement — final chapter INTEGRATION atom must match reinforcement_type
    required_reinforcement = (angle_context or {}).get("integration_reinforcement_type")
    if required_reinforcement and chapter_count >= 1:
        last_row = slot_definitions[chapter_count - 1]
        idx = sum(len(row) for row in slot_definitions[: chapter_count - 1])
        final_integration_aids: list[str] = []
        for st in last_row:
            if (st or "").upper() == "INTEGRATION" and idx < len(atom_ids):
                aid = atom_ids[idx]
                if "placeholder:" not in aid and "silence:" not in aid:
                    final_integration_aids.append(aid)
            idx += 1
        if final_integration_aids and integration_atom_metadata:
            has_match = any(
                (integration_atom_metadata.get(aid) or {}).get("reinforcement_type") == required_reinforcement
                for aid in final_integration_aids
            )
            if not has_match and enforce_integration_reinforcement:
                errors.append(
                    f"Angle requires integration_reinforcement_type={required_reinforcement!r}; "
                    "add at least one INTEGRATION atom tagged reinforcement_type for persona/topic pool."
                )
            elif not has_match:
                warnings.append(
                    f"Angle integration_reinforcement_type={required_reinforcement!r}: no INTEGRATION atom in final chapter has matching reinforcement_type; consider tagging."
                )
        elif required_reinforcement and not integration_atom_metadata:
            warnings.append(
                f"Angle integration_reinforcement_type={required_reinforcement!r} required but INTEGRATION atom metadata not loaded; consider tagging INTEGRATION atoms with reinforcement_type."
            )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
