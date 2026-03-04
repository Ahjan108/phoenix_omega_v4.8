#!/usr/bin/env python3
"""
EI V2 Promotion Gate Checker

Reads the rigorous eval report and checks all V2 promotion criteria:
  Gate 1: Quality — composite score, per-dimension floors, agreement rate
  Gate 2: Performance — per-slot latency, V2/V1 ratio, per-book overhead
  Gate 3: Safety — zero regression, absolute floor, no silent drops

Appends result to promotion_history.jsonl for consecutive-pass tracking.
Writes promotion_gate_result.json with full breakdown.

Exit codes:
  0 = all gates pass (V2 is promotion-ready this run)
  1 = one or more gates fail (V1 stays authoritative)

Usage:
  PYTHONPATH=. python scripts/ci/check_ei_v2_promotion_gate.py \
    --eval-report artifacts/ei_v2/eval_rigorous_report.json \
    --criteria config/quality/ei_v2_promotion_criteria.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    import re
    text = path.read_text(encoding="utf-8")
    result: Dict[str, Any] = {}
    current_section = None
    current_sub = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and ":" in stripped:
            key, _, val = stripped.partition(":")
            val = val.strip()
            if val:
                if val == "true":
                    result[key.strip()] = True
                elif val == "false":
                    result[key.strip()] = False
                else:
                    try:
                        result[key.strip()] = float(val) if "." in val else int(val)
                    except ValueError:
                        result[key.strip()] = val
            else:
                current_section = key.strip()
                result[current_section] = {}
                current_sub = None
        elif current_section and line.startswith("  ") and not line.startswith("    "):
            key, _, val = stripped.partition(":")
            val = val.strip()
            if val:
                if val == "true":
                    result[current_section][key.strip()] = True
                elif val == "false":
                    result[current_section][key.strip()] = False
                else:
                    try:
                        result[current_section][key.strip()] = float(val) if "." in val else int(val)
                    except ValueError:
                        result[current_section][key.strip()] = val
            else:
                current_sub = key.strip()
                result[current_section][current_sub] = {}
        elif current_section and current_sub and line.startswith("    "):
            key, _, val = stripped.partition(":")
            val = val.strip()
            if val:
                if val == "true":
                    result[current_section][current_sub][key.strip()] = True
                elif val == "false":
                    result[current_section][current_sub][key.strip()] = False
                else:
                    try:
                        result[current_section][current_sub][key.strip()] = float(val) if "." in val else int(val)
                    except ValueError:
                        result[current_section][current_sub][key.strip()] = val
    return result


def check_quality_gate(
    eval_data: Dict[str, Any],
    criteria: Dict[str, Any],
) -> tuple[bool, List[str]]:
    """Gate 1: Quality checks."""
    quality_cfg = criteria.get("quality", {})
    issues: List[str] = []

    scores = eval_data.get("quality_scores", {})
    overall = scores.get("overall_composite", 0)
    min_overall = float(quality_cfg.get("min_overall_composite", 0.55))
    if overall < min_overall:
        issues.append(f"overall_composite {overall:.4f} < min {min_overall}")

    min_dims = quality_cfg.get("min_dimension_scores", {})
    for dim, floor in min_dims.items():
        actual = scores.get(dim, 0)
        if actual < float(floor):
            issues.append(f"{dim} {actual:.4f} < min {floor}")

    v1v2 = eval_data.get("v1_vs_v2", {})
    agreement = v1v2.get("agreement_rate", 0)
    min_agree = float(quality_cfg.get("min_v1v2_agreement_rate", 0.10))
    if agreement < min_agree:
        issues.append(f"v1v2_agreement_rate {agreement:.4f} < min {min_agree}")

    max_false_flags = int(quality_cfg.get("max_v2_false_safety_flags_per_book", 5))
    safety_flags = v1v2.get("safety_flags", 0)
    books = eval_data.get("meta", {}).get("books_evaluated", 1)
    flags_per_book = safety_flags / max(1, books)
    if flags_per_book > max_false_flags:
        issues.append(f"v2_safety_flags/book {flags_per_book:.1f} > max {max_false_flags}")

    return len(issues) == 0, issues


def check_performance_gate(
    eval_data: Dict[str, Any],
    criteria: Dict[str, Any],
) -> tuple[bool, List[str]]:
    """Gate 2: Performance checks."""
    perf_cfg = criteria.get("performance", {})
    issues: List[str] = []

    timing = eval_data.get("timing", {})
    books = eval_data.get("books", [])

    max_slot_ms = float(perf_cfg.get("max_v2_avg_slot_ms", 50.0))
    max_ratio = float(perf_cfg.get("max_v2_v1_ratio", 100.0))
    max_book_ms = float(perf_cfg.get("max_v2_per_book_ms", 5000.0))

    v2_slot_times = []
    v1_slot_times = []
    v2_book_times = []

    for book in books:
        v2_book_ms = book.get("v1v2_ms", 0)
        v2_book_times.append(v2_book_ms)
        if book.get("v1v2_avg_v2_ms", 0) > 0:
            v2_slot_times.append(book["v1v2_avg_v2_ms"])
        if book.get("v1v2_avg_v1_ms", 0) > 0:
            v1_slot_times.append(book["v1v2_avg_v1_ms"])

    if v2_slot_times:
        avg_v2_slot = sum(v2_slot_times) / len(v2_slot_times)
        if avg_v2_slot > max_slot_ms:
            issues.append(f"v2_avg_slot_ms {avg_v2_slot:.2f} > max {max_slot_ms}")

    if v1_slot_times and v2_slot_times:
        avg_v1 = sum(v1_slot_times) / len(v1_slot_times)
        avg_v2 = sum(v2_slot_times) / len(v2_slot_times)
        if avg_v1 > 0:
            ratio = avg_v2 / avg_v1
            if ratio > max_ratio:
                issues.append(f"v2/v1_ratio {ratio:.1f}x > max {max_ratio}x")

    if v2_book_times:
        avg_book = sum(v2_book_times) / len(v2_book_times)
        if avg_book > max_book_ms:
            issues.append(f"v2_per_book_ms {avg_book:.0f} > max {max_book_ms}")

    return len(issues) == 0, issues


def check_safety_gate(
    eval_data: Dict[str, Any],
    criteria: Dict[str, Any],
) -> tuple[bool, List[str]]:
    """Gate 3: Safety zero-regression checks."""
    safety_cfg = criteria.get("safety", {})
    issues: List[str] = []

    scores = eval_data.get("quality_scores", {})
    min_safety = float(safety_cfg.get("min_safety_compliance", 0.95))
    actual_safety = scores.get("safety_compliance", 0)
    if actual_safety < min_safety:
        issues.append(f"safety_compliance {actual_safety:.4f} < floor {min_safety}")

    max_regression = int(safety_cfg.get("max_safety_regression_count", 0))

    books = eval_data.get("books", [])
    regression_count = 0
    for book in books:
        for ch in book.get("chapters", []):
            if ch.get("safety_compliance", 1.0) < min_safety:
                regression_count += 1

    if regression_count > max_regression:
        issues.append(f"safety_regressions {regression_count} > max {max_regression}")

    return len(issues) == 0, issues


def check_dimension_gates_gate(
    eval_data: Dict[str, Any],
    criteria: Dict[str, Any],
) -> tuple[bool, List[str]]:
    """Gate 4: Dimension enforcement — per-chapter quality gates must pass."""
    dg_cfg = criteria.get("dimension_gates", {})
    issues: List[str] = []

    dg_summary = eval_data.get("dimension_gate_summary")
    if not dg_summary:
        issues.append(
            "dimension_gate_summary missing in eval report — "
            "run rigorous eval with dimension gates enabled"
        )
        return False, issues

    total_chapters = int(dg_summary.get("total_chapters", 0))
    if total_chapters == 0:
        return True, []

    fail_count = int(dg_summary.get("total_fail_count", 0))
    warn_count = int(dg_summary.get("total_warn_count", 0))

    max_fail_rate = float(dg_cfg.get("max_chapter_fail_rate", 0.20))
    fail_rate = fail_count / total_chapters
    if fail_rate > max_fail_rate:
        issues.append(
            f"chapter_fail_rate {fail_rate:.2%} > max {max_fail_rate:.0%} "
            f"({fail_count} fails / {total_chapters} chapters)"
        )

    max_warn_rate = float(dg_cfg.get("max_warn_rate", 0.50))
    warn_rate = warn_count / total_chapters
    if warn_rate > max_warn_rate:
        issues.append(
            f"chapter_warn_rate {warn_rate:.2%} > max {max_warn_rate:.0%} "
            f"({warn_count} warns / {total_chapters} chapters)"
        )

    min_pass_rates = dg_cfg.get("min_dimension_pass_rates", {})
    dim_pass_rates = dg_summary.get("dimension_pass_rates", {})
    for dim, min_rate in min_pass_rates.items():
        actual = dim_pass_rates.get(dim, 0)
        if actual < float(min_rate):
            issues.append(f"{dim} pass_rate {actual:.2%} < min {min_rate:.0%}")

    max_failures_per_book = int(dg_cfg.get("max_total_gate_failures_per_book", 3))
    per_book_failures = dg_summary.get("failures_per_book", [])
    for i, count in enumerate(per_book_failures):
        if count > max_failures_per_book:
            issues.append(
                f"book {i} gate_failures {count} > max {max_failures_per_book}"
            )

    return len(issues) == 0, issues


def check_hybrid_override_gate(
    eval_data: Dict[str, Any],
    criteria: Dict[str, Any],
) -> tuple[bool, List[str]]:
    """Gate 5: Hybrid override quality — overrides must improve outcomes."""
    ho_cfg = criteria.get("hybrid_override", {})
    issues: List[str] = []

    ho_data = eval_data.get("hybrid_override")
    if not ho_data:
        issues.append(
            "hybrid_override data missing in eval report — "
            "run rigorous eval with --hybrid to collect override/block statistics"
        )
        return False, issues

    total_slots = int(ho_data.get("total_slots", 0))
    override_count = int(ho_data.get("override_count", 0))
    block_count = int(ho_data.get("block_count", 0))
    override_success_count = int(ho_data.get("override_success_count", 0))

    if total_slots == 0:
        return True, []

    min_success_rate = float(ho_cfg.get("min_override_success_rate", 0.60))
    if override_count > 0:
        success_rate = override_success_count / override_count
        if success_rate < min_success_rate:
            issues.append(
                f"override_success_rate {success_rate:.2%} < min {min_success_rate:.0%} "
                f"({override_success_count}/{override_count} overrides improved)"
            )
    # When override_count==0, success rate is vacuously 1.0 — pass

    max_override_rate = float(ho_cfg.get("max_override_rate", 0.40))
    override_rate = override_count / total_slots
    if override_rate > max_override_rate:
        issues.append(
            f"override_rate {override_rate:.2%} > max {max_override_rate:.0%} "
            f"({override_count}/{total_slots} slots)"
        )

    max_block_rate = float(ho_cfg.get("max_block_rate", 0.20))
    block_rate = block_count / total_slots
    if block_rate > max_block_rate:
        issues.append(
            f"block_rate {block_rate:.2%} > max {max_block_rate:.0%} "
            f"({block_count}/{total_slots} slots)"
        )

    return len(issues) == 0, issues


def update_history(
    history_path: Path,
    passed: bool,
    result: Dict[str, Any],
) -> int:
    """Append to promotion_history.jsonl, return consecutive pass count."""
    history_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "overall_composite": result.get("quality_scores", {}).get("overall_composite"),
        "safety_compliance": result.get("quality_scores", {}).get("safety_compliance"),
        "agreement_rate": result.get("v1_vs_v2", {}).get("agreement_rate"),
    }

    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    consecutive = 0
    if history_path.exists():
        lines = history_path.read_text(encoding="utf-8").strip().splitlines()
        for line in reversed(lines):
            try:
                rec = json.loads(line)
                if rec.get("passed"):
                    consecutive += 1
                else:
                    break
            except (json.JSONDecodeError, KeyError):
                break

    return consecutive


def main() -> int:
    ap = argparse.ArgumentParser(description="EI V2 promotion gate checker")
    ap.add_argument("--eval-report", required=True, help="Path to eval_rigorous_report.json")
    ap.add_argument("--criteria", required=True, help="Path to ei_v2_promotion_criteria.yaml")
    ap.add_argument("--out", default=None, help="Output path (default: artifacts/ei_v2/promotion_gate_result.json)")
    args = ap.parse_args()

    eval_path = Path(args.eval_report)
    criteria_path = Path(args.criteria)

    if not eval_path.exists():
        print(f"ERROR: eval report not found: {eval_path}", file=sys.stderr)
        return 1
    if not criteria_path.exists():
        print(f"ERROR: criteria file not found: {criteria_path}", file=sys.stderr)
        return 1

    eval_data = json.loads(eval_path.read_text(encoding="utf-8"))
    criteria = _load_yaml(criteria_path)

    print("=" * 55)
    print("  EI V2 PROMOTION GATE CHECK")
    print("=" * 55)

    q_pass, q_issues = check_quality_gate(eval_data, criteria)
    p_pass, p_issues = check_performance_gate(eval_data, criteria)
    s_pass, s_issues = check_safety_gate(eval_data, criteria)
    dg_pass, dg_issues = check_dimension_gates_gate(eval_data, criteria)
    ho_pass, ho_issues = check_hybrid_override_gate(eval_data, criteria)

    all_pass = q_pass and p_pass and s_pass and dg_pass and ho_pass

    print(f"\n  Gate 1 — Quality:         {'PASS' if q_pass else 'FAIL'}")
    for iss in q_issues:
        print(f"    - {iss}")

    print(f"  Gate 2 — Performance:   {'PASS' if p_pass else 'FAIL'}")
    for iss in p_issues:
        print(f"    - {iss}")

    print(f"  Gate 3 — Safety:        {'PASS' if s_pass else 'FAIL'}")
    for iss in s_issues:
        print(f"    - {iss}")

    print(f"  Gate 4 — Dimension gates: {'PASS' if dg_pass else 'FAIL'}")
    for iss in dg_issues:
        print(f"    - {iss}")

    print(f"  Gate 5 — Hybrid override: {'PASS' if ho_pass else 'FAIL'}")
    for iss in ho_issues:
        print(f"    - {iss}")

    promo_cfg = criteria.get("promotion", {})
    history_path = REPO_ROOT / (promo_cfg.get("history_file", "artifacts/ei_v2/promotion_history.jsonl"))
    consecutive = update_history(history_path, all_pass, eval_data)
    required = int(promo_cfg.get("consecutive_passes_required", 5))

    print(f"\n  Consecutive passes: {consecutive} / {required} required")

    promotion_ready = all_pass and consecutive >= required
    auto_promote = promo_cfg.get("auto_promote", False)

    if promotion_ready:
        if auto_promote:
            print("\n  PROMOTION: READY — auto-promote is ON")
            print("  V2 would replace V1 as production selector.")
        else:
            print(f"\n  PROMOTION: READY — {consecutive} consecutive passes achieved")
            print("  auto_promote is OFF — manual approval required to flip V1 → V2.")
    elif all_pass:
        print(f"\n  PROMOTION: NOT YET — gates pass but need {required - consecutive} more consecutive runs")
    else:
        print(f"\n  PROMOTION: BLOCKED — fix failing gates above")
        print("  V1 remains authoritative. V2 is advisory only.")

    print("\n" + "=" * 55)

    out_path = Path(args.out) if args.out else (REPO_ROOT / "artifacts" / "ei_v2" / "promotion_gate_result.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "all_gates_pass": all_pass,
        "promotion_ready": promotion_ready,
        "consecutive_passes": consecutive,
        "consecutive_required": required,
        "auto_promote": auto_promote,
        "gate_1_quality": {"pass": q_pass, "issues": q_issues},
        "gate_2_performance": {"pass": p_pass, "issues": p_issues},
        "gate_3_safety": {"pass": s_pass, "issues": s_issues},
        "gate_4_dimension_gates": {"pass": dg_pass, "issues": dg_issues},
        "gate_5_hybrid_override": {"pass": ho_pass, "issues": ho_issues},
        "eval_summary": {
            "overall_composite": eval_data.get("quality_scores", {}).get("overall_composite"),
            "safety_compliance": eval_data.get("quality_scores", {}).get("safety_compliance"),
            "agreement_rate": eval_data.get("v1_vs_v2", {}).get("agreement_rate"),
            "books_evaluated": eval_data.get("meta", {}).get("books_evaluated"),
        },
    }

    out_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"\n  Result written: {out_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
