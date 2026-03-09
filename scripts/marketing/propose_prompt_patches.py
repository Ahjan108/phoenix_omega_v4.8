#!/usr/bin/env python3
"""
Experiment Agent — Prompt Patch Proposer

Reads persona/topic briefs + existing prompts, generates patch proposals.
Writes proposals to artifacts/marketing/patch_proposals.jsonl.

THIS SCRIPT HAS ZERO SIDE EFFECTS ON PRODUCTION FILES.
All patches are proposals only. promotion_gate.py is the sole apply path.

Exploration policy: 80% exploit (improve winning patterns), 20% explore (try new variants).

Usage:
  python3 scripts/marketing/propose_prompt_patches.py --from-briefs
  python3 scripts/marketing/propose_prompt_patches.py --dry-run
"""

import argparse
import json
import os
import sys
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import uuid4
from collections import defaultdict


DEFAULT_EXPLORATION_RATE = 0.2


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


def _load_briefs(brief_dir: str) -> Dict[Tuple[str, str], Dict]:
    """
    Load all brief JSON files from artifacts/marketing/briefs/.

    Returns:
        Dict mapping (persona_id, topic_id) -> brief dict
    """
    briefs = {}
    brief_path = Path(brief_dir)

    if not brief_path.exists():
        print(f"Warning: Brief directory does not exist: {brief_dir}", file=sys.stderr)
        return briefs

    for persona_dir in brief_path.iterdir():
        if not persona_dir.is_dir():
            continue

        persona_id = persona_dir.name

        for brief_file in persona_dir.glob("*.json"):
            topic_id = brief_file.stem

            try:
                with open(brief_file, 'r') as f:
                    brief = json.load(f)
                    briefs[(persona_id, topic_id)] = brief
            except (IOError, json.JSONDecodeError) as e:
                print(f"Warning: Could not read {brief_file}: {e}", file=sys.stderr)

    return briefs


def _load_existing_prompts(repo: str) -> Dict[str, str]:
    """
    Load existing marketing/content prompts from production or prompts directory.

    Returns:
        Dict mapping prompt_key -> prompt_text
    """
    prompts = {}

    # Check multiple locations
    prompt_locations = [
        Path(repo) / "prompts" / "marketing",
        Path(repo) / "config" / "prompts" / "marketing",
        Path(repo) / "marketing" / "prompts",
    ]

    for location in prompt_locations:
        if location.exists():
            for prompt_file in location.glob("*.txt") | location.glob("*.md"):
                prompt_key = prompt_file.stem
                try:
                    with open(prompt_file, 'r') as f:
                        prompts[prompt_key] = f.read()
                except IOError as e:
                    print(f"Warning: Could not read {prompt_file}: {e}", file=sys.stderr)

    # Fallback: create placeholder prompts if none found
    if not prompts:
        prompts = {
            "default_hook": "Engage with {persona} through their core anxieties.",
            "default_cta": "Take the first step: {action}",
            "default_framing": "This is about {topic} — and your path forward.",
        }

    return prompts


def _should_explore(exploration_rate: float = DEFAULT_EXPLORATION_RATE) -> bool:
    """
    Determine whether to generate an exploratory patch (vs. exploit).

    Args:
        exploration_rate: Probability of exploration (default 0.2 = 20%)

    Returns:
        True if should explore, False if should exploit
    """
    return random.random() < exploration_rate


def _load_exploration_policy(repo: str) -> float:
    """
    Load exploration rate from config/marketing/exploration_policy.yaml if exists.

    Returns:
        Exploration rate (0.0 to 1.0), defaults to DEFAULT_EXPLORATION_RATE
    """
    policy_file = Path(repo) / "config" / "marketing" / "exploration_policy.yaml"

    if policy_file.exists():
        try:
            config = _load_yaml_config(str(policy_file))
            if "exploration_rate" in config:
                rate_str = config.get("exploration_rate", str(DEFAULT_EXPLORATION_RATE))
                try:
                    return float(rate_str)
                except ValueError:
                    pass
        except Exception as e:
            print(f"Warning: Could not load exploration policy: {e}", file=sys.stderr)

    return DEFAULT_EXPLORATION_RATE


