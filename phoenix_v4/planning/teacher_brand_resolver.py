"""
Resolve (teacher_id, brand_id) from config when caller does not supply them.
Authority: PLANNING_STATUS.md — config that assigns teacher_id, brand_id per book/series/wave.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
ASSIGNMENTS_PATH = CONFIG_CATALOG / "brand_teacher_assignments.yaml"
BRAND_TEACHER_MATRIX_PATH = CONFIG_CATALOG / "brand_teacher_matrix.yaml"


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


def _default_brand() -> str:
    """Prefer first configured brand in brand_teacher_matrix.yaml; fallback to phoenix."""
    if not BRAND_TEACHER_MATRIX_PATH.exists():
        return "phoenix"
    try:
        import yaml
        data = yaml.safe_load(BRAND_TEACHER_MATRIX_PATH.read_text()) or {}
        brands = data.get("brands") or {}
        if isinstance(brands, dict) and brands:
            return next(iter(brands.keys()))
    except Exception:
        pass
    return "phoenix"


def resolve_teacher_brand(
    topic_id: str = "",
    persona_id: str = "",
    series_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    assignments_path: Optional[Path] = None,
) -> tuple[str, str]:
    """
    Return (teacher_id, brand_id) from matching assignment rows.
    Empty topic_ids/persona_ids/series_ids in a row means "any"; otherwise row must match.
    If multiple rows match, deterministically route by hash(topic,persona,series) for load spread.
    Defaults: default_teacher + first brand from brand_teacher_matrix.yaml (fallback phoenix).
    """
    assignments = _load_assignments(assignments_path)
    default_brand = _default_brand()
    if not assignments:
        return "default_teacher", brand_id or default_brand

    matches: list[dict[str, Any]] = []
    for row in assignments:
        row_brand = row.get("brand_id") or default_brand
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
        matches.append(row)

    if not matches:
        return "default_teacher", brand_id or default_brand

    if len(matches) == 1:
        chosen = matches[0]
    else:
        candidates = sorted(
            matches,
            key=lambda r: (
                str(r.get("brand_id") or default_brand),
                str(r.get("teacher_id") or "default_teacher"),
            ),
        )
        selector_key = f"{topic_id}|{persona_id}|{series_id or ''}"
        h = int(hashlib.sha256(selector_key.encode("utf-8")).hexdigest(), 16)
        chosen = candidates[h % len(candidates)]
    return (
        chosen.get("teacher_id") or "default_teacher",
        chosen.get("brand_id") or brand_id or default_brand,
    )
