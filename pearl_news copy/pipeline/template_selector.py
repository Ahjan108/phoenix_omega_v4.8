"""
Pearl News — select one template per feed item by topic.

Maps topic (from classifier) to template_id from article_templates_index.
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

# Topic → template_id. Must match keys in article_templates_index.yaml.
DEFAULT_TOPIC_TO_TEMPLATE: dict[str, str] = {
    "mental_health": "youth_feature",
    "education": "youth_feature",
    "climate": "hard_news_spiritual_response",
    "peace_conflict": "interfaith_dialogue_report",
    "economy_work": "hard_news_spiritual_response",
    "inequality": "explainer_context",
    "partnerships": "hard_news_spiritual_response",
    "general": "hard_news_spiritual_response",
}


def _load_template_index(config_path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required; pip install pyyaml")
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def select_templates(
    items: list[dict[str, Any]],
    config_path: str | Path | None = None,
    topic_to_template: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """
    Add template_id to each item based on topic.

    :param items: Classified items (must have topic from classify_sdgs).
    :param config_path: Path to article_templates_index.yaml (for validation).
    :param topic_to_template: Override mapping; defaults to DEFAULT_TOPIC_TO_TEMPLATE.
    :return: Items with template_id added.
    """
    root = Path(__file__).resolve().parent.parent
    path = Path(config_path) if config_path else root / "config" / "article_templates_index.yaml"
    mapping = topic_to_template or DEFAULT_TOPIC_TO_TEMPLATE

    valid_templates: set[str] = set()
    if path.exists():
        index = _load_template_index(path)
        templates = index.get("templates") or {}
        valid_templates = set(templates.keys())
    else:
        valid_templates = set(DEFAULT_TOPIC_TO_TEMPLATE.values())

    default_template = "hard_news_spiritual_response"

    result: list[dict[str, Any]] = []
    for item in items:
        topic = item.get("topic") or "general"
        template_id = mapping.get(topic, default_template)
        if template_id not in valid_templates and valid_templates:
            template_id = default_template
        out = {**item, "template_id": template_id}
        result.append(out)

    logger.info("Selected templates for %d items (templates: %s)", len(result), set(i["template_id"] for i in result))
    return result
