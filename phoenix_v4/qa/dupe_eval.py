"""
DupEval — Platform Duplication Evaluation (pre-publish structural similarity gate).

Compares structural fingerprints only: no prose, no embeddings, no NLP.
Prevents: near-identical arc clones, teacher×persona skin swaps, template reuse,
same emotional curve reuse, same slot layout, same exercise placement.

Pipeline order: compile → structural_entropy_check → dupe_eval → update_similarity_index → publish.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


# Band sequence extraction priority (standardized for index and comparison)
BAND_SEQ_KEYS = [
    "emotional_temperature_sequence",
    "required_band_by_chapter",
    "emotional_band_sequence",
    "dominant_band_sequence",
]


def band_seq_from_plan(plan: dict) -> str:
    """Standardized band sequence string. Priority: temp sequence → required_band → dominant_band → chapters."""
    for k in BAND_SEQ_KEYS:
        v = plan.get(k)
        if isinstance(v, list) and v:
            return "-".join(str(x) if x is not None else "3" for x in v)
    bands = plan.get("dominant_band_sequence")
    if isinstance(bands, list) and bands:
        return "-".join(str(b) if b is not None else "3" for b in bands)
    chs = plan.get("chapters") or plan.get("compiled", {}).get("chapters") or []
    out = []
    for ch in chs:
        b = ch.get("required_band") or ch.get("band") or ch.get("dominant_band")
        out.append(str(b) if b is not None else "3")
    return "-".join(out) if out else ""


def exercise_chapters_from_plan(plan: dict) -> list[int]:
    """Chapter numbers (1-based) that contain an EXERCISE slot."""
    chs = plan.get("chapters") or plan.get("compiled", {}).get("chapters")
    if chs is not None:
        ex = []
        for i, ch in enumerate(chs, start=1):
            slots = ch.get("slots") or ch.get("resolved_slots") or []
            for s in slots:
                t = (s.get("slot_type") or s.get("type") or s.get("role") or "").upper()
                if t == "EXERCISE":
                    ex.append(i)
                    break
        return ex
    ch_slots = plan.get("chapter_slot_sequence") or []
    ex = []
    for i, row in enumerate(ch_slots, start=1):
        if "EXERCISE" in (str(s).upper() for s in row):
            ex.append(i)
    return ex


def slot_signature(plan: dict) -> str:
    """Deterministic hash of format + slot layout."""
    format_id = plan.get("format_id") or plan.get("structural_format") or ""
    ch_slots = plan.get("chapter_slot_sequence") or []
    slot_names = []
    for row in ch_slots:
        for s in row:
            name = (
                (s.get("slot_id") or s.get("name") or s.get("slot_type") or str(s)).strip()
                if isinstance(s, dict)
                else (str(s).strip() if s else "")
            )
            slot_names.append(name)
    payload = format_id + "|" + "|".join(slot_names)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _plan_flat(plan: dict) -> list[tuple[str, str]]:
    """(atom_id, slot_type) in chapter order."""
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


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def story_and_exercise_family_distributions(
    plan: dict, atoms_dir: Path | None
) -> tuple[dict[str, int], dict[str, int]]:
    """From plan + atoms_dir build story_family_dist and exercise_family_dist (counts by family)."""
    story_dist: dict[str, int] = {}
    ex_dist: dict[str, int] = {}
    if not atoms_dir or not atoms_dir.exists():
        return story_dist, ex_dist
    for atom_id, slot_type in _plan_flat(plan):
        if "placeholder:" in atom_id or "silence:" in atom_id:
            continue
        slot_dir = atoms_dir / slot_type
        path = slot_dir / f"{atom_id}.yaml"
        atom = _load_yaml(path)
        if not atom:
            continue
        if slot_type == "STORY":
            fam = atom.get("structure_family") or "UNKNOWN"
            story_dist[fam] = story_dist.get(fam, 0) + 1
        elif slot_type == "EXERCISE":
            fam = atom.get("exercise_family") or "UNKNOWN"
            ex_dist[fam] = ex_dist.get(fam, 0) + 1
    return story_dist, ex_dist


def _l1_similarity(a: dict[str, int], b: dict[str, int]) -> float:
    """1 - normalized L1 distance between count dicts. 1.0 = identical, 0.0 = no overlap."""
    all_keys = set(a) | set(b)
    if not all_keys:
        return 1.0
    l1 = sum(abs(a.get(k, 0) - b.get(k, 0)) for k in all_keys)
    total = sum(a.get(k, 0) + b.get(k, 0) for k in all_keys)
    if total == 0:
        return 1.0
    max_l1 = total  # max L1 when disjoint
    return 1.0 - (l1 / max_l1)


def sim_band(a: str, b: str) -> float:
    aa = a.split("-") if a else []
    bb = b.split("-") if b else []
    n = min(len(aa), len(bb))
    if n == 0:
        return 0.0
    matches = sum(1 for i in range(n) if aa[i] == bb[i])
    return matches / n


def jaccard(a: list[int], b: list[int]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# CTSS weights: arc 0.25, band 0.20, slot 0.15, ex_pos 0.15, story_family 0.15, ex_family 0.10
W_ARC = 0.25
W_BAND = 0.20
W_SLOT = 0.15
W_EX = 0.15
W_STORY_FAM = 0.15
W_EX_FAM = 0.10


def ctss(new: dict, old: dict) -> float:
    """Structural similarity (SF). Includes story_family_dist and exercise_family_dist when present."""
    sim_arc = 1.0 if (new.get("arc_id") and new["arc_id"] == old.get("arc_id")) else 0.0
    sim_b = sim_band(new.get("band_seq", ""), old.get("band_seq", ""))
    sim_slots = 1.0 if (new.get("slot_sig") and new["slot_sig"] == old.get("slot_sig")) else 0.0
    sim_ex = jaccard(new.get("exercise_chapters") or [], old.get("exercise_chapters") or [])
    sim_story_fam = _l1_similarity(
        new.get("story_family_dist") or {}, old.get("story_family_dist") or {}
    )
    sim_ex_fam = _l1_similarity(
        new.get("exercise_family_dist") or {}, old.get("exercise_family_dist") or {}
    )
    return (
        W_ARC * sim_arc
        + W_BAND * sim_b
        + W_SLOT * sim_slots
        + W_EX * sim_ex
        + W_STORY_FAM * sim_story_fam
        + W_EX_FAM * sim_ex_fam
    )


def tss(new: dict, old: dict) -> float:
    """Teacher Signature similarity. Used only when same teacher (teacher_mode)."""
    if new.get("teacher_id") != old.get("teacher_id"):
        return 0.0
    # Intro/outro style ID overlap; core_teachings overlap
    intro_a = set(new.get("intro_style_ids") or [])
    intro_b = set(old.get("intro_style_ids") or [])
    outro_a = set(new.get("outro_style_ids") or [])
    outro_b = set(old.get("outro_style_ids") or [])
    core_a = set(new.get("core_teachings_used") or [])
    core_b = set(old.get("core_teachings_used") or [])
    j_intro = len(intro_a & intro_b) / len(intro_a | intro_b) if (intro_a or intro_b) else 0.0
    j_outro = len(outro_a & outro_b) / len(outro_a | outro_b) if (outro_a or outro_b) else 0.0
    j_core = len(core_a & core_b) / len(core_a | core_b) if (core_a or core_b) else 0.0
    return (j_intro + j_outro + j_core) / 3.0


def mss(new: dict, old: dict) -> float:
    """Metadata style similarity. Identical style IDs ratio."""
    keys = ["title_style_id", "subtitle_style_id", "blurb_style_id", "chapter_name_style_id", "cover_style_id"]
    matches = 0
    count = 0
    for k in keys:
        a, b = new.get(k), old.get(k)
        if a is None and b is None:
            continue
        count += 1
        if a is not None and b is not None and a == b:
            matches += 1
    return matches / count if count else 0.0


# Final DupEval weights (Teacher Mode): 0.50 CTSS, 0.30 TSS, 0.20 MSS
W_CTSS = 0.50
W_TSS = 0.30
W_MSS = 0.20


def final_dup_score(new: dict, old: dict, teacher_mode: bool) -> float:
    if teacher_mode and new.get("teacher_id") and new["teacher_id"] == old.get("teacher_id"):
        return W_CTSS * ctss(new, old) + W_TSS * tss(new, old) + W_MSS * mss(new, old)
    return ctss(new, old)


# Thresholds
BLOCK_DIFFERENT_TEACHER = 0.75
REVIEW_DIFFERENT_TEACHER = 0.65
BLOCK_SAME_TEACHER = 0.85
REVIEW_SAME_TEACHER = 0.72
BLOCK_SAME_TEACHER_SAME_ARC = 0.70


def _strat_rule_block(new: dict, old: dict) -> bool:
    """Same teacher + same arc + same band sequence → block (catalog farm risk)."""
    if (new.get("teacher_id") or "") != (old.get("teacher_id") or ""):
        return False
    if (new.get("arc_id") or "") != (old.get("arc_id") or ""):
        return False
    return (new.get("band_seq") or "") == (old.get("band_seq") or "")


def run_dupe_eval(
    plan: dict,
    index: list[dict],
    teacher_mode: bool = False,
    atoms_dir: Path | None = None,
    block_different: float = BLOCK_DIFFERENT_TEACHER,
    review_different: float = REVIEW_DIFFERENT_TEACHER,
    block_same: float = BLOCK_SAME_TEACHER,
    review_same: float = REVIEW_SAME_TEACHER,
    block_same_arc: float = BLOCK_SAME_TEACHER_SAME_ARC,
) -> tuple[str, float, dict | None]:
    """
    Compare plan fingerprint against index. Returns (verdict, worst_score, worst_row).
    verdict: "pass" | "review" | "block"
    """
    new_row = build_fingerprint(plan, atoms_dir=atoms_dir, teacher_mode=teacher_mode)
    worst = 0.0
    worst_row: dict | None = None
    for old in index:
        score = final_dup_score(new_row, old, teacher_mode)
        if score > worst:
            worst = score
            worst_row = old

    if worst_row is None:
        return "pass", 0.0, None

    same_teacher = (new_row.get("teacher_id") or "") == (worst_row.get("teacher_id") or "")
    same_arc = (new_row.get("arc_id") or "") == (worst_row.get("arc_id") or "")

    if _strat_rule_block(new_row, worst_row):
        return "block", worst, worst_row

    if same_teacher and same_arc and worst >= block_same_arc:
        return "block", worst, worst_row
    if same_teacher and worst >= block_same:
        return "block", worst, worst_row
    if same_teacher and worst >= review_same:
        return "review", worst, worst_row
    if worst >= block_different:
        return "block", worst, worst_row
    if worst >= review_different:
        return "review", worst, worst_row
    return "pass", worst, worst_row


def build_fingerprint(
    plan: dict,
    atoms_dir: Path | None = None,
    teacher_mode: bool = False,
    book_id: str | None = None,
) -> dict:
    """Build index row (fingerprint) from plan. Optionally enrich with story/exercise family dist from atoms_dir."""
    story_fam, ex_fam = story_and_exercise_family_distributions(plan, atoms_dir)
    row: dict[str, Any] = {
        "book_id": book_id or plan.get("plan_id") or plan.get("book_id") or "",
        "teacher_id": plan.get("teacher_id") or "",
        "arc_id": plan.get("arc_id") or "",
        "band_seq": band_seq_from_plan(plan),
        "slot_sig": slot_signature(plan),
        "exercise_chapters": exercise_chapters_from_plan(plan),
        "engine_id": plan.get("engine_id") or plan.get("engine") or "",
        "format_id": plan.get("format_id") or plan.get("structural_format") or "",
        "plan_hash": plan.get("plan_hash") or "",
        "story_family_dist": story_fam,
        "exercise_family_dist": ex_fam,
    }
    if teacher_mode and atoms_dir and atoms_dir.exists():
        intro_ids, outro_ids, core_used = _teacher_signature_from_plan(plan, atoms_dir)
        row["intro_style_ids"] = intro_ids
        row["outro_style_ids"] = outro_ids
        row["core_teachings_used"] = core_used
    else:
        row["intro_style_ids"] = []
        row["outro_style_ids"] = []
        row["core_teachings_used"] = []
    for k in ("title_style_id", "subtitle_style_id", "blurb_style_id", "chapter_name_style_id", "cover_style_id"):
        if plan.get(k) is not None:
            row[k] = plan[k]
    return row


def _teacher_signature_from_plan(
    plan: dict, atoms_dir: Path
) -> tuple[list[str], list[str], list[str]]:
    """Extract intro_style_ids, outro_style_ids, core_teachings_used from plan atoms."""
    intro_ids: list[str] = []
    outro_ids: list[str] = []
    core_used: set[str] = set()
    for atom_id, slot_type in _plan_flat(plan):
        if "placeholder:" in atom_id or "silence:" in atom_id:
            continue
        path = atoms_dir / slot_type / f"{atom_id}.yaml"
        atom = _load_yaml(path)
        if not atom:
            continue
        if slot_type == "STORY":
            ti = atom.get("author_intro_style_id")
            if ti:
                intro_ids.append(str(ti))
            to = atom.get("author_outro_style_id")
            if to:
                outro_ids.append(str(to))
        for tag in atom.get("tags") or []:
            if isinstance(tag, str) and tag.startswith("core:"):
                core_used.add(tag)
    return intro_ids, outro_ids, list(core_used)


def check_wave_density(rows: list[dict]) -> tuple[list[str], list[str]]:
    """
    Wave-level density check. Returns (errors, warnings).
    FAIL if: >30% same arc_id, >40% identical band_seq, >50% identical slot_sig, >60% identical exercise placement.
    """
    errors: list[str] = []
    warnings: list[str] = []
    n = len(rows)
    if n == 0:
        return [], []

    arc_counts: dict[str, int] = {}
    band_counts: dict[str, int] = {}
    slot_counts: dict[str, int] = {}
    ex_key_counts: dict[str, int] = {}

    for r in rows:
        arc_id = r.get("arc_id") or "_"
        arc_counts[arc_id] = arc_counts.get(arc_id, 0) + 1
        band_seq = r.get("band_seq") or ""
        band_counts[band_seq] = band_counts.get(band_seq, 0) + 1
        slot_sig = r.get("slot_sig") or ""
        slot_counts[slot_sig] = slot_counts.get(slot_sig, 0) + 1
        ex_ch = tuple(r.get("exercise_chapters") or [])
        ex_key_counts[str(ex_ch)] = ex_key_counts.get(str(ex_ch), 0) + 1

    for arc_id, c in arc_counts.items():
        if arc_id == "_":
            continue
        if c / n > 0.30:
            errors.append(f"Wave density: >30% same arc_id ({arc_id}): {c}/{n}")

    for band_seq, c in band_counts.items():
        if not band_seq:
            continue
        if c / n > 0.40:
            errors.append(f"Wave density: >40% identical band_seq: {c}/{n}")

    for slot_sig, c in slot_counts.items():
        if not slot_sig:
            continue
        if c / n > 0.50:
            errors.append(f"Wave density: >50% identical slot_sig: {c}/{n}")

    for ex_key, c in ex_key_counts.items():
        if ex_key == "()":
            continue
        if c / n > 0.60:
            errors.append(f"Wave density: >60% identical exercise placement: {c}/{n}")

    return errors, warnings


def load_index(path: str | Path) -> list[dict]:
    path = Path(path)
    rows = []
    if not path.exists():
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows
