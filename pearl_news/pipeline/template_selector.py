"""
Pearl News — select one of the 5 article templates per feed item based on topic, SDG, and source.
Uses article_templates_index.yaml; applies simple rules for diversity.
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

TEMPLATE_IDS = [
    "hard_news_spiritual_response",
    "youth_feature",
    "interfaith_dialogue_report",
    "explainer_context",
    "commentary",
]

DEFAULT_TOPIC_TO_TEMPLATE = {
    "mental_health": "youth_feature",
    "education": "youth_feature",
    "peace_conflict": "interfaith_dialogue_report",
    "inequality": "explainer_context",
}


def _load_index(config_root: Path) -> dict[str, Any]:
    path = config_root / "article_templates_index.yaml"
    if not path.exists() or yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def select_templates(
    items: list[dict[str, Any]],
    config_root: Path | None = None,
    topic_to_template: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """
    Set template_id on each item.
    Priority:
    1) suggested_template from classifier
    2) caller override mapping (topic_to_template)
    3) config topic_to_template mapping (if present in article_templates_index.yaml)
    4) default topic mapping
    5) source heuristics
    6) hard_news_spiritual_response fallback
    """
    root = Path(__file__).resolve().parent.parent
    config_root = config_root or (root / "config")
    index = _load_index(config_root)
    templates = index.get("templates") or {}
    config_topic_map = index.get("topic_to_template") or {}
    merged_topic_map = dict(DEFAULT_TOPIC_TO_TEMPLATE)
    merged_topic_map.update(config_topic_map)
    if topic_to_template:
        merged_topic_map.update(topic_to_template)

    for i, item in enumerate(items):
        suggested = item.get("suggested_template")
        source = item.get("source_feed_id") or ""
        topic = item.get("topic") or ""

        if suggested and suggested in TEMPLATE_IDS:
            template_id = suggested
        elif topic in merged_topic_map and merged_topic_map[topic] in TEMPLATE_IDS:
            template_id = merged_topic_map[topic]
        elif source == "un_news_sdgs" and topic in ("education", "mental_health"):
            template_id = "youth_feature"
        elif source == "un_news_sdgs":
            template_id = "explainer_context"
        else:
            template_id = "hard_news_spiritual_response"

        item["template_id"] = template_id
        if template_id in templates:
            item["template_file"] = templates[template_id].get("file") or f"{template_id}.yaml"
        else:
            item["template_file"] = f"{template_id}.yaml"

    logger.info("Selected templates for %d items", len(items))
    return items
