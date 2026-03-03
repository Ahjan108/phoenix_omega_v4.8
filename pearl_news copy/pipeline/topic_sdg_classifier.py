"""
Pearl News — map feed items to topic and SDG(s) using sdg_news_topic_mapping.yaml.

Keyword matching only (no LLM). Adds: topic, primary_sdg, sdg_labels, un_body to each item.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


def _load_mapping(config_path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required; pip install pyyaml")
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def _text_for_matching(item: dict[str, Any]) -> str:
    """Combine title and summary for keyword search."""
    parts = [
        item.get("title") or "",
        item.get("raw_title") or "",
        item.get("summary") or "",
        item.get("raw_summary") or "",
    ]
    return " ".join(str(p) for p in parts).lower()


def _match_topic(text: str, keyword_to_topic: list[dict[str, Any]]) -> str | None:
    """Return first matching topic from keyword rules."""
    for rule in keyword_to_topic or []:
        keywords = rule.get("keywords") or []
        topic = rule.get("topic")
        if not topic:
            continue
        for kw in keywords:
            if kw.lower() in text:
                return topic
    return None


def classify_sdgs(
    items: list[dict[str, Any]],
    config_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Add topic, primary_sdg, sdg_labels, un_body to each item from sdg_news_topic_mapping.

    :param items: Normalized feed items from ingest_feeds.
    :param config_path: Path to sdg_news_topic_mapping.yaml (default: pearl_news/config/).
    :return: Items with added keys; unmatched items get topic "general", primary_sdg "17".
    """
    root = Path(__file__).resolve().parent.parent
    path = Path(config_path) if config_path else root / "config" / "sdg_news_topic_mapping.yaml"
    if not path.exists():
        logger.warning("SDG mapping not found: %s; using defaults", path)
        mapping = {"topic_to_sdg": {}, "keyword_to_topic": []}
    else:
        mapping = _load_mapping(path)

    topic_to_sdg = mapping.get("topic_to_sdg") or {}
    keyword_to_topic = mapping.get("keyword_to_topic") or []

    default_topic = "general"
    default_sdg = "17"
    default_labels = {"17": "Partnerships for the Goals"}
    default_un_body = "United Nations"

    result: list[dict[str, Any]] = []
    for item in items:
        text = _text_for_matching(item)
        topic = _match_topic(text, keyword_to_topic)
        if not topic:
            topic = default_topic

        info = topic_to_sdg.get(topic, {})
        primary_sdg = info.get("primary_sdg") or default_sdg
        sdg_labels = info.get("sdg_labels") or default_labels
        un_body = info.get("un_body") or default_un_body

        out = {**item, "topic": topic, "primary_sdg": primary_sdg, "sdg_labels": sdg_labels, "un_body": un_body}
        result.append(out)

    logger.info("Classified %d items (topics: %s)", len(result), set(i["topic"] for i in result))
    return result
