"""
Chapter flow gate: rejects flat/choppy chapter prose before delivery.
Deterministic heuristics only (no model scoring).
"""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class ChapterFlowResult:
    status: str
    score: int
    errors: list[str]
    warnings: list[str]
    metrics: dict


_FORBIDDEN_PATTERNS = [
    re.compile(r"\{[^}]+\}"),
    re.compile(r"^---\s*$", re.M),
    re.compile(r"\[(?:family|voice_mode|mode|reframe_type):", re.I),
    re.compile(r"\b(?:family|voice_mode|mode|reframe_type|mechanism_emphasis)\s*:", re.I),
]

_REPETITIVE_PHRASES = [
    "i have noticed that",
    "what i have come to understand",
    "what i have come to think",
    "there is a mechanism that",
]

_TRANSITION_CUES = (
    "that moment",
    "which means",
    "so when",
    "this is why",
    "in practice",
    "for example",
    "here is",
    "because",
)

_THESIS_CUES = (
    "principle:",
    "the point is",
    "what this means",
    "this is not",
)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z']+", text.lower()))


def evaluate_chapter_flow(chapter_text: str) -> ChapterFlowResult:
    errors: list[str] = []
    warnings: list[str] = []

    text = (chapter_text or "").strip()
    if not text:
        return ChapterFlowResult("FAIL", 0, ["CHAPTER_EMPTY"], [], {})

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    sentences = _sentences(text)
    if len(sentences) < 14:
        errors.append("TOO_SHORT_FOR_AUDIO_FLOW")

    for pat in _FORBIDDEN_PATTERNS:
        if pat.search(text):
            errors.append("DELIVERY_ARTIFACT_PRESENT")
            break

    lower = text.lower()
    for phrase in _REPETITIVE_PHRASES:
        count = lower.count(phrase)
        if count > 1:
            errors.append(f"REPETITIVE_STEM:{phrase}")

    transition_hits = sum(1 for cue in _TRANSITION_CUES if cue in lower)
    if transition_hits < 3:
        errors.append("WEAK_TRANSITIONS")

    thesis_hits = sum(1 for cue in _THESIS_CUES if cue in lower)
    if thesis_hits < 1:
        errors.append("MISSING_CLEAR_POINT")

    overlaps = []
    for i in range(1, len(paragraphs)):
        prev_tokens = _token_set(paragraphs[i - 1])
        curr_tokens = _token_set(paragraphs[i])
        if not prev_tokens or not curr_tokens:
            continue
        jaccard = len(prev_tokens & curr_tokens) / max(1, len(prev_tokens | curr_tokens))
        overlaps.append(jaccard)
    avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
    if overlaps and avg_overlap < 0.05:
        errors.append("CHOPPY_SECTION_JUMPS")

    sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
    std_len = statistics.pstdev(sentence_lengths) if len(sentence_lengths) >= 2 else 0.0
    if std_len < 4.0:
        warnings.append("LOW_RHYTHM_VARIATION")

    if not re.search(r"\b(breathe|pause|exhale|inhale|write|name|notice|choose|practice)\b", lower):
        errors.append("NO_ACTIONABLE_STEP")

    status = "PASS" if not errors else "FAIL"
    score = max(0, 100 - len(errors) * 15 - len(warnings) * 5)

    metrics = {
        "paragraphs": len(paragraphs),
        "sentences": len(sentences),
        "transition_hits": transition_hits,
        "thesis_hits": thesis_hits,
        "avg_adjacent_overlap": round(avg_overlap, 3),
        "sentence_len_std": round(std_len, 2),
    }
    return ChapterFlowResult(status, score, errors, warnings, metrics)
