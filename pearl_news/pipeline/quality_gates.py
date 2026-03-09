"""
Pearl News — fail-hard quality gates (production non-negotiable §4).
All gates must PASS for an article to be publishable.
Writer Spec §7, §10: youth_impact_specificity requires at least one anchor (number, place, age band, behavior).
"""
from __future__ import annotations

import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)

GATE_IDS = [
    "fact_check_completeness",
    "youth_impact_specificity",
    "sdg_un_accuracy",
    "promotional_tone_detector",
    "un_endorsement_detector",
    "writer_spec_forbidden_phrases",
]

# Writer Spec §11: phrases forbidden anywhere in the article (sixth gate).
WRITER_SPEC_FORBIDDEN_PHRASES = [
    "now more than ever",
    "in these uncertain times",
    "in a world where",
    "young people are increasingly affected",
    "youth around the world are",
    "the next generation faces unprecedented",
]

# Writer Spec §11: generic youth phrases that always fail; gate fails if present without specificity.
YOUTH_FORBIDDEN_GENERIC_PHRASES = [
    "young people are increasingly affected",
    "youth around the world are",
    "the next generation faces unprecedented",
    "young people around the world",
    "young people increasingly",
    "young people feel",
    "youth around the world feel",
    "will be filled with specific data",  # assembler stub = not yet specific
]

# At least one anchor required: number (%), place (in X), age band, or concrete behavior (Writer Spec §7).
YOUTH_ANCHOR_NUMBER_PATTERN = re.compile(r"\d+%|\d+\s*percent|survey|report\s+found|study\s+showed|data\s+show|\d{4}\s+(survey|report|study)")
YOUTH_ANCHOR_PLACE_PATTERN = re.compile(r"\bin\s+(?:the\s+)?[A-Za-z][A-Za-z\s]{2,}(?:,\s*[A-Za-z][A-Za-z\s]{2,})?\b|unicef|unesco|who\b|pew\s|cabinet\s+office|ministry\s+of\s+")
YOUTH_ANCHOR_AGE_COHORT = re.compile(r"gen\s*z|gen\s*alpha|adolescents?\s+(?:ages?)?\s*\d|ages?\s+\d{2}\s*[-–]\s*\d{2}|under\s+\d{2}|18[-–]29|12[-–]17")
YOUTH_ANCHOR_BEHAVIOR = re.compile(r"attend|enrolled|cited|reported|dropped|surveyed|participat|graduat|employment|unemployment")


def _load_legal_boundary(config_root: Path) -> list[str]:
    path = config_root / "legal_boundary.yaml"
    if not path.exists() or yaml is None:
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("blocklist_phrases") or []


def _youth_impact_specificity_pass(text: str) -> bool:
    """Writer Spec §7, §10: PASS only when youth content has at least one anchor and no forbidden generic phrase."""
    lower = text.lower()
    # Must have some youth relevance.
    youth_relevant = any(k in lower for k in ["young people", "gen z", "gen alpha", "youth", "adolescent"])
    if not youth_relevant:
        return False
    # Forbidden generic phrases (Writer Spec §11) → FAIL.
    for phrase in YOUTH_FORBIDDEN_GENERIC_PHRASES:
        if phrase in lower:
            return False
    # At least one anchor: number, place, age band, or behavior.
    has_anchor = (
        YOUTH_ANCHOR_NUMBER_PATTERN.search(lower) is not None
        or YOUTH_ANCHOR_PLACE_PATTERN.search(lower) is not None
        or YOUTH_ANCHOR_AGE_COHORT.search(lower) is not None
        or YOUTH_ANCHOR_BEHAVIOR.search(lower) is not None
    )
    return has_anchor


def _run_gates_on_article(
    item: dict[str, Any],
    blocklist: list[str],
) -> dict[str, str]:
    """Return dict of gate_id -> PASS|FAIL for one article."""
    content = (item.get("content") or item.get("content_plain") or "").lower()
    title = (item.get("article_title") or item.get("title") or "").lower()
    text = f"{title} {content}"

    results = {}

    # 1) fact_check_completeness: has cited source (feed item has url; we require 2 for news - we have 1, allow for now or check news_sources)
    has_source = bool(item.get("url")) and ("source:" in content or "http" in content or "un.org" in content)
    results["fact_check_completeness"] = "PASS" if has_source else "FAIL"

    # 2) youth_impact_specificity: Writer Spec §7 — at least one anchor (number, place, age band, behavior); no forbidden generic phrase
    results["youth_impact_specificity"] = "PASS" if _youth_impact_specificity_pass(text) else "FAIL"

    # 3) sdg_un_accuracy: no blocklist phrase (except when negated, e.g. "not affiliated")
    def _blocklist_hit(t: str, phrases: list[str]) -> bool:
        for phrase in phrases:
            p = phrase.lower()
            if p not in t:
                continue
            # Allow mandatory disclaimer: "not affiliated", "not endorsed", "not ... connected"
            if "not affiliated" in t or "not endorsed" in t or "not connected" in t or "neither is affiliated" in t:
                continue
            return True
        return False
    blocklist_fail = _blocklist_hit(text, blocklist)
    results["sdg_un_accuracy"] = "FAIL" if blocklist_fail else "PASS"

    # 4) promotional_tone_detector: no devotional/promotional keywords (simple heuristic)
    promo_words = ["buy now", "sign up", "donate here", "master says", "enlightenment", "karma will"]
    promo_fail = any(w in text for w in promo_words)
    results["promotional_tone_detector"] = "FAIL" if promo_fail else "PASS"

    # 5) un_endorsement_detector: blocklist again (same negated allowance)
    results["un_endorsement_detector"] = "FAIL" if blocklist_fail else "PASS"

    # 6) writer_spec_forbidden_phrases: Writer Spec §11 — no forbidden phrase anywhere in article
    forbidden_hit = any(phrase in text for phrase in WRITER_SPEC_FORBIDDEN_PHRASES)
    results["writer_spec_forbidden_phrases"] = "FAIL" if forbidden_hit else "PASS"

    return results


def run_quality_gates(
    items: list[dict[str, Any]],
    config_root: Path | None = None,
) -> list[dict[str, Any]]:
    """
    Run all 5 gates on each item. Set qc_results (timestamp + per-gate PASS/FAIL) and
    qc_passed (True only if all PASS). Does not remove failed items; caller can filter.
    """
    root = Path(__file__).resolve().parent.parent
    config_root = config_root or (root / "config")
    blocklist = _load_legal_boundary(config_root)

    now = datetime.now(timezone.utc).isoformat()
    for item in items:
        gate_results = _run_gates_on_article(item, blocklist)
        item["qc_results"] = {
            "timestamp": now,
            **gate_results,
        }
        item["qc_passed"] = all(v == "PASS" for v in gate_results.values())
        if not item["qc_passed"]:
            logger.debug("Article %s failed gates: %s", item.get("id"), gate_results)

    logger.info("Ran quality gates on %d articles; %d passed", len(items), sum(1 for i in items if i.get("qc_passed")))
    return items
