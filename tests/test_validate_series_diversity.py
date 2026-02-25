"""
Acceptance tests for Series Diversity Validator (P0).
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _plan(series_id: str, inst: int, primary_mechanism_id: str = "", journey_shape_id: str = "", band_curve_id: str = "",
          book_structure_id: str = "linear", motif_id: str = "m1", reframe_profile_id: str = "balanced") -> dict:
    return {
        "plan_id": f"book_{series_id}_{inst}",
        "series_id": series_id,
        "installment_number": inst,
        "primary_mechanism_id": primary_mechanism_id or None,
        "journey_shape_id": journey_shape_id or "recognition_to_agency",
        "band_curve_id": band_curve_id or None,
        "book_structure_id": book_structure_id,
        "motif_id": motif_id,
        "reframe_profile_id": reframe_profile_id,
    }


class TestValidateSeriesDiversity(unittest.TestCase):
    """Hard fail on adjacent (mechanism+journey) or band_curve; soft warn on combo density."""

    def test_hard_fail_adjacent_same_mechanism_journey(self):
        from phoenix_v4.qa.validate_series_diversity import validate_series_diversity
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "p1.json").write_text(json.dumps(_plan("s1", 1, "shame", "recognition_to_agency", "gentle_rise")))
            (d / "p2.json").write_text(json.dumps(_plan("s1", 2, "shame", "recognition_to_agency", "two_peak")))
            hard, soft = validate_series_diversity(d)
            self.assertGreater(len(hard), 0, "Must hard-fail when adjacent share primary_mechanism_id + journey_shape_id")
            self.assertTrue(any("adjacent_mech_journey" in str(v) for v in hard))

    def test_hard_fail_adjacent_same_band_curve_id(self):
        from phoenix_v4.qa.validate_series_diversity import validate_series_diversity
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "p1.json").write_text(json.dumps(_plan("s1", 1, "shame", "linear_rise", "gentle_rise")))
            (d / "p2.json").write_text(json.dumps(_plan("s1", 2, "grief", "crisis_landing", "gentle_rise")))
            hard, soft = validate_series_diversity(d)
            self.assertGreater(len(hard), 0, "Must hard-fail when adjacent share band_curve_id")
            self.assertTrue(any("adjacent_band_curve" in str(v) for v in hard))

    def test_soft_warning_combo_density_no_fail(self):
        from phoenix_v4.qa.validate_series_diversity import validate_series_diversity
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            # Same (book_structure, journey, motif, reframe) combo on all 3 -> high density; but adjacent mech+journey and band_curve all differ -> no hard fail
            (d / "p1.json").write_text(json.dumps(_plan("s1", 1, "shame", "linear_rise", "gentle_rise",
                book_structure_id="linear_transformation", motif_id="m1", reframe_profile_id="balanced")))
            (d / "p2.json").write_text(json.dumps(_plan("s1", 2, "grief", "crisis_landing", "two_peak",
                book_structure_id="linear_transformation", motif_id="m1", reframe_profile_id="balanced")))
            (d / "p3.json").write_text(json.dumps(_plan("s1", 3, "overwhelm", "recognition_to_agency", "steady_build",
                book_structure_id="linear_transformation", motif_id="m1", reframe_profile_id="balanced")))
            hard, soft = validate_series_diversity(d)
            self.assertEqual(len(hard), 0, "Combo density should not hard-fail")
            self.assertIsInstance(soft, list)


if __name__ == "__main__":
    unittest.main()
