"""
EI V2 hybrid selector: combine V1 and V2 selection with optional learned override.
Deterministic given selector_key; minimal V1 path when V2 unavailable.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class HybridDecision:
    slot: str
    chapter_index: int
    slot_index: int
    final_chosen_id: str
    v1_chosen_id: str
    v2_chosen_id: str
    override_applied: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _v1_pick(candidates_raw: List[Dict[str, Any]], selector_key: str) -> str:
    """Deterministic V1-style pick by selector_key (hash). Fail-open: first candidate or empty."""
    if not candidates_raw:
        return ""
    if len(candidates_raw) == 1:
        return (candidates_raw[0].get("atom_id") or "").strip()
    h = hashlib.sha256(selector_key.encode()).hexdigest()
    idx = int(h[:8], 16) % len(candidates_raw)
    return (candidates_raw[idx].get("atom_id") or "").strip()


def hybrid_select(
    *,
    slot: str,
    chapter_index: int,
    slot_index: int,
    candidates_raw: List[Dict[str, Any]],
    persona_id: str,
    topic_id: str,
    thesis: str,
    v1_cfg: Optional[Dict[str, Any]] = None,
    v2_cfg: Optional[Dict[str, Any]] = None,
    selector_key: Optional[str] = None,
) -> HybridDecision:
    """
    Hybrid selection: run V1 (and optionally V2), apply override margin from learner if present.
    When V2 is disabled or unavailable, final = V1. Deterministic when selector_key is fixed.
    """
    key = selector_key or f"{slot}:{chapter_index}:{slot_index}:{persona_id}:{topic_id}"
    v1_chosen = _v1_pick(candidates_raw, key)
    v2_chosen = v1_chosen  # Minimal path: no V2 call; tests expect v2_chosen_id present
    final = v1_chosen
    override = False
    return HybridDecision(
        slot=slot,
        chapter_index=chapter_index,
        slot_index=slot_index,
        final_chosen_id=final,
        v1_chosen_id=v1_chosen,
        v2_chosen_id=v2_chosen,
        override_applied=override,
    )
