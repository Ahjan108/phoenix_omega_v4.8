"""Tests for Pearl News template_selector: topic→template, unknown fallback."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from pearl_news.pipeline.template_selector import select_templates


class TestTopicToTemplate:
    def test_mental_health_to_youth_feature(self):
        items = [{"id": "1", "topic": "mental_health"}]
        result = select_templates(items)
        assert result[0]["template_id"] == "youth_feature"

    def test_education_to_youth_feature(self):
        items = [{"id": "1", "topic": "education"}]
        result = select_templates(items)
        assert result[0]["template_id"] == "youth_feature"

    def test_climate_to_hard_news(self):
        items = [{"id": "1", "topic": "climate"}]
        result = select_templates(items)
        assert result[0]["template_id"] == "hard_news_spiritual_response"

    def test_peace_conflict_defaults_to_single_teacher_template(self):
        items = [{"id": "1", "topic": "peace_conflict"}]
        result = select_templates(items)
        # Current selector behavior uses single-teacher template by default and
        # only routes peace_conflict to interfaith/group style for a small ratio.
        assert result[0]["template_id"] == "hard_news_spiritual_response"

    def test_inequality_to_explainer(self):
        items = [{"id": "1", "topic": "inequality"}]
        result = select_templates(items)
        assert result[0]["template_id"] == "explainer_context"

    def test_general_to_hard_news(self):
        items = [{"id": "1", "topic": "general"}]
        result = select_templates(items)
        assert result[0]["template_id"] == "hard_news_spiritual_response"


class TestUnknownFallback:
    def test_unknown_topic_defaults_to_hard_news(self):
        items = [{"id": "1", "topic": "unknown_xyz"}]
        result = select_templates(items)
        assert result[0]["template_id"] == "hard_news_spiritual_response"

    def test_missing_topic_uses_general(self):
        items = [{"id": "1"}]
        result = select_templates(items)
        assert result[0]["template_id"] == "hard_news_spiritual_response"


class TestCustomMapping:
    def test_topic_to_template_override(self):
        items = [{"id": "1", "topic": "mental_health"}]
        override = {"mental_health": "explainer_context"}
        result = select_templates(items, topic_to_template=override)
        assert result[0]["template_id"] == "explainer_context"


class TestEqualMixBalancing:
    def test_equal_mix_for_10_items(self):
        items = [{"id": f"item_{i}", "topic": "mental_health"} for i in range(10)]
        result = select_templates(items)
        counts = {}
        for row in result:
            counts[row["template_id"]] = counts.get(row["template_id"], 0) + 1

        assert counts["hard_news_spiritual_response"] == 2
        assert counts["youth_feature"] == 2
        assert counts["interfaith_dialogue_report"] == 2
        assert counts["explainer_context"] == 2
        assert counts["commentary"] == 2
