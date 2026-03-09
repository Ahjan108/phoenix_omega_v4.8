"""
Teacher Portfolio Planner: allocate (teacher, topic, persona) for a wave.
Reads config/catalog_planning/brand_teacher_matrix.yaml, teacher_registry,
and teacher_topic_persona_scores.yaml (fit scores → volume/format).
Authority: specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md, specs/TEACHER_UNIVERSAL_AND_SCORING_SPEC.md.
"""
from __future__ import annotations

from collections import Counter, defaultdict
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
SCORES_PATH = CONFIG_CATALOG / "teacher_topic_persona_scores.yaml"


@dataclass
class TeacherAllocation:
    """Single book allocation for a wave."""
    teacher_id: str
    topic_id: str
    persona_id: str
    brand_id: str
    position_in_wave: int
    # Editorial program (Brand → Program → Series → Book). Authority: docs/CATALOG_ARCHITECTURE_AT_SCALE.md.
    # Resolved from editorial_programs.yaml by (brand_id, teacher_id); fallback brand_id when absent.
    program_id: str = ""
    # Worldview (intellectual lens) for catalog differentiation. Resolved from program's worldview_id.
    # Scale differentiation before volume; same topic across worldviews = different ecosystems.
    worldview_id: str = ""
    # Fit score (0–1) and band when teacher_topic_persona_scores.yaml is used; weak → prefer shorter format
    composite_score: Optional[float] = None
    score_band: Optional[str] = None


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


def _load_canonical_personas() -> list[str]:
    """Load persona IDs from config/catalog_planning/canonical_personas.yaml for allocation diversity."""
    data = _load_yaml(CONFIG_CATALOG / "canonical_personas.yaml")
    personas = data.get("personas") or []
    return list(personas) if isinstance(personas, list) else []


def load_teacher_topic_persona_scores(path: Optional[Path] = None) -> dict[str, Any]:
    """Load teacher_topic_persona_scores.yaml; empty dict if missing."""
    return _load_yaml(path or SCORES_PATH)


def load_editorial_programs(path: Optional[Path] = None) -> dict[str, Any]:
    """Load editorial_programs.yaml; empty dict if missing. Keys: programs (dict of program_id -> config).
    Validates no duplicate (brand_id, worldview_id, metadata_style_family); raises ValueError if duplicate.
    """
    cfg = _load_yaml(path or (CONFIG_CATALOG / "editorial_programs.yaml"))
    validate_editorial_programs_uniqueness(cfg)
    return cfg


def validate_editorial_programs_uniqueness(programs_cfg: dict[str, Any]) -> None:
    """Raise ValueError if any (brand_id, worldview_id, metadata_style_family) tuple is duplicated across programs."""
    if not programs_cfg:
        return
    programs = programs_cfg.get("programs") or {}
    seen: set[tuple[str, str, str]] = set()
    for pid, p in programs.items():
        brand = (p.get("brand_id") or "").strip()
        worldview = (p.get("worldview_id") or "").strip()
        family = (p.get("metadata_style_family") or "").strip()
        key = (brand, worldview, family)
        if key in seen:
            raise ValueError(
                f"editorial_programs: duplicate (brand_id, worldview_id, metadata_style_family) "
                f"for program {pid}: ({brand}, {worldview}, {family}). Each program must be distinct."
            )
        seen.add(key)


def resolve_program_id(
    brand_id: str,
    teacher_id: str,
    programs_cfg: dict[str, Any],
) -> str:
    """
    Resolve program_id for (brand_id, teacher_id) from editorial_programs.yaml.
    Teacher domain: each program lists teachers; first program that has this brand and teacher wins.
    Fallback: brand_id so downstream always has a non-empty program key.
    """
    if not programs_cfg:
        return brand_id
    programs = programs_cfg.get("programs") or {}
    for pid, cfg in programs.items():
        if cfg.get("brand_id") != brand_id:
            continue
        teachers = cfg.get("teachers") or []
        if teacher_id in teachers:
            return pid
    return brand_id


