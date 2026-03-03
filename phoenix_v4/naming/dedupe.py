"""
In-memory deduplication: TF-IDF index and n-gram overlap.
Phase 1: no file writes. Authority: SYSTEMS_DOCUMENTATION §29.2.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

# Lightweight TF-IDF: no sklearn dependency for Phase 1
def _tokenize(text: str) -> list[str]:
    t = (text or "").lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    return [w for w in t.split() if w]


def _tf(tokens: list[str]) -> Counter:
    return Counter(tokens)


def build_tfidf_index(titles: list[str]) -> Any:
    """
    Build index from existing titles. Empty list = no dedupe.
    Returns an opaque TfidfIndex (dict-based) for cosine_similarity.
    """
    if not titles:
        return {"idf": {}, "docs": [], "vocab": set()}
    vocab: set[str] = set()
    doc_tfs: list[Counter] = []
    for t in titles:
        toks = _tokenize(t)
        vocab.update(toks)
        doc_tfs.append(Counter(toks))
    # IDF: log((N+1)/(df+1))+1
    N = len(doc_tfs)
    df: Counter = Counter()
    for tf in doc_tfs:
        for w in tf:
            df[w] += 1
    idf = {}
    for w in vocab:
        idf[w] = 1.0 + (1.0 if N == 0 else __import__("math").log((N + 1) / (df.get(w, 0) + 1)))
    # Store tf vectors and idf for cosine
    docs_tf = [dict(tf) for tf in doc_tfs]
    return {"idf": idf, "docs": docs_tf, "vocab": vocab, "N": N}


def _tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    tf = Counter(tokens)
    v = {}
    for w, c in tf.items():
        v[w] = c * idf.get(w, 1.0)
    return v


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a.get(w, 0) * b.get(w, 0) for w in set(a) | set(b))
    na = sum(x * x for x in a.values()) ** 0.5
    nb = sum(x * x for x in b.values()) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def cosine_similarity(candidate: str, index: Any) -> float:
    """Return max cosine similarity between candidate and any indexed title."""
    if not index or not index.get("docs"):
        return 0.0
    toks = _tokenize(candidate)
    idf = index.get("idf") or {}
    v = _tfidf_vector(toks, idf)
    if not v:
        return 0.0
    best = 0.0
    for doc_tf in index["docs"]:
        doc_v = {w: c * idf.get(w, 1.0) for w, c in doc_tf.items()}
        best = max(best, _cosine(v, doc_v))
    return best


def ngram_overlap(candidate: str, existing: list[str], n: int = 3) -> float:
    """Return max n-gram overlap fraction (0.0–1.0) vs existing strings."""
    def ngrams(s: str) -> set[str]:
        toks = _tokenize(s)
        if len(toks) < n:
            return set()
        return set(" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1))
    c_ng = ngrams(candidate)
    if not c_ng:
        return 0.0
    best = 0.0
    for ex in existing:
        e_ng = ngrams(ex)
        if not e_ng:
            continue
        overlap = len(c_ng & e_ng) / len(c_ng)
        best = max(best, overlap)
    return best
