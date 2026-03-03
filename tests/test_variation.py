"""
Tests for Structural Variation V4: schema, selector, reorder, validators.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Repo root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_schema_backward_compat():
    """Missing variation fields are auto-filled with defaults."""
    from phoenix_v4.planning.schema_v4 import apply_variation_defaults, VARIATION_DEFAULTS

    plan = {"plan_hash": "abc", "chapter_slot_sequence": [[], [], []]}
    applied = apply_variation_defaults(plan, chapter_count=3)
    assert applied["book_structure_id"] == VARIATION_DEFAULTS["book_structure_id"]
    assert applied["journey_shape_id"] == VARIATION_DEFAULTS["journey_shape_id"]
    assert applied["motif_id"] == VARIATION_DEFAULTS["motif_id"]
    assert applied["section_reorder_mode"] == VARIATION_DEFAULTS["section_reorder_mode"]
    assert applied["reframe_profile_id"] == VARIATION_DEFAULTS["reframe_profile_id"]
    assert len(applied["chapter_archetypes"]) == 3


def test_variation_signature_deterministic():
    """Same knobs => same variation_signature."""
    from phoenix_v4.planning.schema_v4 import compute_variation_signature

    a = compute_variation_signature(
        "linear_transformation", "recognition_to_agency", "motif_pattern",
        "none", "balanced", "MAP_PROMISE", "self_worth", "nyc_executives", "arc_1", 1,
        ["establish", "expose", "integrate"],
    )
    b = compute_variation_signature(
        "linear_transformation", "recognition_to_agency", "motif_pattern",
        "none", "balanced", "MAP_PROMISE", "self_worth", "nyc_executives", "arc_1", 1,
        ["establish", "expose", "integrate"],
    )
    assert a == b
    c = compute_variation_signature(
        "three_act", "recognition_to_agency", "motif_pattern",
        "none", "balanced", "MAP_PROMISE", "self_worth", "nyc_executives", "arc_1", 1,
        ["establish", "expose", "integrate"],
    )
    assert a != c


def test_get_plan_variation_signature():
    """Recompute from plan dict; missing keys use defaults."""
    from phoenix_v4.planning.schema_v4 import get_plan_variation_signature

    plan = {
        "topic_id": "t",
        "persona_id": "p",
        "chapter_slot_sequence": [[ "HOOK", "SCENE" ]],
        "book_structure_id": "linear_transformation",
        "journey_shape_id": "recognition_to_agency",
        "motif_id": "motif_pattern",
        "section_reorder_mode": "none",
        "reframe_profile_id": "balanced",
        "chapter_archetypes": ["establish"],
    }
    sig = get_plan_variation_signature(plan)
    assert isinstance(sig, str) and len(sig) == 32


def test_deterministic_selection_same_seed():
    """Same seed + same inputs => same knobs."""
    from phoenix_v4.planning.variation_selector import select_variation_knobs

    a = select_variation_knobs("self_worth", "nyc_executives", 8, seed="test_seed_001")
    b = select_variation_knobs("self_worth", "nyc_executives", 8, seed="test_seed_001")
    assert a["book_structure_id"] == b["book_structure_id"]
    assert a["journey_shape_id"] == b["journey_shape_id"]
    assert a["motif_id"] == b["motif_id"]
    assert a["variation_signature"] == b["variation_signature"]
    assert a["chapter_archetypes"] == b["chapter_archetypes"]


def test_section_reorder_safety():
    """_apply_section_reorder preserves slot type set and count per chapter."""
    from phoenix_v4.planning.assembly_compiler import _apply_section_reorder

    slot_defs = [
        ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"],
        ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"],
    ]
    out = _apply_section_reorder(slot_defs, "local_reflection_integration")
    assert len(out) == len(slot_defs)
    for i, row in enumerate(out):
        assert set(row) == set(slot_defs[i])
        assert len(row) == len(slot_defs[i])
    # none leaves unchanged
    out_none = _apply_section_reorder(slot_defs, "none")
    assert out_none == slot_defs


def test_validate_motif_saturation_pass():
    """Motif injections within limits pass."""
    from phoenix_v4.qa.validate_motif_saturation import validate_motif_saturation

    plan = {
        "chapter_slot_sequence": [["HOOK", "REFLECTION"], ["HOOK", "REFLECTION"]],
        "motif_injections": [
            {"chapter_index": 0, "slot_index": 1, "phrase": "One."},
            {"chapter_index": 1, "slot_index": 1, "phrase": "Two."},
        ],
    }
    r = validate_motif_saturation(plan)
    assert r.valid, r.errors


def test_validate_motif_saturation_fail_per_chapter():
    """More than 2 motif injections in one chapter fails."""
    from phoenix_v4.qa.validate_motif_saturation import validate_motif_saturation

    plan = {
        "chapter_slot_sequence": [["REFLECTION", "REFLECTION", "REFLECTION"]],
        "motif_injections": [
            {"chapter_index": 0, "slot_index": 0, "phrase": "A"},
            {"chapter_index": 0, "slot_index": 1, "phrase": "B"},
            {"chapter_index": 0, "slot_index": 2, "phrase": "C"},
        ],
    }
    r = validate_motif_saturation(plan)
    assert not r.valid
    assert any("chapter" in e for e in r.errors)


def test_validate_variation_signature_present():
    """Plan with valid variation_signature passes."""
    from phoenix_v4.planning.schema_v4 import get_plan_variation_signature
    from phoenix_v4.qa.validate_variation_signature import validate_variation_signature

    plan = {
        "topic_id": "t", "persona_id": "p",
        "chapter_slot_sequence": [["HOOK"]],
        "book_structure_id": "linear_transformation",
        "journey_shape_id": "recognition_to_agency",
        "motif_id": "motif_pattern",
        "section_reorder_mode": "none",
        "reframe_profile_id": "balanced",
        "chapter_archetypes": ["establish"],
    }
    plan["variation_signature"] = get_plan_variation_signature(plan)
    r = validate_variation_signature(plan)
    assert r.valid, r.errors


def test_validate_variation_signature_missing():
    """Plan missing variation_signature fails."""
    from phoenix_v4.qa.validate_variation_signature import validate_variation_signature

    r = validate_variation_signature({"plan_hash": "x"})
    assert not r.valid
    assert any("variation_signature" in e for e in r.errors)


def test_validate_journey_shape_coverage():
    """Valid journey_shape_id in config passes."""
    from phoenix_v4.qa.validate_journey_shape_coverage import validate_journey_shape_coverage

    plan = {"journey_shape_id": "recognition_to_agency", "chapter_slot_sequence": [[], [], [], [], [], [], [], []]}
    r = validate_journey_shape_coverage(plan)
    assert r.valid, r.errors


def test_validate_section_reorder_safety():
    """Same slot type set per chapter passes."""
    from phoenix_v4.qa.validate_section_reorder_safety import validate_section_reorder_safety

    plan = {"chapter_slot_sequence": [["HOOK", "SCENE", "STORY"], ["HOOK", "SCENE", "STORY"]], "section_reorder_mode": "hook_scene_swap"}
    r = validate_section_reorder_safety(plan)
    assert r.valid, r.errors


if __name__ == "__main__":
    test_schema_backward_compat()
    test_variation_signature_deterministic()
    test_get_plan_variation_signature()
    test_deterministic_selection_same_seed()
    test_section_reorder_safety()
    test_validate_motif_saturation_pass()
    test_validate_motif_saturation_fail_per_chapter()
    test_validate_variation_signature_present()
    test_validate_variation_signature_missing()
    test_validate_journey_shape_coverage()
    test_validate_section_reorder_safety()
    print("All variation tests passed.")
