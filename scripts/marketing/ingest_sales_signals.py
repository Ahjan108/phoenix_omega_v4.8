#!/usr/bin/env python3
"""
Market Loop Agent — Sales Signal Ingestion

Reads sales/conversion/retention data from configured path (CSV or JSONL),
normalizes to unified signal schema, validates canonical IDs.

Sales signals older than 7 days MUST NOT drive promotion decisions.

Usage:
  python3 scripts/marketing/ingest_sales_signals.py --input path/to/sales.csv
  python3 scripts/marketing/ingest_sales_signals.py --input path/to/sales.jsonl
  python3 scripts/marketing/ingest_sales_signals.py --dry-run
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _load_canonical_ids(repo: Path) -> Tuple[Set[str], Set[str]]:
    """
    Load canonical personas and topics from YAML config.

    Returns:
        Tuple of (canonical_personas, canonical_topics) as sets of IDs
    """
    personas_path = repo / "config" / "catalog_planning" / "canonical_personas.yaml"
    topics_path = repo / "config" / "catalog_planning" / "canonical_topics.yaml"

    personas = set()
    topics = set()

    if personas_path.exists():
        with open(personas_path) as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict):
                raw = data.get("personas", [])
                for item in raw:
                    if isinstance(item, str):
                        personas.add(item)
                    elif isinstance(item, dict) and "id" in item:
                        personas.add(item["id"])

    if topics_path.exists():
        with open(topics_path) as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict):
                raw = data.get("topics", [])
                for item in raw:
                    if isinstance(item, str):
                        topics.add(item)
                    elif isinstance(item, dict) and "id" in item:
                        topics.add(item["id"])

    logger.info(f"Loaded {len(personas)} canonical personas, {len(topics)} canonical topics")
    return personas, topics


def _read_csv(path: Path) -> List[Dict[str, Any]]:
    """
    Read CSV file with expected columns: date, persona_id, topic_id, metric_name, metric_value, source

    Args:
        path: Path to CSV file

    Returns:
        List of record dicts
    """
    records = []

    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                logger.error(f"CSV file {path} has no headers")
                return records

            for row in reader:
                records.append(dict(row))

        logger.info(f"Read {len(records)} records from {path}")
    except Exception as e:
        logger.error(f"Error reading CSV {path}: {e}")
        sys.exit(1)

    return records


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """
    Read JSONL file with signal schema fields.

    Args:
        path: Path to JSONL file

    Returns:
        List of record dicts
    """
    records = []

    try:
        with open(path) as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON at line {line_num}: {e}")

        logger.info(f"Read {len(records)} records from {path}")
    except Exception as e:
        logger.error(f"Error reading JSONL {path}: {e}")
        sys.exit(1)

    return records


def _normalize_to_signal(
    record: Dict[str, Any],
    canonical_personas: Set[str],
    canonical_topics: Set[str]
) -> Optional[Dict[str, Any]]:
    """
    Convert CSV/JSONL record to unified signal schema.

    Determines signal_type based on metric_name.

    Args:
        record: Raw record from CSV or JSONL
        canonical_personas: Set of valid persona IDs
        canonical_topics: Set of valid topic IDs

    Returns:
        Signal dict or None if record cannot be normalized
    """
    # Handle both CSV and JSONL record formats
    persona_id = record.get("persona_id")
    topic_id = record.get("topic_id")
    date_str = record.get("date") or record.get("timestamp_utc")
    metric_name = record.get("metric_name")
    metric_value = record.get("metric_value")
    source = record.get("source", "sales_system")

    # Validate required fields
    if not all([persona_id, topic_id, date_str, metric_name, metric_value]):
        logger.debug(f"Missing required fields in record: {record}")
        return None

    # Validate canonical IDs
    if persona_id not in canonical_personas:
        logger.debug(f"Unknown persona_id: {persona_id}")
        return None

    if topic_id not in canonical_topics:
        logger.debug(f"Unknown topic_id: {topic_id}")
        return None

    # Parse timestamp
    try:
        if isinstance(date_str, str):
            # Try ISO format first
            if "T" in date_str:
                timestamp = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                # Try YYYY-MM-DD format
                timestamp = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            timestamp = date_str if isinstance(date_str, datetime) else datetime.now(timezone.utc)
    except ValueError as e:
        logger.debug(f"Could not parse timestamp {date_str}: {e}")
        return None

    # Determine signal type based on metric name
    metric_lower = metric_name.lower()
    if any(x in metric_lower for x in ["conversion", "sale", "purchase"]):
        signal_type = "sales_conversion"
    elif any(x in metric_lower for x in ["retention", "churn", "repeat"]):
        signal_type = "retention_signal"
    else:
        signal_type = "sales_metric"

    # Convert metric_value to float
    try:
        metric_float = float(metric_value)
    except (ValueError, TypeError):
        logger.debug(f"Could not convert metric_value to float: {metric_value}")
        return None

    signal = {
        "source": source,
        "timestamp_utc": timestamp.isoformat(),
        "persona_id": persona_id,
        "topic_id": topic_id,
        "signal_type": signal_type,
        "confidence": 0.95,  # Sales data is typically reliable
        "freshness_ts": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "run_id": str(uuid4()),
            "feed_url": None,
            "model": "sales_system_v1"
        },
        "payload": {
            "metric_name": metric_name,
            "metric_value": metric_float
        }
    }

    return signal


def _enforce_freshness(signal: Dict[str, Any], max_age_days: int = 7) -> None:
    """
    Mark stale signals and adjust confidence.

    Sales signals older than 7 days should NOT drive promotion decisions.

    Modifies signal in place.

    Args:
        signal: Signal dict with timestamp_utc
        max_age_days: Maximum age before marking as stale
    """
    if "timestamp_utc" not in signal:
        return

    try:
        signal_time = datetime.fromisoformat(signal["timestamp_utc"].replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - signal_time).days

        if age_days > max_age_days:
            signal["confidence"] = 0.0
            signal["stale"] = True
            signal["days_old"] = age_days
            logger.debug(f"Marked signal as stale ({age_days} days old)")
    except (ValueError, AttributeError) as e:
        logger.warning(f"Could not enforce freshness: {e}")


def _write_signals(signals: List[Dict[str, Any]], output_dir: Path) -> None:
    """
    Write signals to JSONL file, appending to existing data.

    Args:
        signals: List of signal dicts
        output_dir: Output directory path
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_file = output_dir / f"sales_signals_{today}.jsonl"

    with open(output_file, "a") as f:
        for signal in signals:
            f.write(json.dumps(signal) + "\n")

    logger.info(f"Wrote {len(signals)} signals to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Market Loop Agent — Sales Signal Ingestion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--input", type=Path, required=True,
        help="Path to sales data (CSV or JSONL)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse and validate but do not write"
    )
    parser.add_argument(
        "--repo", type=Path, default=Path.cwd(),
        help="Repository root path"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate input file
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    repo = args.repo

    # Load canonical IDs
    canonical_personas, canonical_topics = _load_canonical_ids(repo)

    if not canonical_personas or not canonical_topics:
        logger.error("No canonical IDs loaded. Aborting.")
        sys.exit(1)

    # Read input file based on extension
    if args.input.suffix.lower() == ".csv":
        records = _read_csv(args.input)
    elif args.input.suffix.lower() == ".jsonl":
        records = _read_jsonl(args.input)
    else:
        logger.error(f"Unsupported file format: {args.input.suffix}")
        sys.exit(1)

    if not records:
        logger.warning("No records read from input file")
        return

    # Normalize and validate signals
    valid_signals = []
    stale_signals = []
    rejected_count = 0

    for record in records:
        signal = _normalize_to_signal(record, canonical_personas, canonical_topics)

        if signal is None:
            rejected_count += 1
            continue

        # Enforce freshness constraints
        _enforce_freshness(signal, max_age_days=7)

        if signal.get("stale"):
            stale_signals.append(signal)
        else:
            valid_signals.append(signal)

    # Write outputs
    if not args.dry_run:
        output_dir = repo / "artifacts" / "marketing" / "signals"
        _write_signals(valid_signals, output_dir)

        # Also write stale signals for audit trail
        if stale_signals:
            stale_dir = repo / "artifacts" / "marketing"
            stale_dir.mkdir(parents=True, exist_ok=True)
            stale_file = stale_dir / "stale_signals.jsonl"

            with open(stale_file, "a") as f:
                for signal in stale_signals:
                    f.write(json.dumps(signal) + "\n")

            logger.info(f"Wrote {len(stale_signals)} stale signals to {stale_file}")

    # Summary stats
    logger.info("=" * 70)
    logger.info("INGESTION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total records read:    {len(records)}")
    logger.info(f"Valid (fresh):         {len(valid_signals)}")
    logger.info(f"Stale (> 7 days):      {len(stale_signals)}")
    logger.info(f"Rejected (bad ID):     {rejected_count}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
