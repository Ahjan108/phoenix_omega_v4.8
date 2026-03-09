#!/usr/bin/env python3
"""
EI V2 — Research + Sales Feature Hook

Loads signals from unified signal store, computes features:
  - research_strength: quality/quantity of research for this persona/topic
  - sales_conv_signal: sales conversion trend (positive/negative/neutral)
  - trend_alignment: how well content aligns with current trends

Integrates with EI V2 via config gate:
  research_sales.enabled: true/false (in ei_v2_config.yaml)
  Fail-open: if signals unavailable, return neutral scores (no crash).

Shadow mode: when research_sales.shadow: true, features are computed
and logged but not included in composite score.
"""

import json
import logging
import os
from collections import namedtuple
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Neutral features for fail-open behavior
ResearchSalesFeatures = namedtuple(
    "ResearchSalesFeatures",
    [
        "research_strength",      # float 0-1: quality/quantity of research
        "sales_conv_signal",      # float -1 to 1: sales conversion trend
        "trend_alignment",        # float 0-1: alignment with trends
        "signal_count",           # int: number of signals used
        "loaded_from_store",      # bool: whether signals were successfully loaded
        "shadow",                 # bool: whether in shadow mode
    ],
)

NEUTRAL_FEATURES = ResearchSalesFeatures(
    research_strength=0.5,
    sales_conv_signal=0.0,
    trend_alignment=0.5,
    signal_count=0,
    loaded_from_store=False,
    shadow=False,
)


class ResearchSalesError(Exception):
    """Base exception for research sales features."""
    pass


