#!/usr/bin/env python3
"""
Platform similarity gate (extended CTSS).

FAIL if worst similarity >= --block.
WARN if worst similarity >= --review.

Design constraints:
- Structural only (no NLP, no embeddings, no prose similarity).
- Backwards-compatible extraction across minor plan schema drift.
- Index fields: book_id, teacher_id, arc_id, band_seq (list), slot_sig, exercise_chapters,
  story_fam_vec, ex_fam_vec, tps, engine_id, format_id.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ----------------------------
# Utilities
# ----------------------------

def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def jaccard(a: List[int], b: List[int]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def l1_dist(a: List[int], b: List[int]) -> int:
    return sum(abs(x - y) for x, y in zip(a, b))


def norm_l1_sim(a: List[int], b: List[int]) -> float:
    sa, sb = sum(a), sum(b)
    if sa == 0 and sb == 0:
        return 1.0
    max_l1 = max(sa, sb) * 2
    if max_l1 == 0:
        return 1.0
    return 1.0 - (l1_dist(a, b) / max_l1)


def normalized_lcs_ratio(a: List[str], b: List[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    n, m = len(a), len(b)
    dp = [0] * (m + 1)
    for i in range(1, n + 1):
        prev = 0
        for j in range(1, m + 1):
            cur = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = cur
    lcs = dp[m]
    return lcs / max(n, m)


# ----------------------------
# Plan extraction (robust)
# ----------------------------

def plan_id(plan: Dict[str, Any], fallback_path: str) -> str:
    return (
        plan.get("plan_id")
        or plan.get("book_id")
        or plan.get("id")
        or os.path.basename(fallback_path)
    )


def teacher_id(plan: Dict[str, Any], override: str = "") -> str:
    return plan.get("teacher_id") or plan.get("teacher") or override or ""


def arc_id(plan: Dict[str, Any]) -> str:
    return plan.get("arc_id") or plan.get("arc") or ""


def engine_id(plan: Dict[str, Any]) -> str:
    return plan.get("engine_id") or plan.get("engine") or ""


def format_id(plan: Dict[str, Any]) -> str:
    return (
        plan.get("format_id")
        or plan.get("format_structural_id")
        or plan.get("structural_format")
        or ""
    )


def slot_signature(plan: Dict[str, Any]) -> str:
    fmt = format_id(plan)
    seq = plan.get("chapter_slot_sequence")
    if seq is None:
        seq = plan.get("slot_definitions") or plan.get("chapters") or []
    payload = json.dumps(seq, sort_keys=True, ensure_ascii=False)
    return f"{fmt}:{sha256_str(payload)}"


def band_seq_from_plan(plan: Dict[str, Any]) -> Tuple[List[str], str]:
    for key in (
        "emotional_temperature_sequence",
        "required_band_by_chapter",
        "dominant_band_sequence",
    ):
        v = plan.get(key)
        if isinstance(v, list) and v:
            return [str(x) for x in v], key

    chs = safe_list(plan.get("chapters"))
    bands: List[str] = []
    for ch in chs:
        if not isinstance(ch, dict):
            continue
        for k in ("required_band", "dominant_band", "band"):
            if k in ch:
                bands.append(str(ch.get(k)))
                break
    if bands:
        return bands, "chapters.*"
    return [], "missing"


def exercise_chapters_from_plan(plan: Dict[str, Any]) -> List[int]:
    explicit = plan.get("exercise_chapters")
    if isinstance(explicit, list):
        return [int(x) for x in explicit]

    seq = safe_list(plan.get("chapter_slot_sequence"))
    ex: List[int] = []
    for ci, chapter in enumerate(seq):
        slots = chapter
        if isinstance(chapter, dict):
            slots = chapter.get("slots") or chapter.get("chapter_slots") or []
        for s in safe_list(slots):
            if isinstance(s, dict):
                t = s.get("slot_type") or s.get("type")
            else:
                t = str(s)
            if str(t).upper() == "EXERCISE":
                ex.append(ci)
                break
    return ex


def _collect_slot_records(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seq = safe_list(plan.get("chapter_slot_sequence"))
    for ci, chapter in enumerate(seq):
        slots = chapter
        if isinstance(chapter, dict):
            slots = chapter.get("slots") or chapter.get("chapter_slots") or []
        for s in safe_list(slots):
            if isinstance(s, dict):
                rec = dict(s)
                rec["_chapter_index"] = ci
                out.append(rec)
    return out


def story_family_dist(
    plan: Dict[str, Any], families: Optional[List[str]] = None
) -> List[int]:
    slots = _collect_slot_records(plan)
    vals: List[str] = []
    for s in slots:
        st = (s.get("slot_type") or s.get("type") or "").upper()
        if st == "STORY":
            fam = s.get("structure_family") or s.get("story_family") or s.get("family")
            if fam:
                vals.append(str(fam))
    if families is None:
        families = sorted(set(vals))
        plan["_story_families"] = families
    c = Counter(vals)
    return [int(c.get(f, 0)) for f in families]


def exercise_family_dist(
    plan: Dict[str, Any], families: Optional[List[str]] = None
) -> List[int]:
    slots = _collect_slot_records(plan)
    vals: List[str] = []
    for s in slots:
        st = (s.get("slot_type") or s.get("type") or "").upper()
        if st == "EXERCISE":
            fam = s.get("exercise_family") or s.get("family")
            if fam:
                vals.append(str(fam))
    if families is None:
        families = sorted(set(vals))
        plan["_exercise_families"] = families
    c = Counter(vals)
    return [int(c.get(f, 0)) for f in families]


def teacher_presence_sequence(plan: Dict[str, Any]) -> List[int]:
    seq = safe_list(plan.get("chapter_slot_sequence"))
    buckets: List[int] = []
    for chapter in seq:
        slots = chapter
        if isinstance(chapter, dict):
            slots = chapter.get("slots") or chapter.get("chapter_slots") or []
        cnt = 0
        for s in safe_list(slots):
            if not isinstance(s, dict):
                continue
            tinfo = s.get("teacher") if isinstance(s.get("teacher"), dict) else {}
            if s.get("teacher_id") or tinfo.get("teacher_id"):
                cnt += 1
        if cnt == 0:
            buckets.append(0)
        elif cnt == 1:
            buckets.append(1)
        elif cnt == 2:
            buckets.append(2)
        else:
            buckets.append(3)
    return buckets


# ----------------------------
# CTSS (extended)
# ----------------------------

@dataclass
class FingerprintRow:
    book_id: str
    teacher_id: str
    arc_id: str
    band_seq: List[str]
    slot_sig: str
    exercise_chapters: List[int]
    story_fam_vec: List[int]
    ex_fam_vec: List[int]
    tps: List[int]
    engine_id: str
    format_id: str
    freebie_bundle_signature: str = ""
    cta_signature: str = ""
    compression_pos_sig: str = ""
    compression_len_vec: List[str] = field(default_factory=list)  # S/M/L per chapter; backward compat
    role_seq: str = ""  # DEV SPEC 3: emotional_role_sig compact e.g. r-d-f-s-i
    angle_id: str = ""  # V4.7 Angle Integration; backward compat: missing = ""
    variation_signature: str = ""  # Structural Variation V4; backward compat: missing = ""


def ctss(a: FingerprintRow, b: FingerprintRow) -> float:
    sim_arc = 1.0 if a.arc_id and (a.arc_id == b.arc_id) else 0.0
    sim_angle = 1.0 if (getattr(a, "angle_id", "") or "") and (getattr(a, "angle_id", "") == getattr(b, "angle_id", "")) else 0.0
    sim_band = normalized_lcs_ratio(a.band_seq, b.band_seq)
    sim_slots = 1.0 if a.slot_sig and (a.slot_sig == b.slot_sig) else 0.0
    sim_ex_pos = jaccard(a.exercise_chapters, b.exercise_chapters)
    sim_story_fam = norm_l1_sim(a.story_fam_vec, b.story_fam_vec)
    sim_ex_fam = norm_l1_sim(a.ex_fam_vec, b.ex_fam_vec)
    sim_tps = norm_l1_sim(a.tps, b.tps)
    sim_freebie = 1.0 if (a.freebie_bundle_signature and a.freebie_bundle_signature == b.freebie_bundle_signature) else 0.0
    sim_cta = 1.0 if (a.cta_signature and a.cta_signature == b.cta_signature) else 0.0
    sim_compression_pos = 1.0 if (a.compression_pos_sig and a.compression_pos_sig == b.compression_pos_sig) else 0.0
    sim_compression_len = normalized_lcs_ratio(
        a.compression_len_vec or [], b.compression_len_vec or []
    )
    sim_role = 1.0 if (a.role_seq and a.role_seq == b.role_seq) else 0.0
    sim_variation = 1.0 if (getattr(a, "variation_signature", "") or "") and (
        (getattr(a, "variation_signature", "") or "") == (getattr(b, "variation_signature", "") or "")
    ) else 0.0
    # Weights: 0.04 angle_id (V4.7); 0.01 variation_signature (V4); total 1.0
    return (
        0.17 * sim_arc
        + 0.12 * sim_band
        + 0.11 * sim_slots
        + 0.13 * sim_ex_pos
        + 0.07 * sim_story_fam
        + 0.07 * sim_ex_fam
        + 0.11 * sim_tps
        + 0.04 * sim_freebie
        + 0.04 * sim_cta
        + 0.02 * sim_compression_pos
        + 0.02 * sim_compression_len
        + 0.05 * sim_role
        + 0.05 * sim_angle
        + 0.01 * sim_variation
    )


def row_from_plan(
    plan: Dict[str, Any], plan_path: str, teacher_override: str = ""
) -> FingerprintRow:
    bid = plan_id(plan, plan_path)
    tid = teacher_id(plan, teacher_override)
    aid = arc_id(plan)
    bands, band_src = band_seq_from_plan(plan)
    plan["_band_source_used"] = band_src

    slot_sig = slot_signature(plan)
    ex_ch = exercise_chapters_from_plan(plan)

    sf_bins = (
        plan.get("story_family_bins")
        if isinstance(plan.get("story_family_bins"), list)
        else None
    )
    ex_bins = (
        plan.get("exercise_family_bins")
        if isinstance(plan.get("exercise_family_bins"), list)
        else None
    )
    sf_vec = story_family_dist(plan, families=sf_bins)
    ex_vec = exercise_family_dist(plan, families=ex_bins)
    tps = teacher_presence_sequence(plan)
    freebie_bundle = plan.get("freebie_bundle") or []
    freebie_bundle_signature = "|".join(sorted(freebie_bundle)) if isinstance(freebie_bundle, list) else ""
    cta_signature = str(plan.get("cta_template_id") or "")
    compression_pos_sig = str(plan.get("compression_pos_sig") or "")
    compression_len_vec = list(plan.get("compression_len_vec") or [])
    role_seq = str(plan.get("emotional_role_sig") or "")
    angle_id_val = str(plan.get("angle_id") or "")
    variation_signature_val = str(plan.get("variation_signature") or "")

    return FingerprintRow(
        book_id=bid,
        teacher_id=tid,
        arc_id=aid,
        band_seq=bands,
        slot_sig=slot_sig,
        exercise_chapters=ex_ch,
        story_fam_vec=sf_vec,
        ex_fam_vec=ex_vec,
        tps=tps,
        engine_id=engine_id(plan),
        format_id=format_id(plan),
        freebie_bundle_signature=freebie_bundle_signature,
        cta_signature=cta_signature,
        compression_pos_sig=compression_pos_sig,
        compression_len_vec=compression_len_vec,
        role_seq=role_seq,
        angle_id=angle_id_val,
        variation_signature=variation_signature_val,
    )


def load_index(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _parse_band_seq(raw: Any) -> List[str]:
    """Backward compat: index may have band_seq as string '2-3-4' or list."""
    if isinstance(raw, str):
        return [x for x in raw.split("-") if x]
    return [str(x) for x in safe_list(raw)]


def _parse_exercise_chapters(raw: Any) -> List[int]:
    if not raw:
        return []
    if isinstance(raw, list):
        return [int(x) for x in raw]
    return []


def old_row_to_fingerprint(old: Dict[str, Any]) -> FingerprintRow:
    """Build FingerprintRow from index row (supports legacy band_seq string and optional freebie/compression/angle_id)."""
    return FingerprintRow(
        book_id=str(old.get("book_id", "")),
        teacher_id=str(old.get("teacher_id", "")),
        arc_id=str(old.get("arc_id", "")),
        band_seq=_parse_band_seq(old.get("band_seq")),
        slot_sig=str(old.get("slot_sig", "")),
        exercise_chapters=_parse_exercise_chapters(old.get("exercise_chapters")),
        story_fam_vec=[int(x) for x in safe_list(old.get("story_fam_vec"))],
        ex_fam_vec=[int(x) for x in safe_list(old.get("ex_fam_vec"))],
        tps=[int(x) for x in safe_list(old.get("tps"))],
        engine_id=str(old.get("engine_id", "")),
        format_id=str(old.get("format_id", "")),
        freebie_bundle_signature=str(old.get("freebie_bundle_signature", "")),
        cta_signature=str(old.get("cta_signature", "")),
        compression_pos_sig=str(old.get("compression_pos_sig", "")),
        compression_len_vec=[str(x) for x in safe_list(old.get("compression_len_vec"))],
        role_seq=str(old.get("role_seq", "")),
        angle_id=str(old.get("angle_id", "")),
        variation_signature=str(old.get("variation_signature", "")),
    )


def normalize_vectors(
    a: FingerprintRow, b: FingerprintRow
) -> Tuple[FingerprintRow, FingerprintRow]:
    def pad(v: List[int], n: int) -> List[int]:
        return v + [0] * max(0, n - len(v))

    sf_n = max(len(a.story_fam_vec), len(b.story_fam_vec))
    ex_n = max(len(a.ex_fam_vec), len(b.ex_fam_vec))
    tps_n = max(len(a.tps), len(b.tps))

    a2 = FingerprintRow(
        **{
            **a.__dict__,
            "story_fam_vec": pad(a.story_fam_vec, sf_n),
            "ex_fam_vec": pad(a.ex_fam_vec, ex_n),
            "tps": pad(a.tps, tps_n),
        }
    )
    b2 = FingerprintRow(
        **{
            **b.__dict__,
            "story_fam_vec": pad(b.story_fam_vec, sf_n),
            "ex_fam_vec": pad(b.ex_fam_vec, ex_n),
            "tps": pad(b.tps, tps_n),
        }
    )
    return a2, b2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="New compiled plan JSON")
    ap.add_argument("--index", required=True, help="JSONL index of prior books")
    ap.add_argument("--teacher-id", default="", help="Teacher id for the new book (if not in plan)")
    ap.add_argument("--block", type=float, default=0.78, help="Block threshold")
    ap.add_argument("--review", type=float, default=0.65, help="Review threshold (warn)")
    ap.add_argument(
        "--cross-teacher-only",
        action="store_true",
        help="Only compare against different teachers",
    )
    args = ap.parse_args()

    with open(args.plan, "r", encoding="utf-8") as f:
        plan = json.load(f)

    new_row = row_from_plan(plan, args.plan, teacher_override=args.teacher_id)
    index = load_index(args.index)

    worst = 0.0
    worst_row: Optional[Dict[str, Any]] = None

    for old in index:
        if (
            args.cross_teacher_only
            and new_row.teacher_id
            and old.get("teacher_id") == new_row.teacher_id
        ):
            continue

        old_fp = old_row_to_fingerprint(old)
        a2, b2 = normalize_vectors(new_row, old_fp)
        s = ctss(a2, b2)
        if s > worst:
            worst = s
            worst_row = old

    if worst >= args.block:
        print("PLATFORM SIMILARITY CHECK: FAIL")
        print(f" - Worst CTSS={worst:.3f} vs {worst_row.get('book_id') if worst_row else 'UNKNOWN'}")
        return 2

    if worst >= args.review:
        print("PLATFORM SIMILARITY CHECK: WARN")
        print(f" - Worst CTSS={worst:.3f} vs {worst_row.get('book_id') if worst_row else 'UNKNOWN'}")
        return 0

    print("PLATFORM SIMILARITY CHECK: PASS")
    print(f" - Worst CTSS={worst:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
