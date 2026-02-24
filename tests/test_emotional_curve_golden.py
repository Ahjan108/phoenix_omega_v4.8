"""
Golden test for emotional curve: dominant_band_sequence, chapter_slot_sequence, atom_ids.
Uses test-only atoms_root and bindings_path; no production config edits.
"""
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)


def _load_fixture():
    import yaml
    path = REPO_ROOT / "tests" / "golden" / "emotional_curve_fixture.yaml"
    return yaml.safe_load(path.read_text())


def test_emotional_curve_golden():
    """Assert compile_plan output matches locked fixture: bands, slots, atom_ids."""
    import yaml
    from phoenix_v4.planning.assembly_compiler import compile_plan

    fixture = _load_fixture()
    book_spec = fixture["book_spec"]
    format_plan = fixture["format_plan"]
    atoms_root = REPO_ROOT / fixture["atoms_root"]
    bindings_path = REPO_ROOT / fixture["bindings_path"]
    arc = fixture.get("arc")

    out = compile_plan(
        book_spec,
        format_plan,
        arc=arc,
        atoms_root=atoms_root,
        bindings_path=bindings_path,
    )

    assert out.dominant_band_sequence == fixture["expected_dominant_band_sequence"], (
        "dominant_band_sequence mismatch"
    )
    assert out.chapter_slot_sequence == fixture["expected_chapter_slot_sequence"], (
        "chapter_slot_sequence mismatch"
    )
    assert out.atom_ids == fixture["expected_atom_ids"], "atom_ids mismatch"


def test_emotional_curve_band_absent_defaults_to_3():
    """One block without BAND: that chapter gets default band 3 (negative test)."""
    import yaml
    from phoenix_v4.planning.assembly_compiler import compile_plan

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_default = {"golden_test_topic": {"allowed_engines": ["default_band_engine"]}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.safe_dump(bindings_default, f)
        bindings_path_default = Path(f.name)
    minimal_arc = {
        "arc_id": "golden_band_default_arc",
        "persona": "golden_test_persona",
        "topic": "golden_test_topic",
        "engine": "default_band_engine",
        "format": "F001",
        "chapter_count": 3,
        "emotional_curve": [3, 4, 5],
        "emotional_temperature_curve": {1: "warm", 2: "warm", 3: "warm"},
        "chapter_intent": {1: "establish", 2: "expose", 3: "integrate"},
        "reflection_strategy_sequence": ["didactic", "socratic", "didactic"],
        "cost_chapter_index": 2,
        "resolution_type": "open_loop",
        "motif": {},
        "emotional_role_sequence": ["recognition", "reframe", "integration"],
    }
    try:
        out = compile_plan(
            {"persona_id": "golden_test_persona", "topic_id": "golden_test_topic", "seed": "emotional_golden_seed"},
            {"chapter_count": 3, "slot_definitions": [["STORY"], ["STORY"], ["STORY"]]},
            arc=minimal_arc,
            atoms_root=atoms_root,
            bindings_path=bindings_path_default,
        )
    finally:
        bindings_path_default.unlink(missing_ok=True)

    assert out.dominant_band_sequence is not None
    assert 3 in out.dominant_band_sequence, "Expected default 3 in sequence when BAND absent in one block"
    assert set(out.dominant_band_sequence) == {3, 4, 5}


if __name__ == "__main__":
    test_emotional_curve_golden()
    test_emotional_curve_band_absent_defaults_to_3()
    print("All emotional curve golden tests passed.")
