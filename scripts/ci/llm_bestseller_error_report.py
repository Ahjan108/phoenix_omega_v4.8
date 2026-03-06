#!/usr/bin/env python3
"""
Read 10k simulation results (or analysis), identify bestseller-related failures,
and optionally have an LLM classify/summarize bestseller errors. 100% testing: use with
--min-pass-rate 1.0 in analyze_pearl_prime_sim.py to fail on any failure.
Usage:
  python scripts/ci/llm_bestseller_error_report.py --input artifacts/simulation_10k.json [--llm] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Format IDs that are "bestseller" tier (template/format name contains bestseller)
BESTSELLER_PREFIX = "bestseller"

# Heuristic root-cause buckets (order matters: first match wins)
ERROR_CATEGORY_PATTERNS = [
    ("insufficient_pool", ["insufficient pool", "capability_fail", "insufficient pool for plan"]),
    ("validation_rule", ["parts ", "characters_min", "characters_max", "slots", "tier", "integration_modes", "flinch", "reflection_max", "special story"]),
    ("phase2_waveform", ["waveform", "phase2_waveform"]),
    ("phase2_arc", ["arc_failed", "phase2_arc"]),
    ("phase2_drift", ["drift"]),
    ("phase3_volatility", ["volatility", "volatile"]),
    ("phase3_cognitive", ["cognitive", "cognitive_overload"]),
    ("phase3_consequence", ["consequence", "reaction"]),
    ("phase3_reassurance", ["reassurance", "repetition"]),
    ("unknown", []),
]
# High-risk tier/format: failure rate above this is flagged as bestseller-risk
HIGH_RISK_FAILURE_RATE = 0.20


def load_sim(path: Path) -> tuple[list[dict], dict]:
    """Load simulation JSON. Returns (results, summary)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data.get("results", [])
    summary = data.get("summary", {})
    return results, summary


def identify_bestseller_errors(results: list[dict]) -> dict:
    """From results, tag failures on bestseller formats, root-cause buckets, and risk scoring."""
    failed = [r for r in results if not r.get("passed")]
    bestseller_failures = [
        r for r in failed
        if BESTSELLER_PREFIX in (r.get("format_id") or "").lower()
    ]
    root_cause_buckets = bucket_failures_by_root_cause(failed)
    risk = compute_tier_format_risk(results)
    return {
        "total_failed": len(failed),
        "bestseller_failed": len(bestseller_failures),
        "bestseller_errors": [
            {
                "request_id": r.get("request_id"),
                "format_id": r.get("format_id"),
                "tier": r.get("tier"),
                "errors": r.get("errors", []),
                "phase2_errors": r.get("phase2_errors", []),
                "phase3_errors": r.get("phase3_errors", []),
                "root_cause": classify_error_root_cause(r.get("errors") or []),
            }
            for r in bestseller_failures[:50]  # cap for LLM context
        ],
        "all_failure_sample": [
            {
                "request_id": r.get("request_id"),
                "format_id": r.get("format_id"),
                "tier": r.get("tier"),
                "errors": (r.get("errors") or [])[:5],
                "root_cause": classify_error_root_cause(r.get("errors") or []),
            }
            for r in failed[:30]
        ],
        "error_reasons_summary": _count_error_reasons(failed),
        "root_cause_buckets": root_cause_buckets,
        "high_risk_formats": risk["high_risk_formats"],
        "high_risk_tiers": risk["high_risk_tiers"],
        "failure_rate_by_format": risk["failure_rate_by_format"],
        "failure_rate_by_tier": risk["failure_rate_by_tier"],
    }


