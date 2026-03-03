"""
Deterministic selection for intro/ending variation: opening_style_id, integration_ending_style_id, carry_line_style_id.
Authority: Controlled Intro/Conclusion Variation plan. Same hash algorithm as slot_resolver.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_SOT = REPO_ROOT / "config" / "source_of_truth"


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _selector_index(selector_key: str, available_count: int) -> int:
    """Same as slot_resolver: SHA256(selector_key) -> first 16 bytes big-endian int -> modulo len(available)."""
    if available_count <= 0:
        return 0
    digest = hashlib.sha256(selector_key.encode("utf-8")).digest()
    n = int.from_bytes(digest[:16], "big")
    return n % available_count


def select_opening_style_id(
    topic_id: str,
    persona_id: str,
    seed: str = "default_seed",
    config_root: Optional[Path] = None,
) -> str:
    """
    Deterministic opening recognition style for chapter 0. Returns style id from opening_recognition_styles.yaml.
    """
    config_root = config_root or CONFIG_SOT
    path = config_root / "opening_recognition_styles.yaml"
    data = _load_yaml(path)
    styles = data.get("styles") or {}
    style_ids = [k for k in sorted(styles.keys()) if isinstance(styles.get(k), dict)]
    if not style_ids:
        return ""
    key = f"{topic_id}|{persona_id}|{seed}"
    idx = _selector_index(key, len(style_ids))
    return style_ids[idx]


def select_integration_ending_style_id(
    topic_id: str,
    persona_id: str,
    seed: str = "default_seed",
    config_root: Optional[Path] = None,
) -> str:
    """Deterministic integration ending style for final chapter."""
    config_root = config_root or CONFIG_SOT
    path = config_root / "integration_ending_styles.yaml"
    data = _load_yaml(path)
    styles = data.get("styles") or {}
    style_ids = [k for k in sorted(styles.keys()) if isinstance(styles.get(k), dict)]
    if not style_ids:
        return ""
    key = f"ending|{topic_id}|{persona_id}|{seed}"
    idx = _selector_index(key, len(style_ids))
    return style_ids[idx]


def select_carry_line_style_id(
    topic_id: str,
    persona_id: str,
    seed: str = "default_seed",
    config_root: Optional[Path] = None,
) -> str:
    """Deterministic carry-line style for final chapter."""
    config_root = config_root or CONFIG_SOT
    path = config_root / "carry_line_styles.yaml"
    data = _load_yaml(path)
    styles = data.get("styles") or {}
    style_ids = [k for k in sorted(styles.keys()) if isinstance(styles.get(k), dict)]
    if not style_ids:
        return ""
    key = f"carry|{topic_id}|{persona_id}|{seed}"
    idx = _selector_index(key, len(style_ids))
    return style_ids[idx]


def select_carry_line(
    carry_line_style_id: str,
    topic_id: str,
    persona_id: str,
    seed: str = "default_seed",
    config_root: Optional[Path] = None,
) -> str:
    """
    Pick one line from the given carry_line_style (list of lines). Deterministic.
    Returns empty string if style missing or no lines.
    """
    config_root = config_root or CONFIG_SOT
    path = config_root / "carry_line_styles.yaml"
    data = _load_yaml(path)
    styles = data.get("styles") or {}
    style = styles.get(carry_line_style_id) if isinstance(carry_line_style_id, str) else None
    if not isinstance(style, dict):
        return ""
    lines = style.get("lines") or style.get("line") or []
    if isinstance(lines, str):
        lines = [lines]
    if not lines:
        return ""
    key = f"carry_line|{carry_line_style_id}|{topic_id}|{persona_id}|{seed}"
    idx = _selector_index(key, len(lines))
    return (lines[idx] or "").strip()
