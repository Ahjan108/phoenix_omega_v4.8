"""
Embedding thesis alignment for EI V1.

SQLite-backed cache for embeddings. get_embedding fetches or computes,
thesis_similarity returns cosine similarity between thesis and candidate text.
"""
from __future__ import annotations

import hashlib
import math
import sqlite3
from pathlib import Path
from typing import Any, Callable, List, Optional


class EmbeddingCache:
    """SQLite-backed cache for embeddings."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else None
        self._conn: Optional[sqlite3.Connection] = None

    def _get_conn(self) -> Optional[sqlite3.Connection]:
        if self.db_path is None:
            return None
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS embeddings "
                "(text_hash TEXT PRIMARY KEY, embedding_blob BLOB, model TEXT)"
            )
        return self._conn

    def get(self, text: str, model: str = "") -> Optional[List[float]]:
        """Retrieve cached embedding if present."""
        conn = self._get_conn()
        if conn is None:
            return None
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        row = conn.execute(
            "SELECT embedding_blob FROM embeddings WHERE text_hash = ? AND model = ?",
            (h, model),
        ).fetchone()
        if row is None:
            return None
        import json
        return json.loads(row[0])

    def set(self, text: str, embedding: List[float], model: str = "") -> None:
        """Store embedding in cache."""
        conn = self._get_conn()
        if conn is None:
            return
        import json
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        blob = json.dumps(embedding)
        conn.execute(
            "INSERT OR REPLACE INTO embeddings (text_hash, embedding_blob, model) VALUES (?, ?, ?)",
            (h, blob, model),
        )
        conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


def get_embedding(
    text: str,
    embed_fn: Callable[[str, str], List[float]],
    model: str = "",
    cache: Optional[EmbeddingCache] = None,
) -> List[float]:
    """
    Get embedding for text. Uses cache if provided and hit; otherwise calls embed_fn.
    """
    if cache:
        cached = cache.get(text, model)
        if cached is not None:
            return cached
    vec = embed_fn(text, model)
    if cache:
        cache.set(text, vec, model)
    return vec


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def thesis_similarity(
    thesis: str,
    candidate_text: str,
    embed_fn: Callable[[str, str], List[float]],
    model: str = "",
    cache: Optional[EmbeddingCache] = None,
) -> float:
    """
    Compute cosine similarity between thesis and candidate text embeddings.
    Returns value in [0, 1] (cosine is typically [-1, 1]; we clamp and rescale).
    """
    if not thesis or not candidate_text:
        return 0.0
    vec_t = get_embedding(thesis, embed_fn, model, cache)
    vec_c = get_embedding(candidate_text, embed_fn, model, cache)
    sim = _cosine_similarity(vec_t, vec_c)
    # Rescale [-1, 1] -> [0, 1]
    return max(0.0, min(1.0, (sim + 1.0) / 2.0))
