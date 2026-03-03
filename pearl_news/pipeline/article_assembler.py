"""
Pearl News — fill template slots from feed item + atoms.

MVP: rule-based assembly from feed data and config. No LLM. Slots filled from:
- news_event: feed summary
- youth_impact: short placeholder from topic
- sdg_ref: from sdg_labels + un_body (classifier output)
- teacher_quotes_practices: placeholder (no atom store yet)
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


def _load_template(template_id: str, root: Path) -> dict[str, Any] | None:
    templates_dir = root / "article_templates"
    candidates = [f"{template_id}.yaml", f"{template_id}.yml"]
    for name in candidates:
        p = templates_dir / name
        if p.exists():
            if yaml is None:
                return {"section_slots": []}
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    return None


def _youth_impact_placeholder(topic: str) -> str:
    """Short placeholder for youth impact by topic."""
    placeholders: dict[str, str] = {
        "climate": "Young people are increasingly affected by climate impacts and are leading advocacy for action.",
        "mental_health": "Youth mental health remains a priority for families and communities worldwide.",
        "education": "Education systems continue to adapt to support young learners.",
        "peace_conflict": "Conflict and displacement disproportionately affect young people.",
        "economy_work": "Youth employment and economic opportunity remain key concerns.",
        "inequality": "Inequality affects young people's access to opportunity.",
        "partnerships": "Partnerships across sectors support youth-focused initiatives.",
        "general": "The issue has significant implications for young people and future generations.",
    }
    return placeholders.get(topic, placeholders["general"])


def _sdg_ref_text(primary_sdg: str, sdg_labels: dict[str, str], un_body: str) -> str:
    """Build SDG reference paragraph (no endorsement claim)."""
    label = sdg_labels.get(primary_sdg, f"SDG {primary_sdg}")
    return (
        f"This story relates to Sustainable Development Goal {primary_sdg} ({label}). "
        f"Relevant UN work in this area is led by {un_body}."
    )


def _assemble_one(item: dict[str, Any], template: dict[str, Any], root: Path) -> dict[str, Any]:
    """Fill slots and produce article dict (title, content, featured_image, etc.)."""
    slots = template.get("section_slots") or []
    topic = item.get("topic") or "general"
    primary_sdg = item.get("primary_sdg") or "17"
    sdg_labels = item.get("sdg_labels") or {"17": "Partnerships for the Goals"}
    un_body = item.get("un_body") or "United Nations"

    summary = item.get("summary") or item.get("raw_summary") or "No summary available."
    url = item.get("url") or ""

    sections: list[str] = []
    for slot_def in slots:
        slot = slot_def.get("slot", "")
        source = slot_def.get("source", "")
        if not slot:
            continue
        if source == "news_event" or slot == "news_summary":
            sections.append(f"<p>{summary}</p>")
        elif source == "youth_impact" or slot in ("youth_impact", "youth_narrative"):
            sections.append(f"<p>{_youth_impact_placeholder(topic)}</p>")
        elif source == "sdg_ref" or slot in ("sdg_un_tie", "sdg_framework"):
            sections.append(f"<p>{_sdg_ref_text(primary_sdg, sdg_labels, un_body)}</p>")
        elif source == "teacher_quotes_practices" or "teacher" in slot.lower():
            sections.append("<p><em>Forum perspective to be added.</em></p>")
        elif source == "generate" and slot == "headline":
            continue  # headline becomes title
        elif source == "generate":
            sections.append("<p></p>")

    content = "\n".join(sections)
    if url:
        content += f'\n<p><a href="{url}">Source</a></p>'

    title = item.get("title") or item.get("raw_title") or "(No title)"

    images = item.get("images") or []
    featured_image = None
    if images:
        img = images[0]
        featured_image = {
            "url": img.get("url"),
            "credit": img.get("credit") or item.get("source_feed_title", ""),
            "source_url": img.get("source_url") or url,
        }
        if img.get("caption"):
            featured_image["caption"] = img["caption"]

    return {
        "id": item.get("id"),
        "_feed_item_id": item.get("id"),
        "title": title,
        "content": content,
        "slug": None,
        "featured_image": featured_image,
        "template_id": item.get("template_id"),
        "topic": topic,
        "primary_sdg": primary_sdg,
        "source_url": url,
        "pub_date": item.get("pub_date"),
        "teacher_ids": item.get("teacher_ids") or [],
        "stressor_tags": item.get("stressor_tags") or [],
        "region": item.get("region") or item.get("source_feed_id") or "",
    }


def assemble_articles(
    items: list[dict[str, Any]],
    templates_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Produce article drafts from classified + template-selected items.

    :param items: Items from select_templates (must have template_id, topic, primary_sdg, etc.).
    :param templates_dir: Base path for article_templates (default: pearl_news/article_templates).
    :return: List of article dicts (title, content, featured_image, ...) ready for QC and posting.
    """
    root = Path(templates_dir) if templates_dir else Path(__file__).resolve().parent.parent

    result: list[dict[str, Any]] = []
    for item in items:
        template_id = item.get("template_id") or "hard_news_spiritual_response"
        template = _load_template(template_id, root)
        if not template:
            logger.warning("Template %s not found; using minimal", template_id)
            template = {"section_slots": [{"slot": "news_summary", "source": "news_event"}]}
        article = _assemble_one(item, template, root)
        result.append(article)

    logger.info("Assembled %d articles", len(result))
    return result
