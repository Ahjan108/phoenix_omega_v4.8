"""Load config/video/*.yaml. REPO_ROOT relative to scripts/video/."""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(rel_path: str) -> dict:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        raise RuntimeError("PyYAML required for config/video; pip install pyyaml")
    return yaml.safe_load(text) or {}


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))
