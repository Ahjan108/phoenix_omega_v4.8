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
    Score 0–3 for chapter 1: angle (framing) 0–2 + opening_style bonus 0–1.
    angle_context may have framing_mode and/or opening_style_id (Controlled Intro/Conclusion Variation).
    """
    meta = atom_metadata or {}
    score = 0
    framing = (angle_context.get("framing_mode") or "").strip().lower()
    if framing:
        role = (meta.get("emotional_role") or "").lower()
        family = (meta.get("semantic_family") or "").lower()
        affinity = meta.get("angle_affinity")
        if isinstance(affinity, list) and framing in [str(a).lower() for a in affinity]:
            score = 2
        elif framing == "debunk":
            if slot_type == "STORY" and family in ("failed_attempt", "misbelief"):
                score = 1
            elif slot_type == "REFLECTION" and role == "destabilization":
                score = 1
        elif framing == "framework":
            if slot_type == "STORY" and family == "discovery":
                score = 1
            elif slot_type == "REFLECTION" and role == "recognition":
                score = 1
        elif framing == "reveal":
            if slot_type == "HOOK" and role == "destabilization":
                score = 1
            elif slot_type == "STORY" and family == "revelation":
                score = 1
        elif framing == "leverage":
            if slot_type == "STORY" and family == "mechanism":
                score = 1
            elif slot_type == "REFLECTION" and role == "reframe":
                score = 1
    # Opening recognition style: soft bias (boost atoms with matching opening_style metadata)
    opening_style_id = (angle_context.get("opening_style_id") or "").strip().lower()
    if opening_style_id:
        atom_style = (meta.get("opening_style") or "").strip().lower()
        if atom_style and atom_style == opening_style_id:
            score += 1
    return min(score, 3)


def score_ending_atom(atom_metadata: Optional[dict[str, Any]], integration_ending_style_id: str) -> int:
    """
    Score 0 or 1 for final-chapter INTEGRATION ending style bias (Controlled Intro/Conclusion Variation).
    Atoms with metadata ending_style matching integration_ending_style_id get 1; else 0.
    """
    if not (integration_ending_style_id or integration_ending_style_id.strip()):
        return 0
    meta = atom_metadata or {}
    atom_style = (meta.get("ending_style") or "").strip().lower()
    want = integration_ending_style_id.strip().lower()
    return 1 if atom_style and atom_style == want else 0
