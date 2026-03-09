"""
EI v2 In Planning: load content_quality_signals from file with strict schema validation.
Reject malformed rows; log counts of dropped rows. Optional: aggregate from section_scores.jsonl.
Canonical join: use identity keys (brand_id, teacher_id, topic_id, persona_id, program_id, series_id) when present.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from phoenix_v4.planning.ei_planning_contracts import validate_content_quality_signal_row


def load_content_quality_signals_from_file(
    path: Path,
    required_signal_fields: Optional[List[str]] = None,
) -> Tuple[List[Dict[str, Any]], int, int, List[str]]:
    """
    Load content_quality_signals from JSON or JSONL. Validate each row (required_signal_fields if set).
    Returns: (accepted_rows, loaded_count, dropped_count, validation_errors).
    """
    accepted: List[Dict[str, Any]] = []
    dropped = 0
    errors: List[str] = []

    if not path.exists():
        return accepted, 0, 0, [f"File not found: {path}"]

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return accepted, 0, 0, []

    rows: List[Dict[str, Any]] = []
    if raw.startswith("["):
        try:
            rows = json.loads(raw)
            if not isinstance(rows, list):
                return accepted, 0, 0, [f"Expected JSON array, got {type(rows).__name__}"]
        except json.JSONDecodeError as e:
            return accepted, 0, 0, [f"JSON decode error: {e}"]
    else:
        for i, line in enumerate(raw.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
                else:
                    dropped += 1
                    errors.append(f"Line {i}: not a dict")
            except json.JSONDecodeError as e:
                dropped += 1
                errors.append(f"Line {i}: {e}")

    required = required_signal_fields or []
    for i, row in enumerate(rows):
        validated = validate_content_quality_signal_row(row, required_signal_fields=required)
        if validated is not None:
            accepted.append(validated)
        else:
            dropped += 1
            errors.append(f"Row {i + 1}: missing required fields {required!r} or invalid")

    return accepted, len(accepted), dropped, errors


def signals_by_tuple_key(
    rows: List[Dict[str, Any]],
    week: str | int = "",
) -> Dict[Tuple[str, str, str, str, str, str, str], Dict[str, Any]]:
    """
    Index signal rows by canonical planning tuple key when identity keys are present.
    Rows without all identity keys are skipped (not indexed).
    """
    from phoenix_v4.planning.ei_planning_contracts import (
        OUTCOME_IDENTITY_KEYS,
        planning_tuple_key,
    )

    by_key: Dict[Tuple[str, str, str, str, str, str, str], Dict[str, Any]] = {}
    for row in rows:
        if not all(k in row for k in OUTCOME_IDENTITY_KEYS):
            continue
        k = planning_tuple_key(
            row.get("brand_id", ""),
            row.get("teacher_id", ""),
            row.get("topic_id", ""),
            row.get("persona_id", ""),
            row.get("program_id", ""),
            row.get("series_id", ""),
            row.get("week", week),
        )
        by_key[k] = row
    return by_key
