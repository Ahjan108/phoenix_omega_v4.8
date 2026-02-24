"""
Tests for arc loader: valid arc loads, emotional_curve length, first/last role, invalid role rejected.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_valid_arc_loads():
    """A well-formed arc YAML loads without errors."""
    try:
        import yaml
    except ImportError:
        return
    from phoenix_v4.planning.arc_loader import load_arc

    arc_path = REPO_ROOT / "tests" / "fixtures" / "minimal_arc.yaml"
    if not arc_path.exists():
        arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "nyc_executives__self_worth__shame__F006.yaml"
    if not arc_path.exists():
        return
    arc = load_arc(arc_path)
    assert arc.arc_id
    assert arc.chapter_count == len(arc.emotional_curve)
    assert arc.chapter_count == len(arc.emotional_role_sequence)


def test_emotional_curve_length():
    """emotional_curve length must equal chapter_count."""
    from phoenix_v4.planning.arc_loader import validate_arc_schema

    arc = {
        "arc_id": "x",
        "persona": "p",
        "topic": "t",
        "engine": "e",
        "format": "F001",
        "chapter_count": 5,
        "emotional_curve": [1, 2, 3, 4],  # length 4 != 5
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm", 4: "warm", 5: "warm"},
        "chapter_intent": {1: "a", 2: "b", 3: "c", 4: "d", 5: "e"},
        "reflection_strategy_sequence": ["didactic"] * 5,
        "cost_chapter_index": 3,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["recognition", "destabilization", "reframe", "stabilization", "integration"],
    }
    errs = validate_arc_schema(arc)
    assert any("emotional_curve" in e for e in errs)


def test_first_chapter_recognition():
    """First emotional_role must be recognition (or opening_override)."""
    from phoenix_v4.planning.arc_loader import validate_arc_schema

    arc = {
        "arc_id": "x",
        "persona": "p",
        "topic": "t",
        "engine": "e",
        "format": "F001",
        "chapter_count": 3,
        "emotional_curve": [2, 3, 2],
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm"},
        "chapter_intent": {1: "a", 2: "b", 3: "c"},
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["reframe", "stabilization", "integration"],  # first not recognition
    }
    errs = validate_arc_schema(arc)
    assert any("recognition" in e.lower() for e in errs)


def test_last_chapter_integration():
    """Last emotional_role must be integration."""
    from phoenix_v4.planning.arc_loader import validate_arc_schema

    arc = {
        "arc_id": "x",
        "persona": "p",
        "topic": "t",
        "engine": "e",
        "format": "F001",
        "chapter_count": 3,
        "emotional_curve": [2, 3, 2],
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm"},
        "chapter_intent": {1: "a", 2: "b", 3: "c"},
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["recognition", "reframe", "stabilization"],  # last not integration
    }
    errs = validate_arc_schema(arc)
    assert any("integration" in e.lower() for e in errs)


def test_invalid_role_rejected():
    """Unknown role name raises validation error."""
    from phoenix_v4.planning.arc_loader import validate_arc_schema

    arc = {
        "arc_id": "x",
        "persona": "p",
        "topic": "t",
        "engine": "e",
        "format": "F001",
        "chapter_count": 3,
        "emotional_curve": [2, 3, 2],
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm"},
        "chapter_intent": {1: "a", 2: "b", 3: "c"},
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["recognition", "invalid_role", "integration"],
    }
    errs = validate_arc_schema(arc)
    assert any("invalid_role" in e or "emotional_role" in e for e in errs)
