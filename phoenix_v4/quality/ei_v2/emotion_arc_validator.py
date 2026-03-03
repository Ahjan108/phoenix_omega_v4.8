"""
Emotion arc validation for EI V2.

Validates that rendered chapter prose actually delivers the intended
emotional trajectory from the arc blueprint. Bridges the gap between
structural arc rules (BAND values, emotional_role) and prose reality.

Uses a valence/arousal lexicon to estimate the emotional state of each
paragraph, then compares the trajectory to the arc intent.

Modes:
  - "lexicon": Built-in valence/arousal word lists. Zero dependencies.
  - "model": Classification via external model callback (future).
"""
from __future__ import annotations

import re
import statistics
from typing import Any, Dict, List, Optional


# Valence lexicon: word -> valence score in [-1, +1].
# Negative = distress/activation; Positive = relief/resolution.
# Calibrated for therapeutic self-help prose.
_VALENCE_LEXICON: Dict[str, float] = {
    # Negative valence (distress, activation, recognition)
    "panic": -0.8, "dread": -0.7, "terror": -0.8, "fear": -0.6,
    "anxiety": -0.5, "anxious": -0.5, "overwhelm": -0.6, "overwhelmed": -0.6,
    "shame": -0.7, "guilt": -0.5, "anger": -0.5, "rage": -0.7,
    "grief": -0.6, "loss": -0.4, "pain": -0.5, "hurt": -0.5,
    "lonely": -0.5, "alone": -0.4, "trapped": -0.6, "stuck": -0.4,
    "numb": -0.4, "empty": -0.5, "exhausted": -0.5, "burned": -0.4,
    "spiral": -0.5, "collapse": -0.6, "breaking": -0.5, "broken": -0.5,
    "failing": -0.5, "failed": -0.4, "worthless": -0.7, "hopeless": -0.7,
    "tight": -0.3, "tension": -0.3, "clenched": -0.4, "racing": -0.4,
    "shaking": -0.4, "trembling": -0.4, "sweating": -0.3, "cold": -0.2,
    "alarm": -0.4, "threat": -0.5, "danger": -0.5, "crisis": -0.5,
    # Neutral-low (mechanism/observation)
    "notice": 0.0, "observe": 0.0, "pattern": 0.0, "mechanism": 0.0,
    "automatic": -0.1, "habit": -0.1, "loop": -0.2, "repeat": -0.1,
    "signal": 0.0, "response": 0.0, "trigger": -0.2, "reaction": -0.1,
    # Transition (turning/shifting)
    "but": 0.0, "however": 0.0, "shift": 0.1, "change": 0.1,
    "different": 0.1, "new": 0.1, "instead": 0.1, "pause": 0.1,
    "slow": 0.1, "wait": 0.0, "choose": 0.2, "choice": 0.2,
    # Positive valence (relief, resolution, agency)
    "breath": 0.2, "breathe": 0.3, "exhale": 0.3, "release": 0.3,
    "soften": 0.3, "settle": 0.3, "ease": 0.3, "calm": 0.4,
    "ground": 0.2, "grounded": 0.3, "anchor": 0.2, "steady": 0.3,
    "safe": 0.4, "safety": 0.4, "trust": 0.3, "held": 0.3,
    "courage": 0.4, "strength": 0.3, "resilience": 0.3, "capable": 0.3,
    "clarity": 0.4, "clear": 0.3, "understand": 0.2, "insight": 0.3,
    "agency": 0.4, "reclaim": 0.3, "rebuild": 0.3, "recover": 0.3,
    "forward": 0.3, "momentum": 0.3, "progress": 0.3, "growth": 0.3,
    "worth": 0.3, "enough": 0.3, "whole": 0.4, "real": 0.2,
    "acceptance": 0.4, "compassion": 0.4, "kindness": 0.4, "gentle": 0.3,
}

# Arousal lexicon: word -> arousal score in [0, 1].
# High = intense/activated; Low = calm/reflective.
_AROUSAL_LEXICON: Dict[str, float] = {
    "panic": 0.9, "racing": 0.8, "terror": 0.9, "rage": 0.8,
    "scream": 0.8, "slam": 0.7, "sprint": 0.7, "shaking": 0.7,
    "crisis": 0.7, "alarm": 0.7, "emergency": 0.8, "collapse": 0.7,
    "confront": 0.6, "fight": 0.7, "flee": 0.7, "freeze": 0.5,
    "breath": 0.2, "breathe": 0.2, "exhale": 0.2, "whisper": 0.2,
    "gentle": 0.1, "soft": 0.1, "quiet": 0.1, "still": 0.1,
    "calm": 0.1, "slow": 0.2, "settle": 0.2, "rest": 0.1,
    "notice": 0.2, "observe": 0.2, "pause": 0.2, "reflect": 0.2,
}

# Expected emotional trajectory patterns by arc BAND value.
# BAND 1 = light recognition, BAND 4 = peak intensity/cost.
_BAND_VALENCE_EXPECTATIONS = {
    1: {"valence_range": (-0.1, 0.3), "description": "light recognition, mild positive"},
    2: {"valence_range": (-0.3, 0.1), "description": "recognition, mechanism naming"},
    3: {"valence_range": (-0.5, -0.1), "description": "activation, cost, turning point"},
    4: {"valence_range": (-0.7, -0.3), "description": "peak intensity, deep cost"},
}

