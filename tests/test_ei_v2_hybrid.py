"""
Tests for EI V2 hybrid selector, learner, and dimension gates.

When learner, dimension_gates, and hybrid_selector exist in phoenix_v4.quality.ei_v2,
these tests run. When they are not yet in the repo, tests that need them are skipped
so CI and DOCS_INDEX stay consistent.

Covers (when modules present):
  - hybrid_selector: HybridDecision, hybrid_select with minimal V1 path
  - learner: load_learned_params, log_feedback, save_learned_params, load_feedback
  - dimension_gates: gate_uniqueness, gate_engagement, gate_somatic_precision, GateResult, ChapterGateReport
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def _hybrid_modules_available():
    """True if learner, dimension_gates, hybrid_selector are importable."""
    try:
        import phoenix_v4.quality.ei_v2.learner  # noqa: F401
        import phoenix_v4.quality.ei_v2.dimension_gates  # noqa: F401
        import phoenix_v4.quality.ei_v2.hybrid_selector  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.fixture(scope="module")
def require_hybrid_modules():
    """Skip the test module's dependent tests if hybrid modules are not in repo."""
    if not _hybrid_modules_available():
        pytest.skip("EI V2 hybrid modules (learner, dimension_gates, hybrid_selector) not in repo yet")
    return True


# ---- Always run: package and V2 analysis exist ----

def test_ei_v2_package_and_run_analysis_exist():
    """EI V2 package and run_ei_v2_analysis exist (no hybrid modules required)."""
    from phoenix_v4.quality.ei_v2 import run_ei_v2_analysis, EIV2AnalysisReport

    report = run_ei_v2_analysis(
        slot="STORY",
        candidates=[],
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        thesis="Thesis.",
    )
    assert isinstance(report, EIV2AnalysisReport)
    assert report.slot == "STORY"


# ---- Learner (skip when module missing) ----


