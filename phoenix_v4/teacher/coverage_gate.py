"""
Teacher Mode: mandatory pre-compile coverage gate.
Validates teacher atom inventory against required slots (from format_plan + arc) before compile.
Runs after arc selected and format expanded; fails with TeacherCoverageError and writes gap report on gaps.
Authority: plan §1–2, §7; Gate M (slot type compatibility).
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TEACHER_BANKS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"


class TeacherCoverageError(Exception):
    """Raised when teacher_mode and required slots exceed available teacher atoms (pre-compile gate)."""


def _approved_dir(teacher_id: str) -> Path:
    return TEACHER_BANKS_ROOT / teacher_id / "approved_atoms"


def _get_emotional_curve(arc: Any) -> list[int]:
    """Extract emotional_curve (band per chapter) from arc object or dict."""
    if arc is None:
        return []
    if isinstance(arc, dict):
        curve = arc.get("emotional_curve") or []
        return [int(x) for x in curve]
    return list(getattr(arc, "emotional_curve", []))


def _get_slot_definitions_for_required(
    format_plan: dict[str, Any],
    chapter_count: Optional[int] = None,
) -> list[list[str]]:
    """
    Return slot_definitions with same expansion as compiler: length must match chapter_count.
    If format_plan has one row, expand to chapter_count; else use as-is (caller must ensure length).
    """
    slot_definitions = format_plan.get("slot_definitions") or []
    if not isinstance(slot_definitions, list):
        return []
    ch = chapter_count or int(format_plan.get("chapter_count") or format_plan.get("target_chapter_count", 12))
    if len(slot_definitions) == ch:
        return [list(row) for row in slot_definitions]
    if len(slot_definitions) == 1 and isinstance(slot_definitions[0], list):
        template = list(slot_definitions[0])
        return [template[:] for _ in range(ch)]
    if len(slot_definitions) > ch:
        return [list(slot_definitions[i]) for i in range(ch)]
    template = list(slot_definitions[-1]) if slot_definitions else []
    extra = [template[:] for _ in range(ch - len(slot_definitions))]
    return [list(row) for row in slot_definitions] + extra


def compute_required_slots(
    book_spec: dict[str, Any],
    format_plan: dict[str, Any],
    arc: Any,
) -> tuple[dict[str, int], dict[str, int]]:
    """
    Compute required slot counts from final expanded format + arc.
    Returns (required_by_slot_type, required_story_by_band).
    Use the same slot_definitions the compiler will use (after arc alignment; section_reorder does not change counts).
    """
    chapter_count = int(format_plan.get("chapter_count") or format_plan.get("target_chapter_count", 12))
    slot_definitions = _get_slot_definitions_for_required(format_plan, chapter_count)
    emotional_curve = _get_emotional_curve(arc)
    if len(emotional_curve) != chapter_count and emotional_curve:
        # Pad or trim to match
        if len(emotional_curve) > chapter_count:
            emotional_curve = emotional_curve[:chapter_count]
        else:
            emotional_curve = emotional_curve + [3] * (chapter_count - len(emotional_curve))
    elif not emotional_curve:
        emotional_curve = [3] * chapter_count

    required_by_slot: dict[str, int] = defaultdict(int)
    required_story_by_band: dict[str, int] = defaultdict(int)
    for ch_idx, row in enumerate(slot_definitions):
        for st in row:
            slot_type = str(st).strip().upper()
            if not slot_type:
                continue
            required_by_slot[slot_type] += 1
            if slot_type == "STORY":
                band = emotional_curve[ch_idx] if ch_idx < len(emotional_curve) else 3
                required_story_by_band[str(band)] += 1
    return dict(required_by_slot), dict(required_story_by_band)


def compute_available_teacher_atoms(teacher_id: str) -> dict[str, int]:
    """Count approved teacher atoms per slot type (directories under approved_atoms/)."""
    root = _approved_dir(teacher_id)
    out: dict[str, int] = defaultdict(int)
    if not root.exists():
        return dict(out)
    for slot_dir in root.iterdir():
        if not slot_dir.is_dir():
            continue
        slot = slot_dir.name
        count = sum(1 for f in slot_dir.iterdir() if f.suffix in (".yaml", ".yml", ".json"))
        out[slot] = count
    return dict(out)


def compute_story_band_inventory(teacher_id: str) -> dict[str, int]:
    """Count STORY atoms per emotional band from approved_atoms/STORY/*.yaml."""
    root = _approved_dir(teacher_id) / "STORY"
    bands: dict[str, int] = defaultdict(int)
    if not root.exists():
        return dict(bands)
    try:
        import yaml
    except ImportError:
        return dict(bands)
    for f in root.iterdir():
        if f.suffix not in (".yaml", ".yml"):
            continue
        try:
            data = yaml.safe_load(f.read_text()) or {}
            band = data.get("band") or data.get("BAND") or 3
            bands[str(band)] = bands.get(str(band), 0) + 1
        except Exception:
            bands["3"] = bands.get("3", 0) + 1
    return dict(bands)


def make_gap_report(
    teacher_id: str,
    required_by_slot: dict[str, int],
    required_story_by_band: dict[str, int],
    available_by_slot: dict[str, int],
    story_band_inventory: dict[str, int],
    book_spec: dict[str, Any],
    format_plan: dict[str, Any],
    arc: Any,
    fallback_required: bool = False,
) -> dict[str, Any]:
    """Build gap report dict (for artifacts/teacher_coverage_report.json)."""
    gaps_by_slot: dict[str, Any] = {}
    slot_types_in_format = set(required_by_slot.keys())
    for slot_type in sorted(slot_types_in_format):
        need = required_by_slot.get(slot_type, 0)
        have = available_by_slot.get(slot_type, 0)
        if slot_type == "STORY":
            gaps_story = {}
            for band, need_b in required_story_by_band.items():
                have_b = story_band_inventory.get(band, 0)
                if need_b > have_b:
                    gaps_story[f"band_{band}"] = need_b - have_b
            total_missing = sum(gaps_story.values())
            if total_missing > 0:
                gaps_by_slot["STORY"] = gaps_story if gaps_story else {"total_missing": total_missing}
            else:
                gaps_by_slot["STORY"] = {}
        else:
            if need > have:
                gaps_by_slot[slot_type] = {"total_missing": need - have}
            else:
                gaps_by_slot[slot_type] = {}
    return {
        "teacher_id": teacher_id,
        "topic_id": book_spec.get("topic_id") or book_spec.get("topic", ""),
        "persona_id": book_spec.get("persona_id") or book_spec.get("persona", ""),
        "format_id": format_plan.get("format_id") or format_plan.get("format_structural_id") or "",
        "arc_id": getattr(arc, "arc_id", None) or (arc.get("arc_id") if isinstance(arc, dict) else ""),
        "required_by_slot": dict(required_by_slot),
        "required_story_by_band": required_story_by_band,
        "available_by_slot": available_by_slot,
        "story_band_inventory": story_band_inventory,
        "gaps": gaps_by_slot,
        "fallback_required": fallback_required,
    }


def run_coverage_gate(
    book_spec: dict[str, Any],
    format_plan: dict[str, Any],
    arc: Any,
    teacher_exercise_fallback: bool = False,
    artifacts_dir: Optional[Path] = None,
) -> tuple[bool, Optional[dict[str, Any]]]:
    """
    Run mandatory teacher coverage gate (after arc + format expanded, before compile).
    Returns (passed, gap_report_dict). If not passed, caller must write gap_report to artifacts and raise TeacherCoverageError.
    Gate M: every slot_type in format_plan must have sufficient teacher atoms (or EXERCISE with fallback_required when fallback enabled and teacher pool > 0).
    """
    import json as _json
    teacher_id = (book_spec.get("teacher_id") or "").strip()
    if not teacher_id or teacher_id == "default_teacher":
        return True, None

    required_by_slot, required_story_by_band = compute_required_slots(book_spec, format_plan, arc)
    available_by_slot = compute_available_teacher_atoms(teacher_id)
    story_band_inventory = compute_story_band_inventory(teacher_id)

    fallback_required = False
    slot_types_in_format = set(required_by_slot.keys())

    for slot_type in slot_types_in_format:
        need = required_by_slot.get(slot_type, 0)
        if need == 0:
            continue
        have = available_by_slot.get(slot_type, 0)
        if slot_type == "STORY":
            for band, need_b in required_story_by_band.items():
                have_b = story_band_inventory.get(band, 0)
                if need_b > have_b:
                    report = make_gap_report(
                        teacher_id,
                        required_by_slot,
                        required_story_by_band,
                        available_by_slot,
                        story_band_inventory,
                        book_spec,
                        format_plan,
                        arc,
                        fallback_required=False,
                    )
                    if artifacts_dir:
                        (artifacts_dir / "teacher_coverage_report.json").write_text(
                            _json.dumps(report, indent=2),
                            encoding="utf-8",
                        )
                    return False, report
        elif slot_type == "EXERCISE":
            if need > have:
                if teacher_exercise_fallback and have > 0:
                    fallback_required = True  # allow pass; record shortage in report
                else:
                    report = make_gap_report(
                        teacher_id,
                        required_by_slot,
                        required_story_by_band,
                        available_by_slot,
                        story_band_inventory,
                        book_spec,
                        format_plan,
                        arc,
                        fallback_required=False,
                    )
                    if artifacts_dir:
                        (artifacts_dir / "teacher_coverage_report.json").write_text(
                            _json.dumps(report, indent=2),
                            encoding="utf-8",
                        )
                    return False, report
        else:
            if need > have:
                report = make_gap_report(
                    teacher_id,
                    required_by_slot,
                    required_story_by_band,
                    available_by_slot,
                    story_band_inventory,
                    book_spec,
                    format_plan,
                    arc,
                    fallback_required=False,
                )
                if artifacts_dir:
                    (artifacts_dir / "teacher_coverage_report.json").write_text(
                        _json.dumps(report, indent=2),
                        encoding="utf-8",
                    )
                return False, report

    report = make_gap_report(
        teacher_id,
        required_by_slot,
        required_story_by_band,
        available_by_slot,
        story_band_inventory,
        book_spec,
        format_plan,
        arc,
        fallback_required=fallback_required,
    )
    return True, report
