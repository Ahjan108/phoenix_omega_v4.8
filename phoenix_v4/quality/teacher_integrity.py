"""
Teacher integrity scoring for EI V1.

Detects promo phrases, miracle claims, sectarian superiority, endorsement implication.
Supports softening for lineage-safe framing when configured.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# --- Phrase lists ---
PROMO_PHRASES: List[str] = [
    "sign up", "enroll now", "register today", "subscribe", "join my",
    "limited time", "act now", "don't miss", "exclusive offer", "buy now",
    "my program", "my course", "my coaching", "my method", "my system",
    "free trial", "free consultation", "discount", "promo code", "special offer",
]

MIRACLE_CLAIMS: List[str] = [
    "miracle", "guaranteed", "100% effective", "cure", "instant",
    "permanently fix", "never feel again", "eliminate", "eradicate",
    "proven to cure", "scientifically proven", "clinically proven",
]

SECTARIAN_SUPERIORITY: List[str] = [
    "the only way", "the one true", "real practitioners", "authentic lineage",
    "others get it wrong", "everyone else", "the correct approach",
    "true teaching", "genuine path",
]

ENDORSEMENT_IMPLICATION: List[str] = [
    "as seen on", "featured in", "used by", "trusted by", "recommended by",
    "endorsed by", "celebrity", "famous", "millions of",
]

# Lineage-safe framing: phrases that soften sectarian language when used together
DEFAULT_ALLOWLIST: List[str] = [
    "many paths", "different approaches", "one approach among many",
    "this tradition", "in this lineage", "one way to",
]


@dataclass
class TeacherIntegrityPenalty:
    """Penalty result from teacher integrity check."""
    penalty: float
    categories: Dict[str, float] = None
    reason_codes: List[str] = None

    def __post_init__(self) -> None:
        if self.categories is None:
            self.categories = {}
        if self.reason_codes is None:
            self.reason_codes = []


def _count_phrase_hits(text: str, phrases: List[str]) -> int:
    """Case-insensitive phrase count."""
    tl = text.lower()
    return sum(1 for p in phrases if p.lower() in tl)


def _count_pattern_hits(text: str, patterns: List[re.Pattern]) -> int:
    """Count regex pattern matches."""
    return sum(len(p.findall(text)) for p in patterns)


def compute_teacher_integrity_penalty(
    text: str,
    cfg: Optional[Dict[str, Any]] = None,
) -> TeacherIntegrityPenalty:
    """
    Compute teacher integrity penalty. Higher penalty = more problematic language.

    Softening: when soften_categories is configured and text contains allowlist
    phrases (lineage-safe framing), reduce penalty for those categories only.
    Promo, miracle, endorsement stay full penalty.
    """
    cfg = cfg or {}
    soften_categories = cfg.get("soften_categories", [])
    allowlist = cfg.get("allowlist", DEFAULT_ALLOWLIST)

    text = text or ""
    text_lower = text.lower()
    has_allowlist = any(aw.lower() in text_lower for aw in allowlist)

    categories: Dict[str, float] = {}
    reason_codes: List[str] = []

    # Promo - no softening
    promo_hits = _count_phrase_hits(text, PROMO_PHRASES)
    promo_score = min(1.0, promo_hits / 2.0)
    categories["promo"] = promo_score
    if promo_score >= 0.5:
        reason_codes.append("promo_detected")

    # Miracle claims - no softening
    miracle_hits = _count_phrase_hits(text, MIRACLE_CLAIMS)
    miracle_score = min(1.0, miracle_hits / 2.0)
    categories["miracle"] = miracle_score
    if miracle_score >= 0.5:
        reason_codes.append("miracle_claim_detected")

    # Sectarian superiority - soften if allowlist present
    sect_hits = _count_phrase_hits(text, SECTARIAN_SUPERIORITY)
    sect_score = min(1.0, sect_hits / 2.0)
    if "sectarian" in soften_categories and has_allowlist and sect_score > 0:
        sect_score *= 0.3  # Soften
    categories["sectarian"] = sect_score
    if sect_score >= 0.5:
        reason_codes.append("sectarian_superiority_detected")

    # Endorsement implication - no softening (or optionally if in soften_categories)
    end_hits = _count_phrase_hits(text, ENDORSEMENT_IMPLICATION)
    end_score = min(1.0, end_hits / 2.0)
    if "endorsement" in soften_categories and has_allowlist and end_score > 0:
        end_score *= 0.3
    categories["endorsement"] = end_score
    if end_score >= 0.5:
        reason_codes.append("endorsement_implication_detected")

    # Aggregate penalty (weighted)
    weights = {
        "promo": 0.30,
        "miracle": 0.35,
        "sectarian": 0.20,
        "endorsement": 0.15,
    }
    penalty = sum(categories.get(k, 0) * w for k, w in weights.items())
    penalty = min(1.0, penalty)

    return TeacherIntegrityPenalty(
        penalty=round(penalty, 4),
        categories={k: round(v, 4) for k, v in categories.items()},
        reason_codes=reason_codes,
    )
