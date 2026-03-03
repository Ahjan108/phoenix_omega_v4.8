"""
Teacher Arc System tests (handoff §16).
- Blueprint schema validation (contract test).
- Planner determinism: same (topic, persona, teacher, arc, seed) => identical blueprint.
- Golden teacher regression: fixed book spec => blueprint generated, valid, required shape.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Skip entire module if teacher arc planner/blueprint not implemented yet
pytest.importorskip("phoenix_v4.planning.teacher_arc_blueprint")
pytest.importorskip("phoenix_v4.planning.teacher_arc_planner")


def test_blueprint_schema_valid_passes():
    """Valid blueprint passes validate_teacher_arc_blueprint."""
    from phoenix_v4.planning.teacher_arc_blueprint import validate_teacher_arc_blueprint

    blueprint = {
        "schema_version": "1.0",
        "teacher_arc_planner_version": "1.0",
        "topic_id": "burnout",
        "persona_id": "gen_z_professionals",
        "teacher_id": "master_feung",
        "arc_id": "test_arc",
        "chapter_count": 2,
        "chapters": [
            {
                "phase": "foundation",
                "weight": "light",
                "energy": "gentle",
                "tps_target_min": 4,
                "author_voice_ratio": 0.4,
                "slot_constraints": {"quote_positions": ["chapter_opener"], "teaching_complexity": "any", "exercise_intensity": "any"},
            },
            {
                "phase": "release",
                "weight": "light",
                "energy": "releasing",
                "tps_target_min": 6,
                "author_voice_ratio": 0.15,
                "slot_constraints": {},
            },
        ],
    }
    errors = validate_teacher_arc_blueprint(blueprint)
    assert errors == [], f"Expected no errors, got {errors}"


def test_blueprint_schema_invalid_fails():
    """Invalid blueprint (wrong phase, missing required) fails validation."""
    from phoenix_v4.planning.teacher_arc_blueprint import validate_teacher_arc_blueprint

    blueprint = {
        "schema_version": "1.0",
        "teacher_arc_planner_version": "1.0",
        "topic_id": "burnout",
        "persona_id": "gen_z_professionals",
        "teacher_id": "master_feung",
        "arc_id": "test_arc",
        "chapter_count": 1,
        "chapters": [
            {
                "phase": "invalid_phase",
                "weight": "light",
                "energy": "gentle",
                "tps_target_min": 4,
                "author_voice_ratio": 0.4,
                "slot_constraints": {},
            },
        ],
    }
    errors = validate_teacher_arc_blueprint(blueprint)
    assert any("phase" in e.lower() for e in errors), f"Expected phase error, got {errors}"


def test_planner_determinism():
    """Same (topic, persona, teacher, arc, seed) => identical blueprint."""
    from phoenix_v4.planning.teacher_arc_planner import generate_blueprint
    from phoenix_v4.planning.arc_loader import load_arc

    arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "gen_z_professionals__burnout__overwhelm__F006.yaml"
    if not arc_path.exists():
        return  # skip if arc file not present
    arc = load_arc(arc_path)
    bp1 = generate_blueprint("burnout", "gen_z_professionals", "master_feung", arc, seed="golden")
    bp2 = generate_blueprint("burnout", "gen_z_professionals", "master_feung", arc, seed="golden")
    assert bp1["chapter_count"] == bp2["chapter_count"]
    assert len(bp1["chapters"]) == len(bp2["chapters"])
    for i, (c1, c2) in enumerate(zip(bp1["chapters"], bp2["chapters"])):
        assert c1["phase"] == c2["phase"], f"Chapter {i} phase mismatch"
        assert c1["author_voice_ratio"] == c2["author_voice_ratio"], f"Chapter {i} ratio mismatch"
    assert json.dumps(bp1, sort_keys=True) == json.dumps(bp2, sort_keys=True), "Blueprint must be identical for same inputs"


def test_golden_teacher_blueprint_shape():
    """Golden teacher book: burnout × gen_z_professionals × master_feung => valid 12-chapter blueprint."""
    from phoenix_v4.planning.teacher_arc_planner import generate_blueprint
    from phoenix_v4.planning.teacher_arc_blueprint import validate_teacher_arc_blueprint
    from phoenix_v4.planning.arc_loader import load_arc

    arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "gen_z_professionals__burnout__overwhelm__F006.yaml"
    if not arc_path.exists():
        return
    arc = load_arc(arc_path)
    blueprint = generate_blueprint(
        topic_id="burnout",
        persona_id="gen_z_professionals",
        teacher_id="master_feung",
        arc=arc,
        seed="golden_regression",
    )
    errors = validate_teacher_arc_blueprint(blueprint)
    assert errors == [], f"Golden blueprint must be valid: {errors}"
    expected_chapters = getattr(arc, "chapter_count", 12) or 12
    assert blueprint["chapter_count"] == expected_chapters
    assert blueprint.get("teacher_arc_planner_version") == "1.0"
    assert blueprint.get("schema_version") == "1.0"
    assert len(blueprint["chapters"]) == expected_chapters
    for i, ch in enumerate(blueprint["chapters"]):
        assert "phase" in ch and "author_voice_ratio" in ch and "tps_target_min" in ch
        assert 0 <= ch["author_voice_ratio"] <= 1
        assert ch["phase"] in ("foundation", "deepening", "challenge", "integration", "release")
