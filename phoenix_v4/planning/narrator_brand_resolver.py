"""
Resolve default narrator_id from brand when run_pipeline does not supply --narrator.
Authority: Writer Spec §23.5, §23.6; config/brand_narrator_assignments.yaml.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSIGNMENTS_PATH = REPO_ROOT / "config" / "brand_narrator_assignments.yaml"
REGISTRY_PATH = REPO_ROOT / "config" / "narrators" / "narrator_registry.yaml"


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


def _load_registry(path: Optional[Path] = None) -> dict:
    path = path or REGISTRY_PATH
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def resolve_narrator_from_brand(
    brand_id: str = "",
    assignments_path: Optional[Path] = None,
) -> Optional[str]:
    """
    Return default_narrator (narrator_id) for the given brand from config, or None.
    """
    assignments = _load_assignments(assignments_path)
    if not assignments or not brand_id:
        return None
    for row in assignments:
        if (row.get("brand_id") or "") != brand_id:
            continue
        default = row.get("default_narrator")
        if default is None or (isinstance(default, str) and not default.strip()):
            return None
        return default.strip() if isinstance(default, str) else None
    return None


def validate_narrator_for_book(
    narrator_id: str,
    brand_id: str,
    topic_id: str = "",
    registry_path: Optional[Path] = None,
) -> tuple[bool, str]:
    """
    Validate narrator is in registry, brand compatible, approved, and topic not disallowed.
    Returns (ok, error_message). ok=True means valid.
    """
    reg = _load_registry(registry_path)
    narrators = (reg.get("narrators") or {})
    entry = narrators.get(narrator_id)
    if not entry:
        return False, f"narrator_id '{narrator_id}' not in config/narrators/narrator_registry.yaml"
    if entry.get("status") != "approved":
        return False, f"narrator_id '{narrator_id}' status is not approved"
    compat = entry.get("brand_compatibility") or []
    if brand_id and compat and brand_id not in compat:
        return False, f"narrator_id '{narrator_id}' brand_compatibility does not include brand_id '{brand_id}'"
    disallowed = entry.get("disallowed_topics") or []
    if topic_id and disallowed and topic_id in disallowed:
        return False, f"narrator_id '{narrator_id}' disallowed_topics includes topic_id '{topic_id}'"
    return True, ""
