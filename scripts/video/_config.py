"""Load config/video/*.yaml. REPO_ROOT relative to scripts/video/. Config snapshot hash + atomic write."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

CONFIG_VIDEO_DIR = "config/video"


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


def config_snapshot_hash(config_dir: str = CONFIG_VIDEO_DIR) -> str:
    """Hash of all .yaml file contents under config_dir, recursively (sorted by path). Identifies which config version produced an artifact."""
    root = REPO_ROOT / config_dir
    if not root.exists():
        return hashlib.sha256(b"").hexdigest()[:16]
    parts = []
    for p in sorted(root.rglob("*.yaml")):
        parts.append(str(p.relative_to(root)))
        parts.append(p.read_text(encoding="utf-8"))
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()[:16]


def write_atomically(out_path: Path, data: dict | list, encoding: str = "utf-8") -> None:
    """Write JSON to out_path via temp file + rename so the file appears only when complete."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding=encoding)
    tmp.rename(out_path)


def should_skip_output(
    out_path: Path,
    required_keys: list[str],
    force: bool,
    expected_config_hash: str | None = None,
) -> bool:
    """If not force and out_path exists and has all required_keys, return True (skip). If expected_config_hash is set and existing output has config_hash, skip only when they match; otherwise treat as stale and do not skip."""
    if force:
        return False
    if not out_path.exists():
        return False
    try:
        obj = json.loads(out_path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or not all(k in obj for k in required_keys):
            return False
        if expected_config_hash is not None:
            if "config_hash" not in obj:
                return False  # existing output is stale (no config_hash), do not skip
            if obj["config_hash"] != expected_config_hash:
                return False  # config changed, output is stale
        return True
    except Exception:
        return False
