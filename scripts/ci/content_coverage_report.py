#!/usr/bin/env python3
"""
Single content-coverage report: atoms (STORY + non-STORY), plan-time coverage_check, teacher readiness,
and Pearl Prime v2 slot readiness (PIVOT/TAKEAWAY/THREAD/PERMISSION).

Answers "is any book prose/content missing?" by:
1. Running atoms coverage (persona×topic×engine STORY + persona×topic non-STORY) — same logic as test_atoms_coverage_100_percent.
2. Running plan-time coverage_check (K-table + pool sizes for discovered persona×topic pairs).
3. Running teacher readiness (min EXERCISE/HOOK/REFLECTION/INTEGRATION) per teacher from teacher_registry.
4. Running Pearl Prime v2 slot check (PIVOT/TAKEAWAY/THREAD/PERMISSION) via book_script_content_validation:
   - PIVOT: `pivot` field on STORY atoms in teacher banks
   - TAKEAWAY: `chapter_thesis` field in master_arcs (20 entries per arc)
   - THREAD: `chapter_thread` field in master_arcs (20 entries per arc)
   - PERMISSION: `chapter_permission` field in master_arcs (high-cost intents only)
   See docs/CHAPTER_THESIS_BANK.md for machine-readable lookup tables to auto-populate arc fields.

Outputs:
- artifacts/content_coverage_report.json — machine-readable summary and per-teacher readiness.
- One-page summary to stdout (missing STORY tuples, missing non-STORY slots, plan errors, teachers with gaps,
  v2 slot arc field gaps).

Usage: from repo root, python scripts/ci/content_coverage_report.py [--out FILE] [--no-teachers] [--no-v2-slots]
See: docs/CONTENT_COVERAGE_ANALYSIS.md, docs/DOCS_INDEX.md § How to check for missing book content.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _run_story_coverage() -> tuple[bool, str]:
    """Reuse test_atoms_coverage_100_percent STORY coverage. Returns (passed, message)."""
    try:
        from tests.test_atoms_coverage_100_percent import run_sim_test
        return run_sim_test()
    except Exception as e:
        return False, f"Atoms STORY check failed: {e}"


def _run_non_story_coverage() -> tuple[bool, str]:
    """Reuse test_atoms_coverage_100_percent non-STORY coverage. Returns (passed, message)."""
    try:
        from tests.test_atoms_coverage_100_percent import run_non_story_sim_test
        return run_non_story_sim_test()
    except Exception as e:
        return False, f"Atoms non-STORY check failed: {e}"


def _run_plan_coverage_check() -> tuple[bool, list[str]]:
    """Run coverage_checker over discovered (persona, topic). Returns (all_passed, errors)."""
    try:
        from phoenix_v4.planning.coverage_checker import run_coverage_check
        return run_coverage_check(atoms_root=REPO_ROOT / "atoms", format_structural_id="F006", mode="strict")
    except Exception as e:
        return False, [str(e)]


def _load_teacher_ids() -> list[str]:
    """Teachers from config/teachers/teacher_registry.yaml."""
    reg = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"
    if not reg.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(reg.read_text(encoding="utf-8"))
        return list((data.get("teachers") or {}).keys())
    except Exception:
        return []


def _run_teacher_readiness(teacher_id: str, min_exercise: int = 12) -> tuple[bool, str]:
    """Run check_teacher_readiness for one teacher. Returns (passed, detail)."""
    script = REPO_ROOT / "scripts" / "ci" / "check_teacher_readiness.py"
    if not script.exists():
        return True, "check_teacher_readiness.py not found; skipped"
    r = subprocess.run(
        [
            sys.executable,
            str(script),
            "--teacher",
            teacher_id,
            "--min-exercise",
            str(min_exercise),
            "--min-hook", "0",
            "--min-reflection", "0",
            "--min-integration", "0",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if r.returncode == 0:
        return True, (r.stdout or "").strip() or "PASS"
    return False, (r.stderr or r.stdout or "FAIL").strip()


def _run_v2_slots_check() -> tuple[bool, dict]:
    """Run Pearl Prime v2 slot check via book_script_content_validation. Returns (passed, result_dict)."""
    try:
        from scripts.book_script_content_validation import check_v2_slots
        result = check_v2_slots(REPO_ROOT)
        return result.get("status") == "ok", result
    except Exception as e:
        return False, {"error": str(e), "status": "error"}


def _run_all_teacher_readiness(skip_teachers: bool) -> dict[str, dict]:
    """Run teacher readiness for each teacher. Returns { teacher_id: { "ok": bool, "detail": str } }."""
    out: dict[str, dict] = {}
    if skip_teachers:
        return out
    teachers = _load_teacher_ids()
    for tid in teachers:
        approved = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / tid / "approved_atoms"
        if not approved.exists():
            out[tid] = {"ok": True, "detail": "no approved_atoms; skipped"}
            continue
        ok, detail = _run_teacher_readiness(tid)
        out[tid] = {"ok": ok, "detail": detail}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Single content-coverage report: atoms + plan coverage + teacher readiness"
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "artifacts" / "content_coverage_report.json",
        help="Output JSON path",
    )
    ap.add_argument(
        "--no-teachers",
        action="store_true",
        help="Skip teacher readiness (faster)",
    )
    ap.add_argument(
        "--no-v2-slots",
        action="store_true",
        help="Skip Pearl Prime v2 slot check (PIVOT/TAKEAWAY/THREAD/PERMISSION arc field check)",
    )
    args = ap.parse_args()

    story_ok, story_msg = _run_story_coverage()
    non_story_ok, non_story_msg = _run_non_story_coverage()
    plan_ok, plan_errors = _run_plan_coverage_check()
    teacher_results = _run_all_teacher_readiness(skip_teachers=args.no_teachers)
    v2_ok, v2_result = (True, {"status": "skipped"}) if args.no_v2_slots else _run_v2_slots_check()

    teachers_failed = [tid for tid, t in teacher_results.items() if not t.get("ok")]
    any_fail = not story_ok or not non_story_ok or not plan_ok or bool(teachers_failed) or not v2_ok

    report = {
        "story_coverage_ok": story_ok,
        "story_message": story_msg,
        "non_story_coverage_ok": non_story_ok,
        "non_story_message": non_story_msg,
        "plan_coverage_ok": plan_ok,
        "plan_coverage_errors": plan_errors,
        "teacher_readiness": teacher_results,
        "teachers_failed": teachers_failed,
        "v2_slots_ok": v2_ok,
        "v2_slots": v2_result,
        "summary_ok": not any_fail,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # One-page summary
    print("=== Content coverage report ===\n")
    print("1. Atoms STORY (persona × topic × engine):", "PASS" if story_ok else "FAIL")
    print("   ", story_msg[:200] + ("..." if len(story_msg) > 200 else ""))
    print()
    print("2. Atoms non-STORY (persona × topic × HOOK/SCENE/REFLECTION/EXERCISE/INTEGRATION):", "PASS" if non_story_ok else "FAIL")
    print("   ", non_story_msg[:200] + ("..." if len(non_story_msg) > 200 else ""))
    print()
    print("3. Plan coverage (K-table + pool sizes, discovered pairs):", "PASS" if plan_ok else "FAIL")
    if plan_errors:
        for e in plan_errors[:15]:
            print("   ", e)
        if len(plan_errors) > 15:
            print("   ... and", len(plan_errors) - 15, "more")
    print()
    print("4. Teacher readiness (min pool per teacher):", "PASS" if not teachers_failed else f"FAIL ({len(teachers_failed)} teachers)")
    if teachers_failed:
        for tid in teachers_failed[:10]:
            print("   ", tid, "—", (teacher_results.get(tid) or {}).get("detail", "")[:80])
        if len(teachers_failed) > 10:
            print("   ... and", len(teachers_failed) - 10, "more")
    print()
    if not args.no_v2_slots:
        print("5. Pearl Prime v2 slots (PIVOT/TAKEAWAY/THREAD/PERMISSION arc fields + atom pivot):", "PASS" if v2_ok else "FAIL")
        v2_counts = (v2_result.get("arc_issue_counts") or {})
        for issue, cnt in v2_counts.items():
            if cnt:
                print(f"   {issue}: {cnt} arcs")
        pivot_missing = v2_result.get("story_atoms_missing_pivot", 0)
        pivot_ok_count = v2_result.get("story_atoms_with_pivot", 0)
        if pivot_missing or pivot_ok_count:
            print(f"   STORY atoms pivot field: {pivot_ok_count} present / {pivot_missing} missing")
        if v2_result.get("error"):
            print("   error:", v2_result["error"])
        print()
    print("Report written to:", args.out.relative_to(REPO_ROOT))
    if any_fail:
        print("\nMissing content: fix STORY/non-STORY pools (see tests/test_atoms_coverage_100_percent), plan coverage (phoenix_v4/planning/coverage_checker), teacher pools (scripts/ci/check_teacher_readiness), or v2 slot arc fields (see docs/CHAPTER_THESIS_BANK.md for auto-populate tables).")
        return 1
    print("\nNo missing book content detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
