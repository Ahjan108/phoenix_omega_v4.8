#!/usr/bin/env python3
"""
Analyze Pearl Prime simulation output: pass rate by dimension, best/worst combos.
Robust intelligent testing: per-format/per-tier gates, baseline regression, coverage
assertions, phase2/phase3 dimension gates. Fails CI when any gate fails.
Usage: python scripts/ci/analyze_pearl_prime_sim.py --input artifacts/simulation_10k.json [--baseline PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_sim(path: Path) -> tuple[list[dict], dict]:
    """Load simulation JSON. Returns (results, summary)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data.get("results", [])
    summary = data.get("summary", {})
    return results, summary


def binomial_stderr(p: float, n: int) -> float:
    """Standard error for pass rate (binomial). Returns 0 if n==0."""
    if n <= 0:
        return 0.0
    return math.sqrt(p * (1 - p) / n)


def analyze(results: list[dict], summary: dict) -> dict:
    """Compute analysis: pass_rate by format, tier; best/worst combos."""
    n = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    overall_rate = passed / n if n else 0

    by_format: dict[str, dict] = {}
    by_tier: dict[str, dict] = {}
    by_combo: dict[tuple[str, str], list[bool]] = {}

    for r in results:
        fid = r.get("format_id", "?")
        tier = r.get("tier", "?")
        ok = r.get("passed", False)

        by_format.setdefault(fid, {"pass": 0, "fail": 0, "total": 0})
        by_format[fid]["total"] += 1
        if ok:
            by_format[fid]["pass"] += 1
        else:
            by_format[fid]["fail"] += 1

        by_tier.setdefault(tier, {"pass": 0, "fail": 0, "total": 0})
        by_tier[tier]["total"] += 1
        if ok:
            by_tier[tier]["pass"] += 1
        else:
            by_tier[tier]["fail"] += 1

        key = (fid, tier)
        by_combo.setdefault(key, []).append(ok)

    pass_rate_by_format = {f: d["pass"] / d["total"] if d["total"] else 0 for f, d in by_format.items()}
    pass_rate_by_tier = {t: d["pass"] / d["total"] if d["total"] else 0 for t, d in by_tier.items()}

    combo_rates = [(k, sum(v) / len(v) if v else 0, len(v)) for k, v in by_combo.items()]
    best_combos = sorted(combo_rates, key=lambda x: -x[1])[:10]
    worst_combos = sorted(combo_rates, key=lambda x: x[1])[:10]

    error_reasons = summary.get("error_reasons", {})
    phase2 = summary.get("phase2", {})
    phase3 = summary.get("phase3", {})

    # Phase 2/3 pass rates (when present): of non-skipped runs, what % passed
    phase2_total = (phase2.get("phase2_passed", 0) + phase2.get("phase2_failed", 0)) if phase2 else 0
    phase2_rate = (phase2.get("phase2_passed", 0) / phase2_total) if phase2_total else 1.0
    phase3_total = (phase3.get("phase3_passed", 0) + phase3.get("phase3_failed", 0)) if phase3 else 0
    phase3_rate = (phase3.get("phase3_passed", 0) / phase3_total) if phase3_total else 1.0

    return {
        "n": n,
        "passed": passed,
        "failed": n - passed,
        "overall_pass_rate": overall_rate,
        "overall_pass_rate_stderr": binomial_stderr(overall_rate, n),
        "pass_rate_by_format": pass_rate_by_format,
        "pass_rate_by_tier": pass_rate_by_tier,
        "by_format": by_format,
        "by_tier": by_tier,
        "best_combos": [{"format_id": k[0], "tier": k[1], "pass_rate": rate, "count": cnt} for k, rate, cnt in best_combos],
        "worst_combos": [{"format_id": k[0], "tier": k[1], "pass_rate": rate, "count": cnt} for k, rate, cnt in worst_combos],
        "error_reasons": error_reasons,
        "phase2_summary": phase2,
        "phase3_summary": phase3,
        "phase2_pass_rate": phase2_rate,
        "phase3_pass_rate": phase3_rate,
        "phase2_n": phase2_total,
        "phase3_n": phase3_total,
    }


