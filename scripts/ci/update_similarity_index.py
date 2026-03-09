#!/usr/bin/env python3
"""
Append one compiled plan to the JSONL similarity index (extended CTSS fingerprint).

Row format: book_id, teacher_id, arc_id, band_seq (list), slot_sig, exercise_chapters,
story_fam_vec, ex_fam_vec, tps, engine_id, format_id.

When Stage 3 has emitted structural fields (slot_sig, exercise_chapters, emotional_temperature_sequence,
story_family_distribution, exercise_family_distribution, teacher_presence_sequence), use them;
otherwise fall back to row_from_plan extraction.

Pipeline: compile → structural_entropy_check → check_platform_similarity → update_similarity_index → publish.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Same dir as check_platform_similarity
_CI_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_CI_DIR))

from check_platform_similarity import row_from_plan  # noqa: E402


def _dict_to_fam_vec(d: dict) -> list[int]:
    """Convert family count dict to stable vector (sorted keys)."""
    if not d:
        return []
    return [int(d.get(k, 0)) for k in sorted(d)]


def append_to_index(plan: dict, index_path: str, plan_path: str = "", teacher_override: str = "") -> dict:
    """
    Build index row from plan. Prefer Stage 3 embedded fields when present; else use row_from_plan.
    Returns the row dict written to the index.
    """
    plan_id_val = plan.get("plan_id") or plan.get("plan_hash") or Path(plan_path).stem if plan_path else ""
    teacher_id_val = plan.get("teacher_id") or teacher_override or ""
    arc_id_val = plan.get("arc_id") or ""
    format_id_val = plan.get("format_id") or plan.get("format_structural_id") or plan.get("structural_format") or ""
    engine_id_val = plan.get("engine_id") or plan.get("engine") or ""

    # Prefer Stage 3 emitted structural fields (deterministic CI)
    band_seq = plan.get("emotional_temperature_sequence")
    if band_seq is None and plan.get("dominant_band_sequence"):
        band_seq = [str(b) if b is not None else "3" for b in plan["dominant_band_sequence"]]
    slot_sig = plan.get("slot_sig")
    exercise_chapters = plan.get("exercise_chapters")
    story_family_dist = plan.get("story_family_distribution")
    exercise_family_dist = plan.get("exercise_family_distribution")
    teacher_presence_seq = plan.get("teacher_presence_sequence")

    freebie_bundle = plan.get("freebie_bundle") or []
    freebie_bundle_signature = "|".join(sorted(freebie_bundle)) if isinstance(freebie_bundle, list) else ""
    cta_signature = str(plan.get("cta_template_id") or "")
    compression_pos_sig = str(plan.get("compression_pos_sig") or "")
    compression_len_vec = list(plan.get("compression_len_vec") or [])
    role_seq = str(plan.get("emotional_role_sig") or "")
    angle_id_val = str(plan.get("angle_id") or "")
    topic_id_val = str(plan.get("topic_id") or "")
    # Structural Variation V4
    book_structure_id = str(plan.get("book_structure_id") or "")
    journey_shape_id = str(plan.get("journey_shape_id") or "")
    motif_id = str(plan.get("motif_id") or "")
    reframe_profile_id = str(plan.get("reframe_profile_id") or "")
    variation_signature = str(plan.get("variation_signature") or "")

    if slot_sig is not None and exercise_chapters is not None and band_seq is not None:
        # Use Stage 3 embedded fields
        story_fam_vec = story_family_dist if isinstance(story_family_dist, list) else _dict_to_fam_vec(story_family_dist or {})
        ex_fam_vec = exercise_family_dist if isinstance(exercise_family_dist, list) else _dict_to_fam_vec(exercise_family_dist or {})
        tps = list(teacher_presence_seq) if teacher_presence_seq else []
        row = {
            "book_id": plan_id_val,
            "teacher_id": teacher_id_val,
            "arc_id": arc_id_val,
            "band_seq": list(band_seq),
            "slot_sig": str(slot_sig),
            "exercise_chapters": [int(x) for x in exercise_chapters],
            "story_fam_vec": story_fam_vec,
            "ex_fam_vec": ex_fam_vec,
            "tps": tps,
            "engine_id": engine_id_val,
            "format_id": format_id_val,
            "freebie_bundle_signature": freebie_bundle_signature,
            "cta_signature": cta_signature,
            "compression_pos_sig": compression_pos_sig,
            "compression_len_vec": compression_len_vec,
            "role_seq": role_seq,
            "angle_id": angle_id_val,
            "topic_id": topic_id_val,
            "book_structure_id": book_structure_id,
            "journey_shape_id": journey_shape_id,
            "motif_id": motif_id,
            "reframe_profile_id": reframe_profile_id,
            "variation_signature": variation_signature,
        }
    else:
        # Fallback: extract from plan via row_from_plan
        fp = row_from_plan(plan, plan_path or "plan.json", teacher_override=teacher_override)
        row = {
            "book_id": fp.book_id,
            "teacher_id": fp.teacher_id,
            "arc_id": fp.arc_id,
            "band_seq": fp.band_seq,
            "slot_sig": fp.slot_sig,
            "exercise_chapters": fp.exercise_chapters,
            "story_fam_vec": fp.story_fam_vec,
            "ex_fam_vec": fp.ex_fam_vec,
            "tps": fp.tps,
            "engine_id": fp.engine_id,
            "format_id": fp.format_id,
            "freebie_bundle_signature": getattr(fp, "freebie_bundle_signature", "") or "",
            "cta_signature": getattr(fp, "cta_signature", "") or "",
            "compression_pos_sig": getattr(fp, "compression_pos_sig", "") or "",
            "compression_len_vec": list(getattr(fp, "compression_len_vec", None) or []),
            "role_seq": getattr(fp, "role_seq", "") or "",
            "angle_id": getattr(fp, "angle_id", "") or "",
            "topic_id": getattr(fp, "topic_id", "") or "",
            "book_structure_id": getattr(fp, "book_structure_id", "") or "",
            "journey_shape_id": getattr(fp, "journey_shape_id", "") or "",
            "motif_id": getattr(fp, "motif_id", "") or "",
            "reframe_profile_id": getattr(fp, "reframe_profile_id", "") or "",
            "variation_signature": getattr(fp, "variation_signature", "") or "",
        }
    return row


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Append plan to catalog similarity index (extended CTSS; JSONL)"
    )
    ap.add_argument("--plan", required=True, help="Compiled plan JSON path")
    ap.add_argument("--index", required=True, help="JSONL index path (append one line)")
    ap.add_argument("--teacher-id", default="", help="Teacher id if not in plan")
    args = ap.parse_args()

    with open(args.plan, "r", encoding="utf-8") as f:
        plan = json.load(f)

    if args.teacher_id and not plan.get("teacher_id"):
        plan = {**plan, "teacher_id": args.teacher_id}

    row = append_to_index(plan, args.index, plan_path=args.plan, teacher_override=args.teacher_id)

    Path(args.index).parent.mkdir(parents=True, exist_ok=True)
    with open(args.index, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Appended to index: {args.index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
