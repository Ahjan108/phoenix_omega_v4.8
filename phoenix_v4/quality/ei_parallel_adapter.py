"""
EI Parallel Adapter: runs V1 and V2 side-by-side on the same candidates.

Produces a comparison report showing:
  - V1 chosen candidate + scoring breakdown
  - V2 chosen candidate + all dimension scores
  - Agreement/disagreement and reasons
  - Per-candidate V1 vs V2 score deltas
  - Aggregate statistics for multi-slot comparison

Wire into the pipeline with --ei-v2-compare to produce comparison artifacts
without changing production behavior (V1 always wins; V2 is advisory).
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from phoenix_v4.quality.ei_adapter import (
    EISelectionOutput,
    apply_ei_selection,
)
from phoenix_v4.quality.ei_v2 import (
    EIV2AnalysisReport,
    run_ei_v2_analysis,
)
from phoenix_v4.quality.ei_v2.config import load_ei_v2_config


@dataclass
class SlotComparisonResult:
    """Comparison for a single slot invocation."""
    slot: str
    chapter_index: int
    slot_index: int
    v1_chosen_id: str
    v2_chosen_id: Optional[str]
    agreement: bool
    v1_composite: float
    v2_composite: Optional[float]
    v1_debug: Dict[str, Any] = field(default_factory=dict)
    v2_report: Dict[str, Any] = field(default_factory=dict)
    timing_ms: Dict[str, float] = field(default_factory=dict)


@dataclass
class PipelineComparisonReport:
    """Aggregate comparison across all slots in a pipeline run."""
    plan_hash: str
    persona_id: str
    topic_id: str
    total_slots: int = 0
    agreements: int = 0
    disagreements: int = 0
    agreement_rate: float = 0.0
    slot_results: List[Dict[str, Any]] = field(default_factory=list)
    v2_safety_flags: List[Dict[str, Any]] = field(default_factory=list)
    v2_dedup_flags: List[Dict[str, Any]] = field(default_factory=list)
    v2_tts_issues: List[Dict[str, Any]] = field(default_factory=list)
    v2_arc_issues: List[Dict[str, Any]] = field(default_factory=list)
    timing_summary: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)


def compare_slot(
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
    selector_key: Optional[str] = None,
    teacher_mode: bool = False,
    embed_fn: Optional[Callable] = None,
    call_llm_json: Optional[Callable] = None,
    chapter_text: Optional[str] = None,
    arc_intent: Optional[Dict[str, Any]] = None,
) -> SlotComparisonResult:
    """
    Run V1 and V2 on the same candidates and compare results.

    V1 output is authoritative (used by the pipeline). V2 is advisory only.
    """
    if v2_cfg is None:
        v2_cfg = load_ei_v2_config()

    # --- Run V1 ---
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

    # --- Run V2 ---
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
    agreement = (v1_chosen_id == v2_chosen_id) if v2_chosen_id else True

    # Extract V2 composite for chosen candidate
    v2_composite = None
    for cr in v2_report.candidates:
        if cr.candidate_id == v2_chosen_id:
            if cr.rerank_score is not None:
                v2_composite = cr.rerank_score
            break

    return SlotComparisonResult(
        slot=slot,
        chapter_index=chapter_index,
        slot_index=slot_index,
        v1_chosen_id=v1_chosen_id,
        v2_chosen_id=v2_chosen_id,
        agreement=agreement,
        v1_composite=v1_composite,
        v2_composite=v2_composite,
        v1_debug={
            "selector": v1_result.debug.selector,
            "scoring_table": v1_result.debug.scoring_table,
            "rejected": v1_result.debug.rejected_candidates,
            "llm_override": v1_result.debug.llm_override,
        },
        v2_report=v2_report.to_dict(),
        timing_ms={"v1_ms": round(v1_ms, 2), "v2_ms": round(v2_ms, 2)},
    )


def build_pipeline_comparison(
    slot_results: List[SlotComparisonResult],
    *,
    plan_hash: str = "",
    persona_id: str = "",
    topic_id: str = "",
) -> PipelineComparisonReport:
    """
    Aggregate slot-level comparisons into a full pipeline report.
    """
    report = PipelineComparisonReport(
        plan_hash=plan_hash,
        persona_id=persona_id,
        topic_id=topic_id,
        total_slots=len(slot_results),
    )

    total_v1_ms = 0.0
    total_v2_ms = 0.0

    for sr in slot_results:
        if sr.agreement:
            report.agreements += 1
        else:
            report.disagreements += 1

        report.slot_results.append(asdict(sr))
        total_v1_ms += sr.timing_ms.get("v1_ms", 0)
        total_v2_ms += sr.timing_ms.get("v2_ms", 0)

        # Collect V2 flags for executive summary
        v2_data = sr.v2_report
        for cr in v2_data.get("candidates", []):
            safety = cr.get("safety", {})
            if safety.get("risk_score", 0) > 0.3:
                report.v2_safety_flags.append({
                    "slot": sr.slot,
                    "chapter": sr.chapter_index,
                    "candidate_id": cr.get("candidate_id"),
                    "risk_score": safety.get("risk_score"),
                    "reason_codes": safety.get("reason_codes", []),
                })

            tts = cr.get("tts_readability", {})
            if tts and tts.get("composite", 1.0) < 0.5:
                report.v2_tts_issues.append({
                    "slot": sr.slot,
                    "chapter": sr.chapter_index,
                    "candidate_id": cr.get("candidate_id"),
                    "composite": tts.get("composite"),
                    "issues": tts.get("issues", []),
                })

        for dupe in v2_data.get("semantic_duplicates", []):
            if dupe.get("similarity", 0) >= 0.4:
                report.v2_dedup_flags.append({
                    "slot": sr.slot,
                    "chapter": sr.chapter_index,
                    **dupe,
                })

        arc = v2_data.get("emotion_arc")
        if arc and arc.get("status") != "PASS":
            report.v2_arc_issues.append({
                "slot": sr.slot,
                "chapter": sr.chapter_index,
                **arc,
            })

    if report.total_slots > 0:
        report.agreement_rate = round(report.agreements / report.total_slots, 4)

    report.timing_summary = {
        "total_v1_ms": round(total_v1_ms, 2),
        "total_v2_ms": round(total_v2_ms, 2),
        "avg_v1_ms": round(total_v1_ms / max(1, len(slot_results)), 2),
        "avg_v2_ms": round(total_v2_ms / max(1, len(slot_results)), 2),
    }

    return report


def write_comparison_report(
    report: PipelineComparisonReport,
    output_dir: Path,
) -> Path:
    """Write comparison report to artifacts."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "ei_v1_v2_comparison.json"
    path.write_text(report.to_json(), encoding="utf-8")

    # Write executive summary as a readable text file
    summary_path = output_dir / "ei_v1_v2_summary.txt"
    lines = [
        "EI V1 vs V2 Comparison Summary",
        "=" * 40,
        f"Plan hash: {report.plan_hash}",
        f"Persona: {report.persona_id}  Topic: {report.topic_id}",
        f"Total slots compared: {report.total_slots}",
        f"Agreements: {report.agreements} ({report.agreement_rate * 100:.1f}%)",
        f"Disagreements: {report.disagreements}",
        "",
        f"V1 total time: {report.timing_summary.get('total_v1_ms', 0):.0f}ms",
        f"V2 total time: {report.timing_summary.get('total_v2_ms', 0):.0f}ms",
        "",
    ]

    if report.v2_safety_flags:
        lines.append(f"Safety flags ({len(report.v2_safety_flags)}):")
        for flag in report.v2_safety_flags[:10]:
            lines.append(f"  Ch{flag['chapter']} {flag['slot']}: "
                         f"risk={flag['risk_score']:.2f} {flag.get('reason_codes', [])}")
        lines.append("")

    if report.v2_dedup_flags:
        lines.append(f"Duplication flags ({len(report.v2_dedup_flags)}):")
        for flag in report.v2_dedup_flags[:10]:
            lines.append(f"  Ch{flag['chapter']} {flag['slot']}: "
                         f"{flag['id_a']} <-> {flag['id_b']} sim={flag['similarity']:.3f}")
        lines.append("")

    if report.v2_tts_issues:
        lines.append(f"TTS readability issues ({len(report.v2_tts_issues)}):")
        for issue in report.v2_tts_issues[:10]:
            lines.append(f"  Ch{issue['chapter']} {issue['slot']}: "
                         f"score={issue['composite']:.2f} {issue.get('issues', [])[:2]}")
        lines.append("")

    if report.v2_arc_issues:
        lines.append(f"Emotion arc issues ({len(report.v2_arc_issues)}):")
        for issue in report.v2_arc_issues[:10]:
            lines.append(f"  Ch{issue['chapter']} {issue['slot']}: "
                         f"status={issue['status']} {issue.get('errors', [])[:2]}")
        lines.append("")

    if not any([report.v2_safety_flags, report.v2_dedup_flags,
                report.v2_tts_issues, report.v2_arc_issues]):
        lines.append("No issues flagged by V2.")

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return path
