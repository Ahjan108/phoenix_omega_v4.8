"""
Gate 3: Callback Integrity. Dev Spec §2.4.
Enforce symbolic continuity. Setups must return; threads must close.
"""
from __future__ import annotations

from typing import Any

from phoenix_v4.qa._narrative_plan_utils import get_all_plan_atom_ids_for_metadata
from phoenix_v4.qa.validate_compiled_plan import ValidationResult


def validate_callback_integrity(
    plan: Any,
    atom_metadata: dict[str, dict[str, Any]],
) -> ValidationResult:
    """
    Returns ValidationResult(valid, errors, warnings).
    Every callback_id with phase=setup must have a corresponding phase=return later.
    Every phase=return must have a prior phase=setup. Max 2 unclosed threads at book end.
    """
    errors: list[str] = []
    warnings: list[str] = []
    atom_ids = get_all_plan_atom_ids_for_metadata(plan)
    # Build ordered list of (index, atom_id, callback_id, callback_phase)
    callbacks: list[tuple[int, str, str | None, str | None]] = []
    for idx, aid in enumerate(atom_ids):
        meta = atom_metadata.get(aid) or {}
        cid = meta.get("callback_id")
        phase = meta.get("callback_phase")
        if cid or phase:
            callbacks.append((idx, aid, cid, phase))

    setups: dict[str, int] = {}  # callback_id -> first index where setup appears
    returns: dict[str, list[int]] = {}  # callback_id -> list of indices where return appears
    for idx, _aid, cid, phase in callbacks:
        if not cid:
            continue
        if phase == "setup":
            if cid not in setups:
                setups[cid] = idx
        elif phase == "return":
            returns.setdefault(cid, []).append(idx)

    # Return without setup
    for cid, indices in returns.items():
        if cid not in setups:
            errors.append(f"Callback '{cid}': phase=return appears but no prior phase=setup (ungrounded payoff).")

    # Setup without return (orphaned)
    unclosed = []
    for cid in setups:
        if cid not in returns or not returns[cid]:
            unclosed.append(cid)
    if len(unclosed) > 2:
        errors.append(
            f"Callback integrity: {len(unclosed)} unclosed threads at end of book (max 2 allowed): {unclosed[:5]}{'...' if len(unclosed) > 5 else ''}."
        )
    for cid in unclosed[:3]:
        errors.append(f"Callback '{cid}': phase=setup has no matching phase=return (orphaned thread).")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
