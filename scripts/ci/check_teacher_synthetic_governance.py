#!/usr/bin/env python3
"""
CI: Teacher synthetic governance (plan §5.6). Recompute counts from atom_ids + atom_sources; do not trust stored counts.
Rules: no placeholders; synthetic ratio caps; native ratio min; teacher_sourced ratio min; max synthetic per book; doctrine consistency.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

DEFAULTS = {
    "synthetic_ratio_total_max": 0.40,
    "synthetic_ratio_story_max": 0.30,
    "synthetic_ratio_exercise_max": 0.50,
    "synthetic_ratio_hook_max": 0.50,
    "teacher_native_ratio_min": 0.60,
    "teacher_sourced_ratio_min": 0.70,
    "max_synthetic_atoms_per_book": 15,
    "require_no_placeholders_teacher_mode": True,
}


def _is_placeholder_or_silence(atom_id: str) -> bool:
    return isinstance(atom_id, str) and (atom_id.startswith("placeholder:") or atom_id.startswith("silence:"))


def _counts_from_slots(atom_ids: list, atom_sources: list | None) -> tuple[int, int, int, int]:
    """Recompute from final slot list: native, synthetic, practice_fallback, placeholders."""
    native = synthetic = fallback = placeholders = 0
    sources = atom_sources if atom_sources and len(atom_sources) == len(atom_ids) else [None] * len(atom_ids)
    for aid, src in zip(atom_ids, sources):
        if _is_placeholder_or_silence(aid):
            placeholders += 1
            continue
        if src == "teacher_native":
            native += 1
        elif src == "teacher_synthetic":
            synthetic += 1
        elif src == "practice_fallback":
            fallback += 1
        else:
            native += 1  # treat unknown as native for non-teacher
    return native, synthetic, fallback, placeholders


def check_book(plan: dict, cfg: dict) -> tuple[bool, list[str], dict]:
    """Return (passed, errors, diagnostic)."""
    errors: list[str] = []
    if not plan.get("teacher_mode") or not plan.get("teacher_id"):
        return True, [], {}
    atom_ids = plan.get("atom_ids") or []
    atom_sources = plan.get("atom_sources") or []
    native, synthetic, fallback, placeholders = _counts_from_slots(atom_ids, atom_sources)
    total = native + synthetic + fallback + placeholders
    total_content = native + synthetic + fallback

    diagnostic = {
        "plan_id": plan.get("plan_id") or plan.get("plan_hash"),
        "teacher_id": plan.get("teacher_id"),
        "doctrine_fingerprint": plan.get("doctrine_fingerprint"),
        "counts": {"teacher_native": native, "teacher_synthetic": synthetic, "practice_fallback": fallback, "placeholders": placeholders},
        "total_atoms": total,
        "total_content": total_content,
    }

    if cfg.get("require_no_placeholders_teacher_mode", True) and placeholders > 0:
        errors.append("Teacher mode: placeholders present (Rule 1)")

    if total_content == 0:
        diagnostic["synthetic_ratio_total"] = 0.0
        diagnostic["teacher_native_ratio_total"] = 0.0
        diagnostic["teacher_sourced_ratio"] = 0.0
        return len(errors) == 0, errors, diagnostic

    synth_ratio = synthetic / total_content if total_content else 0
    native_ratio = native / total if total else 0
    teacher_sourced = (native + synthetic) / total if total else 0

    diagnostic["synthetic_ratio_total"] = round(synth_ratio, 4)
    diagnostic["teacher_native_ratio_total"] = round(native_ratio, 4)
    diagnostic["teacher_sourced_ratio"] = round(teacher_sourced, 4)

    if synth_ratio > cfg.get("synthetic_ratio_total_max", DEFAULTS["synthetic_ratio_total_max"]):
        errors.append(f"synthetic_ratio_total {synth_ratio:.4f} > max (Rule 2)")

    if native_ratio < cfg.get("teacher_native_ratio_min", DEFAULTS["teacher_native_ratio_min"]):
        errors.append(f"teacher_native_ratio_total {native_ratio:.4f} < min (Rule 5)")

    if teacher_sourced < cfg.get("teacher_sourced_ratio_min", DEFAULTS["teacher_sourced_ratio_min"]):
        errors.append(f"teacher_sourced_ratio {teacher_sourced:.4f} < min (Rule 7)")

    if synthetic > cfg.get("max_synthetic_atoms_per_book", DEFAULTS["max_synthetic_atoms_per_book"]):
        errors.append(f"synthetic count {synthetic} > max per book (Rule 6)")

    if synthetic > 0 and not plan.get("doctrine_fingerprint"):
        errors.append("synthetic atoms present but doctrine_fingerprint missing (Rule 4)")

    return len(errors) == 0, errors, diagnostic


def main() -> int:
    ap = argparse.ArgumentParser(description="Check teacher synthetic governance (CI)")
    ap.add_argument("plan", nargs="*", help="Plan JSON file(s)")
    ap.add_argument("--config", help="Config YAML/JSON for thresholds")
    ap.add_argument("--out", default=None, help="Write artifacts/teacher_synthetic_report.json")
    args = ap.parse_args()
    cfg = dict(DEFAULTS)
    if args.config and Path(args.config).exists():
        data = json.loads(Path(args.config).read_text(encoding="utf-8"))
        cfg.update(data.get("teacher_synthetic_governance") or data)
    reports = []
    all_errors: list[str] = []
    for path in args.plan or []:
        p = Path(path)
        if not p.exists():
            continue
        plan = json.loads(p.read_text(encoding="utf-8"))
        passed, errs, diag = check_book(plan, cfg)
        reports.append(diag)
        if not passed:
            all_errors.extend([f"[{p.name}] {e}" for e in errs])
    if args.out:
        out_path = REPO_ROOT / "artifacts" / "teacher_synthetic_report.json" if args.out == "1" else Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({"books": reports, "passed": len(all_errors) == 0}, indent=2), encoding="utf-8")
    if all_errors:
        for e in all_errors:
            print(e, file=sys.stderr)
        print("TEACHER SYNTHETIC GOVERNANCE: FAIL", file=sys.stderr)
        return 1
    print("TEACHER SYNTHETIC GOVERNANCE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
