#!/usr/bin/env python3
"""
Lint an exercise YAML: schema (required sections), word counts, banned phrases, body reference.
Usage: python -m tools.exercise_lint.lint_exercise <path_to_exercise.yaml>
Exit 0 if no errors; 1 if errors. Warnings do not change exit code unless --strict.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

REQUIRED_SECTIONS = ("intro", "guided_practice", "aha_noticing", "integration")
MIN_WORDS = {"intro": 60, "guided_practice": 80, "aha_noticing": 40, "integration": 40}
BANNED_PHRASES = [
    "you will", "this will", "guarantee", "cure", "heal", "fix", "transform",
    "forever", "completely", "promise", "fixing language", "resolution language",
]
BODY_REFERENCE_WORDS = (
    "breath", "chest", "shoulders", "jaw", "rhythm", "tension", "body", "sensation",
    "belly", "feet", "hands", "spine", "heart", "nervous system",
)


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        return {"__load_error": str(e)}


def lint_exercise(path: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ([f"File not found: {path}"], [])

    data = _load_yaml(path)
    if "__load_error" in data:
        return ([f"Invalid YAML: {data['__load_error']}"], [])

    if not isinstance(data.get("content"), dict):
        errors.append("Missing or invalid 'content' (must be dict with intro, guided_practice, aha_noticing, integration)")
        return (errors, warnings)

    content = data["content"]
    for sec in REQUIRED_SECTIONS:
        if sec not in content:
            errors.append(f"Missing required section: content.{sec}")
        else:
            text = content[sec]
            if not isinstance(text, str):
                text = str(text) if text else ""
            wc = _word_count(text)
            min_w = MIN_WORDS.get(sec, 0)
            if min_w and wc < min_w:
                errors.append(f"content.{sec}: word count {wc} < minimum {min_w}")

    full_text = " ".join(str(content.get(s, "")) for s in REQUIRED_SECTIONS).lower()
    for phrase in BANNED_PHRASES:
        if phrase.lower() in full_text:
            errors.append(f"Banned phrase found: {phrase!r}")

    aha = content.get("aha_noticing") or ""
    if isinstance(aha, str) and aha.strip():
        if not any(w in aha.lower() for w in BODY_REFERENCE_WORDS):
            warnings.append("aha_noticing: no body reference word (e.g. breath, chest, body)")
        if "notice" not in aha.lower() and "might notice" not in aha.lower():
            warnings.append("aha_noticing: should contain 'notice' or 'might notice'")

    return (errors, warnings)


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint exercise YAML")
    ap.add_argument("file", type=Path, help="Path to exercise YAML")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = ap.parse_args()
    path = args.file.resolve()
    errors, warnings = lint_exercise(path, strict=args.strict)
    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
