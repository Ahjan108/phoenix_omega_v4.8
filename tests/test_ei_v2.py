"""
Tests for Enlightened Intelligence V2 modules.

Validates all six AI technique modules and the parallel adapter
run correctly with no external dependencies (heuristic modes).
"""
from __future__ import annotations

import json
import statistics
import tempfile
from pathlib import Path

import pytest

# ---- Sample data ----

SAMPLE_THESIS = "Your nervous system fires an alarm before your mind catches up. The panic is real but the threat may not be."

SAMPLE_STORY_SAFE = (
    "That morning, Sarah opened her laptop at the kitchen table. Her jaw was tight. "
    "Her shoulders pulled up toward her ears. The email subject line read 'Urgent: Q3 Review.' "
    "She hadn't opened it yet, but her body had already decided what it meant.\n\n"
    "Her chest tightened. A familiar heat rose through her throat. "
    "She noticed her hands hovering above the keyboard, not typing. Just hovering. "
    "The alarm was already running — faster than she could think about it.\n\n"
    "She paused. Took one breath. Then another. The email was still there. "
    "The alarm was still running. But she noticed something: the threat was the email. "
    "The alarm was her body. They were not the same thing."
)

SAMPLE_STORY_UNSAFE = (
    "This revolutionary technique will cure your anxiety permanently. "
    "Guaranteed results in just one session. Sign up now for my exclusive program. "
    "100% effective for all anxiety disorders including generalized anxiety disorder "
    "and post-traumatic stress disorder. You are broken but I can fix you."
)

SAMPLE_STORY_DUPLICATE = (
    "That morning, Sarah opened her laptop at the kitchen table. Her jaw was tight. "
    "Her shoulders pulled toward her ears. The email subject said 'Urgent: Q3 Review.' "
    "She hadn't opened it, but her body already decided what it meant.\n\n"
    "Her chest got tight. A familiar heat rose in her throat. "
    "She noticed her hands hovering over the keyboard. Not typing. Hovering. "
    "The alarm was already going — faster than she could process.\n\n"
    "She paused. One breath. Then another. The email was still there. "
    "The alarm was still running. But she noticed: the threat was the email. "
    "The alarm was her body. They were different things."
)


# ---- Cross-Encoder Reranker ----

class TestCrossEncoderReranker:
    def test_rerank_returns_sorted_by_score(self):
        from phoenix_v4.quality.ei_v2.cross_encoder_reranker import rerank_candidates

        texts = [SAMPLE_STORY_SAFE, "Random unrelated text about cooking pasta and butter.", SAMPLE_STORY_UNSAFE]
        ids = ["safe_story", "unrelated", "unsafe_story"]
        result = rerank_candidates(SAMPLE_THESIS, texts, ids)

        assert len(result) == 3
        assert result[0]["score"] >= result[1]["score"] >= result[2]["score"]
        # Safe story and unsafe story both share domain vocabulary with thesis;
        # the unrelated text should always rank last.
        assert result[-1]["id"] == "unrelated"

    def test_rerank_top_n(self):
        from phoenix_v4.quality.ei_v2.cross_encoder_reranker import rerank_candidates

        texts = ["text a", "text b", "text c"]
        ids = ["a", "b", "c"]
        result = rerank_candidates("thesis", texts, ids, cfg={"top_n": 2})
        assert len(result) == 2

    def test_rerank_empty_input(self):
        from phoenix_v4.quality.ei_v2.cross_encoder_reranker import rerank_candidates
        result = rerank_candidates("thesis", [], [])
        assert result == []


# ---- Safety Classifier ----

class TestSafetyClassifier:
    def test_safe_text_low_risk(self):
        from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
        result = classify_safety(SAMPLE_STORY_SAFE)
        assert result["risk_score"] < 0.3
        assert len(result["reason_codes"]) == 0

    def test_unsafe_text_high_risk(self):
        from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
        result = classify_safety(SAMPLE_STORY_UNSAFE)
        assert result["risk_score"] > 0.3
        assert len(result["reason_codes"]) > 0
        assert "medical_claim_detected" in result["reason_codes"]

    def test_promotional_detected(self):
        from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
        result = classify_safety("Sign up now for my exclusive program. Limited time offer.")
        assert result["categories"]["promotional"]["hits"] > 0

    def test_clinical_language_detected(self):
        from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
        result = classify_safety(
            "Patients diagnosed with generalized anxiety disorder show comorbidity "
            "with major depressive disorder per DSM-5 criteria."
        )
        assert result["categories"]["clinical_language"]["hits"] > 0
        assert "clinical_language_detected" in result["reason_codes"]

    def test_pathologizing_detected(self):
        from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
        result = classify_safety("You are broken. You have a dysfunctional pattern.")
        assert result["categories"]["pathologizing"]["hits"] > 0

    def test_empty_text(self):
        from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
        result = classify_safety("")
        assert result["risk_score"] == 0.0


