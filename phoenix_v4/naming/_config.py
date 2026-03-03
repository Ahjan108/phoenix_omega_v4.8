"""Shared config loading for naming engine. Paths relative to repo root."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OMEGA_TITLE_ENTROPY = REPO_ROOT / "omega" / "title_entropy"
PHOENIX_POLICY = REPO_ROOT / "phoenix_v4" / "policy"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_mechanism_blacklist() -> list[str]:
    data = load_yaml(OMEGA_TITLE_ENTROPY / "mechanism_blacklist.yaml")
    bl = data.get("mechanism_blacklist") or {}
    terms = list(bl.get("clinical_terms") or []) + list(bl.get("abstraction_terms") or [])
    return [t.lower().strip() for t in terms if t]


def load_naming_scoring() -> dict[str, Any]:
    data = load_yaml(PHOENIX_POLICY / "naming_scoring.yaml")
    return data.get("naming_scoring") or {}


def load_intent_taxonomy() -> dict[str, Any]:
    return load_yaml(OMEGA_TITLE_ENTROPY / "intent_taxonomy.yaml")


def load_recognition_lexemes() -> dict[str, Any]:
    return load_yaml(PHOENIX_POLICY / "recognition_lexemes.yaml")


def load_subtitle_patterns() -> dict[str, Any]:
    return load_yaml(OMEGA_TITLE_ENTROPY / "subtitle_patterns.yaml")


def load_persona_flavor() -> dict[str, Any]:
    return load_yaml(OMEGA_TITLE_ENTROPY / "persona_title_flavor.yaml")


def load_title_stems() -> list[str]:
    data = load_yaml(OMEGA_TITLE_ENTROPY / "title_stems.yaml")
    return list(data.get("stems") or [])
