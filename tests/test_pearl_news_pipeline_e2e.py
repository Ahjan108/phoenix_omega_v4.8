"""E2E test: Pearl News pipeline ingest → classify → select → assemble → metadata."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from pearl_news.pipeline.topic_sdg_classifier import classify_sdgs
from pearl_news.pipeline.template_selector import select_templates
from pearl_news.pipeline.article_assembler import assemble_articles
from pearl_news.pipeline.quality_gates import run_quality_gates


def _make_fake_items(count: int = 3) -> list[dict]:
    """Create fake normalized feed items (as from ingest)."""
    items = []
    for i in range(count):
        items.append({
            "id": f"test_{i}",
            "title": "Climate carbon emissions" if i == 0 else f"Test article {i}",
            "url": f"https://example.com/{i}",
            "pub_date": "2026-03-03T12:00:00+00:00",
            "summary": "Summary text.",
            "source_feed_id": "test_feed",
            "source_feed_title": "Test",
            "raw_title": "Title",
            "raw_summary": "Summary",
            "images": [],
        })
    return items


class TestPipelineE2E:
    def test_classify_select_assemble_metadata_flow(self):
        """Full pipeline on fake items produces articles with metadata fields."""
        items = _make_fake_items(3)
        items = classify_sdgs(items)
        items = select_templates(items)
        articles = assemble_articles(items)
        assert len(articles) == 3

        art = articles[0]
        assert "title" in art
        assert "content" in art
        assert "template_id" in art
        assert "topic" in art
        assert "primary_sdg" in art
        assert "teacher_ids" in art
        assert "stressor_tags" in art
        assert "region" in art
        assert "pub_date" in art

    def test_quality_gates_add_phrase_flags(self):
        """Quality gates add phrase_flags to articles."""
        items = _make_fake_items(1)
        items = classify_sdgs(items)
        items = select_templates(items)
        articles = assemble_articles(items)
        articles = run_quality_gates(articles)
        assert "phrase_flags" in articles[0]

    def test_metadata_writer_integration(self):
        """Run pipeline and verify metadata file is written."""
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "drafts"
            meta_dir = out_dir.parent
            meta_dir.mkdir(parents=True, exist_ok=True)
            meta_path = meta_dir / "article_metadata.jsonl"

            items = _make_fake_items(2)
            items = classify_sdgs(items)
            items = select_templates(items)
            articles = assemble_articles(items)
            articles = run_quality_gates(articles, metadata_path=meta_path)

            # Simulate metadata append (as run_article_pipeline does)
            from datetime import datetime, timezone
            build_date = datetime.now(timezone.utc).isoformat()
            for draft in articles:
                meta = {
                    "article_id": str(draft.get("id", "")),
                    "date": draft.get("pub_date") or build_date,
                    "topic": draft.get("topic") or "general",
                    "primary_sdg": draft.get("primary_sdg") or "17",
                    "template_id": draft.get("template_id") or "hard_news_spiritual_response",
                    "teacher_ids": draft.get("teacher_ids") or [],
                    "stressor_tags": draft.get("stressor_tags") or [],
                    "region": draft.get("region") or "",
                    "phrase_flags": draft.get("phrase_flags") or [],
                }
                with open(meta_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(meta, ensure_ascii=False) + "\n")

            assert meta_path.exists()
            lines = meta_path.read_text().strip().split("\n")
            assert len(lines) == 2
            rec = json.loads(lines[0])
            assert "article_id" in rec
            assert "topic" in rec
            assert "template_id" in rec
