"""
Tests for EI V2 marketing lexicon loader.

Unit tests (valid fixture), fail-safe (corruption), and calibration gate (locked thresholds).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.quality.ei_v2.marketing_lexicons import (
    invalidate_marketing_cache,
    lexicon_tokenize,
    load_marketing_lexicons,
    get_persona_topic_lexicons,
    get_banned_clinical_and_forbidden,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "ei_v2_marketing"
REPO_ROOT = Path(__file__).resolve().parent.parent
CALIBRATION_EVAL_PATH = Path(__file__).resolve().parent / "fixtures" / "ei_v2_marketing_calibration_eval.json"

# Locked calibration thresholds (plan)
MAX_DELTA_DOMAIN_SIM = 0.12
MAX_DELTA_SAFETY = 0.10


class TestLexiconTokenize:
    """Shared tokenizer: lowercase, normalize, min length 2."""

    def test_lowercase(self):
        assert lexicon_tokenize("Hello World") == ["hello", "world"]

    def test_min_length(self):
        assert "a" not in lexicon_tokenize("a bc def")
        assert "bc" in lexicon_tokenize("a bc def")

    def test_empty(self):
        assert lexicon_tokenize("") == []
        assert lexicon_tokenize(None) == []


class TestLoadMarketingLexicons:
    """Unit test: load from valid fixture."""

    def setup_method(self):
        invalidate_marketing_cache()

    def test_load_valid_fixture(self):
        cfg = {
            "marketing_sources": {
                "enabled": True,
                "source_path": str(FIXTURES_DIR),
                "use_marketing_lexicons": True,
                "use_marketing_safety_bans": True,
            }
        }
        result = load_marketing_lexicons(cfg, repo_root=REPO_ROOT)
        assert result is not None
        persona_lex, topic_lex, banned, forbidden, hashes = result
        assert "gen_z_professionals" in persona_lex
        assert "anxiety" in topic_lex
        assert "burnout" in topic_lex
        assert "generalized anxiety disorder" in banned or any("generalized" in b for b in banned)
        assert "file_02_hash" in hashes
        assert "file_03_hash" in hashes
        assert "file_04_hash" in hashes

    def test_get_persona_topic_returns_empty_when_disabled(self):
        cfg = {"marketing_sources": {"enabled": False}}
        p, t = get_persona_topic_lexicons(cfg, repo_root=REPO_ROOT)
        assert p == {}
        assert t == {}

    def test_get_banned_returns_empty_when_safety_bans_disabled(self):
        cfg = {"marketing_sources": {"enabled": True, "use_marketing_safety_bans": False}}
        b, f = get_banned_clinical_and_forbidden(cfg, repo_root=REPO_ROOT)
        assert b == set()
        assert f == set()


class TestFailSafe:
    """Corruption tests: graceful fallback, no crash."""

    def setup_method(self):
        invalidate_marketing_cache()

    def test_missing_file_fallback(self):
        cfg = {
            "marketing_sources": {
                "enabled": True,
                "source_path": str(REPO_ROOT / "nonexistent_marketing_dir"),
                "use_marketing_lexicons": True,
            }
        }
        result = load_marketing_lexicons(cfg, repo_root=REPO_ROOT)
        assert result is None

    def test_bad_yaml_fallback(self, tmp_path):
        bad = tmp_path / "02_emotional_vocabulary_patch.yaml"
        bad.write_text("not: valid: yaml: [")
        (tmp_path / "03_consumer_language_by_topic.yaml").write_text("topics: []")
        (tmp_path / "04_invisible_scripts.yaml").write_text("scripts: []")
        cfg = {
            "marketing_sources": {
                "enabled": True,
                "source_path": str(tmp_path),
                "use_marketing_lexicons": True,
            }
        }
        result = load_marketing_lexicons(cfg, repo_root=REPO_ROOT)
        assert result is None

    def test_empty_topics_fallback(self, tmp_path):
        (tmp_path / "02_emotional_vocabulary_patch.yaml").write_text("global_constraints:\n  forbidden_title_tokens: []")
        (tmp_path / "03_consumer_language_by_topic.yaml").write_text("topics: []")
        (tmp_path / "04_invisible_scripts.yaml").write_text("scripts: []")
        cfg = {
            "marketing_sources": {
                "enabled": True,
                "source_path": str(tmp_path),
                "use_marketing_lexicons": True,
            }
        }
        result = load_marketing_lexicons(cfg, repo_root=REPO_ROOT)
        assert result is None

    def test_missing_required_key_03_fallback(self, tmp_path):
        (tmp_path / "02_emotional_vocabulary_patch.yaml").write_text("global_constraints:\n  forbidden_title_tokens: []")
        (tmp_path / "03_consumer_language_by_topic.yaml").write_text("{}")
        (tmp_path / "04_invisible_scripts.yaml").write_text("scripts: []")
        cfg = {
            "marketing_sources": {
                "enabled": True,
                "source_path": str(tmp_path),
                "use_marketing_lexicons": True,
            }
        }
        result = load_marketing_lexicons(cfg, repo_root=REPO_ROOT)
        assert result is None


class TestCalibrationGate:
    """Locked thresholds: domain_thesis_similarity delta <= 0.12, safety delta <= 0.10."""

    def setup_method(self):
        invalidate_marketing_cache()

    def test_calibration_deltas_within_bounds(self):
        if not CALIBRATION_EVAL_PATH.exists():
            pytest.skip("Calibration eval fixture not found")
        eval_data = json.loads(CALIBRATION_EVAL_PATH.read_text())
        from phoenix_v4.quality.ei_v2.domain_embeddings import domain_thesis_similarity
        from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config

        cfg = load_ei_v2_config()
        cfg_off = {**cfg, "marketing_sources": {**cfg.get("marketing_sources", {}), "enabled": False}}
        cfg_on = {**cfg, "marketing_sources": {**cfg.get("marketing_sources", {}), "enabled": True, "source_path": str(FIXTURES_DIR)}}
        invalidate_marketing_cache()

        domain_deltas = []
        safety_deltas = []
        for item in eval_data[:2]:
            passage = item["passage"]
            thesis = item["thesis"]
            persona_id = item.get("persona_id", "")
            topic_id = item.get("topic_id", "")
            domain_cfg = cfg.get("domain_embeddings", {})
            safety_cfg = cfg.get("safety_classifier", {})

            sim_off = domain_thesis_similarity(thesis, passage, persona_id=persona_id, topic_id=topic_id, cfg=cfg_off)
            sim_on = domain_thesis_similarity(thesis, passage, persona_id=persona_id, topic_id=topic_id, cfg=cfg_on)
            domain_deltas.append(abs(sim_on - sim_off))

            res_off = classify_safety(passage, cfg=safety_cfg, full_cfg=cfg_off)
            res_on = classify_safety(passage, cfg=safety_cfg, full_cfg=cfg_on)
            safety_deltas.append(abs(res_on["risk_score"] - res_off["risk_score"]))

        max_domain_delta = max(domain_deltas) if domain_deltas else 0
        max_safety_delta = max(safety_deltas) if safety_deltas else 0
        assert max_domain_delta <= MAX_DELTA_DOMAIN_SIM, f"domain_thesis_similarity delta {max_domain_delta} > {MAX_DELTA_DOMAIN_SIM}"
        assert max_safety_delta <= MAX_DELTA_SAFETY, f"safety risk_score delta {max_safety_delta} > {MAX_DELTA_SAFETY}"
