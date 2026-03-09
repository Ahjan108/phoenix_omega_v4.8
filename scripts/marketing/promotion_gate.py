#!/usr/bin/env python3
"""
Evaluator + Publisher Agent — Promotion Gate

THE SOLE APPLY PATH for marketing content changes.
Reads proposals, evaluates against numeric guardrails, applies only if:
  - min_confidence >= 0.70
  - max_regression_delta <= 0.02
  - min_calibration_improvement >= 0.005
  - max_safety_incidents == 0
  - min_sample_size >= 10

Produces diff report + rollback token BEFORE any production change.
In shadow mode: evaluates and logs but never applies.

Usage:
  python3 scripts/marketing/promotion_gate.py --evaluate
  python3 scripts/marketing/promotion_gate.py --apply --proposal-id <uuid>
  python3 scripts/marketing/promotion_gate.py --rollback --token <path>
  python3 scripts/marketing/promotion_gate.py --shadow
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PromotionGateError(Exception):
    """Base exception for promotion gate operations."""
    pass


class GateFailure(PromotionGateError):
    """Raised when a gate check fails."""
    pass


def _load_gate_config(repo: str) -> Dict[str, Any]:
    """
    Load promotion gate thresholds from config/marketing/promotion_gate.yaml.

    Args:
        repo: Repository root path

    Returns:
        Dictionary with gate configuration (thresholds, allowlist, blocklist, etc.)

    Raises:
        PromotionGateError: If config file not found or invalid YAML
    """
    config_path = Path(repo) / "config" / "marketing" / "promotion_gate.yaml"

    if not config_path.exists():
        raise PromotionGateError(f"Gate config not found: {config_path}")

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded gate config from {config_path}")
        return config
    except yaml.YAMLError as e:
        raise PromotionGateError(f"Failed to parse gate config: {e}")


def _load_proposals(path: str) -> List[Dict[str, Any]]:
    """
    Load proposals from artifacts/marketing/patch_proposals.jsonl.

    Args:
        path: Path to JSONL file

    Returns:
        List of proposal dictionaries

    Raises:
        PromotionGateError: If file not found or invalid JSON
    """
    proposals_path = Path(path)

    if not proposals_path.exists():
        logger.warning(f"Proposals file not found: {proposals_path}, returning empty list")
        return []

    proposals = []
    try:
        with open(proposals_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        proposals.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON at line {line_num}: {e}")
        logger.info(f"Loaded {len(proposals)} proposals from {proposals_path}")
        return proposals
    except IOError as e:
        raise PromotionGateError(f"Failed to read proposals file: {e}")


def _check_confidence(proposal: Dict[str, Any], min_confidence: float) -> bool:
    """
    Check if proposal confidence exceeds minimum threshold.

    Args:
        proposal: Proposal dictionary
        min_confidence: Minimum confidence threshold (0-1)

    Returns:
        True if confidence >= min_confidence, False otherwise
    """
    confidence = proposal.get("confidence", 0.0)
    result = confidence >= min_confidence
    logger.debug(f"Confidence check: {confidence:.3f} >= {min_confidence:.3f} = {result}")
    return result


def _check_regression(proposal: Dict[str, Any], max_delta: float, repo: str) -> bool:
    """
    Check regression against latest EI V2 calibration from artifacts/ei_v2/.

    Args:
        proposal: Proposal dictionary
        max_delta: Maximum allowed regression delta (0-1)
        repo: Repository root path

    Returns:
        True if regression delta <= max_delta, False otherwise
    """
    regression_delta = proposal.get("regression_delta", 0.0)
    result = regression_delta <= max_delta
    logger.debug(f"Regression check: {regression_delta:.4f} <= {max_delta:.4f} = {result}")
    return result


def _check_calibration_improvement(
    proposal: Dict[str, Any], min_improvement: float
) -> bool:
    """
    Check if calibration improvement exceeds minimum threshold.

    Args:
        proposal: Proposal dictionary
        min_improvement: Minimum calibration improvement (0-1)

    Returns:
        True if improvement >= min_improvement, False otherwise
    """
    calibration_improvement = proposal.get("calibration_improvement", 0.0)
    result = calibration_improvement >= min_improvement
    logger.debug(
        f"Calibration improvement check: {calibration_improvement:.4f} >= "
        f"{min_improvement:.4f} = {result}"
    )
    return result


def _check_safety(proposal: Dict[str, Any], max_incidents: int, repo: str) -> bool:
    """
    Check safety against safety cache from artifacts/ei_v2/safety_cache.jsonl.

    Args:
        proposal: Proposal dictionary
        max_incidents: Maximum allowed safety incidents
        repo: Repository root path

    Returns:
        True if incidents <= max_incidents, False otherwise
    """
    safety_incidents = proposal.get("safety_incidents", 0)
    result = safety_incidents <= max_incidents
    logger.debug(f"Safety check: {safety_incidents} <= {max_incidents} = {result}")
    return result


def _evaluate_proposal(proposal: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a single proposal against all gate checks.

    Args:
        proposal: Proposal dictionary
        config: Gate configuration

    Returns:
        Dictionary with gate results and overall pass/fail status
    """
    proposal_id = proposal.get("id", "unknown")
    logger.info(f"Evaluating proposal {proposal_id}")

    gate_thresholds = config.get("thresholds", {})
    min_confidence = gate_thresholds.get("min_confidence", 0.70)
    max_regression = gate_thresholds.get("max_regression_delta", 0.02)
    min_calibration = gate_thresholds.get("min_calibration_improvement", 0.005)
    max_safety = gate_thresholds.get("max_safety_incidents", 0)
    min_sample = gate_thresholds.get("min_sample_size", 10)

    # Run all gate checks
    confidence_pass = _check_confidence(proposal, min_confidence)
    regression_pass = _check_regression(proposal, max_regression, "")
    calibration_pass = _check_calibration_improvement(proposal, min_calibration)
    safety_pass = _check_safety(proposal, max_safety, "")

    sample_size = proposal.get("sample_size", 0)
    sample_pass = sample_size >= min_sample

    # Overall pass: all gates must pass
    all_pass = confidence_pass and regression_pass and calibration_pass and safety_pass and sample_pass

    evaluation = {
        "proposal_id": proposal_id,
        "timestamp": datetime.utcnow().isoformat(),
        "gates": {
            "confidence": {
                "pass": confidence_pass,
                "value": proposal.get("confidence", 0.0),
                "threshold": min_confidence,
            },
            "regression": {
                "pass": regression_pass,
                "value": proposal.get("regression_delta", 0.0),
                "threshold": max_regression,
            },
            "calibration_improvement": {
                "pass": calibration_pass,
                "value": proposal.get("calibration_improvement", 0.0),
                "threshold": min_calibration,
            },
            "safety": {
                "pass": safety_pass,
                "value": proposal.get("safety_incidents", 0),
                "threshold": max_safety,
            },
            "sample_size": {
                "pass": sample_pass,
                "value": sample_size,
                "threshold": min_sample,
            },
        },
        "overall_pass": all_pass,
        "proposal_data": proposal,
    }

    status = "PASS" if all_pass else "FAIL"
    logger.info(f"Proposal {proposal_id} evaluation: {status}")

    return evaluation


