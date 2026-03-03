#!/usr/bin/env python3
"""
Check that substantive changes to the Canonical Spec are accompanied by a version bump
and a migration note. Use in CI or pre-commit when specs/PHOENIX_V4_CANONICAL_SPEC.md is modified.

Usage:
  python scripts/check_spec_version_bump.py [before_path] [after_path]
  If one path given: compare with current working tree.
  If no paths: compare HEAD vs working tree for specs/PHOENIX_V4_CANONICAL_SPEC.md.

Exit 0 if OK; non-zero if content changed without version bump or version bumped without migration note.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = REPO_ROOT / "specs" / "PHOENIX_V4_CANONICAL_SPEC.md"

VERSION_RE = re.compile(r"^\*\*Version:\*\*\s*(.+)$", re.MULTILINE)


def normalize(text: str) -> str:
    """Normalize for comparison: strip trailing whitespace, collapse blank lines to single newline."""
    lines = [line.rstrip() for line in text.splitlines()]
    out: list[str] = []
    prev_blank = False
    for line in lines:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        out.append(line)
        prev_blank = is_blank
    return "\n".join(out) + ("\n" if out else "")


def get_version_line(text: str) -> str | None:
    m = VERSION_RE.search(text)
    return m.group(1).strip() if m else None


def content_changed(before: str, after: str) -> bool:
    return normalize(before) != normalize(after)


def has_migration_note(text: str) -> bool:
    """True if text contains a migration note (word 'Migration' in a line)."""
    return "Migration" in text


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(argv) >= 2:
        before_content = Path(argv[0]).read_text()
        after_content = Path(argv[1]).read_text()
    elif len(argv) == 1:
        try:
            result = subprocess.run(
                ["git", "show", "HEAD:" + str(DEFAULT_SPEC)],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=5,
            )
            if result.returncode != 0:
                print("check_spec_version_bump: could not read HEAD version of spec (not in git?).", file=sys.stderr)
                return 2
            before_content = result.stdout
        except Exception as e:
            print(f"check_spec_version_bump: {e}", file=sys.stderr)
            return 2
        after_content = Path(argv[0]).read_text()
    else:
        try:
            result = subprocess.run(
                ["git", "show", "HEAD:" + str(DEFAULT_SPEC)],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=5,
            )
            if result.returncode != 0:
                print("check_spec_version_bump: could not read HEAD version (not in git?).", file=sys.stderr)
                return 2
            before_content = result.stdout
        except Exception as e:
            print(f"check_spec_version_bump: {e}", file=sys.stderr)
            return 2
        if not DEFAULT_SPEC.exists():
            print("check_spec_version_bump: spec file not found.", file=sys.stderr)
            return 2
        after_content = DEFAULT_SPEC.read_text()

    if not content_changed(before_content, after_content):
        return 0

    before_ver = get_version_line(before_content)
    after_ver = get_version_line(after_content)

    if before_ver == after_ver:
        print(
            "check_spec_version_bump: spec content changed but Version line unchanged. "
            "Bump the Version line and add a migration note (e.g. 'Migration:' in Part 0 or a new section).",
            file=sys.stderr,
        )
        return 1

    if not has_migration_note(after_content):
        print(
            "check_spec_version_bump: Version was bumped but no migration note found. "
            "Add a line containing 'Migration' (e.g. in Part 0 or a new subsection) to record consequences.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
