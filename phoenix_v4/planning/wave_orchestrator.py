#!/usr/bin/env python3
"""
Wave Orchestrator — deterministic wave selection

Input:
- candidate plan JSONs (compiled; must have arc_id, emotional_temperature_sequence, slot_sig, exercise_chapters)
Output:
- selected wave plan list (paths) + wave metrics

Strategy:
Greedy selection with penalty scoring and constraint enforcement.
Deterministic by seed.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter
from typing import Any, Dict, List, Tuple


def load_plan(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def band_seq(p: Dict[str, Any]) -> str:
    seq = p.get("emotional_temperature_sequence") or p.get("dominant_band_sequence") or []
    return "-".join(str(x) for x in seq)


def ex_pattern(p: Dict[str, Any]) -> str:
    xs = p.get("exercise_chapters") or []
    return ",".join(str(int(x)) for x in xs)


def mode_share(values: List[str]) -> float:
    if not values:
        return 0.0
    c = Counter(values)
    _, cnt = c.most_common(1)[0]
    return cnt / len(values)


def wave_ok(wave: List[Dict[str, Any]]) -> bool:
    arcs = [str(p.get("arc_id", "")) for p in wave]
    bands = [band_seq(p) for p in wave]
    slots = [str(p.get("slot_sig", "")) for p in wave]
    exps = [ex_pattern(p) for p in wave]
    return (
        mode_share(arcs) < 0.30
        and mode_share(bands) < 0.40
        and mode_share(slots) < 0.50
        and mode_share(exps) < 0.60
    )


def penalty(candidate: Dict[str, Any], wave: List[Dict[str, Any]]) -> float:
    """
    Lower is better.
    Penalize collisions with existing wave on key dimensions.
    """
    if not wave:
        return 0.0

    c_arc = candidate.get("arc_id", "")
    c_band = band_seq(candidate)
    c_slot = candidate.get("slot_sig", "")
    c_exp = ex_pattern(candidate)

    arc_hits = sum(1 for p in wave if p.get("arc_id") == c_arc)
    band_hits = sum(1 for p in wave if band_seq(p) == c_band)
    slot_hits = sum(1 for p in wave if p.get("slot_sig") == c_slot)
    exp_hits = sum(1 for p in wave if ex_pattern(p) == c_exp)

    return (
        1.5 * arc_hits
        + 2.0 * band_hits
        + 2.5 * slot_hits
        + 1.8 * exp_hits
    )


def orchestrate(
    candidates: List[Tuple[str, Dict[str, Any]]],
    wave_size: int,
    seed: int,
) -> List[Tuple[str, Dict[str, Any]]]:
    random.seed(seed)
    pool = list(candidates)
    random.shuffle(pool)

    wave: List[Tuple[str, Dict[str, Any]]] = []

    for _ in range(wave_size):
        best_i = None
        best_score = 1e9
        wave_plans = [p for _, p in wave]

        for i, (path, plan) in enumerate(pool):
            trial_wave = wave_plans + [plan]
            if len(trial_wave) >= 10 and not wave_ok(trial_wave):
                continue

            s = penalty(plan, wave_plans)
            if s < best_score:
                best_score = s
                best_i = i

        if best_i is None:
            break

        wave.append(pool.pop(best_i))

    return wave


def main() -> int:
    ap = argparse.ArgumentParser(description="Wave orchestrator: select a balanced wave from candidates")
    ap.add_argument("--candidates-dir", required=True, help="Directory of compiled plan JSONs")
    ap.add_argument("--wave-size", type=int, default=60, help="Target wave size")
    ap.add_argument("--seed", type=int, default=0, help="Random seed")
    ap.add_argument("--out", default="artifacts/waves/wave_selected.txt", help="Output: one plan path per line")
    args = ap.parse_args()

    paths = [
        os.path.join(args.candidates_dir, fn)
        for fn in os.listdir(args.candidates_dir)
        if fn.endswith(".json")
    ]
    paths.sort()

    if not paths:
        print("No candidate plans found.", file=sys.stderr)
        return 1

    candidates = []
    for p in paths:
        try:
            plan = load_plan(p)
            if plan.get("slot_sig") is None or plan.get("exercise_chapters") is None:
                continue
            candidates.append((p, plan))
        except Exception:
            continue

    if not candidates:
        print("No valid candidate plans (need slot_sig, exercise_chapters).", file=sys.stderr)
        return 1

    wave = orchestrate(candidates, min(args.wave_size, len(candidates)), args.seed)

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for path, _ in wave:
            f.write(path + "\n")

    print("WAVE ORCHESTRATOR: wrote", args.out)
    print("  selected:", len(wave))

    plans = [p for _, p in wave]
    arcs = [str(p.get("arc_id", "")) for p in plans]
    bands = [band_seq(p) for p in plans]
    slots = [str(p.get("slot_sig", "")) for p in plans]
    exps = [ex_pattern(p) for p in plans]
    print("  arc mode share:", f"{mode_share(arcs) * 100:.1f}%")
    print("  band mode share:", f"{mode_share(bands) * 100:.1f}%")
    print("  slot mode share:", f"{mode_share(slots) * 100:.1f}%")
    print("  ex pattern mode share:", f"{mode_share(exps) * 100:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
