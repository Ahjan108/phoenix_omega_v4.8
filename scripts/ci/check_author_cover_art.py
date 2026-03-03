#!/usr/bin/env python3
"""
CI gate: every launchable author has author cover art registry entry, existing PNG, valid style/palette.
Launchable = teachers in brand_teacher_matrix + author_ids in author_registry.
Authority: docs/authoring/AUTHOR_COVER_ART_SYSTEM.md
Run: PYTHONPATH=. python3 scripts/ci/check_author_cover_art.py [--repo-root PATH]
Exit: 0 pass, 1 fail.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _launchable_author_ids(repo_root: Path) -> set[str]:
    """Teachers in brand_teacher_matrix + author_ids in author_registry."""
    ids: set[str] = set()
    # Teachers assigned to any brand
    matrix_path = repo_root / "config" / "catalog_planning" / "brand_teacher_matrix.yaml"
    matrix = _load_yaml(matrix_path)
    for brand_data in (matrix.get("brands") or {}).values():
        for tid in brand_data.get("teachers") or []:
            if isinstance(tid, str) and tid.strip():
                ids.add(tid.strip())
    # Pen-name authors
    author_reg_path = repo_root / "config" / "author_registry.yaml"
    author_reg = _load_yaml(author_reg_path)
    for aid in (author_reg.get("authors") or {}).keys():
        if isinstance(aid, str) and aid.strip():
            ids.add(aid.strip())
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate launchable authors have cover art registry + PNG + style/palette")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Repo root")
    args = ap.parse_args()
    repo_root = args.repo_root

    registry_path = repo_root / "config" / "authoring" / "author_cover_art_registry.yaml"
    if not registry_path.exists():
        print("FAIL: author cover art registry missing:", registry_path, file=sys.stderr)
        return 1

    reg = _load_yaml(registry_path)
    authors_reg = reg.get("authors") or {}

    launchable = _launchable_author_ids(repo_root)
    if not launchable:
        print("PASS: no launchable authors (empty brand_teacher_matrix + author_registry); skip", file=sys.stderr)
        return 0

    errors: list[str] = []
    for aid in sorted(launchable):
        if aid not in authors_reg:
            errors.append(f"{aid}: missing from author_cover_art_registry.yaml")
            continue
        entry = authors_reg[aid]
        base_path_str = entry.get("cover_art_base")
        if not base_path_str or not isinstance(base_path_str, str):
            errors.append(f"{aid}: cover_art_base missing or invalid")
            continue
        full_path = (repo_root / base_path_str).resolve()
        if not full_path.exists():
            errors.append(f"{aid}: cover_art_base file does not exist: {base_path_str}")
        style_hint = entry.get("style_hint")
        if not style_hint or not isinstance(style_hint, str) or not style_hint.strip():
            errors.append(f"{aid}: style_hint missing or empty")
        palette_tokens = entry.get("palette_tokens")
        if not isinstance(palette_tokens, list) or len(palette_tokens) == 0:
            errors.append(f"{aid}: palette_tokens missing or empty")

    if errors:
        for e in errors:
            print("FAIL:", e, file=sys.stderr)
        print("Author cover art gate: every launchable author must have registry entry, existing PNG, style_hint, palette_tokens.", file=sys.stderr)
        return 1
    print("PASS: all launchable authors have cover art registry entry, PNG, style_hint, palette_tokens.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
