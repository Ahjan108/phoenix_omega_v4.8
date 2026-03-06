"""
Enlightened Intelligence V2: enhanced AI techniques for candidate selection,
safety classification, duplication detection, emotional arc validation,
TTS readability, and domain-tuned embeddings.

Runs in parallel with EI V1 for A/B comparison. Every module is:
  - Deterministic given same inputs (cacheable)
  - Fail-open by default (scores/flags, never blocks unless configured)
  - Config-gated (enable/disable per dimension)

Thesis and arc context (for EI learning and book assembly):
  - When the plan has chapter_thesis (from arc), callers pass the chapter thesis
    for that chapter as thesis; otherwise a book-level thesis (e.g. topic + persona).
  - arc_intent may include: band, emotional_role, chapter_index, chapter_thesis,
    bestseller_structure. EI v2 uses these for thesis alignment and emotion arc.
  - Slot may be any known type, including PIVOT, TAKEAWAY, PERMISSION, THREAD
    (see config book_structure.known_slot_types).

Usage (parallel comparison):
    from phoenix_v4.quality.ei_v2 import run_ei_v2_analysis

    report = run_ei_v2_analysis(
        slot="STORY",
        candidates=candidates_raw,
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        thesis="Your nervous system fires an alarm...",  # chapter thesis when from arc
        chapter_text="...",
        arc_intent={"band": 3, "emotional_role": "MECHANISM_PROOF", "chapter_thesis": "...", "bestseller_structure": "case_file"},
        cfg=ei_v2_config,
    )
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
from phoenix_v4.quality.ei_v2.cross_encoder_reranker import rerank_candidates
from phoenix_v4.quality.ei_v2.domain_embeddings import domain_thesis_similarity
from phoenix_v4.quality.ei_v2.emotion_arc_validator import validate_emotion_arc
from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates
from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability


@dataclass
class EIV2CandidateReport:
    candidate_id: str
    safety: Dict[str, Any] = field(default_factory=dict)
    rerank_score: Optional[float] = None
    domain_similarity: Optional[float] = None
    tts_readability: Optional[Dict[str, Any]] = None


@dataclass
class EIV2AnalysisReport:
    """Full V2 analysis output for one slot invocation."""
    slot: str
    candidates: List[EIV2CandidateReport] = field(default_factory=list)
    rerank_order: List[str] = field(default_factory=list)
    semantic_duplicates: List[Dict[str, Any]] = field(default_factory=list)
    emotion_arc: Optional[Dict[str, Any]] = None
    v2_chosen_id: Optional[str] = None
    v1_chosen_id: Optional[str] = None
    agreement: Optional[bool] = None
    config_used: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_ei_v2_analysis(
    *,
    slot: str,
    candidates: List[Dict[str, Any]],
    persona_id: str,
    topic_id: str,
    thesis: str,
    chapter_text: Optional[str] = None,
    arc_intent: Optional[Dict[str, Any]] = None,
    cfg: Optional[Dict[str, Any]] = None,
    embed_fn=None,
    call_llm_json=None,
    v1_chosen_id: Optional[str] = None,
) -> EIV2AnalysisReport:
    """
    Run all enabled V2 AI analyses on a set of candidates.

    Returns an EIV2AnalysisReport with per-candidate scores and a
    V2 recommendation. Compare v2_chosen_id vs v1_chosen_id to measure
    agreement with the current pipeline.
    """
    if cfg is None:
        cfg = load_ei_v2_config()

    report = EIV2AnalysisReport(
        slot=slot,
        v1_chosen_id=v1_chosen_id,
        config_used={k: v.get("enabled", False) for k, v in cfg.items() if isinstance(v, dict)},
    )

    if not candidates:
        return report

    texts = [c.get("text", "") for c in candidates]
    ids = [c.get("id") or c.get("atom_id", f"c{i}") for i, c in enumerate(candidates)]

    candidate_reports = {cid: EIV2CandidateReport(candidate_id=cid) for cid in ids}

    # --- Safety classifier ---
    safety_cfg = cfg.get("safety_classifier", {})
    if safety_cfg.get("enabled", False):
        for cid, text in zip(ids, texts):
            result = classify_safety(text, slot=slot, cfg=safety_cfg, full_cfg=cfg)
            candidate_reports[cid].safety = result

    # --- Cross-encoder reranking ---
    rerank_cfg = cfg.get("cross_encoder", {})
    if rerank_cfg.get("enabled", False) and thesis:
        ranked = rerank_candidates(thesis, texts, ids, cfg=rerank_cfg)
        report.rerank_order = [r["id"] for r in ranked]
        for r in ranked:
            candidate_reports[r["id"]].rerank_score = r["score"]

    # --- Domain embeddings ---
    domain_cfg = cfg.get("domain_embeddings", {})
    if domain_cfg.get("enabled", False) and thesis and embed_fn:
        for cid, text in zip(ids, texts):
            sim = domain_thesis_similarity(
                thesis, text,
                persona_id=persona_id,
                topic_id=topic_id,
                cfg=cfg,
                embed_fn=embed_fn,
            )
            candidate_reports[cid].domain_similarity = sim

    # --- TTS readability ---
    tts_cfg = cfg.get("tts_readability", {})
    if tts_cfg.get("enabled", False):
        for cid, text in zip(ids, texts):
            tts_result = score_tts_readability(text, cfg=tts_cfg)
            candidate_reports[cid].tts_readability = tts_result

    # --- Semantic dedup ---
    dedup_cfg = cfg.get("semantic_dedup", {})
    if dedup_cfg.get("enabled", False) and len(texts) >= 2:
        dupes = detect_semantic_duplicates(texts, ids, cfg=dedup_cfg)
        report.semantic_duplicates = dupes

    # --- Emotion arc validation (chapter-level, not per-candidate) ---
    arc_cfg = cfg.get("emotion_arc", {})
    if arc_cfg.get("enabled", False) and chapter_text and arc_intent:
        arc_result = validate_emotion_arc(chapter_text, arc_intent, cfg=arc_cfg)
        report.emotion_arc = arc_result

    report.candidates = list(candidate_reports.values())

    # --- V2 composite selection ---
    report.v2_chosen_id = _select_v2_best(ids, candidate_reports, report, cfg)
    report.agreement = (report.v2_chosen_id == v1_chosen_id) if v1_chosen_id else None

    return report


def _select_v2_best(
    ids: List[str],
    candidate_reports: Dict[str, EIV2CandidateReport],
    report: EIV2AnalysisReport,
    cfg: Dict[str, Any],
) -> Optional[str]:
    """Composite scoring across V2 dimensions to pick a winner."""
    if not ids:
        return None

    weights = cfg.get("composite_weights", {})
    w_rerank = float(weights.get("rerank", 0.35))
    w_safety = float(weights.get("safety", 0.25))
    w_domain = float(weights.get("domain_similarity", 0.20))
    w_tts = float(weights.get("tts_readability", 0.20))

    best_id = ids[0]
    best_score = -999.0

    for cid in ids:
        cr = candidate_reports[cid]
        score = 0.0

        if cr.rerank_score is not None:
            score += w_rerank * cr.rerank_score

        if isinstance(cr.safety, dict):
            risk = float(cr.safety.get("risk_score", 0.0))
            score += w_safety * (1.0 - risk)

        if cr.domain_similarity is not None:
            score += w_domain * cr.domain_similarity

        if isinstance(cr.tts_readability, dict):
            readability = float(cr.tts_readability.get("composite", 0.5))
            score += w_tts * readability

        if score > best_score or (score == best_score and cid < best_id):
            best_score = score
            best_id = cid

    return best_id
