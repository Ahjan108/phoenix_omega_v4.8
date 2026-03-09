"""
Pearl News — select one of the 5 article templates per feed item based on topic, SDG, and source.
Uses article_templates_index.yaml and deterministic balancing for equal template mix.
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

# Default topic → template; single-teacher style remains the default for peace_conflict.
DEFAULT_TOPIC_TO_TEMPLATE = {
    "mental_health": "youth_feature",
    "education": "youth_feature",
    "peace_conflict": "hard_news_spiritual_response",
    "inequality": "explainer_context",
}


def _load_index(config_root: Path) -> dict[str, Any]:
    path = config_root / "article_templates_index.yaml"
    if not path.exists() or yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _preferred_template(item: dict[str, Any], merged_topic_map: dict[str, str]) -> str:
    """Compute preferred template from deterministic mapping rules."""
    suggested = item.get("suggested_template")
    source = item.get("source_feed_id") or ""
    topic = item.get("topic") or ""

    if suggested and suggested in TEMPLATE_IDS:
        return suggested
    if topic in merged_topic_map and merged_topic_map[topic] in TEMPLATE_IDS:
        return merged_topic_map[topic]
    if source == "un_news_sdgs" and topic in ("education", "mental_health"):
        return "youth_feature"
    if source == "un_news_sdgs":
        return "explainer_context"
    return "hard_news_spiritual_response"


def _equal_mix_assignments(preferred: list[str]) -> list[str]:
    """
    Build deterministic equal-mix assignments across all templates.
    Each template gets floor(N/5) or ceil(N/5) items.
    """
    n = len(preferred)
    template_count = len(TEMPLATE_IDS)
    base = n // template_count
    remainder = n % template_count

    quotas: dict[str, int] = {
        template_id: base + (1 if i < remainder else 0)
        for i, template_id in enumerate(TEMPLATE_IDS)
    }

    assigned: list[str | None] = [None] * n
    for idx, pref in enumerate(preferred):
        if quotas.get(pref, 0) > 0:
            assigned[idx] = pref
            quotas[pref] -= 1

    fill_pool: list[str] = []
    for template_id in TEMPLATE_IDS:
        fill_pool.extend([template_id] * quotas[template_id])

    fill_index = 0
    out: list[str] = []
    for current in assigned:
        if current is not None:
            out.append(current)
            continue
        out.append(fill_pool[fill_index])
        fill_index += 1
    return out


def select_templates(
    items: list[dict[str, Any]],
    config_root: Path | None = None,
    topic_to_template: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """
    Set template_id on each item.
    Priority for preferred template:
    1) suggested_template from classifier
    2) caller override mapping (topic_to_template)
    3) config topic_to_template mapping (if present in article_templates_index.yaml)
    4) default topic mapping
    5) source heuristics
    6) hard_news_spiritual_response fallback

    Final selection behavior:
    - If batch size < 5, use preferred template directly (topic-driven behavior).
    - If batch size >= 5, rebalance to equal mix across all 5 templates.
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

    preferred = [_preferred_template(item, merged_topic_map) for item in items]
    if len(items) < len(TEMPLATE_IDS):
        selected = preferred
    else:
        selected = _equal_mix_assignments(preferred)

    for item, template_id in zip(items, selected):
        item["template_id"] = template_id
        if template_id in templates:
            item["template_file"] = templates[template_id].get("file") or f"{template_id}.yaml"
        else:
            item["template_file"] = f"{template_id}.yaml"

    logger.info("Selected templates for %d items", len(items))
    return items
