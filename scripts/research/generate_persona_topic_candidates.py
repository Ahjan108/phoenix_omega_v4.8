#!/usr/bin/env python3
"""
Generate persona/topic metadata candidate updates from the research KB.
Reads artifacts/research/kb/entries.jsonl, extracts signals, and writes
proposed patches to artifacts/ei_v2/metadata_candidates/<YYYYMMDD>_<batch>.json.

These candidates are SHADOW only — they do not affect live EI V2 until:
  1. check_metadata_promotion_gate.py passes
  2. promote_metadata_candidates.py is run (manual step)

Usage:
  python scripts/research/generate_persona_topic_candidates.py
  python scripts/research/generate_persona_topic_candidates.py --dry-run
  python scripts/research/generate_persona_topic_candidates.py --min-confidence 0.75
"""
from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
KB_ENTRIES_PATH = REPO_ROOT / "artifacts" / "research" / "kb" / "entries.jsonl"
CANDIDATES_DIR = REPO_ROOT / "artifacts" / "ei_v2" / "metadata_candidates"

# Map Pearl News topics → EI V2 topic IDs (for persona/topic metadata patches)
TOPIC_MAP = {
    "mental_health": "mental_health",
    "climate": "environmental_issues",
    "economy_work": "financial_stress",
    "education": "identity_self_discovery",
    "peace_conflict": "grief",
    "inequality": "self_worth",
    "partnerships": "courage",
}

# Gen Z/Alpha personas that benefit most from research-derived signals
TARGET_PERSONAS = ["gen_alpha_students", "gen_z_professionals"]

STOP_WORDS = {
    "the", "a", "an", "and", "or", "of", "in", "to", "is", "are", "for",
    "at", "on", "by", "with", "this", "that", "from", "but", "as", "be",
    "was", "were", "their", "they", "have", "has", "had", "not", "all", "it",
    "its", "can", "which", "who", "when", "where", "than", "more", "most",
    "yet", "also", "both", "each", "into", "per", "only", "any",
}


def _load_entries(min_confidence: float) -> list[dict]:
    if not KB_ENTRIES_PATH.exists():
        logger.error("KB not found: %s — run build_research_kb.py first", KB_ENTRIES_PATH)
        return []
    entries = []
    with open(KB_ENTRIES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    e = json.loads(line)
                    if float(e.get("confidence") or 0) >= min_confidence:
                        entries.append(e)
                except Exception:
                    pass
    logger.info("Loaded %d entries (confidence >= %.2f)", len(entries), min_confidence)
    return entries


def _extract_key_phrases(text: str, max_phrases: int = 8) -> list[str]:
    """Extract meaningful 2-3 word phrases from text."""
    words = re.findall(r'\b[a-z][a-z\'-]{2,}\b', text.lower())
    words = [w for w in words if w not in STOP_WORDS and len(w) > 3]
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)
               if words[i] not in STOP_WORDS and words[i+1] not in STOP_WORDS]
    # Prefer longer phrases; deduplicate
    seen = set()
    result = []
    for p in bigrams:
        if p not in seen:
            seen.add(p)
            result.append(p)
        if len(result) >= max_phrases:
            break
    return result


def _build_topic_vocabulary_patches(entries: list[dict]) -> list[dict[str, Any]]:
    """
    Generate vocabulary patches: new phrases to add to topic lexicons in domain_embeddings.
    """
    patches = []
    from collections import defaultdict
    topic_phrases: dict[str, list] = defaultdict(list)

    for entry in entries:
        pn_topics = entry.get("topics") or []
        claim = entry.get("claim") or ""
        evidence = entry.get("evidence") or ""
        invisible = entry.get("invisible_script") or ""
        phrases = _extract_key_phrases(f"{claim} {evidence} {invisible}", max_phrases=6)
        for pn_topic in pn_topics:
            ei_topic = TOPIC_MAP.get(pn_topic)
            if ei_topic:
                topic_phrases[ei_topic].extend(phrases)

    for ei_topic, phrase_list in topic_phrases.items():
        # Deduplicate, sort by frequency
        from collections import Counter
        freq = Counter(phrase_list)
        top_phrases = [p for p, _ in freq.most_common(12)]
        if top_phrases:
            patches.append({
                "patch_type": "topic_vocabulary_add",
                "target": f"domain_embeddings._TOPIC_LEXICONS.{ei_topic}",
                "add_terms": top_phrases,
                "source": "research_kb",
                "rationale": f"Terms extracted from {len(entries)} research KB entries for topic '{ei_topic}'",
            })
    return patches


