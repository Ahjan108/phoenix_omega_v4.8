#!/usr/bin/env python3
"""
Teacher Presence Score (TPS) report for Teacher Mode compiled plans.
Structural only: no prose inspection. Authority: specs/TEACHER_MODE_STRUCTURAL_SPEC.md §3.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def get_chapter_slot_sequence(plan: dict) -> list[list[str]]:
    """Extract chapter_slot_sequence from plan dict."""
    seq = plan.get("chapter_slot_sequence")
    if seq is not None:
        return [list(ch) for ch in seq]
    return []


def compute_tps_per_chapter(chapter_slot_sequence: list[list[str]]) -> list[int]:
    """
    TPS = 2 * (STORY count in chapter) + 2 * (EXERCISE count in chapter).
    When teacher_mode is true, all atoms are teacher-sourced; no need to check atom_id.
    """
    out = []
    for ch_slots in chapter_slot_sequence:
        story_count = sum(1 for s in ch_slots if s == "STORY")
        exercise_count = sum(1 for s in ch_slots if s == "EXERCISE")
        tps = 2 * story_count + 2 * exercise_count
        out.append(tps)
    return out


def get_threshold(book_spec: dict | None, teacher_defaults: dict | None) -> int:
    """Resolve TPS threshold from teacher_dominance or default."""
    dominance = None
    if book_spec:
        dominance = book_spec.get("teacher_dominance")
    if not dominance and teacher_defaults:
        dominance = teacher_defaults.get("teacher_dominance")
    if dominance == "light":
        return 3
    if dominance == "strong":
        return 7
    return 5  # balanced default


def run_report(
    plan_path: Path,
    book_spec_path: Path | None = None,
    teacher_registry_path: Path | None = None,
    threshold_override: int | None = None,
) -> dict:
    """Produce TPS summary and per-chapter scores."""
    plan = {}
    if plan_path.exists():
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)
    book_spec = {}
    if book_spec_path and book_spec_path.exists():
        with open(book_spec_path, encoding="utf-8") as f:
            book_spec = json.load(f)
    teacher_id = (book_spec or plan).get("teacher_id") or plan.get("teacher_id")
    teacher_defaults = {}
    if teacher_registry_path and teacher_registry_path.exists() and teacher_id:
        reg = _load_yaml(teacher_registry_path)
        if isinstance(reg.get("teachers"), dict):
            teacher_defaults = reg["teachers"].get(teacher_id, {}).get("teacher_mode_defaults") or {}

    chapter_slot_sequence = get_chapter_slot_sequence(plan)
    tps_per_chapter = compute_tps_per_chapter(chapter_slot_sequence)
    threshold = threshold_override if threshold_override is not None else get_threshold(book_spec, teacher_defaults)
    flagged = [i + 1 for i, t in enumerate(tps_per_chapter) if t < threshold]
    avg_tps = sum(tps_per_chapter) / len(tps_per_chapter) if tps_per_chapter else 0

    return {
        "teacher_id": teacher_id,
        "teacher_mode": (book_spec or plan).get("teacher_mode", False),
        "chapter_count": len(chapter_slot_sequence),
        "tps_per_chapter": tps_per_chapter,
        "tps_threshold": threshold,
        "chapters_below_threshold": flagged,
        "average_tps": round(avg_tps, 1),
        "pass": len(flagged) == 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Teacher Presence Score (TPS) report for Teacher Mode plans")
    ap.add_argument("--plan", required=True, help="Path to compiled plan JSON")
    ap.add_argument("--book-spec", default=None, help="Path to BookSpec JSON (optional)")
    ap.add_argument("--teacher-registry", default=None, help="Path to teacher_registry.yaml (optional)")
    ap.add_argument("--threshold", type=int, default=None, help="Override TPS threshold (e.g. 4)")
    ap.add_argument("--out", default=None, help="Write report JSON here")
    args = ap.parse_args()
    repo = REPO_ROOT
    registry = Path(args.teacher_registry) if args.teacher_registry else repo / "config" / "teachers" / "teacher_registry.yaml"
    report = run_report(
        Path(args.plan),
        Path(args.book_spec) if args.book_spec else None,
        registry,
        args.threshold,
    )
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Wrote {args.out}")
    print("Teacher Presence Summary:")
    print(f"  Chapters: {report['chapter_count']}  TPS/chapter: {report['tps_per_chapter']}")
    print(f"  Average TPS: {report['average_tps']}  Threshold: {report['tps_threshold']}")
    if report["chapters_below_threshold"]:
        print(f"  FLAG: Chapters below threshold: {report['chapters_below_threshold']}")
        print(f"  Pass: {report['pass']}")
    else:
        print("  Pass: True")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
