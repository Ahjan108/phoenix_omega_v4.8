"""
Cross-catalog memorable line registry — shared logic.

- Normalize line text (lowercase, strip punctuation, collapse whitespace).
- Hash → track occurrences, books, brands.
- Append-only JSONL canonical; snapshot JSON for queries.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def normalize_line(text: str) -> str:
    """
    Deterministic normalization: lowercase, strip punctuation, collapse whitespace,
    remove leading/trailing quotes. No stopwords (avoids collisions).
    """
    if not text or not isinstance(text, str):
        return ""
    t = text.lower().strip()
    t = re.sub(r"['\"](.*)['\"]", r"\1", t)
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def line_hash(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def load_policy(config_path: Optional[Path] = None) -> Dict[str, Any]:
    path = config_path or REPO_ROOT / "config" / "quality" / "memorable_line_registry_policy.yaml"
    if not path.exists():
        return {
            "max_occurrences_global": 2,
            "max_occurrences_per_brand": 1,
            "max_occurrences_per_wave": 1,
            "strength_levels_tracked": ["good", "great"],
            "block_on_violation": True,
        }
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("memorable_line_registry") or data
    except Exception:
        return {
            "max_occurrences_global": 2,
            "max_occurrences_per_brand": 1,
            "max_occurrences_per_wave": 1,
            "strength_levels_tracked": ["good", "great"],
            "block_on_violation": True,
        }


def load_registry_jsonl(jsonl_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load append-only JSONL into by-hash index. Each line is one event:
    { line_hash, normalized_text, book_id?, brand_id?, strength?, seen_at? }.
    """
    index: Dict[str, Dict[str, Any]] = {}
    if not jsonl_path.exists():
        return index
    for raw in jsonl_path.read_text(encoding="utf-8").strip().splitlines():
        if not raw.strip():
            continue
        try:
            rec = json.loads(raw)
            h = rec.get("line_hash")
            if not h:
                continue
            if h not in index:
                index[h] = {
                    "line_hash": h,
                    "normalized_text": rec.get("normalized_text", ""),
                    "first_seen_book_id": rec.get("book_id"),
                    "occurrence_count": 0,
                    "books": [],
                    "brands": [],
                    "strength_max": rec.get("strength", "ok"),
                    "last_seen_at": rec.get("seen_at", ""),
                }
            ent = index[h]
            ent["occurrence_count"] = ent.get("occurrence_count", 0) + 1
            bid = rec.get("book_id")
            if bid and bid not in ent.get("books", []):
                ent.setdefault("books", []).append(bid)
            brand = rec.get("brand_id")
            if brand and brand not in ent.get("brands", []):
                ent.setdefault("brands", []).append(brand)
            s = (rec.get("strength") or "ok").lower()
            if s == "great" or ent.get("strength_max") == "great":
                ent["strength_max"] = "great"
            elif s == "good" and ent.get("strength_max") != "great":
                ent["strength_max"] = "good"
            ent["last_seen_at"] = rec.get("seen_at") or ent.get("last_seen_at", "")
        except (json.JSONDecodeError, KeyError):
            continue
    return index


def append_record(jsonl_path: Path, record: Dict[str, Any]) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_snapshot(index: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    lines = []
    for ent in index.values():
        lines.append({
            "line_hash": ent["line_hash"],
            "normalized_text": ent.get("normalized_text", ""),
            "first_seen_book_id": ent.get("first_seen_book_id"),
            "occurrence_count": ent.get("occurrence_count", 0),
            "books": list(ent.get("books", [])),
            "brands": list(ent.get("brands", [])),
            "strength_max": ent.get("strength_max", "ok"),
            "last_seen_at": ent.get("last_seen_at", ""),
        })
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ"),
        "lines": lines,
    }


def extract_lines_from_bundle(bundle_path: Path) -> List[tuple]:
    """
    Extract (normalized_text, strength, book_id, brand_id) from bundle.
    Only includes strength in strength_levels_tracked (default good, great).
    """
    try:
        data = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    book_id = data.get("book_id", "")
    brand_id = data.get("brand_id") or ""
    tool = (data.get("tool_results") or {}).get("memorable_line_detector") or {}
    line_list = tool.get("lines") or []
    policy = load_policy()
    tracked = set(policy.get("strength_levels_tracked") or ["good", "great"])
    out = []
    for item in line_list:
        strength = (item.get("strength") or "ok").lower()
        if strength not in tracked:
            continue
        text = (item.get("text") or "").strip()
        if not text:
            continue
        norm = normalize_line(text)
        if not norm:
            continue
        out.append((norm, strength, book_id, brand_id))
    return out
