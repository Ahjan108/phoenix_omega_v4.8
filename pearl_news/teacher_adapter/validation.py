"""
Pearl News teacher adapter payload validation (adapter spec §6).

Adapter-level checks: framework term, diagnosis, practice, quote language, bridge, safety.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from pearl_news.teacher_adapter.adapter import NewsTeacherPayload


@dataclass
class AdapterValidationResult:
    """Result of validate_adapter_payload."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_adapter_payload(payload: NewsTeacherPayload | None) -> AdapterValidationResult:
    """
    Run adapter-level validation (spec §6).

    Required checks:
    - framework term is explicit
    - diagnosis is non-generic
    - practice is concrete
    - quote language has lift
    - bridge is useful and not vague
    - safety boundary is respected
    """
    errors: list[str] = []
    warnings: list[str] = []

    if payload is None:
        return AdapterValidationResult(valid=False, errors=["Payload is None."])

    # Framework term explicit
    ft = (payload.teacher_framework_term or "").strip()
    if len(ft) < 5:
        errors.append("teacher_framework_term must be explicit (min 5 chars).")
    elif _is_generic(ft):
        warnings.append("teacher_framework_term may be too generic.")

    # Diagnosis non-generic
    dc = (payload.teacher_diagnostic_claim or "").strip()
    if len(dc) < 15:
        errors.append("teacher_diagnostic_claim must be non-generic (min 15 chars).")
    elif _is_generic(dc):
        warnings.append("teacher_diagnostic_claim may sound generic.")

    # Practice concrete
    np = (payload.teacher_named_practice or "").strip()
    if len(np) < 2:
        errors.append("teacher_named_practice must be concrete.")
    if np and np.lower() in ("reflection", "mindfulness", "meditation") and len(np.split()) < 3:
        warnings.append("teacher_named_practice could be more specific.")

    # Quote language has lift
    quotes = payload.teacher_quotes or []
    if not quotes:
        warnings.append("teacher_quotes empty; commentary may lack rhetorical lift.")
    else:
        short = sum(1 for q in quotes if len((q or "").strip()) < 20)
        if short == len(quotes):
            warnings.append("All teacher_quotes very short; consider longer phrases for lift.")

    # Bridge useful and not vague
    bb = (payload.teacher_behavior_bridge or "").strip()
    if len(bb) < 10:
        errors.append("teacher_behavior_bridge must be useful (min 10 chars).")
    if bb and _is_vague(bb):
        warnings.append("teacher_behavior_bridge may be too vague.")
    cb = (payload.teacher_civic_bridge or "").strip()
    if len(cb) < 8:
        errors.append("teacher_civic_bridge must be present (min 8 chars).")

    # Safety boundary respected (content check is editorial; we only require presence)
    sb = (payload.teacher_safety_boundary or "").strip()
    if len(sb) < 10:
        errors.append("teacher_safety_boundary must be explicit.")

    return AdapterValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def _is_generic(text: str) -> bool:
    generic_phrases = (
        "mindfulness", "reflection", "inner peace", "finding balance",
        "being present", "self-care", "well-being", "resilience",
    )
    t = text.lower()
    return any(p in t for p in generic_phrases) and len(t.split()) < 12


def _is_vague(text: str) -> bool:
    vague = ("consider", "could", "might", "perhaps", "something", "one can", "readers can try")
    t = text.lower()
    return any(v in t for v in vague) and len(t.split()) < 15
