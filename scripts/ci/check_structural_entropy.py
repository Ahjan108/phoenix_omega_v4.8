#!/usr/bin/env python3
"""
Structural entropy CI gate for Teacher Mode: min cohesion, family concentration, core anchors.
Reads compiled plan + BookSpec; loads atom metadata from teacher_banks. No prose scoring.
Authority: Teacher Mode structural design — anti-template, platform safety.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

MIN_STORY_WORDS = 120
MIN_EXERCISE_WORDS = 90
MAX_FAMILY_CONCENTRATION = 0.60  # FAIL if one family > 60% (exercise)
WARN_FAMILY_CONCENTRATION = 0.45  # WARN if > 45%
# Single story family dominance (platform-safe)
MAX_STORY_FAMILY_SHARE = 0.70  # FAIL if one story structure_family > 70%
WARN_STORY_FAMILY_SHARE = 0.55  # WARN if > 55%
MIN_UNIQUE_INTRO_STYLE_IDS = 3  # WARN if book uses < 3 distinct intro style IDs
MIN_CORE_ANCHORS_BOOK = 4   # FAIL if unique core anchors < 4
WARN_CORE_ANCHORS_BOOK = 6  # WARN if < 6
MIN_TEACHER_ANCHOR_WORDS = 60  # Non-STORY atom with teacher_id must be > 60w to count as anchor
EXPANDED_FORBIDDEN_IN_BODY = "[EXPANDED]"  # FAIL if present in any atom body (audit in YAML only)
# COMPRESSION slot (DEV SPEC 2)
MIN_COMPRESSION_WORDS = 40
MAX_COMPRESSION_WORDS = 120
COMPRESSION_ATOMS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "compression_atoms"
# DEV SPEC 3: Emotional Role Taxonomy
ALLOWED_EMOTIONAL_ROLES = frozenset({"recognition", "destabilization", "reframe", "stabilization", "integration"})


def _load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _word_count(text: str) -> int:
    return len((text or "").split())


def _compression_one_insight_fail(body: str) -> list[str]:
    """Structural-only: FAIL if list/step/multi-insight patterns. DEV SPEC 2."""
    errs: list[str] = []
    if not body:
        return errs
    low = body.lower()
    if re.search(r"\b(1\.|2\.|3\.|first\s*,\s*second|step\s+one|step\s+1)\b", low):
        errs.append("COMPRESSION: numbered list or step language (one-insight only)")
    if re.search(r"\b(here are|steps?:\s|step\s+\d)\b", low):
        errs.append("COMPRESSION: 'steps' or 'here are' pattern (one-insight only)")
    pivot_markers = ["but also", "and also", "another thing"]
    if sum(1 for m in pivot_markers if m in low) > 2:
        errs.append("COMPRESSION: more than 2 pivot markers (single insight)")
    if body.count(":") > 1:
        errs.append("COMPRESSION: more than one colon (often multi-idea)")
    return errs


def _plan_has_compression(plan: dict) -> bool:
    """True if slot_definitions or chapter_slot_sequence contains COMPRESSION."""
    seq = plan.get("chapter_slot_sequence") or plan.get("slot_definitions") or []
    for row in seq:
        slots = row if isinstance(row, list) else (row.get("slots") or []) if isinstance(row, dict) else []
        for s in slots or []:
            st = (s.get("slot_type") or s.get("type") or s) if isinstance(s, dict) else s
            if str(st).upper() == "COMPRESSION":
                return True
    return False


def _load_compression_atom(atom_id: str, approved: Path | None, plan: dict, book_spec: dict, repo_root: Path) -> dict | None:
    """Load COMPRESSION atom YAML: try approved/COMPRESSION/<id>.yaml then compression_atoms/approved/<persona>/<topic>/."""
    if approved is not None:
        teacher_path = approved / "COMPRESSION" / f"{atom_id}.yaml"
        if teacher_path.exists():
            return _load_yaml(teacher_path)
    persona_id = plan.get("persona_id") or book_spec.get("persona_id") or ""
    topic_id = plan.get("topic_id") or book_spec.get("topic_id") or ""
    if persona_id and topic_id:
        canon_dir = repo_root / "SOURCE_OF_TRUTH" / "compression_atoms" / "approved" / persona_id / topic_id
        if canon_dir.exists():
            for path in canon_dir.glob("*.yaml"):
                data = _load_yaml(path)
                if data and data.get("atom_id") == atom_id:
                    return data
    return None


def get_plan_flat(plan: dict) -> list[tuple[str, str]]:
    """Returns [(atom_id, slot_type), ...] in chapter order."""
    atom_ids = plan.get("atom_ids") or []
    ch_slots = plan.get("chapter_slot_sequence") or []
    flat = []
    idx = 0
    for row in ch_slots:
        for slot_type in row:
            if idx < len(atom_ids):
                flat.append((atom_ids[idx], slot_type))
                idx += 1
    return flat


def get_plan_by_chapter(plan: dict) -> list[list[tuple[str, str]]]:
    """Returns [[(atom_id, slot_type), ...], ...] one list per chapter."""
    atom_ids = plan.get("atom_ids") or []
    ch_slots = plan.get("chapter_slot_sequence") or []
    by_chapter: list[list[tuple[str, str]]] = []
    idx = 0
    for row in ch_slots:
        chapter: list[tuple[str, str]] = []
        for slot_type in row:
            if idx < len(atom_ids):
                chapter.append((atom_ids[idx], slot_type))
                idx += 1
        by_chapter.append(chapter)
    return by_chapter


def _max_consecutive_run(ids: list[str]) -> int:
    if not ids:
        return 0
    best = cur = 1
    last = ids[0]
    for v in ids[1:]:
        if v and v == last:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
            last = v
    return best


# ---------- Plan-based dominance gates (work from compiled plan alone; no atoms_dir required) ----------

def _plan_has_rich_slots(plan: dict) -> bool:
    """True if chapter_slot_sequence is list of dicts with 'slots' (Stage 3 rich output)."""
    seq = plan.get("chapter_slot_sequence") or []
    if not seq:
        return False
    first = seq[0]
    return isinstance(first, dict) and "slots" in first


def check_story_family_dominance(plan: dict, errors: list[str], warnings: list[str]) -> None:
    """
    Production dominance check when plan has rich chapter_slot_sequence (chapter["slots"], slot["slot_type"], slot["structure_family"]).
    FAIL if single story family share > 70%; WARN if > 55%.
    """
    if not _plan_has_rich_slots(plan):
        return
    families: list[str] = []
    for chapter in plan.get("chapter_slot_sequence") or []:
        for slot in (chapter.get("slots") or []):
            if (slot.get("slot_type") or slot.get("type")) == "STORY":
                fam = slot.get("structure_family") or slot.get("story_family") or slot.get("family")
                if fam:
                    families.append(str(fam))
    if not families:
        return
    counts = Counter(families)
    top = counts.most_common(1)[0]
    share = top[1] / len(families)
    if share > 0.70:
        errors.append(f"Story family dominance {share:.0%} > 70%")
    elif share > 0.55:
        warnings.append(f"Story family dominance {share:.0%} > 55%")


def check_intro_style_distribution(plan: dict, warnings: list[str]) -> None:
    """
    When plan has rich chapters with author_intro_style_id, WARN if unique intro style IDs < 3.
    """
    if not _plan_has_rich_slots(plan):
        return
    styles: list[str] = []
    for chapter in plan.get("chapter_slot_sequence") or []:
        if isinstance(chapter, dict) and chapter.get("author_intro_style_id"):
            styles.append(str(chapter["author_intro_style_id"]))
    if styles and len(set(styles)) < 3:
        warnings.append("Intro style diversity < 3 unique IDs")


def _mode_share(xs: list[str]) -> tuple[float, str]:
    if not xs:
        return 0.0, ""
    c = Counter(xs)
    val, cnt = c.most_common(1)[0]
    return cnt / len(xs), val


def _story_family_share_from_plan(plan: dict) -> float:
    """
    Max share of structure_family across STORY slots when plan embeds per-slot metadata.
    If chapter_slot_sequence is list-of-strings (slot type only), returns 0.0.
    """
    fams: list[str] = []
    seq = plan.get("chapter_slot_sequence") or []
    for ch in seq:
        slots = ch.get("slots") if isinstance(ch, dict) else ch
        for s in slots or []:
            if not isinstance(s, dict):
                continue
            st = str(s.get("slot_type") or s.get("type") or "").upper()
            if st == "STORY":
                f = s.get("structure_family") or s.get("story_family") or s.get("family")
                if f:
                    fams.append(str(f))
    share, _ = _mode_share(fams)
    return share


def _intro_style_ids_from_plan(plan: dict) -> list[str]:
    """Collect author_intro_style_id from plan when embedded per-chapter or per-slot."""
    ids: list[str] = []
    seq = plan.get("chapter_slot_sequence") or []
    for ch in seq:
        if isinstance(ch, dict) and ch.get("author_intro_style_id"):
            ids.append(str(ch["author_intro_style_id"]))
        slots = ch.get("slots") if isinstance(ch, dict) else ch
        for s in slots or []:
            if isinstance(s, dict) and s.get("author_intro_style_id"):
                ids.append(str(s["author_intro_style_id"]))
    return ids


def apply_dominance_gates(plan: dict, errors: list[str], warnings: list[str]) -> None:
    """
    Plan-based dominance checks (no atoms_dir). Use when plan embeds structure_family / intro style.
    - FAIL if single story family dominance > 70%; WARN if > 55%.
    - WARN if unique intro style IDs < 3.
    """
    fam_share = _story_family_share_from_plan(plan)
    if fam_share > 0.70:
        errors.append(f"Plan-based: single story family dominance {fam_share:.0%} > 70%")
    elif fam_share > 0.55:
        warnings.append(f"Plan-based: story family dominance {fam_share:.0%} > 55% (review)")

    intro_ids = _intro_style_ids_from_plan(plan)
    uniq = len(set(intro_ids))
    if intro_ids and uniq < 3:
        warnings.append(f"Plan-based: unique author_intro_style_id = {uniq} < 3 (review)")


def run_checks(
    plan_path: Path,
    book_spec_path: Path | None,
    repo_root: Path,
    atoms_dir: Path | None = None,
    teacher_mode_force: bool = False,
    allow_missing_role_seq: bool = False,
) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings). FAIL: min words, missing atom, (teacher-mode) per-chapter exercise/anchor, style ID run > 3. DEV SPEC 3: emotional_role_sequence checks."""
    errors: list[str] = []
    warnings: list[str] = []

    plan = _load_json(plan_path)
    book_spec = _load_json(book_spec_path) if book_spec_path else {}
    teacher_mode = teacher_mode_force or plan.get("teacher_mode") or book_spec.get("teacher_mode", False)
    teacher_id = plan.get("teacher_id") or book_spec.get("teacher_id")

    # DEV SPEC 3: Emotional role sequence (Arc-First mandatory unless --allow-missing-role-seq)
    ch_seq = plan.get("chapter_slot_sequence") or []
    chapter_count = len(ch_seq) if ch_seq else int(plan.get("chapter_count") or 0)
    role_seq = plan.get("emotional_role_sequence")
    if not allow_missing_role_seq and chapter_count > 0:
        if not role_seq or not isinstance(role_seq, list):
            errors.append("emotional_role_sequence required (Arc-First). Use --allow-missing-role-seq for legacy plans.")
        elif len(role_seq) != chapter_count:
            errors.append(f"emotional_role_sequence length ({len(role_seq)}) must equal chapter_count ({chapter_count})")
        else:
            for r in role_seq:
                if r not in ALLOWED_EMOTIONAL_ROLES:
                    errors.append(f"emotional_role_sequence contains invalid role {r!r}. Allowed: {sorted(ALLOWED_EMOTIONAL_ROLES)}")
                    break
            if role_seq and role_seq[-1] != "integration":
                errors.append("Last chapter must have emotional_role integration")
            if role_seq and role_seq[0] != "recognition":
                warnings.append("First chapter should be emotional_role recognition (unless arc has opening_override)")
            run_len = 1
            for i in range(1, len(role_seq)):
                if role_seq[i] == role_seq[i - 1]:
                    run_len += 1
                    if run_len > 2:
                        errors.append(f"Max 2 consecutive same emotional_role; chapters {i - 1}-{i} repeat {role_seq[i]}")
                        break
                else:
                    run_len = 1

    # Plan-based dominance gates (work from plan alone; no atoms_dir)
    apply_dominance_gates(plan, errors, warnings)
    # Production dominance (rich-slot shape only)
    check_story_family_dominance(plan, errors, warnings)
    check_intro_style_distribution(plan, warnings)

    if atoms_dir is not None:
        approved = Path(atoms_dir)
    else:
        if not teacher_mode or not teacher_id:
            return errors, warnings
        approved = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "approved_atoms"

    has_compression = _plan_has_compression(plan)
    approved_exists = approved.exists()
    if not approved_exists and not has_compression:
        errors.append(f"Atoms root not found: {approved}")
        return errors, warnings

    flat = get_plan_flat(plan)
    by_chapter = get_plan_by_chapter(plan)
    story_families: list[str] = []
    exercise_families: list[str] = []
    story_word_counts: list[int] = []
    exercise_word_counts: list[int] = []
    core_anchors: set[str] = set()
    intro_style_ids_by_chapter: list[str] = []
    outro_style_ids_by_chapter: list[str] = []
    compression_families: list[str] = []

    for atom_id, slot_type in flat:
        if not approved_exists and slot_type != "COMPRESSION":
            continue
        if "placeholder:" in atom_id:
            if slot_type == "COMPRESSION":
                errors.append(f"COMPRESSION slot missing atom (placeholder): chapter/slot in plan")
            continue
        if slot_type == "COMPRESSION":
            atom = _load_compression_atom(atom_id, approved if approved_exists else None, plan, book_spec, repo_root)
            if not atom:
                errors.append(f"Missing COMPRESSION atom referenced by plan: {atom_id}")
                continue
            body = (atom.get("body") or "").strip()
            wc = _word_count(body)
            if wc < MIN_COMPRESSION_WORDS or wc > MAX_COMPRESSION_WORDS:
                errors.append(f"COMPRESSION atom {atom_id}: word count {wc} outside 40-120")
            for e in _compression_one_insight_fail(body):
                errors.append(f"COMPRESSION {atom_id}: {e}")
            fam = atom.get("compression_family")
            if fam:
                compression_families.append(str(fam))
            continue
        slot_dir = approved / slot_type
        path = slot_dir / f"{atom_id}.yaml"
        atom = _load_yaml(path)
        if not atom:
            errors.append(f"Missing atom referenced by plan: {atom_id}")
            continue
        body = (atom.get("body") or "").strip()
        if EXPANDED_FORBIDDEN_IN_BODY in body:
            errors.append(f"Atom body must not contain '{EXPANDED_FORBIDDEN_IN_BODY}' (audit in YAML only): {atom_id}")
        wc = _word_count(body)
        if slot_type == "STORY":
            story_word_counts.append(wc)
            if wc > 0 and wc < MIN_STORY_WORDS:
                errors.append(f"STORY atom too short (<120w): {atom_id} ({wc}w)")
            fam = atom.get("structure_family")
            if fam:
                story_families.append(fam)
        elif slot_type == "EXERCISE":
            exercise_word_counts.append(wc)
            if wc > 0 and wc < MIN_EXERCISE_WORDS:
                errors.append(f"EXERCISE atom too short (<90w): {atom_id} ({wc}w)")
            fam = atom.get("exercise_family")
            if fam:
                exercise_families.append(fam)
        for tag in atom.get("tags") or []:
            if isinstance(tag, str) and tag.startswith("core:"):
                core_anchors.add(tag)

    # Per-chapter STORY intro/outro style IDs (for consecutive-run check)
    for chapter_slots in by_chapter:
        ch_intro, ch_outro = "", ""
        for atom_id, slot_type in chapter_slots:
            if slot_type != "STORY" or "placeholder:" in atom_id:
                continue
            path = approved / slot_type / f"{atom_id}.yaml"
            atom = _load_yaml(path)
            if atom:
                ch_intro = atom.get("author_intro_style_id", "")
                ch_outro = atom.get("author_outro_style_id", "")
                break
        intro_style_ids_by_chapter.append(ch_intro)
        outro_style_ids_by_chapter.append(ch_outro)

    # Intro style diversity: WARN if book uses < 3 distinct intro style IDs
    unique_intros = len(set(i for i in intro_style_ids_by_chapter if i))
    if teacher_mode and unique_intros < MIN_UNIQUE_INTRO_STYLE_IDS and unique_intros > 0:
        warnings.append(f"Teacher-mode: unique author_intro_style_ids = {unique_intros} (recommend >= {MIN_UNIQUE_INTRO_STYLE_IDS})")

    # Teacher-mode: per-chapter exercise and teacher anchor (STORY with teacher_id OR atom with teacher_id and >60w)
    if teacher_mode:
        for ch_idx, chapter_slots in enumerate(by_chapter):
            has_exercise = False
            has_teacher_anchor = False
            for atom_id, slot_type in chapter_slots:
                if "placeholder:" in atom_id:
                    continue
                if slot_type == "EXERCISE":
                    has_exercise = True
                path = approved / slot_type / f"{atom_id}.yaml"
                atom = _load_yaml(path)
                if atom:
                    t = atom.get("teacher") or {}
                    if isinstance(t, dict) and t.get("teacher_id"):
                        body_wc = _word_count((atom.get("body") or "").strip())
                        if slot_type == "STORY":
                            has_teacher_anchor = True
                        elif body_wc > MIN_TEACHER_ANCHOR_WORDS:
                            has_teacher_anchor = True
            if not has_exercise:
                errors.append(f"Teacher-mode: chapter {ch_idx + 1} missing EXERCISE slot/atom")
            if not has_teacher_anchor:
                errors.append(
                    f"Teacher-mode: chapter {ch_idx + 1} missing teacher anchor "
                    "(need STORY with teacher_id or atom with teacher_id and >60 words)"
                )

    # Consecutive intro/outro style ID runs (teacher-mode)
    if teacher_mode and intro_style_ids_by_chapter:
        if _max_consecutive_run(intro_style_ids_by_chapter) > 3:
            errors.append("Teacher-mode: author_intro_style_id repeats > 3 consecutive chapters")
        if _max_consecutive_run(outro_style_ids_by_chapter) > 3:
            errors.append("Teacher-mode: author_outro_style_id repeats > 3 consecutive chapters")

    # COMPRESSION family diversity (DEV SPEC 2): fail if >70% chapters share same compression_family
    if compression_families:
        fam_counts = Counter(compression_families)
        total = len(compression_families)
        max_share = max(fam_counts.values()) / total if total else 0
        if max_share > 0.70:
            errors.append(f"COMPRESSION: one compression_family > 70% of chapters ({max_share:.0%})")

    # Story family dominance (single-family share; platform-safe)
    if story_families:
        counts = Counter(story_families)
        total = len(story_families)
        max_pct = max(c / total for c in counts.values()) if total else 0
        if max_pct > MAX_STORY_FAMILY_SHARE:
            errors.append(f"Story structure_family dominance {max_pct:.1%} > {MAX_STORY_FAMILY_SHARE:.0%} (FAIL)")
        elif max_pct > WARN_STORY_FAMILY_SHARE:
            warnings.append(f"Story structure_family dominance {max_pct:.1%} (WARN)")
    # Exercise family concentration
    if exercise_families:
        counts = Counter(exercise_families)
        total = len(exercise_families)
        max_pct = max(c / total for c in counts.values()) if total else 0
        if max_pct > MAX_FAMILY_CONCENTRATION:
            errors.append(f"Exercise family concentration {max_pct:.1%} > {MAX_FAMILY_CONCENTRATION:.0%} (FAIL)")
        elif max_pct > WARN_FAMILY_CONCENTRATION:
            warnings.append(f"Exercise family concentration {max_pct:.1%} (WARN)")

    # Core anchor coverage
    n_core = len(core_anchors)
    if n_core < MIN_CORE_ANCHORS_BOOK:
        errors.append(f"Core teaching anchors in book: {n_core} (min {MIN_CORE_ANCHORS_BOOK})")
    elif n_core < WARN_CORE_ANCHORS_BOOK:
        warnings.append(f"Core teaching anchors in book: {n_core} (recommend >= {WARN_CORE_ANCHORS_BOOK})")

    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Structural entropy CI gate (Teacher Mode). FAIL-only checks: min words, missing atom, per-chapter exercise/anchor, style ID run > 3.")
    ap.add_argument("--plan", required=True, help="Compiled plan JSON")
    ap.add_argument("--book-spec", default=None, help="BookSpec JSON (optional)")
    ap.add_argument("--atoms-dir", default=None, help="Root approved_atoms directory (if not set, use repo teacher_banks/<teacher_id>/approved_atoms)")
    ap.add_argument("--teacher-mode", action="store_true", help="Force teacher-mode checks even if plan lacks teacher_mode/teacher_id")
    ap.add_argument("--allow-missing-role-seq", action="store_true", help="Allow plans without emotional_role_sequence (legacy; not for publish)")
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

    errors, warnings = run_checks(
        plan_path, book_spec_path, repo,
        atoms_dir=atoms_dir,
        teacher_mode_force=args.teacher_mode,
        allow_missing_role_seq=args.allow_missing_role_seq,
    )
    report = {"errors": errors, "warnings": warnings, "pass": len(errors) == 0}
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Wrote {args.out}")
    for e in errors:
        print(f"FAIL: {e}")
    for w in warnings:
        print(f"WARN: {w}")
    if not errors and not warnings:
        print("Structural entropy: OK")
    return 0 if len(errors) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
