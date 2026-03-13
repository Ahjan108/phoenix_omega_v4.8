"""
Pearl News teacher–story pairing (adapter spec §2.2).

Decide whether a teacher is a good fit for a given story.
"""
from __future__ import annotations

from typing import Any

from pearl_news.teacher_adapter.adapter import NewsTeacherPayload


def teacher_story_pairing_ok(
    payload: NewsTeacherPayload | None,
    story_context: dict[str, Any],
) -> tuple[bool, list[str]]:
    """
    Check if this teacher is a good fit for this story (spec §2.2).

    Required pairing questions:
    - Can this teacher explain this crisis in their own framework?
    - Is there a named practice or concrete practice family?
    - Is there a real youth behavior loop or lived tension here?
    - Is there a non-generic civic or behavioral bridge?

    Returns (ok: bool, reasons: list[str]) where reasons explain weak answers.
    """
    if payload is None:
        return False, ["No teacher payload available."]
    reasons: list[str] = []

    # Framework: need explicit framework term
    if not (payload.teacher_framework_term and len(payload.teacher_framework_term.strip()) > 5):
        reasons.append("Teacher framework term is weak or missing.")
    # Named practice
    if not (payload.teacher_named_practice and len(payload.teacher_named_practice.strip()) > 2):
        reasons.append("No named practice or concrete practice family.")
    # Diagnostic claim (crisis in their framework)
    if not (payload.teacher_diagnostic_claim and len(payload.teacher_diagnostic_claim.strip()) > 10):
        reasons.append("Diagnostic claim too weak to explain crisis in teacher's framework.")
    # Topic fit vs story topic
    topic = (story_context.get("topic") or story_context.get("news_topic") or "").lower()
    if topic and payload.topic_fit and topic != payload.topic_fit.lower():
        # Allow if topic_fit is a broader category; only warn if clearly mismatched
        if payload.topic_fit.lower() not in topic and topic not in payload.topic_fit.lower():
            reasons.append(f"Topic fit '{payload.topic_fit}' may not match story topic '{topic}'.")
    # Behavioral or civic bridge (non-generic)
    if not (payload.teacher_behavior_bridge and len(payload.teacher_behavior_bridge.strip()) > 15):
        reasons.append("Behavior bridge missing or too vague.")
    if not (payload.teacher_civic_bridge and len(payload.teacher_civic_bridge.strip()) > 10):
        reasons.append("Civic bridge missing or too generic.")

    ok = len(reasons) == 0
    return ok, reasons
