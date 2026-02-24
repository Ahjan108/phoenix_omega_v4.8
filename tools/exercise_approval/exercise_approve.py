#!/usr/bin/env python3
"""
Approve or reject a candidate exercise: copy to approved/ or log rejection.
Usage:
  python -m tools.exercise_approval.exercise_approve approve --id <exercise_id> [--source <path>]
  python -m tools.exercise_approval.exercise_approve reject --id <exercise_id> [--reason "reason"]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXERCISES_V4 = REPO_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4"
CANDIDATE_DIR = EXERCISES_V4 / "candidate"
APPROVED_DIR = EXERCISES_V4 / "approved"


def _find_candidate_by_id(exercise_id: str) -> Path | None:
    """Locate candidate YAML by exercise id (from content or filename)."""
    for path in (CANDIDATE_DIR / "_stubs").rglob("*.yaml") if (CANDIDATE_DIR / "_stubs").exists() else []:
        try:
            import yaml
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            if data.get("id") == exercise_id:
                return path
        except Exception:
            continue
    for path in CANDIDATE_DIR.rglob("*.yaml"):
        if path.name.startswith("."):
            continue
        try:
            import yaml
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            if data.get("id") == exercise_id:
                return path
        except Exception:
            continue
    return None


def cmd_approve(exercise_id: str, source: Path | None) -> int:
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required for exercise_approve", file=sys.stderr)
        return 1
    src = source or _find_candidate_by_id(exercise_id)
    if not src or not src.exists():
        print(f"ERROR: Candidate not found for id={exercise_id}", file=sys.stderr)
        return 1
    with open(src) as f:
        data = yaml.safe_load(f) or {}
    persona = (data.get("metadata") or {}).get("persona", "default")
    topic = (data.get("metadata") or {}).get("topic", "default")
    out_dir = APPROVED_DIR / str(persona) / str(topic)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{exercise_id}.yaml"
    data["approval"] = data.get("approval") or {}
    data["approval"]["status"] = "approved"
    with open(out_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f"Approved: {out_path}")
    return 0


def cmd_reject(exercise_id: str, reason: str) -> int:
    print(f"Rejected id={exercise_id}: {reason or '(no reason)'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Approve or reject exercise by id")
    sub = ap.add_subparsers(dest="cmd", required=True)
    app = sub.add_parser("approve")
    app.add_argument("--id", required=True, help="Exercise id (e.g. ex_breath_regulation_stub)")
    app.add_argument("--source", type=Path, help="Path to candidate YAML (default: find by id)")
    rej = sub.add_parser("reject")
    rej.add_argument("--id", required=True, help="Exercise id")
    rej.add_argument("--reason", default="", help="Reason for rejection")
    args = ap.parse_args()
    if args.cmd == "approve":
        return cmd_approve(args.id, getattr(args, "source", None))
    return cmd_reject(args.id, getattr(args, "reason", ""))


if __name__ == "__main__":
    sys.exit(main())
