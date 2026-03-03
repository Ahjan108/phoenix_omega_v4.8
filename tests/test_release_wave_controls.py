"""
Tests for Phase 6 release-wave similarity & burst controls.
Covers: weekly caps, exact clusters, anti-homogeneity score, legacy plan handling.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _minimal_plan(book_id: str, topic_id: str, persona_id: str, arc_id: str, slot_sig: str, band_sig: str, **overrides) -> dict:
    base = {
        "plan_id": book_id,
        "topic_id": topic_id,
        "persona_id": persona_id,
        "arc_id": arc_id,
        "slot_sig": slot_sig,
        "dominant_band_sequence": [int(x) for x in band_sig.split("-")] if band_sig else [3, 3, 4],
        "chapter_slot_sequence": [["STORY"], ["STORY"], ["STORY"]],
        "variation_signature": overrides.pop("variation_signature", "v1"),
    }
    if band_sig:
        base["dominant_band_sequence"] = [int(x) for x in band_sig.split("-")]
    base.update(overrides)
    return base


class TestReleaseWaveControls(unittest.TestCase):
    """Phase 6 release wave checks."""

    def test_weekly_cap_topic_exceeded(self):
        """Topic burst: 10 books same topic → FAIL WEEKLY_CAP_TOPIC_EXCEEDED."""
        from phoenix_v4.ops.check_release_wave import check_release_wave

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plans_dir = tmp_path / "plans"
            plans_dir.mkdir()
            config = tmp_path / "config.yaml"
            config.write_text("""
release_wave_controls:
  allow_legacy_plans: true
  weekly_caps:
    max_same_topic: 6
  clustering:
    enabled: false
  anti_homogeneity:
    enabled: false
""")
            # 10 plans same topic, different persona/arc to avoid other caps
            sig = "F006:abc123"
            band = "2-3-4-4-3"
            for i in range(10):
                plan = _minimal_plan(
                    book_id=f"book_{i}",
                    topic_id="anxiety",
                    persona_id=f"persona_{i % 3}",
                    arc_id=f"arc_{i}",
                    slot_sig=sig,
                    band_sig=band,
                )
                (plans_dir / f"p{i}.json").write_text(json.dumps(plan))

            result = check_release_wave(plans_dir, config)
        self.assertEqual(result.status, "FAIL")
        codes = [v.code for v in result.violations]
        self.assertIn("WEEKLY_CAP_TOPIC_EXCEEDED", codes)

    def test_exact_cluster_too_large(self):
        """Exact cluster: 5 plans same wave_fingerprint → FAIL."""
        from phoenix_v4.ops.check_release_wave import check_release_wave

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plans_dir = tmp_path / "plans"
            plans_dir.mkdir()
            config = tmp_path / "config.yaml"
            config.write_text("""
release_wave_controls:
  allow_legacy_plans: true
  weekly_caps:
    max_same_wave_fingerprint: 3
  clustering:
    enabled: true
    exact_bucket_min_cluster_size: 3
  anti_homogeneity:
    enabled: false
""")
            sig = "F006:same_slot_hash"
            band = "2-3-4-4-3-2"
            arc = "persona_anxiety_watcher_F006"
            for i in range(5):
                plan = _minimal_plan(
                    book_id=f"book_{i}",
                    topic_id="anxiety",
                    persona_id="gen_z",
                    arc_id=arc,
                    slot_sig=sig,
                    band_sig=band,
                    variation_signature="same_var",
                )
                (plans_dir / f"p{i}.json").write_text(json.dumps(plan))

            result = check_release_wave(plans_dir, config)
        self.assertEqual(result.status, "FAIL")
        codes = [v.code for v in result.violations]
        self.assertTrue(any("WAVE_CLUSTER" in c or "EXACT" in c for c in codes))
        self.assertGreaterEqual(len(result.exact_clusters), 1)
        self.assertEqual(result.exact_clusters[0].size, 5)

    def test_anti_homogeneity_score_diverse_passes(self):
        """Diverse wave → PASS (score above threshold)."""
        from phoenix_v4.ops.check_release_wave import check_release_wave

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plans_dir = tmp_path / "plans"
            plans_dir.mkdir()
            config = tmp_path / "config.yaml"
            config.write_text("""
release_wave_controls:
  allow_legacy_plans: true
  weekly_caps:
    max_same_topic: 10
    max_same_persona: 10
    max_same_arc_id: 10
  clustering:
    enabled: false
  anti_homogeneity:
    enabled: true
    min_score: 0.5
    weights:
      topic_diversity: 0.25
      persona_diversity: 0.25
      arc_diversity: 0.25
      band_shape_diversity: 0.25
      slot_diversity: 0.0
      variation_diversity: 0.0
