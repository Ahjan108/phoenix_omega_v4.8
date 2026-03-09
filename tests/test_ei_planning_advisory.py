"""
Tests for EI v2 In Planning advisory layer.
Authority: specs/EI_V2_IN_PLANNING_SPEC.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

import pytest

from phoenix_v4.planning.ei_planning_advisory import (
    BoostCutRecommendation,
    EIPlanningAdvisoryReport,
    PlanningCandidate,
    PlanningWarning,
    SeriesRecommendation,
    TupleScore,
    run_ei_planning_advisory,
)
from phoenix_v4.planning.teacher_portfolio_planner import TeacherAllocation


def test_planning_candidate_from_allocation():
    a = TeacherAllocation(
        teacher_id="ahjan",
        topic_id="anxiety",
        persona_id="gen_z",
        brand_id="stillness_press",
        position_in_wave=1,
        program_id="stillness_default",
        worldview_id="buddhist",
    )
    c = PlanningCandidate.from_allocation(a, series_id="s1", concept_id="c1")
    assert c.teacher_id == "ahjan"
    assert c.program_id == "stillness_default"
    assert c.series_id == "s1"
    assert c.concept_id == "c1"


def test_run_ei_planning_advisory_empty():
    report = run_ei_planning_advisory([], plan_id="empty")
    assert report.plan_id == "empty"
    assert report.candidates == []
    assert report.tuple_scores == []
    assert report.ranked_candidate_indices == []
    assert report.boost_cut_recommendations == []
    assert report.series_recommendations == []
    assert report.warnings == []


def test_run_ei_planning_advisory_stub_returns_scores_and_ranking():
    candidates = [
        PlanningCandidate("b1", "t1", "top1", "p1", "prog1", "wv1", 1),
        PlanningCandidate("b1", "t1", "top2", "p2", "prog1", "wv1", 2),
    ]
    report = run_ei_planning_advisory(candidates, plan_id="test-plan")
    assert report.plan_id == "test-plan"
    assert len(report.candidates) == 2
    assert len(report.tuple_scores) == 2
    assert report.tuple_scores[0].candidate_index == 0
    # No outcomes/signals: degrade_only gives quality_confidence=0.5, expected_engagement=0.5, risks=0 -> composite from weights
    assert 0 <= report.tuple_scores[0].composite <= 1.0
    assert report.ranked_candidate_indices == [0, 1]
    assert "ei_planning_advisory_enabled" in report.metadata


def test_report_to_dict_roundtrip():
    candidates = [PlanningCandidate("b1", "t1", "top1", "p1", "prog1", "wv1")]
    report = run_ei_planning_advisory(candidates, plan_id="rt")
    d = report.to_dict()
    assert d["plan_id"] == "rt"
    assert len(d["candidates"]) == 1
    assert d["candidates"][0]["brand_id"] == "b1"
    assert len(d["tuple_scores"]) == 1
    assert d["ranked_candidate_indices"] == [0]


def test_boost_cut_and_warning_to_dict():
    r = BoostCutRecommendation(
        dimension="program_id",
        dimension_value="stillness_default",
        direction="boost",
        reason="Higher engagement in past weeks",
        score_delta=0.1,
        confidence=0.8,
        expected_kpi_effect="+5% read-through",
        policy_check_status="allowed",
    )
    d = r.to_dict()
    assert d["dimension"] == "program_id"
    assert d["policy_check_status"] == "allowed"

    w = PlanningWarning("HIGH_SIMILARITY", "Two slots very similar", "high", [0, 1], "topic_id")
    wd = w.to_dict()
    assert wd["code"] == "HIGH_SIMILARITY"
    assert wd["severity"] == "high"


# --- Quality gates: missing/partial signals, deterministic ranking, policy envelope ---


def test_missing_partial_signal_handling():
    """Missing or partial historical_outcomes/content_quality_signals must not crash; metadata reflects what was used."""
    candidates = [PlanningCandidate("b1", "t1", "top1", "p1", "prog1", "wv1")]
    # Empty signals
    report_empty = run_ei_planning_advisory(
        candidates,
        plan_id="partial",
        historical_outcomes=None,
        content_quality_signals=None,
    )
    assert report_empty.metadata["historical_outcomes_used"] is False
    assert report_empty.metadata["content_signals_used"] is False

    # Empty dicts (provided but no data)
    report_provided = run_ei_planning_advisory(
        candidates,
        plan_id="partial",
        historical_outcomes={},
        content_quality_signals={},
    )
    assert report_provided.metadata["historical_outcomes_used"] is True
    assert report_provided.metadata["content_signals_used"] is True

    # Partial content_quality_signals (e.g. list of dicts with only some keys)
    report_partial = run_ei_planning_advisory(
        candidates,
        plan_id="partial",
        content_quality_signals=[{"quality_confidence": 0.7}],
        cfg={"required_signal_fields": ["quality_confidence", "duplication_risk"], "missing_signal_policy": "degrade_only"},
    )
    assert report_partial.metadata["content_signals_used"] is True
    # Stub may record missing_signal_fields when required_signal_fields present
    assert "ei_planning_advisory_enabled" in report_partial.metadata


def test_deterministic_ranking_same_inputs():
    """Same candidates and cfg must produce identical ranked_candidate_indices."""
    candidates = [
        PlanningCandidate("b1", "t1", "top1", "p1", "prog1", "wv1", 1),
        PlanningCandidate("b1", "t1", "top2", "p2", "prog1", "wv1", 2),
        PlanningCandidate("b2", "t2", "top1", "p1", "prog2", "wv2", 1),
    ]
    cfg = {"enabled": True}
    report1 = run_ei_planning_advisory(candidates, plan_id="det", cfg=cfg)
    report2 = run_ei_planning_advisory(candidates, plan_id="det", cfg=cfg)
    assert report1.ranked_candidate_indices == report2.ranked_candidate_indices
    assert report1.ranked_candidate_indices == [0, 1, 2]


def test_no_recommendation_outside_policy_envelope():
    """All boost/cut recommendations must have policy_check_status in the allowed set."""
    candidates = [PlanningCandidate("b1", "t1", "top1", "p1", "prog1", "wv1")]
    report = run_ei_planning_advisory(candidates, plan_id="policy")
    allowed_policy_status = {"allowed", "not_allowed", "unknown"}
    for r in report.boost_cut_recommendations:
        assert r.policy_check_status in allowed_policy_status
    # Stub emits no recommendations; when real recommendations exist, they must stay within envelope
    assert report.boost_cut_recommendations == []  # current stub


def test_planning_tuple_key_canonical():
    """Canonical tuple key is (brand_id, teacher_id, topic_id, persona_id, program_id, series_id, week)."""
    from phoenix_v4.planning.ei_planning_contracts import (
        planning_tuple_key,
        planning_tuple_key_from_candidate,
        planning_tuple_key_from_outcome_row,
    )

    k = planning_tuple_key("b1", "t1", "top1", "p1", "prog1", "s1", "2024-W01")
    assert k == ("b1", "t1", "top1", "p1", "prog1", "s1", "2024-W01")
    c = PlanningCandidate("b1", "t1", "top1", "p1", "prog1", "wv1", series_id="s1")
    k2 = planning_tuple_key_from_candidate(c, week="2024-W01")
    assert k2 == ("b1", "t1", "top1", "p1", "prog1", "s1", "2024-W01")
    row = {"brand_id": "b1", "teacher_id": "t1", "topic_id": "top1", "persona_id": "p1", "program_id": "prog1", "series_id": "s1", "week": "2024-W01"}
    k3 = planning_tuple_key_from_outcome_row(row)
    assert k3 == k


def test_validate_historical_outcome_row():
    """Strict validation: required identity keys; measure keys optional numeric."""
    from phoenix_v4.planning.ei_planning_contracts import validate_historical_outcome_row

    valid = {
        "brand_id": "b1", "teacher_id": "t1", "topic_id": "top1", "persona_id": "p1",
        "program_id": "prog1", "series_id": "s1", "week": "2024-W01",
        "read_through": 0.8, "completion": 0.7,
    }
    out = validate_historical_outcome_row(valid)
    assert out is not None
    assert out["brand_id"] == "b1"
    assert out["read_through"] == 0.8
    assert validate_historical_outcome_row({}) is None
    assert validate_historical_outcome_row({"brand_id": "b1"}) is None  # missing keys


def test_ei_ranking_with_outcomes():
    """With historical_outcomes, higher read_through/completion yields better rank."""
    candidates = [
        PlanningCandidate("b1", "t1", "top1", "p1", "prog1", "wv1", series_id="s1"),
        PlanningCandidate("b1", "t1", "top2", "p2", "prog1", "wv1", series_id="s2"),
    ]
    outcomes = [
        {"brand_id": "b1", "teacher_id": "t1", "topic_id": "top1", "persona_id": "p1", "program_id": "prog1", "series_id": "s1", "week": "",
         "read_through": 0.3, "completion": 0.3, "refund_rate": 0.1, "flag_rate": 0.05},
        {"brand_id": "b1", "teacher_id": "t1", "topic_id": "top2", "persona_id": "p2", "program_id": "prog1", "series_id": "s2", "week": "",
         "read_through": 0.9, "completion": 0.85, "refund_rate": 0.01, "flag_rate": 0.01},
    ]
    report = run_ei_planning_advisory(candidates, plan_id="rank", historical_outcomes=outcomes)
    # Candidate 1 (index 1) has better outcomes -> should rank first
    assert report.ranked_candidate_indices[0] == 1
    assert report.ranked_candidate_indices[1] == 0
    assert report.tuple_scores[1].composite > report.tuple_scores[0].composite


def test_load_historical_outcomes_from_file():
    """File-based adapter: valid rows accepted, malformed rows dropped; counts returned."""
    from phoenix_v4.planning.outcome_ingestion import load_historical_outcomes_from_file

    valid_row = {
        "brand_id": "b1", "teacher_id": "t1", "topic_id": "top1", "persona_id": "p1",
        "program_id": "prog1", "series_id": "s1", "week": "W01",
        "read_through": 0.7, "completion": 0.6,
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps(valid_row) + "\n")
        f.write(json.dumps({"brand_id": "b2"}) + "\n")  # missing keys -> dropped
        path = Path(f.name)
    try:
        accepted, loaded, dropped, errors = load_historical_outcomes_from_file(path)
        assert len(accepted) == 1
        assert accepted[0]["brand_id"] == "b1"
        assert loaded == 1
        assert dropped == 1
        assert len(errors) >= 1
    finally:
        path.unlink(missing_ok=True)


def test_load_content_quality_signals_from_file():
    """File-based adapter: validate with required_signal_fields; return counts."""
    from phoenix_v4.planning.content_quality_signals import load_content_quality_signals_from_file

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(json.dumps([{"quality_confidence": 0.8}, {"quality_confidence": 0.9, "duplication_risk": 0.1}]))
        path = Path(f.name)
    try:
        accepted, loaded, dropped, errors = load_content_quality_signals_from_file(path, required_signal_fields=[])
        assert len(accepted) == 2
        assert loaded == 2
        assert dropped == 0
        accepted2, _, d2, _ = load_content_quality_signals_from_file(path, required_signal_fields=["quality_confidence"])
        assert len(accepted2) == 2
        assert d2 == 0
    finally:
        path.unlink(missing_ok=True)


def test_trust_metrics_eligible():
    """When metrics meet thresholds, is_trust_eligible returns True."""
    from phoenix_v4.planning.trust_metrics import compute_trust_metrics, is_trust_eligible

    outcomes = [
        {"brand_id": "b", "teacher_id": "t", "topic_id": "top", "persona_id": "p", "program_id": "prog", "series_id": "s", "week": "W01", "flag_rate": 0.01, "rejection_rate": 0.01},
        {"brand_id": "b", "teacher_id": "t", "topic_id": "top", "persona_id": "p", "program_id": "prog", "series_id": "s", "week": "W02", "flag_rate": 0.02, "rejection_rate": 0.02},
    ]
    metrics = compute_trust_metrics(outcomes)
    assert metrics["observation_weeks"] == 2
    thresholds = {"min_observation_weeks": 2, "max_flag_rejection_rate": 0.05, "min_quality_lift_vs_baseline": 0.0, "min_recommendation_acceptance_rate": 0.0}
    assert is_trust_eligible(metrics, thresholds) is True


def test_trust_metrics_not_eligible():
    """When observation_weeks below min, is_trust_eligible returns False."""
    from phoenix_v4.planning.trust_metrics import compute_trust_metrics, is_trust_eligible

    metrics = compute_trust_metrics([])
    assert metrics["observation_weeks"] == 0
    assert is_trust_eligible(metrics, {"min_observation_weeks": 4}) is False
