"""
Tests for Phase 12 — Unified Platform Health Scorecard (UPHS).
Covers: component score computation, composite, tier, missing artifacts.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TestScorecard(unittest.TestCase):
    def test_run_with_mock_artifacts_produces_tier(self):
        from phoenix_v4.ops.platform_health_scorecard import run
        with tempfile.TemporaryDirectory() as tmp:
            ops = Path(tmp)
            report_date = "2026-03-04"
            # Minimal coverage health: high GREEN ratio
            (ops / f"coverage_health_weekly_{report_date}.json").write_text(json.dumps({
                "summary": {
                    "total_tuples": 100,
                    "risk_counts": {"BLOCKER": 0, "RED": 10, "YELLOW": 10, "GREEN": 80},
                    "velocity": {"week_over_week_story_delta_total": 50},
                },
                "alerts": {"stagnation": {}, "decay": {"global": []}},
            }))
            # Emotional: good entropy/volatility
            (ops / f"catalog_emotional_distribution_{report_date}.json").write_text(json.dumps({
                "global": {"band_entropy_norm": 0.9, "avg_volatility": 0.5, "band_5_share": 0.08},
                "alerts": [],
            }))
            # CBD: one pair, high score
            (ops / f"cross_brand_divergence_{report_date}.json").write_text(json.dumps({
                "pairwise_scores": [{"score": 0.25}],
                "alerts": [],
            }))
            # BISI: one brand, low drift
            (ops / f"brand_identity_stability_{report_date}.json").write_text(json.dumps({
                "results": [{"brand_id": "phoenix", "drift_score": 0.05}],
                "alerts": [],
            }))
            config = {
                "platform_health_scorecard": {
                    "weights": {"coverage_health": 0.35, "emotional_distribution": 0.25, "cross_brand_divergence": 0.20, "brand_identity_stability": 0.20},
                    "tiers": {"stable": 0.85, "watch": 0.70, "risk": 0.55},
                },
                "cross_brand_divergence": {"thresholds": {"warn_below": 0.18, "fail_below": 0.12}},
            }
            result = run(report_date, ops, config)
            self.assertEqual(result["schema_version"], "1.0")
            self.assertIn(result["tier"], ("STABLE", "WATCH", "RISK", "CRITICAL"))
            self.assertGreaterEqual(result["composite_score"], 0)
            self.assertLessEqual(result["composite_score"], 1)
            self.assertIn("coverage_health_score", result["components"])
            self.assertIn("alerts_summary", result)

    def test_run_missing_artifacts_uses_defaults(self):
        from phoenix_v4.ops.platform_health_scorecard import run
        with tempfile.TemporaryDirectory() as tmp:
            ops = Path(tmp)
            result = run("2026-03-04", ops, {"platform_health_scorecard": {"weights": {"coverage_health": 0.35, "emotional_distribution": 0.25, "cross_brand_divergence": 0.20, "brand_identity_stability": 0.20}, "tiers": {"stable": 0.85, "watch": 0.70, "risk": 0.55}}})
            self.assertEqual(result["composite_score"], 0.5)
            # 0.5 < 0.55 (risk threshold) => CRITICAL
            self.assertEqual(result["tier"], "CRITICAL")
            self.assertFalse(result["sources_loaded"]["coverage_health"])


class TestCLI(unittest.TestCase):
    def test_main_exit_codes(self):
        from phoenix_v4.ops.platform_health_scorecard import main
        import io
        old_argv, old_stdout = sys.argv, sys.stdout
        try:
            sys.argv = ["platform_health_scorecard.py", "--report-date", "2026-03-04", "--ops-dir", str(REPO_ROOT / "artifacts" / "ops")]
            sys.stdout = io.StringIO()
            exit_code = main()
        finally:
            sys.argv, sys.stdout = old_argv, old_stdout
        self.assertIn(exit_code, (0, 1, 2))


if __name__ == "__main__":
    unittest.main()
