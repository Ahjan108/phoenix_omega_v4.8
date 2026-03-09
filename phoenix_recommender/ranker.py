"""Ranker — applies constraints and exploit/explore split."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_constraints_config() -> Dict[str, Any]:
    """Load constraints from config."""
    config_file = REPO_ROOT / "config" / "recommender" / "constraints.yaml"
    if not config_file.exists():
        print(f"WARNING: Constraints config not found at {config_file}")
        return {}

    with open(config_file) as f:
        data = yaml.safe_load(f) or {}
    return data


def apply_per_cycle_limits(scored_candidates: List[Dict[str, Any]],
                           constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply per-cycle limits: max per brand, max per topic, max per teacher.
    Track counts and skip candidates that exceed limits.

    Returns filtered list.
    """
    limits = constraints.get("per_cycle", {})
    max_per_brand = limits.get("max_per_brand", 5)
    max_per_topic = limits.get("max_per_topic", 8)
    max_per_teacher = limits.get("max_per_teacher", 6)

    # For v1, we don't have explicit brand field, so we track differently
    # Brand tracking will be added when brand data is available
    brand_count = {}
    topic_count = {}
    teacher_count = {}

    filtered = []
    for candidate in scored_candidates:
        topic = candidate.get("topic")
        teacher = candidate.get("teacher")
        brand = candidate.get("brand", "default")  # Default if not specified

        # Check limits
        if brand_count.get(brand, 0) >= max_per_brand:
            continue
        if topic_count.get(topic, 0) >= max_per_topic:
            continue
        if teacher_count.get(teacher, 0) >= max_per_teacher:
            continue

        # Increment counters
        brand_count[brand] = brand_count.get(brand, 0) + 1
        topic_count[topic] = topic_count.get(topic, 0) + 1
        teacher_count[teacher] = teacher_count.get(teacher, 0) + 1

        filtered.append(candidate)

    return filtered