# ---- Semantic Dedup ----

class TestSemanticDedup:
    def test_detects_near_duplicate(self):
        from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates
        texts = [SAMPLE_STORY_SAFE, SAMPLE_STORY_DUPLICATE]
        ids = ["original", "near_dupe"]
        dupes = detect_semantic_duplicates(texts, ids)
        assert len(dupes) >= 1
        assert dupes[0]["id_a"] == "original"
        assert dupes[0]["id_b"] == "near_dupe"
        assert dupes[0]["similarity"] > 0.3

    def test_no_false_positive_on_different_texts(self):
        from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates
        texts = [SAMPLE_STORY_SAFE, "A recipe for chocolate cake involves cocoa and butter."]
        ids = ["story", "recipe"]
        dupes = detect_semantic_duplicates(texts, ids)
        # Should have very low similarity
        for d in dupes:
            assert d["similarity"] < 0.5

    def test_single_text_returns_empty(self):
        from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates
        dupes = detect_semantic_duplicates(["only one text"], ["solo"])
        assert dupes == []


# ---- Emotion Arc Validator ----

class TestEmotionArcValidator:
    def test_recognition_band_2(self):
        from phoenix_v4.quality.ei_v2.emotion_arc_validator import validate_emotion_arc
        result = validate_emotion_arc(
            SAMPLE_STORY_SAFE,
            {"band": 2, "emotional_role": "RECOGNITION", "chapter_index": 0},
        )
        assert result["status"] in ("PASS", "WARN")
        assert "avg_valence" in result["metrics"]

    def test_empty_text_skip(self):
        from phoenix_v4.quality.ei_v2.emotion_arc_validator import validate_emotion_arc
        result = validate_emotion_arc("", {"band": 3, "emotional_role": "MECHANISM_PROOF"})
        assert result["status"] == "SKIP"

    def test_metrics_populated(self):
        from phoenix_v4.quality.ei_v2.emotion_arc_validator import validate_emotion_arc
        result = validate_emotion_arc(
            SAMPLE_STORY_SAFE,
            {"band": 3, "emotional_role": "MECHANISM_PROOF"},
        )
        metrics = result["metrics"]
        assert "avg_valence" in metrics
        assert "avg_arousal" in metrics
        assert "trajectory" in metrics
        assert "paragraph_count" in metrics
        assert metrics["paragraph_count"] >= 1


# ---- TTS Readability ----

class TestTTSReadability:
    def test_good_prose_scores_well(self):
        from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability
        result = score_tts_readability(SAMPLE_STORY_SAFE)
        assert result["composite"] > 0.3
        assert "dimensions" in result
        assert "metrics" in result

    def test_detects_long_sentences(self):
        from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability
        long = " ".join(["word"] * 50) + ". " + " ".join(["word"] * 50) + "."
        result = score_tts_readability(long)
        assert result["dimensions"]["sentence_length"] < 0.8
        assert any("long_sentences" in i for i in result["issues"])

    def test_empty_text(self):
        from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability
        result = score_tts_readability("")
        assert result["composite"] >= 0.0

    def test_monotone_detection(self):
        from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability
        mono = ". ".join(["This is a ten word sentence right here now"] * 10) + "."
        result = score_tts_readability(mono)
        assert result["dimensions"]["rhythm_variance"] < 0.8


# ---- Domain Embeddings ----

class TestDomainEmbeddings:
    def test_persona_affinity_boosts_score(self):
        from phoenix_v4.quality.ei_v2.domain_embeddings import domain_thesis_similarity

        text_with_persona = (
            "The notification lit up her phone screen during the group chat. "
            "School homework was piling up and her parents didn't understand."
        )
        text_generic = "A pattern emerged in the data. The mechanism was unclear."

        score_persona = domain_thesis_similarity(
            SAMPLE_THESIS, text_with_persona,
            persona_id="gen_alpha_students", topic_id="anxiety",
        )
        score_generic = domain_thesis_similarity(
            SAMPLE_THESIS, text_generic,
            persona_id="gen_alpha_students", topic_id="anxiety",
        )
        assert score_persona > score_generic

    def test_topic_coherence_matters(self):
        from phoenix_v4.quality.ei_v2.domain_embeddings import domain_thesis_similarity

        score_on_topic = domain_thesis_similarity(
            SAMPLE_THESIS,
            "The anxiety spiral started with worry and fear. Panic was rising.",
            persona_id="gen_z_professionals", topic_id="anxiety",
        )
        score_off_topic = domain_thesis_similarity(
            SAMPLE_THESIS,
            "The budget spreadsheet showed declining revenue. Quarterly targets were missed.",
            persona_id="gen_z_professionals", topic_id="anxiety",
        )
        assert score_on_topic > score_off_topic


