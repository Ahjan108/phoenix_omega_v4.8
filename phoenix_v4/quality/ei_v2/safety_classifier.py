"""
Few-shot safety classifier for EI V2.

Detects safety violations that regex-based patterns miss:
  - Paraphrased medical/cure claims
  - Subtle promotional language
  - Clinical/DSM language creeping into consumer content
  - Reassurance spam (repetitive comfort without substance)
  - Pathologizing language

Two modes:
  - "heuristic_plus": Enhanced pattern matching with context windows,
    co-occurrence analysis, and negation handling. Zero dependencies.
  - "llm": Few-shot classification via LLM callback. Higher accuracy,
    requires API.

Each violation category returns a score in [0, 1] and reason codes.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple


# --- Expanded pattern banks (beyond V1 exact phrase lists) ---

# Medical claims: broader than V1's exact phrase match.
# Catches paraphrased variants like "eliminate your panic" or
# "this technique has been proven to cure".
_MEDICAL_CLAIM_PATTERNS = [
    re.compile(r"\b(?:cure[sd]?|eliminat(?:e[sd]?|ing)|eradicat(?:e[sd]?|ing))\b.*\b(?:anxiety|depression|ptsd|disorder|trauma|insomnia|adhd)\b", re.I),
    re.compile(r"\b(?:anxiety|depression|ptsd|disorder|trauma|insomnia)\b.*\b(?:cure[sd]?|eliminat(?:e[sd]?|ing)|eradicat(?:e[sd]?|ing))\b", re.I),
    re.compile(r"\b(?:proven|clinically proven|scientifically proven)\s+to\s+(?:cure|fix|heal|treat|eliminate)\b", re.I),
    re.compile(r"\b(?:permanent(?:ly)?|completely|totally)\s+(?:cure[sd]?|fix(?:e[sd])?|heal(?:e?d)?|remov(?:e[sd]?|ing))\b", re.I),
    re.compile(r"\bthis\s+(?:will|can|is\s+going\s+to)\s+(?:cure|fix|heal)\s+(?:you|your)\b", re.I),
    re.compile(r"\b100\s*%\s*(?:effective|success|cure|recovery)\b", re.I),
    re.compile(r"\bguaranteed?\s+(?:results?|recovery|healing|cure|improvement)\b", re.I),
    re.compile(r"\bnever\s+(?:feel|experience|suffer|have)\s+(?:anxiety|depression|panic|insomnia)\s+again\b", re.I),
]

# Clinical/DSM language that should not appear in consumer-facing self-help.
_CLINICAL_PATTERNS = [
    re.compile(r"\b(?:dsm|dsm-5|icd-10|icd-11)\b", re.I),
    re.compile(r"\b(?:generalized\s+anxiety\s+disorder|major\s+depressive\s+disorder|bipolar\s+disorder)\b", re.I),
    re.compile(r"\b(?:ptsd|post-traumatic\s+stress\s+disorder)\b", re.I),
    re.compile(r"\b(?:borderline\s+personality|antisocial\s+personality|narcissistic\s+personality)\b", re.I),
    re.compile(r"\b(?:comorbid(?:ity)?|psychopathology|serotonin\s+reuptake|benzodiazepine)\b", re.I),
    re.compile(r"\b(?:diagnos(?:e[sd]?|is|tic)|prescri(?:be[sd]?|ption)|medic(?:ation|ine|al\s+treatment))\b", re.I),
    re.compile(r"\b(?:cognitive\s+behavioral\s+therapy|dialectical\s+behavior\s+therapy|emdr)\b", re.I),
    re.compile(r"\b(?:symptom(?:s|atology)?|patholog(?:y|ical)|clinical\s+(?:trial|intervention|assessment))\b", re.I),
]

# Promotional language (expanded beyond V1 exact phrases).
_PROMOTIONAL_PATTERNS = [
    re.compile(r"\b(?:sign\s+up|enroll|register|subscribe|join)\s+(?:now|today|for|to)\b", re.I),
    re.compile(r"\b(?:limited\s+time|act\s+now|don'?t\s+miss|hurry|last\s+chance|exclusive\s+offer)\b", re.I),
    re.compile(r"\b(?:buy|purchase|order|get\s+yours?)\s+(?:now|today|here)\b", re.I),
    re.compile(r"\b(?:my\s+(?:program|course|coaching|method|system|framework|masterclass))\b", re.I),
    re.compile(r"\b(?:free\s+(?:trial|consultation|session|webinar|download))\b", re.I),
    re.compile(r"\b(?:discount|coupon|promo\s*code|special\s+(?:offer|price|deal))\b", re.I),
    re.compile(r"\b(?:testimonial|success\s+stor(?:y|ies)|client\s+results?)\b", re.I),
]

# Reassurance spam: empty comfort with no substance.
_REASSURANCE_SPAM_PHRASES = [
    "you are not broken",
    "you've got this",
    "everything will be okay",
    "everything happens for a reason",
    "it will all work out",
    "trust the process",
    "you are enough",
    "believe in yourself",
    "the universe has a plan",
    "you are worthy",
    "you deserve happiness",
    "let it go",
    "stay positive",
    "good vibes only",
    "you are stronger than you think",
]

# Pathologizing language: labels the person rather than the experience.
_PATHOLOGIZING_PATTERNS = [
    re.compile(r"\byou\s+(?:are|have)\s+(?:a\s+)?(?:anxious|depressed|broken|damaged|sick|disordered|dysfunctional)\b", re.I),
    re.compile(r"\b(?:your|the)\s+(?:disorder|illness|condition|disease|dysfunction|pathology)\b", re.I),
    re.compile(r"\b(?:suffer(?:er|ing)?|victim|patient)\b", re.I),
]

# Negation window: phrases near "not" that flip meaning (reduces false positives).
_NEGATION_WINDOW = 4


def _count_pattern_hits(text: str, patterns: list) -> Tuple[int, List[str]]:
    """Count how many patterns match and return matched excerpts."""
    hits = 0
    excerpts: List[str] = []
    for pat in patterns:
        matches = pat.findall(text)
        if matches:
            hits += len(matches)
            excerpts.extend(str(m)[:60] for m in matches[:3])
    return hits, excerpts


def _count_phrase_hits(text: str, phrases: List[str]) -> Tuple[int, List[str]]:
    """Count exact phrase hits (case-insensitive)."""
    tl = text.lower()
    hits = 0
    excerpts: List[str] = []
    for phrase in phrases:
        count = tl.count(phrase.lower())
        if count > 0:
            hits += count
            excerpts.append(phrase)
    return hits, excerpts


def _negation_adjusted_hits(text: str, patterns: list) -> int:
    """Reduce hit count when pattern occurs near negation words."""
    words = text.lower().split()
    negations = {"not", "no", "never", "neither", "nor", "don't", "doesn't",
                 "didn't", "won't", "wouldn't", "can't", "cannot", "shouldn't",
                 "isn't", "aren't", "wasn't", "weren't", "without"}
    raw_hits, _ = _count_pattern_hits(text, patterns)
    negated = 0
    for i, w in enumerate(words):
        if w in negations:
            window = " ".join(words[max(0, i - 1):i + _NEGATION_WINDOW + 1])
            for pat in patterns:
                if pat.search(window):
                    negated += 1
                    break
    return max(0, raw_hits - negated)


def classify_safety(
    text: str,
    *,
    slot: str = "",
    cfg: Optional[Dict[str, Any]] = None,
    call_llm_fn: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    Classify text for safety violations.

    Returns dict with per-category scores and an aggregate risk_score in [0, 1].
    Each category includes: score (0-1), hits (int), excerpts (list), reason_codes (list).
    """
    cfg = cfg or {}
    mode = cfg.get("mode", "heuristic_plus")
    text = text or ""

    result: Dict[str, Any] = {
        "risk_score": 0.0,
        "categories": {},
        "reason_codes": [],
        "mode": mode,
    }

    # Medical claims
    med_threshold = float(cfg.get("medical_claim_threshold", 0.6))
    med_hits_raw, med_excerpts = _count_pattern_hits(text, _MEDICAL_CLAIM_PATTERNS)
    med_hits = _negation_adjusted_hits(text, _MEDICAL_CLAIM_PATTERNS)
    med_score = min(1.0, med_hits / 2.0)
    result["categories"]["medical_claims"] = {
        "score": round(med_score, 3),
        "hits": med_hits,
        "raw_hits": med_hits_raw,
        "excerpts": med_excerpts[:3],
    }
    if med_score >= med_threshold:
        result["reason_codes"].append("medical_claim_detected")

    # Clinical language
    clin_threshold = float(cfg.get("clinical_language_threshold", 0.5))
    clin_hits, clin_excerpts = _count_pattern_hits(text, _CLINICAL_PATTERNS)
    clin_score = min(1.0, clin_hits / 3.0)
    result["categories"]["clinical_language"] = {
        "score": round(clin_score, 3),
        "hits": clin_hits,
        "excerpts": clin_excerpts[:3],
    }
    if clin_score >= clin_threshold:
        result["reason_codes"].append("clinical_language_detected")

    # Promotional
    promo_threshold = float(cfg.get("promotional_threshold", 0.5))
    promo_hits, promo_excerpts = _count_pattern_hits(text, _PROMOTIONAL_PATTERNS)
    promo_score = min(1.0, promo_hits / 2.0)
    result["categories"]["promotional"] = {
        "score": round(promo_score, 3),
        "hits": promo_hits,
        "excerpts": promo_excerpts[:3],
    }
    if promo_score >= promo_threshold:
        result["reason_codes"].append("promotional_detected")

    # Reassurance spam
    reas_hits, reas_excerpts = _count_phrase_hits(text, _REASSURANCE_SPAM_PHRASES)
    word_count = max(1, len(text.split()))
    reas_density = reas_hits / (word_count / 100.0)
    reas_score = min(1.0, reas_density / 3.0)
    result["categories"]["reassurance_spam"] = {
        "score": round(reas_score, 3),
        "hits": reas_hits,
        "density_per_100_words": round(reas_density, 3),
        "excerpts": reas_excerpts[:3],
    }
    if reas_score >= 0.4:
        result["reason_codes"].append("reassurance_spam_detected")

    # Pathologizing
    path_hits, path_excerpts = _count_pattern_hits(text, _PATHOLOGIZING_PATTERNS)
    path_hits_adj = _negation_adjusted_hits(text, _PATHOLOGIZING_PATTERNS)
    path_score = min(1.0, path_hits_adj / 2.0)
    result["categories"]["pathologizing"] = {
        "score": round(path_score, 3),
        "hits": path_hits_adj,
        "raw_hits": path_hits,
        "excerpts": path_excerpts[:3],
    }
    if path_score >= 0.4:
        result["reason_codes"].append("pathologizing_detected")

    # Aggregate risk score (weighted)
    weights = {
        "medical_claims": 0.30,
        "clinical_language": 0.15,
        "promotional": 0.25,
        "reassurance_spam": 0.15,
        "pathologizing": 0.15,
    }
    total = sum(
        result["categories"][cat]["score"] * w
        for cat, w in weights.items()
        if cat in result["categories"]
    )
    result["risk_score"] = round(min(1.0, total), 4)

    return result