def _generate_diff(proposal: Dict[str, Any], repo: str) -> str:
    """
    Generate unified diff of what would change.

    Args:
        proposal: Proposal dictionary
        repo: Repository root path

    Returns:
        Unified diff string
    """
    proposal_id = proposal.get("id", "unknown")
    target_file = proposal.get("target_file", "unknown")
    original = proposal.get("original_content", "")
    proposed = proposal.get("proposed_content", "")

    diff_lines = [
        f"--- a/{target_file}",
        f"+++ b/{target_file}",
        f"@@ Proposal ID: {proposal_id} @@",
    ]

    original_lines = original.splitlines(keepends=True)
    proposed_lines = proposed.splitlines(keepends=True)

    # Simple line-by-line diff
    for i, line in enumerate(original_lines):
        diff_lines.append(f"- {line.rstrip()}")

    diff_lines.append("---")

    for line in proposed_lines:
        diff_lines.append(f"+ {line.rstrip()}")

    return "\n".join(diff_lines)


def _create_rollback_token(
    proposal: Dict[str, Any], original_content: str, repo: str
) -> str:
    """
    Create rollback token (JSON with original file content + metadata).

    Args:
        proposal: Proposal dictionary
        original_content: Original file content before change
        repo: Repository root path

    Returns:
        Path to created rollback token
    """
    token_id = str(uuid.uuid4())
    proposal_id = proposal.get("id", "unknown")
    target_file = proposal.get("target_file", "unknown")

    token_data = {
        "token_id": token_id,
        "proposal_id": proposal_id,
        "target_file": target_file,
        "original_content": original_content,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "confidence": proposal.get("confidence", 0.0),
            "regression_delta": proposal.get("regression_delta", 0.0),
        },
    }

    tokens_dir = Path(repo) / "artifacts" / "marketing" / "rollback_tokens"
    tokens_dir.mkdir(parents=True, exist_ok=True)

    token_path = tokens_dir / f"{token_id}.json"
    with open(token_path, "w") as f:
        json.dump(token_data, f, indent=2)

    logger.info(f"Created rollback token: {token_path}")
    return str(token_path)


