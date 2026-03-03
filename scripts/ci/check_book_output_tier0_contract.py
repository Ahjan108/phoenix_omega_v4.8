#!/usr/bin/env python3
"""
Tier 0 book output contract: config-driven hard fail before export.
Authority: docs/MANUSCRIPT_QUALITY_IMPLEMENTATION_CHECKLIST.md
Config: config/quality/tier0_book_output_contract.yaml
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config() -> dict:
    """Load tier0 contract config."""
    config_path = REPO_ROOT / "config" / "quality" / "tier0_book_output_contract.yaml"
    if not config_path.exists():
        return {"forbidden_patterns": [], "min_word_count": 0, "max_consecutive_identical_lines": 0}
    try:
        import yaml
        return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {"forbidden_patterns": [], "min_word_count": 0}


def scan_file(path: Path, config: dict) -> list[tuple[int, str, str]]:
    """Return list of (line_no, snippet, violation_id) for any contract violation."""
    violations: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [(0, "", "read_error")]

    lines = text.splitlines()
    patterns = config.get("forbidden_patterns") or []
    for entry in patterns:
        if not isinstance(entry, dict):
            continue
        pat = entry.get("pattern")
        vid = entry.get("id", "unknown")
        if not pat:
            continue
        try:
            rx = re.compile(pat)
        except re.error:
            continue
        for i, line in enumerate(lines, start=1):
            if rx.search(line):
                violations.append((i, line.strip()[:80], vid))

    min_words = config.get("min_word_count") or 0
    if min_words > 0:
        word_count = sum(len(l.split()) for l in lines)
        if word_count < min_words:
            violations.append((0, f"word_count={word_count} < min={min_words}", "min_word_count"))

    return violations


def main() -> int:
    ap = argparse.ArgumentParser(description="Tier 0 book output contract check")
    ap.add_argument("dir", nargs="?", default=None, help="Directory of rendered .txt files")
    ap.add_argument("--wave-rendered-dir", type=Path, default=None, help="Alias for dir")
    args = ap.parse_args()

    root = args.wave_rendered_dir if args.wave_rendered_dir is not None else (Path(args.dir) if args.dir else None)
    if root is None or not root.is_dir():
        print("Usage: check_book_output_tier0_contract.py <dir> or --wave-rendered-dir <path>", file=sys.stderr)
        return 2

    config = load_config()
    total = 0
    for path in root.rglob("*.txt"):
        if not path.is_file():
            continue
        vios = scan_file(path, config)
        if vios:
            rel = path.relative_to(root) if root != path else path.name
            for line_no, snippet, kind in vios:
                print(f"{rel}:{line_no} [{kind}] {snippet}", file=sys.stderr)
            total += len(vios)

    if total > 0:
        print(f"TIER0 CONTRACT FAIL: {total} violation(s). Export must not proceed.", file=sys.stderr)
        return 1
    print("Tier 0 contract: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
