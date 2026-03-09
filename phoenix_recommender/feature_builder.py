"""Feature builder — constructs feature vectors for scoring."""

from pathlib import Path
from typing import Any, Dict

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


def build_market_demand_feature(candidate: Dict[str, Any]) -> float:
    """
    Market demand: Check if signals/research/ directory exists.
    If signal files exist, score by freshness-weighted relevance.
    If not, return 0.5 (neutral — no data yet).

    For v1, stub implementation returns neutral score.
    """
    signals_dir = REPO_ROOT / "signals" / "research"
    if signals_dir.exists():
        # TODO: Implement actual signal scoring when data available
        return 0.5
    return 0.5


def build_coverage_gap_feature(candidate: Dict[str, Any]) -> float:
    """
    Catalog coverage: Count existing similar entries.
    If catalog/ directory doesn't exist, return high gap score (1.0 = high opportunity).
    If exists, count files matching persona+topic pattern and compute saturation.

    For v1, check if catalog exists; if not, return 1.0 (high gap).
    """
    catalog_dir = REPO_ROOT / "catalog"
    if not catalog_dir.exists():
        # No catalog yet = high coverage gap (opportunity)
        return 1.0

    # TODO: Implement actual saturation counting when catalog structured
    # For now, neutral score
    return 0.5


def build_performance_feature(candidate: Dict[str, Any]) -> float:
    """
    Performance: Stub for v1. Return 0.5 (neutral).

    TODO: When performance data flows from analytics, score by:
      - Engagement metrics for similar persona/topic combos
      - Completion rates
      - Learner satisfaction
    """
    return 0.5


def build_teacher_fit_feature(candidate: Dict[str, Any]) -> float:
    """
    Teacher fit: Check if teacher has atoms for this topic.
    Return 1.0 if covered (already validated by hard gates), 0.3 otherwise.
    """
    topic = candidate.get("topic")
    teacher = candidate.get("teacher")

    topic_file = REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices" / f"topic_{topic}.yaml"
    if not topic_file.exists():
        return 0.3

    try:
        with open(topic_file) as f:
            data = yaml.safe_load(f) or {}
        teachers = data.get("teachers", {})
        if teacher in teachers:
            return 1.0
    except Exception:
        pass

    return 0.3


def build_city_relevance_feature(candidate: Dict[str, Any]) -> float:
    """
    City relevance: Stub for v1. Return 0.5 (neutral).

    TODO: When market data available:
      - Score by audience density in city
      - Language prevalence in city
      - Demand signals from region
    """
    return 0.5


def build_seasonality_feature(candidate: Dict[str, Any]) -> float:
    """
    Seasonality: Stub for v1. Return 0.5 (neutral).

    TODO: When calendar/event data available:
      - Score by seasonal demand patterns
      - Event alignment
      - School/work cycle relevance
    """
    return 0.5


def build_strategic_priority_feature(candidate: Dict[str, Any]) -> float:
    """
    Strategic priority: Stub for v1. Return 0.5 (neutral).

    TODO: When strategic planning data available:
      - Score by quarterly objectives
      - Persona investment strategy
      - Topic expansion priorities
    """
    return 0.5


def build_brand_need_feature(candidate: Dict[str, Any]) -> float:
    """
    Brand need: Stub for v1. Return 0.5 (neutral).

    TODO: When brand requirements available:
      - Score by format availability per brand
      - Catalog gaps by brand
      - Brand-specific topic priorities
    """
    return 0.5


def build_duplication_risk_feature(candidate: Dict[str, Any]) -> float:
    """
    Duplication risk: 0.0 for v1 (will use semantic similarity later).
    Lower is better (less risk = lower penalty weight applied).
    """
    return 0.0


def build_saturation_penalty_feature(candidate: Dict[str, Any]) -> float:
    """
    Saturation penalty: Check catalog saturation for topic.
    Return 0.0 for v1 (no penalty yet without catalog).
    """
    return 0.0


def build_policy_risk_feature(candidate: Dict[str, Any]) -> float:
    """
    Policy risk: Default 0.0 (safe) for v1.

    TODO: When policy restrictions available:
      - Check content policy violations
      - Cultural sensitivity concerns
      - Topic restrictions by region
    """
    return 0.0


def build_feature_vector(candidate: Dict[str, Any]) -> Dict[str, float]:
    """
    Build complete feature vector for a candidate.

    Returns dict mapping feature_name -> score (0.0 to 1.0).
    """
    return {
        # Positive features (weights applied)
        "market_demand": build_market_demand_feature(candidate),
        "coverage_gap": build_coverage_gap_feature(candidate),
        "performance_lift": build_performance_feature(candidate),
        "teacher_fit": build_teacher_fit_feature(candidate),
        "city_relevance": build_city_relevance_feature(candidate),
        "seasonality": build_seasonality_feature(candidate),
        "strategic_priority": build_strategic_priority_feature(candidate),
        "brand_need": build_brand_need_feature(candidate),
        # Penalty features (penalties applied)
        "duplication_risk": build_duplication_risk_feature(candidate),
        "saturation_penalty": build_saturation_penalty_feature(candidate),
        "policy_risk": build_policy_risk_feature(candidate),
    }


def main():
    """Test feature building on a sample candidate."""
    sample_candidate = {
        "candidate_id": "abc123",
        "persona": "gen_z_professionals",
        "topic": "anxiety",
        "teacher": "ahjan",
        "language": "en",
        "format": "core",
        "city_overlay": "nyc",
    }

    features = build_feature_vector(sample_candidate)
    print("\n=== Feature Vector (Sample) ===")
    for feature_name, score in sorted(features.items()):
        print(f"  {feature_name}: {score:.2f}")


if __name__ == "__main__":
    main()
