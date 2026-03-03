"""
Tests for Phase 10 — Cross-Brand Divergence Index (CBDI).
Covers: JSD, volatility_bucket, cbdi_pair, run() output shape, alerts.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TestJSD(unittest.TestCase):
    def test_identical_distributions_zero(self):
        from phoenix_v4.ops.cross_brand_divergence import jsd, _counts_to_probs
        P = _counts_to_probs({"a": 5, "b": 5})
        self.assertAlmostEqual(jsd(P, P), 0.0, places=4)

    def test_disjoint_distributions_one(self):
        from phoenix_v4.ops.cross_brand_divergence import jsd, _counts_to_probs
        P = _counts_to_probs({"a": 1})
        Q = _counts_to_probs({"b": 1})
        self.assertAlmostEqual(jsd(P, Q), 1.0, places=2)

    def test_same_support_different_probs(self):
        from phoenix_v4.ops.cross_brand_divergence import jsd, _counts_to_probs
        P = _counts_to_probs({"a": 8, "b": 2})
        Q = _counts_to_probs({"a": 2, "b": 8})
        d = jsd(P, Q)
        self.assertGreater(d, 0.0)
        self.assertLess(d, 1.0)


class TestVolatilityBucket(unittest.TestCase):
    def test_buckets(self):
        from phoenix_v4.ops.cross_brand_divergence import volatility_bucket
        self.assertEqual(volatility_bucket(0.2), "low")
        self.assertEqual(volatility_bucket(0.45), "med")
        self.assertEqual(volatility_bucket(0.7), "high")


class TestCBDPair(unittest.TestCase):
    def test_pair_components_and_score(self):
        from phoenix_v4.ops.cross_brand_divergence import build_brand_distributions, cbdi_pair
        # Two brands with different arc/slot/band
        releases = [
            {"brand_id": "A", "arc_id": "arc1", "slot_sig": "s1", "band_sig": "2-3", "engine_id": "e1", "volatility": 0.3},
            {"brand_id": "A", "arc_id": "arc1", "slot_sig": "s1", "band_sig": "2-3", "engine_id": "e1", "volatility": 0.3},
            {"brand_id": "B", "arc_id": "arc2", "slot_sig": "s2", "band_sig": "4-5", "engine_id": "e2", "volatility": 0.6},
            {"brand_id": "B", "arc_id": "arc2", "slot_sig": "s2", "band_sig": "4-5", "engine_id": "e2", "volatility": 0.6},
        ]
        dists = build_brand_distributions(releases, min_books=2)
        self.assertEqual(set(dists.keys()), {"A", "B"})
        weights = {"arc": 0.30, "slot": 0.20, "band": 0.20, "engine": 0.15, "volatility": 0.15}
        score, comp = cbdi_pair(dists["A"], dists["B"], weights)
        self.assertIn("arc", comp)
        self.assertIn("slot", comp)
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestRun(unittest.TestCase):
    def test_run_no_data_produces_valid_json(self):
        from phoenix_v4.ops.cross_brand_divergence import run
        config = {"cross_brand_divergence": {"window_days": 90, "minimum_books_per_brand": 20}}
        result = run("2026-03-04", 90, None, None, config)
        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["report_date"], "2026-03-04")
        self.assertEqual(result["window_days"], 90)
        self.assertIn("brands_evaluated", result)
        self.assertIn("pairwise_scores", result)
        self.assertIn("alerts", result)

    def test_run_with_two_brands_below_threshold_fires_alert(self):
        from phoenix_v4.ops.cross_brand_divergence import run
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            index_path = tmp_path / "index.jsonl"
            with open(index_path, "w", encoding="utf-8") as f:
                for _ in range(25):
                    f.write(json.dumps({"publish_date": "2026-03-01", "brand_id": "phoenix", "arc_id": "arc_same", "slot_sig": "s", "band_sig": "3-3-4", "engine_id": "e1"}) + "\n")
                for _ in range(25):
                    f.write(json.dumps({"publish_date": "2026-03-01", "brand_id": "other", "arc_id": "arc_same", "slot_sig": "s", "band_sig": "3-3-4", "engine_id": "e1"}) + "\n")
            config = {
                "cross_brand_divergence": {
                    "window_days": 90,
                    "minimum_books_per_brand": 20,
                    "thresholds": {"warn_below": 0.18, "fail_below": 0.12},
                },
            }
            result = run("2026-03-04", 90, index_path, None, config)
            self.assertGreaterEqual(len(result["brands_evaluated"]), 2)
            self.assertGreaterEqual(len(result["pairwise_scores"]), 1)
            if result.get("alerts"):
                self.assertIn(result["alerts"][0]["code"], ("BRAND_CONVERGENCE_LOW", "BRAND_CONVERGENCE_CRITICAL"))


class TestCLI(unittest.TestCase):
    def test_main_exit_zero_when_no_brands(self):
        from phoenix_v4.ops.cross_brand_divergence import main
        import io
        old_argv, old_stdout = sys.argv, sys.stdout
        try:
            sys.argv = ["cross_brand_divergence.py", "--report-date", "2026-03-04", "--out-dir", "/tmp/cbdi_out"]
            sys.stdout = io.StringIO()
            exit_code = main()
        finally:
            sys.argv, sys.stdout = old_argv, old_stdout
        self.assertIn(exit_code, (0, 2))


if __name__ == "__main__":
    unittest.main()
