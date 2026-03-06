"""
Marketing lexicon loader for EI V2.

Loads persona/topic lexicons and banned terms from marketing_deep_research (02, 03, 04).
Schema version 1; on mismatch: warn + fallback. One shared tokenizer for loader and tests.
Observability: artifacts/ei_v2/marketing_integration.log (JSONL, locked fields).
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    yaml = None

_SCHEMA_VERSION = 1
_MIN_TOKEN_LEN = 2
_LOG_PATH = Path("artifacts/ei_v2/marketing_integration.log")

# Cache: (persona_lexicons, topic_lexicons, banned_clinical, forbidden_tokens, file_hashes)
# keyed by (source_path, mtime_02, mtime_03, mtime_04). None = not loaded or disabled.
_CACHE: Optional[Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Set[str], Set[str], Dict[str, str]]] = None
_CACHE_KEY: Optional[Tuple[Optional[str], float, float, float]] = None


def lexicon_tokenize(text: str) -> List[str]:
    """
    Deterministic tokenizer: lowercase, NFKC, word tokens, strip punctuation, min length.
    Shared by loader and tests. No stopwords for lexicon build.
    """
    if not text or not isinstance(text, str):
        return []
    normalized = unicodedata.normalize("NFKC", text.lower())
    tokens = re.findall(r"\b\w+\b", normalized)
    return [t for t in tokens if len(t) >= _MIN_TOKEN_LEN]


def _file_hash(path: Path) -> str:
    """Content hash (SHA256 hex) for observability."""
    if not path.exists():
        return ""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    except Exception:
        return ""


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def _write_log_record(record: Dict[str, Any], repo_root: Path) -> None:
    log_path = repo_root / _LOG_PATH
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.warning("marketing_lexicons: could not write observability log: %s", e)


def _validate_02(data: Any, path: Path) -> Tuple[bool, Optional[str]]:
    if not isinstance(data, dict):
        return False, "02: root is not a dict"
    if "global_constraints" not in data:
        return False, "02: missing global_constraints"
    gc = data["global_constraints"]
    if not isinstance(gc, dict):
        return False, "02: global_constraints is not a dict"
    if "forbidden_title_tokens" not in gc:
        return False, "02: missing global_constraints.forbidden_title_tokens"
    if not isinstance(gc["forbidden_title_tokens"], list):
        return False, "02: forbidden_title_tokens is not a list"
    return True, None


def _validate_03(data: Any, path: Path) -> Tuple[bool, Optional[str]]:
    if not isinstance(data, dict):
        return False, "03: root is not a dict"
    if "topics" not in data:
        return False, "03: missing topics"
    topics = data["topics"]
    if not isinstance(topics, list):
        return False, "03: topics is not a list"
    if len(topics) == 0:
        return False, "03: topics is empty"
    for i, t in enumerate(topics):
        if not isinstance(t, dict):
            return False, f"03: topics[{i}] is not a dict"
        if "topic_id" not in t:
            return False, f"03: topics[{i}].topic_id missing"
        for key in ("consumer_phrases", "banned_clinical_terms", "culture_specific_phrases", "persona_subtitle_patterns"):
            if key not in t:
                return False, f"03: topics[{i}].{key} missing"
            if not isinstance(t[key], list):
                return False, f"03: topics[{i}].{key} is not a list"
    return True, None


def _validate_04(data: Any, path: Path) -> Tuple[bool, Optional[str]]:
    if not isinstance(data, dict):
        return False, "04: root is not a dict"
    if "scripts" not in data:
        return False, "04: missing scripts"
    scripts = data["scripts"]
    if not isinstance(scripts, list):
        return False, "04: scripts is not a list"
    for i, s in enumerate(scripts):
        if not isinstance(s, dict):
            return False, f"04: scripts[{i}] is not a dict"
        for key in ("persona_id", "topic_id", "invisible_script"):
            if key not in s:
                return False, f"04: scripts[{i}].{key} missing"
    return True, None


def _load_yaml(path: Path) -> Tuple[Any, Optional[str]]:
    if not path.exists():
        return None, "file_missing"
    if yaml is None:
        return None, "yaml_not_available"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data, None
    except Exception as e:
        return None, f"yaml_error: {e!s}"


def invalidate_marketing_cache() -> None:
    """Clear loader cache. Use in tests or admin."""
    global _CACHE, _CACHE_KEY
    _CACHE = None
    _CACHE_KEY = None


def load_marketing_lexicons(
    cfg: Dict[str, Any],
    repo_root: Optional[Path] = None,
) -> Optional[Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Set[str], Set[str], Dict[str, str]]]:
    """
    Load persona lexicons, topic lexicons, banned clinical terms, forbidden tokens, and file hashes.
    Returns None if disabled, or if any required file is missing/malformed (then fallback per component).
    On success returns (persona_lexicons, topic_lexicons, banned_clinical, forbidden_tokens, file_hashes).
    """
    global _CACHE, _CACHE_KEY
    ms = cfg.get("marketing_sources") or {}
    if not ms.get("enabled", False):
        return None
    if not ms.get("use_marketing_lexicons", True) and not ms.get("use_marketing_safety_bans", True):
        return None
    source_path = ms.get("source_path", "").strip()
    if not source_path:
        return None
    repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
    base = repo_root / source_path
    if not base.is_dir():
        logging.warning("marketing_lexicons: source_path not a dir: %s", base)
        return None

    path_02 = base / "02_emotional_vocabulary_patch.yaml"
    path_03 = base / "03_consumer_language_by_topic.yaml"
    path_04 = base / "04_invisible_scripts.yaml"
    mtimes = (_mtime(path_02), _mtime(path_03), _mtime(path_04))
    cache_key = (source_path, mtimes[0], mtimes[1], mtimes[2])
    if _CACHE_KEY == cache_key and _CACHE is not None:
        return _CACHE

    hashes = {
        "file_02_hash": _file_hash(path_02),
        "file_03_hash": _file_hash(path_03),
        "file_04_hash": _file_hash(path_04),
    }
    fallback_reasons: List[str] = []

    # Load 03 (topic lexicons + banned clinical)
    data_03, load_err_03 = _load_yaml(path_03)
    if load_err_03:
        fallback_reasons.append(f"03: {load_err_03}")
        topic_lexicons: Dict[str, Set[str]] = {}
        banned_clinical: Set[str] = set()
    else:
        ok, reason = _validate_03(data_03, path_03)
        if not ok:
            fallback_reasons.append(f"03: {reason}")
            topic_lexicons = {}
            banned_clinical = set()
        else:
            topic_lexicons = {}
            banned_clinical = set()
            for t in data_03["topics"]:
                tid = str(t.get("topic_id", ""))
                tokens = set()
                for phrase in (t.get("consumer_phrases") or []) + (t.get("culture_specific_phrases") or []):
                    if phrase and isinstance(phrase, str):
                        tokens.update(lexicon_tokenize(phrase))
                if tid:
                    topic_lexicons[tid] = tokens
                for term in t.get("banned_clinical_terms") or []:
                    if term and isinstance(term, str):
                        banned_clinical.add(term.strip().lower())

    # Load 04 (persona lexicons from invisible_script)
    data_04, load_err_04 = _load_yaml(path_04)
    if load_err_04:
        fallback_reasons.append(f"04: {load_err_04}")
        persona_lexicons = {}
    else:
        ok, reason = _validate_04(data_04, path_04)
        if not ok:
            fallback_reasons.append(f"04: {reason}")
            persona_lexicons = {}
        else:
            persona_lexicons = {}
            for s in data_04.get("scripts") or []:
                pid = str(s.get("persona_id", ""))
                script = (s.get("invisible_script") or "").strip()
                if not pid:
                    continue
                if pid not in persona_lexicons:
                    persona_lexicons[pid] = set()
                if script:
                    persona_lexicons[pid].update(lexicon_tokenize(script))
            for pid in list(persona_lexicons.keys()):
                if not persona_lexicons[pid]:
                    del persona_lexicons[pid]

    # Load 02 (forbidden tokens)
    data_02, load_err_02 = _load_yaml(path_02)
    if load_err_02:
        fallback_reasons.append(f"02: {load_err_02}")
        forbidden_tokens: Set[str] = set()
    else:
        ok, reason = _validate_02(data_02, path_02)
        if not ok:
            fallback_reasons.append(f"02: {reason}")
            forbidden_tokens = set()
        else:
            forbidden_tokens = set()
            for w in (data_02.get("global_constraints") or {}).get("forbidden_title_tokens") or []:
                if w and isinstance(w, str):
                    forbidden_tokens.add(w.strip().lower())

    use_marketing = bool(persona_lexicons or topic_lexicons)
    if not use_marketing and fallback_reasons:
        for r in fallback_reasons:
            logging.warning("marketing_lexicons: fallback %s", r)
        _write_log_record({
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event": "lexicon_load",
            "source": "built-in",
            "source_path": source_path,
            "file_02_hash": hashes["file_02_hash"],
            "file_03_hash": hashes["file_03_hash"],
            "file_04_hash": hashes["file_04_hash"],
            "fallback_reason": "; ".join(fallback_reasons),
        }, repo_root)
        _CACHE_KEY = cache_key
        _CACHE = None
        return None

    _write_log_record({
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": "lexicon_load",
        "source": "marketing",
        "source_path": source_path,
        "file_02_hash": hashes["file_02_hash"],
        "file_03_hash": hashes["file_03_hash"],
        "file_04_hash": hashes["file_04_hash"],
        "fallback_reason": "",
    }, repo_root)
    _CACHE_KEY = cache_key
    _CACHE = (persona_lexicons, topic_lexicons, banned_clinical, forbidden_tokens, hashes)
    return _CACHE


def get_persona_topic_lexicons(
    cfg: Dict[str, Any],
    repo_root: Optional[Path] = None,
) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """
    Return (persona_lexicons, topic_lexicons). If marketing disabled, use_lexicons false, or load fails,
    returns ({}, {}); caller uses built-in. If non-empty, caller uses marketing data.
    """
    ms = cfg.get("marketing_sources") or {}
    if not ms.get("use_marketing_lexicons", True):
        return {}, {}
    result = load_marketing_lexicons(cfg, repo_root)
    if result is None:
        return {}, {}
    persona, topic, _, _, _ = result
    return persona, topic


def get_banned_clinical_and_forbidden(
    cfg: Dict[str, Any],
    repo_root: Optional[Path] = None,
) -> Tuple[Set[str], Set[str]]:
    """Return (banned_clinical_terms, forbidden_tokens). Empty sets if use_safety_bans false or load fails."""
    ms = cfg.get("marketing_sources") or {}
    if not ms.get("use_marketing_safety_bans", True):
        return set(), set()
    result = load_marketing_lexicons(cfg, repo_root)
    if result is None:
        return set(), set()
    _, _, banned, forbidden, _ = result
    return banned, forbidden
