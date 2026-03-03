"""
Multi-factor title scoring. All weights from config; no hardcoded numbers.
Formula: total = seo + human_appeal - duplication_risk - penalty_score
Authority: SYSTEMS_DOCUMENTATION §29.2.3.
"""
from __future__ import annotations

import re
from typing import Any

from . import dedupe
from ._config import (
    load_intent_taxonomy,
    load_naming_scoring,
    load_recognition_lexemes,
)

# Reject sentinel when primary keyword absent (caller should not score)
REJECT = -1.0


def _tokenize(text: str) -> list[str]:
    t = (text or "").lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    return [w for w in t.split() if w]


def _stem(word: str) -> str:
    """Simple stem: lower, strip. No Porter/Snowball to avoid dependency."""
    return word.lower().strip()[:8]


def _keyword_stem_repeat_count(primary: str, title: str, subtitle: str) -> int:
    """Count how many times the primary keyword stem (or its words) repeat across title+subtitle."""
    combined = f"{title} {subtitle}".lower()
    words = _tokenize(primary)
    if not words:
        return 0
    stems_primary = {_stem(w) for w in words}
    all_tokens = _tokenize(combined)
    repeat = 0
    for w in all_tokens:
        if _stem(w) in stems_primary:
            repeat += 1
    return max(0, repeat - 1)  # first occurrence is not "repeat"


def seo_score(
    title: str,
    subtitle: str,
    primary_keyword: str,
    secondary_keywords: list[str],
    intent_class: str,
    intent_template_match: bool,
    scoring: dict[str, Any],
) -> float:
    """
    Returns SEO score 0.0--1.0, or REJECT if primary keyword absent from both.
    """
    seo_cfg = scoring.get("seo_scoring") or {}
    primary_in_title_pts = seo_cfg.get("primary_in_title", 0.50)
    primary_in_subtitle_pts = seo_cfg.get("primary_in_subtitle_only", 0.30)
    secondary_pts = seo_cfg.get("secondary_in_subtitle", 0.10)
    intent_pts = seo_cfg.get("intent_template_match", 0.10)
    stem_penalty = seo_cfg.get("keyword_stem_repeat_penalty", 0.10)
    stem_max = seo_cfg.get("keyword_stem_repeat_max", 2)

    primary_lower = (primary_keyword or "").lower()
    title_lower = (title or "").lower()
    subtitle_lower = (subtitle or "").lower()

    if primary_lower and primary_lower not in title_lower and primary_lower not in subtitle_lower:
        return REJECT

    score = 0.0
    if primary_lower and primary_lower in title_lower:
        score += primary_in_title_pts
    elif primary_lower and primary_lower in subtitle_lower:
        score += primary_in_subtitle_pts

    if secondary_keywords:
        for kw in secondary_keywords[:3]:
            if (kw or "").lower() in subtitle_lower:
                score += secondary_pts
                break

    if intent_template_match:
        score += intent_pts

    repeat_count = _keyword_stem_repeat_count(primary_keyword, title or "", subtitle or "")
    if repeat_count > stem_max:
        score -= stem_penalty

    return max(0.0, min(1.0, score))


