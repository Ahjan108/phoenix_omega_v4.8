#!/usr/bin/env python3
"""
Assembly Loop — Persona × Topic Brief Builder

Reads unified signal store, groups by (persona_id, topic_id),
and produces structured briefs for downstream consumption by
EI V2, prompt patch proposals, and content assembly.

Phase 2 pilot: 3 personas × 5 topics = 15 pairs.
Phase 3 full: all 10 × 15 = 150 pairs.

Usage:
  python3 scripts/marketing/build_persona_topic_briefs.py --pilot
  python3 scripts/marketing/build_persona_topic_briefs.py --all
  python3 scripts/marketing/build_persona_topic_briefs.py --persona gen_z_professionals --topic anxiety
  python3 scripts/marketing/build_persona_topic_briefs.py --dry-run
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import math
import re
from uuid import uuid4


PILOT_PERSONAS = [
    "gen_z_professionals",
    "millennial_women_professionals",
    "healthcare_rns",
]

PILOT_TOPICS = [
    "anxiety",
    "burnout",
    "sleep_anxiety",
    "self_worth",
    "boundaries",
]


def _load_yaml_config(path: str) -> dict:
    """Load YAML config file (basic parsing)."""
    try:
        import yaml
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback: simple YAML parsing for basic key-value pairs
        config = {}
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            k, v = line.split(':', 1)
                            config[k.strip()] = v.strip()
        except FileNotFoundError:
            pass
        return config


def _load_signals(
    signal_dir: str,
    persona_filter: Optional[List[str]] = None,
    topic_filter: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Read all JSONL files from signal store, filter by persona and topic.

    Args:
        signal_dir: Path to artifacts/marketing/signals/
        persona_filter: List of persona_ids to include (None = all)
        topic_filter: List of topic_ids to include (None = all)

    Returns:
        List of signal dicts
    """
    signals = []
    signal_path = Path(signal_dir)

    if not signal_path.exists():
        print(f"Warning: Signal directory does not exist: {signal_dir}", file=sys.stderr)
        return signals

    for jsonl_file in signal_path.glob("*.jsonl"):
        try:
            with open(jsonl_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            signal = json.loads(line)

                            # Apply filters
                            if persona_filter and signal.get("persona_id") not in persona_filter:
                                continue
                            if topic_filter and signal.get("topic_id") not in topic_filter:
                                continue

                            signals.append(signal)
                        except json.JSONDecodeError as e:
                            print(f"Warning: Invalid JSON in {jsonl_file}: {e}", file=sys.stderr)
        except IOError as e:
            print(f"Warning: Could not read {jsonl_file}: {e}", file=sys.stderr)

    return signals


def _apply_freshness_decay(signals: List[Dict], config: Dict) -> List[Dict]:
    """
    Apply exponential decay to confidence scores based on signal age.

    Decay formula: confidence_decayed = confidence * exp(-age_days / max_age_days)

    Args:
        signals: List of signal dicts
        config: Config dict with research_max_age_days and sales_max_age_days

    Returns:
        List of signals with decayed confidence scores
    """
    research_max_age = config.get("research_max_age_days", 30)
    sales_max_age = config.get("sales_max_age_days", 7)

    now = datetime.utcnow()
    decayed = []

    for signal in signals:
        signal_copy = signal.copy()

        try:
            timestamp_str = signal.get("timestamp_utc", "")
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            age_days = (now - timestamp).days
        except (ValueError, AttributeError):
            age_days = 0

        # Select max age based on signal type
        signal_type = signal.get("signal_type", "").lower()
        if "sales" in signal_type or "revenue" in signal_type:
            max_age = sales_max_age
        else:
            max_age = research_max_age

        # Apply exponential decay
        if age_days > 0 and max_age > 0:
            decay_factor = math.exp(-age_days / max_age)
        else:
            decay_factor = 1.0

        original_confidence = signal_copy.get("confidence", 0.5)
        signal_copy["confidence_original"] = original_confidence
        signal_copy["confidence"] = original_confidence * decay_factor
        signal_copy["age_days"] = age_days
        signal_copy["decay_factor"] = decay_factor

        decayed.append(signal_copy)

    return decayed


def _group_by_persona_topic(signals: List[Dict]) -> Dict[Tuple[str, str], List[Dict]]:
    """
    Group signals by (persona_id, topic_id) pair.

    Returns:
        Dict mapping (persona_id, topic_id) -> list of signals
    """
    groups = defaultdict(list)
    for signal in signals:
        persona_id = signal.get("persona_id")
        topic_id = signal.get("topic_id")
        if persona_id and topic_id:
            groups[(persona_id, topic_id)].append(signal)
    return dict(groups)


def _extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract trending keywords from text payload.
    Simple heuristic: capitalize-case words and multi-word phrases.
    """
    if not text or not isinstance(text, str):
        return []

    # Simple keyword extraction: words > 4 chars, case-sensitive
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    # Also include common lowercase terms that appear multiple times
    all_words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    word_freq = defaultdict(int)
    for word in all_words:
        word_freq[word] += 1

    frequent_words = [w for w, count in word_freq.items() if count >= 2]

    keywords = list(set(words + frequent_words))[:max_keywords]
    return sorted(keywords)


def _build_brief(
    persona_id: str,
    topic_id: str,
    signals: List[Dict],
) -> Dict:
    """
    Build a structured brief from signals.

    Returns:
        Brief dict with persona_id, topic_id, signal_count, avg_confidence, etc.
    """
    if not signals:
        return {
            "persona_id": persona_id,
            "topic_id": topic_id,
            "signal_count": 0,
            "avg_confidence": 0.0,
            "top_research_claims": [],
            "sales_trend_summary": "insufficient_data",
            "content_outcome_summary": [],
            "trend_keywords": [],
            "freshness_score": 0.0,
            "recommended_actions": ["collect_more_signals"],
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    # Calculate aggregate stats
    signal_count = len(signals)
    confidences = [s.get("confidence", 0.5) for s in signals if s.get("confidence") is not None]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    # Sort by confidence × freshness (decay already applied)
    scored_signals = []
    for sig in signals:
        score = sig.get("confidence", 0.5)
        if sig.get("decay_factor"):
            score *= sig.get("decay_factor", 1.0)
        scored_signals.append((score, sig))

    scored_signals.sort(key=lambda x: x[0], reverse=True)
    top_research = scored_signals[:5]

    # Extract research claims
    research_claims = []
    for score, sig in top_research:
        payload = sig.get("payload", {})
        claim = payload.get("claim") or payload.get("insight") or str(payload)
        if claim:
            research_claims.append({
                "claim": claim[:200],  # Truncate
                "confidence": sig.get("confidence", 0.0),
                "source": sig.get("source", "unknown"),
            })

    # Sales trend analysis
    sales_signals = [s for s in signals if "sales" in s.get("signal_type", "").lower()]
    if sales_signals:
        sales_trends = [s.get("payload", {}).get("trend") for s in sales_signals]
        if "up" in str(sales_trends).lower():
            trend_summary = "up"
        elif "down" in str(sales_trends).lower():
            trend_summary = "down"
        else:
            trend_summary = "flat"
    else:
        trend_summary = "no_sales_signals"

    # Content outcomes
    content_signals = [s for s in signals if "content" in s.get("signal_type", "").lower()]
    outcomes = []
    for sig in content_signals:
        payload = sig.get("payload", {})
        perf = payload.get("performance") or payload.get("outcome")
        if perf:
            outcomes.append(perf)

    # Extract trend keywords from all payloads
    all_text = " ".join(str(s.get("payload", {})) for s in signals)
    keywords = _extract_keywords(all_text, max_keywords=8)

    # Freshness score: avg of decay factors
    decay_factors = [s.get("decay_factor", 1.0) for s in signals]
    freshness_score = sum(decay_factors) / len(decay_factors) if decay_factors else 0.0

    # Recommended actions
    actions = []
    if avg_confidence < 0.6:
        actions.append("increase_sampling")
    if freshness_score < 0.5:
        actions.append("refresh_signals")
    if trend_summary == "up":
        actions.append("expand_reach")
    if trend_summary == "down":
        actions.append("adjust_messaging")
    if not actions:
        actions.append("maintain_current_approach")

    return {
        "persona_id": persona_id,
        "topic_id": topic_id,
        "signal_count": signal_count,
        "avg_confidence": round(avg_confidence, 3),
        "top_research_claims": research_claims,
        "sales_trend_summary": trend_summary,
        "content_outcome_summary": outcomes[:3],
        "trend_keywords": keywords,
        "freshness_score": round(freshness_score, 3),
        "recommended_actions": actions,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def _write_briefs(briefs: Dict[Tuple[str, str], Dict], output_dir: str) -> None:
    """
    Write briefs to artifacts/marketing/briefs/{persona_id}/{topic_id}.json

    Args:
        briefs: Dict mapping (persona_id, topic_id) -> brief dict
        output_dir: Root output directory
    """
    briefs_path = Path(output_dir) / "marketing" / "briefs"
    briefs_path.mkdir(parents=True, exist_ok=True)

    for (persona_id, topic_id), brief in briefs.items():
        persona_dir = briefs_path / persona_id
        persona_dir.mkdir(parents=True, exist_ok=True)

        brief_file = persona_dir / f"{topic_id}.json"
        with open(brief_file, 'w') as f:
            json.dump(brief, f, indent=2)

        print(f"Wrote brief: {brief_file}")


def _identify_gaps(
    all_personas: List[str],
    all_topics: List[str],
    briefs_by_pair: Dict[Tuple[str, str], Dict],
) -> List[Tuple[str, str]]:
    """
    Identify (persona, topic) pairs with zero signals.

    Returns:
        List of (persona_id, topic_id) pairs with no signals
    """
    gaps = []
    for persona in all_personas:
        for topic in all_topics:
            if (persona, topic) not in briefs_by_pair:
                gaps.append((persona, topic))
    return gaps


def main():
    parser = argparse.ArgumentParser(
        description="Build persona × topic briefs from signal store"
    )
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="Run on pilot personas/topics (3 × 5 = 15 pairs)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run on all personas/topics (10 × 15 = 150 pairs)",
    )
    parser.add_argument(
        "--persona",
        type=str,
        help="Single persona_id to process",
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Single topic_id to process (requires --persona)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print briefs without writing to disk",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=".",
        help="Repository root path",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Determine persona and topic filters
    if args.persona and args.topic:
        personas = [args.persona]
        topics = [args.topic]
    elif args.persona:
        personas = [args.persona]
        topics = None  # All topics
    elif args.pilot:
        personas = PILOT_PERSONAS
        topics = PILOT_TOPICS
    elif args.all:
        personas = None  # Load from canonical_personas.yaml
        topics = None  # Load from canonical_topics.yaml
    else:
        parser.print_help()
        return 1

    # Load all personas/topics if using --all
    if personas is None:
        personas_file = Path(args.repo) / "canonical_personas.yaml"
        topics_file = Path(args.repo) / "canonical_topics.yaml"

        if not personas_file.exists() or not topics_file.exists():
            print("Error: canonical_personas.yaml or canonical_topics.yaml not found", file=sys.stderr)
            return 1

        personas_config = _load_yaml_config(str(personas_file))
        topics_config = _load_yaml_config(str(topics_file))

        personas = list(personas_config.keys()) if personas_config else []
        topics = list(topics_config.keys()) if topics_config else []

    if args.verbose:
        print(f"Personas: {personas}")
        print(f"Topics: {topics}")

    # Load freshness config
    config_path = Path(args.repo) / "config" / "quality" / "ei_v2_config.yaml"
    if config_path.exists():
        config = _load_yaml_config(str(config_path))
    else:
        config = {"research_max_age_days": 30, "sales_max_age_days": 7}

    if args.verbose:
        print(f"Config: {config}")

    # Load signals
    signal_dir = Path(args.repo) / "artifacts" / "marketing" / "signals"
    signals = _load_signals(
        str(signal_dir),
        persona_filter=personas if personas else None,
        topic_filter=topics if topics else None,
    )

    if args.verbose:
        print(f"Loaded {len(signals)} signals")

    # Apply freshness decay
    signals = _apply_freshness_decay(signals, config)

    # Group by persona × topic
    groups = _group_by_persona_topic(signals)

    # Build briefs
    briefs = {}
    all_targets = [(p, t) for p in (personas or []) for t in (topics or [])]

    for persona_id in (personas or []):
        for topic_id in (topics or []):
            signals_for_pair = groups.get((persona_id, topic_id), [])
            brief = _build_brief(persona_id, topic_id, signals_for_pair)
            briefs[(persona_id, topic_id)] = brief

    # Identify gaps
    gaps = _identify_gaps(personas or [], topics or [], briefs)

    # Output
    if args.dry_run:
        print("\n=== BRIEFS (DRY RUN) ===\n")
        for (persona, topic), brief in sorted(briefs.items()):
            print(f"{persona} × {topic}:")
            print(json.dumps(brief, indent=2))
            print()
    else:
        output_dir = Path(args.repo) / "artifacts"
        output_dir.mkdir(parents=True, exist_ok=True)
        _write_briefs(briefs, str(output_dir))

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Briefs generated: {len(briefs)}")
    print(f"Pairs with signals: {len([b for b in briefs.values() if b['signal_count'] > 0])}")
    print(f"Pairs with zero signals (gaps): {len(gaps)}")

    if gaps and args.verbose:
        print("\nGaps:")
        for persona, topic in gaps:
            print(f"  {persona} × {topic}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
