#!/usr/bin/env python3
"""
phoenix_v4/quality/transformation_heatmap.py

Deterministic chapter-level "transformation signal" heatmap.
- Accepts a compiled prose .txt file (preferred) OR plan JSON that contains chapter text.
- If plan JSON has no chapter text, exits with clear error: use rendered .txt (Stage 6) or ensure plan has compiled_book.chapters[].text.

Exit codes (phoenix_v4/quality/base): 0 PASS, 1 FAIL, 2 WARN (2 = ending_weak).

Usage:
  PYTHONPATH=. python3 phoenix_v4/quality/transformation_heatmap.py --file compiled.txt --json-out artifacts/ops/heatmap.json --ascii
  PYTHONPATH=. python3 phoenix_v4/quality/transformation_heatmap.py --plan artifacts/book_002.plan.json --json-out artifacts/ops/heatmap.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from phoenix_v4.quality.base import EXIT_FAIL, EXIT_PASS, EXIT_WARN

# -----------------------------
# Patterns (tweakable)
# -----------------------------
PATTERNS = {
    "recognition": [
        r"\bif you['']?ve ever\b",
        r"\byou know this feeling\b",
        r"\bthis is you\b",
        r"\byou['']?ve probably\b",
    ],
    "reframe": [
        r"\bwhat if\b",
        r"\bactually\b",
        r"\binstead\b",
        r"\bit['']?s not that\b",
        r"\bthe truth is\b",
    ],
    "challenge": [
        r"\byou must\b",
        r"\byou need to\b",
        r"\bstop\b",
        r"\bchoose\b",
        r"\bstart\b",
    ],
    "relief": [
        r"\bit makes sense\b",
        r"\bno wonder\b",
        r"\bof course\b",
        r"\bthat['']?s okay\b",
    ],
    "identity_shift": [
        r"\byou are not broken\b",
        r"\bmaybe you['']?re\b",
        r"\byou['']?re becoming\b",
        r"\byou['']?re someone who\b",
        r"\bfrom now on\b",
    ],
}

CHAPTER_SPLIT_RE = re.compile(r"^\s*#+\s*chapter\b.*$", re.IGNORECASE | re.MULTILINE)

# -----------------------------
# Data
# -----------------------------


@dataclass(frozen=True)
class ChapterSignals:
    chapter_index: int
    recognition: bool
    reframe: bool
    challenge: bool
    relief: bool
    identity_shift: bool
    hits: Dict[str, int]


# -----------------------------
# Helpers
# -----------------------------


def normalize_text(t: str) -> str:
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    return t.strip()


def count_hits(text: str, pats: List[str]) -> int:
    flags = re.IGNORECASE | re.MULTILINE
    return sum(len(re.findall(p, text, flags)) for p in pats)


def load_from_plan(plan_path: Path) -> Tuple[str, List[str]]:
    data = json.loads(plan_path.read_text(encoding="utf-8"))
    book_id = data.get("book_id") or data.get("plan_id") or data.get("id") or "unknown_book"

    chapter_texts: List[str] = []
    if "compiled_book" in data and isinstance(data["compiled_book"], dict):
        chs = data["compiled_book"].get("chapters", [])
        for ch in chs:
            txt = ch.get("text") or ch.get("prose") or ""
            chapter_texts.append(str(txt))
    elif "chapters" in data and isinstance(data["chapters"], list):
        for ch in data["chapters"]:
            txt = ch.get("text") or ch.get("prose") or ""
            chapter_texts.append(str(txt))
    elif "compiled_chapters" in data and isinstance(data["compiled_chapters"], list):
        for ch in data["compiled_chapters"]:
            txt = ch.get("text") or ch.get("prose") or ""
            chapter_texts.append(str(txt))
    else:
        raise ValueError("PLAN_INPUT_INVALID: could not locate chapter texts in plan JSON")

    if not chapter_texts or all(not t.strip() for t in chapter_texts):
        raise ValueError(
            "PLAN_INPUT_INVALID: Plan JSON has no chapter text. "
            "Use a rendered .txt file (Stage 6: run_pipeline --render-book or render_plan_to_txt.py) "
            "or ensure plan includes compiled_book.chapters[].text."
        )

    return book_id, [normalize_text(t) for t in chapter_texts]


def load_from_file(path: Path) -> Tuple[str, List[str]]:
    text = normalize_text(path.read_text(encoding="utf-8", errors="replace"))
    book_id = path.stem

    splits = CHAPTER_SPLIT_RE.split(text)
    if len(splits) >= 2:
        chapters = [s.strip() for s in splits if s.strip()]
    else:
        chapters = [text] if text else []

    if not chapters:
        raise ValueError("FILE_INPUT_INVALID: no text found")
    return book_id, chapters


def compute_signals(chapters: List[str]) -> List[ChapterSignals]:
    out: List[ChapterSignals] = []
    for i, ch in enumerate(chapters):
        hits = {k: count_hits(ch, PATTERNS[k]) for k in PATTERNS}
        out.append(
            ChapterSignals(
                chapter_index=i,
                recognition=hits["recognition"] > 0,
                reframe=hits["reframe"] > 0,
                challenge=hits["challenge"] > 0,
                relief=hits["relief"] > 0,
                identity_shift=hits["identity_shift"] > 0,
                hits=hits,
            )
        )
    return out


def ending_check(signals: List[ChapterSignals], last_n: int = 2) -> Dict[str, bool]:
    tail = signals[-last_n:] if len(signals) >= last_n else signals
    has_identity = any(s.identity_shift for s in tail)
    has_reframe = any(s.reframe for s in tail)
    return {
        "ending_identity_shift_present": has_identity,
        "ending_reframe_present": has_reframe,
        "ending_weak": not (has_identity and has_reframe),
    }


def run_heatmap_from_path(path: Path) -> dict:
    """
    Run transformation heatmap from rendered text path. Returns bundle-shaped tool result
    for book_quality_bundle: status, metrics, chapter_signals.
    """
    book_id, chapters = load_from_file(path)
    sigs = compute_signals(chapters)
    end = ending_check(sigs, last_n=2)
    recognition_count = sum(s.hits["recognition"] for s in sigs)
    reframe_count = sum(s.hits["reframe"] for s in sigs)
    relief_count = sum(s.hits["relief"] for s in sigs)
    identity_shift_count = sum(s.hits["identity_shift"] for s in sigs)
    ending_strength_score = 0.0 if end["ending_weak"] else 1.0
    status = "warn" if end["ending_weak"] else "pass"
    return {
        "status": status,
        "metrics": {
            "recognition_count": recognition_count,
            "reframe_count": reframe_count,
            "relief_count": relief_count,
            "identity_shift_count": identity_shift_count,
            "ending_strength_score": ending_strength_score,
        },
        "chapter_signals": [
            {
                "chapter_index": s.chapter_index,
                "signals": {
                    "recognition": s.hits["recognition"],
                    "reframe": s.hits["reframe"],
                    "relief": s.hits["relief"],
                    "identity": s.hits["identity_shift"],
                },
            }
            for s in sigs
        ],
    }


def ascii_view(signals: List[ChapterSignals]) -> str:
    lines = []
    for s in signals:
        lines.append(
            f"CH{s.chapter_index+1:02d}: "
            f"R {'✓' if s.recognition else '✗'}  "
            f"RF {'✓' if s.reframe else '✗'}  "
            f"C {'✓' if s.challenge else '✗'}  "
            f"RL {'✓' if s.relief else '✗'}  "
            f"I {'✓' if s.identity_shift else '✗'}"
        )
    return "\n".join(lines)


# -----------------------------
# CLI
# -----------------------------


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="Compiled prose text file")
    g.add_argument("--plan", help="Compiled plan JSON containing chapters")
    ap.add_argument("--json-out", required=True, help="Output JSON path")
    ap.add_argument("--ascii", action="store_true", help="Print ASCII heatmap")
    ap.add_argument("--last-n", type=int, default=2, help="Ending check tail length")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    if args.plan:
        plan_path = Path(args.plan)
        if not plan_path.exists():
            print(f"Error: plan not found: {plan_path}", file=sys.stderr)
            return EXIT_FAIL
        try:
            book_id, chapters = load_from_plan(plan_path)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_FAIL
    else:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            return EXIT_FAIL
        try:
            book_id, chapters = load_from_file(file_path)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_FAIL

    sigs = compute_signals(chapters)
    end = ending_check(sigs, last_n=args.last_n)

    summary = {
        "chapters": len(sigs),
        "chapters_without_reframe": sum(1 for s in sigs if not s.reframe),
        "chapters_without_identity_shift": sum(1 for s in sigs if not s.identity_shift),
        **end,
    }

    payload = {
        "schema_version": "1.0",
        "book_id": book_id,
        "summary": summary,
        "chapter_signals": [asdict(s) for s in sigs],
    }

    outp = Path(args.json_out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.ascii:
        print(ascii_view(sigs))
        print("\nEnding:", "WEAK" if end["ending_weak"] else "OK")

    return EXIT_WARN if end["ending_weak"] else EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
