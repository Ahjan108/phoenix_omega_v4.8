#!/usr/bin/env python3
"""
Monte Carlo CTSS Risk Simulation

Option A (preferred): feed it a directory of compiled candidate plans (>=1000).
Option B: feed it a generator output JSONL of candidate plan paths.

Computes worst-neighbor CTSS for each candidate against an existing index.jsonl.
Output: block_rate, review_rate, worst-CTSS distribution (mean, p50, p90, p95, max).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
from typing import Any, Dict, List


def safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def jaccard(a: List[int], b: List[int]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def l1_sim(a: List[int], b: List[int]) -> float:
    sa, sb = sum(a), sum(b)
    if sa == 0 and sb == 0:
        return 1.0
    max_l1 = max(sa, sb) * 2
    if max_l1 == 0:
        return 1.0
    dist = sum(abs(x - y) for x, y in zip(a, b))
    return 1.0 - (dist / max_l1)


def lcs_ratio(a: List[str], b: List[str]) -> float:
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
    return dp[m] / max(n, m)


def pad(v: List[int], n: int) -> List[int]:
    return v + [0] * max(0, n - len(v))


def ctss(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    sim_arc = 1.0 if a.get("arc_id") and a["arc_id"] == b.get("arc_id") else 0.0
    sim_band = lcs_ratio(
        [str(x) for x in safe_list(a.get("band_seq", []))],
        [str(x) for x in safe_list(b.get("band_seq", []))],
    )
    sim_slots = 1.0 if a.get("slot_sig") and a["slot_sig"] == b.get("slot_sig") else 0.0
    sim_ex = jaccard(
        [int(x) for x in safe_list(a.get("exercise_chapters", []))],
        [int(x) for x in safe_list(b.get("exercise_chapters", []))],
    )

    sf_a = [int(x) for x in safe_list(a.get("story_fam_vec", []))]
    sf_b = [int(x) for x in safe_list(b.get("story_fam_vec", []))]
    ex_a = [int(x) for x in safe_list(a.get("ex_fam_vec", []))]
    ex_b = [int(x) for x in safe_list(b.get("ex_fam_vec", []))]
    tps_a = [int(x) for x in safe_list(a.get("tps", []))]
    tps_b = [int(x) for x in safe_list(b.get("tps", []))]

    sf_n = max(len(sf_a), len(sf_b))
    ex_n = max(len(ex_a), len(ex_b))
    tps_n = max(len(tps_a), len(tps_b))

    sim_sf = l1_sim(pad(sf_a, sf_n), pad(sf_b, sf_n))
    sim_xf = l1_sim(pad(ex_a, ex_n), pad(ex_b, ex_n))
    sim_tps = l1_sim(pad(tps_a, tps_n), pad(tps_b, tps_n))
    sb_a = a.get("freebie_bundle_signature") or ""
    sb_b = b.get("freebie_bundle_signature") or ""
    sim_freebie = 1.0 if (sb_a and sb_a == sb_b) else 0.0
    ca_a = a.get("cta_signature") or ""
    ca_b = b.get("cta_signature") or ""
    sim_cta = 1.0 if (ca_a and ca_a == ca_b) else 0.0
    return (
        0.20 * sim_arc
        + 0.18 * sim_band
        + 0.11 * sim_slots
        + 0.13 * sim_ex
        + 0.09 * sim_sf
        + 0.09 * sim_xf
        + 0.11 * sim_tps
        + 0.04 * sim_freebie
        + 0.04 * sim_cta
    )


def load_index(path: str) -> List[Dict[str, Any]]:
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _dist_to_vec(d: Dict[str, int]) -> List[int]:
    if not d or not isinstance(d, dict):
        return []
    return [int(d.get(k, 0)) for k in sorted(d)]


def plan_to_row(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Convert compiled plan to CTSS row. Handles story_family_distribution dict or story_fam_vec list."""
    band_seq = plan.get("emotional_temperature_sequence") or plan.get("dominant_band_sequence") or []
    story_fam = plan.get("story_fam_vec")
    if story_fam is None and isinstance(plan.get("story_family_distribution"), dict):
        story_fam = _dist_to_vec(plan["story_family_distribution"])
    ex_fam = plan.get("ex_fam_vec")
    if ex_fam is None and isinstance(plan.get("exercise_family_distribution"), dict):
        ex_fam = _dist_to_vec(plan["exercise_family_distribution"])
    freebie_bundle = plan.get("freebie_bundle") or []
    freebie_bundle_signature = "|".join(sorted(freebie_bundle)) if isinstance(freebie_bundle, list) else ""
    cta_signature = str(plan.get("cta_template_id") or "")
    return {
        "book_id": plan.get("plan_id") or plan.get("plan_hash") or plan.get("book_id", ""),
        "teacher_id": plan.get("teacher_id", ""),
        "arc_id": plan.get("arc_id", ""),
        "band_seq": [str(x) for x in band_seq],
        "slot_sig": plan.get("slot_sig", ""),
        "exercise_chapters": [int(x) for x in safe_list(plan.get("exercise_chapters", []))],
        "story_fam_vec": story_fam if isinstance(story_fam, list) else [],
        "ex_fam_vec": ex_fam if isinstance(ex_fam, list) else [],
        "tps": list(plan.get("teacher_presence_sequence") or []),
        "freebie_bundle_signature": freebie_bundle_signature,
        "cta_signature": cta_signature,
    }