def human_appeal_score(
    title: str,
    subtitle: str,
    primary_keyword: str,
    scenario_phrase: str,
    persona_id: str,
    intent_class: str,
    scoring: dict[str, Any],
    blacklist_matches: bool,
) -> float:
    """Human Appeal from recognition lexemes. Clamped 0.0--1.0."""
    ha_cfg = scoring.get("human_appeal") or {}
    lex = load_recognition_lexemes()
    intents = load_intent_taxonomy()
    intents_map = intents.get("intents") or {}

    combined = f"{title or ''} {subtitle or ''}".lower()
    score = 0.0

    scenario_words = [s.lower() for s in (lex.get("scenario_words") or [])]
    if any(s in combined for s in scenario_words):
        score += ha_cfg.get("scenario_lexeme", 0.25)

    persona_lex = lex.get("persona_lexemes") or {}
    persona_list = persona_lex.get(persona_id) or persona_lex.get("nyc_exec") or []
    persona_list = [p.lower() for p in persona_list]
    if any(p in combined for p in persona_list):
        score += ha_cfg.get("persona_lexeme", 0.25)

    distress_verbs = [d.lower() for d in (lex.get("distress_verbs") or [])]
    if any(d in combined for d in distress_verbs):
        score += ha_cfg.get("distress_verb", 0.20)

    outcome_phrases = [o.lower() for o in (lex.get("outcome_phrases") or [])]
    if any(o in combined for o in outcome_phrases):
        score += ha_cfg.get("outcome_phrase", 0.20)

    scenario_word_count = len((scenario_phrase or "").split())
    if scenario_word_count >= 3 and (scenario_phrase or "").lower() in combined:
        score += ha_cfg.get("scenario_3plus_words_bonus", 0.10)

    intent_cfg = intents_map.get(intent_class) or {}
    score += float(intent_cfg.get("recognition_boost", 0))

    if blacklist_matches:
        score -= ha_cfg.get("mechanism_blacklist_penalty", 0.25)
    # Abstract noun dominance: skip for Phase 1 (no POS tagger)
    # Metaphor-only: skip if we already require primary in title/subtitle
    score = max(ha_cfg.get("min_score", 0.0), min(ha_cfg.get("max_score", 1.0), score))
    return score


def duplication_risk(candidate_title: str, existing_titles: list[str], tfidf_index: Any, scoring: dict[str, Any]) -> float:
    """0.0--1.0; caller must reject if cosine > 0.90 or ngram > 0.65 before scoring."""
    if not existing_titles or not tfidf_index:
        return 0.0
    cos = dedupe.cosine_similarity(candidate_title, tfidf_index)
    return cos


def penalty_score(
    title: str,
    subtitle: str,
    scoring: dict[str, Any],
    has_outcome_verb: bool,
    same_template_as_sibling: bool,
) -> float:
    """Aggregate non-content penalties from config."""
    pen_cfg = scoring.get("penalties") or {}
    length_limits = scoring.get("length_limits") or {}
    max_title = length_limits.get("max_title_length", 60)
    score = 0.0
    if len(title or "") > max_title:
        score += pen_cfg.get("title_exceeds_max_length", 0.30)
    # Keyword stuffing: already applied in SEO as stem repeat; skip double-count
    if not has_outcome_verb:
        score += pen_cfg.get("no_outcome_verb_in_subtitle", 0.10)
    if same_template_as_sibling:
        score += pen_cfg.get("same_template_as_series_sibling", 0.10)
    return score


def total_score(
    title: str,
    subtitle: str,
    primary_keyword: str,
    secondary_keywords: list[str],
    scenario_phrase: str,
    persona_id: str,
    intent_class: str,
    intent_template_match: bool,
    template_used: str,
    existing_titles: list[str],
    tfidf_index: Any,
    same_template_as_sibling: bool = False,
) -> dict[str, float]:
    """Compute all four components and total. Returns dict with seo, human_appeal, duplication_risk, penalties, total."""
    scoring = load_naming_scoring()
    from ._config import load_mechanism_blacklist
    blacklist = load_mechanism_blacklist()
    combined = f"{title or ''} {subtitle or ''}".lower()
    blacklist_matches = any(b in combined for b in [x.lower() for x in blacklist]) if blacklist else False

    lex = load_recognition_lexemes()
    outcome_phrases = [o.lower() for o in (lex.get("outcome_phrases") or [])]
    has_outcome = any(o in (subtitle or "").lower() for o in outcome_phrases)

    seo = seo_score(
        title, subtitle, primary_keyword, secondary_keywords or [],
        intent_class, intent_template_match, scoring,
    )
    if seo == REJECT:
        return {"seo": REJECT, "human_appeal": 0, "duplication_risk": 0, "penalties": 0, "total": REJECT}

    human = human_appeal_score(
        title, subtitle, primary_keyword, scenario_phrase, persona_id, intent_class,
        scoring, blacklist_matches,
    )
    dup = duplication_risk(title, existing_titles, tfidf_index, scoring)
    pen = penalty_score(title, subtitle, scoring, has_outcome, same_template_as_sibling)
    total = seo + human - dup - pen
    return {
        "seo": round(seo, 2),
        "human_appeal": round(human, 2),
        "duplication_risk": round(dup, 2),
        "penalties": round(pen, 2),
        "total": round(total, 2),
    }
