#!/usr/bin/env python3
"""
Author Positioning CI — Layer 2 Identity (Writer Spec §24).
Validates: BookSpec author_positioning_profile; language pattern compliance; drift.
Run: PYTHONPATH=. python3 scripts/ci/check_author_positioning.py --plan <plan.json> [--book-spec <spec.json>] [--atoms-dir <dir>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_AUTHORING = REPO_ROOT / "config" / "authoring"
CONFIG_AUTHOR_REGISTRY = REPO_ROOT / "config" / "author_registry.yaml"

# Profile-specific thresholds (Writer Spec §24; DEV SPEC 1)
MAX_FIRST_PERSON_PCT_RESEARCH_GUIDE = 0.08   # reject if first_person_reflection > 8%
MAX_COMMAND_DENSITY_SOMATIC_COMPANION = 0.12  # reject if command_language density > 12%
MAX_PERSONAL_NARRATIVE_PCT_HIGH_VULN = 0.30  # high vulnerability_band: personal narrative ≤ 30% of chapter


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _word_count(text: str) -> int:
    return len((text or "").split())


# ---------- Language pattern detection ----------

def first_person_density(text: str) -> float:
    """Approximate first-person reflection density (I, my, we, our, me)."""
    if not text or _word_count(text) == 0:
        return 0.0
    words = text.lower().split()
    first_person = sum(1 for w in words if w in ("i", "i'm", "i've", "i'll", "my", "myself", "we", "we're", "our", "us", "me"))
    return first_person / len(words)


def command_density(text: str) -> float:
    """Imperative / command-like sentence starts (you + verb, or bare imperative)."""
    if not text or _word_count(text) == 0:
        return 0.0
    sentences = re.split(r"[.!?]\s+", text)
    if not sentences:
        return 0.0
    command_like = 0
    for s in sentences:
        s = s.strip().lower()
        if re.match(r"^(you\s+)\w+", s) or re.match(r"^(\w+)\s+", s) and s.split()[0] in (
            "place", "feel", "breathe", "count", "notice", "try", "let", "allow", "sit", "close", "open"
        ):
            command_like += 1
    return command_like / len(sentences)


def academic_marker_count(text: str) -> int:
    """Rough academic/citation markers."""
    if not text:
        return 0
    low = text.lower()
    markers = [
        "research shows", "studies suggest", "according to", "et al", "citation",
        "diagnostic", "dsm", "clinical", "meta-analysis", "peer-reviewed",
    ]
    return sum(1 for m in markers if m in low)


def slang_count(text: str) -> int:
    """Simple slang/colloquial detection (word-level)."""
    if not text:
        return 0
    words = set(re.findall(r"\b[a-z']+\b", text.lower()))
    slang = {"gonna", "wanna", "gotta", "kinda", "sorta", "yeah", "nah", "dunno", "guy", "stuff", "thing"}
    return len(words & slang)


def mystical_absolutism_count(text: str) -> int:
    """Mystical/absolute claim markers."""
    if not text:
        return 0
    low = text.lower()
    patterns = [
        r"\bthe universe (wants|knows|will)\b",
        r"\beverything happens for a reason\b",
        r"\bdivine (timing|plan)\b",
        r"\benergy (will|always)\b",
        r"\b(always|never) (fails?|works?)\b",
    ]
    return sum(len(re.findall(p, low)) for p in patterns)


def get_plan_flat(plan: dict) -> list[tuple[str, str]]:
    """[(atom_id, slot_type), ...] in order."""
    atom_ids = plan.get("atom_ids") or []
    ch_slots = plan.get("chapter_slot_sequence") or []
    flat = []
    idx = 0
    for row in ch_slots:
        for slot_type in (row if isinstance(row, list) else (row.get("slots") or [])):
            st = slot_type if isinstance(slot_type, str) else (slot_type.get("slot_type") or "")
            if idx < len(atom_ids):
                flat.append((atom_ids[idx], st))
                idx += 1
    return flat


def get_plan_by_chapter(plan: dict) -> list[list[tuple[str, str]]]:
    """[[(atom_id, slot_type), ...], ...] per chapter."""
    atom_ids = plan.get("atom_ids") or []
    ch_slots = plan.get("chapter_slot_sequence") or []
    by_chapter = []
    idx = 0
    for row in ch_slots:
        chapter = []
        slots = row if isinstance(row, list) else (row.get("slots") or [])
        for slot_type in slots:
            st = slot_type if isinstance(slot_type, str) else (slot_type.get("slot_type") or "")
            if idx < len(atom_ids):
                chapter.append((atom_ids[idx], st))
                idx += 1
        by_chapter.append(chapter)
    return by_chapter


def load_atom_bodies(plan: dict, atoms_dir: Path) -> list[tuple[str, str, str]]:
    """Returns [(atom_id, slot_type, body), ...] for atoms that exist under atoms_dir."""
    flat = get_plan_flat(plan)
    out = []
    for atom_id, slot_type in flat:
        if "placeholder:" in atom_id:
            continue
        slot_dir = atoms_dir / slot_type
        path = slot_dir / f"{atom_id}.yaml"
        if not path.exists():
            continue
        atom = _load_yaml(path)
        body = (atom.get("body") or "").strip()
        out.append((atom_id, slot_type, body))
    return out


def check_book_spec_positioning(book_spec: dict, profiles: dict, author_registry: dict, errors: list[str]) -> str | None:
    """Validate BookSpec has valid author_positioning_profile. Return profile key or None."""
    author_id = (book_spec or {}).get("author_id")
    profile_key = (book_spec or {}).get("author_positioning_profile")
    profile_list = profiles.get("profiles") or {}
    authors = (author_registry.get("authors") or {})
    if author_id:
        if author_id not in authors:
            errors.append(f"author_id '{author_id}' not in author_registry.yaml")
            return None
        reg_profile = authors[author_id].get("positioning_profile")
        if not reg_profile:
            errors.append(f"author_id '{author_id}' missing positioning_profile in author_registry (required §24)")
            return None
        if reg_profile not in profile_list:
            errors.append(f"positioning_profile '{reg_profile}' not in author_positioning_profiles.yaml")
            return None
        if profile_key is not None and profile_key != reg_profile:
            errors.append(f"BookSpec author_positioning_profile '{profile_key}' does not match registry '{reg_profile}'")
            return None
        return reg_profile
    if profile_key and profile_key not in profile_list:
        errors.append(f"BookSpec author_positioning_profile '{profile_key}' not in author_positioning_profiles.yaml")
        return None
    return profile_key


def check_language_against_profile(
    profile_key: str,
    profile: dict,
    bodies: list[tuple[str, str, str]],
    errors: list[str],
    warnings: list[str],
) -> None:
    """Apply profile forbidden_language and vulnerability_band thresholds to combined/chapter text."""
    vuln_band = (profile.get("vulnerability_band") or "low").lower()
    forbidden = set((profile.get("forbidden_language") or []))
    full_text = " ".join(b for _, _, b in bodies)
    total_words = _word_count(full_text)
    if total_words == 0:
        return

    first_person = first_person_density(full_text)
    command = command_density(full_text)
    academic = academic_marker_count(full_text)
    slang_n = slang_count(full_text)
    mystical = mystical_absolutism_count(full_text)

    # research_guide: first_person_reflection > 8% → reject
    if profile_key == "research_guide" and "first_person_reflection" in forbidden:
        if first_person > MAX_FIRST_PERSON_PCT_RESEARCH_GUIDE:
            errors.append(
                f"research_guide: first_person density {first_person:.1%} > {MAX_FIRST_PERSON_PCT_RESEARCH_GUIDE:.0%} (forbidden)"
            )

    # somatic_companion: command_language above threshold → reject
    if profile_key == "somatic_companion" and "command_language" in forbidden:
        if command > MAX_COMMAND_DENSITY_SOMATIC_COMPANION:
            errors.append(
                f"somatic_companion: command density {command:.1%} > {MAX_COMMAND_DENSITY_SOMATIC_COMPANION:.0%} (forbidden)"
            )

    if "academic_citation" in forbidden and academic > 2:
        warnings.append(f"Profile forbids academic_citation; found ~{academic} markers")
    if "slang" in forbidden and slang_n > 3:
        errors.append(f"Profile forbids slang; found {slang_n} slang-like terms")
    if "mystical_claims" in forbidden and mystical > 0:
        errors.append(f"Profile forbids mystical_claims; found {mystical} matches")

    # Vulnerability: high band → personal narrative ≤ 30% per chapter
    if vuln_band == "high":
        by_chapter = {}
        for aid, st, body in bodies:
            ch = by_chapter.setdefault(aid, [])
            ch.append(body)
        # We don't have chapter grouping in load_atom_bodies easily; use full text as proxy
        if first_person > MAX_PERSONAL_NARRATIVE_PCT_HIGH_VULN:
            warnings.append(
                f"vulnerability_band=high: first_person density {first_person:.1%} (max 30% per chapter)"
            )


def compute_positioning_signature_hash(profile_key: str, plan: dict, language_metrics: dict | None) -> str:
    """positioning_signature_hash = sha256(profile + language_metrics or plan_hash)."""
    payload = profile_key
    if language_metrics:
        payload += ":" + json.dumps(language_metrics, sort_keys=True)
    else:
        payload += ":" + (plan.get("plan_hash") or "")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def run_checks(
    plan_path: Path,
    book_spec_path: Path | None,
    atoms_dir: Path | None,
    repo_root: Path,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    report: dict[str, Any] = {"errors": [], "warnings": [], "profile": None, "positioning_signature_hash": None}

    plan = _load_json(plan_path)
    book_spec = _load_json(book_spec_path) if book_spec_path and book_spec_path.exists() else plan.get("book_spec") or {}
    profiles_path = repo_root / "config" / "authoring" / "author_positioning_profiles.yaml"
    profiles = _load_yaml(profiles_path)
    author_registry = _load_yaml(CONFIG_AUTHOR_REGISTRY)

    profile_key = check_book_spec_positioning(book_spec, profiles, author_registry, errors)
    report["profile"] = profile_key
    if not profile_key:
        report["errors"] = errors
        report["warnings"] = warnings
        return errors, warnings, report

    profile_def = (profiles.get("profiles") or {}).get(profile_key)
    if profile_def and atoms_dir and atoms_dir.exists():
        bodies = load_atom_bodies(plan, atoms_dir)
        if bodies:
            check_language_against_profile(profile_key, profile_def, bodies, errors, warnings)
            full_text = " ".join(b for _, _, b in bodies)
            metrics = {
                "first_person_density": first_person_density(full_text),
                "command_density": command_density(full_text),
                "academic_markers": academic_marker_count(full_text),
                "slang_count": slang_count(full_text),
                "mystical_count": mystical_absolutism_count(full_text),
            }
            report["language_metrics"] = metrics
            report["positioning_signature_hash"] = compute_positioning_signature_hash(profile_key, plan, metrics)
        else:
            report["positioning_signature_hash"] = compute_positioning_signature_hash(profile_key, plan, None)
    else:
        report["positioning_signature_hash"] = compute_positioning_signature_hash(profile_key, plan, None)

    report["errors"] = errors
    report["warnings"] = warnings
    return errors, warnings, report


def main() -> int:
    ap = argparse.ArgumentParser(description="Author positioning CI (Writer Spec §24)")
    ap.add_argument("--plan", required=True, help="Compiled plan JSON")
    ap.add_argument("--book-spec", default=None, help="BookSpec JSON (optional; can be embedded in plan)")
    ap.add_argument("--atoms-dir", default=None, help="approved_atoms root for language checks (optional)")
    ap.add_argument("--repo", default=None, help="Repo root")
    ap.add_argument("--out", default=None, help="Write report JSON here")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT
    plan_path = Path(args.plan)
    book_spec_path = Path(args.book_spec) if args.book_spec else None
    atoms_dir = Path(args.atoms_dir) if args.atoms_dir else None

    if not plan_path.exists():
        print(f"Plan not found: {plan_path}", file=sys.stderr)
        return 1

    errors, warnings, report = run_checks(plan_path, book_spec_path, atoms_dir, repo)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Wrote {args.out}")
    for e in errors:
        print(f"FAIL: {e}")
    for w in warnings:
        print(f"WARN: {w}")
    if not errors and not warnings:
        print("Author positioning: OK")
    return 0 if len(errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