# Expected trajectory by emotional_role.
_ROLE_VALENCE_EXPECTATIONS = {
    "RECOGNITION": {"expected_start": (-0.3, 0.0), "expected_end": (-0.2, 0.1)},
    "MECHANISM_PROOF": {"expected_start": (-0.4, -0.1), "expected_end": (-0.3, 0.0)},
    "TURNING_POINT": {"expected_start": (-0.5, -0.2), "expected_end": (-0.1, 0.2)},
    "EMBODIMENT": {"expected_start": (-0.2, 0.1), "expected_end": (0.1, 0.4)},
}


def _paragraph_valence(paragraph: str) -> float:
    """Compute average valence for a paragraph."""
    words = re.findall(r"\b\w+\b", paragraph.lower())
    scores = [_VALENCE_LEXICON[w] for w in words if w in _VALENCE_LEXICON]
    if not scores:
        return 0.0
    return statistics.mean(scores)


def _paragraph_arousal(paragraph: str) -> float:
    """Compute average arousal for a paragraph."""
    words = re.findall(r"\b\w+\b", paragraph.lower())
    scores = [_AROUSAL_LEXICON[w] for w in words if w in _AROUSAL_LEXICON]
    if not scores:
        return 0.3  # default moderate
    return statistics.mean(scores)


def _split_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def validate_emotion_arc(
    chapter_text: str,
    arc_intent: Dict[str, Any],
    *,
    cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Validate that chapter prose matches arc intent.

    arc_intent: {"band": int, "emotional_role": str, "chapter_index": int}
    Returns validation result with metrics, warnings, and pass/fail status.
    """
    cfg = cfg or {}
    warn_threshold = float(cfg.get("arc_deviation_warn", 0.3))
    fail_threshold = float(cfg.get("arc_deviation_fail", 0.6))

    paragraphs = _split_paragraphs(chapter_text)
    if not paragraphs:
        return {
            "status": "SKIP",
            "reason": "no_paragraphs",
            "metrics": {},
        }

    # Compute per-paragraph valence and arousal
    valences = [_paragraph_valence(p) for p in paragraphs]
    arousals = [_paragraph_arousal(p) for p in paragraphs]
    avg_valence = statistics.mean(valences) if valences else 0.0
    avg_arousal = statistics.mean(arousals) if arousals else 0.3

    # Trajectory: valence of first third vs last third
    third = max(1, len(valences) // 3)
    start_valence = statistics.mean(valences[:third])
    end_valence = statistics.mean(valences[-third:])
    trajectory = end_valence - start_valence  # positive = relief arc, negative = darkening

    band = arc_intent.get("band")
    emotional_role = arc_intent.get("emotional_role", "")
    warnings: List[str] = []
    errors: List[str] = []

    # Check against BAND expectations
    band_deviation = 0.0
    if band and band in _BAND_VALENCE_EXPECTATIONS:
        expected = _BAND_VALENCE_EXPECTATIONS[band]
        lo, hi = expected["valence_range"]
        if avg_valence < lo:
            band_deviation = abs(avg_valence - lo)
        elif avg_valence > hi:
            band_deviation = abs(avg_valence - hi)

        if band_deviation >= fail_threshold:
            errors.append(
                f"band_{band}_valence_deviation: avg={avg_valence:.2f}, "
                f"expected=[{lo}, {hi}], deviation={band_deviation:.2f}"
            )
        elif band_deviation >= warn_threshold:
            warnings.append(
                f"band_{band}_valence_drift: avg={avg_valence:.2f}, "
                f"expected=[{lo}, {hi}], deviation={band_deviation:.2f}"
            )

    # Check trajectory against emotional_role expectations
    role_deviation = 0.0
    role_upper = emotional_role.upper()
    if role_upper in _ROLE_VALENCE_EXPECTATIONS:
        exp = _ROLE_VALENCE_EXPECTATIONS[role_upper]
        start_lo, start_hi = exp["expected_start"]
        end_lo, end_hi = exp["expected_end"]

        start_dev = max(0, start_lo - start_valence, start_valence - start_hi)
        end_dev = max(0, end_lo - end_valence, end_valence - end_hi)
        role_deviation = (start_dev + end_dev) / 2

        if role_deviation >= fail_threshold:
            errors.append(
                f"role_{role_upper}_trajectory_deviation: "
                f"start={start_valence:.2f}, end={end_valence:.2f}, deviation={role_deviation:.2f}"
            )
        elif role_deviation >= warn_threshold:
            warnings.append(
                f"role_{role_upper}_trajectory_drift: "
                f"start={start_valence:.2f}, end={end_valence:.2f}, deviation={role_deviation:.2f}"
            )

    # Flatness detection: if variance is too low, prose may be emotionally monotone
    if len(valences) >= 3:
        valence_variance = statistics.variance(valences)
        if valence_variance < 0.01:
            warnings.append(f"emotional_flatness: variance={valence_variance:.4f}")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "avg_valence": round(avg_valence, 4),
            "avg_arousal": round(avg_arousal, 4),
            "start_valence": round(start_valence, 4),
            "end_valence": round(end_valence, 4),
            "trajectory": round(trajectory, 4),
            "valence_variance": round(statistics.variance(valences), 4) if len(valences) >= 2 else 0.0,
            "paragraph_count": len(paragraphs),
            "band": band,
            "emotional_role": emotional_role,
            "band_deviation": round(band_deviation, 4),
            "role_deviation": round(role_deviation, 4),
        },
    }
