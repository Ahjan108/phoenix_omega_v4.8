"""Tests for Pearl News quality gates: phrase repetition, teacher saturation, template rotation."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from pearl_news.pipeline.quality_gates import (
    check_teacher_saturation,
    check_template_rotation,
    check_transition_phrase_repetition,
    run_quality_gates,
    filter_passed,
)


class TestCheckTransitionPhraseRepetition:
    def test_empty_text(self):
        assert check_transition_phrase_repetition("") == []
        assert check_transition_phrase_repetition(None) == []

    def test_finds_phrases(self):
        text = "Now, let's discuss youth mental health. With that said, we continue."
        found = check_transition_phrase_repetition(text)
        assert "Now, let's" in found
        assert "With that said" in found
        assert "youth mental health" in found

    def test_case_insensitive(self):
        assert "spiritual leaders" in check_transition_phrase_repetition("SPIRITUAL LEADERS gather")

    def test_no_match(self):
        assert check_transition_phrase_repetition("Clean content with no flags.") == []


class TestCheckTeacherSaturation:
    def test_empty_teachers_passes(self):
        ok, reason = check_teacher_saturation([{"teacher_ids": ["A"] * 10}], [], window=20, cap=0.30)
        assert ok
        assert reason is None

    def test_under_cap_passes(self):
        history = [{"teacher_ids": ["A"]} for _ in range(15)] + [{"teacher_ids": ["B"]} for _ in range(5)]
        ok, reason = check_teacher_saturation(history, ["A"], window=20, cap=0.30)
        assert ok

    def test_over_cap_fails(self):
        history = [{"teacher_ids": ["A"]} for _ in range(15)]
        ok, reason = check_teacher_saturation(history, ["A", "A", "A", "A", "A"], window=20, cap=0.30)
        assert not ok
        assert "A" in (reason or "")

    def test_empty_history_passes(self):
        ok, reason = check_teacher_saturation([], ["A"], window=20, cap=0.30)
        assert ok


class TestCheckTemplateRotation:
    def test_no_repeat_passes(self):
        history = [{"template_id": "A"}, {"template_id": "B"}, {"template_id": "A"}]
        ok, reason = check_template_rotation(history, "B", max_consecutive=3)
        assert ok

    def test_four_consecutive_fails(self):
        history = [{"template_id": "A"}, {"template_id": "A"}, {"template_id": "A"}]
        ok, reason = check_template_rotation(history, "A", max_consecutive=3)
        assert not ok
        assert "A" in (reason or "")

    def test_three_consecutive_passes(self):
        history = [{"template_id": "A"}, {"template_id": "A"}]
        ok, reason = check_template_rotation(history, "A", max_consecutive=3)
        assert ok


class TestRunQualityGates:
    def test_adds_phrase_flags(self):
        items = [{"title": "Test", "content": "Now, let's begin.", "template_id": "hard_news"}]
        result = run_quality_gates(items)
        assert len(result) == 1
        assert "phrase_flags" in result[0]
        assert "Now, let's" in result[0]["phrase_flags"]

    def test_blocklist_still_enforced(self):
        items = [{"title": "UN partner story", "content": "Content", "template_id": "hard_news"}]
        result = run_quality_gates(items)
        assert result[0]["qc_failed"]
        assert "Blocklist" in (result[0].get("qc_fail_reason") or "")

    def test_metadata_path_teacher_saturation(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for _ in range(20):
                f.write(json.dumps({"teacher_ids": ["MasterWu"], "template_id": "youth"}) + "\n")
            path = Path(f.name)
        try:
            items = [
                {"title": "OK", "content": "Clean.", "template_id": "hard_news", "teacher_ids": []},
                {"title": "Saturated", "content": "Clean.", "template_id": "hard_news", "teacher_ids": ["MasterWu"]},
            ]
            result = run_quality_gates(items, metadata_path=path)
            assert result[0]["qc_passed"]
            assert result[1]["qc_failed"]
            assert "MasterWu" in (result[1].get("qc_fail_reason") or "")
        finally:
            path.unlink(missing_ok=True)


class TestFilterPassed:
    def test_filters_failed(self):
        items = [
            {"qc_passed": True, "qc_failed": False},
            {"qc_passed": False, "qc_failed": True},
        ]
        assert len(filter_passed(items)) == 1
