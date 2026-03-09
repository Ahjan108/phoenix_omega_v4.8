"""
EI v2 In Planning: load historical_outcomes from file with strict schema validation.
Reject malformed rows; log counts of dropped rows. Canonical key: ei_planning_contracts.planning_tuple_key_from_outcome_row.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from phoenix_v4.planning.ei_planning_contracts import (
    validate_historical_outcome_row,
)


def load_historical_outcomes_from_file(
    path: Path,
) -> Tuple[List[Dict[str, Any]], int, int, List[str]]:
    """
    Load historical_outcomes from JSON or JSONL. Validate each row (identity keys required).
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

    for i, row in enumerate(rows):
        validated = validate_historical_outcome_row(row)
        if validated is not None:
            accepted.append(validated)
        else:
            dropped += 1
            errors.append(f"Row {i + 1}: missing required identity keys or invalid types")

    return accepted, len(accepted), dropped, errors


def historical_outcomes_by_key(
    rows: List[Dict[str, Any]],
) -> Dict[Tuple[str, str, str, str, str, str, str], Dict[str, Any]]:
    """Index validated outcome rows by canonical tuple key for joins."""
    from phoenix_v4.planning.ei_planning_contracts import planning_tuple_key_from_outcome_row

    by_key: Dict[Tuple[str, str, str, str, str, str, str], Dict[str, Any]] = {}
    for row in rows:
        k = planning_tuple_key_from_outcome_row(row)
        by_key[k] = row
    return by_key
