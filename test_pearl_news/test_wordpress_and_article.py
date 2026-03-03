"""
Tests for Pearl News WordPress client (dry-run / env) and article draft with featured_image.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pearl_news.publish.wordpress_client import (
    WordPressPublishError,
    _get_credentials,
    _normalize_site_url,
    post_article,
)


def test_get_credentials_missing() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(WordPressPublishError) as exc_info:
            _get_credentials()
        assert "WORDPRESS" in str(exc_info.value)


def test_get_credentials_ok() -> None:
    with patch.dict(
        os.environ,
        {
            "WORDPRESS_SITE_URL": "https://example.org",
            "WORDPRESS_USERNAME": "user",
            "WORDPRESS_APP_PASSWORD": "abcd efgh",
        },
        clear=False,
    ):
        site, user, pw = _get_credentials()
        assert site == "https://example.org"
        assert user == "user"
        assert pw == "abcdefgh"


def test_get_credentials_normalizes_missing_scheme() -> None:
    with patch.dict(
        os.environ,
        {
            "WORDPRESS_SITE_URL": "example.org/",
            "WORDPRESS_USERNAME": "user",
            "WORDPRESS_APP_PASSWORD": "abcd efgh",
        },
        clear=False,
    ):
        site, user, pw = _get_credentials()
        assert site == "https://example.org"
        assert user == "user"
        assert pw == "abcdefgh"


def test_normalize_site_url_invalid() -> None:
    with pytest.raises(WordPressPublishError):
        _normalize_site_url("://bad_url")


def test_post_article_with_featured_image_mock() -> None:
    """Test that article with featured_image triggers upload then post (mock requests)."""
    with patch("pearl_news.publish.wordpress_client.requests") as mreq:
        # Image download
        mreq.get.return_value.ok = True
        mreq.get.return_value.content = b"\xff\xd8\xff"
        mreq.get.return_value.raise_for_status = lambda: None
        # Media upload response
        mreq.post.return_value.ok = True
        mreq.post.return_value.json.side_effect = [{"id": 99}, {"id": 1, "title": "Test"}]
        with patch.dict(
            os.environ,
            {
                "WORDPRESS_SITE_URL": "https://example.org",
                "WORDPRESS_USERNAME": "u",
                "WORDPRESS_APP_PASSWORD": "p",
            },
            clear=False,
        ):
            result = post_article(
                title="Test",
                content="<p>Body</p>",
                featured_image={"url": "https://example.com/img.jpg", "credit": "UN News", "source_url": "https://un.org"},
            )
            assert result["id"] == 1
            assert mreq.get.called
            assert mreq.post.call_count >= 2  # media upload (+ optional PATCH), then create post


def test_article_json_with_featured_image(tmp_path: Path) -> None:
    """Article JSON with featured_image has expected keys for post script."""
    article = {
        "title": "Headline",
        "content": "<p>Body</p>",
        "featured_image": {
            "url": "https://news.un.org/img/123.jpg",
            "credit": "UN News",
            "source_url": "https://news.un.org/",
        },
    }
    path = tmp_path / "article.json"
    path.write_text(json.dumps(article, indent=2), encoding="utf-8")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("featured_image", {}).get("url") == "https://news.un.org/img/123.jpg"
    assert data["featured_image"]["credit"] == "UN News"
