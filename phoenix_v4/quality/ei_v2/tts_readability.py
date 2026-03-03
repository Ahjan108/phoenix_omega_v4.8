"""
TTS readability scorer for EI V2.

Scores how well prose "breathes" when spoken by a monotone TTS engine
(Google Play auto-narration). Detects:
  - Sentences that run on and lose the listener
  - Awkward word sequences TTS engines stumble on
  - Missing natural breath points (paragraph breaks)
  - Rhythm monotony across consecutive sentences
  - Problematic constructs (deeply nested parentheses, semicolon chains)

Returns a composite readability score in [0, 1] plus per-dimension metrics.
Designed for the Phoenix audio-first prose contract.
"""
from __future__ import annotations

import math
import re
import statistics
from typing import Any, Dict, List, Optional


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences (handles abbreviations, decimals)."""
    text = re.sub(r"(\w)\.(\w)", r"\1. \2", text)
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _word_count(text: str) -> int:
    return len(text.split())


def _syllable_estimate(word: str) -> int:
    """Rough syllable count for rhythm analysis."""
    word = word.lower().strip(".,!?;:\"'()")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _sentence_lengths(sentences: List[str]) -> List[int]:
    return [_word_count(s) for s in sentences]


def _rhythm_variance(sentences: List[str]) -> float:
    """Coefficient of variation of sentence lengths. Higher = more rhythmic variety."""
    lengths = _sentence_lengths(sentences)
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    stdev = statistics.stdev(lengths)
    return stdev / mean


def _consecutive_similar_length_penalty(sentences: List[str], tolerance: int = 3) -> float:
    """Penalty for consecutive sentences with similar word count (monotone pacing)."""
    lengths = _sentence_lengths(sentences)
    if len(lengths) < 3:
        return 0.0
    consecutive_similar = 0
    max_run = 0
    current_run = 1
    for i in range(1, len(lengths)):
        if abs(lengths[i] - lengths[i - 1]) <= tolerance:
            current_run += 1
        else:
            max_run = max(max_run, current_run)
            current_run = 1
    max_run = max(max_run, current_run)
    if max_run >= 4:
        return min(1.0, (max_run - 3) * 0.25)
    return 0.0


def _long_sentence_penalty(sentences: List[str], max_words: int = 35) -> float:
    """Fraction of sentences exceeding max word count."""
    if not sentences:
        return 0.0
    over = sum(1 for s in sentences if _word_count(s) > max_words)
    return over / len(sentences)


def _short_sentence_ratio(sentences: List[str], min_words: int = 4) -> float:
    """Fraction of very short sentences (can feel choppy in TTS)."""
    if not sentences:
        return 0.0
    short = sum(1 for s in sentences if _word_count(s) < min_words)
    return short / len(sentences)


def _paragraph_break_score(text: str, ideal_per_500: int = 3) -> float:
    """Score paragraph break frequency. Too few = wall of sound; too many = fragmented."""
    wc = max(1, _word_count(text))
    breaks = text.count("\n\n")
    per_500 = breaks / (wc / 500.0)
    if per_500 < 1:
        return max(0.0, per_500)
    if per_500 > ideal_per_500 * 2:
        return max(0.0, 1.0 - (per_500 - ideal_per_500 * 2) / ideal_per_500)
    return min(1.0, per_500 / ideal_per_500)


def _problematic_tts_pattern_count(text: str, patterns: Optional[List[str]] = None) -> int:
    """Count occurrences of patterns that TTS engines handle poorly."""
    default_patterns = [
        r"\b\w{15,}\b",           # Very long words (compounds, technical terms)
        r"\([^)]{50,}\)",         # Long parenthetical asides
        r";\s*\w+;\s*\w+;",      # Semicolon chains
        r"--\s*\w+.*?--",        # Em-dash asides (TTS pausing issues)
        r"\b\d+\.\d+\.\d+\b",   # Version numbers
        r"[A-Z]{4,}",            # All-caps words (TTS may spell out)
        r"\?\s*\?",              # Multiple question marks
        r"!\s*!",                # Multiple exclamation marks
    ]
    patterns = patterns or default_patterns
    count = 0
    for pat_str in patterns:
        try:
            pat = re.compile(pat_str)
            count += len(pat.findall(text))
        except re.error:
            pass
    return count


def _rhetorical_question_penalty(text: str) -> float:
    """Penalize rhetorical questions (TTS makes them sound like real questions)."""
    questions = re.findall(r"[^.!?]*\?", text)
    if not questions:
        return 0.0
    sentences = _split_sentences(text)
    if not sentences:
        return 0.0
    return min(1.0, len(questions) / max(3, len(sentences) * 0.3))


def score_tts_readability(
    text: str,
    *,
    cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Score text for TTS readability.

    Returns dict with:
      - composite: float [0, 1] (higher = better)
      - dimensions: per-dimension scores
      - issues: list of specific problems found
    """
    cfg = cfg or {}
    max_sentence_words = int(cfg.get("max_sentence_words", 35))
    ideal_range = cfg.get("ideal_sentence_range", [8, 25])
    min_para_breaks = int(cfg.get("min_paragraph_breaks_per_500_words", 3))
    rhythm_min = float(cfg.get("rhythm_variance_min", 0.15))
    custom_patterns = cfg.get("problematic_tts_patterns")

    text = text or ""
    sentences = _split_sentences(text)
    issues: List[str] = []

    # Dimension scores (each in [0, 1], higher = better)
    # 1. Sentence length distribution
    long_pen = _long_sentence_penalty(sentences, max_sentence_words)
    short_ratio = _short_sentence_ratio(sentences)
    length_score = 1.0 - (0.6 * long_pen + 0.4 * min(1.0, short_ratio * 2))
    if long_pen > 0.2:
        issues.append(f"long_sentences: {int(long_pen * len(sentences))}/{len(sentences)} exceed {max_sentence_words} words")
    if short_ratio > 0.4:
        issues.append(f"choppy_pacing: {int(short_ratio * 100)}% of sentences under 4 words")

    # 2. Rhythm variance
    rv = _rhythm_variance(sentences)
    rhythm_score = min(1.0, rv / max(rhythm_min, 0.01)) if rv > 0 else 0.0
    monotone_pen = _consecutive_similar_length_penalty(sentences)
    rhythm_score = max(0.0, rhythm_score - monotone_pen)
    if rv < rhythm_min:
        issues.append(f"low_rhythm_variance: {rv:.3f} (min: {rhythm_min})")
    if monotone_pen > 0:
        issues.append(f"monotone_pacing: consecutive similar-length sentences")

    # 3. Paragraph breathing
    para_score = _paragraph_break_score(text, min_para_breaks)
    if para_score < 0.5:
        issues.append("insufficient_paragraph_breaks")

    # 4. TTS-problematic patterns
    prob_count = _problematic_tts_pattern_count(text, custom_patterns)
    tts_pattern_score = max(0.0, 1.0 - prob_count * 0.15)
    if prob_count > 0:
        issues.append(f"tts_problematic_patterns: {prob_count} found")

    # 5. Rhetorical questions
    rq_penalty = _rhetorical_question_penalty(text)
    rq_score = 1.0 - rq_penalty
    if rq_penalty > 0.2:
        issues.append(f"rhetorical_questions: penalty={rq_penalty:.2f}")

    # Composite
    composite = (
        0.25 * length_score
        + 0.25 * rhythm_score
        + 0.20 * para_score
        + 0.15 * tts_pattern_score
        + 0.15 * rq_score
    )

    return {
        "composite": round(max(0.0, min(1.0, composite)), 4),
        "dimensions": {
            "sentence_length": round(length_score, 4),
            "rhythm_variance": round(rhythm_score, 4),
            "paragraph_breathing": round(para_score, 4),
            "tts_pattern_safety": round(tts_pattern_score, 4),
            "rhetorical_question_safety": round(rq_score, 4),
        },
        "metrics": {
            "total_sentences": len(sentences),
            "total_words": _word_count(text),
            "rhythm_cv": round(rv, 4),
            "long_sentence_fraction": round(long_pen, 4),
            "short_sentence_fraction": round(short_ratio, 4),
            "tts_problematic_count": prob_count,
            "paragraph_breaks": text.count("\n\n"),
        },
        "issues": issues,
    }
