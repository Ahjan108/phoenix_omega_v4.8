#!/usr/bin/env python3
"""Docs governance CI: links, freshness headers, and canonical authority anchors."""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

TARGET_MD: list[Path] = sorted((REPO_ROOT / "docs").rglob("*.md")) + sorted((REPO_ROOT / "specs").rglob("*.md"))
if (REPO_ROOT / "ONBOARDING.md").exists():
    TARGET_MD.append(REPO_ROOT / "ONBOARDING.md")

REQUIRED_LAST_UPDATED = [
    REPO_ROOT / "docs" / "DOCS_INDEX.md",
    REPO_ROOT / "docs" / "SYSTEMS_V4.md",
    REPO_ROOT / "specs" / "README.md",
    REPO_ROOT / "ONBOARDING.md",
]

AUTHORITY_GUARD_FILES = [
    REPO_ROOT / "docs" / "DOCS_INDEX.md",
    REPO_ROOT / "docs" / "SYSTEMS_V4.md",
    REPO_ROOT / "specs" / "README.md",
    REPO_ROOT / "ONBOARDING.md",
]

CANONICAL_TOKENS = (
    "DOCS_INDEX.md",
    "PHOENIX_ARC_FIRST_CANONICAL_SPEC.md",
    "PHOENIX_V4_5_WRITER_SPEC.md",
)

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LAST_UPDATED_RE = re.compile(r"(?im)^\*\*Last updated:\*\*\s*(\d{4}-\d{2}-\d{2})\s*$")


def _iter_md_links(text: str) -> Iterable[str]:
    for m in LINK_RE.finditer(text):
        raw = m.group(1).strip()
        if not raw:
            continue
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1].strip()
        if " " in raw:
            raw = raw.split(" ", 1)[0].strip()
        yield raw


def _is_external(target: str) -> bool:
    prefixes = ("http://", "https://", "mailto:", "tel:", "data:", "app://", "vscode://")
    return target.startswith(prefixes) or target.startswith("#") or "{{" in target or "}}" in target


def _resolve_link(src: Path, target: str) -> Path | None:
    no_anchor = target.split("#", 1)[0].strip()
    if not no_anchor:
        return None
    if no_anchor.startswith("/"):
        p = Path(no_anchor)
    else:
        p = (src.parent / no_anchor).resolve()
    return p


def check_links(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"{f}: read error: {e}")
            continue
        for link in _iter_md_links(text):
            if _is_external(link):
                continue
            resolved = _resolve_link(f, link)
            if resolved is None:
                continue
            if not resolved.exists():
                errors.append(f"{f}: broken link '{link}' -> '{resolved}'")
    return errors


def check_last_updated(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for f in files:
        if not f.exists():
            errors.append(f"{f}: missing required file for Last updated validation")
            continue
        text = f.read_text(encoding="utf-8")
        m = LAST_UPDATED_RE.search(text)
        if not m:
            errors.append(f"{f}: missing '**Last updated:** YYYY-MM-DD'")
            continue
        date_str = m.group(1)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append(f"{f}: invalid Last updated date '{date_str}'")
    return errors


def check_authority_guard(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for f in files:
        if not f.exists():
            errors.append(f"{f}: missing required authority file")
            continue
        text = f.read_text(encoding="utf-8")
        missing = [tok for tok in CANONICAL_TOKENS if tok not in text]
        if missing:
            errors.append(f"{f}: missing canonical authority references: {', '.join(missing)}")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(check_links(TARGET_MD))
    errors.extend(check_last_updated(REQUIRED_LAST_UPDATED))
    errors.extend(check_authority_guard(AUTHORITY_GUARD_FILES))

    if errors:
        print("Docs governance check FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Docs governance check PASSED")
    print(f"- checked markdown files: {len(TARGET_MD)}")
    print("- link integrity: OK")
    print("- Last updated headers: OK")
    print("- canonical authority guard: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
