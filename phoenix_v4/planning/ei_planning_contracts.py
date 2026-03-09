"""
EI v2 In Planning: canonical tuple key and schema validation.
Single source of truth for (brand_id, teacher_id, topic_id, persona_id, program_id, series_id, week).
Used by outcome/signals adapters, scoring joins, trust metrics, and reports.
Authority: specs/EI_V2_IN_PLANNING_SPEC.md §12.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Required keys for historical_outcomes rows (spec §12).
OUTCOME_IDENTITY_KEYS = (
    "brand_id",
    "teacher_id",
    "topic_id",
    "persona_id",
    "program_id",
    "series_id",
    "week",
)
OUTCOME_MEASURE_KEYS = (
    "sales",
    "read_through",
    "completion",
    "refund_rate",
    "flag_rate",
    "rejection_rate",
)


def planning_tuple_key(
    brand_id: str,
    teacher_id: str,
    topic_id: str,
    persona_id: str,
    program_id: str,
    series_id: str,
    week: str | int,
) -> Tuple[str, str, str, str, str, str, str]:
    """Canonical dedup/join key for planning tuples. week normalized to str."""
    return (
        str(brand_id or "").strip(),
        str(teacher_id or "").strip(),
        str(topic_id or "").strip(),
        str(persona_id or "").strip(),
        str(program_id or "").strip(),
        str(series_id or "").strip(),
        str(week) if week is not None else "",
    )


def planning_tuple_key_from_candidate(
    candidate: Any,
    week: str | int = "",
) -> Tuple[str, str, str, str, str, str, str]:
    """Build canonical key from a PlanningCandidate (or dict with same keys)."""
    if hasattr(candidate, "brand_id"):
        return planning_tuple_key(
            candidate.brand_id,
            candidate.teacher_id,
            candidate.topic_id,
            candidate.persona_id,
            candidate.program_id,
            getattr(candidate, "series_id", "") or "",
            week,
        )
    d = candidate if isinstance(candidate, dict) else {}
    return planning_tuple_key(
        d.get("brand_id", ""),
        d.get("teacher_id", ""),
        d.get("topic_id", ""),
        d.get("persona_id", ""),
        d.get("program_id", ""),
        d.get("series_id", ""),
        week,
    )


def planning_tuple_key_from_outcome_row(row: Dict[str, Any]) -> Tuple[str, str, str, str, str, str, str]:
    """Build canonical key from a historical_outcomes row (must have identity keys)."""
    return planning_tuple_key(
        row.get("brand_id", ""),
        row.get("teacher_id", ""),
        row.get("topic_id", ""),
        row.get("persona_id", ""),
        row.get("program_id", ""),
        row.get("series_id", ""),
        row.get("week", ""),
    )


def validate_historical_outcome_row(row: Any) -> Optional[Dict[str, Any]]:
    """
    Validate one historical_outcomes row. Returns validated dict (with identity + measure keys)
    or None if malformed. Does not mutate row.
    """
    if not isinstance(row, dict):
        return None
    for key in OUTCOME_IDENTITY_KEYS:
        if key not in row:
            return None
    out: Dict[str, Any] = {}
    for key in OUTCOME_IDENTITY_KEYS:
        out[key] = row.get(key)
    for key in OUTCOME_MEASURE_KEYS:
        val = row.get(key)
        if val is not None:
            try:
                out[key] = float(val)
            except (TypeError, ValueError):
                out[key] = None
        else:
            out[key] = None
    return out


def validate_content_quality_signal_row(
    row: Any,
    required_signal_fields: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Validate one content_quality_signals row. If required_signal_fields is set,
    row must contain those keys (values can be any). Returns validated dict or None.
    """
    if not isinstance(row, dict):
        return None
    required = required_signal_fields or []
    for key in required:
        if key not in row:
            return None
    return dict(row)
