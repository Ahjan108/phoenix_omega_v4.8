#!/usr/bin/env python3
"""
Run Phoenix V4.5 format simulation: 10 → analyze → fix/enhance → scale to 1k.
Usage:
  python run_simulation.py --n 10
  python run_simulation.py --n 100
  python run_simulation.py --n 1000
  python run_simulation.py --n 10 --analyze
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Run from repo root or simulation/
_sim_dir = Path(__file__).resolve().parent
_repo_root = _sim_dir.parent
sys.path.insert(0, str(_sim_dir))
sys.path.insert(0, str(_repo_root))
from simulator import run_simulation, get_formats, get_validation_matrix, BookRequest
from phase2 import run_phase2_on_results
from phase3_mvp import run_phase3_on_results


def main() -> int:
    ap = argparse.ArgumentParser(description="Phoenix V4.5 format simulation")
    ap.add_argument("--n", type=int, default=10, help="Number of books to simulate (default 10)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    ap.add_argument("--pool", type=int, default=100, help="Mock pool size per atom type")
    ap.add_argument("--phase2", action="store_true", help="Run Phase 2 (waveform, arc, drift) on Phase 1 results")
    ap.add_argument("--phase3", action="store_true", help="Run Phase 3 MVP (volatility, cognitive, consequence, reassurance) on synthetic chapter text")
    ap.add_argument("--analyze", action="store_true", help="Print detailed analysis and failure reasons")
    ap.add_argument("--out", type=str, default="", help="Write results JSON to path")
    ap.add_argument("--no-cover", action="store_true", help="Do not force first N to cover all formats")
    ap.add_argument("--use-format-selector", action="store_true", help="Use Stage 2 format selector (topic+persona+installment) to pick format; deterministic")
    args = ap.parse_args()

    n = max(1, args.n)
    cover_all = not args.no_cover and n >= 14

    requests_arg = None
    stage2_plans_arg = None
    if args.use_format_selector:
        try:
            from phoenix_v4.planning.format_selector import FormatSelector
        except Exception as e:
            print("Error: --use-format-selector requires phoenix_v4.planning.format_selector:", e, file=sys.stderr)
            return 1
        sel = FormatSelector()
        topics = ["relationship_anxiety", "grief", "overwhelm", "false_alarm", "social_anxiety", "shame"]
        personas = ["nyc_exec", "healthcare_worker", "gen_z"]
        teachers = ["teacher_1"]
        requests_arg = []
        stage2_plans_arg = []
        for i in range(n):
            topic = topics[i % len(topics)]
            persona = personas[i % len(personas)]
            installment = (i // (len(topics) * len(personas))) + 1
            plan = sel.select_format(topic, persona, installment)
            stage2_plans_arg.append({
                "format_runtime_id": plan.format_runtime_id,
                "chapter_count": plan.chapter_count,
                "word_target_range": list(plan.word_target_range),
                "tier": plan.tier,
            })
            requests_arg.append(BookRequest(
                format_id=plan.format_runtime_id,
                teacher=teachers[i % len(teachers)],
                persona=persona,
                topic=topic,
                overlay=None,
                seed=args.seed + i,
            ))

    results, summary = run_simulation(
        n=n,
        seed=args.seed,
        pool_per_type=args.pool,
        cover_all_formats=cover_all and not args.use_format_selector,
        requests=requests_arg,
        stage2_plans=stage2_plans_arg,
    )

    if summary.get("error"):
        print("Error:", summary["error"], file=sys.stderr)
        return 1

    passed = summary["passed"]
    failed = summary["failed"]
    rate = summary["pass_rate"]
    print(f"Phase 1 (structure): n={n}  passed={passed}  failed={failed}  pass_rate={rate:.2%}")

    if args.phase2 and results:
        results, phase2_summary = run_phase2_on_results(results)
        summary["phase2"] = phase2_summary
        p2_pass = phase2_summary.get("phase2_passed", 0)
        p2_fail = phase2_summary.get("phase2_failed", 0)
        p2_skip = phase2_summary.get("phase2_skipped", 0)
        drift_ok = phase2_summary.get("drift_stacks_failed", 0) == 0
        print(f"Phase 2 (waveform/arc/drift): passed={p2_pass}  failed={p2_fail}  skipped={p2_skip}  drift_ok={drift_ok}")
        if p2_fail > 0 or not drift_ok:
            print(f"  waveform_failed={phase2_summary.get('waveform_failed', 0)}  arc_failed={phase2_summary.get('arc_failed', 0)}  drift_stacks_failed={phase2_summary.get('drift_stacks_failed', 0)}")
    if args.phase3 and results:
        results, phase3_summary = run_phase3_on_results(results)
        summary["phase3"] = phase3_summary
        p3_pass = phase3_summary.get("phase3_passed", 0)
        p3_fail = phase3_summary.get("phase3_failed", 0)
        p3_skip = phase3_summary.get("phase3_skipped", 0)
        print(f"Phase 3 (content/emotional force): passed={p3_pass}  failed={p3_fail}  skipped={p3_skip}")

    if args.analyze or failed > 0:
        print("\n--- By format ---")
        for fid, counts in sorted(summary.get("by_format", {}).items()):
            p, f = counts.get("pass", 0), counts.get("fail", 0)
            status = "OK" if f == 0 else "FAIL"
            print(f"  {fid}: pass={p} fail={f}  [{status}]")
        print("\n--- By tier ---")
        for tier, counts in sorted(summary.get("by_tier", {}).items()):
            p, f = counts.get("pass", 0), counts.get("fail", 0)
            status = "OK" if f == 0 else "FAIL"
            print(f"  Tier {tier}: pass={p} fail={f}  [{status}]")
        if summary.get("error_reasons"):
            print("\n--- Error reasons (count) ---")
            for reason, count in sorted(summary["error_reasons"].items(), key=lambda x: -x[1]):
                print(f"  {count}: {reason}")
        if args.analyze and failed > 0:
            print("\n--- Failed requests (first 20) ---")
            for r in results:
                if not r.get("passed"):
                    print(f"  {r.get('request_id', '?')} format={r.get('format_id')} tier={r.get('tier')} errors={r.get('errors', [])}")
                    if sum(1 for x in results if not x.get("passed")) >= 20:
                        break
        if args.phase3 and summary.get("phase3"):
            p3 = summary["phase3"]
            if p3.get("phase3_failed", 0) > 0 and args.analyze:
                print("\n--- Phase 3 failed (first 10) ---")
                for r in results:
                    if not r.get("phase3_skipped") and not r.get("phase3_passed"):
                        print(f"  {r.get('request_id', '?')} phase3_errors={r.get('phase3_errors', [])[:3]}")
                        if sum(1 for x in results if not x.get("phase3_skipped") and not x.get("phase3_passed")) >= 10:
                            break
        if args.phase2 and summary.get("phase2"):
            p2 = summary["phase2"]
            if p2.get("phase2_failed", 0) > 0 and args.analyze:
                print("\n--- Phase 2 failed (first 10) ---")
                for r in results:
                    if not r.get("phase2_skipped") and not r.get("phase2_passed"):
                        print(f"  {r.get('request_id', '?')} phase2_errors={r.get('phase2_errors', [])}")
                        if sum(1 for x in results if not x.get("phase2_skipped") and not x.get("phase2_passed")) >= 10:
                            break
            if p2.get("drift_failures"):
                print("\n--- Drift failures (sample) ---")
                for d in p2["drift_failures"][:3]:
                    print(f"  stack_start={d.get('stack_start')} errors={d.get('errors', [])}")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump({"results": results, "summary": summary}, f, indent=2)
        print(f"\nWrote {out_path}")

    phase2_failed = summary.get("phase2", {}).get("phase2_failed", 0)
    drift_failed = summary.get("phase2", {}).get("drift_stacks_failed", 0)
    phase3_failed = summary.get("phase3", {}).get("phase3_failed", 0)
    return 0 if failed == 0 and phase2_failed == 0 and drift_failed == 0 and phase3_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
