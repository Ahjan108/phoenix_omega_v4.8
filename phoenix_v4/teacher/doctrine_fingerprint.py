"""
Doctrine canonicalization and fingerprinting for Teacher Mode (plan §3.8).
Same doctrine content → same hash; harmless formatting changes → same hash.
"""
from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any, Optional

# Order-insensitive list keys (sort for canonical order); all others keep order
ORDER_INSENSITIVE_LISTS = frozenset({
    "primary_methods", "core_principles", "tone_profile", "forbidden_language",
    "allowed_sources", "signature_metaphors", "signature_practices", "avoid_claims",
    "forbidden", "avoid_language",
})

# Non-doctrinal keys to strip before hashing (plan §3.8 Step C)
STRIP_KEYS = frozenset({
    "last_updated", "author", "notes", "review_status", "source_paths",
    "ingest_run_id", "updated_at", "debug", "debug_*", "metadata",
})


def _normalize_string(s: str) -> str:
    if not isinstance(s, str):
        return str(s)
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\r\n", "\n").replace("\r", "\n").strip()
    if "\n" not in s:
        s = " ".join(s.split())
    return s


def _filter_strip_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: _filter_strip_keys(v)
            for k, v in obj.items()
            if k not in STRIP_KEYS and not (isinstance(k, str) and k.startswith("debug_"))
            and v is not None
        }
    if isinstance(obj, list):
        return [_filter_strip_keys(x) for x in obj if x is not None]
    if isinstance(obj, str):
        return _normalize_string(obj)
    return obj


def _canonicalize_value(val: Any, parent_key: Optional[str], oi: frozenset) -> Any:
    if val is None:
        return None
    if isinstance(val, dict):
        out = {}
        for k in sorted(val.keys(), key=lambda x: (str(x),)):
            if val[k] is None:
                continue
            out[k] = _canonicalize_value(val[k], k, oi)
        return out
    if isinstance(val, list):
        cleaned = [_canonicalize_value(x, None, oi) for x in val if x is not None]
        if parent_key and parent_key in oi:
            try:
                cleaned.sort(key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
            except TypeError:
                pass
        return cleaned
    if isinstance(val, str):
        return _normalize_string(val)
    if isinstance(val, (int, float, bool)):
        return val
    return val


def canonicalize_doctrine(obj: Any, order_insensitive_lists: Optional[frozenset] = None) -> Any:
    """
    Normalize doctrine dict for fingerprinting: strip non-doctrinal keys, normalize strings (NFKC, strip),
    sort keys recursively, stable list ordering for order-insensitive lists (plan §3.8 Steps B–E).
    """
    oi = order_insensitive_lists or ORDER_INSENSITIVE_LISTS
    # Strip non-doctrinal keys only at top level (filter recurses internally)
    raw = _filter_strip_keys(obj) if isinstance(obj, dict) else obj
    return _canonicalize_value(raw, None, oi)


def fingerprint_doctrine(obj: Any) -> str:
    """Canonical JSON (sorted keys, no trailing newline) then sha256 hex (plan §3.8 Step F–G)."""
    canonical = canonicalize_doctrine(obj)
    payload = json.dumps(canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    if payload.endswith("\n"):
        payload = payload[:-1]
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_doctrine_yaml(path: Path) -> dict[str, Any]:
    """Load doctrine YAML from path. Fails on duplicate keys / anchors if using safe_load."""
    path = Path(path)
    if not path.exists():
        return {}
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return dict(data) if data else {}
    except Exception:
        return {}