def check_baseline_regression(analysis: dict, baseline: dict, regress_tolerance: float) -> list[str]:
    """Compare to baseline. Return list of regression messages (empty if none)."""
    failures: list[str] = []
    current = analysis.get("overall_pass_rate", 0)
    base_overall = baseline.get("overall_pass_rate")
    if base_overall is not None and current < base_overall - regress_tolerance:
        failures.append(
            f"overall_pass_rate regressed: {current:.2%} vs baseline {base_overall:.2%} (tolerance {regress_tolerance:.0%})"
        )
    for fid, rate in (analysis.get("pass_rate_by_format") or {}).items():
        base_rates = baseline.get("pass_rate_by_format") or {}
        if fid in base_rates and rate < base_rates[fid] - regress_tolerance:
            failures.append(f"format {fid} regressed: {rate:.2%} vs baseline {base_rates[fid]:.2%}")
    for tier, rate in (analysis.get("pass_rate_by_tier") or {}).items():
        base_rates = baseline.get("pass_rate_by_tier") or {}
        if tier in base_rates and rate < base_rates[tier] - regress_tolerance:
            failures.append(f"tier {tier} regressed: {rate:.2%} vs baseline {base_rates[tier]:.2%}")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze Pearl Prime simulation output (robust intelligent gates)")
    ap.add_argument("--input", "-i", required=True, help="Simulation JSON path")
    ap.add_argument("--out", "-o", default="", help="Output analysis JSON (default: artifacts/reports/pearl_prime_sim_analysis.json)")
    ap.add_argument("--baseline", default="", help="Baseline JSON for regression comparison (optional)")
    ap.add_argument("--min-pass-rate", type=float, default=0.95, help="Minimum overall pass rate (default 0.95)")
    ap.add_argument("--min-format-rate", type=float, default=0.0, help="Min pass rate per format (0 = disabled)")
    ap.add_argument("--min-tier-rate", type=float, default=0.0, help="Min pass rate per tier (0 = disabled)")
    ap.add_argument("--min-phase2-rate", type=float, default=0.0, help="Min Phase 2 pass rate when present (0 = disabled)")
    ap.add_argument("--min-phase3-rate", type=float, default=0.0, help="Min Phase 3 pass rate when present (0 = disabled)")
    ap.add_argument("--regress-tolerance", type=float, default=0.05, help="Max allowed drop vs baseline (default 0.05)")
    ap.add_argument("--no-fail", action="store_true", help="Do not exit 1 on threshold failure (report only)")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"Error: input not found: {in_path}", file=sys.stderr)
        return 1

    results, summary = load_sim(in_path)
    analysis = analyze(results, summary)

    out_path = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "reports" / "pearl_prime_sim_analysis.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path}")

    summary_path = out_path.parent / (out_path.stem + "_SUMMARY.txt")
    stderr_str = f" (±{analysis.get('overall_pass_rate_stderr', 0):.2%})" if analysis.get("overall_pass_rate_stderr") else ""
    lines = [
        f"Pearl Prime Simulation Analysis",
        f"n={analysis['n']} passed={analysis['passed']} failed={analysis['failed']}",
        f"overall_pass_rate={analysis['overall_pass_rate']:.2%}{stderr_str}",
        "",
        "Best combos (format_id, tier, rate, count):",
    ]
    for c in analysis["best_combos"][:5]:
        lines.append(f"  {c['format_id']} / {c['tier']}: {c['pass_rate']:.2%} (n={c['count']})")
    lines.append("")
    lines.append("Worst combos:")
    for c in analysis["worst_combos"][:5]:
        lines.append(f"  {c['format_id']} / {c['tier']}: {c['pass_rate']:.2%} (n={c['count']})")
    if analysis.get("phase2_n"):
        lines.append(f"\nPhase 2 pass rate: {analysis.get('phase2_pass_rate', 0):.2%} (n={analysis['phase2_n']})")
    if analysis.get("phase3_n"):
        lines.append(f"Phase 3 pass rate: {analysis.get('phase3_pass_rate', 0):.2%} (n={analysis['phase3_n']})")
    if analysis.get("error_reasons"):
        lines.append("")
        lines.append("Error reasons:")
        for reason, cnt in sorted(analysis["error_reasons"].items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  {cnt}: {reason}")
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {summary_path}")

    # --- Intelligent gates (all must pass unless --no-fail) ---
    gate_failures: list[str] = []

    min_rate = args.min_pass_rate
    if args.baseline:
        base_path = Path(args.baseline)
        if base_path.exists():
            base_data = json.loads(base_path.read_text(encoding="utf-8"))
            min_rate = base_data.get("min_pass_rate", min_rate)
            regress = check_baseline_regression(analysis, base_data, args.regress_tolerance)
            gate_failures.extend(regress)

    if analysis["overall_pass_rate"] < min_rate:
        gate_failures.append(
            f"overall_pass_rate {analysis['overall_pass_rate']:.2%} < {min_rate:.2%}"
        )

    if args.min_format_rate > 0:
        for fid, rate in (analysis.get("pass_rate_by_format") or {}).items():
            if rate < args.min_format_rate:
                gate_failures.append(f"format {fid}: pass_rate {rate:.2%} < {args.min_format_rate:.2%}")
    if args.min_tier_rate > 0:
        for tier, rate in (analysis.get("pass_rate_by_tier") or {}).items():
            if rate < args.min_tier_rate:
                gate_failures.append(f"tier {tier}: pass_rate {rate:.2%} < {args.min_tier_rate:.2%}")
    if args.min_phase2_rate > 0 and analysis.get("phase2_n", 0) > 0:
        p2 = analysis.get("phase2_pass_rate", 0)
        if p2 < args.min_phase2_rate:
            gate_failures.append(f"phase2_pass_rate {p2:.2%} < {args.min_phase2_rate:.2%}")
    if args.min_phase3_rate > 0 and analysis.get("phase3_n", 0) > 0:
        p3 = analysis.get("phase3_pass_rate", 0)
        if p3 < args.min_phase3_rate:
            gate_failures.append(f"phase3_pass_rate {p3:.2%} < {args.min_phase3_rate:.2%}")

    if gate_failures:
        for g in gate_failures:
            print(f"FAIL: {g}", file=sys.stderr)
        if not args.no_fail:
            return 1
    else:
        print(f"PASS: overall_pass_rate {analysis['overall_pass_rate']:.2%} >= {min_rate:.2%}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
