"""
EI v2 In Planning: advisory layer only.
Scores deterministic planner output and produces recommendations; never overrides policy.
Authority: specs/EI_V2_IN_PLANNING_SPEC.md.

Input contract (stub-to-real handoff): see spec §12 and config/quality/ei_v2_planning_advisory.yaml.
- historical_outcomes: keyed by (brand_id, teacher_id, topic_id, persona_id, program_id, series_id, week);
  fields: sales, read_through, completion, refund_rate, flag_rate, rejection_rate.
- content_quality_signals: aggregated EI metrics per book/tuple; required_signal_fields and
  missing_signal_policy in config define required keys and behavior when missing/partial.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from phoenix_v4.planning.teacher_portfolio_planner import TeacherAllocation


@dataclass
class PlanningCandidate:
    """One planned tuple (brand, teacher, topic, persona, program, worldview, optional series/concept)."""
    brand_id: str
    teacher_id: str
    topic_id: str
    persona_id: str
    program_id: str
    worldview_id: str
    position_in_wave: int = 0
    series_id: str = ""
    concept_id: str = ""

    @classmethod
    def from_allocation(cls, a: TeacherAllocation, series_id: str = "", concept_id: str = "") -> PlanningCandidate:
        return cls(
            brand_id=a.brand_id,
            teacher_id=a.teacher_id,
            topic_id=a.topic_id,
            persona_id=a.persona_id,
            program_id=a.program_id or "",
            worldview_id=a.worldview_id or "",
            position_in_wave=a.position_in_wave,
            series_id=series_id,
            concept_id=concept_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TupleScore:
    """EI score for one planning tuple."""
    candidate_index: int
    quality_confidence: float
    duplication_risk: float
    metadata_risk: float
    expected_engagement: float
    composite: float
    dimensions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BoostCutRecommendation:
    """Suggest increase/decrease by dimension (program/teacher/topic/persona)."""
    dimension: str  # program_id | teacher_id | topic_id | persona_id
    dimension_value: str
    direction: str  # boost | cut
    reason: str
    score_delta: float
    confidence: float
    expected_kpi_effect: str = ""
    policy_check_status: str = "allowed"  # allowed | not_allowed | unknown

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SeriesRecommendation:
    """Series continuation vs new start priority."""
    series_id: str
    recommendation: str  # continue_first | new_start_ok | complete_cluster_first
    reason: str
    confidence: float
    expected_read_through: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PlanningWarning:
    """Warning for UI: risk or weak differentiation."""
    code: str
    message: str
    severity: str  # high | medium | low
    candidate_indices: List[int] = field(default_factory=list)
    dimension: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EIPlanningAdvisoryReport:
    """Full output of run_ei_planning_advisory."""
    plan_id: str
    candidates: List[PlanningCandidate]
    tuple_scores: List[TupleScore]
    boost_cut_recommendations: List[BoostCutRecommendation]
    series_recommendations: List[SeriesRecommendation]
    warnings: List[PlanningWarning]
    ranked_candidate_indices: List[int]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "candidates": [c.to_dict() for c in self.candidates],
            "tuple_scores": [s.to_dict() for s in self.tuple_scores],
            "boost_cut_recommendations": [r.to_dict() for r in self.boost_cut_recommendations],
            "series_recommendations": [r.to_dict() for r in self.series_recommendations],
            "warnings": [w.to_dict() for w in self.warnings],
            "ranked_candidate_indices": self.ranked_candidate_indices,
            "metadata": self.metadata,
        }


def _outcomes_by_key(
    historical_outcomes: Any,
) -> Dict[tuple, Dict[str, Any]]:
    """Normalize historical_outcomes to dict keyed by canonical tuple."""
    from phoenix_v4.planning.ei_planning_contracts import planning_tuple_key_from_outcome_row
    from phoenix_v4.planning.outcome_ingestion import historical_outcomes_by_key

    if historical_outcomes is None:
        return {}
    if isinstance(historical_outcomes, dict):
        return historical_outcomes
    if isinstance(historical_outcomes, list):
        return historical_outcomes_by_key(historical_outcomes)
    return {}


def _signals_by_key(
    content_quality_signals: Any,
) -> Dict[tuple, Dict[str, Any]]:
    """Normalize content_quality_signals to dict keyed by canonical tuple."""
    from phoenix_v4.planning.content_quality_signals import signals_by_tuple_key

    if content_quality_signals is None:
        return {}
    if isinstance(content_quality_signals, dict):
        return content_quality_signals
    if isinstance(content_quality_signals, list):
        return signals_by_tuple_key(content_quality_signals, week="")
    return {}


def _aggregate_outcome_rows(rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Single aggregated outcome from a list of outcome rows (e.g. mean read_through, completion, etc.)."""
    if not rows:
        return None
    n = len(rows)
    def _f(key: str) -> float:
        s = 0.0
        for r in rows:
            v = r.get(key)
            try:
                s += float(v) if v is not None else 0.0
            except (TypeError, ValueError):
                pass
        return s / n
    return {"read_through": _f("read_through"), "completion": _f("completion"), "refund_rate": _f("refund_rate"), "flag_rate": _f("flag_rate"), "rejection_rate": _f("rejection_rate")}


