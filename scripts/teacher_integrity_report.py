#!/usr/bin/env python3
"""
Per-teacher integrity report: doctrine, vocabulary, exercise counts.
Authority: specs/TEACHER_INTEGRITY_SPEC.md. No prose scoring; structural only.
"""
from __future__ import annotations

import argparse
import json
import sys
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


def _load_atom_bodies(approved_root: Path, slot_type: str) -> list[str]:
    bodies = []
    slot_dir = approved_root / slot_type
    if not slot_dir.exists():
        return bodies
    for path in slot_dir.glob("*.yaml"):
        data = _load_yaml(path)
        if data and isinstance(data.get("body"), str):
            bodies.append(data["body"])
    return bodies


def run_report(teacher_id: str, repo_root: Path) -> dict:
    banks = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id
    config = repo_root / "config" / "teachers" / "teacher_registry.yaml"
    doctrine_path = banks / "doctrine" / "doctrine.yaml"
    approved = banks / "approved_atoms"

    reg = _load_yaml(config)
    teacher_reg = reg.get("teachers", {}).get(teacher_id, {}) if teacher_id else {}
    doctrine = _load_yaml(doctrine_path)

    # Doctrine boundaries (from registry)
    allowed_topics = teacher_reg.get("allowed_topics", [])
    disallowed_topics = teacher_reg.get("disallowed_topics", [])
    allowed_engines = teacher_reg.get("allowed_engines", [])
    allowed_resolution_types = teacher_reg.get("allowed_resolution_types", [])
    identity_shift_allowed = teacher_reg.get("identity_shift_allowed", False)

    # Vocabulary: optional core_terms / forbidden_terms in doctrine; else use glossary and forbidden_claims
    core_terms = doctrine.get("core_terms")
    if core_terms is None and doctrine.get("glossary"):
        core_terms = []
        for g in doctrine["glossary"]:
            if isinstance(g, str):
                core_terms.append(g.split(" / ")[0].strip().lower())
            else:
                core_terms.append(str(g).lower())
    forbidden_terms = doctrine.get("forbidden_terms")
    if forbidden_terms is None and doctrine.get("forbidden_claims"):
        forbidden_terms = [str(c).lower() for c in doctrine["forbidden_claims"]]
    core_terms = core_terms or []
    forbidden_terms = forbidden_terms or []

    # Gather all approved atom bodies
    all_bodies = []
    slot_counts = {}
    for slot in ("STORY", "EXERCISE", "QUOTE", "TEACHING", "HOOK", "SCENE", "INTEGRATION"):
        bodies = _load_atom_bodies(approved, slot)
        slot_counts[slot] = len(bodies)
        all_bodies.extend(bodies)
    combined_text = " ".join(all_bodies).lower()

    # Vocabulary checks
    core_present = sum(1 for t in core_terms if t.lower() in combined_text)
    core_total = len(core_terms)
    forbidden_found = [t for t in forbidden_terms if t.lower() in combined_text]
    vocabulary_ok = len(forbidden_found) == 0

    return {
        "teacher_id": teacher_id,
        "doctrine_boundaries": {
            "allowed_topics": allowed_topics,
            "disallowed_topics": disallowed_topics,
            "allowed_engines": allowed_engines,
            "allowed_resolution_types": allowed_resolution_types,
            "identity_shift_allowed": identity_shift_allowed,
        },
        "atom_counts_by_slot": slot_counts,
        "vocabulary": {
            "core_terms_defined": core_total,
            "core_terms_present_in_atoms": core_present,
            "forbidden_terms_defined": len(forbidden_terms),
            "forbidden_terms_found": forbidden_found,
            "vocabulary_violations": not vocabulary_ok,
        },
        "exercise_identity": {
            "exercise_atom_count": slot_counts.get("EXERCISE", 0),
            "total_atoms": sum(slot_counts.values()),
        },
        "pass": vocabulary_ok,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Per-teacher integrity report")
    ap.add_argument("--teacher", required=True, help="Teacher id")
    ap.add_argument("--repo", default=None, help="Repo root (default: parent of scripts/)")
    ap.add_argument("--out", default=None, help="Write JSON report here")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT
    report = run_report(args.teacher.strip().lower(), repo)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Wrote {args.out}")
    print(f"Teacher: {report['teacher_id']}")
    print(f"  Atoms: {report['atom_counts_by_slot']}")
    print(f"  Vocabulary: core {report['vocabulary']['core_terms_present_in_atoms']}/{report['vocabulary']['core_terms_defined']} present; forbidden found: {report['vocabulary']['forbidden_terms_found']}")
    print(f"  Pass: {report['pass']}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
