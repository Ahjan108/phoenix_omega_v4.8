"""
Pre-intro block resolution with per-brand pattern banks and deterministic selection.
Authority: Controlled Intro/Conclusion Variation plan.
When intro_ending_variation_enabled is false, callers use YAML-only (no resolution).
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_SOT = REPO_ROOT / "config" / "source_of_truth"
PRE_INTRO_BANKS = CONFIG_SOT / "pre_intro" / "banks.yaml"

# §23.4 order; required when author_id set (series_line optional).
PRE_INTRO_BLOCK_ORDER = (
    "narrator_intro",
    "book_title_line",
    "series_line",
    "author_intro",
    "author_background",
    "why_this_book",
    "transition_line",
)
REQUIRED_BLOCKS_WHEN_AUTHOR = frozenset({
    "narrator_intro", "book_title_line", "author_intro",
    "author_background", "why_this_book", "transition_line",
})


def compute_pre_intro_signature(full_pre_intro_text: str) -> str:
    """SHA256 of full resolved pre-intro text; first 16 chars. Used for intro caps and duplicate gate."""
    digest = hashlib.sha256(full_pre_intro_text.encode("utf-8")).hexdigest()
    return digest[:16]


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _selector_index(selector_key: str, available_count: int) -> int:
    """Deterministic index; same algorithm as slot_resolver."""
    if available_count <= 0:
        return 0
    digest = hashlib.sha256(selector_key.encode("utf-8")).digest()
    n = int.from_bytes(digest[:16], "big")
    return n % available_count


def _get_bank_for_brand(banks_data: dict, brand_id: str) -> dict:
    """Return bank config for brand or default."""
    brands = banks_data.get("brands") or {}
    if brand_id and brand_id in brands:
        return brands[brand_id] or {}
    return banks_data.get("default") or {}


def resolve_pre_intro_blocks(
    author_assets: dict[str, Any],
    brand_id: str,
    selector_key: str,
    book_title: str = "",
    series_name: str = "",
    include_series_line: bool = False,
    pattern_bank_overrides_yaml: bool = False,
    config_root: Optional[Path] = None,
) -> dict[str, str]:
    """
    Resolve pre-intro blocks: merge stable (YAML) with dynamic (pattern bank or YAML).
    - Stable: author_intro, author_background — always from author_assets audiobook_pre_intro.
    - Dynamic: narrator_intro, book_title_line, series_line, why_this_book, transition_line.
    Precedence: when pattern_bank_overrides_yaml and bank has variants for that block, use bank;
    else use YAML. If bank missing for brand/block use YAML. If YAML missing for required block, raise.
    """
    config_root = config_root or CONFIG_SOT
    blocks = dict(author_assets.get("audiobook_pre_intro") or {})

    # Load banks
    banks_path = config_root / "pre_intro" / "banks.yaml"
    banks_data = _load_yaml(banks_path) if banks_path.exists() else {}
    bank = _get_bank_for_brand(banks_data, brand_id)

    pen_name = author_assets.get("pen_name") or ""

    # book_title_line: prefer runtime; validate conflict if YAML has value and runtime differs
    if book_title and pen_name:
        runtime_line = f'You are listening to "{book_title}", written by {pen_name}.'
        yaml_line = blocks.get("book_title_line", "").strip()
        if yaml_line and yaml_line != runtime_line:
            raise ValueError(
                f"Pre-intro book_title_line conflict: YAML has fixed line, runtime title differs. "
                f"Use one source (runtime injection or fixed YAML)."
            )
        blocks["book_title_line"] = runtime_line
    elif not blocks.get("book_title_line") and not book_title:
        # Will be validated later: required block can be missing and we fail in validator
        pass
    elif not blocks.get("book_title_line"):
        blocks["book_title_line"] = ""

    # series_line: only when include_series_line; usually from YAML
    if not include_series_line:
        blocks.pop("series_line", None)
    # else leave as from YAML or empty

    # why_this_book from bank (pre_intro_frames) or YAML
    frames = bank.get("pre_intro_frames") or []
    if isinstance(frames, list) and frames:
        # Entries can be dict with 'text' or plain str
        texts = []
        for f in frames:
            if isinstance(f, dict) and f.get("text"):
                texts.append(str(f["text"]).strip())
            elif isinstance(f, str) and f.strip():
                texts.append(f.strip())
        if texts and (pattern_bank_overrides_yaml or not blocks.get("why_this_book")):
            idx = _selector_index(f"{selector_key}:why_this_book", len(texts))
            blocks["why_this_book"] = texts[idx]
    if not blocks.get("why_this_book") and "why_this_book" in REQUIRED_BLOCKS_WHEN_AUTHOR:
        pass  # validator will fail

    # narrator_intro from bank or YAML
    variants = bank.get("narrator_intro_variants") or []
    if isinstance(variants, list) and variants:
        str_variants = [v.strip() for v in variants if isinstance(v, str) and v.strip()]
        if str_variants and (pattern_bank_overrides_yaml or not blocks.get("narrator_intro")):
            idx = _selector_index(f"{selector_key}:narrator_intro", len(str_variants))
            blocks["narrator_intro"] = str_variants[idx]
    # else keep YAML value or leave missing

    # transition_line from bank or YAML
    trans = bank.get("transition_line_variants") or []
    if isinstance(trans, list) and trans:
        str_trans = [t.strip() for t in trans if isinstance(t, str) and t.strip()]
        if str_trans and (pattern_bank_overrides_yaml or not blocks.get("transition_line")):
            idx = _selector_index(f"{selector_key}:transition_line", len(str_trans))
            blocks["transition_line"] = str_trans[idx]

    # Build result in §23.4 order; omit series_line unless include_series_line. Do not add empty string for missing required blocks.
    out: dict[str, str] = {}
    for k in PRE_INTRO_BLOCK_ORDER:
        if k == "series_line" and not include_series_line:
            continue
        v = blocks.get(k)
        if isinstance(v, str) and v.strip():
            out[k] = v.strip()
        elif k != "series_line":
            # Optional series_line may be absent; other blocks keep raw so validator can fail on missing required
            if v is not None and isinstance(v, str):
                out[k] = v
    return out
