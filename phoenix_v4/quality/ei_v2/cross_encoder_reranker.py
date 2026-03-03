"""
Cross-encoder reranking for EI V2.

Takes a thesis (query) and candidate texts, scores each pair, and returns
candidates ranked by relevance. Two modes:

  - "heuristic": Enhanced heuristic scoring that simulates cross-encoder
    behavior using token overlap, semantic field matching, and positional
    weighting. No external model needed.

  - "model": Uses a real cross-encoder model via call_model_fn callback.
    Model must accept (text_a, text_b) -> float score.

Heuristic mode is default and runs everywhere with zero dependencies.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Any, Callable, Dict, List, Optional


# Semantic field clusters — words that indicate shared meaning even when
# surface tokens differ. Tuned for therapeutic/somatic self-help domain.
_SEMANTIC_FIELDS = {
    "body_activation": {
        "chest", "jaw", "shoulders", "stomach", "throat", "breath",
        "breathing", "heart", "pulse", "tight", "tension", "shaking",
        "sweat", "cold", "heat", "nausea", "dizzy", "racing",
    },
    "emotional_state": {
        "anxious", "anxiety", "fear", "panic", "dread", "worry",
        "overwhelm", "exhaustion", "burnout", "grief", "shame",
        "guilt", "anger", "sadness", "loneliness", "numbness",
    },
    "cognitive_pattern": {
        "overthinking", "rumination", "spiral", "loop", "catastrophize",
        "predict", "analyze", "rehearse", "replay", "anticipate",
        "fixate", "obsess", "doubt", "second-guess",
    },
    "action_verbs": {
        "breathe", "pause", "notice", "ground", "anchor", "release",
        "soften", "settle", "slow", "rest", "exhale", "inhale",
    },
    "relational": {
        "boundary", "boundaries", "relationship", "partner", "family",
        "colleague", "friend", "trust", "safety", "connection",
        "attachment", "abandonment", "rejection",
    },
    "temporal_concrete": {
        "morning", "night", "3am", "2am", "monday", "commute",
        "meeting", "deadline", "alarm", "notification", "email",
        "phone", "screen",
    },
}

_FIELD_WORDS: Dict[str, str] = {}
for field_name, words in _SEMANTIC_FIELDS.items():
    for w in words:
        _FIELD_WORDS[w] = field_name


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", (text or "").lower())


def _semantic_field_overlap(tokens_a: List[str], tokens_b: List[str]) -> float:
    """Score based on shared semantic fields, not just shared tokens."""
    fields_a = {_FIELD_WORDS[t] for t in tokens_a if t in _FIELD_WORDS}
    fields_b = {_FIELD_WORDS[t] for t in tokens_b if t in _FIELD_WORDS}
    if not fields_a and not fields_b:
        return 0.0
    intersection = fields_a & fields_b
    union = fields_a | fields_b
    return len(intersection) / len(union) if union else 0.0


def _token_overlap(tokens_a: List[str], tokens_b: List[str]) -> float:
    """Jaccard similarity on token sets, ignoring stopwords."""
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                 "being", "have", "has", "had", "do", "does", "did", "will",
                 "would", "could", "should", "may", "might", "can", "shall",
                 "to", "of", "in", "for", "on", "with", "at", "by", "from",
                 "as", "into", "through", "during", "before", "after", "and",
                 "but", "or", "nor", "not", "so", "yet", "both", "either",
                 "neither", "each", "every", "all", "any", "few", "more",
                 "most", "other", "some", "such", "no", "only", "own", "same",
                 "than", "too", "very", "just", "because", "if", "when",
                 "while", "that", "this", "it", "its", "i", "you", "your",
                 "they", "them", "their", "we", "our", "he", "she", "his",
                 "her", "my", "me"}
    set_a = {t for t in tokens_a if t not in stopwords}
    set_b = {t for t in tokens_b if t not in stopwords}
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def _positional_bonus(thesis_tokens: List[str], candidate_tokens: List[str]) -> float:
    """Bonus if thesis concepts appear in the first 30 tokens of candidate (early recognition)."""
    if not thesis_tokens or not candidate_tokens:
        return 0.0
    early = set(candidate_tokens[:30])
    thesis_set = set(thesis_tokens)
    if not thesis_set:
        return 0.0
    overlap = early & thesis_set
    return min(1.0, len(overlap) / max(3, len(thesis_set) * 0.3))


def _heuristic_score(thesis: str, candidate_text: str) -> float:
    """Heuristic cross-encoder-like score in [0, 1]."""
    t_tokens = _tokenize(thesis)
    c_tokens = _tokenize(candidate_text)

    token_sim = _token_overlap(t_tokens, c_tokens)
    field_sim = _semantic_field_overlap(t_tokens, c_tokens)
    pos_bonus = _positional_bonus(t_tokens, c_tokens)

    raw = 0.40 * token_sim + 0.40 * field_sim + 0.20 * pos_bonus
    return min(1.0, raw)


def rerank_candidates(
    thesis: str,
    texts: List[str],
    ids: List[str],
    *,
    cfg: Optional[Dict[str, Any]] = None,
    call_model_fn: Optional[Callable[[str, str], float]] = None,
) -> List[Dict[str, Any]]:
    """
    Rerank candidates by thesis relevance.

    Returns list of {"id": str, "score": float} sorted descending by score.
    """
    cfg = cfg or {}
    mode = cfg.get("mode", "heuristic")
    top_n = int(cfg.get("top_n", len(texts)))

    scored: List[Dict[str, Any]] = []

    for cid, text in zip(ids, texts):
        if mode == "model" and call_model_fn is not None:
            try:
                score = call_model_fn(thesis, text)
            except Exception:
                score = _heuristic_score(thesis, text)
        else:
            score = _heuristic_score(thesis, text)

        scored.append({"id": cid, "score": round(score, 4)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