def _count_error_reasons(failed: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in failed:
        for e in r.get("errors") or []:
            out[e] = out.get(e, 0) + 1
    return dict(sorted(out.items(), key=lambda x: -x[1]))


def classify_error_root_cause(errors: list[str]) -> str:
    """Map error messages to a single root-cause category (heuristic, no LLM)."""
    combined = " ".join(e.lower() for e in (errors or []))
    for category, patterns in ERROR_CATEGORY_PATTERNS:
        if category == "unknown":
            continue
        for p in patterns:
            if p in combined:
                return category
    return "unknown"


def bucket_failures_by_root_cause(failed: list[dict]) -> dict[str, int]:
    """Group failures by heuristic root cause."""
    buckets: dict[str, int] = {}
    for r in failed:
        cause = classify_error_root_cause(r.get("errors") or [])
        buckets[cause] = buckets.get(cause, 0) + 1
    return dict(sorted(buckets.items(), key=lambda x: -x[1]))


def compute_tier_format_risk(results: list[dict]) -> dict:
    """Flag formats/tiers with failure rate > HIGH_RISK_FAILURE_RATE as bestseller-risk."""
    by_format: dict[str, list[bool]] = {}
    by_tier: dict[str, list[bool]] = {}
    for r in results:
        fid = r.get("format_id") or "?"
        tier = r.get("tier") or "?"
        ok = r.get("passed", False)
        by_format.setdefault(fid, []).append(ok)
        by_tier.setdefault(tier, []).append(ok)
    high_risk_formats = [
        fid for fid, outcomes in by_format.items()
        if outcomes and (1 - sum(outcomes) / len(outcomes)) > HIGH_RISK_FAILURE_RATE
    ]
    high_risk_tiers = [
        t for t, outcomes in by_tier.items()
        if outcomes and (1 - sum(outcomes) / len(outcomes)) > HIGH_RISK_FAILURE_RATE
    ]
    return {
        "high_risk_formats": high_risk_formats,
        "high_risk_tiers": high_risk_tiers,
        "failure_rate_by_format": {f: 1 - sum(o) / len(o) if o else 0 for f, o in by_format.items()},
        "failure_rate_by_tier": {t: 1 - sum(o) / len(o) if o else 0 for t, o in by_tier.items()},
    }


def build_prompt_for_llm(identified: dict, summary: dict) -> str:
    """Build a single prompt text for the LLM to read and identify bestseller errors."""
    lines = [
        "## 10k book simulation failure summary",
        f"Total failed: {identified['total_failed']}",
        f"Failures on bestseller-tier formats: {identified['bestseller_failed']}",
        "",
        "### Error reason counts (all failures)",
        json.dumps(identified.get("error_reasons_summary", {}), indent=2),
        "",
        "### Bestseller-format failures (sample)",
        json.dumps(identified.get("bestseller_errors", [])[:20], indent=2),
        "",
        "### Other failure sample (format_id, tier, errors)",
        json.dumps(identified.get("all_failure_sample", [])[:15], indent=2),
    ]
    if summary.get("phase2"):
        lines.append("\n### Phase 2 summary")
        lines.append(json.dumps(summary["phase2"], indent=2))
    if summary.get("phase3"):
        lines.append("\n### Phase 3 summary")
        lines.append(json.dumps(summary["phase3"], indent=2))
    lines.append("")
    lines.append(
        "Identify and list: (1) bestseller error: any failure that indicates content or structure "
        "would not meet bestseller-tier quality (e.g. missing emotional force, weak structure, "
        "pool/plan issues that disproportionately affect premium formats). "
        "(2) Root cause category (e.g. insufficient_pool, validation_rule, phase2_volatility, phase3_cognitive). "
        "(3) One-line recommendation per category. Reply with valid JSON: "
        '{"bestseller_errors": [{"summary": "...", "cause": "..."}], "root_causes": [{"category": "...", "count_estimate": 0, "recommendation": "..."}]}'
    )
    return "\n".join(lines)


def call_llm(prompt: str, dry_run: bool) -> dict:
    """Optional LLM call to classify bestseller errors. Returns structured dict or empty."""
    if dry_run:
        return {"llm_skipped": True, "reason": "dry_run"}
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"llm_skipped": True, "reason": "no_api_key"}
    try:
        import anthropic
    except ImportError:
        return {"llm_skipped": True, "reason": "anthropic_not_installed"}
    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system="You are a QA analyst. Reply only with valid JSON.",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        if msg.content and isinstance(msg.content, list) and len(msg.content) > 0:
            block = msg.content[0]
            text = block.text if hasattr(block, "text") else (block.get("text", "") if isinstance(block, dict) else "")
            if text:
                # Extract JSON from markdown code block if present
                if "```" in text:
                    for part in text.split("```"):
                        if part.strip().startswith("json"):
                            text = part.strip()[4:].strip()
                            break
                        try:
                            return json.loads(part.strip())
                        except json.JSONDecodeError:
                            continue
                return json.loads(text)
    except Exception as e:
        return {"llm_skipped": True, "reason": "llm_error", "error": str(e)}
    return {"llm_skipped": True, "reason": "no_response"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Identify bestseller errors from 10k sim; optional LLM report")
    ap.add_argument("--input", "-i", required=True, help="Simulation JSON (e.g. artifacts/simulation_10k.json)")
    ap.add_argument("--out", "-o", default="", help="Output report dir (default: artifacts/reports)")
    ap.add_argument("--llm", action="store_true", help="Call LLM to classify and recommend")
    ap.add_argument("--dry-run", action="store_true", help="Skip LLM even if --llm")
    ap.add_argument("--strict", action="store_true", help="Fail if any format/tier has failure rate > 20% (bestseller-risk)")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"Error: input not found: {in_path}", file=sys.stderr)
        return 1

    results, summary = load_sim(in_path)
    identified = identify_bestseller_errors(results)

    out_dir = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Heuristic recommendations per root cause (no LLM)
    cause_recommendations = {
        "insufficient_pool": "Increase mock pool size or relax plan slot counts for sim; for real pipeline add atoms to pools.",
        "validation_rule": "Review validation_matrix and format rules; adjust tier/format constraints.",
        "phase2_waveform": "Check waveform/temperature curve config and volatile chapter assignment.",
        "phase2_arc": "Verify arc alignment and emotional_curve vs plan slots.",
        "phase2_drift": "Inspect drift stack rules and silence/volatile quotas.",
        "phase3_volatility": "Ensure volatile chapters have escalation/sensory/reaction density.",
        "phase3_cognitive": "Lower cognitive-to-body ratio or add body-lexeme content.",
        "phase3_consequence": "Add reaction markers after action verbs in consequence window.",
        "phase3_reassurance": "Reduce reassurance phrase repetition across chapters.",
        "unknown": "Inspect error messages and add pattern to ERROR_CATEGORY_PATTERNS.",
    }
    root_causes_with_rec = [
        {"category": c, "count": cnt, "recommendation": cause_recommendations.get(c, "")}
        for c, cnt in (identified.get("root_cause_buckets") or {}).items()
    ]

    report = {
        "bestseller_failed": identified["bestseller_failed"],
        "total_failed": identified["total_failed"],
        "bestseller_errors_sample": identified["bestseller_errors"],
        "error_reasons_summary": identified["error_reasons_summary"],
        "root_cause_buckets": identified.get("root_cause_buckets", {}),
        "root_causes_with_recommendations": root_causes_with_rec,
        "high_risk_formats": identified.get("high_risk_formats", []),
        "high_risk_tiers": identified.get("high_risk_tiers", []),
        "failure_rate_by_format": identified.get("failure_rate_by_format", {}),
        "failure_rate_by_tier": identified.get("failure_rate_by_tier", {}),
    }

    if args.llm:
        prompt = build_prompt_for_llm(identified, summary)
        llm_out = call_llm(prompt, args.dry_run)
        report["llm_analysis"] = llm_out
        if not llm_out.get("llm_skipped"):
            report["llm_bestseller_errors"] = llm_out.get("bestseller_errors", [])
            report["llm_root_causes"] = llm_out.get("root_causes", [])

    report_path = out_dir / "bestseller_error_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {report_path}")

    summary_lines = [
        "Bestseller Error Report (10k sim) — robust intelligent testing",
        f"Total failed: {identified['total_failed']}",
        f"Bestseller-format failures: {identified['bestseller_failed']}",
        "",
        "Root cause (heuristic):",
    ]
    for rc in root_causes_with_rec[:10]:
        rec = rc["recommendation"]
        summary_lines.append(f"  {rc['count']}: {rc['category']} — {(rec[:60] + '...') if len(rec) > 60 else rec}")
    summary_lines.append("")
    summary_lines.append("Error reason counts:")
    for reason, cnt in list(identified["error_reasons_summary"].items())[:15]:
        summary_lines.append(f"  {cnt}: {reason}")
    if identified.get("high_risk_formats") or identified.get("high_risk_tiers"):
        summary_lines.append("")
        summary_lines.append("High-risk (failure rate > 20%):")
        summary_lines.append(f"  formats: {identified.get('high_risk_formats', [])}")
        summary_lines.append(f"  tiers: {identified.get('high_risk_tiers', [])}")
    if report.get("llm_analysis") and not report["llm_analysis"].get("llm_skipped"):
        summary_lines.append("")
        summary_lines.append("LLM root causes:")
        for rc in report.get("llm_root_causes", []):
            summary_lines.append(f"  - {rc.get('category', '')}: {rc.get('recommendation', '')}")
    summary_path = out_dir / "bestseller_error_report_SUMMARY.txt"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"Wrote {summary_path}")

    # Intelligent gates: fail on bestseller failures; optional --strict = fail on high-risk format/tier
    if identified["bestseller_failed"] > 0:
        print(f"FAIL: {identified['bestseller_failed']} bestseller-format failure(s) (100% testing)", file=sys.stderr)
        return 1
    strict = getattr(args, "strict", False)
    if strict and (identified.get("high_risk_formats") or identified.get("high_risk_tiers")):
        print("FAIL: high-risk format/tier detected (--strict); see report", file=sys.stderr)
        return 1
    if identified["total_failed"] > 0 and args.llm:
        print("WARN: non-bestseller failures present; see report", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
