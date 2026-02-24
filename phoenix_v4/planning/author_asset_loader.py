"""
Load pen-name author assets (bio, why_this_book, authority_position, audiobook_pre_intro).
Authority: Writer Spec §23.3, AUTHOR_ASSET_WORKBOOK.md.
Used when pipeline runs with --author or author resolved from brand.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_AUTHORS_ROOT = REPO_ROOT / "assets" / "authors"
CONFIG_AUTHOR_REGISTRY = REPO_ROOT / "config" / "author_registry.yaml"

ASSET_FILES = ("bio", "why_this_book", "authority_position", "audiobook_pre_intro")


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_text(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8").strip()


def _extract_bio(data: dict) -> str:
    if not data:
        return ""
    # bio.yaml: bio: > or bio: "..."
    v = data.get("bio")
    if isinstance(v, str):
        return v.strip()
    return ""


def _extract_why_this_book(data: dict) -> str:
    if not data:
        return ""
    v = data.get("why_this_book")
    if isinstance(v, str):
        return v.strip()
    return ""


def _extract_authority_position(data: dict) -> str | dict:
    if not data:
        return {}
    v = data.get("authority_position")
    if v is None:
        return {}
    if isinstance(v, str):
        return {"raw": v}
    if isinstance(v, dict):
        return v
    return {}


def _extract_audiobook_pre_intro(data: dict) -> dict:
    """Return dict of blocks: narrator_intro, book_title_line, series_line, author_intro, author_background, why_this_book, transition_line."""
    if not data:
        return {}
    out: dict[str, str] = {}
    for key in (
        "narrator_intro",
        "book_title_line",
        "series_line",
        "author_intro",
        "author_background",
        "why_this_book",
        "transition_line",
    ):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            out[key] = v.strip()
    return out


def load_author_registry(repo_root: Optional[Path] = None) -> dict:
    """Load config/author_registry.yaml."""
    root = repo_root or REPO_ROOT
    path = root / "config" / "author_registry.yaml"
    return _load_yaml(path)


def load_author_assets(
    author_id: str,
    repo_root: Optional[Path] = None,
    author_registry: Optional[dict] = None,
    assets_root_override: Optional[Path] = None,
) -> dict[str, Any]:
    """
    Load author bio, why_this_book, authority_position, audiobook_pre_intro.
    Tries: assets_root_override, then assets/authors/<author_id>/, then registry assets_path if present.
    Returns dict with keys: author_id, pen_name, bio, why_this_book, authority_position (dict or str),
    audiobook_pre_intro (dict of blocks), positioning_profile, errors (list of missing-file messages).
    Writer Spec §23.3: compile fails if any required asset missing; caller can check errors and fail.
    """
    root = repo_root or REPO_ROOT
    registry = author_registry if author_registry is not None else load_author_registry(root)
    authors = (registry.get("authors") or {}).get(author_id) or {}
    pen_name = authors.get("pen_name") or author_id.replace("_", " ").title()
    positioning_profile = authors.get("positioning_profile") or ""

    # Resolve assets directory
    assets_dir: Optional[Path] = None
    if assets_root_override and assets_root_override.is_dir():
        assets_dir = assets_root_override
    else:
        primary = root / "assets" / "authors" / author_id
        if primary.is_dir():
            assets_dir = primary
        else:
            # Registry may point to a path (e.g. deli/mnt/user-data/outputs/luna_hart or deli/kai_nakamura_all_assets.yaml)
            path_str = authors.get("assets_path")
            if isinstance(path_str, str) and path_str:
                candidate = (root / path_str).resolve()
                if candidate.is_file():
                    # Single file with multiple YAML docs (e.g. kai_nakamura_all_assets.yaml)
                    return _load_author_assets_from_single_file(
                        author_id=author_id,
                        path=candidate,
                        pen_name=pen_name,
                        positioning_profile=positioning_profile,
                    )
                if candidate.is_dir():
                    assets_dir = candidate

    errors: list[str] = []
    result: dict[str, Any] = {
        "author_id": author_id,
        "pen_name": pen_name,
        "positioning_profile": positioning_profile,
        "bio": "",
        "why_this_book": "",
        "authority_position": {},
        "audiobook_pre_intro": {},
        "errors": errors,
    }

    if not assets_dir:
        errors.append(f"no assets directory for author_id={author_id} (tried assets/authors/{author_id}/ and registry assets_path)")
        return result

    # Load each asset from separate files (bio.yaml, etc.)
    bio_path = assets_dir / "bio.yaml"
    why_path = assets_dir / "why_this_book.yaml"
    auth_path = assets_dir / "authority_position.yaml"
    pre_path = assets_dir / "audiobook_pre_intro.yaml"

    bio_data = _load_yaml(bio_path)
    why_data = _load_yaml(why_path)
    auth_data = _load_yaml(auth_path)
    pre_data = _load_yaml(pre_path)

    if not bio_data and not bio_path.exists():
        errors.append(f"missing {bio_path.relative_to(root) if root in bio_path.parents else bio_path}")
    if not why_data and not why_path.exists():
        errors.append(f"missing {why_path.relative_to(root) if root in why_path.parents else why_path}")
    if not auth_data and not auth_path.exists():
        errors.append(f"missing {auth_path.relative_to(root) if root in auth_path.parents else auth_path}")
    if not pre_data and not pre_path.exists():
        errors.append(f"missing {pre_path.relative_to(root) if root in pre_path.parents else pre_path}")

    result["bio"] = _extract_bio(bio_data)
    result["why_this_book"] = _extract_why_this_book(why_data)
    result["authority_position"] = _extract_authority_position(auth_data)
    result["audiobook_pre_intro"] = _extract_audiobook_pre_intro(pre_data)

    return result


def _load_author_assets_from_single_file(
    author_id: str,
    path: Path,
    pen_name: str,
    positioning_profile: str,
) -> dict[str, Any]:
    """Load from a single file containing multiple YAML documents (e.g. kai_nakamura_all_assets.yaml)."""
    errors: list[str] = []
    result: dict[str, Any] = {
        "author_id": author_id,
        "pen_name": pen_name,
        "positioning_profile": positioning_profile,
        "bio": "",
        "why_this_book": "",
        "authority_position": {},
        "audiobook_pre_intro": {},
        "errors": errors,
    }
    if not path.exists() or yaml is None:
        errors.append(f"file not found or yaml unavailable: {path}")
        return result
    raw = path.read_text(encoding="utf-8")
    docs = list(yaml.safe_load_all(raw)) if raw.strip() else []
    # Expect order: bio, why_this_book, authority_position, audiobook_pre_intro (per AUTHOR_ASSET_WORKBOOK)
    bio_data = docs[0] if len(docs) > 0 else {}
    why_data = docs[1] if len(docs) > 1 else {}
    auth_data = docs[2] if len(docs) > 2 else {}
    pre_data = docs[3] if len(docs) > 3 else {}
    result["bio"] = _extract_bio(bio_data)
    result["why_this_book"] = _extract_why_this_book(why_data)
    result["authority_position"] = _extract_authority_position(auth_data)
    result["audiobook_pre_intro"] = _extract_audiobook_pre_intro(pre_data)
    return result


def render_audiobook_pre_intro(
    author_assets: dict[str, Any],
    book_title: str = "",
    series_name: str = "",
    include_series_line: bool = False,
) -> str:
    """
    Render the narrator-read pre-intro text from author_assets (Writer Spec §23.4 order).
    Blocks: narrator_intro, book_title_line, series_line (if include_series_line), author_intro, author_background, why_this_book, transition_line.
    """
    blocks = author_assets.get("audiobook_pre_intro") or {}
    parts = []
    if blocks.get("narrator_intro"):
        parts.append(blocks["narrator_intro"])
    if blocks.get("book_title_line"):
        parts.append(blocks["book_title_line"])
    elif book_title and author_assets.get("pen_name"):
        parts.append(f'You are listening to "{book_title}", written by {author_assets["pen_name"]}.')
    if include_series_line and blocks.get("series_line"):
        parts.append(blocks["series_line"])
    if blocks.get("author_intro"):
        parts.append(blocks["author_intro"])
    if blocks.get("author_background"):
        parts.append(blocks["author_background"])
    if blocks.get("why_this_book"):
        parts.append(blocks["why_this_book"])
    if blocks.get("transition_line"):
        parts.append(blocks["transition_line"])
    return "\n\n".join(parts)
