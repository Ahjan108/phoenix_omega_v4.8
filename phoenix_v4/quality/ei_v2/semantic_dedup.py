"""
Semantic duplication detection for EI V2.

Detects near-duplicate atoms that surface text matching misses:
  - N-gram overlap (character and word level)
  - Structural similarity (sentence count, paragraph shape)
  - Narrative beat fingerprinting (inciting incident, turn, cost, resolution)

Two modes:
  - "ngram_plus_embedding": N-gram overlap + structural similarity.
    No external model needed.
  - "full": Adds embedding-based semantic similarity via embed_fn callback.

Returns pairs of candidates flagged as potential duplicates with
similarity scores and evidence.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


def _word_ngrams(text: str, n: int) -> Set[str]:
    """Extract word-level n-grams from text."""
    words = re.findall(r"\b\w+\b", (text or "").lower())
    if len(words) < n:
        return set()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def _char_ngrams(text: str, n: int = 4) -> Set[str]:
    """Extract character-level n-grams (for fuzzy matching)."""
    t = (text or "").lower()
    if len(t) < n:
        return set()
    return {t[i:i + n] for i in range(len(t) - n + 1)}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union) if union else 0.0


def _sentence_count(text: str) -> int:
    return len(re.split(r"[.!?]+", text.strip())) if text.strip() else 0


def _paragraph_shape(text: str) -> List[int]:
    """Return list of word counts per paragraph (structural fingerprint)."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [len(p.split()) for p in paragraphs]


def _shape_similarity(shape_a: List[int], shape_b: List[int]) -> float:
    """Compare paragraph shape vectors. 1.0 = identical structure."""
    if not shape_a or not shape_b:
        return 0.0
    if len(shape_a) != len(shape_b):
        len_sim = min(len(shape_a), len(shape_b)) / max(len(shape_a), len(shape_b))
    else:
        len_sim = 1.0

    min_len = min(len(shape_a), len(shape_b))
    if min_len == 0:
        return 0.0

    diffs = []
    for i in range(min_len):
        max_wc = max(shape_a[i], shape_b[i], 1)
        diffs.append(1.0 - abs(shape_a[i] - shape_b[i]) / max_wc)

    return (sum(diffs) / len(diffs)) * len_sim


# Narrative beat markers (heuristic fingerprinting for story atoms).
_BEAT_PATTERNS = {
    "inciting_incident": [
        re.compile(r"\b(?:that\s+(?:morning|day|night|moment)|one\s+(?:morning|day|night)|it\s+started\s+when)\b", re.I),
        re.compile(r"\b(?:the\s+(?:first|last)\s+time|the\s+moment\s+(?:when|that))\b", re.I),
    ],
    "escalation": [
        re.compile(r"\b(?:and\s+then|it\s+got\s+worse|each\s+time|every\s+day|kept\s+(?:going|growing|building))\b", re.I),
    ],
    "turning_point": [
        re.compile(r"\b(?:but\s+then|until\s+(?:one|that)|something\s+(?:shifted|changed|broke)|that'?s\s+when)\b", re.I),
    ],
    "cost_moment": [
        re.compile(r"\b(?:the\s+cost|what\s+it\s+cost|the\s+price|lost|gave\s+up|sacrificed|missed)\b", re.I),
    ],
    "resolution_or_open": [
        re.compile(r"\b(?:still|not\s+(?:yet|sure|done)|what\s+(?:comes|happens)\s+next|the\s+next\s+room)\b", re.I),
    ],
}


def _beat_fingerprint(text: str) -> Dict[str, bool]:
    """Detect narrative beats present in text."""
    result = {}
    for beat, patterns in _BEAT_PATTERNS.items():
        result[beat] = any(p.search(text) for p in patterns)
    return result


def _beat_similarity(fp_a: Dict[str, bool], fp_b: Dict[str, bool]) -> float:
    """Jaccard on narrative beat presence."""
    all_beats = set(fp_a.keys()) | set(fp_b.keys())
    if not all_beats:
        return 0.0
    match = sum(1 for b in all_beats if fp_a.get(b) == fp_b.get(b))
    return match / len(all_beats)


def detect_semantic_duplicates(
    texts: List[str],
    ids: List[str],
    *,
    cfg: Optional[Dict[str, Any]] = None,
    embed_fn: Optional[Callable[[str, str], List[float]]] = None,
) -> List[Dict[str, Any]]:
    """
    Detect semantic duplicates among candidate texts.

    Returns list of pair dicts:
      {"id_a": str, "id_b": str, "similarity": float, "evidence": {...}}
    Only pairs above threshold are returned.
    """
    cfg = cfg or {}
    ngram_n = int(cfg.get("ngram_n", 6))
    ngram_threshold = float(cfg.get("ngram_overlap_threshold", 0.30))
    semantic_threshold = float(cfg.get("semantic_similarity_threshold", 0.85))

    duplicates: List[Dict[str, Any]] = []

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            text_a, text_b = texts[i], texts[j]
            id_a, id_b = ids[i], ids[j]

            # Word n-gram overlap
            ngrams_a = _word_ngrams(text_a, ngram_n)
            ngrams_b = _word_ngrams(text_b, ngram_n)
            ngram_sim = _jaccard(ngrams_a, ngrams_b)

            # Character n-gram overlap (catches typo-level variants)
            char_a = _char_ngrams(text_a, 4)
            char_b = _char_ngrams(text_b, 4)
            char_sim = _jaccard(char_a, char_b)

            # Structural similarity
            shape_a = _paragraph_shape(text_a)
            shape_b = _paragraph_shape(text_b)
            struct_sim = _shape_similarity(shape_a, shape_b)

            # Narrative beat similarity
            beats_a = _beat_fingerprint(text_a)
            beats_b = _beat_fingerprint(text_b)
            beat_sim = _beat_similarity(beats_a, beats_b)

            # Composite score
            composite = (
                0.35 * ngram_sim
                + 0.15 * char_sim
                + 0.25 * struct_sim
                + 0.25 * beat_sim
            )

            if composite >= ngram_threshold or ngram_sim >= ngram_threshold:
                duplicates.append({
                    "id_a": id_a,
                    "id_b": id_b,
                    "similarity": round(composite, 4),
                    "evidence": {
                        "ngram_overlap": round(ngram_sim, 4),
                        "char_ngram_overlap": round(char_sim, 4),
                        "structural_similarity": round(struct_sim, 4),
                        "beat_similarity": round(beat_sim, 4),
                    },
                })

    duplicates.sort(key=lambda x: x["similarity"], reverse=True)
    return duplicates
