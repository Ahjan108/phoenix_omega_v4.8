"""
EI Adapter: per-slot candidate selection for Enlightened Intelligence V1.

Applies heuristic scoring (somatic precision, concreteness, risk penalty, thesis alignment),
threshold gates (fail-open), embedding thesis alignment, teacher integrity penalties,
and deterministic or GA-based selection with optional LLM tie-break.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# --- Body words (somatic precision) ---
BODY_WORDS = frozenset({
    "shoulder", "shoulders", "breath", "breathing", "stomach", "jaw", "chest",
    "heart", "racing", "tight", "tensed", "tension", "relax", "release",
    "ground", "grounded", "body", "sensation", "felt", "feeling",
})

# --- Concrete patterns (grounded, specific) ---
CONCRETE_PATTERNS: List[re.Pattern] = [
    re.compile(r"\b(?:at|in|on)\s+the\s+\w+", re.I),
    re.compile(r"\b\d+\s*(?:am|pm|o'?clock|minutes?|hours?)\b", re.I),
    re.compile(r"\b(?:screen|phone|email|calendar|notification)\b", re.I),
    re.compile(r"\b(?:gate|desk|office|kitchen|bedroom)\b", re.I),
]

# --- Risk patterns (overclaim, miracle language) ---
RISK_PATTERNS: List[re.Pattern] = [
    re.compile(r"\b(?:instantly|everything\s+changed|miracle|guarantee|cure)\b", re.I),
    re.compile(r"['\"]it\s+was\s+intense['\"]", re.I),
    re.compile(r"['\"]the\s+only\s+way['\"]", re.I),
]


@dataclass
class EICandidate:
    """A candidate atom for EI selection."""
    atom_id: str
    text: str
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def candidate_id(self) -> str:
        return self.atom_id


@dataclass
class EISelectionDebug:
    """Debug info for EI selection."""
    slot: str
    selector: str
    thresholds_applied: Dict[str, Any] = field(default_factory=dict)
    rejected_candidates: List[str] = field(default_factory=list)
    scoring_table: List[Dict[str, Any]] = field(default_factory=list)
    seed_used: Optional[str] = None
    llm_override: Optional[str] = None
    embedding_similarity: Optional[float] = None
    teacher_penalties: Dict[str, float] = field(default_factory=dict)


@dataclass
class EISelectionOutput:
    """Result of EI selection."""
    chosen: EICandidate
    debug: EISelectionDebug


def _score_text(text: str) -> Dict[str, float]:
    """
    Heuristic scoring for somatic_precision, concreteness, risk_penalty, thesis_alignment.
    thesis_alignment is 0.0 here; caller applies embedding similarity separately.
    """
    text_lower = text.lower()
    words = set(text_lower.split())

    # Somatic precision: body word density
    body_hits = len(words & BODY_WORDS)
    somatic_precision = min(1.0, body_hits / 3.0) if body_hits else 0.0

    # Concreteness: concrete pattern matches
    concrete_hits = sum(1 for p in CONCRETE_PATTERNS if p.search(text))
    concreteness = min(1.0, concrete_hits / 2.0) if concrete_hits else 0.0

    # Risk penalty: overclaim / miracle language
    risk_hits = sum(1 for p in RISK_PATTERNS if p.search(text))
    risk_penalty = min(1.0, risk_hits / 2.0) if risk_hits else 0.0

    return {
        "somatic_precision": somatic_precision,
        "concreteness": concreteness,
        "risk_penalty": risk_penalty,
        "thesis_alignment": 0.0,
    }


def _selector_index(selector_key: str, available_count: int) -> int:
    """
    SHA256 deterministic index. Same algorithm as slot_resolver.
    """
    if available_count <= 0:
        return 0
    digest = hashlib.sha256(selector_key.encode("utf-8")).digest()
    n = int.from_bytes(digest[:16], "big")
    return n % available_count


def _apply_threshold_gates(
    candidates: List[EICandidate],
    cfg: Dict[str, Any],
) -> tuple[List[EICandidate], List[str], Dict[str, Any]]:
    """
    Filter candidates by threshold config. Fail-open: if no thresholds or all fail,
    return all candidates.
    """
    thresholds = cfg.get("thresholds", {}) or {}
    if not thresholds:
        return candidates, [], {}

    original = list(candidates)
    remaining: List[EICandidate] = []
    rejected: List[str] = []
    applied: Dict[str, Any] = {}

    for candidate in original:
        scores = _score_text(candidate.text)
        fail = False
        for key, threshold in thresholds.items():
            if key not in scores:
                continue
            val = scores[key]
            if isinstance(threshold, str):
                # e.g. "min:0.3" or "max:0.5"
                if threshold.startswith("min:"):
                    min_val = float(threshold.split(":")[1])
                    if val < min_val:
                        fail = True
                        applied[key] = {"min": min_val, "actual": val}
                elif threshold.startswith("max:"):
                    max_val = float(threshold.split(":")[1])
                    if val > max_val:
                        fail = True
                        applied[key] = {"max": max_val, "actual": val}
            elif isinstance(threshold, (int, float)):
                if key == "risk_penalty" and val > threshold:
                    fail = True
                    applied[key] = {"max": threshold, "actual": val}
                elif key in ("somatic_precision", "concreteness", "thesis_alignment") and val < threshold:
                    fail = True
                    applied[key] = {"min": threshold, "actual": val}
            if fail:
                break
        if fail:
            rejected.append(candidate.atom_id)
        else:
            remaining.append(candidate)

    if not remaining and rejected:
        # Fail-open: return all original candidates
        return original, [], applied
    return remaining, rejected, applied


def apply_ei_selection(
    *,
    slot: str,
    candidates_raw: List[Dict[str, Any]],
    persona_id: str,
    topic_id: str,
    thesis: str,
    cfg: Dict[str, Any],
    selector_key: Optional[str] = None,
    teacher_mode: bool = False,
    embed_fn: Optional[Callable[..., Any]] = None,
    call_llm_json: Optional[Callable[..., Any]] = None,
) -> EISelectionOutput:
    """
    Main entry point: apply threshold gates, embedding thesis alignment,
    teacher integrity, scoring, selector (rule_best hash or ga_best score),
    and optional LLM tie-break.
    """
    cfg = cfg or {}
    selector = cfg.get("selector", "rule_best")
    allow_override = cfg.get("allow_override_for_rule_best", True)

    # Build EICandidates
    candidates: List[EICandidate] = []
    for c in candidates_raw or []:
        atom_id = c.get("id") or c.get("atom_id", "")
        text = c.get("text", "")
        meta = c.get("meta") or c.get("metadata") or {}
        if atom_id:
            candidates.append(EICandidate(atom_id=atom_id, text=text, meta=meta))

    if not candidates:
        empty = EICandidate(atom_id="", text="", meta={})
        return EISelectionOutput(
            chosen=empty,
            debug=EISelectionDebug(slot=slot, selector="none", rejected_candidates=[]),
        )

    # Threshold gates
    candidates, rejected, thresholds_applied = _apply_threshold_gates(candidates, cfg)

    # Thesis alignment (embedding similarity) - floor/ceiling from config
    thesis_cfg = cfg.get("thesis_alignment", {}) or {}
    floor_val = float(thesis_cfg.get("floor", 0.0))
    ceiling_val = float(thesis_cfg.get("ceiling", 1.0))

    if thesis and embed_fn:
        try:
            from phoenix_v4.quality.ei_embeddings import thesis_similarity
            for c in candidates:
                sim = thesis_similarity(thesis, c.text, embed_fn=embed_fn)
                sim_clamped = max(floor_val, min(ceiling_val, sim))
                c.meta["embedding_similarity"] = sim_clamped
        except Exception:
            pass

    # Teacher integrity penalties
    teacher_penalties: Dict[str, float] = {}
    if teacher_mode:
        try:
            from phoenix_v4.quality.teacher_integrity import compute_teacher_integrity_penalty
            for c in candidates:
                penalty = compute_teacher_integrity_penalty(c.text, cfg=cfg.get("teacher_integrity", {}))
                teacher_penalties[c.atom_id] = penalty.penalty
                c.meta["teacher_penalty"] = penalty.penalty
        except Exception:
            pass

    # Score each candidate
    scoring_table: List[Dict[str, Any]] = []
    for c in candidates:
        scores = _score_text(c.text)
        emb_sim = c.meta.get("embedding_similarity", 0.0)
        scores["thesis_alignment"] = emb_sim
        penalty = teacher_penalties.get(c.atom_id, 0.0)
        composite = (
            scores["somatic_precision"] * 0.25
            + scores["concreteness"] * 0.25
            + scores["thesis_alignment"] * 0.35
            - scores["risk_penalty"] * 0.25
            - penalty * 0.1
        )
        composite = max(0.0, min(1.0, composite))
        scoring_table.append({
            "candidate_id": c.atom_id,
            "somatic_precision": scores["somatic_precision"],
            "concreteness": scores["concreteness"],
            "risk_penalty": scores["risk_penalty"],
            "thesis_alignment": scores["thesis_alignment"],
            "teacher_penalty": penalty,
            "composite": composite,
        })

    # Selection
    seed = selector_key or f"{persona_id}:{topic_id}:{slot}"
    chosen: EICandidate
    llm_override: Optional[str] = None

    if selector == "rule_best":
        # Deterministic: pick by hash among top scorers
        scoring_table.sort(key=lambda r: (-r["composite"], r["candidate_id"]))
        top_score = scoring_table[0]["composite"] if scoring_table else 0.0
        tied = [r for r in scoring_table if r["composite"] >= top_score - 0.001]
        tied_ids = [r["candidate_id"] for r in tied]
        idx = _selector_index(seed, len(tied_ids))
        chosen_id = tied_ids[idx]
        chosen = next(c for c in candidates if c.atom_id == chosen_id)

        # Optional LLM tie-break
        if allow_override and call_llm_json and len(tied_ids) > 1:
            try:
                from phoenix_v4.quality.ei_llm_judge import judge_tie_break
                result = judge_tie_break(
                    thesis=thesis,
                    candidates=[c for c in candidates if c.atom_id in tied_ids],
                    call_llm_json=call_llm_json,
                    cfg=cfg.get("llm_judge", {}),
                )
                if result and result.chosen_id:
                    llm_override = result.chosen_id
                    chosen = next((c for c in candidates if c.atom_id == result.chosen_id), chosen)
            except Exception:
                pass
    else:
        # ga_best: highest composite wins
        scoring_table.sort(key=lambda r: (-r["composite"], r["candidate_id"]))
        chosen_id = scoring_table[0]["candidate_id"] if scoring_table else candidates[0].atom_id
        chosen = next(c for c in candidates if c.atom_id == chosen_id)

    embedding_sim = chosen.meta.get("embedding_similarity")

    debug = EISelectionDebug(
        slot=slot,
        selector=selector,
        thresholds_applied=thresholds_applied,
        rejected_candidates=rejected,
        scoring_table=scoring_table,
        seed_used=seed,
        llm_override=llm_override,
        embedding_similarity=embedding_sim,
        teacher_penalties=teacher_penalties,
    )

    return EISelectionOutput(chosen=chosen, debug=debug)
