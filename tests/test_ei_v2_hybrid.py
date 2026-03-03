"""
Tests for EI V2 hybrid selector, learner, dimension gates, and catalog calibrator.

Covers:
  - Learner: feedback logging, learning cycle, parameter persistence
  - Hybrid Selector: override logic, block logic, V1-keeps-winning default
  - Dimension Gates: uniqueness, engagement, somatic precision, listen, cohesion
  - Config: hybrid section loads correctly
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

# ---- Sample data reused across tests ----

SAMPLE_TEXT_SOMATIC = (
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

SAMPLE_TEXT_FLAT = (
    "Anxiety is a problem. Many people have anxiety. It is common. "
    "You should try to relax. Relaxation is important. "
    "There are many ways to relax. You can try breathing. "
    "Breathing is helpful. It can calm you down."
)

SAMPLE_TEXT_ENGAGING = (
    "That morning, everything changed. You know that feeling — the one where your "
    "stomach drops before your mind catches up? Here's the thing: your body already "
    "knows what's happening.\n\n"
    "But then something unexpected occurred. Until that moment, Sarah had believed "
    "the catch was that anxiety meant something was wrong with her. Yet the problem "
    "was never the alarm — it was what she believed the alarm meant.\n\n"
    "Remember when we talked about the body's alarm system? This pattern shows up "
    "again and again. What comes next will change how you think about every anxious "
    "moment you've ever had. Stay with this."
)

SAMPLE_TEXT_DUPLICATE = (
    "That morning, Sarah opened her laptop at the kitchen table. Her jaw was tight. "
    "Her shoulders pulled up toward her ears. The email subject line read 'Urgent: Q3 Review.' "
    "She hadn't opened it yet, but her body had already decided what it meant."
)


# ============================================================
#  Learner Tests
# ============================================================

class TestLearner:
    def test_feedback_roundtrip(self, tmp_path):
        from phoenix_v4.quality.ei_v2.learner import (
            FeedbackRecord, log_feedback, load_feedback
        )
        p = tmp_path / "fb.jsonl"
        rec = FeedbackRecord(
            timestamp="2026-03-03T00:00:00Z",
            slot="STORY", chapter_index=0,
            persona_id="gen_z", topic_id="anxiety",
            v1_chosen_id="a1", v2_chosen_id="a2",
            hybrid_chosen_id="a1", override_applied=False,
            v1_composite=0.6, v2_composite=0.7, margin=0.1,
        )
        log_feedback(rec, p)
        log_feedback(rec, p)
        loaded = load_feedback(p)
        assert len(loaded) == 2
        assert loaded[0].slot == "STORY"

    def test_feedback_limit(self, tmp_path):
        from phoenix_v4.quality.ei_v2.learner import (
            FeedbackRecord, log_feedback, load_feedback
        )
        p = tmp_path / "fb.jsonl"
        for i in range(20):
            rec = FeedbackRecord(
                timestamp=f"2026-03-03T00:00:{i:02d}Z",
                slot="STORY", chapter_index=i % 8,
                persona_id="gen_z", topic_id="anxiety",
                v1_chosen_id="a1", v2_chosen_id="a2",
                hybrid_chosen_id="a1", override_applied=(i % 3 == 0),
                v1_composite=0.5, v2_composite=0.6, margin=0.1,
                dimension_scores={"engagement": 0.3, "somatic_precision": 0.4},
            )
            log_feedback(rec, p)
        loaded = load_feedback(p, limit=5)
        assert len(loaded) == 5

    def test_learn_default_params(self, tmp_path):
        from phoenix_v4.quality.ei_v2.learner import load_learned_params
        params = load_learned_params(tmp_path / "nonexistent.json")
        assert params.version == 0
        assert "rerank" in params.composite_weights
        assert params.override_margin == 0.12

    def test_learn_persists(self, tmp_path):
        from phoenix_v4.quality.ei_v2.learner import (
            FeedbackRecord, log_feedback, learn, load_learned_params
        )
        fb_path = tmp_path / "fb.jsonl"
        params_path = tmp_path / "params.json"
        for i in range(15):
            rec = FeedbackRecord(
                timestamp=f"2026-03-03T00:00:{i:02d}Z",
                slot="STORY", chapter_index=i % 5,
                persona_id="gen_z", topic_id="anxiety",
                v1_chosen_id="a1", v2_chosen_id="a2",
                hybrid_chosen_id="a1",
                override_applied=(i % 4 == 0),
                v1_composite=0.5, v2_composite=0.55, margin=0.05,
                dimension_scores={
                    "engagement": 0.15,
                    "somatic_precision": 0.20,
                    "uniqueness": 0.80,
                },
            )
            log_feedback(rec, fb_path)

        params = learn(fb_path, params_path, window=50)
        assert params.version == 1
        assert params.total_observations == 15
        assert params_path.exists()

        reloaded = load_learned_params(params_path)
        assert reloaded.version == 1

    def test_learn_boosts_weak_dimensions(self, tmp_path):
        from phoenix_v4.quality.ei_v2.learner import (
            FeedbackRecord, log_feedback, learn
        )
        fb_path = tmp_path / "fb.jsonl"
        params_path = tmp_path / "params.json"
        for i in range(20):
            rec = FeedbackRecord(
                timestamp=f"2026-03-03T00:00:{i:02d}Z",
                slot="STORY", chapter_index=0,
                persona_id="gen_z", topic_id="anxiety",
                v1_chosen_id="a1", v2_chosen_id="a2",
                hybrid_chosen_id="a1", override_applied=False,
                dimension_scores={
                    "engagement": 0.10,
                    "somatic_precision": 0.12,
                },
            )
            log_feedback(rec, fb_path)

        params = learn(fb_path, params_path)
        assert params.dimension_ema.get("engagement", 1.0) < 0.25


# ============================================================
#  Dimension Gates Tests
# ============================================================

class TestDimensionGates:
    def test_gate_engagement_pass(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_engagement
        result = gate_engagement(SAMPLE_TEXT_ENGAGING, chapter_index=1)
        assert result.dimension == "engagement"
        assert result.status in ("PASS", "WARN")
        assert result.score > 0.2

    def test_gate_engagement_fail(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_engagement
        result = gate_engagement(SAMPLE_TEXT_FLAT, chapter_index=1)
        assert result.status in ("FAIL", "WARN")
        assert len(result.issues) > 0

    def test_gate_somatic_pass(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_somatic_precision
        result = gate_somatic_precision(SAMPLE_TEXT_SOMATIC)
        assert result.dimension == "somatic_precision"
        assert result.score > 0.3

    def test_gate_somatic_low_for_flat_text(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_somatic_precision
        result = gate_somatic_precision(SAMPLE_TEXT_FLAT)
        somatic_result = gate_somatic_precision(SAMPLE_TEXT_SOMATIC)
        assert result.score < somatic_result.score

    def test_gate_uniqueness_single_chapter(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_uniqueness
        result = gate_uniqueness(SAMPLE_TEXT_SOMATIC, [SAMPLE_TEXT_SOMATIC], 0)
        assert result.dimension == "uniqueness"
        assert result.status == "PASS"

    def test_gate_uniqueness_duplicate_chapters(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_uniqueness
        texts = [SAMPLE_TEXT_DUPLICATE, SAMPLE_TEXT_DUPLICATE + " And she breathed."]
        result = gate_uniqueness(texts[0], texts, 0)
        assert result.score < 1.0

    def test_gate_listen_experience(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_listen_experience
        result = gate_listen_experience(SAMPLE_TEXT_SOMATIC)
        assert result.dimension == "listen_experience"
        assert 0.0 <= result.score <= 1.0

    def test_gate_cohesion_chapter_0(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_cohesion
        result = gate_cohesion(SAMPLE_TEXT_ENGAGING, chapter_index=0)
        assert result.score == 0.5

    def test_gate_cohesion_later_chapter(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_cohesion
        result = gate_cohesion(SAMPLE_TEXT_ENGAGING, chapter_index=2)
        assert result.dimension == "cohesion"
        assert result.score > 0

    def test_enforce_all_gates(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import enforce_chapter_gates
        texts = [SAMPLE_TEXT_ENGAGING, SAMPLE_TEXT_SOMATIC, SAMPLE_TEXT_FLAT]
        report = enforce_chapter_gates(texts[0], 0, texts)
        assert report.chapter_index == 0
        assert len(report.gates) == 5
        assert report.overall_status in ("PASS", "WARN", "FAIL")

    def test_enforce_fail_mode_block_raises(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import (
            DimensionGateBlockError,
            enforce_chapter_gates,
        )
        # Use very short flat text that will fail multiple gates
        cfg = {"fail_mode": "block", "engagement": {"pass_threshold": 0.99}}
        with pytest.raises(DimensionGateBlockError) as exc_info:
            enforce_chapter_gates(SAMPLE_TEXT_FLAT, 0, [SAMPLE_TEXT_FLAT], cfg)
        assert exc_info.value.report.fail_count > 0

    def test_enforce_fail_mode_warn_returns(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import enforce_chapter_gates
        cfg = {"fail_mode": "warn"}
        report = enforce_chapter_gates(SAMPLE_TEXT_FLAT, 0, [SAMPLE_TEXT_FLAT], cfg)
        assert report.chapter_index == 0
        assert report.overall_status in ("PASS", "WARN", "FAIL")

    def test_enforce_flat_chapter_gets_warnings(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import enforce_chapter_gates
        texts = [SAMPLE_TEXT_FLAT, SAMPLE_TEXT_SOMATIC]
        report = enforce_chapter_gates(texts[0], 0, texts)
        assert report.warn_count + report.fail_count > 0

    def test_gate_result_to_dict(self):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_engagement
        result = gate_engagement(SAMPLE_TEXT_ENGAGING, 0)
        d = result.to_dict()
        assert "dimension" in d
        assert "score" in d
        assert isinstance(d["issues"], list)


# ============================================================
#  Hybrid Selector Tests
# ============================================================

class TestHybridSelector:
    """Tests that exercise hybrid_select logic without real V1/V2 infra."""

    def test_hybrid_decision_dataclass(self):
        from phoenix_v4.quality.ei_v2.hybrid_selector import HybridDecision
        d = HybridDecision(
            slot="STORY", chapter_index=0, slot_index=0,
            final_chosen_id="a1", v1_chosen_id="a1", v2_chosen_id="a2",
            override_applied=False,
        )
        assert d.final_chosen_id == "a1"
        out = d.to_dict()
        assert out["slot"] == "STORY"
        assert out["override_applied"] is False

    def test_compute_v2_composite(self):
        from phoenix_v4.quality.ei_v2 import EIV2AnalysisReport, EIV2CandidateReport
        from phoenix_v4.quality.ei_v2.hybrid_selector import _compute_v2_composite

        report = EIV2AnalysisReport(slot="STORY")
        report.candidates = [
            EIV2CandidateReport(
                candidate_id="a1",
                rerank_score=0.8,
                safety={"risk_score": 0.1},
                domain_similarity=0.7,
                tts_readability={"composite": 0.6},
            ),
        ]
        weights = {"rerank": 0.35, "safety": 0.25, "domain_similarity": 0.20, "tts_readability": 0.20}
        score = _compute_v2_composite("a1", report, weights)
        assert score > 0

    def test_get_candidate_safety_risk(self):
        from phoenix_v4.quality.ei_v2 import EIV2AnalysisReport, EIV2CandidateReport
        from phoenix_v4.quality.ei_v2.hybrid_selector import _get_candidate_safety_risk

        report = EIV2AnalysisReport(slot="STORY")
        report.candidates = [
            EIV2CandidateReport(candidate_id="a1", safety={"risk_score": 0.7}),
        ]
        assert _get_candidate_safety_risk("a1", report) == 0.7
        assert _get_candidate_safety_risk("missing", report) == 0.0


# ============================================================
#  Config Tests
# ============================================================

class TestConfig:
    def test_hybrid_config_loads(self):
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
        cfg = load_ei_v2_config()
        hybrid = cfg.get("hybrid", {})
        assert "override_margin" in hybrid
        assert hybrid["override_margin"] == 0.12

    def test_dimension_gates_config_loads(self):
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
        cfg = load_ei_v2_config()
        gates = cfg.get("dimension_gates", {})
        assert gates.get("enabled") is True
        assert "engagement" in gates
        assert "somatic_precision" in gates

    def test_learner_config_loads(self):
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
        cfg = load_ei_v2_config()
        learner = cfg.get("learner", {})
        assert learner.get("enabled") is True
        assert learner.get("learning_window") == 200


# ============================================================
#  Integration: Dimension Gates + Learner
# ============================================================

class TestIntegration:
    def test_gates_feed_learner(self, tmp_path):
        """Dimension gate scores can be logged to learner feedback."""
        from phoenix_v4.quality.ei_v2.dimension_gates import enforce_chapter_gates
        from phoenix_v4.quality.ei_v2.learner import (
            FeedbackRecord, log_feedback, load_feedback
        )
        texts = [SAMPLE_TEXT_ENGAGING, SAMPLE_TEXT_SOMATIC]
        report = enforce_chapter_gates(texts[0], 0, texts)

        dim_scores = {}
        for g in report.gates:
            dim_scores[g.dimension] = g.score

        fb_path = tmp_path / "fb.jsonl"
        rec = FeedbackRecord(
            timestamp="2026-03-03T00:00:00Z",
            slot="STORY", chapter_index=0,
            persona_id="gen_z", topic_id="anxiety",
            v1_chosen_id="a1", v2_chosen_id="a2",
            hybrid_chosen_id="a1", override_applied=False,
            dimension_scores=dim_scores,
        )
        log_feedback(rec, fb_path)
        loaded = load_feedback(fb_path)
        assert len(loaded) == 1
        assert "engagement" in loaded[0].dimension_scores

    def test_promotion_criteria_includes_new_gates(self):
        """Promotion criteria YAML includes dimension_gates and hybrid_override."""
        from pathlib import Path
        import yaml as _yaml
        criteria_path = Path("config/quality/ei_v2_promotion_criteria.yaml")
        if not criteria_path.exists():
            pytest.skip("criteria file not found")
        data = _yaml.safe_load(criteria_path.read_text())
        assert "dimension_gates" in data
        assert "hybrid_override" in data
        assert data["dimension_gates"]["max_chapter_fail_rate"] == 0.20
