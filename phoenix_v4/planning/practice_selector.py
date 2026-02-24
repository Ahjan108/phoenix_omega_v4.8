"""
Deterministic practice item selection for EXERCISE backstop and slot_07_practice.
Loads store from SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STORE_PATH = REPO_ROOT / "SOURCE_OF_TRUTH" / "practice_library" / "store" / "practice_items.jsonl"
SELECTION_RULES_PATH = REPO_ROOT / "config" / "practice" / "selection_rules.yaml"


def _load_rules(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_store(store_path: Optional[Path] = None) -> list[dict[str, Any]]:
    """Load practice_items.jsonl; return list of PracticeItem dicts."""
    path = store_path or STORE_PATH
    if not path.exists():
        return []
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def get_backstop_pool(
    store_path: Optional[Path] = None,
    rules_path: Optional[Path] = None,
) -> list[Any]:
    """
    Return pool of practice items as AtomEntry-like objects for EXERCISE backstop.
    Only when EXERCISE_BACKSTOP is enabled and allowed_content_types are used to filter.
    Returns list of objects with .atom_id and .metadata (content_type in metadata for future use).
    """
    from phoenix_v4.planning.pool_index import AtomEntry

    rules = _load_rules(rules_path or SELECTION_RULES_PATH)
    slots = rules.get("slots") or {}
    backstop = slots.get("EXERCISE_BACKSTOP") or {}
    if not backstop.get("enabled", True):
        return []
    allowed = set(backstop.get("allowed_content_types") or [])
    if not allowed:
        allowed = {
            "sensory_grounding", "meditations", "reflections", "self_inquiry",
            "gratitude_practices", "affirmations", "body_awareness", "thought_experiments", "integration_bridges",
        }
    items = load_store(store_path)
    out = []
    for it in items:
        ct = it.get("content_type")
        if ct not in allowed:
            continue
        practice_id = it.get("practice_id")
        if not practice_id:
            continue
        out.append(AtomEntry(atom_id=practice_id, metadata={"content_type": ct}, atom_source="practice_fallback"))
    out.sort(key=lambda e: e.atom_id)
    return out


def get_practice_prose_map(store_path: Optional[Path] = None) -> dict[str, str]:
    """Return practice_id -> text for all items in store (for prose resolution)."""
    items = load_store(store_path)
    return {it["practice_id"]: (it.get("text") or "").strip() for it in items if it.get("practice_id")}
