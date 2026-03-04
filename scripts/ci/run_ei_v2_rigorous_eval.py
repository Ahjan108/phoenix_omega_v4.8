#!/usr/bin/env python3
"""
Rigorous EI V1 vs V2 Evaluation Harness

Compiles and renders books across every working persona × topic × engine combo,
then evaluates each chapter on 10 quality dimensions for bestselling self-help
audiobooks.  Also runs the V1 vs V2 parallel adapter on every slot to measure
selection agreement, safety, duplication, TTS, and emotional-arc improvements.

Dimensions scored (0-1 each):
  1. THERAPEUTIC VALUE     – recognition-first, non-pathologizing, earned insight
  2. EMOTIONAL COHERENCE   – chapter arc matches blueprint
  3. ENGAGEMENT            – hook strength, narrative tension, forward momentum
  4. CHAPTER JOURNEY       – clear point, progression, actionable takeaway
  5. COHESION              – cross-chapter thread continuity
  6. LISTEN EXPERIENCE     – TTS readability, rhythm, breath, pacing
  7. MARKETABILITY         – invisible script, specificity, persona fit
  8. SAFETY COMPLIANCE     – no medical claims, no clinical language, no promo
  9. CONTENT UNIQUENESS    – no duplicate atoms, no repeated structures
 10. SOMATIC PRECISION     – body-grounded moments, concrete sensory detail

Outputs:
  artifacts/ei_v2/eval_rigorous_report.json   – full data
  artifacts/ei_v2/eval_rigorous_summary.txt   – executive summary

Usage:
  PYTHONPATH=. python scripts/ci/run_ei_v2_rigorous_eval.py
  PYTHONPATH=. python scripts/ci/run_ei_v2_rigorous_eval.py --full
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
from phoenix_v4.quality.ei_v2.dimension_gates import enforce_chapter_gates
from phoenix_v4.quality.ei_v2.hybrid_selector import hybrid_select
from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability
from phoenix_v4.quality.ei_v2.emotion_arc_validator import validate_emotion_arc
from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates
from phoenix_v4.quality.ei_v2.domain_embeddings import domain_thesis_similarity
from phoenix_v4.quality.ei_parallel_adapter import compare_slot, build_pipeline_comparison

# ── Working evaluation combos (verified against atom inventory) ──

EVAL_MATRIX_FULL = [
    ("gen_z_professionals", "anxiety", "spiral", "F006"),
    ("gen_z_professionals", "anxiety", "overwhelm", "F002"),
    ("gen_z_professionals", "overthinking", "spiral", "F006"),
    ("gen_alpha_students", "anxiety", "spiral", "F006"),
    ("educators", "anxiety", "overwhelm", "F006"),
    ("nyc_executives", "boundaries", "shame", "F006"),
    ("nyc_executives", "self_worth", "shame", "F006"),
]

EVAL_MATRIX_QUICK = [
    ("gen_z_professionals", "anxiety", "spiral", "F006"),
    ("gen_z_professionals", "overthinking", "spiral", "F006"),
    ("educators", "anxiety", "overwhelm", "F006"),
]

# ── Heuristic rubrics for the 10 quality dimensions ──

_HOOK_PATTERNS = [
    re.compile(r"\b(?:that\s+(?:morning|night|moment|day)|one\s+(?:morning|night|day))\b", re.I),
    re.compile(r"\b(?:you'?ve\s+(?:been|done|felt|noticed|tried)|you\s+(?:know|remember|feel))\b", re.I),
    re.compile(r"\b(?:here'?s\s+(?:the|what)|what\s+(?:if|happens|nobody))\b", re.I),
]
_TENSION_MARKERS = [
    re.compile(r"\b(?:but\s+then|until|except|and\s+then|still|yet|however)\b", re.I),
    re.compile(r"\b(?:not\s+because|not\s+yet|not\s+quite|almost|nearly)\b", re.I),
]
_FORWARD_MOMENTUM = [
    re.compile(r"\b(?:next|what\s+comes|the\s+next\s+(?:room|chapter|step))\b", re.I),
    re.compile(r"\b(?:there\s+is\s+(?:something|more)|not\s+(?:yet\s+)?(?:done|over|finished))\b", re.I),
]
_RECOGNITION_PATTERNS = [
    re.compile(r"\b(?:you'?ve\s+(?:been|already|probably)|you\s+(?:already|know\s+(?:this|that)|recognize))\b", re.I),
    re.compile(r"\b(?:sound\s+familiar|felt\s+(?:this|that)|noticed\s+(?:this|that))\b", re.I),
    re.compile(r"\b(?:before\s+you\s+(?:knew|named|realized)|without\s+(?:knowing|realizing))\b", re.I),
]
_JOURNEY_MARKERS = [
    re.compile(r"\b(?:so\s+(?:when|here'?s|this\s+is)|which\s+means|in\s+practice|what\s+this\s+looks\s+like)\b", re.I),
    re.compile(r"\b(?:the\s+(?:point|truth|pattern|mechanism|shift)|this\s+is\s+(?:why|where|how|what))\b", re.I),
    re.compile(r"\b(?:try\s+this|notice\s+(?:what|how|when)|pay\s+attention|the\s+next\s+time)\b", re.I),
]
_COHESION_MARKERS = [
    re.compile(r"\b(?:remember\s+(?:when|the|that)|earlier|as\s+we\s+(?:saw|discussed|noticed))\b", re.I),
    re.compile(r"\b(?:this\s+pattern|the\s+same\s+(?:thing|pattern|alarm)|again|once\s+more)\b", re.I),
]
_SOMATIC_WORDS = frozenset({
    "shoulder", "shoulders", "breath", "breathing", "stomach", "jaw", "chest",
    "heart", "racing", "tight", "tensed", "tension", "relax", "release",
    "ground", "grounded", "body", "sensation", "hands", "throat", "pulse",
    "heat", "cold", "sweat", "shaking", "trembling", "nausea",
})
_CONCRETE_PATTERNS = [
    re.compile(r"\b(?:at|in|on)\s+(?:the|my|his|her)\s+\w+", re.I),
    re.compile(r"\b\d{1,2}:\d{2}\b"),
    re.compile(r"\b(?:screen|phone|email|calendar|notification|desk|office|kitchen|car|bed)\b", re.I),
    re.compile(r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|morning|evening|night)\b", re.I),
]
_INVISIBLE_SCRIPT_PATTERNS = [
    re.compile(r"\byou\s+learned\s+to\b", re.I),
    re.compile(r"\byou'?ve\s+(?:been|spent)\s+so\s+long\b", re.I),
    re.compile(r"\b(?:the\s+part\s+(?:of\s+you|that)|the\s+version\s+of\s+you)\b", re.I),
]


def _hits(text: str, patterns: list) -> int:
    return sum(1 for p in patterns if p.search(text))

def _wc(text: str) -> int:
    return len(text.split())

def _somatic_density(text: str) -> float:
    words = set(re.findall(r"\b\w+\b", text.lower()))
    return len(words & _SOMATIC_WORDS) / max(1.0, _wc(text) / 100.0)


# ── Per-chapter evaluation ──

@dataclass
class ChapterEval:
    chapter_index: int
    word_count: int
    therapeutic_value: float = 0.0
    emotional_coherence: float = 0.0
    engagement: float = 0.0
    chapter_journey: float = 0.0
    cohesion: float = 0.0
    listen_experience: float = 0.0
    marketability: float = 0.0
    safety_compliance: float = 0.0
    content_uniqueness: float = 0.0
    somatic_precision: float = 0.0
    composite: float = 0.0
    issues: List[str] = field(default_factory=list)
    eval_ms: float = 0.0


def evaluate_chapter(
    chapter_text: str,
    chapter_index: int,
    arc_intent: Dict[str, Any],
    persona_id: str,
    topic_id: str,
    all_chapter_texts: List[str],
) -> ChapterEval:
    t0 = time.monotonic()
    wc = _wc(chapter_text)
    ev = ChapterEval(chapter_index=chapter_index, word_count=wc)
    if wc < 10:
        ev.eval_ms = (time.monotonic() - t0) * 1000
        return ev

    safety = classify_safety(chapter_text)
    patho = safety["categories"].get("pathologizing", {}).get("score", 0)
    reassur = safety["categories"].get("reassurance_spam", {}).get("score", 0)

    ev.therapeutic_value = min(1.0,
        0.4 * min(1.0, _hits(chapter_text, _RECOGNITION_PATTERNS) / 2.0)
        + 0.3 * (1.0 - patho)
        + 0.3 * (1.0 - reassur))

    arc_result = validate_emotion_arc(chapter_text, arc_intent)
    ev.emotional_coherence = {"PASS": 1.0, "WARN": 0.6}.get(arc_result["status"], 0.2)
    ev.issues.extend(arc_result.get("warnings", [])[:2])

    ev.engagement = min(1.0,
        0.35 * min(1.0, _hits(chapter_text, _HOOK_PATTERNS) / 2.0)
        + 0.40 * min(1.0, _hits(chapter_text, _TENSION_MARKERS) / 3.0)
        + 0.25 * min(1.0, _hits(chapter_text, _FORWARD_MOMENTUM) / 1.5))

    paras = [p.strip() for p in chapter_text.split("\n\n") if p.strip()]
    ev.chapter_journey = min(1.0,
        0.5 * min(1.0, _hits(chapter_text, _JOURNEY_MARKERS) / 3.0)
        + 0.3 * (1.0 if len(paras) >= 3 else 0.3)
        + 0.2 * min(1.0, wc / 400.0))

    ev.cohesion = min(1.0,
        0.6 * min(1.0, _hits(chapter_text, _COHESION_MARKERS) / 2.0)
        + 0.4 * (0.8 if chapter_index > 0 else 0.5))

    tts = score_tts_readability(chapter_text)
    ev.listen_experience = tts["composite"]
    ev.issues.extend(tts.get("issues", [])[:2])

    thesis = f"{topic_id} for {persona_id}"
    ev.marketability = min(1.0,
        0.3 * min(1.0, _hits(chapter_text, _INVISIBLE_SCRIPT_PATTERNS) / 1.5)
        + 0.4 * domain_thesis_similarity(thesis, chapter_text, persona_id=persona_id, topic_id=topic_id)
        + 0.3 * min(1.0, _hits(chapter_text, _CONCRETE_PATTERNS) / 4.0))

    ev.safety_compliance = 1.0 - safety["risk_score"]

    if len(all_chapter_texts) > 1:
        others = [t for i, t in enumerate(all_chapter_texts) if i != chapter_index and t.strip()]
        if others:
            dupes = detect_semantic_duplicates(
                [chapter_text] + others[:5],
                [f"ch{chapter_index}"] + [f"other{i}" for i in range(len(others[:5]))])
            max_sim = max((d["similarity"] for d in dupes), default=0.0)
            ev.content_uniqueness = max(0.0, 1.0 - max_sim * 2)
        else:
            ev.content_uniqueness = 1.0
    else:
        ev.content_uniqueness = 1.0

    ev.somatic_precision = min(1.0,
        0.6 * min(1.0, _somatic_density(chapter_text) / 3.0)
        + 0.4 * min(1.0, _hits(chapter_text, _CONCRETE_PATTERNS) / 4.0))

    ev.composite = (
        0.15 * ev.therapeutic_value
        + 0.12 * ev.emotional_coherence
        + 0.12 * ev.engagement
        + 0.12 * ev.chapter_journey
        + 0.08 * ev.cohesion
        + 0.12 * ev.listen_experience
        + 0.10 * ev.marketability
        + 0.08 * ev.safety_compliance
        + 0.05 * ev.content_uniqueness
        + 0.06 * ev.somatic_precision)

    ev.eval_ms = (time.monotonic() - t0) * 1000
    return ev


# ── Full book evaluation + V1/V2 slot comparison ──

@dataclass
class BookEvalResult:
    persona_id: str
    topic_id: str
    engine: str
    format_code: str
    total_chapters: int = 0
    total_words: int = 0
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    # Averages per dimension
    avg_therapeutic: float = 0.0
    avg_emotional_coherence: float = 0.0
    avg_engagement: float = 0.0
    avg_journey: float = 0.0
    avg_cohesion: float = 0.0
    avg_listen: float = 0.0
    avg_marketability: float = 0.0
    avg_safety: float = 0.0
    avg_uniqueness: float = 0.0
    avg_somatic: float = 0.0
    overall_composite: float = 0.0
    # V1 vs V2 comparison
    v1v2_total_slots: int = 0
    v1v2_agreements: int = 0
    v1v2_agreement_rate: float = 0.0
    v1v2_safety_flags: int = 0
    v1v2_dedup_flags: int = 0
    v1v2_tts_issues: int = 0
    v1v2_arc_issues: int = 0
    v1v2_avg_v1_ms: float = 0.0
    v1v2_avg_v2_ms: float = 0.0
    v1v2_details: Dict[str, Any] = field(default_factory=dict)
    # Dimension gates (from enforce_chapter_gates)
    dim_gate_fail_count: int = 0
    dim_gate_warn_count: int = 0
    dim_gate_chapters_with_fail: int = 0
    dim_gate_chapters_with_warn: int = 0
    dim_gate_per_dim_pass: Dict[str, int] = field(default_factory=dict)
    # Hybrid override (from hybrid_select)
    hybrid_total_slots: int = 0
    hybrid_override_count: int = 0
    hybrid_block_count: int = 0
    hybrid_override_success_count: int = 0
    # Timing
    compile_ms: float = 0.0
    render_ms: float = 0.0
    eval_ms: float = 0.0
    v1v2_ms: float = 0.0
    total_ms: float = 0.0
    safety_flags: List[str] = field(default_factory=list)
    arc_issues: List[str] = field(default_factory=list)


def evaluate_book(persona_id: str, topic_id: str, engine: str, fmt: str) -> Optional[BookEvalResult]:
    arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / f"{persona_id}__{topic_id}__{engine}__{fmt}.yaml"
    if not arc_path.exists():
        return None

    result = BookEvalResult(persona_id=persona_id, topic_id=topic_id, engine=engine, format_code=fmt)

    # ── Compile ──
    t0 = time.monotonic()
    try:
        from phoenix_v4.planning.arc_loader import load_arc
        from phoenix_v4.planning.catalog_planner import CatalogPlanner
        from phoenix_v4.planning.format_selector import FormatSelector
        from phoenix_v4.planning.assembly_compiler import compile_plan

        arc = load_arc(arc_path)
        planner = CatalogPlanner()
        book_spec = planner.produce_single(
            topic_id=topic_id, persona_id=persona_id,
            teacher_id="default_teacher", brand_id="phoenix_core",
            seed=f"eval_{persona_id}_{topic_id}_{engine}")
        bsd = book_spec.to_dict()
        bsd["atoms_model"] = "legacy"

        sel = FormatSelector()
        fp = sel.select_format(topic_id=topic_id, persona_id=persona_id)
        fpd = fp.to_compiler_input()
        if fpd.get("chapter_count") != arc.chapter_count:
            fpd["chapter_count"] = arc.chapter_count
            sd = fpd.get("slot_definitions") or []
            if len(sd) == 1:
                fpd["slot_definitions"] = [list(sd[0]) for _ in range(arc.chapter_count)]
            elif len(sd) > arc.chapter_count:
                fpd["slot_definitions"] = sd[:arc.chapter_count]
            else:
                fpd["slot_definitions"] = list(sd) + [list(sd[-1] if sd else []) for _ in range(arc.chapter_count - len(sd))]

        compiled = compile_plan(bsd, fpd, arc_path=arc_path, atoms_model="legacy")
        plan = {
            "plan_hash": compiled.plan_hash,
            "chapter_slot_sequence": compiled.chapter_slot_sequence,
            "atom_ids": compiled.atom_ids,
            "dominant_band_sequence": compiled.dominant_band_sequence,
            "emotional_role_sequence": compiled.emotional_role_sequence or [],
            "persona_id": persona_id, "topic_id": topic_id,
        }
    except Exception as exc:
        print(f"  COMPILE FAIL: {exc}", file=sys.stderr)
        return None
    result.compile_ms = (time.monotonic() - t0) * 1000

    # ── Render ──
    t0 = time.monotonic()
    try:
        from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan
        render_result = resolve_prose_for_plan(plan)
        prose_map = render_result.prose_map
    except Exception as exc:
        print(f"  RENDER FAIL: {exc}", file=sys.stderr)
        return None
    result.render_ms = (time.monotonic() - t0) * 1000

    chapter_slot_seq = plan["chapter_slot_sequence"]
    atom_ids = plan["atom_ids"]
    band_seq = plan.get("dominant_band_sequence") or []
    role_seq = plan.get("emotional_role_sequence") or []

    # Build chapter texts + per-slot atom data
    chapter_texts: List[str] = []
    chapter_slot_atoms: List[List[Dict[str, Any]]] = []  # for V1/V2 comparison
    idx = 0
    for ch_idx, slots in enumerate(chapter_slot_seq):
        parts, slot_atoms = [], []
        for slot in slots:
            if idx < len(atom_ids):
                aid = atom_ids[idx]
                prose = prose_map.get(aid, "")
                parts.append(prose)
                slot_atoms.append({"slot": slot, "atom_id": aid, "prose": prose})
                idx += 1
        chapter_texts.append("\n\n".join(p for p in parts if p))
        chapter_slot_atoms.append(slot_atoms)

    result.total_chapters = len(chapter_texts)
    result.total_words = sum(_wc(t) for t in chapter_texts)

    # ── Quality Evaluation ──
    t0 = time.monotonic()
    chapter_evals = []
    for ch_idx, ch_text in enumerate(chapter_texts):
        band = band_seq[ch_idx] if ch_idx < len(band_seq) else None
        role = role_seq[ch_idx] if ch_idx < len(role_seq) else ""
        arc_intent = {"band": band, "emotional_role": role, "chapter_index": ch_idx}
        ev = evaluate_chapter(ch_text, ch_idx, arc_intent, persona_id, topic_id, chapter_texts)
        chapter_evals.append(ev)
    result.eval_ms = (time.monotonic() - t0) * 1000

    if chapter_evals:
        result.avg_therapeutic = statistics.mean(e.therapeutic_value for e in chapter_evals)
        result.avg_emotional_coherence = statistics.mean(e.emotional_coherence for e in chapter_evals)
        result.avg_engagement = statistics.mean(e.engagement for e in chapter_evals)
        result.avg_journey = statistics.mean(e.chapter_journey for e in chapter_evals)
        result.avg_cohesion = statistics.mean(e.cohesion for e in chapter_evals)
        result.avg_listen = statistics.mean(e.listen_experience for e in chapter_evals)
        result.avg_marketability = statistics.mean(e.marketability for e in chapter_evals)
        result.avg_safety = statistics.mean(e.safety_compliance for e in chapter_evals)
        result.avg_uniqueness = statistics.mean(e.content_uniqueness for e in chapter_evals)
        result.avg_somatic = statistics.mean(e.somatic_precision for e in chapter_evals)
        result.overall_composite = statistics.mean(e.composite for e in chapter_evals)

    result.chapters = [asdict(e) for e in chapter_evals]

    for ev in chapter_evals:
        if ev.safety_compliance < 0.7:
            result.safety_flags.append(f"ch{ev.chapter_index}: safety={ev.safety_compliance:.2f}")
        for iss in ev.issues:
            if "arc" in iss.lower() or "deviation" in iss.lower() or "band" in iss.lower():
                result.arc_issues.append(f"ch{ev.chapter_index}: {iss}")

    # ── Dimension gates (enforce_chapter_gates) ──
    v2_cfg = load_ei_v2_config()
    dim_gate_cfg = v2_cfg.get("dimension_gates", {})
    dim_names = ("uniqueness", "engagement", "somatic_precision", "listen_experience", "cohesion")
    per_dim_pass: Dict[str, int] = {d: 0 for d in dim_names}
    chapters_with_fail = 0
    chapters_with_warn = 0
    for ch_idx, ch_text in enumerate(chapter_texts):
        gate_report = enforce_chapter_gates(ch_text, ch_idx, chapter_texts, dim_gate_cfg)
        result.dim_gate_fail_count += gate_report.fail_count
        result.dim_gate_warn_count += gate_report.warn_count
        if gate_report.fail_count > 0:
            chapters_with_fail += 1
        if gate_report.warn_count > 0:
            chapters_with_warn += 1
        for g in gate_report.gates:
            if g.dimension in per_dim_pass and g.status == "PASS":
                per_dim_pass[g.dimension] += 1
    result.dim_gate_per_dim_pass = per_dim_pass
    result.dim_gate_chapters_with_fail = chapters_with_fail
    result.dim_gate_chapters_with_warn = chapters_with_warn

    # ── V1 vs V2 Parallel Slot Comparison + Hybrid Override ──
    t0 = time.monotonic()
    v1_cfg = {"selector": "ga_best"}
    slot_comparisons = []

    for ch_idx, (ch_text, slot_atoms) in enumerate(zip(chapter_texts, chapter_slot_atoms)):
        band = band_seq[ch_idx] if ch_idx < len(band_seq) else None
        role = role_seq[ch_idx] if ch_idx < len(role_seq) else ""
        arc_intent = {"band": band, "emotional_role": role, "chapter_index": ch_idx}
        for s_idx, sa in enumerate(slot_atoms):
            all_candidates_for_slot = [
                {"id": a["atom_id"], "text": a["prose"]}
                for a in slot_atoms if a["prose"]
            ]
            if len(all_candidates_for_slot) < 2:
                continue
            thesis = f"{topic_id} for {persona_id}"
            try:
                comparison = compare_slot(
                    slot=sa["slot"],
                    chapter_index=ch_idx,
                    slot_index=s_idx,
                    candidates_raw=all_candidates_for_slot,
                    persona_id=persona_id,
                    topic_id=topic_id,
                    thesis=thesis,
                    v1_cfg=v1_cfg,
                    v2_cfg=v2_cfg,
                    chapter_text=ch_text,
                    arc_intent=arc_intent,
                )
                slot_comparisons.append(comparison)
            except Exception:
                pass
            # Hybrid override stats (same slots as compare_slot)
            try:
                hd = hybrid_select(
                    slot=sa["slot"],
                    chapter_index=ch_idx,
                    slot_index=s_idx,
                    candidates_raw=all_candidates_for_slot,
                    persona_id=persona_id,
                    topic_id=topic_id,
                    thesis=thesis,
                    v1_cfg=v1_cfg,
                    v2_cfg=v2_cfg,
                    chapter_text=ch_text,
                    arc_intent=arc_intent,
                )
                result.hybrid_total_slots += 1
                if hd.override_applied:
                    result.hybrid_override_count += 1
                    if hd.v2_composite_v2winner > hd.v1_composite:
                        result.hybrid_override_success_count += 1
                if hd.block_applied:
                    result.hybrid_block_count += 1
            except Exception:
                pass

    if slot_comparisons:
        pipeline_cmp = build_pipeline_comparison(
            slot_comparisons,
            plan_hash=plan.get("plan_hash", ""),
            persona_id=persona_id,
            topic_id=topic_id,
        )
        result.v1v2_total_slots = pipeline_cmp.total_slots
        result.v1v2_agreements = pipeline_cmp.agreements
        result.v1v2_agreement_rate = pipeline_cmp.agreement_rate
        result.v1v2_safety_flags = len(pipeline_cmp.v2_safety_flags)
        result.v1v2_dedup_flags = len(pipeline_cmp.v2_dedup_flags)
        result.v1v2_tts_issues = len(pipeline_cmp.v2_tts_issues)
        result.v1v2_arc_issues = len(pipeline_cmp.v2_arc_issues)
        result.v1v2_avg_v1_ms = pipeline_cmp.timing_summary.get("avg_v1_ms", 0)
        result.v1v2_avg_v2_ms = pipeline_cmp.timing_summary.get("avg_v2_ms", 0)
        result.v1v2_details = pipeline_cmp.to_dict()

    result.v1v2_ms = (time.monotonic() - t0) * 1000
    result.total_ms = result.compile_ms + result.render_ms + result.eval_ms + result.v1v2_ms

    return result


# ── Summary ──

def build_summary(results: List[BookEvalResult], total_time_s: float) -> str:
    W = 72
    lines = [
        "=" * W,
        "  RIGOROUS EVALUATION: SELF-HELP AUDIOBOOK QUALITY + V1 vs V2",
        "=" * W, "",
        f"  Books evaluated:   {len(results)}",
        f"  Total chapters:    {sum(r.total_chapters for r in results)}",
        f"  Total words:       {sum(r.total_words for r in results):,}",
        f"  Personas covered:  {len(set(r.persona_id for r in results))}",
        f"  Total time:        {total_time_s:.1f}s",
        "",
    ]

    # ── Quality Dimension Scores ──
    dims = [
        ("Therapeutic Value",   [r.avg_therapeutic for r in results]),
        ("Emotional Coherence", [r.avg_emotional_coherence for r in results]),
        ("Engagement",          [r.avg_engagement for r in results]),
        ("Chapter Journey",     [r.avg_journey for r in results]),
        ("Cohesion",            [r.avg_cohesion for r in results]),
        ("Listen Experience",   [r.avg_listen for r in results]),
        ("Marketability",       [r.avg_marketability for r in results]),
        ("Safety Compliance",   [r.avg_safety for r in results]),
        ("Content Uniqueness",  [r.avg_uniqueness for r in results]),
        ("Somatic Precision",   [r.avg_somatic for r in results]),
    ]

    lines.append("  AUDIOBOOK QUALITY DIMENSIONS (avg across all books)")
    lines.append("  " + "-" * (W - 4))
    for name, scores in dims:
        avg = statistics.mean(scores)
        lo, hi = min(scores), max(scores)
        bar_len = 25
        filled = int(avg * bar_len)
        bar = "#" * filled + "." * (bar_len - filled)
        grade = "A" if avg >= 0.8 else ("B" if avg >= 0.6 else ("C" if avg >= 0.4 else ("D" if avg >= 0.2 else "F")))
        lines.append(f"  {grade} {name:<22} [{bar}] {avg:.3f}  (lo={lo:.2f} hi={hi:.2f})")

    overall = statistics.mean(r.overall_composite for r in results)
    lines.append("")
    grade = "A" if overall >= 0.8 else ("B" if overall >= 0.6 else ("C" if overall >= 0.4 else ("D" if overall >= 0.2 else "F")))
    lines.append(f"  {grade} OVERALL COMPOSITE:  {overall:.4f}")
    lines.append("")

    # ── V1 vs V2 Head-to-Head ──
    lines.append("  V1 vs V2 PARALLEL COMPARISON")
    lines.append("  " + "-" * (W - 4))
    total_slots = sum(r.v1v2_total_slots for r in results)
    total_agree = sum(r.v1v2_agreements for r in results)
    rate = total_agree / max(1, total_slots)
    lines.append(f"  Total slots compared:  {total_slots}")
    lines.append(f"  Agreements:            {total_agree} ({rate*100:.1f}%)")
    lines.append(f"  Disagreements:         {total_slots - total_agree}")
    lines.append(f"  V2 safety flags:       {sum(r.v1v2_safety_flags for r in results)}")
    lines.append(f"  V2 dedup flags:        {sum(r.v1v2_dedup_flags for r in results)}")
    lines.append(f"  V2 TTS issues:         {sum(r.v1v2_tts_issues for r in results)}")
    lines.append(f"  V2 arc issues:         {sum(r.v1v2_arc_issues for r in results)}")
    lines.append("")

    # ── Performance ──
    lines.append("  PERFORMANCE (per book)")
    lines.append("  " + "-" * (W - 4))
    for label, getter in [
        ("Compile",  lambda r: r.compile_ms),
        ("Render",   lambda r: r.render_ms),
        ("Evaluate", lambda r: r.eval_ms),
        ("V1vs V2",  lambda r: r.v1v2_ms),
        ("Total",    lambda r: r.total_ms),
    ]:
        vals = [getter(r) for r in results]
        lines.append(f"  {label:<10} avg: {statistics.mean(vals):>8.0f}ms  "
                      f"min: {min(vals):>6.0f}ms  max: {max(vals):>6.0f}ms")

    v1_times = [r.v1v2_avg_v1_ms for r in results if r.v1v2_avg_v1_ms > 0]
    v2_times = [r.v1v2_avg_v2_ms for r in results if r.v1v2_avg_v2_ms > 0]
    if v1_times and v2_times:
        lines.append("")
        lines.append(f"  V1 avg per slot: {statistics.mean(v1_times):.2f}ms")
        lines.append(f"  V2 avg per slot: {statistics.mean(v2_times):.2f}ms")
        ratio = statistics.mean(v2_times) / max(0.001, statistics.mean(v1_times))
        lines.append(f"  V2/V1 ratio:     {ratio:.2f}x {'(V2 slower)' if ratio > 1 else '(V2 faster)'}")
    lines.append("")

    # ── Per-Book Breakdown ──
    lines.append("  PER-BOOK RESULTS")
    lines.append("  " + "-" * (W - 4))
    sorted_books = sorted(results, key=lambda r: r.overall_composite, reverse=True)
    for r in sorted_books:
        agree_str = f" V1V2={r.v1v2_agreement_rate*100:.0f}%" if r.v1v2_total_slots else ""
        lines.append(
            f"  {r.overall_composite:.4f}  {r.persona_id}/{r.topic_id}/{r.engine}"
            f"  ({r.total_chapters}ch, {r.total_words}w, {r.total_ms:.0f}ms){agree_str}"
        )
    lines.append("")

    # ── Weakest → Strongest ──
    lines.append("  DIMENSIONS RANKED (weakest → strongest)")
    lines.append("  " + "-" * (W - 4))
    dim_avgs = sorted(
        [(name, statistics.mean(scores)) for name, scores in dims],
        key=lambda x: x[1])
    for name, avg in dim_avgs:
        grade = "A" if avg >= 0.8 else ("B" if avg >= 0.6 else ("C" if avg >= 0.4 else ("D" if avg >= 0.2 else "F")))
        indicator = " *** NEEDS WORK ***" if avg < 0.4 else (" * room to improve *" if avg < 0.6 else "")
        lines.append(f"  {grade}  {avg:.3f}  {name}{indicator}")

    # ── Issues ──
    all_safety = [f for r in results for f in r.safety_flags]
    all_arc = [f for r in results for f in r.arc_issues]
    if all_safety:
        lines.append("")
        lines.append(f"  SAFETY FLAGS ({len(all_safety)})")
        for f in all_safety[:8]:
            lines.append(f"    {f}")
    if all_arc:
        lines.append("")
        lines.append(f"  ARC ISSUES ({len(all_arc)})")
        for f in all_arc[:8]:
            lines.append(f"    {f}")

    lines.append("")
    lines.append("=" * W)
    return "\n".join(lines)


def _build_dimension_gate_summary(results: List[BookEvalResult]) -> Dict[str, Any]:
    total_chapters = sum(r.total_chapters for r in results)
    dim_names = ("uniqueness", "engagement", "somatic_precision", "listen_experience", "cohesion")
    pass_rates = {}
    for dim in dim_names:
        passed = sum(r.dim_gate_per_dim_pass.get(dim, 0) for r in results)
        pass_rates[dim] = round(passed / max(1, total_chapters), 4)
    return {
        "total_chapters": total_chapters,
        "total_fail_count": sum(r.dim_gate_chapters_with_fail for r in results),
        "total_warn_count": sum(r.dim_gate_chapters_with_warn for r in results),
        "dimension_pass_rates": pass_rates,
        "failures_per_book": [r.dim_gate_fail_count for r in results],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="Run all 7 working books")
    ap.add_argument("--sample", type=int, default=None)
    args = ap.parse_args()

    matrix = EVAL_MATRIX_FULL if args.full else (EVAL_MATRIX_FULL[:args.sample] if args.sample else EVAL_MATRIX_QUICK)

    out_dir = REPO_ROOT / "artifacts" / "ei_v2"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"  Rigorous EI Evaluation — {len(matrix)} books")
    print(f"{'='*50}")

    results: List[BookEvalResult] = []
    t_total = time.monotonic()

    for i, (persona, topic, engine, fmt) in enumerate(matrix):
        label = f"{persona}/{topic}/{engine}"
        print(f"\n[{i+1}/{len(matrix)}] {label} ...", end="", flush=True)
        book = evaluate_book(persona, topic, engine, fmt)
        if book:
            results.append(book)
            agree_str = f" V1V2={book.v1v2_agreement_rate*100:.0f}%" if book.v1v2_total_slots else ""
            print(f" score={book.overall_composite:.4f} ({book.total_chapters}ch, {book.total_words}w, {book.total_ms:.0f}ms){agree_str}")
        else:
            print(" SKIP")

    total_time = time.monotonic() - t_total

    if not results:
        print("\nNo books evaluated successfully.", file=sys.stderr)
        return 1

    report_data = {
        "meta": {
            "books_evaluated": len(results),
            "total_chapters": sum(r.total_chapters for r in results),
            "total_words": sum(r.total_words for r in results),
            "personas": list(set(r.persona_id for r in results)),
            "total_time_s": round(total_time, 2),
        },
        "quality_scores": {
            "overall_composite": round(statistics.mean(r.overall_composite for r in results), 4),
            "therapeutic_value": round(statistics.mean(r.avg_therapeutic for r in results), 4),
            "emotional_coherence": round(statistics.mean(r.avg_emotional_coherence for r in results), 4),
            "engagement": round(statistics.mean(r.avg_engagement for r in results), 4),
            "chapter_journey": round(statistics.mean(r.avg_journey for r in results), 4),
            "cohesion": round(statistics.mean(r.avg_cohesion for r in results), 4),
            "listen_experience": round(statistics.mean(r.avg_listen for r in results), 4),
            "marketability": round(statistics.mean(r.avg_marketability for r in results), 4),
            "safety_compliance": round(statistics.mean(r.avg_safety for r in results), 4),
            "content_uniqueness": round(statistics.mean(r.avg_uniqueness for r in results), 4),
            "somatic_precision": round(statistics.mean(r.avg_somatic for r in results), 4),
        },
        "v1_vs_v2": {
            "total_slots": sum(r.v1v2_total_slots for r in results),
            "agreements": sum(r.v1v2_agreements for r in results),
            "agreement_rate": round(sum(r.v1v2_agreements for r in results) / max(1, sum(r.v1v2_total_slots for r in results)), 4),
            "safety_flags": sum(r.v1v2_safety_flags for r in results),
            "dedup_flags": sum(r.v1v2_dedup_flags for r in results),
            "tts_issues": sum(r.v1v2_tts_issues for r in results),
            "arc_issues": sum(r.v1v2_arc_issues for r in results),
        },
        "timing": {
            "avg_compile_ms": round(statistics.mean(r.compile_ms for r in results), 1),
            "avg_render_ms": round(statistics.mean(r.render_ms for r in results), 1),
            "avg_eval_ms": round(statistics.mean(r.eval_ms for r in results), 1),
            "avg_v1v2_ms": round(statistics.mean(r.v1v2_ms for r in results), 1),
            "avg_total_ms": round(statistics.mean(r.total_ms for r in results), 1),
        },
        "dimension_gate_summary": _build_dimension_gate_summary(results),
        "hybrid_override": {
            "total_slots": sum(r.hybrid_total_slots for r in results),
            "override_count": sum(r.hybrid_override_count for r in results),
            "block_count": sum(r.hybrid_block_count for r in results),
            "override_success_count": sum(r.hybrid_override_success_count for r in results),
        },
        "books": [asdict(r) for r in results],
    }

    json_path = out_dir / "eval_rigorous_report.json"
    json_path.write_text(json.dumps(report_data, indent=2, default=str), encoding="utf-8")

    summary = build_summary(results, total_time)
    summary_path = out_dir / "eval_rigorous_summary.txt"
    summary_path.write_text(summary, encoding="utf-8")

    print(f"\n{summary}")
    print(f"\n  Reports: {json_path}")
    print(f"           {summary_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
