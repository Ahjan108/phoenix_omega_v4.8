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


def _load_index(config_root: Path) -> dict[str, Any]:
    path = config_root / "article_templates_index.yaml"
    if not path.exists() or yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def select_templates(
    items: list[dict[str, Any]],
    config_root: Path | None = None,
) -> list[dict[str, Any]]:
    """
    Set template_id on each item. Uses suggested_template from classifier if present;
    otherwise defaults to hard_news_spiritual_response. SDG feed items can use explainer or youth_feature.
    """
    root = Path(__file__).resolve().parent.parent
    config_root = config_root or (root / "config")
    index = _load_index(config_root)
    templates = index.get("templates") or {}

    for i, item in enumerate(items):
        suggested = item.get("suggested_template")
        source = item.get("source_feed_id") or ""
        topic = item.get("topic") or ""

        if suggested and suggested in TEMPLATE_IDS:
            template_id = suggested
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