# ---- Full V2 Analysis ----

class TestFullV2Analysis:
    def test_run_ei_v2_analysis(self):
        from phoenix_v4.quality.ei_v2 import run_ei_v2_analysis

        candidates = [
            {"id": "safe_1", "text": SAMPLE_STORY_SAFE},
            {"id": "unsafe_1", "text": SAMPLE_STORY_UNSAFE},
        ]
        report = run_ei_v2_analysis(
            slot="STORY",
            candidates=candidates,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            thesis=SAMPLE_THESIS,
            v1_chosen_id="safe_1",
        )
        assert report.slot == "STORY"
        assert len(report.candidates) == 2
        assert report.v2_chosen_id is not None
        assert report.v1_chosen_id == "safe_1"
        assert report.agreement is not None

    def test_v2_prefers_safe_over_unsafe(self):
        from phoenix_v4.quality.ei_v2 import run_ei_v2_analysis

        candidates = [
            {"id": "safe_1", "text": SAMPLE_STORY_SAFE},
            {"id": "unsafe_1", "text": SAMPLE_STORY_UNSAFE},
        ]
        report = run_ei_v2_analysis(
            slot="STORY",
            candidates=candidates,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            thesis=SAMPLE_THESIS,
        )
        assert report.v2_chosen_id == "safe_1"


# ---- Config ----

class TestConfig:
    def test_defaults_loaded(self):
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
        cfg = load_ei_v2_config()
        assert "safety_classifier" in cfg
        assert "cross_encoder" in cfg
        assert "tts_readability" in cfg
        assert cfg["safety_classifier"]["enabled"] is True

    def test_config_from_file(self):
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
        cfg = load_ei_v2_config(Path("config/quality/ei_v2_config.yaml"))
        assert cfg["safety_classifier"]["enabled"] is True
        assert cfg["cross_encoder"]["mode"] == "heuristic"


# ---- Parallel Adapter ----

class TestParallelAdapter:
    def test_compare_slot_runs(self):
        from phoenix_v4.quality.ei_parallel_adapter import compare_slot

        candidates = [{"id": "atom_1", "text": SAMPLE_STORY_SAFE, "meta": {}}]
        result = compare_slot(
            slot="STORY",
            chapter_index=0,
            slot_index=0,
            candidates_raw=candidates,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            thesis=SAMPLE_THESIS,
            v1_cfg={},
            v2_cfg=None,
        )
        assert result.v1_chosen_id == "atom_1"
        assert result.v2_chosen_id is not None
        assert result.timing_ms["v1_ms"] >= 0
        assert result.timing_ms["v2_ms"] >= 0

    def test_build_pipeline_comparison(self):
        from phoenix_v4.quality.ei_parallel_adapter import (
            compare_slot,
            build_pipeline_comparison,
        )

        candidates = [{"id": "atom_1", "text": SAMPLE_STORY_SAFE, "meta": {}}]
        results = []
        for ch in range(3):
            r = compare_slot(
                slot="STORY",
                chapter_index=ch,
                slot_index=0,
                candidates_raw=candidates,
                persona_id="gen_z_professionals",
                topic_id="anxiety",
                thesis=SAMPLE_THESIS,
                v1_cfg={},
            )
            results.append(r)

        report = build_pipeline_comparison(
            results,
            plan_hash="test_hash",
            persona_id="gen_z_professionals",
            topic_id="anxiety",
        )
        assert report.total_slots == 3
        assert report.agreement_rate >= 0.0
        assert report.timing_summary["total_v1_ms"] >= 0

    def test_write_comparison_report(self):
        from phoenix_v4.quality.ei_parallel_adapter import (
            compare_slot,
            build_pipeline_comparison,
            write_comparison_report,
        )

        candidates = [{"id": "atom_1", "text": SAMPLE_STORY_SAFE, "meta": {}}]
        r = compare_slot(
            slot="STORY", chapter_index=0, slot_index=0,
            candidates_raw=candidates,
            persona_id="gen_z_professionals", topic_id="anxiety",
            thesis=SAMPLE_THESIS, v1_cfg={},
        )
        report = build_pipeline_comparison([r], plan_hash="test")

        with tempfile.TemporaryDirectory() as td:
            path = write_comparison_report(report, Path(td))
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["total_slots"] == 1
            summary = Path(td) / "ei_v1_v2_summary.txt"
            assert summary.exists()
