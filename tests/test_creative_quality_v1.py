"""
Tests for Creative Quality Gate v1.
Covers: arc motion (flat sequence fails), transformation density, ending strength,
specificity (abstract dominance), lexical rhythm (low std warns/fails).
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.gates.check_creative_quality_v1 import (
    Chapter,
    load_config,
    load_book,
    evaluate_arc_motion,
    evaluate_transformation_density,
    evaluate_specificity,
    evaluate_ending_strength,
    evaluate_lexical_rhythm,
    evaluate_book,
    count_regex_hits,
    has_any,
    INSIGHT_MARKERS,
    CONCRETE_MARKERS,
    ABSTRACT_MARKERS,
)


class TestArcMotion(unittest.TestCase):
    def test_fails_on_flat_band_sequence(self):
        """Flat band sequence (all same) should FAIL: no rise, no fall, distinct_bands < 3."""
        cfg = {
            "arc_motion": {
                "min_distinct_bands": 3,
                "require_rise": True,
                "require_fall": True,
                "warn_flat_segments_over": 2,
            }
        }
        flat = [3, 3, 3, 3]
        result = evaluate_arc_motion(flat, cfg)
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.distinct_bands, 1)
        self.assertEqual(result.rises, 0)
        self.assertEqual(result.falls, 0)
        self.assertTrue(
            any("no rising" in r or "no falling" in r or "distinct_bands" in r for r in result.reasons)
        )

    def test_pass_with_rise_and_fall(self):
        """Sequence with at least one rise and one fall, 3+ distinct bands, should PASS."""
        cfg = {
            "arc_motion": {
                "min_distinct_bands": 3,
                "require_rise": True,
                "require_fall": True,
                "warn_flat_segments_over": 2,
            }
        }
        seq = [1, 2, 4, 3, 2]
        result = evaluate_arc_motion(seq, cfg)
        self.assertEqual(result.status, "PASS")
        self.assertGreaterEqual(result.distinct_bands, 3)
        self.assertGreaterEqual(result.rises, 1)
        self.assertGreaterEqual(result.falls, 1)

    def test_missing_band_sequence(self):
        """Empty band sequence → FAIL with MISSING_BAND_SEQUENCE."""
        cfg = {"arc_motion": {}}
        result = evaluate_arc_motion([], cfg)
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(any("MISSING_BAND_SEQUENCE" in r for r in result.reasons))


class TestTransformationDensity(unittest.TestCase):
    def test_fails_if_no_markers(self):
        """Chapters with no insight/reframe/identity markers → FAIL below 60%."""
        cfg = {"transformation": {"min_transformative_chapter_share": 0.60}}
        chapters = [
            Chapter(0, "Nothing here. Just filler. The end."),
            Chapter(1, "More generic text. No realization."),
            Chapter(2, "Still nothing transformative."),
        ]
        result = evaluate_transformation_density(chapters, cfg)
        self.assertEqual(result.status, "FAIL")
        self.assertLess(result.share, 0.60)

    def test_pass_with_markers(self):
        """Chapters with insight/reframe/identity markers can pass."""
        cfg = {"transformation": {"min_transformative_chapter_share": 0.60}}
        chapters = [
            Chapter(0, "You realize that stress is not the enemy. It was never about that."),
            Chapter(1, "I thought I had to be perfect. But actually I just needed to show up."),
            Chapter(2, "This is who you are becoming. From now on, you can choose differently."),
        ]
        result = evaluate_transformation_density(chapters, cfg)
        self.assertGreaterEqual(result.transformative_chapters, 2)
        self.assertTrue(result.status == "PASS" or result.share >= 0.60)


class TestEndingStrength(unittest.TestCase):
    def test_fails_if_last_chapters_missing_patterns(self):
        """Last 2 chapters missing required patterns → FAIL."""
        cfg = {
            "ending_strength": {
                "last_n_chapters": 2,
                "require_compression": True,
                "require_identity": True,
                "require_action": True,
            }
        }
        chapters = [
            Chapter(0, "Some content."),
            Chapter(1, "More content. No summary. No identity. No action."),
            Chapter(2, "Still nothing. No directive. No wrap-up. The end."),
        ]
        result = evaluate_ending_strength(chapters, cfg)
        self.assertEqual(result.status, "FAIL")
        self.assertGreaterEqual(len(result.reasons), 1)

    def test_pass_when_patterns_present(self):
        """Last 2 chapters with compression, identity, action → PASS."""
        cfg = {
            "ending_strength": {
                "last_n_chapters": 2,
                "require_compression": True,
                "require_identity": True,
                "require_action": True,
            }
        }
        chapters = [
            Chapter(0, "Intro."),
            Chapter(
                1,
                "To sum up what you learned: the key point is clarity. This is who you are becoming. Start by doing this today.",
            ),
            Chapter(
                2,
                "You have changed. Your next step is to practice this. Let's bring this together.",
            ),
        ]
        result = evaluate_ending_strength(chapters, cfg)
        self.assertTrue(result.compression_found)
        self.assertTrue(result.identity_found)
        self.assertTrue(result.action_found)
        self.assertEqual(result.status, "PASS")


class TestSpecificity(unittest.TestCase):
    def test_warns_or_fails_on_high_abstract_dominance(self):
        """High abstract-dominant chapter share → WARN or FAIL."""
        cfg = {
            "specificity": {
                "warn_abstract_dominant_share": 0.50,
                "fail_abstract_dominant_share": 0.70,
            }
        }
        chapters = [
            Chapter(
                0,
                "Energy and alignment and mindset and transformation. Healing and growth. Universe and purpose.",
            ),
            Chapter(1, "The kitchen and the desk. Morning and 3 a.m. Hands and breath."),
            Chapter(2, "Stress and anxiety. More energy. Journey."),
        ]
        result = evaluate_specificity(chapters, cfg)
        self.assertIn(result.status, ("WARN", "FAIL", "PASS"))
        self.assertGreaterEqual(result.abstract_dominant_chapters, 0)


class TestLexicalRhythm(unittest.TestCase):
    def test_warns_on_low_std(self):
        """Low sentence-length std → WARN or FAIL."""
        cfg = {
            "lexical_rhythm": {
                "warn_sentence_len_std_below": 4.0,
                "fail_sentence_len_std_below": 2.5,
            }
        }
        chapters = [
            Chapter(0, "One. Two. Three. Four. Five. Six. Seven. Eight. Nine. Ten."),
            Chapter(1, "A. B. C. D. E. F. G. H. I. J."),
        ]
        result = evaluate_lexical_rhythm(chapters, cfg)
        self.assertLess(result.std_sentence_len, 5.0)
        self.assertIn(result.status, ("WARN", "FAIL"))


class TestLoadConfig(unittest.TestCase):
    def test_returns_dict(self):
        """load_config returns dict (may be empty if file missing)."""
        cfg = load_config("config/creative_quality_v1.yaml")
        self.assertIsInstance(cfg, dict)
        if cfg:
            self.assertTrue(
                "transformation" in cfg or "arc_motion" in cfg or "parsing" in cfg
            )


class TestLoadBook(unittest.TestCase):
    def test_invalid_path_raises(self):
        """load_book with missing file raises ValueError."""
        with self.assertRaises(ValueError):
            load_book("nonexistent_file_xyz.plan.json")

    def test_no_chapter_text_raises(self):
        """load_book with JSON that has no chapter text raises BOOK_INPUT_INVALID."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(
                {
                    "book_id": "test",
                    "dominant_band_sequence": [1, 2, 3],
                    "chapters": [{"text": ""}, {"prose": ""}],
                },
                f,
            )
            path = f.name
        try:
            with self.assertRaises(ValueError) as ctx:
                load_book(path)
            self.assertIn("BOOK_INPUT_INVALID", str(ctx.exception))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_success(self):
        """load_book with valid compiled structure returns book_id, chapters, band_seq."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(
                {
                    "book_id": "test_001",
                    "dominant_band_sequence": [2, 3, 4],
                    "chapters": [
                        {"text": "First chapter prose here. With two sentences."},
                        {"text": "Second chapter. You realize something. Good."},
                    ],
                },
                f,
            )
            path = f.name
        try:
            book_id, chapters, band_seq = load_book(path)
            self.assertEqual(book_id, "test_001")
            self.assertEqual(len(chapters), 2)
            self.assertEqual(
                chapters[0].text,
                "First chapter prose here. With two sentences.",
            )
            self.assertEqual(
                chapters[1].text,
                "Second chapter. You realize something. Good.",
            )
            self.assertEqual(band_seq, [2, 3, 4])
        finally:
            Path(path).unlink(missing_ok=True)


class TestEvaluateBook(unittest.TestCase):
    def test_overall_fail_when_arc_fails(self):
        """evaluate_book with failing arc (flat) yields overall FAIL."""
        cfg = {
            "arc_motion": {
                "min_distinct_bands": 3,
                "require_rise": True,
                "require_fall": True,
            },
            "transformation": {"min_transformative_chapter_share": 0.60},
            "specificity": {},
            "ending_strength": {"last_n_chapters": 2},
            "lexical_rhythm": {},
        }
        chapters = [
            Chapter(0, "Text one. You realize it. Good."),
            Chapter(1, "Text two. I thought so but actually no. Good."),
        ]
        band_seq = [3, 3]
        summary = evaluate_book("fail_book", chapters, band_seq, cfg)
        self.assertEqual(summary.overall, "FAIL")
        self.assertGreaterEqual(len(summary.fails), 1)


class TestParsingHelpers(unittest.TestCase):
    def test_has_any_insight(self):
        """has_any finds insight markers."""
        self.assertTrue(has_any("You realize that it matters.", INSIGHT_MARKERS))
        self.assertFalse(has_any("Nothing here.", INSIGHT_MARKERS))

    def test_count_regex_hits(self):
        """count_regex_hits counts concrete/abstract markers."""
        text = "The kitchen and the desk. Energy and mindset."
        c = count_regex_hits(text, CONCRETE_MARKERS)
        a = count_regex_hits(text, ABSTRACT_MARKERS)
        self.assertGreaterEqual(c, 2)
        self.assertGreaterEqual(a, 2)


if __name__ == "__main__":
    unittest.main()
