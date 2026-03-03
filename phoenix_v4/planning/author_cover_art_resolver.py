"""
Resolve author/teacher to cover art base background for pipeline output and export metadata.
Authority: docs/authoring/AUTHOR_COVER_ART_SYSTEM.md, config/authoring/author_cover_art_registry.yaml
Used by: run_pipeline.py (plan output), export/storefront (cover_variant_id, palette).
Fallback: first author in registry when author/teacher not found.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "config" / "authoring" / "author_cover_art_registry.yaml"

_DEFAULT_AUTHOR_ID = "ahjan"


def _load_registry(repo_root: Optional[Path] = None) -> dict:
    root = repo_root or REPO_ROOT
    path = root / "config" / "authoring" / "author_cover_art_registry.yaml"
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_author_cover_art(
    author_id_or_teacher_id: Optional[str],
    repo_root: Optional[Path] = None,
) -> dict[str, Any]:
    """
    Resolve cover art base and metadata for pipeline/export.
    Uses author_id or teacher_id (Teacher Mode uses teacher as cover author).
    Returns dict: cover_art_base (str path), style_hint (str), palette_tokens (list), cover_variant_id (str).
    Fallback: default author's base when id missing or not in registry.
    """
    root = repo_root or REPO_ROOT
    reg = _load_registry(root)
    authors = reg.get("authors") or {}

    effective_id = (author_id_or_teacher_id or "").strip()
    if not effective_id or effective_id not in authors:
        effective_id = _DEFAULT_AUTHOR_ID
        if effective_id not in authors and authors:
            effective_id = next(iter(authors))

    entry = authors.get(effective_id) or {}
    base_path_str = entry.get("cover_art_base") or ""
    if base_path_str:
        base_path = (root / base_path_str).resolve()
        if not base_path.exists():
            base_path_str = ""
    if not base_path_str and authors.get(_DEFAULT_AUTHOR_ID):
        base_path_str = authors[_DEFAULT_AUTHOR_ID].get("cover_art_base") or ""
        if base_path_str and not (root / base_path_str).resolve().exists():
            base_path_str = ""
    style_hint = entry.get("style_hint") or ""
    palette_tokens = entry.get("palette_tokens")
    if not isinstance(palette_tokens, list):
        palette_tokens = []

    return {
        "cover_art_base": base_path_str,
        "cover_art_style_hint": style_hint,
        "cover_art_palette_tokens": list(palette_tokens),
        "cover_variant_id": effective_id,
    }
