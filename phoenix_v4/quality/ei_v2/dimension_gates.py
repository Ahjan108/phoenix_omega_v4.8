"""
Dimension Enforcement Gates — per-chapter quality minimums.

Enforces hard floors on the weakest quality dimensions:
  UNIQUENESS  — dedup caps per chapter/book, banned repeated structures
  ENGAGEMENT  — hook density, tension markers, chapter-end pull-forward
  SOMATIC     — body-signal atoms per chapter, somatic lexicon minimums
  LISTEN      — TTS readability floor
  COHESION    — cross-chapter thread reference minimum

Each gate returns PASS/WARN/FAIL with specific issues and remediation hints.
Gates are config-driven so thresholds can be tuned by the learner.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class DimensionGateBlockError(Exception):
    """Raised when fail_mode=block and a dimension gate fails."""

    def __init__(self, report: "ChapterGateReport", message: str = ""):
        self.report = report
        super().__init__(message or f"Dimension gate FAIL (chapter {report.chapter_index}): {report.fail_count} gate(s) failed")


@dataclass
class GateResult:
    dimension: str
    status: str  # PASS, WARN, FAIL
    score: float = 0.0
    threshold_pass: float = 0.0
    threshold_warn: float = 0.0
    issues: List[str] = field(default_factory=list)
    remediation: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "status": self.status,
            "score": round(self.score, 4),
            "threshold_pass": self.threshold_pass,
            "threshold_warn": self.threshold_warn,
            "issues": self.issues,
            "remediation": self.remediation,
        }


@dataclass
class ChapterGateReport:
    chapter_index: int
    gates: List[GateResult] = field(default_factory=list)
    overall_status: str = "PASS"
    fail_count: int = 0
    warn_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_index": self.chapter_index,
            "overall_status": self.overall_status,
            "fail_count": self.fail_count,
            "warn_count": self.warn_count,
            "gates": [g.to_dict() for g in self.gates],
        }


# ── Somatic lexicon ──

_SOMATIC_WORDS = frozenset({
    "shoulder", "shoulders", "breath", "breathing", "inhale", "exhale",
    "stomach", "gut", "jaw", "chest", "heart", "racing", "tight",
    "tighten", "tightens", "tightened", "tensed", "tension", "clench",
    "clenched", "relax", "release", "loosen", "ground", "grounded",
    "body", "sensation", "hands", "fists", "throat", "pulse", "heat",
    "cold", "sweat", "sweating", "shaking", "trembling", "nausea",
    "dizzy", "lightheaded", "spine", "belly", "rib", "ribs", "muscles",
    "face", "forehead", "temples", "neck", "lungs", "knees", "skin",
})

# ── Engagement patterns ──

_HOOK_PATTERNS = [
    re.compile(r"\b(?:that\s+(?:morning|night|moment|day)|one\s+(?:morning|night|day))\b", re.I),
    re.compile(r"\b(?:you'?ve\s+(?:been|done|felt|noticed|tried)|you\s+(?:know|remember|feel))\b", re.I),
    re.compile(r"\b(?:here'?s\s+(?:the|what)|what\s+(?:if|happens|nobody))\b", re.I),
    re.compile(r"\b(?:imagine|picture\s+this|consider)\b", re.I),
]

_TENSION_MARKERS = [
    re.compile(r"\b(?:but\s+then|until|except|and\s+then|still|yet|however)\b", re.I),
    re.compile(r"\b(?:not\s+because|not\s+yet|not\s+quite|almost|nearly)\b", re.I),
    re.compile(r"\b(?:the\s+problem|the\s+catch|the\s+twist|the\s+thing\s+is)\b", re.I),
]

_PULL_FORWARD_PATTERNS = [
    re.compile(r"\b(?:next|what\s+comes\s+next|in\s+the\s+next\s+chapter)\b", re.I),
    re.compile(r"\b(?:there\s+is\s+(?:something|more)|we'?re\s+(?:not\s+)?done)\b", re.I),
    re.compile(r"\b(?:but\s+first|before\s+(?:we|you)\s+(?:go|move)|stay\s+with)\b", re.I),
    re.compile(r"\b(?:what\s+you'?ll\s+(?:discover|learn|see|find)|ready\s+for)\b", re.I),
]

# ── Cohesion patterns ──

_COHESION_MARKERS = [
    re.compile(r"\b(?:remember\s+(?:when|the|that|how)|earlier|as\s+we\s+(?:saw|discussed|noticed))\b", re.I),
    re.compile(r"\b(?:this\s+pattern|the\s+same\s+(?:thing|pattern|alarm)|again|once\s+more)\b", re.I),
    re.compile(r"\b(?:back\s+in\s+chapter|we\s+(?:talked|spoke)\s+about|you\s+(?:already|may)\s+recall)\b", re.I),
]

# ── Banned repeated structures ──

_REPEATED_STRUCTURE_PATTERNS = [
    re.compile(r"^(?:You\s+(?:know|remember|feel))\b", re.M),
    re.compile(r"^(?:Here'?s\s+(?:the|what))\b", re.M),
    re.compile(r"^(?:Let\s+me\s+(?:tell|ask|explain))\b", re.M),
]


def _hits(text: str, patterns: list) -> int:
    return sum(1 for p in patterns if p.search(text))


def _wc(text: str) -> int:
    return len(text.split())


def _somatic_count(text: str) -> int:
    words = set(re.findall(r"\b\w+\b", text.lower()))
    return len(words & _SOMATIC_WORDS)


def _last_paragraph(text: str) -> str:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paras[-1] if paras else ""


# ── Gate implementations ──

def gate_uniqueness(
    chapter_text: str,
    all_chapter_texts: List[str],
    chapter_index: int,
    cfg: Optional[Dict[str, Any]] = None,
) -> GateResult:
    """Uniqueness gate: dedup caps per chapter."""
    cfg = cfg or {}
    from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates

    pass_threshold = float(cfg.get("pass_threshold", 0.15))
    warn_threshold = float(cfg.get("warn_threshold", 0.30))
    max_structural_repeats = int(cfg.get("max_structural_repeats_per_chapter", 2))

    result = GateResult(
        dimension="uniqueness",
        status="PASS",
        threshold_pass=pass_threshold,
        threshold_warn=warn_threshold,
    )

    if len(all_chapter_texts) > 1:
        others = [(i, t) for i, t in enumerate(all_chapter_texts) if i != chapter_index and t.strip()]
        if others:
            texts = [chapter_text] + [t for _, t in others]
            ids = [f"ch{chapter_index}"] + [f"ch{i}" for i, _ in others]
            dupes = detect_semantic_duplicates(texts, ids)
            max_sim = max(
                (float(d.get("similarity", 0.0)) for d in dupes if isinstance(d, dict)),
                default=0.0,
            )
            result.score = max(0.0, 1.0 - max_sim * 2)

            if max_sim > warn_threshold:
                result.status = "FAIL"
                result.issues.append(f"max_dedup_similarity={max_sim:.3f} exceeds {warn_threshold}")
                result.remediation.append("Replace duplicated atoms or rewrite chapter content")
            elif max_sim > pass_threshold:
                result.status = "WARN"
                result.issues.append(f"dedup_similarity={max_sim:.3f} approaching threshold")
        else:
            result.score = 1.0
    else:
        result.score = 1.0

    repeat_count = sum(
        len(p.findall(chapter_text))
        for p in _REPEATED_STRUCTURE_PATTERNS
    )
    if repeat_count > max_structural_repeats:
        if result.status == "PASS":
            result.status = "WARN"
        result.issues.append(f"repeated_structures={repeat_count} > cap {max_structural_repeats}")
        result.remediation.append("Vary chapter opening patterns")

    return result


def gate_engagement(
    chapter_text: str,
    chapter_index: int,
    cfg: Optional[Dict[str, Any]] = None,
) -> GateResult:
    """Engagement gate: hook density, tension, pull-forward."""
    cfg = cfg or {}
    min_hooks = int(cfg.get("min_hooks_per_chapter", 1))
    min_tension = int(cfg.get("min_tension_markers", 2))
    require_pull_forward = cfg.get("require_pull_forward", True)
    pass_score = float(cfg.get("pass_threshold", 0.35))
    warn_score = float(cfg.get("warn_threshold", 0.20))

    result = GateResult(
        dimension="engagement",
        status="PASS",
        threshold_pass=pass_score,
        threshold_warn=warn_score,
    )

    wc = _wc(chapter_text)
    if wc < 20:
        result.score = 0.0
        result.status = "FAIL"
        result.issues.append("chapter too short for engagement analysis")
        return result

    hook_hits = _hits(chapter_text, _HOOK_PATTERNS)
    tension_hits = _hits(chapter_text, _TENSION_MARKERS)
    last_para = _last_paragraph(chapter_text)
    pull_forward_hits = _hits(last_para, _PULL_FORWARD_PATTERNS)

    result.score = min(1.0,
        0.35 * min(1.0, hook_hits / max(1, min_hooks))
        + 0.40 * min(1.0, tension_hits / max(1, min_tension))
        + 0.25 * min(1.0, pull_forward_hits / 1.0))

    if hook_hits < min_hooks:
        result.issues.append(f"hooks={hook_hits} < min {min_hooks}")
        result.remediation.append("Add a recognition hook or scene-setting opener in first paragraph")

    if tension_hits < min_tension:
        result.issues.append(f"tension_markers={tension_hits} < min {min_tension}")
        result.remediation.append("Add narrative tension (but then, until, the catch is)")

    if require_pull_forward and pull_forward_hits < 1:
        result.issues.append("no pull-forward line in final paragraph")
        result.remediation.append("End chapter with forward momentum (what comes next, stay with this)")

    if result.score < warn_score:
        result.status = "FAIL"
    elif result.score < pass_score:
        result.status = "WARN"

    return result


def gate_somatic_precision(
    chapter_text: str,
    cfg: Optional[Dict[str, Any]] = None,
) -> GateResult:
    """Somatic precision gate: body-signal minimums."""
    cfg = cfg or {}
    min_somatic_words = int(cfg.get("min_somatic_words_per_chapter", 3))
    min_density = float(cfg.get("min_somatic_density_per_100w", 1.5))
    pass_score = float(cfg.get("pass_threshold", 0.40))
    warn_score = float(cfg.get("warn_threshold", 0.25))

    result = GateResult(
        dimension="somatic_precision",
        status="PASS",
        threshold_pass=pass_score,
        threshold_warn=warn_score,
    )

    wc = _wc(chapter_text)
    somatic_n = _somatic_count(chapter_text)
    density = somatic_n / max(1.0, wc / 100.0)

    result.score = min(1.0, 0.5 * min(1.0, somatic_n / max(1, min_somatic_words))
                       + 0.5 * min(1.0, density / min_density))

    if somatic_n < min_somatic_words:
        result.issues.append(f"somatic_words={somatic_n} < min {min_somatic_words}")
        result.remediation.append("Add body-grounded language (shoulder tension, chest tightness, breath changes)")

    if density < min_density:
        result.issues.append(f"somatic_density={density:.2f}/100w < min {min_density}")
        result.remediation.append("Increase body-signal frequency throughout chapter")

    if result.score < warn_score:
        result.status = "FAIL"
    elif result.score < pass_score:
        result.status = "WARN"

    return result


def gate_listen_experience(
    chapter_text: str,
    cfg: Optional[Dict[str, Any]] = None,
) -> GateResult:
    """Listen experience gate: TTS readability floor."""
    cfg = cfg or {}
    from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability

    pass_score = float(cfg.get("pass_threshold", 0.55))
    warn_score = float(cfg.get("warn_threshold", 0.40))

    tts = score_tts_readability(chapter_text)
    score = float(tts.get("composite", 0.5)) if isinstance(tts, dict) else 0.5

    result = GateResult(
        dimension="listen_experience",
        status="PASS",
        score=score,
        threshold_pass=pass_score,
        threshold_warn=warn_score,
    )

    if score < warn_score:
        result.status = "FAIL"
        if isinstance(tts, dict):
            result.issues.extend((tts.get("issues") or [])[:3])
        result.remediation.append("Shorten long sentences, add paragraph breaks, vary rhythm")
    elif score < pass_score:
        result.status = "WARN"
        if isinstance(tts, dict):
            result.issues.extend((tts.get("issues") or [])[:2])

    return result


def gate_cohesion(
    chapter_text: str,
    chapter_index: int,
    cfg: Optional[Dict[str, Any]] = None,
) -> GateResult:
    """Cohesion gate: cross-chapter thread references."""
    cfg = cfg or {}
    min_references = int(cfg.get("min_cross_chapter_refs", 1))
    pass_score = float(cfg.get("pass_threshold", 0.40))
    warn_score = float(cfg.get("warn_threshold", 0.25))

    result = GateResult(
        dimension="cohesion",
        status="PASS",
        threshold_pass=pass_score,
        threshold_warn=warn_score,
    )

    if chapter_index == 0:
        result.score = 0.5
        return result

    cohesion_hits = _hits(chapter_text, _COHESION_MARKERS)
    result.score = min(1.0, cohesion_hits / max(1, min_references + 1))

    if cohesion_hits < min_references:
        result.issues.append(f"cross_chapter_refs={cohesion_hits} < min {min_references}")
        result.remediation.append("Reference earlier chapter themes (remember when, as we saw, this pattern)")

    if result.score < warn_score:
        result.status = "FAIL"
    elif result.score < pass_score:
        result.status = "WARN"

    return result


def enforce_chapter_gates(
    chapter_text: str,
    chapter_index: int,
    all_chapter_texts: List[str],
    cfg: Optional[Dict[str, Any]] = None,
) -> ChapterGateReport:
    """
    Run all dimension gates on a single chapter.

    When cfg.fail_mode == "block" and any gate fails, raises DimensionGateBlockError.
    When cfg.fail_mode == "warn" (default), returns report without raising.
    """
    cfg = cfg or {}
    fail_mode = str(cfg.get("fail_mode", "warn")).lower()

    gates = [
        gate_uniqueness(chapter_text, all_chapter_texts, chapter_index,
                        cfg.get("uniqueness", {})),
        gate_engagement(chapter_text, chapter_index,
                        cfg.get("engagement", {})),
        gate_somatic_precision(chapter_text,
                               cfg.get("somatic_precision", {})),
        gate_listen_experience(chapter_text,
                               cfg.get("listen_experience", {})),
        gate_cohesion(chapter_text, chapter_index,
                      cfg.get("cohesion", {})),
    ]

    report = ChapterGateReport(chapter_index=chapter_index, gates=gates)
    for g in gates:
        if g.status == "FAIL":
            report.fail_count += 1
        elif g.status == "WARN":
            report.warn_count += 1

    if report.fail_count > 0:
        report.overall_status = "FAIL"
        if fail_mode == "block":
            failed_dims = [g.dimension for g in gates if g.status == "FAIL"]
            raise DimensionGateBlockError(
                report,
                f"Chapter {chapter_index}: {report.fail_count} gate(s) FAIL "
                f"({', '.join(failed_dims)}) — fail_mode=block"
            )
    elif report.warn_count > 0:
        report.overall_status = "WARN"

    return report
