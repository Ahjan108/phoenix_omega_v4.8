#!/usr/bin/env python3
"""
phoenix_v4/quality/story_atom_lint.py

Deterministic story-atom linting:
- checks specificity, conflict, cost, insight pivot
- scores PASS/WARN/FAIL per atom
- CANONICAL.txt: parses ## ROLE vNN --- metadata --- prose blocks and lints each atom separately (no whole-file masking).
- Other .txt/.md: linted as single blob (one result per file).

Exit codes (see phoenix_v4/quality/base.py): 0 PASS, 1 FAIL, 2 WARN.

Usage:
  PYTHONPATH=. python3 phoenix_v4/quality/story_atom_lint.py --path atoms/.../CANONICAL.txt --json-out artifacts/ops/story_lint.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from phoenix_v4.quality.base import (
    EXIT_FAIL,
    EXIT_PASS,
    EXIT_WARN,
    parse_canonical_blocks_from_path,
    status_to_exit_code,
)

# -----------------------------
# Patterns (tweakable)
# -----------------------------

ACTION_VERBS = [
    r"\b(sat|stood|walked|drove|ran|stared|grabbed|held|shook|typed|called|texted|opened|closed|slammed)\b",
]
SENSORY_WORDS = [
    r"\b(cold|warm|loud|silent|tight|heavy|burning|buzzing|aching|sweaty|shaky)\b",
]
CONFLICT_MARKERS = [
    r"\b(but|however|although|yet)\b",
    r"\b(couldn['']t|cannot|can't)\b",
    r"\b(wanted to|should)\b",
]
COST_MARKERS = [
    r"\b(lost|exhausted|ashamed|avoided|broke|collapsed|quit)\b",
    r"\b(couldn['']t sleep|stopped eating|panic|crying)\b",
]
PIVOT_MARKERS = [
    r"\b(I|she|he|they)\s+(realized|noticed|understood|saw|recognized)\b",
    r"\b(the truth was|that's when|thats when|it hit (me|her|him)|what (I|she|he) didn['']t know)\b",
]

PROPER_NOUN_RE = re.compile(r"\b(?!I\b)[A-Z][a-z]{2,}\b")
WORD_RE = re.compile(r"\b[\w'']+\b")

# -----------------------------
# Data
# -----------------------------


@dataclass(frozen=True)
class StoryLintResult:
    path: str
    story_id: str
    word_count: int
    flags: List[str]
    missing_signals: int
    status: str  # PASS/WARN/FAIL
    notes: List[str]
    band: str = ""


# -----------------------------
# Helpers
# -----------------------------


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_hits(text: str, patterns: List[str]) -> int:
    flags = re.IGNORECASE | re.MULTILINE
    return sum(len(re.findall(p, text, flags)) for p in patterns)


def has_any(text: str, patterns: List[str]) -> bool:
    return count_hits(text, patterns) > 0


def count_proper_nouns(text: str) -> int:
    tokens = PROPER_NOUN_RE.findall(text)
    return len(tokens)


def derive_story_id(path: Path) -> str:
    return path.stem


def lint_one_prose(prose: str, story_id: str, path: str, band: str = "") -> StoryLintResult:
    """Lint a single story prose block. Used for per-atom and single-blob modes."""
    text = normalize_text(prose)
    wc = word_count(text)

    flags: List[str] = []
    notes: List[str] = []

    if wc < 120:
        flags.append("TOO_SHORT_LT_120")

    proper_n = count_proper_nouns(text)
    has_action = has_any(text, ACTION_VERBS)
    has_sensory = has_any(text, SENSORY_WORDS)
    if (proper_n == 0) and (not has_action) and (not has_sensory):
        flags.append("NO_SPECIFIC_DETAIL")

    if not has_any(text, CONFLICT_MARKERS):
        flags.append("NO_INTERNAL_CONFLICT")

    if not has_any(text, COST_MARKERS):
        flags.append("NO_COST_SIGNAL")

    pivot = has_any(text, PIVOT_MARKERS)
    if not pivot:
        flags.append("NO_INSIGHT_PIVOT")
        if wc < 180:
            notes.append("Short story with no pivot tends to read generic.")

    signal_flags = {"NO_SPECIFIC_DETAIL", "NO_INTERNAL_CONFLICT", "NO_COST_SIGNAL", "NO_INSIGHT_PIVOT"}
    missing = sum(1 for f in flags if f in signal_flags)

    status = "PASS"
    if "TOO_SHORT_LT_120" in flags or missing >= 3:
        status = "FAIL"
    elif missing == 2:
        status = "WARN"

    return StoryLintResult(
        path=path,
        story_id=story_id,
        word_count=wc,
        flags=flags,
        missing_signals=missing,
        status=status,
        notes=notes,
        band=band,
    )


def lint_story(text: str, path: Path) -> StoryLintResult:
    """Lint whole text as one story (legacy single-blob)."""
    return lint_one_prose(text, derive_story_id(path), str(path), band="")


def iter_text_files(root: Path) -> List[Path]:
    if root.is_file():
        return [root]
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".txt", ".md"):
            files.append(p)
    return sorted(files)


def lint_canonical_file(path: Path) -> List[StoryLintResult]:
    """Parse CANONICAL.txt into blocks and lint each atom. Raises ValueError if malformed."""
    blocks = parse_canonical_blocks_from_path(path)
    path_str = str(path)
    return [
        lint_one_prose(block.body, block.atom_id, path_str, band=block.band)
        for block in blocks
    ]


# -----------------------------
# CLI
# -----------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="File or directory of story atoms")
    ap.add_argument("--json-out", default=None, help="Write JSON report to this path")
    ap.add_argument(
        "--fail-on",
        choices=["PASS", "WARN", "FAIL"],
        default="FAIL",
        help="Exit nonzero if any result is at/above this severity",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path)

    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        return 1

    results: List[StoryLintResult] = []
    for f in iter_text_files(root):
        try:
            if f.name == "CANONICAL.txt":
                try:
                    results.extend(lint_canonical_file(f))
                except ValueError as ve:
                    results.append(
                        StoryLintResult(
                            path=str(f),
                            story_id=derive_story_id(f),
                            word_count=0,
                            flags=["MALFORMED_CANONICAL"],
                            missing_signals=4,
                            status="FAIL",
                            notes=[str(ve)],
                            band="",
                        )
                    )
            else:
                text = f.read_text(encoding="utf-8", errors="replace")
                results.append(lint_story(text, f))
        except Exception as e:
            results.append(
                StoryLintResult(
                    path=str(f),
                    story_id=derive_story_id(f),
                    word_count=0,
                    flags=["READ_ERROR"],
                    missing_signals=4,
                    status="FAIL",
                    notes=[str(e)],
                    band="",
                )
            )
            continue

    if not results:
        print("No story files found.", file=sys.stderr)
        return 1

    fail_count = sum(1 for r in results if r.status == "FAIL")
    warn_count = sum(1 for r in results if r.status == "WARN")
    pass_count = sum(1 for r in results if r.status == "PASS")
    overall = "fail" if fail_count else ("warn" if warn_count else "pass")

    # Ops artifact (schema story_atom_lint_v1)
    entity_id = str(root.resolve())
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    ops_payload = {
        "schema_version": "1.0",
        "tool": "story_atom_lint",
        "entity_type": "atom_file",
        "entity_id": entity_id,
        "generated_at": generated_at,
        "status": overall,
        "summary": {
            "total_atoms": len(results),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "pass_count": pass_count,
        },
        "details": [
            {
                "atom_id": r.story_id,
                "band": r.band,
                "status": r.status.lower(),
                "issues": list(r.flags),
            }
            for r in results
        ],
    }

    outp = Path(args.json_out) if args.json_out else None
    if not outp:
        outp = REPO_ROOT / "artifacts" / "ops" / f"story_atom_lint_summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(ops_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    top = [r for r in results if r.status != "PASS"][:20]
    if top:
        print("\nTop issues:")
        for r in top:
            print(f"- {r.status} {r.story_id} ({r.word_count}w) {Path(r.path).name} :: {', '.join(r.flags)}")

    return status_to_exit_code(overall)


if __name__ == "__main__":
    raise SystemExit(main())