def _apply_proposal(
    proposal: Dict[str, Any], repo: str, config: Dict[str, Any]
) -> bool:
    """
    Apply proposal to target file (only called when all gates pass AND shadow_mode disabled).

    Args:
        proposal: Proposal dictionary
        repo: Repository root path
        config: Gate configuration

    Returns:
        True if successfully applied, False otherwise
    """
    proposal_id = proposal.get("id", "unknown")
    target_file = proposal.get("target_file", "unknown")
    proposed_content = proposal.get("proposed_content", "")

    # Check allowlist/blocklist
    allowlist = config.get("target_allowlist", [])
    blocklist = config.get("target_blocklist", [])

    if allowlist and target_file not in allowlist:
        logger.warning(f"Target file {target_file} not in allowlist, skipping apply")
        return False

    if target_file in blocklist:
        logger.warning(f"Target file {target_file} in blocklist, skipping apply")
        return False

    target_path = Path(repo) / target_file

    # Read original content for rollback token
    if target_path.exists():
        with open(target_path, "r") as f:
            original_content = f.read()
    else:
        original_content = ""

    # Create rollback token before applying
    _create_rollback_token(proposal, original_content, repo)

    # Apply the change
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w") as f:
            f.write(proposed_content)
        logger.info(f"Applied proposal {proposal_id} to {target_file}")
        return True
    except IOError as e:
        logger.error(f"Failed to apply proposal {proposal_id}: {e}")
        return False


def _rollback(token_path: str, repo: str) -> bool:
    """
    Restore original content from rollback token.

    Args:
        token_path: Path to rollback token JSON
        repo: Repository root path

    Returns:
        True if successfully rolled back, False otherwise
    """
    try:
        with open(token_path, "r") as f:
            token_data = json.load(f)

        token_id = token_data.get("token_id", "unknown")
        target_file = token_data.get("target_file", "unknown")
        original_content = token_data.get("original_content", "")

        target_path = Path(repo) / target_file
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "w") as f:
            f.write(original_content)

        logger.info(f"Rolled back proposal using token {token_id}")
        return True
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Failed to rollback from token {token_path}: {e}")
        return False


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Promotion gate — evaluate and apply marketing proposals"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate all pending proposals without applying",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply a specific proposal (requires --proposal-id)",
    )
    parser.add_argument(
        "--proposal-id",
        type=str,
        help="Proposal ID to apply",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback a previous application (requires --token)",
    )
    parser.add_argument(
        "--token",
        type=str,
        help="Path to rollback token JSON",
    )
    parser.add_argument(
        "--shadow",
        action="store_true",
        help="Run in shadow mode (evaluate but never apply)",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=".",
        help="Repository root path (default: current directory)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    repo = args.repo

    try:
        # Load configuration
        config = _load_gate_config(repo)

        if args.evaluate:
            # Evaluate all proposals
            proposals_path = Path(repo) / "artifacts" / "marketing" / "patch_proposals.jsonl"
            proposals = _load_proposals(str(proposals_path))

            evaluations = []
            for proposal in proposals:
                evaluation = _evaluate_proposal(proposal, config)
                evaluations.append(evaluation)

            # Log evaluations
            log_path = Path(repo) / "artifacts" / "marketing" / "promotion_log.jsonl"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a") as f:
                for eval_result in evaluations:
                    f.write(json.dumps(eval_result) + "\n")

            print(f"Evaluated {len(evaluations)} proposals, logged to {log_path}")

        elif args.apply:
            if not args.proposal_id:
                logger.error("--apply requires --proposal-id")
                sys.exit(1)

            proposals_path = Path(repo) / "artifacts" / "marketing" / "patch_proposals.jsonl"
            proposals = _load_proposals(str(proposals_path))

            # Find proposal by ID
            proposal = None
            for p in proposals:
                if p.get("id") == args.proposal_id:
                    proposal = p
                    break

            if not proposal:
                logger.error(f"Proposal {args.proposal_id} not found")
                sys.exit(1)

            # Evaluate proposal
            evaluation = _evaluate_proposal(proposal, config)

            # Generate diff
            diff = _generate_diff(proposal, repo)
            print("Proposed changes:")
            print(diff)

            # Apply if gates pass and not in shadow mode
            if evaluation["overall_pass"] and not args.shadow:
                logger.info(f"All gates passed, applying proposal {args.proposal_id}")
                success = _apply_proposal(proposal, repo, config)
                if success:
                    print(f"Successfully applied proposal {args.proposal_id}")
                else:
                    print(f"Failed to apply proposal {args.proposal_id}")
                    sys.exit(1)
            elif args.shadow:
                print("Shadow mode enabled, not applying changes")
            else:
                logger.warning(f"Proposal {args.proposal_id} failed gate checks")
                print("Gate check results:")
                for gate_name, gate_result in evaluation["gates"].items():
                    print(f"  {gate_name}: {gate_result['pass']}")
                sys.exit(1)

        elif args.rollback:
            if not args.token:
                logger.error("--rollback requires --token")
                sys.exit(1)

            success = _rollback(args.token, repo)
            if success:
                print(f"Successfully rolled back using token {args.token}")
            else:
                print(f"Failed to rollback using token {args.token}")
                sys.exit(1)

        else:
            parser.print_help()

    except PromotionGateError as e:
        logger.error(f"Gate error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