def _generate_exploit_patch(
    brief: Dict,
    prompt: str,
) -> Dict:
    """
    Propose improvements to proven patterns based on brief signals.

    Args:
        brief: Brief dict from artifacts/marketing/briefs/
        prompt: Current prompt text

    Returns:
        Patch dict with proposed changes
    """
    persona_id = brief.get("persona_id", "unknown")
    topic_id = brief.get("topic_id", "unknown")
    keywords = brief.get("trend_keywords", [])
    top_claims = brief.get("top_research_claims", [])
    sales_trend = brief.get("sales_trend_summary", "flat")

    # Build diff preview
    diff_parts = ["## Exploit Patch (Proven Pattern)"]

    # Suggestion 1: Incorporate top keywords
    if keywords:
        keyword_phrase = ", ".join(keywords[:3])
        diff_parts.append(f"\n+ Add keywords to hook: {keyword_phrase}")

    # Suggestion 2: Leverage sales trend
    if sales_trend == "up":
        diff_parts.append("\n+ Expand reach: increase ad spend or impressions")
    elif sales_trend == "down":
        diff_parts.append("\n+ Adjust messaging: pivot to pain points from research")

    # Suggestion 3: Strengthen claims
    if top_claims:
        claim_snippet = top_claims[0].get("claim", "")[:100]
        diff_parts.append(f"\n+ Reinforce with research: '{claim_snippet}...'")

    # Suggestion 4: Optimize CTA
    diff_parts.append("\n+ Refine CTA: test {persona}-specific call-to-action variant")

    diff_preview = "".join(diff_parts)

    # Confidence based on signal count and freshness
    signal_count = brief.get("signal_count", 0)
    freshness = brief.get("freshness_score", 0.0)
    confidence = min(0.95, (signal_count / 10.0) * freshness)

    return {
        "patch_type": "exploit",
        "confidence": round(confidence, 3),
        "diff_preview": diff_preview,
    }


def _generate_explore_patch(
    brief: Dict,
    prompt: str,
) -> Dict:
    """
    Propose experimental variant (new hook, CTA, framing).

    Args:
        brief: Brief dict from artifacts/marketing/briefs/
        prompt: Current prompt text

    Returns:
        Patch dict with proposed changes
    """
    persona_id = brief.get("persona_id", "unknown")
    topic_id = brief.get("topic_id", "unknown")
    keywords = brief.get("trend_keywords", [])
    outcomes = brief.get("content_outcome_summary", [])

    # Build diff preview with experimental ideas
    diff_parts = ["## Explore Patch (Experimental Variant)"]

    # Experimental idea 1: New angle on topic
    diff_parts.append(f"\n+ Test new framing: 'Your {topic_id} is solvable with [new_approach]'")

    # Experimental idea 2: Different CTA
    if persona_id:
        diff_parts.append(f"\n+ Try different CTA: 'As a {persona_id}, here's what works for you'")

    # Experimental idea 3: Novel hook
    if keywords:
        hook_keyword = keywords[0]
        diff_parts.append(f"\n+ New hook: Lead with '{hook_keyword}' as primary driver")

    # Experimental idea 4: Content variant
    diff_parts.append("\n+ Test longer-form vs. short-form content mix")

    diff_preview = "".join(diff_parts)

    # Lower confidence for exploratory patches
    risk_level = "medium"
    confidence = 0.5  # Exploratory = lower confidence, higher risk

    return {
        "patch_type": "explore",
        "confidence": confidence,
        "diff_preview": diff_preview,
        "risk_level": risk_level,
    }


def _build_proposal(
    patch_dict: Dict,
    persona_id: str,
    topic_id: str,
    target_file: str,
    brief_snapshot: Dict,
) -> Dict:
    """
    Create a proposal dict for a patch.

    Args:
        patch_dict: Dict with patch_type, confidence, diff_preview
        persona_id: Persona ID
        topic_id: Topic ID
        target_file: Target prompt file path
        brief_snapshot: Brief dict (for context)

    Returns:
        Proposal dict with proposal_id, timestamp, status, etc.
    """
    proposal_id = str(uuid4())
    patch_type = patch_dict.get("patch_type", "unknown")

    risk_level = patch_dict.get("risk_level", "low" if patch_type == "exploit" else "medium")

    return {
        "proposal_id": proposal_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "patch_type": patch_type,
        "persona_id": persona_id,
        "topic_id": topic_id,
        "target_file": target_file,
        "diff_preview": patch_dict.get("diff_preview", ""),
        "confidence": patch_dict.get("confidence", 0.5),
        "risk_level": risk_level,
        "brief_snapshot": brief_snapshot,
        "status": "proposed",
    }


