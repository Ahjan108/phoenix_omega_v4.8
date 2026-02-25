"""
Regression tests for pre-publish gates (run_prepublish_gates.py).

Canonical order: structural entropy -> platform similarity -> prose duplication
-> wave density -> update_similarity_index (last, only on full pass).
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


def _minimal_plan_missing_role_sequence() -> dict:
    """Minimal plan that fails structural entropy (missing emotional_role_sequence)."""
    return {
        "plan_id": "test_book_001",
        "topic_id": "anxiety",
        "persona_id": "gen_z_professional",
        "arc_id": "arc_test",
        "chapter_count": 3,
        "chapter_slot_sequence": [["STORY"], ["STORY"], ["STORY"]],
        "slot_sig": "F006:abc",
        "dominant_band_sequence": [2, 3, 4],
        # no emotional_role_sequence -> check_structural_entropy fails
    }


class TestPrepublishGates(unittest.TestCase):
    """Pre-publish gate runner behavior."""

    def test_index_not_updated_when_gate_1_fails(self):
        """When any of gates 1-4 fails, similarity index must not be updated."""
        script = REPO_ROOT / "scripts" / "ci" / "run_prepublish_gates.py"
        self.assertTrue(script.exists(), "run_prepublish_gates.py must exist")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plans_dir = tmp_path / "plans"
            plans_dir.mkdir()
            wave_rendered = tmp_path / "rendered"
            wave_rendered.mkdir()
            index_path = tmp_path / "index.jsonl"

            # Initial index: one sentinel line so we can detect append
            sentinel = '{"book_id":"sentinel","arc_id":"x"}\n'
            index_path.write_text(sentinel)
            initial_content = index_path.read_text()

            # Plan that fails structural entropy (missing emotional_role_sequence)
            plan = _minimal_plan_missing_role_sequence()
            (plans_dir / "book_001.json").write_text(json.dumps(plan))

            # At least one rendered .txt so prose dup has something to read
            (wave_rendered / "book_001.txt").write_text("Chapter one.\n\nSome prose here.")

            cmd = [
                sys.executable,
                str(script),
                "--plans-dir", str(plans_dir),
                "--index", str(index_path),
                "--wave-rendered-dir", str(wave_rendered),
                "--catalog-rendered-dir", str(tmp_path),  # empty, no catalog
            ]
            result = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.assertNotEqual(result.returncode, 0, "Prepublish must exit non-zero when a gate fails")
            # Index must not have been modified (no append)
            self.assertEqual(
                index_path.read_text(),
                initial_content,
                "Similarity index must not be updated when any of gates 1-4 fails",
            )


if __name__ == "__main__":
    unittest.main()
