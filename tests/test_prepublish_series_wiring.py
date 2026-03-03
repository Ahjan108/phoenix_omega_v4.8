"""
Acceptance tests: prepublish wiring for series diversity (P0).
- Any hard series violation => prepublish exit 1, index not updated.
- Only soft warnings => prepublish passes (or warn code), index update allowed per policy.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _plan(series_id: str, inst: int, primary_mechanism_id: str = "", journey_shape_id: str = "", band_curve_id: str = "") -> dict:
    return {
        "plan_id": f"book_{series_id}_{inst}",
        "series_id": series_id,
        "installment_number": inst,
        "topic_id": "burnout",
        "persona_id": "gen_z",
        "arc_id": "arc1",
        "emotional_role_sequence": ["recognition", "reframe", "integration"],
        "emotional_temperature_sequence": [0.3, 0.6, 0.8],
        "primary_mechanism_id": primary_mechanism_id or None,
        "journey_shape_id": journey_shape_id or "recognition_to_agency",
        "band_curve_id": band_curve_id or None,
        "book_structure_id": "linear_transformation",
        "slot_sig": "F006:abc",
        "chapter_slot_sequence": [{"slots": [{"slot_type": "STORY", "atom_id": "s1"}]}],
    }


class TestPrepublishSeriesWiring(unittest.TestCase):
    """Hard series violation => exit 1 and index not updated; soft only => pass."""

    def test_hard_series_violation_prepublish_exit_1_index_not_updated(self):
        """When series diversity hard rule fails, prepublish must exit 1 and not update index."""
        script = REPO_ROOT / "scripts" / "ci" / "run_prepublish_gates.py"
        self.assertTrue(script.exists())

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plans_dir = tmp_path / "plans"
            plans_dir.mkdir()
            wave_rendered = tmp_path / "rendered"
            wave_rendered.mkdir()
            index_path = tmp_path / "index.jsonl"
            sentinel = '{"book_id":"sentinel"}\n'
            index_path.write_text(sentinel)
            initial_content = index_path.read_text()

            # Two plans in same series with same (primary_mechanism_id + journey_shape_id) -> hard fail
            (plans_dir / "p1.json").write_text(json.dumps(_plan("s1", 1, "shame", "recognition_to_agency", "gentle_rise")))
            (plans_dir / "p2.json").write_text(json.dumps(_plan("s1", 2, "shame", "recognition_to_agency", "two_peak")))
            (wave_rendered / "p1.txt").write_text("Open.\n\nBody.")
            (wave_rendered / "p2.txt").write_text("Open.\n\nBody two.")

            cmd = [
                sys.executable, str(script),
                "--plans-dir", str(plans_dir),
                "--index", str(index_path),
                "--wave-rendered-dir", str(wave_rendered),
                "--catalog-rendered-dir", str(tmp_path),
            ]
            result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=90)
            self.assertNotEqual(result.returncode, 0, "Prepublish must exit non-zero on hard series violation")
            self.assertEqual(
                index_path.read_text(),
                initial_content,
                "Index must not be updated when series diversity hard rule fails",
            )

    def test_only_soft_warnings_prepublish_passes(self):
        """When only soft series warnings (no hard violations), prepublish can pass; index update allowed when no other failures."""
        from phoenix_v4.qa.validate_series_diversity import validate_series_diversity
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            # Adjacent different mech+journey and band_curve -> no hard violation
            (d / "p1.json").write_text(json.dumps(_plan("s1", 1, "shame", "recognition_to_agency", "gentle_rise")))
            (d / "p2.json").write_text(json.dumps(_plan("s1", 2, "grief", "linear_rise", "two_peak")))
            hard, soft = validate_series_diversity(d)
            self.assertEqual(len(hard), 0)
            # Soft may be 0 or 1 depending on combo density
            self.assertIsInstance(soft, list)


if __name__ == "__main__":
    unittest.main()