def apply_language_floors(scored_candidates: List[Dict[str, Any]],
                         constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Enforce language floor constraints.
    Each language must represent at least floor% of top N recommendations.

    For v1, we log but don't reject; constraints apply post-ranking.
    """
    floors = constraints.get("language_floors", {})
    if not floors or not scored_candidates:
        return scored_candidates

    # Count language distribution
    language_counts = {}
    for candidate in scored_candidates:
        lang = candidate.get("language")
        language_counts[lang] = language_counts.get(lang, 0) + 1

    total = len(scored_candidates)
    for lang, floor in floors.items():
        actual_ratio = language_counts.get(lang, 0) / total if total > 0 else 0
        if actual_ratio < floor:
            print(f"WARNING: Language {lang} floor {floor:.0%} not met (actual: {actual_ratio:.0%})")

    return scored_candidates


def apply_diversity_constraints(scored_candidates: List[Dict[str, Any]],
                               constraints: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Check diversity minimums (unique personas, topics, teachers).
    Log warnings if minimums not met, but don't reject.

    Returns (candidates, diversity_metrics).
    """
    diversity = constraints.get("diversity", {})
    min_personas = diversity.get("min_unique_personas", 5)
    min_topics = diversity.get("min_unique_topics", 8)
    min_teachers = diversity.get("min_unique_teachers", 4)

    if not scored_candidates:
        return scored_candidates, {}

    unique_personas = set(c.get("persona") for c in scored_candidates)
    unique_topics = set(c.get("topic") for c in scored_candidates)
    unique_teachers = set(c.get("teacher") for c in scored_candidates)

    metrics = {
        "unique_personas": len(unique_personas),
        "unique_topics": len(unique_topics),
        "unique_teachers": len(unique_teachers),
    }

    if len(unique_personas) < min_personas:
        print(f"WARNING: Persona diversity {len(unique_personas)} below minimum {min_personas}")
    if len(unique_topics) < min_topics:
        print(f"WARNING: Topic diversity {len(unique_topics)} below minimum {min_topics}")
    if len(unique_teachers) < min_teachers:
        print(f"WARNING: Teacher diversity {len(unique_teachers)} below minimum {min_teachers}")

    return scored_candidates, metrics


def apply_explore_exploit_split(scored_candidates: List[Dict[str, Any]],
                               constraints: Dict[str, Any],
                               top_n: int) -> List[Dict[str, Any]]:
    """
    Apply explore/exploit split:
      - First (1 - explore_ratio) slots = highest score (exploit)
      - Remaining slots = moderate score + high uncertainty (explore)

    Tags each with slot_type: "exploit" or "explore".
    """
    explore_ratio = constraints.get("explore_ratio", 0.20)
    if not scored_candidates or top_n <= 0:
        return scored_candidates

    # Calculate split
    exploit_count = max(1, int(top_n * (1 - explore_ratio)))
    explore_count = top_n - exploit_count

    result = []

    # Exploit: highest scores
    exploit_candidates = scored_candidates[:exploit_count]
    for i, candidate in enumerate(exploit_candidates):
        candidate_copy = candidate.copy()
        candidate_copy["slot_type"] = "exploit"
        candidate_copy["position"] = i + 1
        result.append(candidate_copy)

    # Explore: remaining candidates (could be high uncertainty with moderate score)
    explore_candidates = scored_candidates[exploit_count:exploit_count + explore_count]
    for i, candidate in enumerate(explore_candidates):
        candidate_copy = candidate.copy()
        candidate_copy["slot_type"] = "explore"
        candidate_copy["position"] = exploit_count + i + 1
        result.append(candidate_copy)

    return result


def rank_candidates(scored_candidates: List[Dict[str, Any]], top_n: int = 50) -> List[Dict[str, Any]]:
    """
    Main ranking function. Apply constraints and split.

    Steps:
      1. Sort by score descending
      2. Apply per-cycle limits
      3. Apply language floors
      4. Check diversity
      5. Apply exploit/explore split
      6. Tag with position, score, reason_codes, slot_type

    Returns ranked list with metadata.
    """
    constraints = load_constraints_config()

    # Sort by score descending
    sorted_candidates = sorted(scored_candidates, key=lambda x: x.get("score", 0.0), reverse=True)

    # Apply per-cycle limits
    limited = apply_per_cycle_limits(sorted_candidates, constraints)

    # Apply language floors
    limited = apply_language_floors(limited, constraints)

    # Check diversity
    limited, diversity_metrics = apply_diversity_constraints(limited, constraints)

    # Apply exploit/explore split
    ranked = apply_explore_exploit_split(limited, constraints, top_n)

    # Attach diversity metrics to first result (for reporting)
    if ranked:
        ranked[0]["_diversity_metrics"] = diversity_metrics

    return ranked


def main():
    """Test ranking on sample scored candidates."""
    sample_scored = [
        {
            "candidate_id": "abc123",
            "persona": "gen_z_professionals",
            "topic": "anxiety",
            "teacher": "ahjan",
            "language": "en",
            "city_overlay": "nyc",
            "score": 0.75,
            "reason_codes": ["high_demand", "coverage_gap"],
        },
        {
            "candidate_id": "def456",
            "persona": "millennial_women_professionals",
            "topic": "burnout",
            "teacher": "miki",
            "language": "ja-JP",
            "city_overlay": "tokyo",
            "score": 0.68,
            "reason_codes": ["coverage_gap"],
        },
        {
            "candidate_id": "ghi789",
            "persona": "tech_finance_burnout",
            "topic": "boundaries",
            "teacher": "junko",
            "language": "en",
            "city_overlay": "london",
            "score": 0.62,
            "reason_codes": ["strong_teacher_fit"],
        },
    ]

    ranked = rank_candidates(sample_scored, top_n=2)
    print("\n=== Ranked Results (Sample, top 2) ===")
    for r in ranked:
        print(f"  #{r['position']}: {r['candidate_id']} (score: {r['score']:.4f}, slot: {r['slot_type']})")
        print(f"    Reasons: {', '.join(r.get('reason_codes', []))}")


if __name__ == "__main__":
    main()
