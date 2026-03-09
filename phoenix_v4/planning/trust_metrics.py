"""
EI v2 In Planning: trust metrics for auto-apply gating.
Compute observation_weeks, flag_rejection_rate, quality_lift_vs_baseline, recommendation_acceptance_rate
from historical_outcomes and optionally last N planning_advisory_report / audit log.
Authority: specs/EI_V2_IN_PLANNING_SPEC.md §5, §7.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _quality_scalar(row: Dict[str, Any]) -> Optional[float]:
    """Single quality number per outcome row: read_through if present, else 1 - (refund_rate + flag_rate)/2."""
    rt = row.get("read_through")
    if rt is not None:
        try:
            return float(rt)
        except (TypeError, ValueError):
            pass
    ref = row.get("refund_rate")
    flag = row.get("flag_rate")
    try:
        r = float(ref) if ref is not None else 0.0
        f = float(flag) if flag is not None else 0.0
        return 1.0 - (r + f) / 2.0
    except (TypeError, ValueError):
        return None


def compute_trust_metrics(
    historical_outcomes: List[Dict[str, Any]],
    report_path: Optional[Path] = None,
    audit_log_path: Optional[Path] = None,
    min_observation_weeks: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Compute current trust metrics for auto-apply eligibility.
    Returns dict with: observation_weeks, flag_rejection_rate, quality_lift_vs_baseline,
    recommendation_acceptance_rate, and optionally baseline_weeks (when min_observation_weeks is set).
    Baseline: first min_observation_weeks (chronologically) with advisory-only are the baseline cohort;
    quality_lift_vs_baseline = delta between post-baseline quality and baseline quality.
    """
    metrics: Dict[str, Any] = {
        "observation_weeks": 0,
        "flag_rejection_rate": 0.0,
        "quality_lift_vs_baseline": 0.0,
        "recommendation_acceptance_rate": 0.0,
    }
    if not historical_outcomes:
        return metrics

    weeks = set()
    flag_sum = 0.0
    rej_sum = 0.0
    n = 0
    for row in historical_outcomes:
        w = row.get("week")
        if w is not None and str(w).strip():
            weeks.add(str(w).strip())
        f = row.get("flag_rate")
        r = row.get("rejection_rate")
        if f is not None:
            try:
                flag_sum += float(f)
                n += 1
            except (TypeError, ValueError):
                pass
        if r is not None:
            try:
                rej_sum += float(r)
            except (TypeError, ValueError):
                pass
    metrics["observation_weeks"] = len(weeks)
    if n > 0:
        metrics["flag_rejection_rate"] = (flag_sum + rej_sum) / (2 * n) if n else 0.0

    if min_observation_weeks is not None and min_observation_weeks > 0 and weeks:
        sorted_weeks = sorted(weeks)
        baseline_weeks = set(sorted_weeks[: min_observation_weeks])
        baseline_qualities: List[float] = []
        post_baseline_qualities: List[float] = []
        for row in historical_outcomes:
            w = row.get("week")
            if w is None or not str(w).strip():
                continue
            q = _quality_scalar(row)
            if q is None:
                continue
            if str(w).strip() in baseline_weeks:
                baseline_qualities.append(q)
            else:
                post_baseline_qualities.append(q)
        if baseline_qualities and post_baseline_qualities:
            baseline_avg = sum(baseline_qualities) / len(baseline_qualities)
            post_avg = sum(post_baseline_qualities) / len(post_baseline_qualities)
            metrics["quality_lift_vs_baseline"] = post_avg - baseline_avg
            metrics["baseline_weeks"] = list(baseline_weeks)

    if metrics.get("quality_lift_vs_baseline", 0.0) == 0.0 and report_path and report_path.exists():
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
            meta = data.get("metadata") or {}
            if "quality_lift_vs_baseline" in meta:
                metrics["quality_lift_vs_baseline"] = float(meta["quality_lift_vs_baseline"])
        except (json.JSONDecodeError, OSError, TypeError):
            pass

    if audit_log_path and audit_log_path.exists():
        accepted = 0
        total = 0
        try:
            for line in audit_log_path.read_text(encoding="utf-8").strip().splitlines():
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    total += 1
                    if row.get("applied") or row.get("acceptance") == "approved":
                        accepted += 1
                except json.JSONDecodeError:
                    continue
            if total > 0:
                metrics["recommendation_acceptance_rate"] = accepted / total
        except OSError:
            pass

    return metrics


def is_trust_eligible(
    metrics: Dict[str, Any],
    trust_thresholds: Dict[str, Any],
) -> bool:
    """
    Return True if all trust thresholds are met for auto-apply.
    trust_thresholds: min_observation_weeks, max_flag_rejection_rate,
    min_quality_lift_vs_baseline, min_recommendation_acceptance_rate.
    """
    if not trust_thresholds:
        return False
    min_weeks = int(trust_thresholds.get("min_observation_weeks", 0))
    max_flag = float(trust_thresholds.get("max_flag_rejection_rate", 1.0))
    min_lift = float(trust_thresholds.get("min_quality_lift_vs_baseline", 0.0))
    min_accept = float(trust_thresholds.get("min_recommendation_acceptance_rate", 0.0))
    if metrics.get("observation_weeks", 0) < min_weeks:
        return False
    if metrics.get("flag_rejection_rate", 1.0) > max_flag:
        return False
    if metrics.get("quality_lift_vs_baseline", -1.0) < min_lift:
        return False
    if metrics.get("recommendation_acceptance_rate", 0.0) < min_accept:
        return False
    return True
