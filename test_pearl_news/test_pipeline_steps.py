"""Tests for Pearl News pipeline steps: classifier, template selector, assembler, quality gates, qc."""
from __future__ import annotations

import pytest
from pearl_news.pipeline.topic_sdg_classifier import classify_sdgs
from pearl_news.pipeline.template_selector import select_templates
from pearl_news.pipeline.article_assembler import assemble_articles
from pearl_news.pipeline.quality_gates import run_quality_gates, filter_passed
from pearl_news.pipeline.qc_checklist import run_qc_checklist, filter_checklist_passed


@pytest.fixture
def sample_items():
    return [
        {
            "id": "abc123",
            "title": "Climate summit addresses carbon emissions",
            "summary": "Leaders meet to discuss climate action.",
            "url": "https://example.com/1",
            "source_feed_id": "un_news",
            "source_feed_title": "UN News",
            "images": [{"url": "https://example.com/img.jpg", "credit": "UN"}],
        },
        {
            "id": "def456",
            "title": "Mental health support for students",
            "summary": "Schools expand wellbeing programs.",
            "url": "https://example.com/2",
            "source_feed_id": "un_news",
            "images": [],
        },
    ]


def test_classify_sdgs(sample_items):
    out = classify_sdgs(sample_items)
    assert len(out) == 2
    assert out[0]["topic"] == "climate"
    assert out[0]["primary_sdg"] == "13"
    assert out[1]["topic"] == "mental_health"
    assert out[1]["primary_sdg"] == "3"


def test_select_templates(sample_items):
    classified = classify_sdgs(sample_items)
    out = select_templates(classified)
    assert out[0]["template_id"] == "hard_news_spiritual_response"
    assert out[1]["template_id"] == "youth_feature"


def test_assemble_articles(sample_items):
    classified = classify_sdgs(sample_items)
    selected = select_templates(classified)
    articles = assemble_articles(selected)
    assert len(articles) == 2
    assert "title" in articles[0]
    assert "content" in articles[0]
    assert "featured_image" in articles[0]
    assert articles[0]["featured_image"]["url"] == "https://example.com/img.jpg"
    assert "SDG 13" in articles[0]["content"] or "Climate Action" in articles[0]["content"]


def test_quality_gates_pass():
    items = [{"title": "Test", "content": "Normal article text."}]
    out = run_quality_gates(items)
    assert out[0]["qc_passed"] is True
    assert out[0]["qc_failed"] is False


def test_quality_gates_blocklist():
    items = [{"title": "Test", "content": "We are a UN partner in this project."}]
    out = run_quality_gates(items)
    assert out[0]["qc_passed"] is False
    assert "UN partner" in (out[0].get("qc_fail_reason") or "")


def test_filter_passed():
    items = [
        {"qc_passed": True, "qc_failed": False},
        {"qc_passed": False, "qc_failed": True},
    ]
    assert len(filter_passed(items)) == 1


def test_qc_checklist():
    items = [{"title": "Test", "content": "Body"}]
    out = run_qc_checklist(items)
    assert out[0]["qc_checklist_passed"] is True


def test_qc_checklist_fail_missing_title():
    items = [{"title": "", "content": "Body"}]
    out = run_qc_checklist(items)
    assert out[0]["qc_checklist_passed"] is False
    assert "Missing title" in (out[0].get("qc_checklist_notes") or [])


def test_full_pipeline_chain(sample_items):
    classified = classify_sdgs(sample_items)
    selected = select_templates(classified)
    articles = assemble_articles(selected)
    gated = run_quality_gates(articles)
    qc = run_qc_checklist(gated)
    passed = filter_checklist_passed(filter_passed(qc))
    assert len(passed) >= 1
    assert all("title" in a and "content" in a for a in passed)
