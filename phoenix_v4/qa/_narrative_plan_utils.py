"""Shared helpers for narrative gates: extract plan structure and STORY/SCENE atom IDs per chapter."""
from __future__ import annotations

from typing import Any


def _plan_attr(plan: dict | Any, key: str, default: Any = None) -> Any:
    if hasattr(plan, key):
        return getattr(plan, key, default)
    return (plan or {}).get(key, default)


def get_atom_ids(plan: dict | Any) -> list[str]:
    return list(_plan_attr(plan, "atom_ids") or [])


def get_chapter_slot_sequence(plan: dict | Any) -> list[list[str]]:
    return list(_plan_attr(plan, "chapter_slot_sequence") or [])


def get_chapter_count(plan: dict | Any) -> int:
    css = get_chapter_slot_sequence(plan)
    return len(css) if css else 0


def iter_chapter_slot_atom_ids(plan: dict | Any) -> list[tuple[int, int, str, str]]:
    """
    Yield (chapter_idx, slot_idx, slot_type, atom_id) for each slot.
    atom_id may be placeholder/silence; callers filter to real atom IDs.
    """
    atom_ids = get_atom_ids(plan)
    css = get_chapter_slot_sequence(plan)
    idx = 0
    out: list[tuple[int, int, str, str]] = []
    for ch, row in enumerate(css):
        for si, slot_type in enumerate(row):
            if idx < len(atom_ids):
                out.append((ch, si, slot_type, atom_ids[idx]))
            idx += 1
    return out


def get_story_atom_ids_by_chapter(plan: dict | Any) -> list[list[str]]:
    """Return list of lists: chapter_index -> list of STORY atom_ids (excluding placeholders/silence)."""
    css = get_chapter_slot_sequence(plan)
    atom_ids = get_atom_ids(plan)
    n_ch = len(css)
    by_ch: list[list[str]] = [[] for _ in range(n_ch)]
    idx = 0
    for ch, row in enumerate(css):
        if ch >= n_ch:
            break
        for slot_type in row:
            if idx >= len(atom_ids):
                break
            aid = atom_ids[idx]
            if (slot_type or "").upper() == "STORY" and "placeholder:" not in aid and "silence:" not in aid:
                by_ch[ch].append(aid)
            idx += 1
    return by_ch


def get_all_plan_atom_ids_for_metadata(plan: dict | Any) -> list[str]:
    """All atom IDs in plan that are real (not placeholder/silence). Used for callback/identity scanning."""
    atom_ids = get_atom_ids(plan)
    return [a for a in atom_ids if "placeholder:" not in a and "silence:" not in a]


def get_exercise_chapters(plan: dict | Any) -> list[int]:
    """Chapter indices (0-based) that contain an EXERCISE slot."""
    ex_ch = _plan_attr(plan, "exercise_chapters")
    if ex_ch is not None and isinstance(ex_ch, list):
        return list(ex_ch)
    # Derive from chapter_slot_sequence
    css = get_chapter_slot_sequence(plan)
    return [
        i for i, row in enumerate(css)
        if any((s or "").upper() == "EXERCISE" for s in row)
    ]


def get_emotional_curve(plan: dict | Any, arc: dict | Any = None) -> list[int]:
    """1-5 intensity per chapter. From plan.emotional_curve or arc.emotional_curve or dominant_band_sequence as fallback."""
    curve = _plan_attr(plan, "emotional_curve")
    if curve and len(curve) >= get_chapter_count(plan):
        return list(curve)[: get_chapter_count(plan)]
    if arc:
        ac = (arc.get("emotional_curve") if isinstance(arc, dict) else None) or getattr(arc, "emotional_curve", None)
        if ac and len(ac) >= get_chapter_count(plan):
            return list(ac)[: get_chapter_count(plan)]
    # Use dominant_band_sequence as proxy (bands 1-5)
    dbs = _plan_attr(plan, "dominant_band_sequence") or []
    n = get_chapter_count(plan)
    if len(dbs) >= n:
        return [int(b) if b is not None else 2 for b in dbs[:n]]
    return [2] * n
