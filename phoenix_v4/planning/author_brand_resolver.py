"""
Resolve default_author (pen-name author_id) from brand when run_pipeline does not supply --author.
Authority: SYSTEMS_V4.md — "resolve author from brand"; config/brand_author_assignments.yaml.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
ASSIGNMENTS_PATH = REPO_ROOT / "config" / "brand_author_assignments.yaml"


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


def resolve_author_from_brand(
    brand_id: str = "",
    topic_id: str = "",
    persona_id: str = "",
    series_id: Optional[str] = None,
    assignments_path: Optional[Path] = None,
) -> Optional[str]:
    """
    Return default_author (author_id) for the given brand from config, or None if no assignment.
    First matching row wins. Empty topic_ids/persona_ids/series_ids in a row means "any".
    """
    assignments = _load_assignments(assignments_path)
    if not assignments or not brand_id:
        return None

    for row in assignments:
        row_brand = row.get("brand_id") or ""
        if row_brand != brand_id:
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
        default_author = row.get("default_author")
        if default_author is None or (isinstance(default_author, str) and not default_author.strip()):
            return None
        return default_author.strip() if isinstance(default_author, str) else None

    return None
