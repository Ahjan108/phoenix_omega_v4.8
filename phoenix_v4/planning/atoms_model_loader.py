"""
Load config/catalog_planning/atoms_model.yaml for legacy vs cluster policy.
Policy: persona_id in legacy_personas → legacy; else cluster.
Single source of truth for atoms_model; allocation_personas_file only overrides allocation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from phoenix_v4.planning.catalog_planner import AtomsModel

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PATH = REPO_ROOT / "config" / "catalog_planning" / "atoms_model.yaml"


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_atoms_model_config(path: Optional[Path] = None) -> dict:
    """Load atoms_model.yaml. Returns dict with legacy_personas (list) and allocation_personas_file (str | null)."""
    p = path or DEFAULT_PATH
    data = _load_yaml(p)
    return {
        "legacy_personas": list(data.get("legacy_personas") or []),
        "allocation_personas_file": data.get("allocation_personas_file") or data.get("cluster_personas_file"),
    }


def is_legacy_persona(persona_id: str, config_path: Optional[Path] = None) -> bool:
    """True iff persona_id is in legacy_personas (atoms_model = legacy). Single source of truth for policy."""
    cfg = load_atoms_model_config(config_path)
    return persona_id in set(cfg["legacy_personas"])


def atoms_model_for_persona(persona_id: str, config_path: Optional[Path] = None) -> AtomsModel:
    """Return atoms_model for persona_id: legacy if in legacy_personas, else cluster."""
    return AtomsModel.LEGACY if is_legacy_persona(persona_id, config_path) else AtomsModel.CLUSTER


def get_allocation_personas_path(config_path: Optional[Path] = None) -> Optional[Path]:
    """Path to optional persona list file for allocation (allocation_personas_file or cluster_personas_file). Returns None if not set."""
    cfg = load_atoms_model_config(config_path)
    raw = cfg.get("allocation_personas_file")
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / "config" / "catalog_planning" / raw
    return path
