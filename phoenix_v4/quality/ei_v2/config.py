"""
EI V2 config loader.

Loads from config/quality/ei_v2_config.yaml with sensible defaults.
All modules are disabled by default — enable via config to opt in.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    yaml = None

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "quality" / "ei_v2_config.yaml"
_CACHE: Dict[str, Any] | None = None

DEFAULTS: Dict[str, Any] = {
    "safety_classifier": {
        "enabled": True,
        "mode": "heuristic_plus",
        "medical_claim_threshold": 0.6,
        "promotional_threshold": 0.5,
        "clinical_language_threshold": 0.5,
        "cache_enabled": True,
        "cache_path": "artifacts/ei_v2/safety_cache.jsonl",
    },
    "cross_encoder": {
        "enabled": True,
        "mode": "heuristic",
        "model": None,
        "cache_enabled": True,
        "cache_path": "artifacts/ei_v2/rerank_cache.db",
        "top_n": 5,
    },
    "domain_embeddings": {
        "enabled": True,
        "mode": "weighted",
        "persona_weight": 0.3,
        "topic_weight": 0.3,
        "thesis_weight": 0.4,
        "cache_enabled": True,
        "cache_path": "artifacts/ei_v2/domain_embed_cache.db",
    },
    "tts_readability": {
        "enabled": True,
        "max_sentence_words": 35,
        "ideal_sentence_range": [8, 25],
        "min_paragraph_breaks_per_500_words": 3,
        "rhythm_variance_min": 0.15,
        "problematic_tts_patterns": [
            r"\b\w{15,}\b",
            r"\([^)]{50,}\)",
            r";\s*\w+;\s*\w+;",
        ],
    },
    "semantic_dedup": {
        "enabled": True,
        "mode": "ngram_plus_embedding",
        "ngram_n": 6,
        "ngram_overlap_threshold": 0.30,
        "semantic_similarity_threshold": 0.85,
        "cache_enabled": True,
        "cache_path": "artifacts/ei_v2/dedup_cache.db",
    },
    "emotion_arc": {
        "enabled": True,
        "mode": "lexicon",
        "valence_lexicon_size": "medium",
        "arc_deviation_warn": 0.3,
        "arc_deviation_fail": 0.6,
    },
    "composite_weights": {
        "rerank": 0.35,
        "safety": 0.25,
        "domain_similarity": 0.20,
        "tts_readability": 0.20,
    },
}


def load_ei_v2_config(path: Path | None = None) -> Dict[str, Any]:
    """Load V2 config, merging file values over defaults."""
    global _CACHE
    if _CACHE is not None and path is None:
        return _CACHE

    cfg = _deep_copy_dict(DEFAULTS)
    config_path = path or _CONFIG_PATH
    if config_path.exists() and yaml is not None:
        try:
            file_cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            cfg = _deep_merge(cfg, file_cfg)
        except Exception:
            pass

    if path is None:
        _CACHE = cfg
    return cfg


def _deep_copy_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out[k] = _deep_copy_dict(v)
        elif isinstance(v, list):
            out[k] = list(v)
        else:
            out[k] = v
    return out


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = _deep_copy_dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result
