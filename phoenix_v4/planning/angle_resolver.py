"""
Angle Integration Layer (V4.7). DEV SPEC: angle as structural narrative driver.
Loads config/angles/angle_registry.yaml; resolves arc path from angle; provides angle context for Stage 3.
Arc-First remains authoritative. Angle chooses variant (arc_path when set).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ANGLE_REGISTRY = REPO_ROOT / "config" / "angles" / "angle_registry.yaml"


def load_angle_registry(registry_path: Optional[Path] = None) -> dict[str, Any]:
    """Load angle_registry.yaml. Returns {angles: {angle_id: {...}}} or empty dict."""
    path = registry_path or DEFAULT_ANGLE_REGISTRY
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_angle_context(
    angle_id: Optional[str],
    registry_path: Optional[Path] = None,
    fail_fast: bool = False,
) -> Optional[dict[str, Any]]:
    """
    Return angle context dict for angle_id (chapter_1_role_bias, integration_reinforcement_type, framing_mode, etc.)
    or None if angle_id missing/not in registry. If fail_fast=True and angle_id is non-empty but not in registry, raise ValueError.
    """
    if not angle_id or not (angle_id := str(angle_id).strip()):
        return None
    reg = load_angle_registry(registry_path)
    angles_map = reg.get("angles") or {}
    angles = angles_map.get(angle_id)
    if not angles or not isinstance(angles, dict):
        if fail_fast:
            raise ValueError(
                f"angle_id {angle_id!r} not found in angle_registry (config/angles/angle_registry.yaml). "
                "Add it or omit angle_id."
            )
        return None
    return dict(angles)


def resolve_arc_path(
    angle_id: Optional[str],
    default_arc_path: Path,
    repo_root: Optional[Path] = None,
    registry_path: Optional[Path] = None,
) -> Path:
    """
    If angle_id is in registry and has arc_path set, return resolved path (repo_root / arc_path);
    else return default_arc_path. Arc variant is static; no runtime randomization.
    """
    path = default_arc_path
    root = repo_root or REPO_ROOT
    if not angle_id or not (angle_id := str(angle_id).strip()):
        return path
    ctx = get_angle_context(angle_id, registry_path)
    if not ctx:
        return path
    arc_path_str = ctx.get("arc_path")
    if not arc_path_str or not isinstance(arc_path_str, str):
        return path
    resolved = (root / arc_path_str.strip()).resolve()
    if resolved.exists():
        return resolved
    return path
