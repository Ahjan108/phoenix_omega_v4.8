"""
Plan schema V4: variation knobs and backward compatibility.
Authority: Structural Variation + Anti-Cluster Storytelling System (V4) Dev Spec.
All new plans must populate variation fields; missing fields are auto-filled with defaults.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

# Defaults for backward compatibility when plan JSON lacks variation fields.
VARIATION_DEFAULTS = {
    "book_structure_id": "linear_transformation",
    "journey_shape_id": "recognition_to_agency",
    "motif_id": "motif_pattern",
    "section_reorder_mode": "none",
    "reframe_profile_id": "balanced",
    "chapter_archetypes": [],  # filled to len(chapter_count) from structure + journey
}
# Canonical key order for variation_signature hash (spec: include angle_id).
VARIATION_SIGNATURE_KEYS = (
    "book_structure_id",
    "journey_shape_id",
    "motif_id",
    "section_reorder_mode",
    "reframe_profile_id",
    "angle_id",
    "topic_id",
    "persona_id",
    "arc_id",
    "installment_number",
)


def apply_variation_defaults(plan: dict[str, Any], chapter_count: int = 0) -> dict[str, Any]:
    """
    Return plan with variation fields present. Missing fields get defaults.
    If chapter_archetypes is missing or wrong length, fill with derived default sequence.
    """
    out = dict(plan)
    for key, default in VARIATION_DEFAULTS.items():
        if key not in out or out[key] is None:
            out[key] = default
    arch = out.get("chapter_archetypes") or []
    if isinstance(arch, list) and chapter_count > 0 and len(arch) != chapter_count:
        # Default: repeat establish -> integrate pattern
        base = ["establish", "expose", "destabilize", "reframe", "stabilize", "integrate"]
        out["chapter_archetypes"] = [base[i % len(base)] for i in range(chapter_count)]
    return out


def compute_variation_signature(
    book_structure_id: str,
    journey_shape_id: str,
    motif_id: str,
    section_reorder_mode: str,
    reframe_profile_id: str,
    angle_id: str = "",
    topic_id: str = "",
    persona_id: str = "",
    arc_id: str = "",
    installment_number: Optional[int] = None,
    chapter_archetypes: Optional[list[str]] = None,
) -> str:
    """
    Deterministic SHA256 over canonicalized knob tuple (spec §3, §6).
    Includes angle_id to align with V4.7.
    """
    payload = {
        "book_structure_id": book_structure_id,
        "journey_shape_id": journey_shape_id,
        "motif_id": motif_id,
        "section_reorder_mode": section_reorder_mode,
        "reframe_profile_id": reframe_profile_id,
        "angle_id": angle_id or "",
        "topic_id": topic_id or "",
        "persona_id": persona_id or "",
        "arc_id": arc_id or "",
        "installment_number": installment_number if installment_number is not None else 0,
        "chapter_archetypes": tuple(chapter_archetypes) if chapter_archetypes else (),
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]


def get_plan_variation_signature(plan: dict[str, Any]) -> str:
    """
    Compute variation_signature from plan dict. Uses existing variation_signature
    if present and recomputes from knobs otherwise; applies defaults for missing keys.
    """
    if plan.get("variation_signature"):
        return plan["variation_signature"]
    chapter_count = 0
    ch_seq = plan.get("chapter_slot_sequence") or []
    if ch_seq:
        chapter_count = len(ch_seq)
    applied = apply_variation_defaults(plan, chapter_count)
    return compute_variation_signature(
        book_structure_id=applied.get("book_structure_id", VARIATION_DEFAULTS["book_structure_id"]),
        journey_shape_id=applied.get("journey_shape_id", VARIATION_DEFAULTS["journey_shape_id"]),
        motif_id=applied.get("motif_id", VARIATION_DEFAULTS["motif_id"]),
        section_reorder_mode=applied.get("section_reorder_mode", VARIATION_DEFAULTS["section_reorder_mode"]),
        reframe_profile_id=applied.get("reframe_profile_id", VARIATION_DEFAULTS["reframe_profile_id"]),
        angle_id=applied.get("angle_id", ""),
        topic_id=applied.get("topic_id", ""),
        persona_id=applied.get("persona_id", ""),
        arc_id=applied.get("arc_id", ""),
        installment_number=applied.get("installment_number"),
        chapter_archetypes=applied.get("chapter_archetypes"),
    )
