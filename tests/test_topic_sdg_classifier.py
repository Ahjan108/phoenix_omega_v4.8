"""Tests for Pearl News topic_sdg_classifier: keyword→topic, topic→SDG, fallback."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from pearl_news.pipeline.topic_sdg_classifier import classify_sdgs


class TestKeywordToTopic:
    def test_climate_keywords(self):
        items = [{"title": "Carbon emissions rise", "summary": "Heat waves hit."}]
        result = classify_sdgs(items)
        assert len(result) == 1
        assert result[0]["topic"] == "climate"

    def test_mental_health_keywords(self):
        items = [{"title": "Youth anxiety", "summary": "Mental health crisis."}]
        result = classify_sdgs(items)
        assert result[0]["topic"] == "mental_health"

    def test_education_keywords(self):
        items = [{"title": "Student learning", "summary": "School reforms."}]
        result = classify_sdgs(items)
        assert result[0]["topic"] == "education"

    def test_peace_conflict_keywords(self):
        items = [{"title": "Refugee crisis", "summary": "Peace talks."}]
        result = classify_sdgs(items)
        assert result[0]["topic"] == "peace_conflict"

    def test_economy_keywords(self):
        items = [{"title": "Youth unemployment", "summary": "Job market."}]
        result = classify_sdgs(items)
        assert result[0]["topic"] == "economy_work"


class TestTopicToSdg:
    def test_climate_maps_to_sdg13(self):
        items = [{"title": "Climate carbon", "summary": ""}]
        result = classify_sdgs(items)
        assert result[0]["primary_sdg"] == "13"
        assert "13" in result[0].get("sdg_labels", {})

    def test_mental_health_maps_to_sdg3(self):
        items = [{"title": "Anxiety depression", "summary": ""}]
        result = classify_sdgs(items)
        assert result[0]["primary_sdg"] == "3"

    def test_education_maps_to_sdg4(self):
        items = [{"title": "School student", "summary": ""}]
        result = classify_sdgs(items)
        assert result[0]["primary_sdg"] == "4"


class TestFallback:
    def test_unknown_topic_fallback_to_general(self):
        items = [{"title": "Random xyz abc", "summary": "No keywords."}]
        result = classify_sdgs(items)
        assert result[0]["topic"] == "general"

    def test_general_maps_to_sdg17(self):
        items = [{"title": "Random", "summary": ""}]
        result = classify_sdgs(items)
        assert result[0]["primary_sdg"] == "17"
        assert result[0]["topic"] == "general"

    def test_un_body_present(self):
        items = [{"title": "Climate", "summary": ""}]
        result = classify_sdgs(items)
        assert "un_body" in result[0]
        assert result[0]["un_body"]


class TestCustomConfig:
    def test_custom_mapping_path(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
topic_to_sdg:
  custom_topic:
    primary_sdg: "1"
    sdg_labels: {"1": "No Poverty"}
    un_body: "UN"
keyword_to_topic:
  - keywords: ["custom"]
    topic: custom_topic
""")
            path = Path(f.name)
        try:
            items = [{"title": "Custom story", "summary": ""}]
            result = classify_sdgs(items, config_path=path)
            assert result[0]["topic"] == "custom_topic"
            assert result[0]["primary_sdg"] == "1"
        finally:
            path.unlink(missing_ok=True)
