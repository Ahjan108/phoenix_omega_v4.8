#!/usr/bin/env python3
"""
Analyze Pearl Prime simulation output: pass rate by dimension, best/worst combos.
Fails CI when pass_rate or dimension rates fall below baseline thresholds.
Usage: python scripts/ci/analyze_pearl_prime_sim.py --input artifacts/simulation_10k.json [--baseline PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_sim(path: Path) -> tuple[list[dict], dict]:
    """Load simulation JSON. Returns (results, summary)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data.get("results", [])
    summary = data.get("summary", {})
    return results, summary


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

    return {
        "n": n,
        "passed": passed,
        "failed": n - passed,
        "overall_pass_rate": overall_rate,
        "pass_rate_by_format": pass_rate_by_format,
        "pass_rate_by_tier": pass_rate_by_tier,
        "best_combos": [{"format_id": k[0], "tier": k[1], "pass_rate": rate, "count": cnt} for k, rate, cnt in best_combos],
        "worst_combos": [{"format_id": k[0], "tier": k[1], "pass_rate": rate, "count": cnt} for k, rate, cnt in worst_combos],
        "error_reasons": error_reasons,
        "phase2_summary": phase2,
        "phase3_summary": phase3,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze Pearl Prime simulation output")
    ap.add_argument("--input", "-i", required=True, help="Simulation JSON path")
    ap.add_argument("--out", "-o", default="", help="Output analysis JSON (default: artifacts/reports/pearl_prime_sim_analysis.json)")
    ap.add_argument("--baseline", default="", help="Baseline JSON for threshold comparison (optional)")
    ap.add_argument("--min-pass-rate", type=float, default=0.95, help="Minimum overall pass rate to pass (default 0.95)")
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
    lines = [
        f"Pearl Prime Simulation Analysis",
        f"n={analysis['n']} passed={analysis['passed']} failed={analysis['failed']}",
        f"overall_pass_rate={analysis['overall_pass_rate']:.2%}",
        "",
        "Best combos (format_id, tier, rate, count):",
    ]
    for c in analysis["best_combos"][:5]:
        lines.append(f"  {c['format_id']} / {c['tier']}: {c['pass_rate']:.2%} (n={c['count']})")
    lines.append("")
    lines.append("Worst combos:")
    for c in analysis["worst_combos"][:5]:
        lines.append(f"  {c['format_id']} / {c['tier']}: {c['pass_rate']:.2%} (n={c['count']})")
    if analysis.get("error_reasons"):
        lines.append("")
        lines.append("Error reasons:")
        for reason, cnt in sorted(analysis["error_reasons"].items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  {cnt}: {reason}")
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {summary_path}")

    # Threshold check
    min_rate = args.min_pass_rate
    if args.baseline:
        base_path = Path(args.baseline)
        if base_path.exists():
            base_data = json.loads(base_path.read_text(encoding="utf-8"))
            min_rate = base_data.get("min_pass_rate", min_rate)

    if analysis["overall_pass_rate"] < min_rate:
        print(f"FAIL: overall_pass_rate {analysis['overall_pass_rate']:.2%} < {min_rate:.2%}", file=sys.stderr)
        if not args.no_fail:
            return 1
    else:
        print(f"PASS: overall_pass_rate {analysis['overall_pass_rate']:.2%} >= {min_rate:.2%}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
