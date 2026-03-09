"""
EI V2 hybrid selector: combine V1 and V2 selection with optional learned override.
Deterministic given selector_key; minimal V1 path when V2 unavailable.
Accepts program_id and worldview_id for future editorial-coherence biasing (passed through, not yet used).
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_EI_V2_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _EI_V2_ROOT.parent.parent.parent


def _v1_pick(candidates_raw: List[Dict[str, Any]], selector_key: str) -> str:
    """Deterministic V1-style pick by selector_key (hash). Fail-open: first candidate or empty."""
    if not candidates_raw:
        return ""
    if len(candidates_raw) == 1:
        return (candidates_raw[0].get("atom_id") or candidates_raw[0].get("id") or "").strip()
    h = hashlib.sha256(selector_key.encode()).hexdigest()
    idx = int(h[:8], 16) % len(candidates_raw)
    c = candidates_raw[idx]
    return (c.get("atom_id") or c.get("id") or "").strip()


def _composite_score_from_report(candidate_id: str, report: Any, cfg: Dict[str, Any]) -> float:
    """Compute V2 composite score for one candidate from EIV2AnalysisReport. Uses same weights as _select_v2_best."""
    weights = cfg.get("composite_weights", {})
    w_rerank = float(weights.get("rerank", 0.35))
    w_safety = float(weights.get("safety", 0.25))
    w_domain = float(weights.get("domain_similarity", 0.20))
    w_tts = float(weights.get("tts_readability", 0.20))
    score = 0.0
    for cr in getattr(report, "candidates", []) or []:
        if getattr(cr, "candidate_id", None) != candidate_id:
            continue
        if cr.rerank_score is not None:
            score += w_rerank * cr.rerank_score
        if isinstance(cr.safety, dict):
            risk = float(cr.safety.get("risk_score", 0.0))
            score += w_safety * (1.0 - risk)
        if cr.domain_similarity is not None:
            score += w_domain * cr.domain_similarity
        if isinstance(getattr(cr, "tts_readability", None), dict):
            readability = float(cr.tts_readability.get("composite", 0.5))
            score += w_tts * readability
        break
    return score


@dataclass
class HybridDecision:
    slot: str
    chapter_index: int
    slot_index: int
    final_chosen_id: str
    v1_chosen_id: str
    v2_chosen_id: str
    override_applied: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def hybrid_select(
    *,
    slot: str,
    chapter_index: int,
    slot_index: int,
    candidates_raw: List[Dict[str, Any]],
    persona_id: str,
    topic_id: str,
    thesis: str,
    v1_cfg: Optional[Dict[str, Any]] = None,
    v2_cfg: Optional[Dict[str, Any]] = None,
    selector_key: Optional[str] = None,
    program_id: Optional[str] = None,
    worldview_id: Optional[str] = None,
    shadow_mode: bool = False,
    chapter_text: Optional[str] = None,
    arc_intent: Optional[Dict[str, Any]] = None,
) -> HybridDecision:
    """
    Hybrid selection: run V1 (and optionally V2), apply override margin from learner if present.
    When V2 is disabled or unavailable, final = V1. Accepts program_id/worldview_id for future use.
    shadow_mode: when True, always return final = v1_chosen (no override) but still run V2 and log feedback.
    """
    key = selector_key or f"{slot}:{chapter_index}:{slot_index}:{persona_id}:{topic_id}"
    v1_chosen = _v1_pick(candidates_raw, key)
    v2_chosen = v1_chosen
    final = v1_chosen
    override = False

    hybrid_cfg = (v2_cfg or {}).get("hybrid", {}) if isinstance(v2_cfg, dict) else {}
    use_v2 = hybrid_cfg.get("enabled", False) and v2_cfg and len(candidates_raw) > 0

    if use_v2:
        try:
            from phoenix_v4.quality.ei_v2 import run_ei_v2_analysis
            from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
            from phoenix_v4.quality.ei_v2.learner import (
                load_learned_params,
                log_feedback,
                FeedbackRecord,
            )

            cfg = v2_cfg if isinstance(v2_cfg, dict) else load_ei_v2_config()
            candidates_normalized = [
                {
                    "id": c.get("atom_id") or c.get("id") or f"c{i}",
                    "text": c.get("text", ""),
                }
                for i, c in enumerate(candidates_raw)
            ]
            report = run_ei_v2_analysis(
                slot=slot,
                candidates=candidates_normalized,
                persona_id=persona_id,
                topic_id=topic_id,
                thesis=thesis,
                chapter_text=chapter_text,
                arc_intent=arc_intent,
                cfg=cfg,
                v1_chosen_id=v1_chosen,
            )
            v2_chosen = report.v2_chosen_id or v1_chosen

            learned = load_learned_params(
                path=_REPO_ROOT / (cfg.get("learner", {}).get("params_path", "artifacts/ei_v2/learned_params.json"))
            )
            margin = learned.override_margin
            score_v1 = _composite_score_from_report(v1_chosen, report, cfg)
            score_v2 = _composite_score_from_report(v2_chosen, report, cfg)
            if score_v2 - score_v1 >= margin and not shadow_mode:
                final = v2_chosen
                override = True
            else:
                final = v1_chosen

            feedback_path = _REPO_ROOT / (cfg.get("learner", {}).get("feedback_path", "artifacts/ei_v2/learner_feedback.jsonl"))
            log_feedback(
                FeedbackRecord(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    slot=slot,
                    chapter_index=chapter_index,
                    persona_id=persona_id,
                    topic_id=topic_id,
                    v1_chosen_id=v1_chosen,
                    v2_chosen_id=v2_chosen,
                    hybrid_chosen_id=final,
                    override_applied=override,
                ),
                feedback_path,
            )
        except Exception:
            final = v1_chosen
            v2_chosen = v1_chosen
            override = False

    return HybridDecision(
        slot=slot,
        chapter_index=chapter_index,
        slot_index=slot_index,
        final_chosen_id=final,
        v1_chosen_id=v1_chosen,
        v2_chosen_id=v2_chosen,
        override_applied=override,
    )
