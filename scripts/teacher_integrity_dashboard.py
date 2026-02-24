#!/usr/bin/env python3
"""
Teacher Integrity Dashboard: aggregate per-teacher reports.
Authority: specs/TEACHER_INTEGRITY_SPEC.md §10.2.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Teacher integrity dashboard (aggregate)")
    ap.add_argument("--reports", default=None, help="Dir of pre-generated report JSON files (optional)")
    ap.add_argument("--repo", default=None, help="Repo root (to run teacher_integrity_report per teacher)")
    ap.add_argument("--out", default=None, help="Write summary JSON here")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT
    registry_path = repo / "config" / "teachers" / "teacher_registry.yaml"
    reg = _load_yaml(registry_path)
    teachers = list(reg.get("teachers", {}).keys())

    def run_report(teacher_id: str, repo_path: Path) -> dict:
        spec = importlib.util.spec_from_file_location(
            "teacher_integrity_report",
            repo_path / "scripts" / "teacher_integrity_report.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.run_report(teacher_id, repo_path)

    reports = []
    if args.reports:
        reports_dir = Path(args.reports)
        for p in reports_dir.glob("*.json"):
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("teacher_id"):
                reports.append(d)
        for t in teachers:
            if not any(r.get("teacher_id") == t for r in reports):
                reports.append({"teacher_id": t, "pass": True, "skipped": "no report file"})
    else:
        for t in teachers:
            bank = repo / "SOURCE_OF_TRUTH" / "teacher_banks" / t
            if bank.exists():
                try:
                    reports.append(run_report(t, repo))
                except Exception as e:
                    reports.append({"teacher_id": t, "pass": False, "error": str(e)})
            else:
                reports.append({"teacher_id": t, "pass": True, "skipped": "no teacher bank"})

    # Build summary
    summary = {
        "teachers_analyzed": len(reports),
        "teachers": [r.get("teacher_id") for r in reports],
        "doctrine_violations": sum(1 for r in reports if r.get("vocabulary", {}).get("vocabulary_violations")),
        "all_pass": all(r.get("pass", True) for r in reports),
        "reports": reports,
    }
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Wrote {args.out}")

    print("TEACHER INTEGRITY SUMMARY")
    print(f"  Teachers analyzed: {summary['teachers_analyzed']}")
    print(f"  Doctrine/vocabulary violations: {summary['doctrine_violations']}")
    print(f"  Overall: {'PASS' if summary['all_pass'] else 'REVIEW'}")
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
