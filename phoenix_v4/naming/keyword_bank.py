"""
Keyword bank for naming engine. Source: config/catalog_planning/series_templates.yaml.
Read-only; no writes. Authority: SYSTEMS_DOCUMENTATION §29.2.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
SERIES_TEMPLATES_PATH = CONFIG_CATALOG / "series_templates.yaml"

_CACHE: dict[str, Any] | None = None


def _load_series_templates() -> dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not SERIES_TEMPLATES_PATH.exists() or yaml is None:
        _CACHE = {"series": {}}
        return _CACHE
    with open(SERIES_TEMPLATES_PATH) as f:
        data = yaml.safe_load(f) or {}
    _CACHE = data
    return _CACHE


def load_series_templates() -> dict[str, Any]:
    """Load series templates YAML. Returns dict with 'series' key."""
    return _load_series_templates()


def get_keywords(series_id: str, angle_id: str, topic_id: str | None = None) -> dict[str, Any]:
    """
    Primary: first search_keyword + angle slug as natural phrase.
    Secondary: remaining search_keywords from series.
    If angle_id is "{topic_id}_general", strip _general and use topic slug as phrase.
    """
    data = load_series_templates()
    series_cfg = (data.get("series") or {}).get(series_id)
    if not series_cfg:
        return {"primary": angle_id.replace("_", " "), "secondary": []}
    search_keywords = list(series_cfg.get("search_keywords") or [])
    if not search_keywords:
        return {"primary": angle_id.replace("_", " "), "secondary": []}

    # Angle phrase: strip _general and use topic slug if angle is "{topic_id}_general"
    raw_angle = angle_id
    if topic_id and raw_angle == f"{topic_id}_general":
        angle_phrase = topic_id.replace("_", " ")
    else:
        angle_phrase = raw_angle.replace("_", " ")

    primary = f"{search_keywords[0]} {angle_phrase}".strip()
    secondary = search_keywords[1:] if len(search_keywords) > 1 else []
    return {"primary": primary, "secondary": secondary}
