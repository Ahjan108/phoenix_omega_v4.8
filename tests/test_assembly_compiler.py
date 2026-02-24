"""
Tests for Stage 3 assembly compiler: determinism, slot structure, band filtering, arc required.
Uses tests/fixtures/atoms and tests/fixtures/bindings; no production config.
Requires PyYAML for fixture-dependent tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _fixtures_available():
    try:
        import yaml
        p = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
        return p.exists()
    except ImportError:
        return False


def test_determinism():
    """Same (book_spec, format_plan, arc) produces identical plan_hash and atom_ids across multiple runs."""
    if not _fixtures_available():
        return
    from phoenix_v4.planning.assembly_compiler import compile_plan

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_path = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
    book_spec = {"persona_id": "golden_test_persona", "topic_id": "golden_test_topic", "seed": "det_seed"}
    format_plan = {"chapter_count": 3, "slot_definitions": [["STORY"], ["STORY"], ["STORY"]]}
    arc = {
        "arc_id": "det_arc",
        "persona": "golden_test_persona",
        "topic": "golden_test_topic",
        "engine": "test_engine",
        "format": "F001",
        "chapter_count": 3,
        "emotional_curve": [2, 5, 4],
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm"},
        "chapter_intent": {1: "a", 2: "b", 3: "c"},
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["recognition", "reframe", "integration"],
    }
    out1 = compile_plan(book_spec, format_plan, arc=arc, atoms_root=atoms_root, bindings_path=bindings_path)
    out2 = compile_plan(book_spec, format_plan, arc=arc, atoms_root=atoms_root, bindings_path=bindings_path)
    assert out1.plan_hash == out2.plan_hash
    assert out1.atom_ids == out2.atom_ids


def test_no_atom_reuse():
    """No atom_id appears twice in a compiled plan."""
    if not _fixtures_available():
        return
    from phoenix_v4.planning.assembly_compiler import compile_plan

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_path = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
    book_spec = {"persona_id": "golden_test_persona", "topic_id": "golden_test_topic"}
    format_plan = {"chapter_count": 3, "slot_definitions": [["STORY"], ["STORY"], ["STORY"]]}
    arc = {
        "arc_id": "x",
        "persona": "golden_test_persona",
        "topic": "golden_test_topic",
        "engine": "test_engine",
        "format": "F001",
        "chapter_count": 3,
        "emotional_curve": [2, 5, 4],
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm"},
        "chapter_intent": {1: "a", 2: "b", 3: "c"},
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["recognition", "reframe", "integration"],
    }
    out = compile_plan(book_spec, format_plan, arc=arc, atoms_root=atoms_root, bindings_path=bindings_path)
    real_ids = [a for a in out.atom_ids if "placeholder:" not in a and "silence:" not in a]
    assert len(real_ids) == len(set(real_ids)), "Duplicate atom_ids in plan"


def test_slot_definitions_respected():
    """atom_ids length == total slot count; chapter_slot_sequence matches slot_definitions."""
    if not _fixtures_available():
        return
    from phoenix_v4.planning.assembly_compiler import compile_plan

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_path = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
    format_plan = {"chapter_count": 3, "slot_definitions": [["STORY"], ["STORY"], ["STORY"]]}
    arc = {
        "arc_id": "x",
        "persona": "golden_test_persona",
        "topic": "golden_test_topic",
        "engine": "test_engine",
        "format": "F001",
        "chapter_count": 3,
        "emotional_curve": [2, 5, 4],
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm"},
        "chapter_intent": {1: "a", 2: "b", 3: "c"},
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["recognition", "reframe", "integration"],
    }
    out = compile_plan(
        {"persona_id": "golden_test_persona", "topic_id": "golden_test_topic"},
        format_plan,
        arc=arc,
        atoms_root=atoms_root,
        bindings_path=bindings_path,
    )
    total_slots = sum(len(row) for row in format_plan["slot_definitions"])
    assert len(out.atom_ids) == total_slots
    assert out.chapter_slot_sequence == format_plan["slot_definitions"]


def test_arc_required():
    """Raises ValueError when arc is None."""
    from phoenix_v4.planning.assembly_compiler import compile_plan

    book_spec = {"persona_id": "golden_test_persona", "topic_id": "golden_test_topic"}
    format_plan = {"chapter_count": 3, "slot_definitions": [["STORY"], ["STORY"], ["STORY"]]}
    try:
        compile_plan(book_spec, format_plan, arc=None, arc_path=None)
        assert False, "Expected ValueError when arc is None"
    except ValueError as e:
        assert "arc" in str(e).lower()


def test_band_filtering():
    """STORY atoms match arc emotional_curve band per chapter."""
    if not _fixtures_available():
        return
    from phoenix_v4.planning.assembly_compiler import compile_plan

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_path = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
    arc = {
        "arc_id": "x",
        "persona": "golden_test_persona",
        "topic": "golden_test_topic",
        "engine": "test_engine",
        "format": "F001",
        "chapter_count": 3,
        "emotional_curve": [2, 5, 4],
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm"},
        "chapter_intent": {1: "a", 2: "b", 3: "c"},
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["recognition", "reframe", "integration"],
    }
    out = compile_plan(
        {"persona_id": "golden_test_persona", "topic_id": "golden_test_topic"},
        {"chapter_count": 3, "slot_definitions": [["STORY"], ["STORY"], ["STORY"]]},
        arc=arc,
        atoms_root=atoms_root,
        bindings_path=bindings_path,
    )
    assert out.dominant_band_sequence == [2, 5, 4]
