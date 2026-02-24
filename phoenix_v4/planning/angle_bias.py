"""
Angle Integration (V4.7): Chapter 1 framing bias scoring. No pool fork; weighting only.
Deterministic: score_atom returns 0–2; tie-break by atom_id. No candidates match → neutral.
"""
from __future__ import annotations

from typing import Any, Optional

FRAMING_MODES = ("debunk", "framework", "reveal", "leverage")


def score_atom(
    atom_metadata: Optional[dict[str, Any]],
    slot_type: str,
    angle_context: dict[str, Any],
) -> int:
    """
    Score 0–2 for chapter 1 angle bias. angle_context must have framing_mode.
    angle_affinity list on atom boosts to 2 if framing_mode in list; else rule-based 0 or 1.
    """
    meta = atom_metadata or {}
    framing = (angle_context.get("framing_mode") or "").strip().lower()
    if not framing:
        return 0
    role = (meta.get("emotional_role") or "").lower()
    family = (meta.get("semantic_family") or "").lower()
    affinity = meta.get("angle_affinity")
    if isinstance(affinity, list) and framing in [str(a).lower() for a in affinity]:
        return 2
    if framing == "debunk":
        if slot_type == "STORY" and family in ("failed_attempt", "misbelief"):
            return 1
        if slot_type == "REFLECTION" and role == "destabilization":
            return 1
    elif framing == "framework":
        if slot_type == "STORY" and family == "discovery":
            return 1
        if slot_type == "REFLECTION" and role == "recognition":
            return 1
    elif framing == "reveal":
        if slot_type == "HOOK" and role == "destabilization":
            return 1
        if slot_type == "STORY" and family == "revelation":
            return 1
    elif framing == "leverage":
        if slot_type == "STORY" and family == "mechanism":
            return 1
        if slot_type == "REFLECTION" and role == "reframe":
            return 1
    return 0
