"""
Part 3.1 slot resolver: deterministic selection per slot, no reuse in-book.
Selector hash algorithm: SHA256(selector_key) -> first 16 bytes big-endian int -> modulo len(available).
Do not substitute Python's built-in hash() (salted per process, non-deterministic).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from phoenix_v4.planning.pool_index import AtomEntry, PoolIndex


@dataclass
class ResolverContext:
    persona_id: str
    topic_id: str
    slot_definitions: list[list[str]]
    used_atom_ids: set[str]
    pool_index: "PoolIndex"
    selector_key_prefix: str
    # Arc-First: required BAND per chapter for STORY slots (chapter_idx -> 1-5). None = no filter.
    required_band_by_chapter: Optional[dict[int, int]] = None
    # Repetition decay: semantic_family single-use per book (no two atoms from same family).
    used_semantic_families: Optional[set[str]] = None
    # Angle Integration (V4.7): chapter 1 framing bias. Optional dict with framing_mode, etc.
    angle_context: Optional[dict] = None


def _selector_index(selector_key: str, available_count: int) -> int:
    """
    Deterministic index into available list. Mandatory algorithm:
    - SHA256 over selector_key (UTF-8 bytes)
    - First 16 bytes of digest as big-endian int
    - modulo len(available)
    Do not use Python's built-in hash() (salted per run).
    """
    if available_count <= 0:
        return 0
    digest = hashlib.sha256(selector_key.encode("utf-8")).digest()
    # First 16 bytes (or full 32) as big-endian integer
    n = int.from_bytes(digest[:16], "big")
    return n % available_count


def resolve_slot(
    slot_type: str,
    chapter_idx: int,
    slot_idx: int,
    context: ResolverContext,
) -> Optional[str]:
    """
    Return one atom_id for this slot from the pool, or None if pool empty or all used.
    No reuse: only atoms not in context.used_atom_ids are considered.
    Repetition decay: atoms with metadata.semantic_family already used are excluded.
    Determinism: selector_key = prefix + slot_type + ch:slot; SHA256 then modulo.
    """
    pool = context.pool_index.get_pool(
        slot_type,
        context.persona_id,
        context.topic_id,
        None,
    )
    available = [e for e in pool if e.atom_id not in context.used_atom_ids]
    # Repetition decay: exclude atoms whose semantic_family was already used this book
    if context.used_semantic_families is not None:
        available = [
            e for e in available
            if (e.metadata or {}).get("semantic_family") not in context.used_semantic_families
        ]
    # Arc-First: filter STORY by required BAND for this chapter when arc is set
    if slot_type == "STORY" and context.required_band_by_chapter is not None:
        ch_band = context.required_band_by_chapter.get(chapter_idx)
        if ch_band is not None:
            available = [e for e in available if (e.metadata or {}).get("band") == ch_band]
    if not available:
        return None
    # Angle Integration (V4.7): chapter 1 framing bias — rank by angle_bias.score_atom then atom_id; deterministic pick
    if chapter_idx == 0 and context.angle_context:
        from phoenix_v4.planning.angle_bias import score_atom
        def _key(e: "AtomEntry") -> tuple:
            return (-score_atom(e.metadata, slot_type, context.angle_context), e.atom_id)
        available.sort(key=_key)
    else:
        # Lexicographic sort by atom_id (raw UTF-8; no Unicode normalization)
        available.sort(key=lambda e: e.atom_id)
    selector_key = f"{context.selector_key_prefix}:{slot_type}:ch{chapter_idx:02d}:s{slot_idx:02d}"
    idx = _selector_index(selector_key, len(available))
    chosen = available[idx]
    # Track semantic_family for repetition decay (single-use per book)
    fam = (chosen.metadata or {}).get("semantic_family")
    if fam is not None and context.used_semantic_families is not None:
        context.used_semantic_families.add(str(fam))
    return chosen.atom_id
