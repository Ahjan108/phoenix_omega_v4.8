"""
Hard validators — fail-fast, run BEFORE scorer.
All thresholds from config; no hardcoded numbers. Authority: SYSTEMS_DOCUMENTATION §29.2.
"""
from __future__ import annotations

from typing import Any

from . import dedupe
from ._config import load_mechanism_blacklist, load_naming_scoring

HARD_VALIDATORS = [
    "mechanism_blacklist_match_in_title",
    "primary_keyword_absent_from_both",
    "cosine_similarity_gt_090",
    "ngram_overlap_gt_065",
    "title_exceeds_max_length",
    "same_skeleton_gt_3_times_in_wave",
]


def _blacklist_matches(text: str, blacklist: list[str]) -> bool:
    lower = (text or "").lower()
    return any(phrase in lower for phrase in blacklist)


def validate(
    candidate: dict[str, Any],
    existing_titles: list[str],
    current_batch: list[str],
    tfidf_index: Any,
    primary_keyword: str,
) -> tuple[bool, str]:
    """
    Returns (is_valid, rejection_reason).
    If valid, rejection_reason is empty string.
    """
    title = (candidate.get("title") or "").strip()
    subtitle = (candidate.get("subtitle") or "").strip()
    combined = f"{title} {subtitle}".strip()

    scoring = load_naming_scoring()
    length_limits = scoring.get("length_limits") or {}
    dup = scoring.get("duplication") or {}
    validators_cfg = scoring.get("validators") or {}
    max_title_len = length_limits.get("max_title_length", 60)
    cosine_thresh = dup.get("cosine_reject_threshold", 0.90)
    ngram_thresh = dup.get("ngram_reject_threshold", 0.65)
    ngram_n = dup.get("ngram_n", 3)
    skeleton_max = validators_cfg.get("same_skeleton_max_per_wave", 3)

    blacklist = load_mechanism_blacklist()
    if blacklist:
        if _blacklist_matches(title, blacklist):
            return False, "mechanism_blacklist_match_in_title"
        if _blacklist_matches(subtitle, blacklist):
            return False, "mechanism_blacklist_match_in_title"

    primary_lower = (primary_keyword or "").lower()
    if primary_lower:
        in_title = primary_lower in title.lower()
        in_subtitle = primary_lower in subtitle.lower()
        if not in_title and not in_subtitle:
            return False, "primary_keyword_absent_from_both"

    if tfidf_index and existing_titles:
        cos = dedupe.cosine_similarity(title, tfidf_index)
        if cos > cosine_thresh:
            return False, "cosine_similarity_gt_090"
        ngram = dedupe.ngram_overlap(title, existing_titles, n=ngram_n)
        if ngram > ngram_thresh:
            return False, "ngram_overlap_gt_065"

    if len(title) > max_title_len:
        return False, "title_exceeds_max_length"

    template_used = candidate.get("template_used") or candidate.get("template_id") or ""
    if template_used and current_batch:
        skeleton_counts: dict[str, int] = {}
        for s in current_batch:
            skeleton_counts[s] = skeleton_counts.get(s, 0) + 1
        count_this = sum(1 for s in current_batch if s == template_used)
        if count_this > skeleton_max:
            return False, "same_skeleton_gt_3_times_in_wave"

    return True, ""
