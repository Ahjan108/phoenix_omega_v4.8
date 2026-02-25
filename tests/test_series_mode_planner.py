"""
Acceptance tests for Series Roadmap Planner (P0).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TestSeriesModePlanner(unittest.TestCase):
    """Series roadmap planner: deterministic, unique search_intent_id, band_curve_id present."""

    def test_same_seed_identical_roadmap(self):
        from phoenix_v4.planning.series_mode_planner import plan_series_roadmap
        a = plan_series_roadmap("s1", "burnout", "gen_z_professionals", 4, seed="seed_1")
        b = plan_series_roadmap("s1", "burnout", "gen_z_professionals", 4, seed="seed_1")
        self.assertEqual(a, b, "Same seed must produce identical roadmap")

    def test_different_seed_valid_but_different_roadmap(self):
        from phoenix_v4.planning.series_mode_planner import plan_series_roadmap
        a = plan_series_roadmap("s1", "burnout", "gen_z_professionals", 4, seed="seed_a")
        b = plan_series_roadmap("s1", "burnout", "gen_z_professionals", 4, seed="seed_b")
        self.assertNotEqual(a, b, "Different seed may produce different roadmap")
        for row in a + b:
            self.assertIn("installment_number", row)
            self.assertIn("search_intent_id", row)
            self.assertIn("band_curve_id", row)
            self.assertIn("journey_shape_id", row)
            self.assertIn("book_structure_id", row)
            self.assertIn("duration_class", row)

    def test_all_installments_unique_search_intent_id(self):
        from phoenix_v4.planning.series_mode_planner import plan_series_roadmap
        road = plan_series_roadmap("s1", "burnout", "gen_z_professionals", 6, seed="any")
        intents = [r["search_intent_id"] for r in road]
        self.assertEqual(len(intents), len(set(intents)), "search_intent_id must be unique in series")

    def test_band_curve_id_present_every_installment(self):
        from phoenix_v4.planning.series_mode_planner import plan_series_roadmap
        road = plan_series_roadmap("s1", "burnout", "gen_z_professionals", 3, seed="any")
        for r in road:
            self.assertIn("band_curve_id", r)
            self.assertTrue(r["band_curve_id"], "band_curve_id must be non-empty")


if __name__ == "__main__":
    unittest.main()
