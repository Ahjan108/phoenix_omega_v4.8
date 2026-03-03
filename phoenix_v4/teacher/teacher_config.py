"""
Load per-teacher config from config/teachers/<teacher_id>.yaml.
Authority: plan §2.1 — teacher_quality_profile, teacher_exercise_fallback, exercise_wrapper.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_TEACHERS = REPO_ROOT / "config" / "teachers"


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_teacher_config(teacher_id: str) -> dict[str, Any]:
    """
    Load config/teachers/<teacher_id>.yaml. Returns dict with defaults for missing keys.
    Minimum fields per plan: teacher_id, teacher_quality_profile, teacher_exercise_fallback,
    fallback_exercise_share_min, teacher_total_share_min, exercise_wrapper (intro_templates, close_templates).
    """
    out: dict[str, Any] = {
        "teacher_id": teacher_id,
        "teacher_quality_profile": "strict",
        "teacher_exercise_fallback": False,
        "fallback_exercise_share_min": 0.60,
        "teacher_total_share_min": 0.70,
        "exercise_wrapper": {
            "intro_templates": [],
            "close_templates": [],
        },
    }
    path = CONFIG_TEACHERS / f"{teacher_id}.yaml"
    data = _load_yaml(path)
    if not data:
        return out
    for k in ("teacher_quality_profile", "teacher_exercise_fallback", "fallback_exercise_share_min", "teacher_total_share_min"):
        if k in data and data[k] is not None:
            out[k] = data[k]
    if "exercise_wrapper" in data and isinstance(data["exercise_wrapper"], dict):
        ew = data["exercise_wrapper"]
        out["exercise_wrapper"] = {
            "intro_templates": list(ew.get("intro_templates") or []),
            "close_templates": list(ew.get("close_templates") or []),
        }
    return out
