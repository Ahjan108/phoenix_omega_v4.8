#!/usr/bin/env python3
"""
phoenix_v4/quality/memorable_line_detector.py

Deterministic sentence scanning to extract "memorable line candidates".
Heuristics: short declarative lines (8–20 words), contrast, identity phrases, reframe markers.

Input contract: Rendered .txt is preferred. Plan JSON is supported only when it contains
chapter text (compiled_book.chapters[].text). If plan has no chapter text, exits with
clear error: use Stage 6 rendered .txt.

Exit codes (phoenix_v4/quality/base): 0 success; 1 on input/parse error.

Usage:
  PYTHONPATH=. python3 phoenix_v4/quality/memorable_line_detector.py --file compiled.txt --json-out artifacts/ops/mem_lines.json
  PYTHONPATH=. python3 phoenix_v4/quality/memorable_line_detector.py --plan artifacts/book_002.plan.json --json-out artifacts/ops/mem_lines.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from phoenix_v4.quality.base import EXIT_FAIL, EXIT_PASS

WORD_RE = re.compile(r"\b[\w'']+\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")

# Heuristic patterns
CONTRAST = [
    r"\bnot\b.+?\bbut\b",
    r"\bthis isn['']t\b.+?\bthis is\b",
]
IDENTITY = [
    r"\byou are\b",
    r"\byou['']?re\b",
    r"\bthis is\b",
]
REFRAME = [
    r"\bactually\b",
    r"\bthe truth is\b",
    r"\binstead\b",
    r"\bwhat if\b",
]


@dataclass(frozen=True)
class LineCandidate:
    text: str
    chapter_index: int
    sentence_index: int
    word_count: int
    score: float
    tags: List[str]


def normalize_text(t: str) -> str:
    return t.replace("\r\n", "\n").replace("\r", "\n").strip()


def split_sentences(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    parts = SENTENCE_SPLIT_RE.split(text)
    out = []
    for s in parts:
        s = s.strip()
        if len(s) < 10:
            continue
        out.append(s)
    return out


def count_words(s: str) -> int:
    return len(WORD_RE.findall(s))


def hit_any(s: str, pats: List[str]) -> bool:
    flags = re.IGNORECASE | re.MULTILINE
    return any(re.search(p, s, flags) for p in pats)


def score_sentence(s: str) -> Tuple[float, List[str]]:
    wc = count_words(s)
    tags: List[str] = []
    score = 0.0

    if 8 <= wc <= 20:
        score += 2.0
        tags.append("LENGTH_GOOD")
    elif 6 <= wc <= 28:
        score += 1.0
        tags.append("LENGTH_OK")
    else:
        score -= 1.0
        tags.append("LENGTH_WEIRD")

    if hit_any(s, CONTRAST):
        score += 2.0
        tags.append("CONTRAST")
    if hit_any(s, IDENTITY):
        score += 1.5
        tags.append("IDENTITY")
    if hit_any(s, REFRAME):
        score += 1.5
        tags.append("REFRAME")

    if "?" in s:
        score -= 0.5
        tags.append("QUESTION")

    if wc > 28:
        score -= 0.5
        tags.append("LONG")

    return score, tags


def load_chapters_from_plan(plan_path: Path) -> Tuple[str, List[str]]:
    data = json.loads(plan_path.read_text(encoding="utf-8"))
    book_id = data.get("book_id") or data.get("plan_id") or data.get("id") or plan_path.stem

    chapters: List[str] = []
    if "compiled_book" in data and isinstance(data["compiled_book"], dict):
        for ch in data["compiled_book"].get("chapters", []):
            chapters.append(str(ch.get("text") or ch.get("prose") or ""))
    elif "chapters" in data and isinstance(data["chapters"], list):
        for ch in data["chapters"]:
            chapters.append(str(ch.get("text") or ch.get("prose") or ""))
    elif "compiled_chapters" in data and isinstance(data["compiled_chapters"], list):
        for ch in data["compiled_chapters"]:
            chapters.append(str(ch.get("text") or ch.get("prose") or ""))
    else:
        raise ValueError("PLAN_INPUT_INVALID: missing chapter texts")

    chapters = [normalize_text(c) for c in chapters if normalize_text(c)]
    if not chapters:
        raise ValueError(
            "PLAN_INPUT_INVALID: Plan JSON has no chapter text. "
            "Use a rendered .txt file (Stage 6: run_pipeline --render-book or render_plan_to_txt.py) "
            "or ensure plan includes compiled_book.chapters[].text."
        )
    return book_id, chapters


CHAPTER_SPLIT_RE = re.compile(r"^\s*#+\s*chapter\b.*$", re.IGNORECASE | re.MULTILINE)


def load_chapters_from_file(path: Path) -> Tuple[str, List[str]]:
    text = normalize_text(path.read_text(encoding="utf-8", errors="replace"))
    if not text:
        raise ValueError("FILE_INPUT_INVALID: empty file")
    return path.stem, [text]


def load_chapters_from_rendered_file(path: Path) -> Tuple[str, List[str]]:
    """Load rendered .txt with chapter splits (same as transformation_heatmap)."""
    text = normalize_text(path.read_text(encoding="utf-8", errors="replace"))
    if not text:
        raise ValueError("FILE_INPUT_INVALID: empty file")
    splits = CHAPTER_SPLIT_RE.split(text)
    if len(splits) >= 2:
        chapters = [s.strip() for s in splits if s.strip()]
    else:
        chapters = [text]
    return path.stem, chapters


def detect_lines(
    book_id: str,
    chapters: List[str],
    min_score: float = 3.0,
    max_lines: int = 80,
) -> Dict:
    candidates: List[LineCandidate] = []

    total_words = sum(count_words(ch) for ch in chapters)

    for ci, ch in enumerate(chapters):
        sentences = split_sentences(ch)
        for si, s in enumerate(sentences):
            sc, tags = score_sentence(s)
            wc = count_words(s)
            if sc >= min_score:
                candidates.append(
                    LineCandidate(
                        text=s,
                        chapter_index=ci,
                        sentence_index=si,
                        word_count=wc,
                        score=sc,
                        tags=tags,
                    )
                )

    candidates.sort(key=lambda x: (-x.score, x.word_count, x.text))
    uniq: List[LineCandidate] = []
    seen = set()
    for c in candidates:
        t = c.text.strip()
        if t in seen:
            continue
        seen.add(t)
        uniq.append(c)
        if len(uniq) >= max_lines:
            break

    density = (len(uniq) / max(total_words, 1)) * 1000.0

    return {
        "schema_version": "1.0",
        "book_id": book_id,
        "total_words": total_words,
        "memorable_candidate_count": len(uniq),
        "highlight_density_per_1000_words": round(density, 3),
        "candidates": [asdict(u) for u in uniq],
    }


def run_memorable_from_path(
    path: Path,
    min_score: float = 3.0,
    max_lines: int = 80,
    strong_score_threshold: float = 5.0,
) -> dict:
    """
    Run memorable line detector from rendered text path. Returns bundle-shaped tool result
    for book_quality_bundle: status, metrics (memorable_line_count, strong_quote_count,
    quote_density_per_1k_words), lines (text, strength, chapter_index, tags).
    """
    book_id, chapters = load_chapters_from_rendered_file(path)
    raw = detect_lines(book_id, chapters, min_score=min_score, max_lines=max_lines)
    total_words = raw.get("total_words", 1)
    candidates = raw.get("candidates", [])
    memorable_line_count = len(candidates)
    strong_quote_count = sum(1 for c in candidates if (c.get("score") or 0) >= strong_score_threshold)
    quote_density_per_1k_words = round(raw.get("highlight_density_per_1000_words", 0.0), 3)
    lines = []
    for c in candidates:
        sc = c.get("score", 0)
        if sc >= 6.0:
            strength = "great"
        elif sc >= 4.0:
            strength = "good"
        else:
            strength = "ok"
        lines.append({
            "text": c.get("text", ""),
            "strength": strength,
            "chapter_index": c.get("chapter_index", 0),
            "tags": c.get("tags", []),
        })
    return {
        "status": "pass",
        "metrics": {
            "memorable_line_count": memorable_line_count,
            "strong_quote_count": strong_quote_count,
            "quote_density_per_1k_words": quote_density_per_1k_words,
        },
        "lines": lines,
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="Compiled prose text file")
    g.add_argument("--plan", help="Compiled plan JSON containing chapter text")
    ap.add_argument("--json-out", required=True, help="Output JSON path")
    ap.add_argument("--min-score", type=float, default=3.0)
    ap.add_argument("--max-lines", type=int, default=80)
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    if args.plan:
        plan_path = Path(args.plan)
        if not plan_path.exists():
            print(f"Error: plan not found: {plan_path}", file=sys.stderr)
            return EXIT_FAIL
        try:
            book_id, chapters = load_chapters_from_plan(plan_path)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_FAIL
    else:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            return EXIT_FAIL
        try:
            book_id, chapters = load_chapters_from_file(file_path)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_FAIL

    payload = detect_lines(book_id, chapters, min_score=args.min_score, max_lines=args.max_lines)

    outp = Path(args.json_out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        f"Memorable lines: {payload['memorable_candidate_count']} | "
        f"density/1k words: {payload['highlight_density_per_1000_words']}"
    )
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
