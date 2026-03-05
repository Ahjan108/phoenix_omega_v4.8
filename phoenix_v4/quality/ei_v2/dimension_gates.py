"""
EI V2 dimension gates: per-chapter quality gates (uniqueness, engagement, somatic precision).
Used for chapter-level validation; fail-open by default.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, List

# Body-word set for somatic precision (align with ei_adapter)
BODY_WORDS = frozenset({
    "shoulder", "shoulders", "breath", "breathing", "stomach", "jaw", "chest",
    "heart", "racing", "tight", "tensed", "tension", "relax", "release",
    "ground", "grounded", "body", "sensation", "felt", "feeling",
})


@dataclass
class GateResult:
    dimension: str
    status: str  # PASS, WARN, FAIL
    score: float
    issues: List[str] = field(default_factory=list)
    remediation: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "status": self.status,
            "score": self.score,
            "issues": self.issues,
            "remediation": self.remediation,
        }


def gate_uniqueness(text: str, other_texts: List[str], chapter_index: int) -> GateResult:
    """Score uniqueness of this chapter text vs others (avoid duplicate phrasing)."""
    if not text or not text.strip():
        return GateResult("uniqueness", "WARN", 0.0, issues=["empty text"])
    text_lower = text.lower().strip()
    words = set(re.findall(r"\w+", text_lower))
    if len(words) < 5:
        return GateResult("uniqueness", "WARN", 0.5, issues=["very short text"])
    score = 1.0
    issues = []
    for other in other_texts:
        if not other:
            continue
        other_words = set(re.findall(r"\w+", other.lower()))
        overlap = len(words & other_words) / max(len(words), 1)
        if overlap > 0.7:
            score = min(score, 0.3)
            issues.append("high overlap with another chapter")
    status = "PASS" if score >= 0.6 else ("WARN" if score >= 0.3 else "FAIL")
    return GateResult("uniqueness", status, round(score, 3), issues=issues)


def gate_engagement(text: str, chapter_index: int) -> GateResult:
    """Minimum engagement: sentence variety and length."""
    if not text or not text.strip():
        return GateResult("engagement", "FAIL", 0.0, issues=["empty text", "too short"])
    text = text.strip()
    word_count = len(text.split())
    if word_count < 15:
        return GateResult(
            "engagement", "FAIL", 0.0,
            issues=["too short", f"word count {word_count} below minimum 15"],
        )
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) < 2:
        return GateResult("engagement", "WARN", 0.5, issues=["single sentence"])
    score = min(1.0, word_count / 80.0)
    status = "PASS" if score >= 0.5 else "WARN"
    return GateResult("engagement", status, round(score, 3))


def gate_somatic_precision(text: str) -> GateResult:
    """Body-word presence for somatic-heavy content."""
    if not text or not text.strip():
        return GateResult("somatic_precision", "WARN", 0.0, issues=["empty text"])
    text_lower = text.lower()
    words = set(re.findall(r"\w+", text_lower))
    body_hits = len(words & BODY_WORDS)
    score = min(1.0, body_hits / 4.0)
    if score < 0.2:
        return GateResult(
            "somatic_precision", "WARN" if score > 0 else "FAIL",
            round(score, 3),
            issues=["few or no body/sensation words"],
        )
    status = "PASS" if score >= 0.3 else "WARN"
    return GateResult("somatic_precision", status, round(score, 3))


@dataclass
class ChapterGateReport:
    chapter_index: int
    gates: List[GateResult]
    overall_status: str
    fail_count: int
    warn_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "chapter_index": self.chapter_index,
            "gates": [g.to_dict() for g in self.gates],
            "overall_status": self.overall_status,
            "fail_count": self.fail_count,
            "warn_count": self.warn_count,
        }
