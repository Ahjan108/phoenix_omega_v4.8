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

    def test_peace_conflict_to_interfaith(self):
        items = [{"id": "1", "topic": "peace_conflict"}]
        result = select_templates(items)
        assert result[0]["template_id"] == "interfaith_dialogue_report"

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
