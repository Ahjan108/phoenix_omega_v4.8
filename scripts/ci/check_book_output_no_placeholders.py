#!/usr/bin/env python3
"""
Delivery gate: fail if placeholders or metadata artifacts leak into book output.

Authority: specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md §10.6.

Scans rendered book files (e.g. .txt under wave-rendered-dir) for:
- Unreplaced mustache placeholders: {{...}} (e.g. {{cta_text}}, {{slug}}, {{topic}})
- Structural placeholders: [Placeholder: ...], [Silence: ...] (if not intended in final copy)

Exit 0 if no matches; 1 if any file contains forbidden patterns (export must not proceed).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# Mustache-style: {{...}} including common freebie/metadata names
MUSTACHE = re.compile(r"\{\{[^}]+\}\}")
# Structural placeholders from renderer (fail if present in "final" output)
PLACEHOLDER_LINE = re.compile(r"\[Placeholder:\s*[^\]]+\]", re.IGNORECASE)
SILENCE_LINE = re.compile(r"\[Silence:\s*[^\]]+\]", re.IGNORECASE)


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Return list of (line_no, line_content, pattern_name) for any forbidden pattern."""
    violations: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [(0, "", "read_error")]
    for i, line in enumerate(text.splitlines(), start=1):
        if MUSTACHE.search(line):
            violations.append((i, line.strip()[:80], "mustache_placeholder"))
        if PLACEHOLDER_LINE.search(line):
            violations.append((i, line.strip()[:80], "structural_placeholder"))
        if SILENCE_LINE.search(line):
            violations.append((i, line.strip()[:80], "silence_placeholder"))
    return violations


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fail if placeholders/metadata leak into book output (PHOENIX_FREEBIE_SYSTEM_SPEC §10.6)"
    )
    ap.add_argument(
        "dir",
        nargs="?",
        default=None,
        help="Directory containing rendered book files (e.g. wave-rendered-dir). Scans recursively for .txt",
    )
    ap.add_argument(
        "--wave-rendered-dir",
        type=Path,
        default=None,
        help="Alias for dir (wave rendered root)",
    )
    args = ap.parse_args()

    root = args.wave_rendered_dir if args.wave_rendered_dir is not None else (Path(args.dir) if args.dir else None)
    if root is None or not root.is_dir():
        print("Usage: check_book_output_no_placeholders.py <dir> or --wave-rendered-dir <path>", file=sys.stderr)
        return 2

    total = 0
    for path in root.rglob("*.txt"):
        if not path.is_file():
            continue
        violations = scan_file(path)
        if violations:
            rel = path.relative_to(root) if root != path else path.name
            for line_no, snippet, kind in violations:
                print(f"{rel}:{line_no} [{kind}] {snippet}", file=sys.stderr)
            total += len(violations)

    if total > 0:
        print(f"DELIVERY GATE FAIL: {total} placeholder/metadata leak(s) in book output. Export must not proceed.", file=sys.stderr)
        return 1
    print("DELIVERY GATE PASS: no placeholders or metadata in book output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
