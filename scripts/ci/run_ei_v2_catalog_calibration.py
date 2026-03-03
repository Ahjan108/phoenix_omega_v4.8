#!/usr/bin/env python3
"""
EI V2 Catalog-Level Calibration

Runs V2 analysis across all compilable books in the catalog to:
  1. Discover optimal thresholds per dimension
  2. Compute baseline statistics for hybrid override tuning
  3. Feed the learner with catalog-wide observations
  4. Output a calibration report with recommended parameters

This is the "catalog-level calibration" step. After calibration,
per-book hybrid enforcement uses the discovered thresholds.

Usage:
  PYTHONPATH=. python scripts/ci/run_ei_v2_catalog_calibration.py
  PYTHONPATH=. python scripts/ci/run_ei_v2_catalog_calibration.py --learn
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
from phoenix_v4.quality.ei_v2.dimension_gates import enforce_chapter_gates
from phoenix_v4.quality.ei_v2.hybrid_selector import hybrid_select
from phoenix_v4.quality.ei_v2.learner import learn, load_learned_params

CATALOG_COMBOS = [
    ("gen_z_professionals", "anxiety", "spiral", "F006"),
    ("gen_z_professionals", "anxiety", "overwhelm", "F002"),
    ("gen_z_professionals", "overthinking", "spiral", "F006"),
    ("educators", "anxiety", "overwhelm", "F006"),
    ("nyc_executives", "boundaries", "shame", "F006"),
    ("nyc_executives", "self_worth", "shame", "F006"),
]


def compile_and_render_book(persona_id, topic_id, engine, fmt):
    """Compile and render a book, return (plan, prose_map, chapter_texts) or None."""
    arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / f"{persona_id}__{topic_id}__{engine}__{fmt}.yaml"
    if not arc_path.exists():
        return None

    try:
        from phoenix_v4.planning.arc_loader import load_arc
        from phoenix_v4.planning.catalog_planner import CatalogPlanner
        from phoenix_v4.planning.format_selector import FormatSelector
        from phoenix_v4.planning.assembly_compiler import compile_plan

        arc = load_arc(arc_path)
        planner = CatalogPlanner()
        bs = planner.produce_single(
            topic_id=topic_id, persona_id=persona_id,
            teacher_id="default_teacher", brand_id="phoenix_core",
            seed=f"calibrate_{persona_id}_{topic_id}_{engine}")
        bsd = bs.to_dict()
        bsd["atoms_model"] = "legacy"

        sel = FormatSelector()
        fp = sel.select_format(topic_id=topic_id, persona_id=persona_id)
        fpd = fp.to_compiler_input()
        if fpd.get("chapter_count") != arc.chapter_count:
            fpd["chapter_count"] = arc.chapter_count
            sd = fpd.get("slot_definitions") or []
            if len(sd) == 1:
                fpd["slot_definitions"] = [list(sd[0]) for _ in range(arc.chapter_count)]
            elif len(sd) > arc.chapter_count:
                fpd["slot_definitions"] = sd[:arc.chapter_count]
            else:
                fpd["slot_definitions"] = list(sd) + [list(sd[-1] if sd else []) for _ in range(arc.chapter_count - len(sd))]

        compiled = compile_plan(bsd, fpd, arc_path=arc_path, atoms_model="legacy")
        plan = {
            "plan_hash": compiled.plan_hash,
            "chapter_slot_sequence": compiled.chapter_slot_sequence,
            "atom_ids": compiled.atom_ids,
            "dominant_band_sequence": compiled.dominant_band_sequence,
            "emotional_role_sequence": compiled.emotional_role_sequence or [],
            "persona_id": persona_id, "topic_id": topic_id,
        }

        from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan
        render_result = resolve_prose_for_plan(plan)
        prose_map = render_result.prose_map

        chapter_texts = []
        idx = 0
        for slots in plan["chapter_slot_sequence"]:
            parts = []
            for slot in slots:
                if idx < len(plan["atom_ids"]):
                    aid = plan["atom_ids"][idx]
                    prose = prose_map.get(aid, "")
                    if prose:
                        parts.append(prose)
                    idx += 1
            chapter_texts.append("\n\n".join(parts))

        return plan, prose_map, chapter_texts
    except Exception as exc:
        print(f"  SKIP: {exc}", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--learn", action="store_true", help="Run learner after calibration")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    v2_cfg = load_ei_v2_config()
    dim_gate_cfg = v2_cfg.get("dimension_gates", {})

    out_dir = Path(args.out) if args.out else (REPO_ROOT / "artifacts" / "ei_v2")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*55}")
    print(f"  EI V2 CATALOG CALIBRATION — {len(CATALOG_COMBOS)} books")
    print(f"{'='*55}")

    all_gate_results: Dict[str, List[float]] = {
        "uniqueness": [], "engagement": [], "somatic_precision": [],
        "listen_experience": [], "cohesion": [],
    }
    book_results = []
    total_chapters = 0
    total_overrides = 0
    total_blocks = 0
    total_slots_compared = 0
    t_start = time.monotonic()

    for i, (persona, topic, engine, fmt) in enumerate(CATALOG_COMBOS):
        label = f"{persona}/{topic}/{engine}"
        print(f"\n[{i+1}/{len(CATALOG_COMBOS)}] {label} ...", end="", flush=True)

        result = compile_and_render_book(persona, topic, engine, fmt)
        if not result:
            print(" SKIP")
            continue

        plan, prose_map, chapter_texts = result
        band_seq = plan.get("dominant_band_sequence", [])
        role_seq = plan.get("emotional_role_sequence", [])
        n_ch = len(chapter_texts)
        total_chapters += n_ch

        book_gate_failures = 0
        book_gate_warns = 0

        for ch_idx, ch_text in enumerate(chapter_texts):
            gate_report = enforce_chapter_gates(
                ch_text, ch_idx, chapter_texts, dim_gate_cfg)

            for g in gate_report.gates:
                if g.dimension in all_gate_results:
                    all_gate_results[g.dimension].append(g.score)

            book_gate_failures += gate_report.fail_count
            book_gate_warns += gate_report.warn_count

        book_results.append({
            "persona": persona, "topic": topic, "engine": engine,
            "chapters": n_ch,
            "gate_failures": book_gate_failures,
            "gate_warnings": book_gate_warns,
        })

        print(f" {n_ch}ch, {book_gate_failures}F/{book_gate_warns}W gates")

    elapsed = time.monotonic() - t_start

    # --- Compute calibrated thresholds ---
    calibrated = {}
    print(f"\n  CALIBRATED THRESHOLDS (from {total_chapters} chapters)")
    print("  " + "-" * 50)
    for dim, scores in all_gate_results.items():
        if scores:
            avg = statistics.mean(scores)
            p25 = sorted(scores)[max(0, len(scores) // 4)]
            p10 = sorted(scores)[max(0, len(scores) // 10)]
            calibrated[dim] = {
                "mean": round(avg, 4),
                "p25": round(p25, 4),
                "p10": round(p10, 4),
                "recommended_warn": round(p25, 3),
                "recommended_fail": round(p10, 3),
            }
            print(f"  {dim:<22} mean={avg:.3f}  p25={p25:.3f}  p10={p10:.3f}")

    # --- Write calibration report ---
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "books_evaluated": len(book_results),
        "total_chapters": total_chapters,
        "elapsed_s": round(elapsed, 2),
        "calibrated_thresholds": calibrated,
        "per_book": book_results,
    }

    report_path = out_dir / "catalog_calibration.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n  Calibration report: {report_path}")

    # --- Run learner if requested (threshold-only: skip unless feedback exists) ---
    if args.learn:
        learner_cfg = v2_cfg.get("learner", {})
        fb_path = Path(learner_cfg.get("feedback_path", "artifacts/ei_v2/learner_feedback.jsonl"))
        if not fb_path.is_absolute():
            fb_path = REPO_ROOT / fb_path
        if fb_path.exists() and fb_path.stat().st_size > 0:
            print("\n  Running learner (feedback exists)...")
            params_path = Path(learner_cfg.get("params_path", "artifacts/ei_v2/learned_params.json"))
            if not params_path.is_absolute():
                params_path = REPO_ROOT / params_path
            params = learn(
                feedback_path=fb_path,
                params_path=params_path,
                window=int(learner_cfg.get("learning_window", 200)),
            )
            print(f"  Learned params v{params.version}: weights={params.composite_weights}")
            print(f"  Override margin: {params.override_margin}")
        else:
            print("\n  Skipping learner (no feedback data) — calibration is threshold-only.")

    print(f"\n  Total time: {elapsed:.1f}s")
    print(f"{'='*55}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
