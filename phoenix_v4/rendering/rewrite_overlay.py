"""
ML rewrite overlay: build atom_id -> replacement text from rewrite_recs for render.
Conflict policy: when multiple recs target the same atom/slot, deterministic winner is
(1) highest confidence, (2) then newest timestamp. Overlay only — never mutate source atom files.
Staleness guard: if recs carry plan_hash and it does not match current plan, overlay is skipped.
Gated by ml_actions_enabled in config.
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def compute_plan_hash(plan: dict[str, Any]) -> str:
    """Stable hash of plan identity for staleness checks (atom_ids + plan_id)."""
    plan_id = (plan.get("plan_id") or plan.get("plan_hash") or "").strip()
    atom_ids = plan.get("atom_ids") or []
    payload = plan_id + json.dumps(atom_ids, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_rewrite_overlay(
    plan: dict[str, Any],
    rewrite_recs_path: Path,
    book_id: str,
    ml_actions_enabled: bool,
    disable_overlay_for_book_ids: Optional[List[str]] = None,
) -> Dict[str, str]:
    """
    Build atom_id -> replacement_text from rewrite_recs.jsonl for the given book.
    Only recs with atom_id and replacement_text are used. Conflict policy: highest
    confidence first, then newest timestamp. When ml_actions_enabled is False returns {}.
    """
    overlay: Dict[str, str] = {}
    if not ml_actions_enabled or not rewrite_recs_path.exists():
        return overlay

    book_id = (book_id or "").strip()
    if not book_id:
        return overlay
    blocklist = disable_overlay_for_book_ids or []
    if book_id in blocklist:
        logger.info("Rewrite overlay skipped for book_id=%s (disable_overlay_for_book_ids)", book_id)
        return overlay

    current_plan_hash = compute_plan_hash(plan)
    recs: list[dict[str, Any]] = []
    for line in rewrite_recs_path.read_text(encoding="utf-8").strip().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if row.get("book_id") != book_id:
                continue
            atom_id = row.get("atom_id")
            replacement_text = row.get("replacement_text")
            if not atom_id or replacement_text is None:
                continue
            recs.append(row)
        except json.JSONDecodeError:
            continue

    if not recs:
        return overlay

    for r in recs:
        ph = r.get("plan_hash")
        if ph and ph != current_plan_hash:
            logger.warning(
                "Rewrite overlay skipped: plan_hash mismatch (rec=%s vs current=%s); recs may be stale.",
                ph[:16], current_plan_hash[:16],
            )
            return overlay

    # Conflict policy: highest confidence first, then newest timestamp
    def sort_key(r: dict) -> tuple:
        conf = float(r.get("confidence", 0.0))
        ts = (r.get("ts") or "")[:26]
        return (-conf, ts)

    recs.sort(key=sort_key)
    for r in recs:
        aid = (r.get("atom_id") or "").strip()
        text = r.get("replacement_text")
        if aid and text is not None:
            overlay[aid] = str(text).strip()

    return overlay
