"""Scoring model — weighted scoring with reason codes."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_scoring_config() -> Tuple[Dict[str, float], Dict[str, float]]:
    """Load weights and penalties from config."""
    config_file = REPO_ROOT / "config" / "recommender" / "scoring_weights.yaml"
    if not config_file.exists():
        print(f"WARNING: Scoring weights config not found at {config_file}")
        return {}, {}

    with open(config_file) as f:
        data = yaml.safe_load(f) or {}

    weights = data.get("weights", {})
    penalties = data.get("penalties", {})
    return weights, penalties


def compute_score(features: Dict[str, float], weights: Dict[str, float],
                 penalties: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
    """
    Compute weighted score: sum(weight * feature) - sum(penalty * feature).
    Clamp to [0, 1].

    Returns:
        (score, breakdown) where breakdown shows each component's contribution.
    """
    positive_score = 0.0
    negative_score = 0.0
    breakdown = {}

    # Positive features
    for feature_name, feature_value in features.items():
        if feature_name in weights:
            weight = weights[feature_name]
            contribution = weight * feature_value
            positive_score += contribution
            breakdown[feature_name] = {
                "type": "weight",
                "feature_value": feature_value,
                "weight": weight,
                "contribution": contribution,
            }

    # Penalty features
    for feature_name, feature_value in features.items():
        if feature_name in penalties:
            penalty = penalties[feature_name]
            contribution = penalty * feature_value
            negative_score += contribution
            breakdown[feature_name] = {
                "type": "penalty",
                "feature_value": feature_value,
                "penalty": penalty,
                "contribution": contribution,
            }

    # Combined score
    raw_score = positive_score - negative_score
    clamped_score = max(0.0, min(1.0, raw_score))

    return clamped_score, breakdown


def extract_reason_codes(features: Dict[str, float], breakdown: Dict[str, Any]) -> List[str]:
    """
    Extract reason codes for high-value components.
    Include any component with contribution > 0.07 (threshold for visibility).
    """
    reason_codes = []
    code_map = {
        "market_demand": "high_demand",
        "coverage_gap": "coverage_gap",
        "performance_lift": "performance_lift",
        "teacher_fit": "strong_teacher_fit",
        "city_relevance": "city_relevant",
        "seasonality": "seasonal_demand",
        "strategic_priority": "strategic_priority",
        "brand_need": "brand_need",
        "duplication_risk": "duplication_risk",
        "saturation_penalty": "saturation_penalty",
        "policy_risk": "policy_risk",
    }

    for feature_name, detail in breakdown.items():
        contribution = detail.get("contribution", 0.0)
        if abs(contribution) > 0.07:  # Threshold for visibility
            if feature_name in code_map:
                code = code_map[feature_name]
                # Append direction indicator for penalties
                if detail.get("type") == "penalty" and contribution > 0:
                    code = f"{code}_risk"
                reason_codes.append(code)

    return sorted(reason_codes)


def score_candidate(candidate: Dict[str, Any],
                   features: Dict[str, float]) -> Dict[str, Any]:
    """
    Score a single candidate.

    Returns dict with: score, breakdown, reason_codes.
    """
    weights, penalties = load_scoring_config()
    score, breakdown = compute_score(features, weights, penalties)
    reason_codes = extract_reason_codes(features, breakdown)

    return {
        "score": score,
        "breakdown": breakdown,
        "reason_codes": reason_codes,
    }


def main():
    """Test scoring on a sample candidate with features."""
    sample_features = {
        "market_demand": 0.7,
        "coverage_gap": 0.9,
        "performance_lift": 0.5,
        "teacher_fit": 1.0,
        "city_relevance": 0.6,
        "seasonality": 0.4,
        "strategic_priority": 0.3,
        "brand_need": 0.5,
        "duplication_risk": 0.0,
        "saturation_penalty": 0.0,
        "policy_risk": 0.0,
    }

    sample_candidate = {
        "candidate_id": "abc123",
        "persona": "gen_z_professionals",
        "topic": "anxiety",
    }

    result = score_candidate(sample_candidate, sample_features)
    print("\n=== Scoring Result (Sample) ===")
    print(f"Score: {result['score']:.4f}")
    print(f"Reason codes: {', '.join(result['reason_codes'])}")
    print(f"\nBreakdown:")
    for feature_name, detail in sorted(result['breakdown'].items()):
        print(f"  {feature_name}: {detail['contribution']:+.4f} "
              f"({detail.get('weight', detail.get('penalty', 0)):.2f} × {detail['feature_value']:.2f})")


if __name__ == "__main__":
    main()