def _build_invisible_script_patches(entries: list[dict]) -> list[dict[str, Any]]:
    """
    Generate patches: new invisible scripts to add to marketing/research awareness.
    These feed into EI V2 safety_classifier and domain_embeddings.
    """
    patches = []
    scripts = []
    for entry in entries:
        s = entry.get("invisible_script")
        if s and len(s.strip()) > 15:
            scripts.append({
                "text": s.strip()[:200],
                "topics": entry.get("topics", []),
                "cohorts": entry.get("cohorts", []),
                "confidence": float(entry.get("confidence") or 0),
            })
    if scripts:
        patches.append({
            "patch_type": "invisible_scripts_add",
            "target": "config/research_metadata/invisible_scripts.yaml",
            "add_entries": scripts,
            "source": "research_kb",
            "rationale": f"{len(scripts)} new invisible scripts from research KB",
        })
    return patches


def _build_youth_anchor_patches(entries: list[dict]) -> list[dict[str, Any]]:
    """
    Generate patches: youth data anchors (% stats, named sources) to add to
    persona lexicons for gen_alpha_students and gen_z_professionals.
    """
    pct_pattern = re.compile(r"\b(\d+)\s*%")
    anchors = []
    for entry in entries:
        claim = entry.get("claim") or ""
        pcts = pct_pattern.findall(claim)
        for pct in pcts:
            if 5 <= int(pct) <= 95:  # Filter out edge cases (0%, 100%)
                anchors.append(f"{pct}%")
        age_matches = re.findall(r"ages?\s+(\d+[-–]\d+|\d+)", claim)
        anchors.extend([f"ages {a}" for a in age_matches])

    anchors = list(set(anchors))
    if anchors:
        patches = []
        for persona in TARGET_PERSONAS:
            patches.append({
                "patch_type": "persona_vocabulary_add",
                "target": f"domain_embeddings._PERSONA_LEXICONS.{persona}",
                "add_terms": sorted(anchors)[:20],
                "source": "research_kb",
                "rationale": f"Youth data anchors from research KB for persona '{persona}'",
            })
        return patches
    return []


def generate_candidates(min_confidence: float = 0.65) -> dict[str, Any]:
    """Generate all candidate patches from the research KB."""
    entries = _load_entries(min_confidence)
    if not entries:
        return {"error": "No KB entries found"}

    patches = []
    patches.extend(_build_topic_vocabulary_patches(entries))
    patches.extend(_build_invisible_script_patches(entries))
    patches.extend(_build_youth_anchor_patches(entries))

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kb_entries_used": len(entries),
        "min_confidence": min_confidence,
        "patch_count": len(patches),
        "status": "shadow_pending",  # Always shadow until promoted
        "promotion_required": True,
        "patches": patches,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate EI V2 persona/topic metadata candidates from research KB")
    ap.add_argument("--dry-run", action="store_true", help="Print candidates without writing")
    ap.add_argument("--min-confidence", type=float, default=0.65)
    args = ap.parse_args()

    candidates = generate_candidates(min_confidence=args.min_confidence)
    if "error" in candidates:
        logger.error(candidates["error"])
        return 1

    logger.info(
        "Generated %d patches from %d KB entries",
        candidates["patch_count"], candidates["kb_entries_used"],
    )

    if args.dry_run:
        print(f"DRY RUN: {candidates['patch_count']} patches")
        for p in candidates["patches"]:
            print(f"  [{p['patch_type']}] → {p['target']}: {len(p.get('add_terms') or p.get('add_entries') or [])} items")
        return 0

    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    out_path = CANDIDATES_DIR / f"{today}_kb_derived.json"
    out_path.write_text(json.dumps(candidates, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote candidates → %s", out_path)
    print(f"Candidates written to {out_path}")
    print(f"Next step: python scripts/research/check_metadata_promotion_gate.py --candidates {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