""")
            for i in range(6):
                plan = _minimal_plan(
                    book_id=f"book_{i}",
                    topic_id=f"topic_{i % 3}",
                    persona_id=f"persona_{i % 2}",
                    arc_id=f"arc_{i}",
                    slot_sig=f"F006:sig{i}",
                    band_sig=f"2-3-{3 + (i % 2)}",
                )
                (plans_dir / f"p{i}.json").write_text(json.dumps(plan))

            result = check_release_wave(plans_dir, config)
        self.assertEqual(result.status, "PASS")
        self.assertGreaterEqual(result.anti_homogeneity_score, 0.5)

    def test_anti_homogeneity_score_too_low_fails(self):
        """Homogeneous wave → FAIL (score below threshold)."""
        from phoenix_v4.ops.check_release_wave import check_release_wave

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plans_dir = tmp_path / "plans"
            plans_dir.mkdir()
            config = tmp_path / "config.yaml"
            config.write_text("""
release_wave_controls:
  allow_legacy_plans: true
  weekly_caps:
    max_same_topic: 20
    max_same_persona: 20
    max_same_arc_id: 20
  clustering:
    enabled: false
  anti_homogeneity:
    enabled: true
    min_score: 0.62
    weights:
      topic_diversity: 0.25
      persona_diversity: 0.25
      arc_diversity: 0.25
      band_shape_diversity: 0.25
      slot_diversity: 0.0
      variation_diversity: 0.0
""")
            for i in range(8):
                plan = _minimal_plan(
                    book_id=f"book_{i}",
                    topic_id="anxiety",
                    persona_id="gen_z",
                    arc_id="same_arc",
                    slot_sig="F006:same",
                    band_sig="2-3-4-4-3",
                )
                (plans_dir / f"p{i}.json").write_text(json.dumps(plan))

            result = check_release_wave(plans_dir, config)
        self.assertEqual(result.status, "FAIL")
        codes = [v.code for v in result.violations]
        self.assertIn("ANTI_HOMOGENEITY_SCORE_TOO_LOW", codes)

    def test_legacy_plan_skipped_when_allow_legacy(self):
        """Plan missing arc_id and slot_sig (invalid) → skipped when allow_legacy_plans=true."""
        from phoenix_v4.ops.check_release_wave import check_release_wave, extract_wave_row

        # extract_wave_row returns None when no arc_id and no slot_sig
        bad_plan = {"plan_id": "x", "topic_id": "t", "persona_id": "p"}
        row = extract_wave_row(bad_plan, "x.json")
        self.assertIsNone(row)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            plans_dir = tmp_path / "plans"
            plans_dir.mkdir()
            config = tmp_path / "config.yaml"
            config.write_text("""
release_wave_controls:
  allow_legacy_plans: true
  weekly_caps: {}
  clustering:
    enabled: false
  anti_homogeneity:
    enabled: false
""")
            (plans_dir / "bad.json").write_text(json.dumps(bad_plan))
            good = _minimal_plan("g1", "anxiety", "gen_z", "arc1", "F006:s1", "2-3-4")
            (plans_dir / "good.json").write_text(json.dumps(good))

            result = check_release_wave(plans_dir, config)
        self.assertEqual(result.valid_plans, 1)
        self.assertEqual(result.total_plans, 2)
        self.assertTrue(any("missing required" in w.lower() for w in result.warnings))

    def test_wave_fingerprint_and_token_set(self):
        """Wave fingerprint and token set are deterministic and consistent."""
        from phoenix_v4.ops.check_release_wave import (
            WavePlanRow,
            token_set_for_near,
            wave_fingerprint,
        )

        row = WavePlanRow(
            book_id="b1",
            topic_id="t",
            persona_id="p",
            brand_id="phoenix",
            arc_id="arc1",
            engine_id="e1",
            slot_sig="F006:abc",
            band_sig="2-3-4",
            variation_signature="v1",
            teacher_id="",
            teacher_mode=False,
            exercise_chapters_sig="E:1,3",
            role_sig="r|d|f",
            chapter_count=6,
            raw={},
        )
        fp = wave_fingerprint(row)
        self.assertIn("arc1", fp)
        self.assertIn("F006:abc", fp)
        self.assertIn("2-3-4", fp)
        self.assertIn("v1", fp)
        tokens = token_set_for_near(row)
        self.assertIn("arc:arc1", tokens)
        self.assertIn("slot:F006:abc", tokens)
        self.assertIn("band:2-3-4", tokens)


if __name__ == "__main__":
    unittest.main()
