"""
Creative Quality Gate v1. Post-compile, read-only.
Runs after Stage 3 compile, before release-wave gating.
Evaluates fully assembled book with deterministic heuristics; returns PASS / WARN / FAIL.
No LLM scoring, no rewriting, no semantic embeddings.

CLI:
  PYTHONPATH=. python3 phoenix_v4/gates/check_creative_quality_v1.py \\
    --book artifacts/book_002.plan.json --config config/creative_quality_v1.yaml --out-dir artifacts/ops

Exit codes: 0 PASS, 2 WARN, 1 FAIL.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

# --- Types ---
Overall = Literal["PASS", "WARN", "FAIL"]


@dataclass(frozen=True)
class Chapter:
    index: int
    text: str
    band: Optional[int] = None


@dataclass(frozen=True)
class ArcMotionResult:
    distinct_bands: int
    rises: int
    falls: int
    flat_segments: int
    status: Overall
    reasons: List[str]


@dataclass(frozen=True)
class TransformationResult:
    transformative_chapters: int
    total_chapters: int
    share: float
    status: Overall
    reasons: List[str]


@dataclass(frozen=True)
class SpecificityResult:
    abstract_dominant_chapters: int
    total_chapters: int
    share: float
    status: Overall
    reasons: List[str]


@dataclass(frozen=True)
class EndingStrengthResult:
    last_n: int
    compression_found: bool
    identity_found: bool
    action_found: bool
    status: Overall
    reasons: List[str]


@dataclass(frozen=True)
class LexicalRhythmResult:
    sentence_count: int
    avg_sentence_len: float
    std_sentence_len: float
    status: Overall
    reasons: List[str]


@dataclass(frozen=True)
class BookQualitySummary:
    schema_version: str
    book_id: str
    generated_at_utc: str
    overall: Overall
    signals: Dict[str, Any]
    warnings: List[str]
    fails: List[str]


# --- Sentence splitting ---
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", re.UNICODE)


# --- Transformation markers (case-insensitive, compiled once) ---
INSIGHT_MARKERS = [
    re.compile(r"\bI (?:realize|noticed|notice|understand|see|recognized|recognize)\b", re.I),
    re.compile(r"\byou (?:realize|notice|understand|see|recognize)\b", re.I),
    re.compile(r"\bwhat (?:I|you) didn['']t see\b", re.I),
    re.compile(r"\bthe truth is\b", re.I),
    re.compile(r"\bhere'?s what'?s happening\b", re.I),
]
REFRAME_PATTERNS = [
    re.compile(r"\bnot (?:because|that) .+? but\b", re.I),
    re.compile(r"\bI thought .+? but\b", re.I),
    re.compile(r"\bI used to think .+? now\b", re.I),
    re.compile(r"\bthis isn['']t .+? this is\b", re.I),
    re.compile(r"\binstead of .+?, (?:try|choose|practice)\b", re.I),
]
IDENTITY_PATTERNS = [
    re.compile(r"\byou are becoming\b", re.I),
    re.compile(r"\byou are no longer\b", re.I),
    re.compile(r"\bthis is who you are\b", re.I),
    re.compile(r"\byou can be the kind of person who\b", re.I),
    re.compile(r"\bfrom now on, you\b", re.I),
]

# --- Ending strength ---
ENDING_COMPRESSION = [
    re.compile(r"\bto sum up\b", re.I),
    re.compile(r"\bin summary\b", re.I),
    re.compile(r"\bwhat you learned\b", re.I),
    re.compile(r"\bthe key (?:idea|point) is\b", re.I),
    re.compile(r"\blet'?s bring this together\b", re.I),
]
ENDING_IDENTITY_EXTRA = [
    re.compile(r"\byou have changed\b", re.I),
    re.compile(r"\bthis is your new baseline\b", re.I),
]
ENDING_ACTION = [
    re.compile(r"\bstart (?:by|with)\b", re.I),
    re.compile(r"\btry this\b", re.I),
    re.compile(r"\bdo this today\b", re.I),
    re.compile(r"\byour next step is\b", re.I),
    re.compile(r"\bcommit to\b", re.I),
    re.compile(r"\bpractice this\b", re.I),
]

# --- Specificity ---
CONCRETE_MARKERS = [
    re.compile(
        r"\b(?:kitchen|bed|desk|phone|email|calendar|traffic|subway|meeting|boss|hospital|shift|rent|deadline)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:morning|night|3 a\.m\.|noon|yesterday|today|tomorrow|last week)\b",
        re.I,
    ),
    re.compile(r"\b(?:hands|chest|stomach|jaw|shoulders|breath)\b", re.I),
]
ABSTRACT_MARKERS = [
    re.compile(
        r"\b(?:energy|vibration|alignment|mindset|manifest|universe|purpose|journey)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:anxiety|stress|burnout|healing|growth|transformation)\b",
        re.I,
    ),
]


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(path: str) -> Dict[str, Any]:
    """Load creative_quality_v1 config from YAML. Returns nested creative_quality_v1 section or {}."""
    p = Path(path)
    if not p.is_absolute():
        p = REPO_ROOT / path
    data = _load_yaml(p)
    return (data.get("creative_quality_v1") or data) or {}


def load_book(book_path: str) -> Tuple[str, List[Chapter], List[int]]:
    """
    Load book JSON. Returns (book_id, chapters, dominant_band_sequence).
    Chapter text is taken from (in order):
      compiled_book.chapters[*].text
      chapters[*].prose
      compiled_chapters[*].text
    Band sequence from top-level dominant_band_sequence or per-chapter band.
    Raises ValueError with code BOOK_INPUT_INVALID if no chapter text found.
    """
    p = Path(book_path)
    if not p.is_absolute():
        p = REPO_ROOT / book_path
    if not p.exists():
        raise ValueError("BOOK_INPUT_INVALID: file not found")
    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    book_id = (
        data.get("book_id")
        or data.get("plan_id")
        or data.get("plan_hash")
        or str(p.stem)
    )

    # Resolve chapters with text
    chapters: List[Chapter] = []
    raw_chapters = None
    if "compiled_book" in data:
        raw_chapters = data["compiled_book"].get("chapters")
    if raw_chapters is None:
        raw_chapters = data.get("chapters")
    if raw_chapters is None:
        raw_chapters = data.get("compiled_chapters")

    if raw_chapters:
        for i, ch in enumerate(raw_chapters):
            if isinstance(ch, dict):
                text = ch.get("text") or ch.get("prose") or ""
                band = ch.get("band")
                if band is not None:
                    try:
                        band = int(band)
                    except (TypeError, ValueError):
                        band = None
            else:
                text = ""
                band = None
            chapters.append(Chapter(index=i, text=(text or "").strip(), band=band))

    if not chapters or not any(c.text for c in chapters):
        raise ValueError("BOOK_INPUT_INVALID: no chapter text found (tried compiled_book.chapters[].text, chapters[].prose, compiled_chapters[].text)")

    # Dominant band sequence
    band_seq: List[int] = []
    if "dominant_band_sequence" in data and isinstance(data["dominant_band_sequence"], list):
        for b in data["dominant_band_sequence"]:
            try:
                band_seq.append(int(b))
            except (TypeError, ValueError):
                pass
    if not band_seq and chapters:
        band_seq = [c.band for c in chapters if c.band is not None]

    return (book_id, chapters, band_seq)


def normalize_text(text: str) -> str:
    """Normalize whitespace for parsing."""
    if not text:
        return ""
    return " ".join(text.split())


def split_sentences(text: str, cfg: Dict[str, Any]) -> List[str]:
    """Split text into sentences. Drops sentences shorter than min_sentence_chars."""
    if not text:
        return []
    parsing = cfg.get("parsing") or {}
    min_chars = int(parsing.get("min_sentence_chars", 6))
    normalized = normalize_text(text)
    parts = SENTENCE_SPLIT_RE.split(normalized)
    return [s.strip() for s in parts if s.strip() and len(s.strip()) >= min_chars]


def count_regex_hits(text: str, patterns: List[re.Pattern]) -> int:
    """Count total regex matches in text (overlapping not double-counted per pattern)."""
    total = 0
    for pat in patterns:
        total += len(pat.findall(text))
    return total


def has_any(text: str, patterns: List[re.Pattern]) -> bool:
    """True if any pattern matches in text."""
    for pat in patterns:
        if pat.search(text):
            return True
    return False


def evaluate_arc_motion(
    dominant_band_sequence: List[int],
    cfg: Dict[str, Any],
) -> ArcMotionResult:
    if not dominant_band_sequence:
        return ArcMotionResult(
            distinct_bands=0,
            rises=0,
            falls=0,
            flat_segments=0,
            status="FAIL",
            reasons=["MISSING_BAND_SEQUENCE"],
        )
    arc_cfg = cfg.get("arc_motion") or {}
    min_distinct = int(arc_cfg.get("min_distinct_bands", 3))
    require_rise = arc_cfg.get("require_rise", True)
    require_fall = arc_cfg.get("require_fall", True)
    warn_flat_over = int(arc_cfg.get("warn_flat_segments_over", 2))

    reasons: List[str] = []
    distinct_bands = len(set(dominant_band_sequence))
    rises = sum(1 for i in range(1, len(dominant_band_sequence)) if dominant_band_sequence[i] > dominant_band_sequence[i - 1])
    falls = sum(1 for i in range(1, len(dominant_band_sequence)) if dominant_band_sequence[i] < dominant_band_sequence[i - 1])

    flat_segments = 0
    i = 0
    while i < len(dominant_band_sequence):
        j = i + 1
        while j < len(dominant_band_sequence) and dominant_band_sequence[j] == dominant_band_sequence[i]:
            j += 1
        if j - i >= 2:
            flat_segments += 1
        i = j

    status: Overall = "PASS"
    if distinct_bands < min_distinct:
        reasons.append(f"distinct_bands={distinct_bands} < {min_distinct}")
        status = "FAIL"
    if require_rise and rises == 0 and len(dominant_band_sequence) > 1:
        reasons.append("no rising transition")
        status = "FAIL"
    if require_fall and falls == 0 and len(dominant_band_sequence) > 1:
        reasons.append("no falling transition")
        status = "FAIL"
    if status == "PASS" and flat_segments > warn_flat_over:
        reasons.append(f"flat_segments={flat_segments} > {warn_flat_over}")
        status = "WARN"

    return ArcMotionResult(
        distinct_bands=distinct_bands,
        rises=rises,
        falls=falls,
        flat_segments=flat_segments,
        status=status,
        reasons=reasons,
    )


def evaluate_transformation_density(
    chapters: List[Chapter],
    cfg: Dict[str, Any],
) -> TransformationResult:
    trans_cfg = cfg.get("transformation") or {}
    min_share = float(trans_cfg.get("min_transformative_chapter_share", 0.60))

    transformative = 0
    for ch in chapters:
        if not ch.text:
            continue
        if has_any(ch.text, INSIGHT_MARKERS):
            transformative += 1
            continue
        if has_any(ch.text, REFRAME_PATTERNS):
            transformative += 1
            continue
        if has_any(ch.text, IDENTITY_PATTERNS):
            transformative += 1
            continue
    total = len([c for c in chapters if c.text])
    total = total or 1
    share = transformative / total
    reasons: List[str] = []
    status: Overall = "PASS"
    if share < min_share:
        reasons.append(f"transformative_share={share:.2f} < {min_share}")
        status = "FAIL"
    return TransformationResult(
        transformative_chapters=transformative,
        total_chapters=len(chapters),
        share=round(share, 2),
        status=status,
        reasons=reasons,
    )


def evaluate_specificity(
    chapters: List[Chapter],
    cfg: Dict[str, Any],
) -> SpecificityResult:
    spec_cfg = cfg.get("specificity") or {}
    warn_share = float(spec_cfg.get("warn_abstract_dominant_share", 0.50))
    fail_share = float(spec_cfg.get("fail_abstract_dominant_share", 0.70))

    abstract_dominant_count = 0
    for ch in chapters:
        if not ch.text:
            continue
        concrete = count_regex_hits(ch.text, CONCRETE_MARKERS)
        abstract = count_regex_hits(ch.text, ABSTRACT_MARKERS)
        if abstract >= concrete + 2:
            abstract_dominant_count += 1
    total = len([c for c in chapters if c.text])
    total = total or 1
    share = abstract_dominant_count / total
    reasons: List[str] = []
    status: Overall = "PASS"
    if share >= fail_share:
        reasons.append(f"abstract_dominant_share={share:.2f} >= {fail_share}")
        status = "FAIL"
    elif share >= warn_share:
        reasons.append(f"abstract_dominant_share={share:.2f} >= {warn_share}")
        status = "WARN"
    return SpecificityResult(
        abstract_dominant_chapters=abstract_dominant_count,
        total_chapters=len(chapters),
        share=round(share, 2),
        status=status,
        reasons=reasons,
    )


def evaluate_ending_strength(
    chapters: List[Chapter],
    cfg: Dict[str, Any],
) -> EndingStrengthResult:
    end_cfg = cfg.get("ending_strength") or {}
    last_n = int(end_cfg.get("last_n_chapters", 2))
    require_compression = end_cfg.get("require_compression", True)
    require_identity = end_cfg.get("require_identity", True)
    require_action = end_cfg.get("require_action", True)

    if not chapters or last_n <= 0:
        return EndingStrengthResult(
            last_n=last_n,
            compression_found=False,
            identity_found=False,
            action_found=False,
            status="FAIL",
            reasons=["no chapters or last_n <= 0"],
        )
    tail = chapters[-last_n:]
    combined = " ".join(c.text for c in tail if c.text)
    compression_found = has_any(combined, ENDING_COMPRESSION)
    identity_found = has_any(combined, IDENTITY_PATTERNS) or has_any(combined, ENDING_IDENTITY_EXTRA)
    action_found = has_any(combined, ENDING_ACTION)

    reasons: List[str] = []
    status: Overall = "PASS"
    if require_compression and not compression_found:
        reasons.append("compression marker missing in last N chapters")
        status = "FAIL"
    if require_identity and not identity_found:
        reasons.append("identity marker missing in last N chapters")
        status = "FAIL"
    if require_action and not action_found:
        reasons.append("action directive missing in last N chapters")
        status = "FAIL"
    return EndingStrengthResult(
        last_n=last_n,
        compression_found=compression_found,
        identity_found=identity_found,
        action_found=action_found,
        status=status,
        reasons=reasons,
    )


def evaluate_lexical_rhythm(
    chapters: List[Chapter],
    cfg: Dict[str, Any],
) -> LexicalRhythmResult:
    rhythm_cfg = cfg.get("lexical_rhythm") or {}
    warn_std_below = float(rhythm_cfg.get("warn_sentence_len_std_below", 4.0))
    fail_std_below = float(rhythm_cfg.get("fail_sentence_len_std_below", 2.5))

    all_lengths: List[float] = []
    for ch in chapters:
        for s in split_sentences(ch.text, cfg):
            all_lengths.append(len(s.split()))
    if not all_lengths:
        all_lengths = [0.0]
    avg = statistics.mean(all_lengths)
    std = statistics.stdev(all_lengths) if len(all_lengths) > 1 else 0.0
    reasons: List[str] = []
    status: Overall = "PASS"
    if std < fail_std_below:
        reasons.append(f"sentence_len_std={std:.2f} < {fail_std_below}")
        status = "FAIL"
    elif std < warn_std_below:
        reasons.append(f"sentence_len_std={std:.2f} < {warn_std_below}")
        status = "WARN"
    return LexicalRhythmResult(
        sentence_count=len(all_lengths),
        avg_sentence_len=round(avg, 2),
        std_sentence_len=round(std, 2),
        status=status,
        reasons=reasons,
    )


def evaluate_book(
    book_id: str,
    chapters: List[Chapter],
    dominant_band_sequence: List[int],
    cfg: Dict[str, Any],
) -> BookQualitySummary:
    """Run all five signal evaluators and compute overall PASS/WARN/FAIL."""
    arc = evaluate_arc_motion(dominant_band_sequence, cfg)
    trans = evaluate_transformation_density(chapters, cfg)
    spec = evaluate_specificity(chapters, cfg)
    ending = evaluate_ending_strength(chapters, cfg)
    rhythm = evaluate_lexical_rhythm(chapters, cfg)

    signals = {
        "arc_motion": {
            "distinct_bands": arc.distinct_bands,
            "rises": arc.rises,
            "falls": arc.falls,
            "flat_segments": arc.flat_segments,
            "status": arc.status,
            "reasons": arc.reasons,
        },
        "transformation": {
            "transformative_chapters": trans.transformative_chapters,
            "total_chapters": trans.total_chapters,
            "share": trans.share,
            "status": trans.status,
            "reasons": trans.reasons,
        },
        "specificity": {
            "abstract_dominant_chapters": spec.abstract_dominant_chapters,
            "total_chapters": spec.total_chapters,
            "share": spec.share,
            "status": spec.status,
            "reasons": spec.reasons,
        },
        "ending_strength": {
            "last_n": ending.last_n,
            "compression_found": ending.compression_found,
            "identity_found": ending.identity_found,
            "action_found": ending.action_found,
            "status": ending.status,
            "reasons": ending.reasons,
        },
        "lexical_rhythm": {
            "sentence_count": rhythm.sentence_count,
            "avg_sentence_len": rhythm.avg_sentence_len,
            "std_sentence_len": rhythm.std_sentence_len,
            "status": rhythm.status,
            "reasons": rhythm.reasons,
        },
    }

    fails: List[str] = []
    warnings: List[str] = []
    for name, sig in [
        ("arc_motion", arc),
        ("transformation", trans),
        ("specificity", spec),
        ("ending_strength", ending),
        ("lexical_rhythm", rhythm),
    ]:
        if sig.status == "FAIL":
            fails.extend([f"{name}: {r}" for r in sig.reasons])
        elif sig.status == "WARN":
            warnings.extend([f"{name}: {r}" for r in sig.reasons])

    if fails:
        overall: Overall = "FAIL"
    elif len(warnings) >= 2:
        overall = "WARN"
    else:
        overall = "PASS"

    return BookQualitySummary(
        schema_version="1.0",
        book_id=book_id,
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        overall=overall,
        signals=signals,
        warnings=warnings,
        fails=fails,
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Creative Quality Gate v1 — post-compile, read-only, deterministic heuristics",
    )
    ap.add_argument("--book", required=True, help="Path to compiled book JSON")
    ap.add_argument(
        "--config",
        default="config/creative_quality_v1.yaml",
        help="Path to creative_quality_v1 config YAML",
    )
    ap.add_argument(
        "--out-dir",
        default="artifacts/ops",
        help="Directory for book_quality_summary JSON (and optional MD)",
    )
    ap.add_argument("--md", action="store_true", help="Also write a .md summary")
    args = ap.parse_args()

    cfg = load_config(args.config)
    try:
        book_id, chapters, band_seq = load_book(args.book)
    except ValueError as e:
        msg = str(e)
        if "BOOK_INPUT_INVALID" in msg:
            print(msg, file=sys.stderr)
            return 1
        raise

    summary = evaluate_book(book_id, chapters, band_seq, cfg)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    date_suffix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_json = out_dir / f"book_quality_summary_{summary.book_id}_{date_suffix}.json"
    out_json.write_text(json.dumps(summary_to_dict(summary), indent=2), encoding="utf-8")
    if args.md:
        out_md = out_dir / f"book_quality_summary_{summary.book_id}_{date_suffix}.md"
        out_md.write_text(summary_to_md(summary), encoding="utf-8")

    print(summary.overall)
    if summary.fails:
        for f in summary.fails:
            print(f"  FAIL: {f}", file=sys.stderr)
    if summary.warnings:
        for w in summary.warnings:
            print(f"  WARN: {w}", file=sys.stderr)

    if summary.overall == "FAIL":
        return 1
    if summary.overall == "WARN":
        return 2
    return 0


def summary_to_dict(s: BookQualitySummary) -> Dict[str, Any]:
    """Serialize BookQualitySummary to JSON-serializable dict."""
    return {
        "schema_version": s.schema_version,
        "book_id": s.book_id,
        "generated_at_utc": s.generated_at_utc,
        "overall": s.overall,
        "signals": s.signals,
        "warnings": s.warnings,
        "fails": s.fails,
    }


def summary_to_md(s: BookQualitySummary) -> str:
    """Write a short markdown summary."""
    lines = [
        f"# Book Quality Summary — {s.book_id}",
        f"**Generated:** {s.generated_at_utc}",
        f"**Overall:** {s.overall}",
        "",
        "## Signals",
    ]
    for name, sig in s.signals.items():
        lines.append(f"- **{name}:** {sig.get('status', '')} {sig.get('reasons', [])}")
    if s.fails:
        lines.append("")
        lines.append("## Fails")
        for f in s.fails:
            lines.append(f"- {f}")
    if s.warnings:
        lines.append("")
        lines.append("## Warnings")
        for w in s.warnings:
            lines.append(f"- {w}")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