def _build_outcome_fallback_indices(
    outcomes_by_key: Dict[tuple, Dict[str, Any]],
) -> tuple:
    """Build (program, teacher) -> outcome, program_id -> outcome, brand_id -> outcome for cold-start fallback."""
    by_pt: Dict[tuple, List[Dict[str, Any]]] = {}
    by_program: Dict[str, List[Dict[str, Any]]] = {}
    by_brand: Dict[str, List[Dict[str, Any]]] = {}
    for _key, row in outcomes_by_key.items():
        program_id = (row.get("program_id") or "").strip()
        teacher_id = (row.get("teacher_id") or "").strip()
        brand_id = (row.get("brand_id") or "").strip()
        if program_id and teacher_id:
            by_pt.setdefault((program_id, teacher_id), []).append(row)
        if program_id:
            by_program.setdefault(program_id, []).append(row)
        if brand_id:
            by_brand.setdefault(brand_id, []).append(row)
    agg_pt = {k: _aggregate_outcome_rows(v) for k, v in by_pt.items()}
    agg_program = {k: _aggregate_outcome_rows(v) for k, v in by_program.items()}
    agg_brand = {k: _aggregate_outcome_rows(v) for k, v in by_brand.items()}
    return agg_pt, agg_program, agg_brand


def _score_candidate(
    candidate: PlanningCandidate,
    candidate_index: int,
    outcomes_by_key: Dict[tuple, Dict[str, Any]],
    signals_by_key: Dict[tuple, Dict[str, Any]],
    weights: Dict[str, float],
    missing_policy: str,
    outcome_fallback: Optional[tuple] = None,
    global_prior: Optional[Dict[str, float]] = None,
) -> TupleScore:
    """Compute per-dimension and composite score. Uses cold-start fallback: full key -> (program, teacher) -> program -> brand -> global prior."""
    from phoenix_v4.planning.ei_planning_contracts import planning_tuple_key_from_candidate

    key = planning_tuple_key_from_candidate(candidate, week="")
    outcome = outcomes_by_key.get(key)
    if outcome is None and outcome_fallback:
        by_pt, by_program, by_brand = outcome_fallback
        outcome = by_pt.get((candidate.program_id, candidate.teacher_id)) or by_program.get(candidate.program_id) or by_brand.get(candidate.brand_id)
    signal = signals_by_key.get(key)
    has_data = outcome is not None or signal is not None

    def _num(v: Any, default: float) -> float:
        if v is None:
            return default
        try:
            return max(0.0, min(1.0, float(v)))
        except (TypeError, ValueError):
            return default

    if has_data:
        q_from_outcome = (
            1.0 - ((_num((outcome or {}).get("refund_rate"), 0) + _num((outcome or {}).get("flag_rate"), 0)) / 2.0)
            if outcome else 0.5
        )
        quality_confidence = _num((signal or {}).get("quality_confidence"), q_from_outcome)
        duplication_risk = _num((signal or {}).get("duplication_risk"), 0.0)
        metadata_risk = _num((signal or {}).get("metadata_risk"), 0.0)
        o = outcome or {}
        rt = _num(o.get("read_through"), 0.5)
        comp = _num(o.get("completion"), 0.5)
        eng_from_outcome = (rt + comp) / 2.0 if (rt != 0.5 or comp != 0.5) else 0.5
        expected_engagement = _num((signal or {}).get("expected_engagement"), eng_from_outcome)
    else:
        if missing_policy == "skip_scoring":
            quality_confidence = 0.0
            duplication_risk = 0.0
            metadata_risk = 0.0
            expected_engagement = 0.0
        elif global_prior:
            quality_confidence = float(global_prior.get("quality_confidence", 0.5))
            duplication_risk = float(global_prior.get("duplication_risk", 0.0))
            metadata_risk = float(global_prior.get("metadata_risk", 0.0))
            expected_engagement = float(global_prior.get("expected_engagement", 0.5))
        else:
            quality_confidence = 0.5
            duplication_risk = 0.0
            metadata_risk = 0.0
            expected_engagement = 0.5

    w_q = float(weights.get("quality_confidence", 0.35))
    w_d = float(weights.get("duplication_risk", -0.25))
    w_m = float(weights.get("metadata_risk", -0.20))
    w_e = float(weights.get("expected_engagement", 0.20))
    composite = w_q * quality_confidence + w_d * duplication_risk + w_m * metadata_risk + w_e * expected_engagement
    composite = max(0.0, min(1.0, composite))

    return TupleScore(
        candidate_index=candidate_index,
        quality_confidence=quality_confidence,
        duplication_risk=duplication_risk,
        metadata_risk=metadata_risk,
        expected_engagement=expected_engagement,
        composite=composite,
        dimensions={"outcome_present": outcome is not None, "signal_present": signal is not None},
    )


