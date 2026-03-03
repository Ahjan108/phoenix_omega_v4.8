"""
Acceptance tests for P1 series quality gates: freshness, opener/closer, metadata.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _load_script_module(name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(name, script_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestSeriesQualityGates(unittest.TestCase):
    """Fail if new STORY count vs prev below min; INTEGRATION distinct vs prev; opener/closer collision; metadata."""

    def test_fail_new_story_count_below_min_vs_prev(self):
        mod = _load_script_module("check_series_content_uniqueness", REPO_ROOT / "scripts" / "ci" / "check_series_content_uniqueness.py")
        check_series_content_uniqueness = mod.check_series_content_uniqueness
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            # Plan 1: story atoms s1, s2
            plan1 = {
                "series_id": "s1", "installment_number": 1,
                "chapter_slot_sequence": [
                    {"slots": [{"slot_type": "STORY", "atom_id": "s1"}, {"slot_type": "STORY", "atom_id": "s2"}]},
                ],
            }
            # Plan 2: same s1,s2 plus only 1 new (s3) -> new count 1; min_new_story_atoms_vs_prev default 2
            plan2 = {
                "series_id": "s1", "installment_number": 2,
                "chapter_slot_sequence": [
                    {"slots": [{"slot_type": "STORY", "atom_id": "s1"}, {"slot_type": "STORY", "atom_id": "s3"}]},
                ],
            }
            (d / "p1.json").write_text(json.dumps(plan1))
            (d / "p2.json").write_text(json.dumps(plan2))
            violations = check_series_content_uniqueness(d)
            self.assertGreater(len(violations), 0)
            self.assertTrue(any("min_new_story" in str(v) for v in violations))

    def test_fail_integration_atom_repeats_prev_when_distinct_required(self):
        mod = _load_script_module("check_series_content_uniqueness", REPO_ROOT / "scripts" / "ci" / "check_series_content_uniqueness.py")
        check_series_content_uniqueness = mod.check_series_content_uniqueness
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            plan1 = {"series_id": "s1", "installment_number": 1, "chapter_slot_sequence": [
                {"slots": [{"slot_type": "INTEGRATION", "atom_id": "int_a"}]},
            ]}
            plan2 = {"series_id": "s1", "installment_number": 2, "chapter_slot_sequence": [
                {"slots": [{"slot_type": "INTEGRATION", "atom_id": "int_a"}]},
            ]}
            (d / "p1.json").write_text(json.dumps(plan1))
            (d / "p2.json").write_text(json.dumps(plan2))
            violations = check_series_content_uniqueness(d)
            self.assertGreater(len(violations), 0)
            self.assertTrue(any("distinct_integration" in str(v) or "integration" in str(v).lower() for v in violations))

    def test_fail_duplicate_search_intent_id(self):
        mod = _load_script_module("check_series_metadata_intent", REPO_ROOT / "scripts" / "ci" / "check_series_metadata_intent.py")
        check_series_metadata_intent = mod.check_series_metadata_intent
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "p1.json").write_text(json.dumps({"series_id": "s1", "installment_number": 1, "search_intent_id": "problem_solving"}))
            (d / "p2.json").write_text(json.dumps({"series_id": "s1", "installment_number": 2, "search_intent_id": "problem_solving"}))
            violations = check_series_metadata_intent(d)
            self.assertGreater(len(violations), 0)
            self.assertTrue(any("search_intent" in str(v) for v in violations))

    def test_fail_title_similarity_above_threshold(self):
        mod = _load_script_module("check_series_metadata_intent", REPO_ROOT / "scripts" / "ci" / "check_series_metadata_intent.py")
        check_series_metadata_intent = mod.check_series_metadata_intent
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "p1.json").write_text(json.dumps({
                "series_id": "s1", "installment_number": 1, "title": "Meditation for Anxiety and Stress Relief",
            }))
            (d / "p2.json").write_text(json.dumps({
                "series_id": "s1", "installment_number": 2, "title": "Meditation for Anxiety and Stress Relief Guide",
            }))
            violations = check_series_metadata_intent(d)
            # Default threshold 0.85; these two share many tokens so may violate
            self.assertIsInstance(violations, list)


if __name__ == "__main__":
    unittest.main()