def load_candidate_plans(plans_dir: str, max_n: int) -> List[Dict[str, Any]]:
    paths = [os.path.join(plans_dir, fn) for fn in os.listdir(plans_dir) if fn.endswith(".json")]
    paths.sort()
    if max_n and len(paths) > max_n:
        paths = random.sample(paths, max_n)
    out = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Monte Carlo CTSS duplication-risk simulation")
    ap.add_argument("--index", default="artifacts/catalog_similarity/index.jsonl", help="Similarity index")
    ap.add_argument("--candidates-dir", required=True, help="Directory of compiled plan JSONs")
    ap.add_argument("--n", type=int, default=1000, help="Max number of candidates to sample")
    ap.add_argument("--block", type=float, default=0.78, help="Block threshold")
    ap.add_argument("--review", type=float, default=0.65, help="Review threshold")
    ap.add_argument("--cross-teacher-only", action="store_true", help="Only compare against different teachers")
    ap.add_argument("--seed", type=int, default=0, help="Random seed")
    ap.add_argument("--out", default="artifacts/simulation/ctss_monte_carlo.json", help="Output JSON")
    args = ap.parse_args()

    random.seed(args.seed)

    idx = load_index(args.index)
    if not idx:
        print("Index is empty; cannot simulate duplication risk.", file=sys.stderr)
        return 1

    candidates = load_candidate_plans(args.candidates_dir, args.n)
    if not candidates:
        print("No candidate plans found.", file=sys.stderr)
        return 1

    cand_rows = [plan_to_row(p) for p in candidates]

    worsts = []
    blocks = 0
    reviews = 0

    for c in cand_rows:
        worst = 0.0
        for r in idx:
            if args.cross_teacher_only and c.get("teacher_id") and r.get("teacher_id") == c.get("teacher_id"):
                continue
            rr = {
                "book_id": r.get("book_id", ""),
                "teacher_id": r.get("teacher_id", ""),
                "arc_id": r.get("arc_id", ""),
                "band_seq": [str(x) for x in safe_list(r.get("band_seq", []))],
                "slot_sig": r.get("slot_sig", ""),
                "exercise_chapters": [int(x) for x in safe_list(r.get("exercise_chapters", []))],
                "story_fam_vec": [int(x) for x in safe_list(r.get("story_fam_vec", []))],
                "ex_fam_vec": [int(x) for x in safe_list(r.get("ex_fam_vec", []))],
                "tps": [int(x) for x in safe_list(r.get("tps", []))],
            }
            s = ctss(c, rr)
            if s > worst:
                worst = s

        worsts.append(worst)
        if worst >= args.block:
            blocks += 1
        if worst >= args.review:
            reviews += 1

    summary = {
        "n": len(worsts),
        "block_threshold": args.block,
        "review_threshold": args.review,
        "block_rate": blocks / len(worsts),
        "review_rate": reviews / len(worsts),
        "worst_ctss": {
            "mean": float(statistics.mean(worsts)),
            "p50": float(statistics.median(worsts)),
            "p90": float(statistics.quantiles(worsts, n=10)[8]) if len(worsts) >= 10 else None,
            "p95": float(statistics.quantiles(worsts, n=20)[18]) if len(worsts) >= 20 else None,
            "max": float(max(worsts)),
        },
        "sample": worsts[:25],
    }

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("MONTE CARLO CTSS: wrote", args.out)
    print("  block_rate:", f"{summary['block_rate'] * 100:.1f}%")
    print("  review_rate:", f"{summary['review_rate'] * 100:.1f}%")
    print("  mean worst:", f"{summary['worst_ctss']['mean']:.3f}")
    print("  max worst:", f"{summary['worst_ctss']['max']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