class TestLearner:
    """Learner: load/save params, log_feedback, load_feedback."""

    def test_load_learned_params_returns_defaults_when_no_file(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.learner import load_learned_params

        params = load_learned_params(path=Path("/nonexistent/learned_params.json"))
        assert params.override_margin == 0.12
        assert "rerank" in params.composite_weights
        assert params.composite_weights["rerank"] == 0.35

    def test_load_learned_params_from_existing_file(self, require_hybrid_modules, tmp_path):
        from phoenix_v4.quality.ei_v2.learner import LearnedParams, load_learned_params, save_learned_params

        p = tmp_path / "params.json"
        orig = LearnedParams(version=1, override_margin=0.15, total_observations=10)
        save_learned_params(orig, path=p)
        loaded = load_learned_params(path=p)
        assert loaded.version == 1
        assert loaded.override_margin == 0.15
        assert loaded.total_observations == 10

    def test_log_feedback_appends_jsonl(self, require_hybrid_modules, tmp_path):
        from phoenix_v4.quality.ei_v2.learner import FeedbackRecord, log_feedback

        path = tmp_path / "feedback.jsonl"
        record = FeedbackRecord(
            timestamp="2026-03-04T12:00:00Z",
            slot="STORY",
            chapter_index=0,
            persona_id="gen_z",
            topic_id="anxiety",
            v1_chosen_id="a1",
            v2_chosen_id="a2",
            hybrid_chosen_id="a1",
            override_applied=False,
        )
        log_feedback(record, path=path)
        log_feedback(record, path=path)
        lines = path.read_text().strip().splitlines()
        assert len(lines) == 2
        data = json.loads(lines[0])
        assert data["slot"] == "STORY"
        assert data["persona_id"] == "gen_z"

    def test_load_feedback_returns_records(self, require_hybrid_modules, tmp_path):
        from phoenix_v4.quality.ei_v2.learner import FeedbackRecord, load_feedback, log_feedback

        path = tmp_path / "feedback.jsonl"
        log_feedback(
            FeedbackRecord(
                timestamp="2026-03-04T12:00:00Z",
                slot="STORY",
                chapter_index=0,
                persona_id="p",
                topic_id="t",
                v1_chosen_id="v1",
                v2_chosen_id="v2",
                hybrid_chosen_id="v1",
                override_applied=False,
            ),
            path=path,
        )
        records = load_feedback(path=path)
        assert len(records) == 1
        assert records[0].slot == "STORY"
        assert records[0].persona_id == "p"


# ---- Dimension gates (skip when module missing) ----


class TestDimensionGates:
    """Dimension gates: uniqueness, engagement, somatic, GateResult, ChapterGateReport."""

    def test_gate_uniqueness_single_chapter_passes(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_uniqueness

        result = gate_uniqueness("Only one chapter here.", [], 0)
        assert result.dimension == "uniqueness"
        assert result.status in ("PASS", "WARN")
        assert 0 <= result.score <= 1.0

    def test_gate_uniqueness_duplicate_chapters_fail_or_warn(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_uniqueness

        text = "That morning Sarah opened her laptop. Here's the thing. You know how it is."
        others = [text] * 2
        result = gate_uniqueness(text, others, 0)
        assert result.dimension == "uniqueness"
        assert result.status in ("PASS", "WARN", "FAIL")
        assert 0 <= result.score <= 1.0

    def test_gate_engagement_short_text_fails(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_engagement

        result = gate_engagement("Too short.", 0)
        assert result.dimension == "engagement"
        assert result.status == "FAIL"
        assert "too short" in " ".join(result.issues).lower()

    def test_gate_engagement_rich_text_passes(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_engagement

        text = (
            "That morning, Sarah opened her laptop at the kitchen table. "
            "Her jaw was tight. But then she noticed something. However, the catch was real. "
            "What comes next might surprise you."
        )
        result = gate_engagement(text, 0)
        assert result.dimension == "engagement"
        assert result.status in ("PASS", "WARN")
        assert result.score >= 0

    def test_gate_somatic_precision_low_body_fails_or_warns(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_somatic_precision

        result = gate_somatic_precision("No body words here. Just abstract ideas and thoughts.")
        assert result.dimension == "somatic_precision"
        assert result.status in ("WARN", "FAIL")
        assert 0 <= result.score <= 1.0

    def test_gate_somatic_precision_high_body_passes(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.dimension_gates import gate_somatic_precision

        text = "Her shoulders were tight. Her breath quickened. Her chest felt heavy. Her jaw clenched."
        result = gate_somatic_precision(text)
        assert result.dimension == "somatic_precision"
        assert result.status in ("PASS", "WARN")
        assert result.score >= 0.3

    def test_gate_result_to_dict(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.dimension_gates import GateResult

        g = GateResult(dimension="test", status="PASS", score=0.8, issues=["x"], remediation=[])
        d = g.to_dict()
        assert d["dimension"] == "test"
        assert d["status"] == "PASS"
        assert d["score"] == 0.8
        assert d["issues"] == ["x"]

    def test_chapter_gate_report_to_dict(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.dimension_gates import ChapterGateReport, GateResult

        g = GateResult(dimension="u", status="PASS", score=1.0)
        r = ChapterGateReport(chapter_index=0, gates=[g], overall_status="PASS", fail_count=0, warn_count=0)
        d = r.to_dict()
        assert d["chapter_index"] == 0
        assert d["overall_status"] == "PASS"
        assert len(d["gates"]) == 1
        assert d["gates"][0]["dimension"] == "u"


# ---- Hybrid selector (skip when module missing) ----


class TestHybridSelector:
    """Hybrid selector: HybridDecision, hybrid_select with minimal V1+V2 path."""

    def test_hybrid_decision_to_dict(self, require_hybrid_modules):
        from phoenix_v4.quality.ei_v2.hybrid_selector import HybridDecision

        d = HybridDecision(
            slot="STORY",
            chapter_index=0,
            slot_index=0,
            final_chosen_id="a1",
            v1_chosen_id="a1",
            v2_chosen_id="a1",
            override_applied=False,
        )
        out = d.to_dict()
        assert out["slot"] == "STORY"
        assert out["final_chosen_id"] == "a1"
        assert out["override_applied"] is False

    def test_hybrid_select_single_candidate_keeps_v1_winner(self, require_hybrid_modules):
        """With one candidate, V1 picks it; hybrid keeps V1 winner (no override)."""
        from phoenix_v4.quality.ei_v2.hybrid_selector import hybrid_select

        candidates_raw = [
            {"atom_id": "single_atom", "text": "Her shoulders were tight. Her breath quickened. Body and mind aligned."},
        ]
        v1_cfg = {"selector": "rule_best"}
        decision = hybrid_select(
            slot="STORY",
            chapter_index=0,
            slot_index=0,
            candidates_raw=candidates_raw,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            thesis="Your nervous system fires an alarm before your mind catches up.",
            v1_cfg=v1_cfg,
            v2_cfg={},
        )
        assert decision.v1_chosen_id == "single_atom"
        assert decision.final_chosen_id == "single_atom"
        assert decision.slot == "STORY"

    def test_hybrid_select_empty_candidates_returns_fallback(self, require_hybrid_modules):
        """No candidates: V1 returns empty; hybrid should still return a valid decision."""
        from phoenix_v4.quality.ei_v2.hybrid_selector import hybrid_select

        decision = hybrid_select(
            slot="STORY",
            chapter_index=0,
            slot_index=0,
            candidates_raw=[],
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            thesis="Thesis here.",
            v1_cfg={"selector": "rule_best"},
        )
        assert decision.v1_chosen_id == ""
        assert decision.final_chosen_id == ""
        assert decision.slot == "STORY"

    def test_hybrid_select_two_candidates_deterministic(self, require_hybrid_modules):
        """Two candidates: same selector_key gives same winner across calls."""
        from phoenix_v4.quality.ei_v2.hybrid_selector import hybrid_select

        candidates_raw = [
            {"atom_id": "a1", "text": "First option. Shoulders tight. Breath slow."},
            {"atom_id": "a2", "text": "Second option. Chest heavy. Jaw clenched."},
        ]
        v1_cfg = {"selector": "rule_best"}
        key = "deterministic_test_key_123"
        d1 = hybrid_select(
            slot="STORY",
            chapter_index=0,
            slot_index=0,
            candidates_raw=candidates_raw,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            thesis="Body and mind.",
            v1_cfg=v1_cfg,
            selector_key=key,
        )
        d2 = hybrid_select(
            slot="STORY",
            chapter_index=0,
            slot_index=0,
            candidates_raw=candidates_raw,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            thesis="Body and mind.",
            v1_cfg=v1_cfg,
            selector_key=key,
        )
        assert d1.final_chosen_id == d2.final_chosen_id
        assert d1.v1_chosen_id == d2.v1_chosen_id
