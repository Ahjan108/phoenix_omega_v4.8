"""
Engine definition loader (Arc-First Canonical Spec v1.1, ENGINE_DEFINITION_SCHEMA).
Used for engine–arc compatibility check. Structural only.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_ROOT = REPO_ROOT / "config"
DEFAULT_ENGINES_ROOT = CONFIG_ROOT / "source_of_truth" / "engines"

ALLOWED_RESOLUTION_TYPES = frozenset({"open_loop", "internal_shift_only", "grounded_reframe", "identity_shift"})


@dataclass
class EngineDefinition:
    """Loaded engine definition."""
    engine_id: str
    description: str
    core_pattern: list[str]
    allowed_resolution_types: list[str]
    identity_shift_allowed: bool
    open_loop_allowed: bool
    peak_intensity_limit: int
    tone_constraints: list[str]
    prohibited_outcomes: list[str]
    motif_preferences: list[str]
    raw: dict[str, Any]


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def load_engine(engine_id: str, engines_root: Optional[Path] = None) -> Optional[EngineDefinition]:
    """
    Load engine YAML from engines_root / {engine_id}.yaml.
    Returns None if file missing or empty; raises on invalid schema.
    """
    root = engines_root or DEFAULT_ENGINES_ROOT
    path = root / f"{engine_id}.yaml"
    data = _load_yaml(path)
    if not data:
        return None
    eid = data.get("engine_id") or engine_id
    allowed = data.get("allowed_resolution_types") or []
    for r in allowed:
        if r not in ALLOWED_RESOLUTION_TYPES:
            raise ValueError(f"Engine {eid}: allowed_resolution_types contains invalid value {r!r}")
    peak = data.get("peak_intensity_limit")
    if peak is not None and (not isinstance(peak, int) or not (1 <= peak <= 5)):
        raise ValueError(f"Engine {eid}: peak_intensity_limit must be int 1-5, got {peak!r}")
    return EngineDefinition(
        engine_id=str(eid),
        description=str(data.get("description") or ""),
        core_pattern=list(data.get("core_pattern") or []),
        allowed_resolution_types=list(allowed),
        identity_shift_allowed=bool(data.get("identity_shift_allowed", False)),
        open_loop_allowed=bool(data.get("open_loop_allowed", True)),
        peak_intensity_limit=int(peak) if peak is not None else 5,
        tone_constraints=list(data.get("tone_constraints") or []),
        prohibited_outcomes=list(data.get("prohibited_outcomes") or []),
        motif_preferences=list(data.get("motif_preferences") or []),
        raw=data,
    )