def _write_proposals(proposals: List[Dict], output_path: str) -> None:
    """
    Append proposals to artifacts/marketing/patch_proposals.jsonl.

    Args:
        proposals: List of proposal dicts
        output_path: Path to patch_proposals.jsonl
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'a') as f:
        for proposal in proposals:
            f.write(json.dumps(proposal) + "\n")

    print(f"Wrote {len(proposals)} proposals to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate prompt patch proposals from persona/topic briefs"
    )
    parser.add_argument(
        "--from-briefs",
        action="store_true",
        help="Generate proposals from briefs (main mode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print proposals without writing to disk",
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

    if not args.from_briefs and not args.dry_run:
        parser.print_help()
        return 1

    repo_path = Path(args.repo)

    # Load exploration policy
    exploration_rate = _load_exploration_policy(args.repo)
    if args.verbose:
        print(f"Exploration rate: {exploration_rate:.1%}")

    # Load briefs
    brief_dir = repo_path / "artifacts" / "marketing" / "briefs"
    briefs = _load_briefs(str(brief_dir))

    if args.verbose:
        print(f"Loaded {len(briefs)} briefs")

    if not briefs:
        print("Warning: No briefs found. Run build_persona_topic_briefs.py first.", file=sys.stderr)
        return 0

    # Load existing prompts
    prompts = _load_existing_prompts(args.repo)

    if args.verbose:
        print(f"Loaded {len(prompts)} existing prompts")

    # Generate proposals
    proposals = []
    proposal_stats = defaultdict(int)

    for (persona_id, topic_id), brief in sorted(briefs.items()):
        if brief.get("signal_count", 0) == 0:
            if args.verbose:
                print(f"Skipping {persona_id} × {topic_id}: no signals")
            continue

        # Select a prompt to target (or use default)
        target_prompt_key = f"{persona_id}_{topic_id}" if f"{persona_id}_{topic_id}" in prompts else "default_hook"
        target_prompt = prompts.get(target_prompt_key, "")
        target_file = f"prompts/marketing/{target_prompt_key}.txt"

        # Decide: exploit or explore
        should_exp = _should_explore(exploration_rate)

        if should_exp:
            patch = _generate_explore_patch(brief, target_prompt)
            proposal_stats["explore"] += 1
        else:
            patch = _generate_exploit_patch(brief, target_prompt)
            proposal_stats["exploit"] += 1

        # Build proposal
        proposal = _build_proposal(
            patch,
            persona_id,
            topic_id,
            target_file,
            {
                "persona_id": brief.get("persona_id"),
                "topic_id": brief.get("topic_id"),
                "signal_count": brief.get("signal_count"),
                "avg_confidence": brief.get("avg_confidence"),
                "freshness_score": brief.get("freshness_score"),
            },
        )

        proposals.append(proposal)

        if args.verbose:
            print(f"Proposed {patch.get('patch_type')} patch for {persona_id} × {topic_id}")

    # Output
    if args.dry_run:
        print("\n=== PROPOSALS (DRY RUN) ===\n")
        for proposal in proposals:
            print(json.dumps(proposal, indent=2))
            print()
    else:
        output_path = repo_path / "artifacts" / "marketing" / "patch_proposals.jsonl"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_proposals(proposals, str(output_path))

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Proposals generated: {len(proposals)}")
    print(f"  Exploit (80%): {proposal_stats['exploit']}")
    print(f"  Explore (20%): {proposal_stats['explore']}")
    print(f"\nAll proposals written to artifacts/marketing/patch_proposals.jsonl")
    print(f"promotion_gate.py will apply approved proposals.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
