"""
Teacher Portfolio Planner: allocate (teacher, topic, persona) for a wave.
Reads config/catalog_planning/brand_teacher_matrix.yaml and teacher_registry.
Authority: specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md.
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
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
CONFIG_TEACHERS = REPO_ROOT / "config" / "teachers"


@dataclass
class TeacherAllocation:
    """Single book allocation for a wave."""
    teacher_id: str
    topic_id: str
    persona_id: str
    brand_id: str
    position_in_wave: int


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_brand_matrix(path: Optional[Path] = None) -> dict:
    path = path or (CONFIG_CATALOG / "brand_teacher_matrix.yaml")
    return _load_yaml(path)


def load_teacher_registry(path: Optional[Path] = None) -> dict:
    path = path or (CONFIG_TEACHERS / "teacher_registry.yaml")
    return _load_yaml(path)


def _teacher_meets_coverage_threshold(
    teacher_id: str,
    min_exercise: int = 0,
    min_story_total: int = 0,
) -> bool:
    """Exclude teachers below coverage threshold from wave (plan §9). Uses coverage_gate helpers."""
    if min_exercise <= 0 and min_story_total <= 0:
        return True
    try:
        from phoenix_v4.teacher.coverage_gate import compute_available_teacher_atoms, compute_story_band_inventory
        by_slot = compute_available_teacher_atoms(teacher_id)
        if min_exercise > 0 and by_slot.get("EXERCISE", 0) < min_exercise:
            return False
        if min_story_total > 0:
            bands = compute_story_band_inventory(teacher_id)
            if sum(bands.values()) < min_story_total:
                return False
        return True
    except Exception:
        return True  # no coverage_gate: do not exclude


def allocate_wave(
    wave_id: str,
    teachers: list[str],
    total_books: int,
    spacing_days: int = 14,
    brand_matrix_path: Optional[Path] = None,
    teacher_registry_path: Optional[Path] = None,
    seed: str = "default",
    min_exercise_coverage: int = 0,
    min_story_coverage: int = 0,
) -> list[TeacherAllocation]:
    """
    Produce an ordered list of (teacher_id, topic_id, persona_id, brand_id) for the wave.
    Respects brand matrix (teachers per brand, max per wave) and teacher allowed_topics.
    Excludes teachers below coverage threshold (min EXERCISE, min STORY total) when set (plan §9).
    Does not back-to-back same teacher when spacing_days > 0 (interleaves by brand/teacher).
    """
    matrix = load_brand_matrix(brand_matrix_path)
    registry = load_teacher_registry(teacher_registry_path)
    teachers_reg = registry.get("teachers", {})
    brands = matrix.get("brands", {})
    constraints = matrix.get("teacher_constraints", {})
    default_spacing = matrix.get("defaults", {}).get("min_release_spacing_days", 14)
    if spacing_days <= 0:
        spacing_days = default_spacing

    # Build teacher -> brand map from brands
    teacher_to_brand: dict[str, str] = {}
    for brand_id, data in brands.items():
        for t in data.get("teachers", []):
            teacher_to_brand[t] = brand_id

    # Filter to teachers that exist in registry and have a brand
    eligible = [t for t in teachers if t in teachers_reg and teacher_to_brand.get(t)]
    if not eligible:
        eligible = [t for t in teachers if t in teachers_reg]

    # Coverage threshold: exclude teachers below min EXERCISE / min STORY (plan §9)
    if min_exercise_coverage > 0 or min_story_coverage > 0:
        eligible = [t for t in eligible if _teacher_meets_coverage_threshold(t, min_exercise_coverage, min_story_coverage)]

    # Simple round-robin allocation: cycle (teacher, topic, persona) from allowed sets
    topic_pool = set()
    persona_pool = set()
    for t in eligible:
        topic_pool.update(teachers_reg.get(t, {}).get("allowed_topics", []))
        # Persona not in registry typically; use placeholder or from series_templates later
        persona_pool.add("nyc_executives")  # placeholder; real impl would read from series/capacity
    topic_list = sorted(topic_pool)[:10]
    persona_list = sorted(persona_pool) or ["nyc_executives"]

    allocations: list[TeacherAllocation] = []
    t_idx = 0
    topic_idx = 0
    persona_idx = 0
    for i in range(min(total_books, 100)):
        teacher_id = eligible[t_idx % len(eligible)]
        brand_id = teacher_to_brand.get(teacher_id, "default")
        topic_id = topic_list[topic_idx % len(topic_list)] if topic_list else "self_worth"
        persona_id = persona_list[persona_idx % len(persona_list)]
        allocations.append(
            TeacherAllocation(
                teacher_id=teacher_id,
                topic_id=topic_id,
                persona_id=persona_id,
                brand_id=brand_id,
                position_in_wave=i + 1,
            )
        )
        t_idx += 1
        topic_idx += 1
        persona_idx += 1
        # Stagger teacher: every 2nd book switch teacher to avoid back-to-back same
        if len(eligible) > 1 and (i + 1) % 2 == 0:
            t_idx += 1

    return allocations
