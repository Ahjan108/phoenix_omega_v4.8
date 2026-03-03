"""
Teacher × persona compatibility for Teacher Mode. Enforce at planning entry (e.g. run_pipeline).
Prevents off-matrix teacher/persona/engine/locale combinations.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PATH = REPO_ROOT / "config" / "catalog_planning" / "teacher_persona_matrix.yaml"


def load_teacher_matrix(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(path) if path else DEFAULT_PATH
    if not p.exists():
        return {}
    try:
        import yaml
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def validate_teacher_assignment(
    matrix: dict[str, Any],
    teacher_id: str,
    persona_id: str,
    engine_id: str | None = None,
    locale_key: str | None = None,
) -> None:
    """Raise ValueError if teacher_id is not allowed for persona_id / engine_id / locale_key."""
    if not teacher_id:
        return
    teachers = matrix.get("teachers") or {}
    t = teachers.get(teacher_id)
    if not t:
        raise ValueError(f"Teacher '{teacher_id}' not in teacher_persona_matrix")
    allowed_personas = set(t.get("allowed_personas") or [])
    disallowed_personas = set(t.get("disallowed_personas") or [])
    if persona_id and disallowed_personas and persona_id in disallowed_personas:
        raise ValueError(f"Teacher '{teacher_id}' disallowed for persona '{persona_id}'")
    if allowed_personas and persona_id not in allowed_personas:
        raise ValueError(f"Teacher '{teacher_id}' not allowed for persona '{persona_id}'")
    allowed_engines = set(t.get("allowed_engines") or [])
    if engine_id and allowed_engines and engine_id not in allowed_engines:
        raise ValueError(f"Teacher '{teacher_id}' not allowed for engine '{engine_id}'")
    preferred_locales = set(t.get("preferred_locales") or [])
    if locale_key and preferred_locales and locale_key not in preferred_locales:
        raise ValueError(f"Teacher '{teacher_id}' not preferred/allowed for locale '{locale_key}'")
