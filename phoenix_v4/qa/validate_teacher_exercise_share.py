"""
Plan §6.1: When teacher_mode and any EXERCISE from practice_fallback, teacher exercise share ≥ 60%.
(teacher-sourced EXERCISE count) / (total EXERCISE) >= 0.6 → PASS else FAIL.
"""
from __future__ import annotations


def _is_placeholder_or_silence(aid: str) -> bool:
    return isinstance(aid, str) and (aid.startswith("placeholder:") or aid.startswith("silence:"))


def validate_teacher_exercise_share(
    chapter_slot_sequence: list[list[str]],
    atom_ids: list[str],
    atom_sources: list | None,
    min_share: float = 0.60,
) -> tuple[bool, str]:
    """
    When teacher_mode and there are EXERCISE slots, require teacher-sourced EXERCISE share ≥ min_share.
    Returns (passed, error_message). error_message empty when passed.
    """
    if not atom_ids or not chapter_slot_sequence:
        return True, ""
    sources = atom_sources if atom_sources and len(atom_sources) == len(atom_ids) else [None] * len(atom_ids)
    idx = 0
    exercise_teacher = 0  # native + synthetic
    exercise_fallback = 0
    for row in chapter_slot_sequence:
        for slot_type in row:
            if idx >= len(atom_ids):
                break
            if str(slot_type).strip().upper() != "EXERCISE":
                idx += 1
                continue
            aid = atom_ids[idx]
            src = sources[idx] if idx < len(sources) else None
            idx += 1
            if _is_placeholder_or_silence(aid):
                continue
            if src == "practice_fallback":
                exercise_fallback += 1
            elif src in ("teacher_native", "teacher_synthetic"):
                exercise_teacher += 1
            else:
                exercise_teacher += 1
        if idx >= len(atom_ids):
            break
    total_exercise = exercise_teacher + exercise_fallback
    if total_exercise == 0:
        return True, ""
    if exercise_fallback == 0:
        return True, ""
    share = exercise_teacher / total_exercise
    if share < min_share:
        return False, (
            f"Teacher exercise share {share:.2%} < {min_share:.0%} when fallback used "
            f"(teacher EXERCISE={exercise_teacher}, fallback={exercise_fallback}, total={total_exercise})."
        )
    return True, ""


def validate_plan(plan: dict, min_share: float = 0.60) -> tuple[bool, str]:
    """Validate plan dict. Returns (passed, error_message)."""
    if not plan.get("teacher_mode"):
        return True, ""
    ch_seq = plan.get("chapter_slot_sequence") or []
    aids = plan.get("atom_ids") or []
    srcs = plan.get("atom_sources") or []
    return validate_teacher_exercise_share(ch_seq, aids, srcs, min_share=min_share)
