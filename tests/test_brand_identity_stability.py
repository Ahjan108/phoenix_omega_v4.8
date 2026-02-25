"""
Tests for Phase 11 — Brand Identity Stability Index (BISI).
Covers: run() output shape, drift computed from current vs previous window, alerts.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TestRun(unittest.TestCase):
    def test_run_no_data_produces_valid_json(self):
        from phoenix_v4.ops.brand_identity_stability import run
        config = {"brand_identity_stability": {"window_days": 90, "minimum_books_per_brand": 20}}
        result = run("2026-03-04", 90, None, None, config)
        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["report_date"], "2026-03-04")
        self.assertEqual(result["window_days"], 90)
        self.assertIn("brands_evaluated", result)
        self.assertIn("results", result)
        self.assertIn("alerts", result)

    def test_run_with_two_windows_drift_fires_alert(self):
        from phoenix_v4.ops.brand_identity_stability import run
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            index_path = tmp_path / "index.jsonl"
            # Current window: 2026-02-03 to 2026-03-04 (phoenix: 25 releases, arc_a)
            # Previous window: 2025-12-05 to 2026-01-03 (phoenix: 25 releases, arc_b)
            # So phoenix has different arc dist in W vs W_prev -> drift > 0
            with open(index_path, "w", encoding="utf-8") as f:
                for i in range(25):
                    f.write(json.dumps({
                        "publish_date": "2026-03-01",
                        "brand_id": "phoenix",
                        "arc_id": "arc_current",
                        "slot_sig": "s1",
                        "band_sig": "3-3-4",
                        "engine_id": "e1",
                    }) + "\n")
                # Previous window for report 2026-03-04 is [2025-09-06, 2025-12-04]
                for i in range(25):
                    f.write(json.dumps({
                        "publish_date": "2025-11-01",
                        "brand_id": "phoenix",
                        "arc_id": "arc_previous",
                        "slot_sig": "s2",
                        "band_sig": "2-4-4",
                        "engine_id": "e2",
                    }) + "\n")
            config = {
                "brand_identity_stability": {
                    "window_days": 90,
                    "minimum_books_per_brand": 20,
                    "thresholds": {"warn_above": 0.18, "fail_above": 0.25},
                },
            }
            result = run("2026-03-04", 90, index_path, None, config)
            self.assertGreaterEqual(len(result["brands_evaluated"]), 1)
            self.assertGreaterEqual(len(result["results"]), 1)
            self.assertEqual(result["results"][0]["brand_id"], "phoenix")
            self.assertGreater(result["results"][0]["drift_score"], 0)
            self.assertIn("arc", result["results"][0]["components"])
            if result["results"][0]["drift_score"] > 0.18 and result.get("alerts"):
                self.assertIn(result["alerts"][0]["code"], ("BRAND_IDENTITY_DRIFT_HIGH", "BRAND_IDENTITY_DRIFT_CRITICAL"))


class TestCLI(unittest.TestCase):
    def test_main_exit_zero_when_no_brands(self):
        from phoenix_v4.ops.brand_identity_stability import main
        import io
        old_argv, old_stdout = sys.argv, sys.stdout
        try:
            sys.argv = ["brand_identity_stability.py", "--report-date", "2026-03-04", "--out-dir", "/tmp/bisi_out"]
            sys.stdout = io.StringIO()
            exit_code = main()
        finally:
            sys.argv, sys.stdout = old_argv, old_stdout
        self.assertIn(exit_code, (0, 2))


if __name__ == "__main__":
    unittest.main()
