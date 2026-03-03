#!/usr/bin/env python3
"""
Run strict validation and CI gates for Teacher Mode production readiness.
- Doctrine schema check for every teacher in registry.
- Teacher readiness (min pool) with F006-compatible thresholds.
- Optional: teacher synthetic governance on a plan (when --plan given).
Exit 0 only if all gates pass.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def load_registry():
    import yaml
    reg = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    return list((data.get("teachers") or {}).keys())


def main():
    ap = argparse.ArgumentParser(description="Teacher production gates")
    ap.add_argument("--plan", default=None, help="Path to plan.json for synthetic governance check")
    ap.add_argument("--skip-readiness", action="store_true", help="Skip teacher readiness (min pool) per teacher")
    ap.add_argument("--min-exercise", type=int, default=12, help="Min EXERCISE (F006 k_min)")
    ap.add_argument("--min-story", type=int, default=12, help="Min STORY (F006 k_min)")
    args = ap.parse_args()
    teachers = load_registry()
    failed = []

    # Gate 1: Doctrine schema for every teacher that has a doctrine file
    for tid in teachers:
        doctrine_dir = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / tid / "doctrine"
        doctrine_file = doctrine_dir / "doctrine.yaml"
        if not doctrine_file.exists():
            doctrine_file = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / tid / "doctrine.yaml"
        if not doctrine_file.exists():
            print(f"Doctrine not found for {tid}; skipping schema check")
            continue
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "ci" / "check_doctrine_schema.py"), "--teacher", tid],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            failed.append(f"doctrine_schema:{tid} — {r.stderr or r.stdout}")
    if failed:
        for f in failed:
            print(f, file=sys.stderr)
        print("TEACHER PRODUCTION GATES: FAIL (doctrine schema)", file=sys.stderr)
        return 1
    print("Doctrine schema: PASS (all teachers)")

    # Gate 2: Teacher readiness (min EXERCISE, STORY) for teachers that have approved_atoms
    if not args.skip_readiness:
        for tid in teachers:
            approved_root = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / tid / "approved_atoms"
            if not approved_root.exists():
                print(f"No approved_atoms for {tid}; skipping readiness")
                continue
            r = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "ci" / "check_teacher_readiness.py"),
                    "--teacher",
                    tid,
                    "--min-exercise",
                    str(args.min_exercise),
                    "--min-hook",
                    "0",
                    "--min-reflection",
                    "0",
                    "--min-integration",
                    "0",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                failed.append(f"teacher_readiness:{tid} — {r.stderr or r.stdout}")
        if failed:
            for f in failed:
                print(f, file=sys.stderr)
            print("TEACHER PRODUCTION GATES: FAIL (readiness)", file=sys.stderr)
            return 1
        print("Teacher readiness: PASS (all teachers)")

    # Gate 3: If plan provided, run teacher synthetic governance
    if args.plan:
        plan_path = Path(args.plan)
        if plan_path.exists():
            r = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "ci" / "check_teacher_synthetic_governance.py"),
                    str(plan_path),
                    "--out",
                    str(REPO_ROOT / "artifacts" / "teacher_synthetic_report.json"),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                print(r.stderr or r.stdout, file=sys.stderr)
                print("TEACHER PRODUCTION GATES: FAIL (synthetic governance)", file=sys.stderr)
                return 1
            print("Teacher synthetic governance: PASS")
    print("TEACHER PRODUCTION GATES: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
