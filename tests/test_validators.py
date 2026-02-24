"""
Smoke tests for compiled plan validator and arc alignment validator.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_validate_compiled_plan_structure():
    """validate_compiled_plan rejects plan when atom_ids length != total slot count."""
    from phoenix_v4.qa.validate_compiled_plan import validate_compiled_plan

    plan = {
        "atom_ids": ["a", "b"],
        "chapter_slot_sequence": [["STORY"], ["STORY"], ["STORY"]],
        "dominant_band_sequence": [2, 3, 2],
    }
    result = validate_compiled_plan(plan)
    assert not result.valid
    assert any("length" in e or "slot" in e for e in result.errors)


def test_validate_compiled_plan_pass():
    """validate_compiled_plan passes when structure and curve are valid."""
    from phoenix_v4.qa.validate_compiled_plan import validate_compiled_plan

    plan = {
        "atom_ids": ["id1", "id2", "id3"],
        "chapter_slot_sequence": [["STORY"], ["STORY"], ["STORY"]],
        "dominant_band_sequence": [2, 4, 3],
    }
    result = validate_compiled_plan(plan)
    assert result.valid, result.errors


def test_validate_arc_alignment_pass():
    """validate_arc_alignment passes when dominant_band_sequence matches arc emotional_curve."""
    from phoenix_v4.qa.validate_arc_alignment import validate_arc_alignment

    plan = {
        "dominant_band_sequence": [2, 5, 4],
        "chapter_slot_sequence": [["STORY"], ["STORY"], ["STORY"]],
    }
    arc = {
        "chapter_count": 3,
        "emotional_curve": [2, 5, 4],
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
    }
    errs = validate_arc_alignment(plan, arc)
    assert len(errs) == 0, errs


def test_validate_arc_alignment_band_mismatch():
    """validate_arc_alignment fails when plan band != arc curve."""
    from phoenix_v4.qa.validate_arc_alignment import validate_arc_alignment

    plan = {
        "dominant_band_sequence": [2, 3, 4],
        "chapter_slot_sequence": [["STORY"], ["STORY"], ["STORY"]],
    }
    arc = {
        "chapter_count": 3,
        "emotional_curve": [2, 5, 4],
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
    }
    errs = validate_arc_alignment(plan, arc)
    assert any("match" in e or "dominant" in e or str(3) in e for e in errs)