def resolve_worldview_id(program_id: str, programs_cfg: dict[str, Any]) -> str:
    """
    Resolve worldview_id from program config. Fallback: program_id when program has no worldview_id.
    """
    if not programs_cfg:
        return program_id or ""
    programs = programs_cfg.get("programs") or {}
    cfg = programs.get(program_id) or {}
    return (cfg.get("worldview_id") or program_id or "").strip()


def get_composite_score_and_band(
    scores_cfg: dict[str, Any],
    teacher_id: str,
    topic_id: str,
    persona_id: str,
) -> tuple[Optional[float], Optional[str]]:
    """
    Return (composite_score, score_band) for (teacher, topic, persona).
    composite_score in [0, 1]; score_band one of strong | medium | weak.
    """
    if not scores_cfg:
        return None, None
    default = float(scores_cfg.get("default_score", 0.5))
    teachers = scores_cfg.get("teachers") or {}
    t = teachers.get(teacher_id) or {}
    topic_scores = t.get("topic_scores") or {}
    persona_scores = t.get("persona_scores") or {}
    t_score = topic_scores.get(topic_id, default)
    p_score = persona_scores.get(persona_id, default)
    formula = scores_cfg.get("composite_formula", "average")
    if formula == "min":
        composite = min(t_score, p_score)
    else:
        composite = (float(t_score) + float(p_score)) / 2.0
    bands = scores_cfg.get("score_bands") or {}
    band_name = None
    for name, bounds in bands.items():
        if isinstance(bounds, dict):
            lo, hi = bounds.get("min", 0), bounds.get("max", 1)
            if lo <= composite <= hi:
                band_name = name
                break
    return round(composite, 4), band_name


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
    personas_override: Optional[list[str]] = None,
) -> list[TeacherAllocation]:
    """
    Produce an ordered list of (teacher_id, topic_id, persona_id, brand_id) for the wave.
    Respects brand matrix (teachers per brand, max per wave) and teacher allowed_topics.
    Excludes teachers below coverage threshold (min EXERCISE, min STORY total) when set (plan §9).
    Does not back-to-back same teacher when spacing_days > 0 (interleaves by brand/teacher).
    personas_override: if provided, use this list instead of canonical_personas.yaml (e.g. for ZH/cluster allocation).
    """
    matrix = load_brand_matrix(brand_matrix_path)
    registry = load_teacher_registry(teacher_registry_path)
    teachers_reg = registry.get("teachers", {})
    brands = matrix.get("brands", {})
    constraints = matrix.get("teacher_constraints", {})
    # Release cadence is now from config/release_velocity and week-by-week schedule (see docs/RELEASE_VELOCITY_AND_SCHEDULE.md).
    # This spacing is only for allocation interleaving (avoid back-to-back same teacher), not upload timing.
    defaults_map = matrix.get("defaults", {})
    default_spacing = defaults_map.get("min_release_spacing_days") or defaults_map.get("release_spacing_days", 7)
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
    for t in eligible:
        topic_pool.update(teachers_reg.get(t, {}).get("allowed_topics", []))
    topic_list = sorted(topic_pool)
    if not topic_list:
        # Fallback: canonical topics so allocation can proceed
        topics_cfg = _load_yaml(CONFIG_CATALOG / "canonical_topics.yaml")
        topic_list = sorted(topics_cfg.get("topics") or []) or ["self_worth"]

    persona_list = personas_override if personas_override is not None else _load_canonical_personas()
    if not persona_list:
        persona_list = ["tech_finance_burnout"]

    scores_cfg = load_teacher_topic_persona_scores()
    programs_cfg = load_editorial_programs()

    allocations: list[TeacherAllocation] = []
    t_idx = 0
    topic_idx = 0
    persona_idx = 0
    teacher_topic_count: dict[tuple[str, str], int] = defaultdict(int)
    teacher_persona_count: dict[tuple[str, str], int] = defaultdict(int)
    max_attempts = (len(topic_list) or 1) * (len(persona_list) or 1) * 2
    attempt = 0
    if not eligible:
        raise ValueError(
            "Allocation impossible: no eligible teachers (registry + brand matrix). "
            "Check teacher_registry.yaml and brand_teacher_matrix.yaml."
        )
    pool_size = len(eligible) * (len(topic_list) or 1) * (len(persona_list) or 1)
    global_max_iterations = max(total_books * 100, pool_size * 20)
    iterations = 0
    while len(allocations) < total_books:
        iterations += 1
        if iterations > global_max_iterations:
            raise ValueError(
                f"Allocation unsatisfiable: could not fill {total_books} books under current teacher_constraints "
                f"(max_books_per_topic / max_books_per_persona). After {global_max_iterations} iterations produced "
                f"{len(allocations)} allocations. Relax constraints in brand_teacher_matrix.yaml or reduce total_books."
            )
        teacher_id = eligible[t_idx % len(eligible)]
        brand_id = teacher_to_brand.get(teacher_id, "default")
        program_id = resolve_program_id(brand_id, teacher_id, programs_cfg)
        worldview_id = resolve_worldview_id(program_id, programs_cfg)
        topic_id = topic_list[topic_idx % len(topic_list)] if topic_list else "self_worth"
        persona_id = persona_list[persona_idx % len(persona_list)]
        tc = constraints.get(teacher_id, {})
        max_per_topic = tc.get("max_books_per_topic")
        max_per_persona = tc.get("max_books_per_persona")
        over_topic = max_per_topic is not None and teacher_topic_count[(teacher_id, topic_id)] >= max_per_topic
        over_persona = max_per_persona is not None and teacher_persona_count[(teacher_id, persona_id)] >= max_per_persona
        if over_topic or over_persona:
            attempt += 1
            if attempt >= max_attempts:
                t_idx += 1
                attempt = 0
            else:
                topic_idx += 1
                persona_idx += 1
            continue
        attempt = 0
        composite_score, score_band = get_composite_score_and_band(
            scores_cfg, teacher_id, topic_id, persona_id
        )
        allocations.append(
            TeacherAllocation(
                teacher_id=teacher_id,
                topic_id=topic_id,
                persona_id=persona_id,
                brand_id=brand_id,
                position_in_wave=len(allocations) + 1,
                program_id=program_id,
                worldview_id=worldview_id,
                composite_score=composite_score,
                score_band=score_band,
            )
        )
        teacher_topic_count[(teacher_id, topic_id)] += 1
        teacher_persona_count[(teacher_id, persona_id)] += 1
        t_idx += 1
        topic_idx += 1
        persona_idx += 1
        if len(eligible) > 1 and len(allocations) % 2 == 0:
            t_idx += 1

    # Per-author 90-day cap: block wave if any (teacher_id, brand_id) exceeds max in this allocation set.
    # Full 90-day enforcement would require schedule/counts; here we cap this wave only.
    diversity_cfg = _load_yaml(CONFIG_CATALOG / "diversity_guards.yaml")
    cap_90 = diversity_cfg.get("max_titles_per_teacher_per_90_days")
    if cap_90 is not None and cap_90 > 0:
        per_teacher_brand: Counter[tuple[str, str]] = Counter()
        for a in allocations:
            per_teacher_brand[(a.teacher_id, a.brand_id)] += 1
        for (tid, bid), count in per_teacher_brand.items():
            if count > cap_90:
                raise ValueError(
                    f"Per-author 90-day cap: teacher {tid} on brand {bid} has {count} titles in this wave, "
                    f"exceeds max_titles_per_teacher_per_90_days={cap_90}. Reduce wave size or spread across teachers/brands."
                )

    return allocations
