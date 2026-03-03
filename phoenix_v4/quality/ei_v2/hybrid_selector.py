"""
Hybrid V1+V2 Selector — layered candidate selection with override logic.

Flow:
  1. V1 picks winner (stable baseline).
  2. V2 scores same candidates (all enabled modules).
  3. If V2 detects high risk (dedup/tts/arc), block V1 winner or force fallback.
  4. If V2 says current V1 winner is much worse than alternative (margin threshold),
     allow override to V2's pick.
  5. Log every decision (override or keep) with full scores for the learner.

Override rule:
  Keep V1 UNLESS all of these are true:
    a) v2_best_score - v2_v1winner_score >= margin (default 0.12)
    b) V2 best candidate has no safety violation
    c) Dedup risk of V2 best is below cap
    d) Arc deviation of V2 best is below cap

The hybrid selector is the bridge between V1 (stable) and V2 (learning).
As V2 earns trust through the learner, the margin can be lowered.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from phoenix_v4.quality.ei_adapter import EISelectionOutput, apply_ei_selection
from phoenix_v4.quality.ei_v2 import EIV2AnalysisReport, EIV2CandidateReport, run_ei_v2_analysis
from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
from phoenix_v4.quality.ei_v2.ei_warnings import log_ei_warning
from phoenix_v4.quality.ei_v2.learner import (
    FeedbackRecord,
    LearnedParams,
    load_learned_params,
    log_feedback,
)


@dataclass
class HybridDecision:
    """Result of the hybrid selector for one slot."""
    slot: str
    chapter_index: int
    slot_index: int
    final_chosen_id: str
    v1_chosen_id: str
    v2_chosen_id: Optional[str]
    override_applied: bool
    override_reason: str = ""
    block_applied: bool = False
    block_reason: str = ""
    fallback_id: Optional[str] = None
    v1_composite: float = 0.0
    v2_composite_v1winner: float = 0.0
    v2_composite_v2winner: float = 0.0
    margin: float = 0.0
    safety_risk: float = 0.0
    dedup_max_sim: float = 0.0
    arc_deviation: float = 0.0
    tts_composite: float = 0.0
    v1_ms: float = 0.0
    v2_ms: float = 0.0
    total_ms: float = 0.0
    v1_debug: Dict[str, Any] = field(default_factory=dict)
    v2_report: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _compute_v2_composite(
    candidate_id: str,
    v2_report: EIV2AnalysisReport,
    weights: Dict[str, float],
) -> float:
    """Compute V2 composite score for a specific candidate."""
    w_rerank = weights.get("rerank", 0.35)
    w_safety = weights.get("safety", 0.25)
    w_domain = weights.get("domain_similarity", 0.20)
    w_tts = weights.get("tts_readability", 0.20)

    for cr in v2_report.candidates:
        if cr.candidate_id == candidate_id:
            score = 0.0
            if cr.rerank_score is not None:
                score += w_rerank * cr.rerank_score
            if isinstance(cr.safety, dict):
                score += w_safety * (1.0 - float(cr.safety.get("risk_score", 0.0)))
            if cr.domain_similarity is not None:
                score += w_domain * cr.domain_similarity
            if isinstance(cr.tts_readability, dict):
                score += w_tts * float(cr.tts_readability.get("composite", 0.5))
            return score
    return 0.0


def _get_candidate_safety_risk(candidate_id: str, v2_report: EIV2AnalysisReport) -> float:
    for cr in v2_report.candidates:
        if cr.candidate_id == candidate_id:
            if isinstance(cr.safety, dict):
                return float(cr.safety.get("risk_score", 0.0))
            return 0.0
    return 0.0


def _get_candidate_tts(candidate_id: str, v2_report: EIV2AnalysisReport) -> float:
    for cr in v2_report.candidates:
        if cr.candidate_id == candidate_id:
            if isinstance(cr.tts_readability, dict):
                return float(cr.tts_readability.get("composite", 0.5))
            return 0.5
    return 0.5


def _get_max_dedup_sim(candidate_id: str, v2_report: EIV2AnalysisReport) -> float:
    """Max dedup similarity for this candidate against any other."""
    max_sim = 0.0
    for dupe in v2_report.semantic_duplicates:
        if not isinstance(dupe, dict):
            continue
        if dupe.get("id_a") == candidate_id or dupe.get("id_b") == candidate_id:
            max_sim = max(max_sim, float(dupe.get("similarity", 0.0)))
    return max_sim


def _get_arc_deviation(v2_report: EIV2AnalysisReport) -> float:
    if isinstance(v2_report.emotion_arc, dict):
        return float(v2_report.emotion_arc.get("max_deviation", 0.0))
    return 0.0


def hybrid_select(
    *,
    slot: str,
    chapter_index: int,
    slot_index: int,
    candidates_raw: List[Dict[str, Any]],
    persona_id: str,
    topic_id: str,
    thesis: str,
    v1_cfg: Dict[str, Any],
    v2_cfg: Optional[Dict[str, Any]] = None,
    learned_params: Optional[LearnedParams] = None,
    selector_key: Optional[str] = None,
    teacher_mode: bool = False,
    embed_fn: Optional[Callable] = None,
    call_llm_json: Optional[Callable] = None,
    chapter_text: Optional[str] = None,
    arc_intent: Optional[Dict[str, Any]] = None,
    dimension_scores: Optional[Dict[str, float]] = None,
    feedback_path: Optional[Path] = None,
) -> HybridDecision:
    """
    Layered hybrid selection:
      1. V1 picks winner
      2. V2 scores all candidates
      3. Check risk blocks (safety, dedup, arc)
      4. Check override threshold
      5. Log decision for learner
    """
    t_total = time.monotonic()

    if v2_cfg is None:
        v2_cfg = load_ei_v2_config()
    if learned_params is None:
        learned_params = load_learned_params()

    hybrid_cfg = v2_cfg.get("hybrid", {})
    override_margin = learned_params.override_margin if learned_params.override_margin else hybrid_cfg.get("override_margin", 0.12)
    safety_block_threshold = float(hybrid_cfg.get("safety_block_threshold", 0.5))
    dedup_block_threshold = float(hybrid_cfg.get("dedup_block_threshold", 0.6))
    arc_block_threshold = float(hybrid_cfg.get("arc_block_threshold", 0.5))
    tts_block_threshold = float(hybrid_cfg.get("tts_block_threshold", 0.3))
    weights = learned_params.composite_weights or v2_cfg.get("composite_weights", {})

    # --- Step 1: V1 picks winner ---
    t0 = time.monotonic()
    v1_result: EISelectionOutput = apply_ei_selection(
        slot=slot,
        candidates_raw=candidates_raw,
        persona_id=persona_id,
        topic_id=topic_id,
        thesis=thesis,
        cfg=v1_cfg,
        selector_key=selector_key,
        teacher_mode=teacher_mode,
        embed_fn=embed_fn,
        call_llm_json=call_llm_json,
    )
    v1_ms = (time.monotonic() - t0) * 1000
    v1_chosen_id = v1_result.chosen.atom_id

    v1_composite = 0.0
    for row in v1_result.debug.scoring_table:
        if row.get("candidate_id") == v1_chosen_id:
            v1_composite = float(row.get("composite", 0.0))
            break

    # --- Step 2: V2 scores all candidates ---
    t0 = time.monotonic()
    v2_report: EIV2AnalysisReport = run_ei_v2_analysis(
        slot=slot,
        candidates=candidates_raw,
        persona_id=persona_id,
        topic_id=topic_id,
        thesis=thesis,
        chapter_text=chapter_text,
        arc_intent=arc_intent,
        cfg=v2_cfg,
        embed_fn=embed_fn,
        call_llm_json=call_llm_json,
        v1_chosen_id=v1_chosen_id,
    )
    v2_ms = (time.monotonic() - t0) * 1000

    v2_chosen_id = v2_report.v2_chosen_id
    v2_composite_v1winner = _compute_v2_composite(v1_chosen_id, v2_report, weights)
    v2_composite_v2winner = _compute_v2_composite(v2_chosen_id, v2_report, weights) if v2_chosen_id else 0.0

    v1_safety_risk = _get_candidate_safety_risk(v1_chosen_id, v2_report)
    v1_dedup_sim = _get_max_dedup_sim(v1_chosen_id, v2_report)
    arc_deviation = _get_arc_deviation(v2_report)
    v1_tts = _get_candidate_tts(v1_chosen_id, v2_report)

    decision = HybridDecision(
        slot=slot,
        chapter_index=chapter_index,
        slot_index=slot_index,
        final_chosen_id=v1_chosen_id,
        v1_chosen_id=v1_chosen_id,
        v2_chosen_id=v2_chosen_id,
        override_applied=False,
        v1_composite=v1_composite,
        v2_composite_v1winner=v2_composite_v1winner,
        v2_composite_v2winner=v2_composite_v2winner,
        margin=v2_composite_v2winner - v2_composite_v1winner if v2_chosen_id else 0.0,
        safety_risk=v1_safety_risk,
        dedup_max_sim=v1_dedup_sim,
        arc_deviation=arc_deviation,
        tts_composite=v1_tts,
        v1_ms=v1_ms,
        v2_ms=v2_ms,
        v1_debug={
            "selector": v1_result.debug.selector,
            "scoring_table": v1_result.debug.scoring_table,
        },
        v2_report=v2_report.to_dict(),
    )

    # --- Step 3: Risk blocks — force fallback if V1 winner is dangerous ---
    block_reasons = []
    if v1_safety_risk > safety_block_threshold:
        block_reasons.append(f"safety_risk={v1_safety_risk:.2f}>{safety_block_threshold}")
    if v1_dedup_sim > dedup_block_threshold:
        block_reasons.append(f"dedup_sim={v1_dedup_sim:.2f}>{dedup_block_threshold}")
    if arc_deviation > arc_block_threshold:
        block_reasons.append(f"arc_deviation={arc_deviation:.2f}>{arc_block_threshold}")
    if v1_tts < tts_block_threshold:
        block_reasons.append(f"tts={v1_tts:.2f}<{tts_block_threshold}")

    if block_reasons and v2_chosen_id and v2_chosen_id != v1_chosen_id:
        v2_safety = _get_candidate_safety_risk(v2_chosen_id, v2_report)
        v2_dedup = _get_max_dedup_sim(v2_chosen_id, v2_report)
        v2_tts = _get_candidate_tts(v2_chosen_id, v2_report)
        if v2_safety <= safety_block_threshold and v2_dedup <= dedup_block_threshold and v2_tts >= tts_block_threshold:
            decision.block_applied = True
            decision.block_reason = "; ".join(block_reasons)
            decision.fallback_id = v2_chosen_id
            decision.final_chosen_id = v2_chosen_id
            decision.override_applied = True
            decision.override_reason = f"block_fallback: {decision.block_reason}"

    # --- Step 4: Override check — V2 pick better by margin? ---
    if (
        not decision.override_applied
        and v2_chosen_id
        and v2_chosen_id != v1_chosen_id
    ):
        margin = v2_composite_v2winner - v2_composite_v1winner
        v2_best_safety = _get_candidate_safety_risk(v2_chosen_id, v2_report)
        v2_best_dedup = _get_max_dedup_sim(v2_chosen_id, v2_report)

        all_conditions = [
            margin >= override_margin,
            v2_best_safety <= safety_block_threshold,
            v2_best_dedup <= dedup_block_threshold,
            arc_deviation <= arc_block_threshold,
        ]

        if all(all_conditions):
            decision.override_applied = True
            decision.override_reason = f"margin={margin:.4f}>={override_margin:.4f}"
            decision.final_chosen_id = v2_chosen_id

    decision.total_ms = (time.monotonic() - t_total) * 1000

    # --- Step 5: Log for learner ---
    dim_scores = dimension_scores if dimension_scores is not None else {}
    feedback = FeedbackRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        slot=slot,
        chapter_index=chapter_index,
        persona_id=persona_id,
        topic_id=topic_id,
        v1_chosen_id=v1_chosen_id,
        v2_chosen_id=v2_chosen_id,
        hybrid_chosen_id=decision.final_chosen_id,
        override_applied=decision.override_applied,
        override_reason=decision.override_reason,
        v1_composite=v1_composite,
        v2_composite=v2_composite_v2winner,
        margin=decision.margin,
        safety_risk=v1_safety_risk,
        dedup_max_sim=v1_dedup_sim,
        arc_deviation=arc_deviation,
        tts_composite=v1_tts,
        dimension_scores=dim_scores,
    )
    try:
        log_feedback(feedback, feedback_path)
    except Exception as e:
        log_ei_warning(
            "hybrid_selector",
            f"log_feedback failed: {e}",
            {"slot": slot, "chapter_index": chapter_index},
        )

    return decision
