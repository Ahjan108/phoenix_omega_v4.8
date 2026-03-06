#!/usr/bin/env python3
"""
Append a new entry to the Pearl News / EI V2 research KB.
Called after a research run (run_research.py output) or after article publication.

Usage:
  # From a research run YAML
  python scripts/research/kb_append.py \
    --source artifacts/research/psychology/psych_2026-03-06.yaml \
    --layer psychology

  # From article feedback (article contributed a data point to KB)
  python scripts/research/kb_append.py \
    --claim "In Japan, 73% of ages 15-29 report climate worry per MOE 2022." \
    --topics climate \
    --cohorts gen_z \
    --regions japan \
    --layer world_events \
    --source-type article_derived \
    --source-file artifacts/pearl_news/drafts/ja/article_xyz.json \
    --confidence 0.82

  # Interactive (prompts for required fields)
  python scripts/research/kb_append.py --interactive
"""
from __future__ import annotations

import argparse
import json
import hashlib
import logging
from datetime import date, datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
KB_DIR = REPO_ROOT / "artifacts" / "research" / "kb"
ENTRIES_PATH = KB_DIR / "entries.jsonl"
INDEX_PATH = KB_DIR / "index.json"

TOPIC_KEYS = {"climate", "mental_health", "peace_conflict", "education", "economy_work", "inequality", "partnerships"}
LAYER_VALUES = {"psychology", "pain_points", "world_events", "narrative", "platform", "seed"}
SOURCE_TYPES = {"research_run", "manual_doc", "article_derived", "feed_snapshot", "kb_seed"}


