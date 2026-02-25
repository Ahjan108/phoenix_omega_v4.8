"""
Regression tests: malformed CANONICAL.txt, missing chapter text in plan, duplicate memorable-line collisions.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TestMalformedCanonical(unittest.TestCase):
    """Malformed CANONICAL.txt: no valid ## ROLE vNN blocks → ValueError or MALFORMED_CANONICAL in lint result."""

    def test_parse_canonical_blocks_raises_on_empty(self):
        from phoenix_v4.quality.base import parse_canonical_blocks
        with self.assertRaises(ValueError) as ctx:
            parse_canonical_blocks("")
        self.assertIn("No atom blocks", str(ctx.exception))

    def test_parse_canonical_blocks_raises_on_no_valid_blocks(self):
        from phoenix_v4.quality.base import parse_canonical_blocks
        text = "just some prose\n\nno headers here\n"
        with self.assertRaises(ValueError) as ctx:
            parse_canonical_blocks(text)
        self.assertIn("No atom blocks", str(ctx.exception))

    def test_parse_canonical_blocks_from_path_raises_on_malformed_file(self):
        from phoenix_v4.quality.base import parse_canonical_blocks_from_path
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            # No valid ## ROLE vNN blocks → ValueError (no blocks or malformed).
            f.write("## bad header\n---\n---\nbody\n")
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError) as ctx:
                parse_canonical_blocks_from_path(path)
            msg = str(ctx.exception)
            self.assertTrue(
                "malformed" in msg.lower() or "No atom blocks" in msg,
                f"Expected malformed or no blocks message, got: {msg}",
            )
        finally:
            path.unlink(missing_ok=True)

    def test_story_atom_lint_includes_malformed_canonical_flag(self):
        from phoenix_v4.quality.story_atom_lint import lint_canonical_file
        with tempfile.TemporaryDirectory() as d:
            canonical = Path(d) / "CANONICAL.txt"
            canonical.write_text("no blocks at all\n", encoding="utf-8")
            # lint_canonical_file raises ValueError on malformed; CLI catches and adds MALFORMED_CANONICAL result.
            # We test the parser contract; for lint we need to go through the CLI or the code path that catches ValueError.
            from phoenix_v4.quality.base import parse_canonical_blocks_from_path
            with self.assertRaises(ValueError):
                parse_canonical_blocks_from_path(canonical)
        # Direct lint_canonical_file also raises:
        with tempfile.TemporaryDirectory() as d:
            canonical = Path(d) / "CANONICAL.txt"
            canonical.write_text("no blocks", encoding="utf-8")
            with self.assertRaises(ValueError):
                lint_canonical_file(canonical)


class TestMissingChapterTextInPlan(unittest.TestCase):
    """Plan JSON without compiled_book.chapters[].text → detector raises ValueError with clear message."""

    def test_memorable_line_detector_raises_on_plan_without_chapter_text(self):
        from phoenix_v4.quality.memorable_line_detector import load_chapters_from_plan
        plan_without_text = {
            "compiled_book": {
                "chapters": [{"title": "Ch1"}, {"title": "Ch2"}],
            },
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(plan_without_text, f)
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_chapters_from_plan(path)
            msg = str(ctx.exception)
            self.assertTrue(
                "PLAN_INPUT_INVALID" in msg or "no chapter text" in msg or "chapter text" in msg.lower(),
                f"Expected message about chapter text, got: {msg}",
            )
        finally:
            path.unlink(missing_ok=True)

    def test_memorable_line_detector_raises_on_empty_chapters(self):
        from phoenix_v4.quality.memorable_line_detector import load_chapters_from_plan
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"compiled_book": {"chapters": []}}, f)
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError) as ctx:
                load_chapters_from_plan(path)
            self.assertIn("no chapter text", str(ctx.exception).lower())
        finally:
            path.unlink(missing_ok=True)


class TestDuplicateMemorableLineCollision(unittest.TestCase):
    """Same memorable line in two books in one wave → check_memorable_line_registry reports per_wave violation."""

    def test_check_violations_per_wave_duplicate(self):
        from phoenix_v4.ops.check_memorable_line_registry import check_violations, load_policy
        from phoenix_v4.ops.memorable_line_registry import line_hash, normalize_line
        norm = normalize_line("You are not your thoughts.")
        h = line_hash(norm)
        snapshot = {
            "schema_version": "1.0",
            "lines": [
                {
                    "line_hash": h,
                    "normalized_text": norm,
                    "occurrence_count": 2,
                    "books": ["book_001", "book_002"],
                    "strength_max": "good",
                },
            ],
        }
        policy = load_policy()
        wave_book_ids = ["book_001", "book_002"]
        violations = check_violations(snapshot, wave_book_ids, policy)
        per_wave = [v for v in violations if v.get("scope") == "per_wave"]
        self.assertGreater(len(per_wave), 0, "Expected at least one per_wave violation (same line in 2 books in wave)")
        self.assertTrue(
            any("wave" in (v.get("reason") or "").lower() for v in per_wave),
            f"Expected reason to mention wave; got {[v.get('reason') for v in per_wave]}",
        )


if __name__ == "__main__":
    unittest.main()
