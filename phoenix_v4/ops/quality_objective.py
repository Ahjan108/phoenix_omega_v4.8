"""
Quality-aware objective terms for Wave Optimizer (DWO-CS).

Deterministic helpers: normalize quality fields on candidates, compute wave-level
quality stats, and additive objective terms (CSI, ending strength, diversity, low-endings penalty).
"""

from __future__ import annotations

from typing import Any, Dict, List

# Neutral defaults when quality is missing (deterministic constants)
DEFAULT_CSI = 70.0
DEFAULT_ENDING_STRENGTH = 70.0


def normalize_quality(candidate: dict) -> dict:
    """
    Ensure candidate has normalized quality fields for scoring.
    If quality is missing, apply deterministic defaults; do not mutate input.
    """
    q = candidate.get("quality")
    if q and q.get("status") != "missing":
        return {
            "csi_score": float(q.get("csi_score") or DEFAULT_CSI),
            "ending_strength": float(q.get("ending_strength") or DEFAULT_ENDING_STRENGTH),
            "line_type_buckets": dict(q.get("line_type_buckets") or {}),
            "status": q.get("status") or "missing",
        }
    return {
        "csi_score": DEFAULT_CSI,
        "ending_strength": DEFAULT_ENDING_STRENGTH,
        "line_type_buckets": {},
        "status": "missing",
    }


def compute_wave_quality_stats(selected_candidates: List[dict]) -> dict:
    """
    From a list of selected candidates (with quality or defaults), compute
    mean_csi, mean_ending_strength, bucket_coverage, low_ending_ratio.
    """
    if not selected_candidates:
        return {
            "mean_csi": 0.0,
            "mean_ending_strength": 0.0,
            "bucket_coverage": 0.5,
            "low_ending_ratio": 0.0,
        }
    n = len(selected_candidates)
    csi_sum = 0.0
    end_sum = 0.0
    low_count = 0
    buckets_agg: Dict[str, int] = {}
    low_threshold = 65  # definition of "low ending"

    for c in selected_candidates:
        q = normalize_quality(c)
        csi_sum += q["csi_score"]
        end_sum += q["ending_strength"]
        if q["ending_strength"] < low_threshold:
            low_count += 1
        for k, v in (q.get("line_type_buckets") or {}).items():
            buckets_agg[k] = buckets_agg.get(k, 0) + v

    bucket_names = ["identity", "reframe", "relief", "directive"]
    covered = sum(1 for k in bucket_names if (buckets_agg.get(k) or 0) > 0)
    coverage = covered / len(bucket_names) if bucket_names else 0.5

    return {
        "mean_csi": csi_sum / n,
        "mean_ending_strength": end_sum / n,
        "bucket_coverage": coverage,
        "low_ending_ratio": low_count / n,
    }


def compute_quality_objective_terms(
    stats: dict,
    cfg: dict,
) -> dict:
    """
    Compute additive objective terms from wave quality stats and config.
    cfg: quality section with low_ending_threshold, max_low_ending_ratio, etc.
    """
    low_threshold = float(cfg.get("low_ending_threshold", 65))
    max_low_ratio = float(cfg.get("max_low_ending_ratio", 0.30))
    mean_csi = stats.get("mean_csi", 0) / 100.0
    mean_end = stats.get("mean_ending_strength", 0) / 100.0
    coverage = stats.get("bucket_coverage", 0.5)
    ratio_low = stats.get("low_ending_ratio", 0)
    p_low = max(0.0, ratio_low - max_low_ratio)
    return {
        "OBJ_quality_csi": mean_csi,
        "OBJ_quality_end": mean_end,
        "OBJ_quality_diversity": coverage,
        "OBJ_low_penalty": -p_low,
    }


def compute_quality_objective_score(terms: dict, weights: dict) -> float:
    """Weighted sum of quality objective terms."""
    w_csi = float(weights.get("quality_csi", 0))
    w_end = float(weights.get("quality_ending", 0))
    w_div = float(weights.get("quality_diversity", 0))
    w_low = float(weights.get("quality_low_endings_penalty", 0))
    return (
        w_csi * terms.get("OBJ_quality_csi", 0)
        + w_end * terms.get("OBJ_quality_end", 0)
        + w_div * terms.get("OBJ_quality_diversity", 0)
        + w_low * terms.get("OBJ_low_penalty", 0)
    )