def _load_existing_ids() -> set[str]:
    ids = set()
    if ENTRIES_PATH.exists():
        with open(ENTRIES_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        e = json.loads(line)
                        ids.add(e.get("id", ""))
                    except Exception:
                        pass
    return ids


def _make_entry_id(layer: str, topics: list, cohorts: list, seq: int) -> str:
    today = date.today().strftime("%Y%m%d")
    topic_str = "_".join(sorted(topics)[:2]) or "general"
    cohort_str = "_".join(sorted(cohorts)[:1]) or "gen_z"
    return f"{layer}_{topic_str}_{cohort_str}_{today}_{seq:03d}"


def _rebuild_index(entries: list[dict]) -> dict:
    from collections import defaultdict
    by_topic: dict = defaultdict(list)
    by_cohort: dict = defaultdict(list)
    by_region: dict = defaultdict(list)
    by_layer: dict = defaultdict(list)
    for e in entries:
        for t in e.get("topics", []):
            by_topic[t].append(e["id"])
        for c in e.get("cohorts", []):
            by_cohort[c].append(e["id"])
        for r in e.get("regions", []):
            by_region[r].append(e["id"])
        by_layer[e.get("layer", "seed")].append(e["id"])
    return {
        "schema_version": "1.0",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "entry_count": len(entries),
        "by_topic": dict(by_topic),
        "by_cohort": dict(by_cohort),
        "by_region": dict(by_region),
        "by_layer": dict(by_layer),
    }


def append_entry(entry: dict) -> bool:
    """Append one entry to entries.jsonl and rebuild index. Returns True on success."""
    KB_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing for index rebuild
    existing: list[dict] = []
    if ENTRIES_PATH.exists():
        with open(ENTRIES_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        existing.append(json.loads(line))
                    except Exception:
                        pass

    # Dedup by ID
    existing_ids = {e.get("id") for e in existing}
    if entry.get("id") in existing_ids:
        logger.warning("Entry %s already exists; skipping", entry.get("id"))
        return False

    # Append
    with open(ENTRIES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Rebuild index
    all_entries = existing + [entry]
    index = _rebuild_index(all_entries)
    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    # Invalidate in-process cache
    try:
        from pearl_news.research_kb.retrieval import _invalidate_cache
        _invalidate_cache()
    except Exception:
        pass

    logger.info("Appended entry %s → %s", entry.get("id"), ENTRIES_PATH)
    return True


def append_from_source_file(source_path: Path, layer: str, args: argparse.Namespace) -> int:
    """Parse a research YAML or article JSON and append derived entries."""
    if not source_path.exists():
        logger.error("Source file not found: %s", source_path)
        return 1

    existing_ids = _load_existing_ids()
    seq = len(existing_ids)
    appended = 0

    if source_path.suffix in (".yaml", ".yml") and yaml:
        data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        findings = []
        if isinstance(data, list):
            findings = data
        elif isinstance(data, dict):
            for key in ("findings", "insights", "claims", "entries", "results"):
                if key in data and isinstance(data[key], list):
                    findings = data[key]
                    break
            if not findings:
                findings = [data]

        for item in findings:
            if not isinstance(item, dict):
                continue
            claim = item.get("claim") or item.get("finding") or item.get("insight")
            if not claim:
                continue
            topics_raw = item.get("topics") or args.topics or ["partnerships"]
            topics = [t for t in (topics_raw if isinstance(topics_raw, list) else [topics_raw]) if t in TOPIC_KEYS]
            cohorts = item.get("cohorts") or args.cohorts or ["gen_z"]
            regions = item.get("regions") or args.regions or ["global"]
            seq += 1
            entry_id = _make_entry_id(layer, topics, list(cohorts) if isinstance(cohorts, list) else [cohorts], seq)
            entry = {
                "id": entry_id,
                "date": item.get("run_date") or item.get("date") or date.today().isoformat(),
                "source_file": str(source_path.relative_to(REPO_ROOT) if source_path.is_relative_to(REPO_ROOT) else source_path),
                "source_type": args.source_type or "research_run",
                "layer": layer,
                "topics": topics or ["partnerships"],
                "cohorts": list(cohorts) if isinstance(cohorts, list) else [cohorts],
                "regions": list(regions) if isinstance(regions, list) else [regions],
                "claim": str(claim).strip()[:500],
                "evidence": str(item.get("evidence") or "")[:300] or None,
                "source_citation": str(item.get("source") or item.get("citation") or "")[:200] or None,
                "invisible_script": str(item.get("invisible_script") or "")[:300] or None,
                "contradiction": str(item.get("contradiction") or "")[:300] or None,
                "confidence": float(item.get("confidence") or args.confidence or 0.72),
                "tags": list(item.get("tags") or []),
                "provenance": {
                    "run_date": date.today().isoformat(),
                    "model": item.get("model") or "qwen3",
                    "prompt_id": layer,
                },
            }
            entry = {k: v for k, v in entry.items() if v is not None and v != "" and v != []}
            if append_entry(entry):
                appended += 1

    elif source_path.suffix == ".json":
        # Article-derived: extract youth impact / research-like content
        data = json.loads(source_path.read_text(encoding="utf-8"))
        claim = args.claim or f"Article-derived entry from {source_path.name}"
        topics = args.topics or [data.get("topic") or "partnerships"]
        seq += 1
        entry_id = _make_entry_id(layer, topics, args.cohorts or ["gen_z"], seq)
        entry = {
            "id": entry_id,
            "date": date.today().isoformat(),
            "source_file": str(source_path),
            "source_type": "article_derived",
            "layer": layer,
            "topics": [t for t in topics if t in TOPIC_KEYS] or ["partnerships"],
            "cohorts": args.cohorts or ["gen_z"],
            "regions": args.regions or ["global"],
            "claim": claim.strip()[:500],
            "confidence": float(args.confidence or 0.6),
        }
        if append_entry(entry):
            appended += 1

    logger.info("Appended %d new entries from %s", appended, source_path.name)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Append entry to Pearl News research KB")
    ap.add_argument("--source", help="Path to source YAML (research run output) or JSON (article)")
    ap.add_argument("--layer", default="world_events", choices=sorted(LAYER_VALUES))
    ap.add_argument("--claim", help="Claim text (for single-entry append without source file)")
    ap.add_argument("--topics", nargs="+", help="Topic keys (e.g. climate mental_health)")
    ap.add_argument("--cohorts", nargs="+", default=["gen_z"])
    ap.add_argument("--regions", nargs="+", default=["global"])
    ap.add_argument("--source-type", default="research_run", choices=sorted(SOURCE_TYPES))
    ap.add_argument("--source-file", help="Source file path (for attribution)")
    ap.add_argument("--confidence", type=float, default=0.72)
    ap.add_argument("--invisible-script", help="Invisible script for single-entry mode")
    ap.add_argument("--contradiction", help="Contradiction for single-entry mode")
    ap.add_argument("--evidence", help="Evidence / citation text")
    ap.add_argument("--interactive", action="store_true", help="Interactive mode (prompt for fields)")
    args = ap.parse_args()

    if args.source:
        return append_from_source_file(Path(args.source), args.layer, args)

    if args.claim:
        topics = args.topics or ["partnerships"]
        existing = _load_existing_ids()
        seq = len(existing) + 1
        entry_id = _make_entry_id(args.layer, topics, args.cohorts, seq)
        entry = {
            "id": entry_id,
            "date": date.today().isoformat(),
            "source_file": args.source_file or "manual",
            "source_type": args.source_type,
            "layer": args.layer,
            "topics": [t for t in topics if t in TOPIC_KEYS] or ["partnerships"],
            "cohorts": args.cohorts,
            "regions": args.regions,
            "claim": args.claim.strip()[:500],
            "confidence": args.confidence,
        }
        if args.invisible_script:
            entry["invisible_script"] = args.invisible_script[:300]
        if args.contradiction:
            entry["contradiction"] = args.contradiction[:300]
        if args.evidence:
            entry["evidence"] = args.evidence[:300]
        success = append_entry(entry)
        return 0 if success else 1

    if args.interactive:
        print("KB Append — Interactive Mode")
        claim = input("Claim (required): ").strip()
        if not claim:
            print("Claim required.")
            return 1
        topics = input("Topics (space-separated, e.g. climate mental_health): ").split() or ["partnerships"]
        cohorts = input("Cohorts [gen_z]: ").split() or ["gen_z"]
        regions = input("Regions [global]: ").split() or ["global"]
        layer = input("Layer [world_events]: ").strip() or "world_events"
        confidence = float(input("Confidence 0-1 [0.72]: ") or "0.72")
        evidence = input("Evidence (optional): ").strip() or None
        existing = _load_existing_ids()
        seq = len(existing) + 1
        entry_id = _make_entry_id(layer, topics, cohorts, seq)
        entry = {
            "id": entry_id,
            "date": date.today().isoformat(),
            "source_file": "manual_interactive",
            "source_type": "manual_doc",
            "layer": layer,
            "topics": [t for t in topics if t in TOPIC_KEYS] or ["partnerships"],
            "cohorts": cohorts,
            "regions": regions,
            "claim": claim[:500],
            "confidence": confidence,
        }
        if evidence:
            entry["evidence"] = evidence[:300]
        success = append_entry(entry)
        return 0 if success else 1

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
