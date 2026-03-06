#!/usr/bin/env python3
"""
Build (or rebuild) the Pearl News / EI V2 Gen Z/Gen Alpha Research Knowledge Base.
Scans artifacts/research/{psychology,pain_points,world_events,narrative}/ for YAML outputs
from run_research.py, normalizes into KB entries, and writes:
  artifacts/research/kb/entries.jsonl  — append-friendly JSONL
  artifacts/research/kb/index.json     — topic/cohort/region/layer lookup index

Usage:
  python scripts/research/build_research_kb.py
  python scripts/research/build_research_kb.py --rebuild   # Clear existing entries and reseed
  python scripts/research/build_research_kb.py --dry-run   # Show what would be ingested
"""
from __future__ import annotations

import argparse
import json
import hashlib
import logging
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = REPO_ROOT / "artifacts" / "research"
KB_DIR = ARTIFACTS_ROOT / "kb"
ENTRIES_PATH = KB_DIR / "entries.jsonl"
INDEX_PATH = KB_DIR / "index.json"

TOPIC_KEYS = {
    "climate", "mental_health", "peace_conflict", "education",
    "economy_work", "inequality", "partnerships",
}

LAYER_DIRS = {
    "psychology": ARTIFACTS_ROOT / "psychology",
    "pain_points": ARTIFACTS_ROOT / "pain_points",
    "world_events": ARTIFACTS_ROOT / "world_events",
    "narrative": ARTIFACTS_ROOT / "narrative",
    "platform": ARTIFACTS_ROOT / "platform",
}


def _make_entry_id(layer: str, topics: list, cohorts: list, regions: list, source_file: str, seq: int = 0) -> str:
    topic_str = "_".join(sorted(topics)[:2]) or "general"
    cohort_str = "_".join(sorted(cohorts)[:1]) or "gen_z"
    region_str = "_".join(sorted(regions)[:1]) or "global"
    today = date.today().strftime("%Y%m%d")
    base = f"{layer}_{topic_str}_{cohort_str}_{today}_{seq:03d}"
    return base


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]


def _infer_topics(text: str) -> list[str]:
    """Infer Pearl News topic keys from YAML content text."""
    lower = text.lower()
    found = []
    keyword_map = {
        "climate": ["climate", "carbon", "emissions", "temperature", "environment", "ecological"],
        "mental_health": ["mental health", "anxiety", "depression", "wellbeing", "burnout", "stress"],
        "peace_conflict": ["conflict", "peace", "refugee", "war", "violence", "security"],
        "education": ["education", "school", "student", "learning", "university", "credential"],
        "economy_work": ["economy", "work", "job", "employment", "income", "wage", "poverty"],
        "inequality": ["inequality", "equity", "gap", "discrimination", "marginali"],
        "partnerships": ["partnership", "institution", "trust", "civic", "organisation", "ngo"],
    }
    for topic, keywords in keyword_map.items():
        if any(kw in lower for kw in keywords):
            found.append(topic)
    return found or ["partnerships"]


def _infer_cohorts(text: str) -> list[str]:
    lower = text.lower()
    cohorts = []
    if any(k in lower for k in ["gen z", "gen-z", "generation z", "ages 15", "ages 18", "ages 22"]):
        cohorts.append("gen_z")
    if any(k in lower for k in ["gen alpha", "gen-alpha", "generation alpha", "ages 10", "children"]):
        cohorts.append("gen_alpha")
    return cohorts or ["gen_z"]


def _infer_regions(text: str) -> list[str]:
    lower = text.lower()
    regions = []
    if any(k in lower for k in ["japan", "japanese", "tokyo"]):
        regions.append("japan")
    if any(k in lower for k in ["china", "chinese", "beijing", "tangping"]):
        regions.append("china")
    if any(k in lower for k in ["us", "usa", "uk", "australia", "english-speaking"]):
        regions.append("english")
    if not regions or "global" in lower:
        regions.append("global")
    return regions


def _infer_confidence(entry_data: dict) -> float:
    """Infer confidence from presence of citation, sample size mentions, etc."""
    text = json.dumps(entry_data).lower()
    if any(k in text for k in ["n=", "sample size", "national survey", "pew", "gallup", "who ", "unesco"]):
        return 0.88
    if any(k in text for k in ["study", "report", "survey", "census"]):
        return 0.78
    return 0.65


