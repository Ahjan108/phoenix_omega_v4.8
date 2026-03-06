"""
EI V2 — Research KB Lexicon Loader.
Follows the same pattern as marketing_lexicons.py:
  - When enabled + KB present: load research KB signals into EI V2 dimensions.
  - Missing/empty KB: fallback to built-in signals with warning (no crash).
  - One global config switch (research_kb.enabled: false) disables all research integration.

Provides:
  get_research_signals(config, repo_root) → ResearchSignals
  ResearchSignals fields:
    youth_anchors        — concrete data phrases/patterns from KB (for domain_embeddings youth weight)
    invisible_scripts    — invisible script phrases by persona/topic (for safety_classifier awareness)
    contradiction_markers — contradiction phrases (for engagement scoring)
    topic_vocabulary     — topic-relevant terms extracted from KB claims (for domain coherence)
    loaded_from_kb       — True if real KB data was loaded
    kb_entry_count       — number of KB entries used
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, NamedTuple

logger = logging.getLogger(__name__)


class ResearchSignals(NamedTuple):
    youth_anchors: list[str]           # Concrete youth data phrases (% stats, age bands, place names)
    invisible_scripts: list[str]       # Invisible scripts from KB (behavioural assumptions)
    contradiction_markers: list[str]   # Contradiction audit outputs
    topic_vocabulary: dict[str, set[str]]  # topic → relevant terms
    loaded_from_kb: bool
    kb_entry_count: int


# Built-in fallback signals (minimal; used if KB unavailable)
_FALLBACK_YOUTH_ANCHORS = [
    "gen z", "gen alpha", "ages 15-28", "ages 10-15",
    "youth unemployment", "student debt", "mental health",
]
_FALLBACK_INVISIBLE_SCRIPTS = [
    "the system is broken",
    "individual action is insufficient",
    "institutions cannot be trusted",
    "the credential was the path",
]
_FALLBACK_CONTRADICTION_MARKERS = [
    "yet", "despite", "contradiction", "at the same time",
    "while", "though", "paradoxically",
]


def _extract_youth_anchors(entries: list[dict]) -> list[str]:
    """Extract concrete youth data phrases from KB claims and evidence."""
    anchors = set()
    pct_pattern = re.compile(r"\b\d+\s*%")
    age_pattern = re.compile(r"\bages?\s+\d+")
    num_pattern = re.compile(r"\b\d[\d,\.]+\s*(million|billion|thousand|M|B)\b", re.IGNORECASE)

    for entry in entries:
        for field in ("claim", "evidence", "source_citation"):
            text = entry.get(field) or ""
            for match in pct_pattern.findall(text):
                anchors.add(match.strip())
            for match in age_pattern.findall(text):
                anchors.add(match.strip())
            for match in num_pattern.findall(text):
                anchors.add(match[0].strip() if isinstance(match, tuple) else match.strip())

    # Add named generation terms
    anchors.update(["gen z", "gen alpha", "generation z", "generation alpha",
                     "adolescent", "youth", "young people"])
    return sorted(anchors)


def _extract_invisible_scripts(entries: list[dict]) -> list[str]:
    """Extract invisible script phrases from KB entries."""
    scripts = []
    for entry in entries:
        s = entry.get("invisible_script")
        if s and len(s.strip()) > 10:
            # Normalize: lowercase, strip
            scripts.append(s.strip().lower()[:200])
    return list(dict.fromkeys(scripts))  # deduplicate, preserve order


def _extract_contradiction_markers(entries: list[dict]) -> list[str]:
    """Extract contradiction audit phrases from KB entries."""
    markers = []
    for entry in entries:
        c = entry.get("contradiction")
        if c and len(c.strip()) > 10:
            markers.append(c.strip()[:200])
    # Also add structural contradiction words
    markers.extend(["yet", "despite", "contradiction", "paradox", "at the same time",
                     "while claiming", "while reporting", "though", "however",
                     "simultaneously", "coexists with"])
    return list(dict.fromkeys(markers))


def _extract_topic_vocabulary(entries: list[dict]) -> dict[str, set[str]]:
    """Build topic → vocabulary terms from KB claims."""
    vocab: dict[str, set[str]] = {}
    stop_words = {"the", "a", "an", "and", "or", "of", "in", "to", "is", "are", "for",
                  "at", "on", "by", "with", "this", "that", "from", "but", "as", "be"}
    for entry in entries:
        claim = entry.get("claim") or ""
        topics = entry.get("topics") or []
        words = set(w.lower() for w in re.findall(r'\b[a-z]{4,}\b', claim.lower())
                    if w not in stop_words)
        for topic in topics:
            if topic not in vocab:
                vocab[topic] = set()
            vocab[topic].update(words)
    return vocab


def get_research_signals(
    config: dict[str, Any],
    repo_root: Path | None = None,
) -> ResearchSignals:
    """
    Load research signals from KB per EI V2 config.
    config: the full ei_v2_config dict (looks for research_kb section).
    """
    rk_cfg = config.get("research_kb") or {}
    if not rk_cfg.get("enabled", False):
        logger.info("EI V2 research_kb disabled; using built-in fallback signals")
        return ResearchSignals(
            youth_anchors=_FALLBACK_YOUTH_ANCHORS,
            invisible_scripts=_FALLBACK_INVISIBLE_SCRIPTS,
            contradiction_markers=_FALLBACK_CONTRADICTION_MARKERS,
            topic_vocabulary={},
            loaded_from_kb=False,
            kb_entry_count=0,
        )

    # Locate KB
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[4]  # from phoenix_v4/quality/ei_v2/ → repo root
    kb_path = rk_cfg.get("kb_path") or "artifacts/research/kb"
    kb_dir = repo_root / kb_path if not Path(kb_path).is_absolute() else Path(kb_path)
    entries_path = kb_dir / "entries.jsonl"

    if not entries_path.exists():
        logger.warning(
            "EI V2 research_kb: KB not found at %s; using built-in fallback", entries_path
        )
        return ResearchSignals(
            youth_anchors=_FALLBACK_YOUTH_ANCHORS,
            invisible_scripts=_FALLBACK_INVISIBLE_SCRIPTS,
            contradiction_markers=_FALLBACK_CONTRADICTION_MARKERS,
            topic_vocabulary={},
            loaded_from_kb=False,
            kb_entry_count=0,
        )

    # Load entries
    entries: list[dict] = []
    try:
        with open(entries_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    except Exception as e:
        logger.warning("EI V2 research_kb: failed to load %s: %s; using fallback", entries_path, e)
        return ResearchSignals(
            youth_anchors=_FALLBACK_YOUTH_ANCHORS,
            invisible_scripts=_FALLBACK_INVISIBLE_SCRIPTS,
            contradiction_markers=_FALLBACK_CONTRADICTION_MARKERS,
            topic_vocabulary={},
            loaded_from_kb=False,
            kb_entry_count=0,
        )

    # Apply confidence filter
    min_confidence = float(rk_cfg.get("min_confidence") or 0.65)
    entries = [e for e in entries if float(e.get("confidence") or 0) >= min_confidence]

    logger.info("EI V2 research_kb: loaded %d entries (confidence >= %.2f)", len(entries), min_confidence)

    return ResearchSignals(
        youth_anchors=_extract_youth_anchors(entries),
        invisible_scripts=_extract_invisible_scripts(entries),
        contradiction_markers=_extract_contradiction_markers(entries),
        topic_vocabulary=_extract_topic_vocabulary(entries),
        loaded_from_kb=True,
        kb_entry_count=len(entries),
    )