def run_ei_planning_advisory(
    candidates: List[PlanningCandidate],
    plan_id: str = "",
    historical_outcomes: Optional[Any] = None,
    content_quality_signals: Optional[Any] = None,
    cfg: Optional[Dict[str, Any]] = None,
) -> EIPlanningAdvisoryReport:
    """
    Run EI v2 planning advisory on a deterministic candidate set.
    Returns scores, ranked order, boost/cut and series recommendations, and warnings.
    Does not modify policy or constraints; advisory only.
    historical_outcomes: list of validated outcome dicts or dict keyed by canonical tuple.
    content_quality_signals: list of signal dicts (with optional identity keys) or dict keyed by tuple.
    """
    cfg = cfg or {}
    enabled = cfg.get("enabled", True)
    if not candidates:
        return EIPlanningAdvisoryReport(
            plan_id=plan_id,
            candidates=[],
            tuple_scores=[],
            boost_cut_recommendations=[],
            series_recommendations=[],
            warnings=[],
            ranked_candidate_indices=[],
            metadata={"ei_planning_advisory_enabled": enabled},
        )

    outcomes_by_key = _outcomes_by_key(historical_outcomes)
    signals_by_key = _signals_by_key(content_quality_signals)
    weights = dict(cfg.get("scoring_weights") or {
        "quality_confidence": 0.35,
        "duplication_risk": -0.25,
        "metadata_risk": -0.20,
        "expected_engagement": 0.20,
    })
    if cfg.get("use_learned_weights", True):
        try:
            from pathlib import Path
            from phoenix_v4.quality.ei_v2.learner import load_learned_params
            _repo = Path(__file__).resolve().parents[2]
            _params_path = _repo / "artifacts" / "ei_v2" / "learned_params.json"
            learned = load_learned_params(path=_params_path)
            plan_keys = ("quality_confidence", "duplication_risk", "metadata_risk", "expected_engagement")
            for k in plan_keys:
                if k in (learned.composite_weights or {}):
                    weights[k] = float(learned.composite_weights[k])
        except Exception:
            pass
    missing_policy = (cfg.get("missing_signal_policy") or "degrade_only").strip().lower()

    cold_start = cfg.get("cold_start_fallback") or {}
    outcome_fallback: Optional[Tuple[Any, Any, Any]] = None
    global_prior: Optional[Dict[str, float]] = None
    if cold_start.get("enabled", False):
        outcome_fallback = _build_outcome_fallback_indices(outcomes_by_key)
        gp = cold_start.get("global_prior")
        if isinstance(gp, dict) and gp:
            global_prior = {k: float(v) for k, v in gp.items() if isinstance(v, (int, float))}

    tuple_scores: List[TupleScore] = []
    for i, c in enumerate(candidates):
        tuple_scores.append(
            _score_candidate(
                c, i, outcomes_by_key, signals_by_key, weights, missing_policy,
                outcome_fallback=outcome_fallback,
                global_prior=global_prior,
            )
        )
    composite_by_index = [(s.composite, s.candidate_index) for s in tuple_scores]
    ranked_candidate_indices = [idx for _, idx in sorted(composite_by_index, key=lambda x: (-x[0], x[1]))]

    boost_cut_recommendations: List[BoostCutRecommendation] = []
    series_recommendations: List[SeriesRecommendation] = []
    warnings: List[PlanningWarning] = []

    return EIPlanningAdvisoryReport(
        plan_id=plan_id,
        candidates=candidates,
        tuple_scores=tuple_scores,
        boost_cut_recommendations=boost_cut_recommendations,
        series_recommendations=series_recommendations,
        warnings=warnings,
        ranked_candidate_indices=ranked_candidate_indices,
        metadata={
            "ei_planning_advisory_enabled": enabled,
            "historical_outcomes_used": historical_outcomes is not None,
            "content_signals_used": content_quality_signals is not None,
        },
    )
