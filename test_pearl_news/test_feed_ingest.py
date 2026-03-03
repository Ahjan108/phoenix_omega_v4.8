"""
Tests for Pearl News feed ingest: RSS parsing, image extraction, attribution.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from pearl_news.pipeline.feed_ingest import (
    _extract_images_from_entry,
    _first_img_url_from_html,
    _image_content_type,
    ingest_feeds,
    load_feed_config,
)


def test_load_feed_config_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_feed_config(Path("/nonexistent/feeds.yaml"))


def test_load_feed_config_empty_file() -> None:
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        f.write(b"feeds: []\n")
        path = f.name
    try:
        config = load_feed_config(path)
        assert config == []
    finally:
        Path(path).unlink(missing_ok=True)


def test_image_content_type() -> None:
    assert _image_content_type("image/jpeg") is True
    assert _image_content_type("image/png") is True
    assert _image_content_type("IMAGE/PNG") is True
    assert _image_content_type("application/xml") is False
    assert _image_content_type("") is False


def test_first_img_url_from_html() -> None:
    assert _first_img_url_from_html('<img src="https://example.com/a.jpg">') == "https://example.com/a.jpg"
    assert _first_img_url_from_html('<img alt="x" src="https://a.b/c.png" />') == "https://a.b/c.png"
    assert _first_img_url_from_html("<p>No image</p>") is None
    assert _first_img_url_from_html("") is None


class _MockEntry:
    def __init__(self, link="https://news.example/item", title="Item", **kwargs):
        self.link = link
        self.title = title
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_extract_images_from_entry_enclosure() -> None:
    entry = _MockEntry(enclosures=[{"href": "https://cdn.example/img.jpg", "type": "image/jpeg"}])
    images = _extract_images_from_entry(entry, "feed1", "Example News", "https://news.example/item")
    assert len(images) == 1
    assert images[0]["url"] == "https://cdn.example/img.jpg"
    assert images[0]["credit"] == "Example News"
    assert images[0]["source_url"] == "https://news.example/item"


def test_extract_images_from_entry_media_thumbnail() -> None:
    entry = _MockEntry(media_thumbnail=[{"url": "https://thumb.example/t.jpg"}])
    images = _extract_images_from_entry(entry, "f", "Feed", "https://link")
    assert len(images) >= 1
    assert any(i["url"] == "https://thumb.example/t.jpg" for i in images)


def test_extract_images_from_entry_img_in_summary() -> None:
    entry = _MockEntry(
        summary='<p>Text</p><img src="https://inline.example/pic.png" />',
    )
    images = _extract_images_from_entry(entry, "f", "Feed", "https://link")
    assert any("pic.png" in (i.get("url") or "") for i in images)


def test_ingest_feeds_no_feeds(tmp_path: Path) -> None:
    pytest.importorskip("feedparser")
    feeds = tmp_path / "feeds.yaml"
    feeds.write_text("feeds: []\n", encoding="utf-8")
    items = ingest_feeds(feeds, limit=5)
    assert items == []


@pytest.mark.network
def test_ingest_feeds_real_rss() -> None:
    """Fetch real UN News RSS; checks that we get items and optional images."""
    root = Path(__file__).resolve().parents[2]
    feeds_path = root / "pearl_news" / "config" / "feeds.yaml"
    if not feeds_path.exists():
        pytest.skip("pearl_news/config/feeds.yaml not found")
    items = ingest_feeds(feeds_path, limit=3, per_feed_limit=3)
    assert len(items) >= 1
    for item in items:
        assert "id" in item
        assert "title" in item
        assert "url" in item
        assert "source_feed_id" in item
        assert "images" in item
        assert isinstance(item["images"], list)