def _normalize_research_yaml(
    path: Path,
    layer: str,
    existing_ids: set[str],
    seq_counter: dict,
) -> list[dict[str, Any]]:
    """Parse a research YAML output file into KB entries."""
    if yaml is None:
        logger.warning("pyyaml not installed; cannot parse %s", path)
        return []
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        data = yaml.safe_load(raw) or {}
    except Exception as e:
        logger.warning("Could not parse %s: %s", path, e)
        return []

    entries = []
    # Research YAML outputs typically have: topic_key or findings list, etc.
    # Support several common structures from run_research.py output
    findings = []
    if isinstance(data, list):
        findings = data
    elif isinstance(data, dict):
        # Try common keys
        for key in ("findings", "insights", "claims", "entries", "results"):
            if key in data and isinstance(data[key], list):
                findings = data[key]
                break
        if not findings:
            # Treat the whole dict as one entry
            findings = [data]

    for item in findings:
        if not isinstance(item, dict):
            continue
        claim = item.get("claim") or item.get("finding") or item.get("insight") or str(item)[:200]
        if not claim or len(str(claim).strip()) < 20:
            continue

        topics = item.get("topics") or item.get("topic_keys") or _infer_topics(json.dumps(item))
        if isinstance(topics, str):
            topics = [topics]
        cohorts = item.get("cohorts") or item.get("cohort") or _infer_cohorts(json.dumps(item))
        if isinstance(cohorts, str):
            cohorts = [cohorts]
        regions = item.get("regions") or item.get("region") or _infer_regions(json.dumps(item))
        if isinstance(regions, str):
            regions = [regions]

        seq_counter["n"] += 1
        entry_id = _make_entry_id(layer, topics, cohorts, regions, path.name, seq_counter["n"])

        # Skip if already in KB (by content hash — prevent duplicates on rebuild)
        content_hash = _hash_content(str(claim))
        if content_hash in existing_ids:
            continue
        existing_ids.add(content_hash)

        run_date = item.get("run_date") or item.get("date") or date.today().isoformat()
        model = item.get("model") or item.get("provenance", {}).get("model") or "qwen3"

        entry = {
            "id": entry_id,
            "date": run_date if isinstance(run_date, str) else str(run_date),
            "source_file": str(path.relative_to(REPO_ROOT)),
            "source_type": "research_run",
            "layer": layer,
            "topics": list(set(t for t in topics if t in TOPIC_KEYS)) or ["partnerships"],
            "cohorts": list(set(cohorts)),
            "regions": list(set(regions)),
            "claim": str(claim).strip()[:500],
            "evidence": str(item.get("evidence") or "")[:300] or None,
            "source_citation": str(item.get("source") or item.get("citation") or "")[:200] or None,
            "invisible_script": str(item.get("invisible_script") or "")[:300] or None,
            "contradiction": str(item.get("contradiction") or item.get("contradiction_audit") or "")[:300] or None,
            "confidence": float(item.get("confidence") or _infer_confidence(item)),
            "tags": list(item.get("tags") or []),
            "provenance": {
                "run_date": date.today().isoformat(),
                "model": model,
                "prompt_id": item.get("prompt_id") or layer,
            },
        }
        # Clean None values for compactness
        entry = {k: v for k, v in entry.items() if v is not None and v != "" and v != []}
        entries.append(entry)

    logger.info("  %s → %d entries (layer=%s)", path.name, len(entries), layer)
    return entries


def _build_index(entries: list[dict]) -> dict:
    """Build lookup index from entries."""
    by_topic: dict[str, list] = defaultdict(list)
    by_cohort: dict[str, list] = defaultdict(list)
    by_region: dict[str, list] = defaultdict(list)
    by_layer: dict[str, list] = defaultdict(list)

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


def main() -> int:
    ap = argparse.ArgumentParser(description="Build/update Pearl News research KB")
    ap.add_argument("--rebuild", action="store_true", help="Clear existing non-seed entries and rescan")
    ap.add_argument("--dry-run", action="store_true", help="Print what would be ingested, don't write")
    args = ap.parse_args()

    KB_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing entries
    existing_entries: list[dict] = []
    existing_content_hashes: set[str] = set()
    if ENTRIES_PATH.exists() and not args.rebuild:
        with open(ENTRIES_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        e = json.loads(line)
                        existing_entries.append(e)
                        existing_content_hashes.add(_hash_content(e.get("claim", "")))
                    except Exception:
                        pass
        logger.info("Loaded %d existing KB entries", len(existing_entries))
    elif args.rebuild:
        # Keep only seed entries (source_type=kb_seed)
        if ENTRIES_PATH.exists():
            with open(ENTRIES_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            e = json.loads(line)
                            if e.get("source_type") == "kb_seed":
                                existing_entries.append(e)
                                existing_content_hashes.add(_hash_content(e.get("claim", "")))
                        except Exception:
                            pass
        logger.info("Rebuild: kept %d seed entries, rescanning research artifacts", len(existing_entries))

    # Scan research artifact directories for new YAML outputs
    new_entries: list[dict] = []
    seq_counter = {"n": len(existing_entries)}

    for layer, layer_dir in LAYER_DIRS.items():
        if not layer_dir.exists():
            continue
        yaml_files = [f for f in layer_dir.glob("*.yaml") if f.stem != ".gitkeep"]
        yaml_files += [f for f in layer_dir.glob("*.yml") if f.stem != ".gitkeep"]
        if not yaml_files:
            continue
        logger.info("Scanning %s/ (%d files)", layer, len(yaml_files))
        for yf in sorted(yaml_files):
            entries = _normalize_research_yaml(yf, layer, existing_content_hashes, seq_counter)
            new_entries.extend(entries)

    all_entries = existing_entries + new_entries
    logger.info("Total: %d entries (%d existing + %d new)", len(all_entries), len(existing_entries), len(new_entries))

    if args.dry_run:
        print(f"DRY RUN: would write {len(all_entries)} entries ({len(new_entries)} new) to {ENTRIES_PATH}")
        for e in new_entries[:5]:
            print(f"  [{e['layer']}] {e['id']}: {e['claim'][:80]}…")
        return 0

    # Write JSONL
    with open(ENTRIES_PATH, "w", encoding="utf-8") as f:
        for e in all_entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    logger.info("Wrote %s (%d entries, %d bytes)", ENTRIES_PATH, len(all_entries), ENTRIES_PATH.stat().st_size)

    # Write index
    index = _build_index(all_entries)
    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote %s", INDEX_PATH)

    print(f"KB build complete: {len(all_entries)} entries, {len(new_entries)} new")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
