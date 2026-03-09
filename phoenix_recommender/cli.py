"""CLI entry point — argument parsing and main flow."""

import argparse
import json
import sys
from pathlib import Path

from .candidate_generator import generate_candidates
from .feature_builder import build_feature_vector
from .ranker import rank_candidates
from .recommendation_report import generate_reports
from .scoring_model import score_candidate


REPO_ROOT = Path(__file__).resolve().parent.parent


def print_candidates_summary(candidates):
    """Pretty-print candidate summary."""
    print(f"\n{'='*70}")
    print(f"CANDIDATE GENERATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total candidates generated: {len(candidates)}")

    if candidates:
        print(f"\nFirst 10 candidates:")
        for i, c in enumerate(candidates[:10], 1):
            print(f"  {i}. {c['candidate_id']}: "
                  f"{c['persona']} × {c['topic']} × {c['teacher']} × "
                  f"{c['language']} × {c['format']} × {c['city_overlay']}")

        # Diversity stats
        unique_personas = len(set(c["persona"] for c in candidates))
        unique_topics = len(set(c["topic"] for c in candidates))
        unique_teachers = len(set(c["teacher"] for c in candidates))
        unique_languages = len(set(c["language"] for c in candidates))

        print(f"\nDiversity metrics:")
        print(f"  Personas: {unique_personas}")
        print(f"  Topics: {unique_topics}")
        print(f"  Teachers: {unique_teachers}")
        print(f"  Languages: {unique_languages}")


def score_all_candidates(candidates):
    """Score all candidates and return scored list."""
    print(f"\n{'='*70}")
    print(f"FEATURE BUILDING & SCORING")
    print(f"{'='*70}")
    print(f"Scoring {len(candidates)} candidates...")

    scored = []
    for i, candidate in enumerate(candidates):
        if (i + 1) % max(1, len(candidates) // 10) == 0:
            print(f"  Progress: {i + 1}/{len(candidates)}")

        features = build_feature_vector(candidate)
        score_result = score_candidate(candidate, features)

        scored_candidate = candidate.copy()
        scored_candidate.update(score_result)
        scored.append(scored_candidate)

    return scored


def print_ranking_summary(ranked):
    """Pretty-print ranking summary."""
    print(f"\n{'='*70}")
    print(f"RANKING SUMMARY")
    print(f"{'='*70}")
    print(f"Top {len(ranked)} candidates ranked:")

    for r in ranked[:10]:
        print(f"  #{r.get('position', '?')}: {r['candidate_id']} "
              f"(score: {r.get('score', 0):.4f}, slot: {r.get('slot_type', '?')})")
        reasons = r.get("reason_codes", [])
        if reasons:
            print(f"    Reasons: {', '.join(reasons[:3])}")


def explain_candidate(candidate_id, scored_candidates):
    """Print full breakdown for a single candidate."""
    candidate = None
    for c in scored_candidates:
        if c.get("candidate_id") == candidate_id:
            candidate = c
            break

    if not candidate:
        print(f"ERROR: Candidate {candidate_id} not found")
        return

    print(f"\n{'='*70}")
    print(f"CANDIDATE EXPLANATION: {candidate_id}")
    print(f"{'='*70}")
    print(f"\nBasic Info:")
    print(f"  Persona: {candidate['persona']}")
    print(f"  Topic: {candidate['topic']}")
    print(f"  Teacher: {candidate['teacher']}")
    print(f"  Language: {candidate['language']}")
    print(f"  Format: {candidate['format']}")
    print(f"  City: {candidate['city_overlay']}")

    print(f"\nScore: {candidate.get('score', 0):.4f}")
    print(f"\nReason Codes: {', '.join(candidate.get('reason_codes', []))}")

    breakdown = candidate.get("breakdown", {})
    if breakdown:
        print(f"\nDetailed Breakdown:")
        for feature_name, detail in sorted(breakdown.items()):
            contribution = detail.get("contribution", 0.0)
            feature_value = detail.get("feature_value", 0.0)
            weight_or_penalty = detail.get("weight", detail.get("penalty", 0.0))
            print(f"  {feature_name}:")
            print(f"    Feature value: {feature_value:.4f}")
            print(f"    Weight/Penalty: {weight_or_penalty:.4f}")
            print(f"    Contribution: {contribution:+.4f}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Phoenix Recommender v1 — Book recommendation engine"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="Number of top recommendations to return (default: 50)"
    )
    parser.add_argument(
        "--explore-ratio",
        type=float,
        help="Explore/exploit split ratio (overrides config)"
    )
    parser.add_argument(
        "--out",
        type=str,
        default="artifacts/recommendations/",
        help="Output directory for reports (default: artifacts/recommendations/)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show candidates without scoring or ranking"
    )
    parser.add_argument(
        "--explain",
        type=str,
        help="Show full breakdown for a single candidate ID"
    )
    parser.add_argument(
        "--brands",
        type=str,
        help="Filter by brands (comma-separated, optional for v1)"
    )

    args = parser.parse_args()

    # Step 1: Generate candidates
    print(f"\n{'='*70}")
    print(f"PHOENIX RECOMMENDER v1.0.0")
    print(f"{'='*70}")

    candidates = generate_candidates()

    if not candidates:
        print("ERROR: No candidates generated. Check configuration and data files.")
        sys.exit(1)

    print_candidates_summary(candidates)

    # Dry-run mode: exit after candidate generation
    if args.dry_run:
        print("\n[DRY RUN MODE] Exiting after candidate generation.")
        sys.exit(0)

    # Step 2: Score candidates
    scored_candidates = score_all_candidates(candidates)

    # Step 3: Rank candidates
    print(f"\n{'='*70}")
    print(f"RANKING & CONSTRAINT APPLICATION")
    print(f"{'='*70}")
    ranked_candidates = rank_candidates(scored_candidates, top_n=args.top)
    print_ranking_summary(ranked_candidates)

    # Step 4: Generate reports
    print(f"\n{'='*70}")
    print(f"GENERATING REPORTS")
    print(f"{'='*70}")
    json_path, md_path = generate_reports(ranked_candidates, args.out)
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")

    # Step 5: Explain mode (if requested)
    if args.explain:
        explain_candidate(args.explain, scored_candidates)

    print(f"\n{'='*70}")
    print(f"COMPLETE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
