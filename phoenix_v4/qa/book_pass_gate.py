"""
Book pass gate: reject structurally valid but weak books.

Focus:
- clear chapter points (claims) across the book
- non-repetitive claims
- progression across acts
- ending includes net transformation + forward motion

This gate combines narrative metadata gates (mechanism/cost/identity/callback/macro)
with prose-level heuristics.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

from phoenix_v4.qa.callback_integrity_gate import validate_callback_integrity
from phoenix_v4.qa.cost_gradient_gate import validate_cost_gradient
from phoenix_v4.qa.identity_shift_gate import validate_identity_shift
from phoenix_v4.qa.macro_cadence_gate import validate_macro_cadence
from phoenix_v4.qa.mechanism_escalation_gate import validate_mechanism_escalation
from phoenix_v4.qa.validate_compiled_plan import ValidationResult
from phoenix_v4.qa._narrative_plan_utils import iter_chapter_slot_atom_ids, get_chapter_count
from phoenix_v4.rendering.book_renderer import clean_for_delivery
from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan


_STOP = {
    "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "at", "is", "are", "was", "were",
    "it", "that", "this", "with", "as", "be", "by", "you", "your", "we", "they", "their", "but",
}

_CLAIM_CUES = (
    "the point is",
    "what this means",
    "here is what",
    "this is not",
    "which means",
    "because",
)

_ACT1_WORDS = {"alarm", "anxious", "threat", "stuck", "freeze", "fear"}
_ACT2_WORDS = {"mechanism", "pattern", "because", "predict", "loop", "cost"}
_ACT3_WORDS = {"choose", "practice", "next", "start", "move", "can", "still"}


@dataclass
class BookPassDetails:
    valid: bool
    errors: list[str]
    warnings: list[str]
    metrics: dict[str, Any]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z']+", text.lower()) if t not in _STOP]


def _claim_key(sentence: str) -> str:
    toks = _tokens(sentence)
    if not toks:
        return ""
    # keep small stable semantic fingerprint
    return " ".join(sorted(set(toks))[:8])


def _jaccard(a: str, b: str) -> float:
    ta = set(_tokens(a))
    tb = set(_tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _act_scores(text: str) -> tuple[int, int, int]:
    toks = set(_tokens(text))
    s1 = len(toks & _ACT1_WORDS)
    s2 = len(toks & _ACT2_WORDS)
    s3 = len(toks & _ACT3_WORDS)
    return s1, s2, s3


def _collect_chapter_slot_texts(plan: dict[str, Any], prose_map: dict[str, str]) -> list[dict[str, list[str]]]:
    n = get_chapter_count(plan)
    out: list[dict[str, list[str]]] = [{ } for _ in range(n)]
    for ch, _si, slot_type, aid in iter_chapter_slot_atom_ids(plan):
        if ch >= n or "placeholder:" in aid or "silence:" in aid:
            continue
        prose = clean_for_delivery(prose_map.get(aid, "")).strip()
        if not prose:
            continue
        st = (slot_type or "").upper()
        out[ch].setdefault(st, []).append(prose)
    return out


def _pick_claim(ch_slot_text: dict[str, list[str]]) -> str:
    # prefer reflection/integration points, then story fallback
    candidates: list[str] = []
    for st in ("REFLECTION", "INTEGRATION", "STORY"):
        for block in ch_slot_text.get(st, []):
            candidates.extend(_sentences(block))
    if not candidates:
        return ""
    for s in candidates:
        low = s.lower()
        if any(c in low for c in _CLAIM_CUES):
            return s
    return candidates[0]


def validate_book_pass(
    plan: dict[str, Any],
    atom_metadata: dict[str, dict[str, Any]],
    *,
    prose_map: Optional[dict[str, str]] = None,
) -> BookPassDetails:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {}

    if prose_map is None:
        rr = resolve_prose_for_plan(plan)
        prose_map = rr.prose_map

    # Metadata progression gates
    for gate_name, res in (
        ("mechanism", validate_mechanism_escalation(plan, atom_metadata)),
        ("cost", validate_cost_gradient(plan, atom_metadata)),
        ("identity", validate_identity_shift(plan, atom_metadata)),
        ("callback", validate_callback_integrity(plan, atom_metadata)),
        ("macro", validate_macro_cadence(plan)),
    ):
        for e in res.errors:
            errors.append(f"{gate_name}_gate: {e}")
        for w in res.warnings:
            warnings.append(f"{gate_name}_gate: {w}")

    chapter_slots = _collect_chapter_slot_texts(plan, prose_map)
    chapter_claims = [_pick_claim(ch) for ch in chapter_slots]
    claim_keys = [_claim_key(c) for c in chapter_claims if c]
    n_ch = len(chapter_slots)
    claim_coverage = (len([c for c in chapter_claims if c]) / n_ch) if n_ch else 0.0
    metrics["chapter_count"] = n_ch
    metrics["claim_coverage"] = round(claim_coverage, 3)

    if n_ch and claim_coverage < 0.8:
        errors.append(f"book_pass: chapter claim coverage too low ({claim_coverage:.0%} < 80%).")

    # Repetitive claim gate
    if claim_keys:
        from collections import Counter
        counts = Counter(claim_keys)
        most_key, most_count = counts.most_common(1)[0]
        most_share = most_count / len(claim_keys)
        metrics["max_claim_share"] = round(most_share, 3)
        metrics["unique_claim_keys"] = len(counts)
        if most_share > 0.34:
            errors.append(
                f"book_pass: repetitive chapter claims ({most_count}/{len(claim_keys)} = {most_share:.0%} share)."
            )
        elif most_share > 0.25:
            warnings.append(
                f"book_pass: claim repetition elevated ({most_count}/{len(claim_keys)} = {most_share:.0%})."
            )
    else:
        errors.append("book_pass: no chapter claims extracted.")

    # Shuffleability proxy: adjacent claims should not be identical/redundant.
    sims = []
    for i in range(1, len(chapter_claims)):
        a, b = chapter_claims[i - 1], chapter_claims[i]
        if a and b:
            sims.append(_jaccard(a, b))
    if sims:
        mean_sim = sum(sims) / len(sims)
        hi_pairs = sum(1 for s in sims if s > 0.82)
        metrics["adjacent_claim_similarity_mean"] = round(mean_sim, 3)
        metrics["adjacent_claim_similarity_hi_pairs"] = hi_pairs
        if hi_pairs >= max(2, len(sims) // 4):
            errors.append("book_pass: chapters appear shuffleable/redundant (too many near-identical adjacent claims).")

    # Act progression proxy (lexical intent shift)
    if n_ch >= 6:
        one_third = n_ch // 3
        first = chapter_claims[:one_third]
        mid = chapter_claims[one_third : 2 * one_third]
        last = chapter_claims[2 * one_third :]

        def avg_score(claims: list[str], idx: int) -> float:
            vals = []
            for c in claims:
                if not c:
                    continue
                vals.append(_act_scores(c)[idx])
            return (sum(vals) / len(vals)) if vals else 0.0

        act1_first = avg_score(first, 0)
        act2_mid = avg_score(mid, 1)
        act3_last = avg_score(last, 2)
        act3_first = avg_score(first, 2)
        metrics["act_scores"] = {
            "act1_recognition_first": round(act1_first, 3),
            "act2_mechanism_mid": round(act2_mid, 3),
            "act3_agency_last": round(act3_last, 3),
            "act3_agency_first": round(act3_first, 3),
        }
        if act2_mid < 0.6:
            errors.append("book_pass: weak mechanism deepening in middle third.")
        if act3_last <= act3_first:
            errors.append("book_pass: no forward-agency increase by final third.")

    # Ending net transformation statement + forward motion
    if n_ch:
        last_text = " ".join(
            sum((v for v in chapter_slots[-1].values()), [])
        )
        low = last_text.lower()
        has_contrast = bool(re.search(r"\bnot\b.{0,80}\bbut\b", low)) or ("used to" in low and "now" in low)
        has_forward = any(w in low for w in ("next", "start", "practice", "choose", "from now on", "keep"))
        metrics["ending_has_contrast"] = has_contrast
        metrics["ending_has_forward"] = has_forward
        if not has_contrast:
            errors.append("book_pass: ending lacks net transformation contrast statement.")
        if not has_forward:
            errors.append("book_pass: ending lacks forward-motion directive.")

    return BookPassDetails(valid=len(errors) == 0, errors=errors, warnings=warnings, metrics=metrics)

