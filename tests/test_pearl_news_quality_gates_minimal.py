"""Minimal tests for Pearl News quality gates (fail-hard, blocklist, qc_results)."""
from __future__ import annotations

import pytest

from pearl_news.pipeline.quality_gates import run_quality_gates


def test_run_quality_gates_adds_qc_results():
    """run_quality_gates adds qc_results and qc_passed to each item."""
    items = [
        {"id": "a", "title": "Test", "content": "Content with youth and SDG.", "url": "https://un.org/news/1"},
    ]
    result = run_quality_gates(items)
    assert len(result) == 1
    assert "qc_results" in result[0]
    assert "qc_passed" in result[0]
    assert result[0]["qc_results"]["fact_check_completeness"] in ("PASS", "FAIL")
    assert result[0]["qc_results"]["un_endorsement_detector"] in ("PASS", "FAIL")
    assert result[0]["qc_results"]["writer_spec_forbidden_phrases"] in ("PASS", "FAIL")


def test_blocklist_fails_gate():
    """Blocklist phrase in content causes sdg_un_accuracy and un_endorsement_detector FAIL."""
    items = [
        {"id": "b", "title": "UN partner story", "content": "We are UN partner in this.", "url": "https://example.com/1"},
    ]
    result = run_quality_gates(items)
    assert result[0]["qc_results"]["sdg_un_accuracy"] == "FAIL"
    assert result[0]["qc_results"]["un_endorsement_detector"] == "FAIL"
    assert result[0]["qc_passed"] is False


def test_clean_content_passes():
    """Clean content with source, youth relevance, and at least one anchor (Writer Spec §7) passes all gates."""
    items = [
        {
            "id": "c",
            "title": "Climate and youth",
            "content": (
                "In a 2024 UNICEF survey, 68% of Gen Z respondents cited climate as a top concern. "
                "Young people in Japan and elsewhere are affected. Source: https://news.un.org/feed."
            ),
            "url": "https://news.un.org/item",
        },
    ]
    result = run_quality_gates(items)
    assert result[0]["qc_passed"] is True


def test_generic_youth_phrase_fails_specificity_gate():
    """Writer Spec §11: generic youth impact without anchor fails youth_impact_specificity."""
    items = [
        {
            "id": "d",
            "title": "Global update",
            "content": (
                "Young people are increasingly affected by global events in this area. "
                "Gen Z and Gen Alpha seek clarity. Source: https://news.un.org/feed."
            ),
            "url": "https://news.un.org/item",
        },
    ]
    result = run_quality_gates(items)
    assert result[0]["qc_results"]["youth_impact_specificity"] == "FAIL"
    assert result[0]["qc_results"]["writer_spec_forbidden_phrases"] == "FAIL"
    assert result[0]["qc_passed"] is False


def test_forbidden_phrase_fails_writer_spec_gate():
    """Writer Spec §11: 'Now more than ever' (or similar) anywhere in article fails writer_spec_forbidden_phrases."""
    items = [
        {
            "id": "e",
            "title": "Climate and youth",
            "content": (
                "In a 2024 UNICEF survey, 68% of Gen Z cited climate as a top concern. "
                "Now more than ever, young people are engaged. Source: https://news.un.org/feed."
            ),
            "url": "https://news.un.org/item",
        },
    ]
    result = run_quality_gates(items)
    assert result[0]["qc_results"]["writer_spec_forbidden_phrases"] == "FAIL"
    assert result[0]["qc_passed"] is False