def _load_signals_for_pair(
    signal_dir: str,
    persona_id: Optional[str] = None,
    topic_id: Optional[str] = None,
    max_age_days: int = 30,
) -> List[Dict[str, Any]]:
    """
    Load signals from JSONL file, filter by persona/topic, apply freshness.

    Args:
        signal_dir: Directory containing signal JSONL files
        persona_id: Filter by persona ID (optional)
        topic_id: Filter by topic ID (optional)
        max_age_days: Maximum age of signals in days (default: 30)

    Returns:
        List of signal dictionaries matching filters
    """
    signals = []
    signal_path = Path(signal_dir) / "signals.jsonl"

    if not signal_path.exists():
        logger.warning(f"Signal file not found: {signal_path}")
        return signals

    cutoff_time = datetime.utcnow() - timedelta(days=max_age_days)

    try:
        with open(signal_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    signal = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON at line {line_num} in {signal_path}: {e}")
                    continue

                # Apply persona filter
                if persona_id and signal.get("persona_id") != persona_id:
                    continue

                # Apply topic filter
                if topic_id and signal.get("topic_id") != topic_id:
                    continue

                # Apply freshness filter
                try:
                    signal_time = datetime.fromisoformat(signal.get("timestamp", ""))
                    if signal_time < cutoff_time:
                        continue
                except (ValueError, TypeError):
                    logger.warning(f"Invalid timestamp in signal at line {line_num}")
                    continue

                signals.append(signal)

        logger.debug(f"Loaded {len(signals)} signals from {signal_path}")
        return signals

    except IOError as e:
        logger.warning(f"Failed to read signal file {signal_path}: {e}")
        return signals


def _compute_research_strength(signals: List[Dict[str, Any]]) -> float:
    """
    Compute research strength as ratio of high-confidence signals, weighted by freshness.

    Args:
        signals: List of signal dictionaries

    Returns:
        Float between 0 and 1 representing research strength
    """
    if not signals:
        return 0.5  # Neutral default

    now = datetime.utcnow()
    total_weighted_strength = 0.0
    total_weight = 0.0

    for signal in signals:
        # Extract confidence (0-1)
        confidence = signal.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            confidence = 0.5

        # Extract timestamp for freshness weighting
        try:
            signal_time = datetime.fromisoformat(signal.get("timestamp", ""))
            age_days = (now - signal_time).days
            # Linear decay: full weight at 0 days, half weight at 30 days
            freshness_weight = max(0.5, 1.0 - (age_days / 60.0))
        except (ValueError, TypeError):
            freshness_weight = 0.5

        weighted_strength = confidence * freshness_weight
        total_weighted_strength += weighted_strength
        total_weight += freshness_weight

    # Normalize by total weight
    if total_weight > 0:
        strength = min(1.0, total_weighted_strength / total_weight)
    else:
        strength = 0.5

    logger.debug(f"Computed research strength: {strength:.3f} from {len(signals)} signals")
    return strength


def _compute_sales_signal(signals: List[Dict[str, Any]]) -> float:
    """
    Aggregate sales trend: positive values = converting well, negative = not converting.

    Args:
        signals: List of signal dictionaries with sales data

    Returns:
        Float between -1 and 1 representing sales conversion trend
    """
    if not signals:
        return 0.0  # Neutral default

    sales_signals = []

    for signal in signals:
        signal_type = signal.get("type", "")

        # Look for sales-related signals
        if signal_type == "conversion":
            trend = signal.get("trend", 0.0)
            if isinstance(trend, (int, float)):
                sales_signals.append(trend)
        elif signal_type == "engagement":
            # Engagement can indicate sales potential
            value = signal.get("value", 0.0)
            if isinstance(value, (int, float)):
                # Convert engagement score to sales signal (-1 to 1)
                sales_signals.append((value - 0.5) * 2.0)

    if not sales_signals:
        return 0.0

    # Average all sales signals and clamp to [-1, 1]
    avg_signal = sum(sales_signals) / len(sales_signals)
    result = max(-1.0, min(1.0, avg_signal))

    logger.debug(f"Computed sales signal: {result:.3f} from {len(sales_signals)} sales signals")
    return result


def _compute_trend_alignment(signals: List[Dict[str, Any]], content_text: Optional[str]) -> float:
    """
    Compute keyword overlap between trend signals and content.

    Args:
        signals: List of signal dictionaries containing trend data
        content_text: Content text to match against trends

    Returns:
        Float between 0 and 1 representing trend alignment
    """
    if not signals or not content_text:
        return 0.5  # Neutral default

    # Extract all keywords from trend signals
    trend_keywords = set()
    for signal in signals:
        keywords = signal.get("keywords", [])
        if isinstance(keywords, list):
            trend_keywords.update(keywords)

    if not trend_keywords:
        return 0.5

    # Count matches in content
    content_lower = content_text.lower()
    matched_keywords = 0

    for keyword in trend_keywords:
        if isinstance(keyword, str) and keyword.lower() in content_lower:
            matched_keywords += 1

    # Calculate alignment as ratio of matched keywords
    alignment = matched_keywords / len(trend_keywords) if trend_keywords else 0.5
    alignment = max(0.0, min(1.0, alignment))

    logger.debug(f"Computed trend alignment: {alignment:.3f} ({matched_keywords}/{len(trend_keywords)} keywords)")
    return alignment


def get_research_sales_features(
    config: Dict[str, Any],
    repo_root: str,
    persona_id: Optional[str] = None,
    topic_id: Optional[str] = None,
    content_text: Optional[str] = None,
) -> ResearchSalesFeatures:
    """
    Get research and sales features for EI V2 scoring.

    Integrates with EI V2 config gate:
      research_sales.enabled: true/false
      research_sales.shadow: true/false
      research_sales.signal_dir: path to signals

    If not enabled: returns neutral features.
    If signal store empty: returns neutral features with loaded_from_store=False.
    Respects freshness windows (research 30d, sales 7d).
    Fail-open: never crashes, always returns valid ResearchSalesFeatures.

    Args:
        config: EI V2 configuration dictionary
        repo_root: Repository root path
        persona_id: Persona ID for signal filtering (optional)
        topic_id: Topic ID for signal filtering (optional)
        content_text: Content text for trend alignment (optional)

    Returns:
        ResearchSalesFeatures namedtuple with all feature values
    """
    try:
        # Check if feature is enabled in config
        research_sales_config = config.get("research_sales", {})
        if not research_sales_config.get("enabled", False):
            logger.debug("Research-sales features disabled in config")
            return NEUTRAL_FEATURES

        # Check shadow mode
        shadow_mode = research_sales_config.get("shadow", False)

        # Get signal directory
        signal_dir = research_sales_config.get("signal_dir", "artifacts/ei_v2/signals")
        full_signal_dir = Path(repo_root) / signal_dir

        if not full_signal_dir.exists():
            logger.warning(f"Signal directory not found: {full_signal_dir}")
            return ResearchSalesFeatures(
                research_strength=0.5,
                sales_conv_signal=0.0,
                trend_alignment=0.5,
                signal_count=0,
                loaded_from_store=False,
                shadow=shadow_mode,
            )

        # Load signals with different freshness windows
        research_signals = _load_signals_for_pair(
            str(full_signal_dir),
            persona_id=persona_id,
            topic_id=topic_id,
            max_age_days=30,  # Research signals: 30 days
        )

        sales_signals = _load_signals_for_pair(
            str(full_signal_dir),
            persona_id=persona_id,
            topic_id=topic_id,
            max_age_days=7,  # Sales signals: 7 days
        )

        if not research_signals and not sales_signals:
            logger.warning("No signals loaded for persona/topic pair")
            return ResearchSalesFeatures(
                research_strength=0.5,
                sales_conv_signal=0.0,
                trend_alignment=0.5,
                signal_count=0,
                loaded_from_store=False,
                shadow=shadow_mode,
            )

        # Compute features
        research_strength = _compute_research_strength(research_signals)
        sales_conv_signal = _compute_sales_signal(sales_signals)
        trend_alignment = _compute_trend_alignment(research_signals + sales_signals, content_text)

        total_signal_count = len(research_signals) + len(sales_signals)

        features = ResearchSalesFeatures(
            research_strength=research_strength,
            sales_conv_signal=sales_conv_signal,
            trend_alignment=trend_alignment,
            signal_count=total_signal_count,
            loaded_from_store=True,
            shadow=shadow_mode,
        )

        logger.info(
            f"Computed research-sales features: "
            f"strength={research_strength:.3f}, sales={sales_conv_signal:.3f}, "
            f"trend={trend_alignment:.3f}, signals={total_signal_count}, shadow={shadow_mode}"
        )

        return features

    except Exception as e:
        logger.error(f"Error computing research-sales features: {e}", exc_info=True)
        # Fail-open: return neutral features on any error
        return ResearchSalesFeatures(
            research_strength=0.5,
            sales_conv_signal=0.0,
            trend_alignment=0.5,
            signal_count=0,
            loaded_from_store=False,
            shadow=False,
        )


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 research_sales_features.py <config.yaml> [persona_id] [topic_id]")
        sys.exit(1)

    config_path = sys.argv[1]
    persona_id = sys.argv[2] if len(sys.argv) > 2 else None
    topic_id = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        with open(config_path, "r") as f:
            import yaml
            config = yaml.safe_load(f)

        repo_root = Path(config_path).parent.parent.parent

        features = get_research_sales_features(
            config,
            str(repo_root),
            persona_id=persona_id,
            topic_id=topic_id,
        )

        print(f"Research-Sales Features:")
        print(f"  Research Strength: {features.research_strength:.3f}")
        print(f"  Sales Conv Signal: {features.sales_conv_signal:.3f}")
        print(f"  Trend Alignment: {features.trend_alignment:.3f}")
        print(f"  Signal Count: {features.signal_count}")
        print(f"  Loaded From Store: {features.loaded_from_store}")
        print(f"  Shadow Mode: {features.shadow}")

    except Exception as e:
        logger.error(f"Failed to load and process config: {e}")
        sys.exit(1)
