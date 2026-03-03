"""
Tests for Phase 9 — Catalog Emotional Distribution Index.
Covers: volatility formula, entropy, bands_from_sig, aggregate, drift, cache, CLI exit codes.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TestVolatility(unittest.TestCase):
    def test_flat_band_sig_low_volatility(self):
        from phoenix_v4.ops.catalog_emotional_distribution import volatility_from_bands, bands_from_sig
        bands = [3, 3, 3, 3]
        vol = volatility_from_bands(bands)
        self.assertLessEqual(vol, 0.2)
        self.assertEqual(bands_from_sig("3-3-3-3"), [3, 3, 3, 3])

    def test_alternating_high_volatility(self):
        from phoenix_v4.ops.catalog_emotional_distribution import volatility_from_bands
        bands = [1, 5, 1, 5]
        vol = volatility_from_bands(bands)
        self.assertGreaterEqual(vol, 0.7)
        self.assertLessEqual(vol, 1.0)

    def test_single_step_transition_energy(self):
        from phoenix_v4.ops.catalog_emotional_distribution import volatility_from_bands
        # [1,2,3,4,5] -> transitions 1+1+1+1=4, T_max=16, so 0.25; range_util=1.0 -> 0.7*0.25+0.3*1 = 0.475
        bands = [1, 2, 3, 4, 5]
        vol = volatility_from_bands(bands)
        self.assertGreater(vol, 0.4)
        self.assertLess(vol, 0.6)


class TestEntropy(unittest.TestCase):
    def test_uniform_high_entropy(self):
        from phoenix_v4.ops.catalog_emotional_distribution import band_entropy_norm
        counts = {"1": 20, "2": 20, "3": 20, "4": 20, "5": 20}
        h = band_entropy_norm(counts)
        self.assertGreaterEqual(h, 0.99)

    def test_single_band_zero_entropy(self):
        from phoenix_v4.ops.catalog_emotional_distribution import band_entropy_norm
        counts = {"3": 100}
        h = band_entropy_norm(counts)
        self.assertLessEqual(h, 0.01)


class TestBandsFromSig(unittest.TestCase):
    def test_numeric_sig(self):
        from phoenix_v4.ops.catalog_emotional_distribution import bands_from_sig
        self.assertEqual(bands_from_sig("2-3-4-4-2"), [2, 3, 4, 4, 2])
        self.assertEqual(bands_from_sig("1-5"), [1, 5])

    def test_temperature_sig(self):
        from phoenix_v4.ops.catalog_emotional_distribution import bands_from_sig
        self.assertEqual(bands_from_sig("cool-warm-hot"), [2, 3, 4])
        self.assertEqual(bands_from_sig("cool-cool-warm-hot"), [2, 2, 3, 4])


class TestAggregate(unittest.TestCase):
    def test_aggregate_shape(self):
        from phoenix_v4.ops.catalog_emotional_distribution import aggregate
        reports = [
            {"book_id": "b1", "brand_id": "phoenix", "persona_id": "gen_z", "topic_id": "anxiety",
             "band_sig": "2-3-4-4", "max_band": 4, "min_band": 2, "volatility": 0.5},
            {"book_id": "b2", "brand_id": "phoenix", "persona_id": "gen_z", "topic_id": "anxiety",
             "band_sig": "1-3-5", "max_band": 5, "min_band": 1, "volatility": 0.8},
        ]
        global_m, by_brand, by_persona = aggregate(reports)
        self.assertIn("book_count", global_m)
        self.assertIn("chapter_band_distribution", global_m)
        self.assertIn("band_entropy_norm", global_m)
        self.assertIn("avg_volatility", global_m)
        self.assertIn("band_5_share", global_m)
        self.assertIn("phoenix", by_brand)
        self.assertIn("gen_z", by_persona)


class TestRunAndCache(unittest.TestCase):
    def test_run_with_prepopulated_cache_produces_output(self):
        from phoenix_v4.ops.catalog_emotional_distribution import run
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cache_dir = tmp_path / "cache"
            cache_dir.mkdir(parents=True)
            # Pre-populate daily cache for one date in window so run() has data
            report_date = "2026-03-04"
            window_days = 7
            from datetime import datetime, timedelta
            end_dt = datetime.strptime(report_date, "%Y-%m-%d")
            start_dt = end_dt - timedelta(days=window_days - 1)
            some_date = start_dt.strftime("%Y-%m-%d")
            cache_file = cache_dir / f"catalog_emotional_daily_{some_date}.jsonl"
            cache_file.write_text(
                json.dumps({
                    "date": some_date, "book_id": "b1", "brand_id": "phoenix",
                    "persona_id": "gen_z", "topic_id": "anxiety",
                    "band_sig": "2-3-4-4-2", "max_band": 4, "min_band": 2, "volatility": 0.53,
                }) + "\n"
            )
            config = {"catalog_emotional_distribution": {"window_days": window_days}}
            result = run(
                report_date=report_date,
                window_days=window_days,
                history_index_path=None,
                plans_dir=None,
                cache_dir=cache_dir,
                config=config,
            )
            self.assertEqual(result["schema_version"], "1.0")
            self.assertIn("global", result)
            self.assertGreaterEqual(result["global"].get("book_count", 0), 1)
            self.assertIn("chapter_band_distribution", result["global"])
            self.assertIn("by_brand", result)
            self.assertIn("by_persona", result)
            self.assertIn("alerts", result)
            self.assertIn("drift", result)


class TestCLI(unittest.TestCase):
    def test_main_exit_codes(self):
        from phoenix_v4.ops.catalog_emotional_distribution import main
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "out"
            cache_dir = tmp_path / "cache"
            config_path = tmp_path / "config.yaml"
            config_path.write_text("""
catalog_emotional_distribution:
  window_days: 7
  thresholds:
    entropy:
      global_min: 0.99
  alert_policy:
    default_severity: WARN
    hard_fail_codes: []
""")
            # Run with no data: no alerts, exit 0
            import io
            old_argv = sys.argv
            old_stdout = sys.stdout
            try:
                sys.argv = [
                    "catalog_emotional_distribution.py",
                    "--report-date", "2026-03-04",
                    "--window-days", "7",
                    "--plans-dir", str(tmp_path),
                    "--cache-dir", str(cache_dir),
                    "--out-dir", str(out_dir),
                    "--config", str(config_path),
                ]
                sys.stdout = io.StringIO()
                exit_code = main()
            finally:
                sys.argv = old_argv
                sys.stdout = old_stdout
            self.assertIn(exit_code, (0, 2))


if __name__ == "__main__":
    unittest.main()
