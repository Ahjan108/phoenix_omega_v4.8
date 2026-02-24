"""
Resolve (teacher_id, brand_id) from config when caller does not supply them.
Authority: PLANNING_STATUS.md — config that assigns teacher_id, brand_id per book/series/wave.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
ASSIGNMENTS_PATH = CONFIG_CATALOG / "brand_teacher_assignments.yaml"


def _load_assignments(path: Optional[Path] = None) -> list[dict[str, Any]]:
    path = path or ASSIGNMENTS_PATH
    if not path.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(path.read_text()) or {}
        return data.get("assignments") or []
    except Exception:
        return []


def resolve_teacher_brand(
    topic_id: str = "",
    persona_id: str = "",
    series_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    assignments_path: Optional[Path] = None,
) -> tuple[str, str]:
    """
    Return (teacher_id, brand_id) from first matching assignment row.
    Empty topic_ids/persona_ids/series_ids in a row means "any"; otherwise row must match.
    Defaults: default_teacher, phoenix.
    """
    assignments = _load_assignments(assignments_path)
    if not assignments:
        return "default_teacher", brand_id or "phoenix"

    for row in assignments:
        row_brand = row.get("brand_id") or "phoenix"
        if brand_id and row_brand != brand_id:
            continue
        topic_ids = row.get("topic_ids") or []
        persona_ids = row.get("persona_ids") or []
        series_ids = row.get("series_ids") or []
        if topic_ids and topic_id and topic_id not in topic_ids:
            continue
        if persona_ids and persona_id and persona_id not in persona_ids:
            continue
        if series_ids and series_id and series_id not in series_ids:
            continue
        return (row.get("teacher_id") or "default_teacher"), (row.get("brand_id") or brand_id or "phoenix")

    return "default_teacher", brand_id or "phoenix"
