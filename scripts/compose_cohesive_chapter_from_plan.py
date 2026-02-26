#!/usr/bin/env python3
"""
Compose one cohesive chapter from an existing compiled plan.

Uses actual plan-selected slot prose, then applies a thesis-threaded assembly pass:
hook -> scene -> bridge -> teaching -> bridge -> story -> bridge -> exercise -> integration.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow
from phoenix_v4.rendering.book_renderer import clean_for_delivery
from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def _de_scaffold(text: str) -> str:
    # Reuse delivery cleanup so metadata/---/{vars} are removed consistently.
    return clean_for_delivery(text or "")


def _trim_reflection(reflection: str, max_sentences: int = 7) -> str:
    sents = _sentences(reflection)
    if not sents:
        return ""
    keep_keywords = ("choice", "cost", "regret", "perfect", "frozen", "adjust", "path", "mechanism")
    chosen: list[str] = []
    for s in sents:
        low = s.lower()
        if any(k in low for k in keep_keywords):
            chosen.append(s)
        if len(chosen) >= max_sentences:
            break
    if len(chosen) < 4:
        chosen = sents[:max_sentences]
    joined = " ".join(chosen)
    joined = re.sub(r"\bI have noticed that\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat I have come to understand is that\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat I have come to think about is\s+", "", joined, flags=re.I)
    return joined.strip()


def _derive_thesis(reflection: str) -> str:
    sents = _sentences(reflection)
    for s in sents:
        low = s.lower()
        if "perfect choices do not exist" in low:
            return "The point is that perfection is not available, but movement is."
        if "regret" in low and "choice" in low:
            return "The point is that anxiety predicts regret so loudly that it blocks useful decisions."
        if "mechanism" in low and "choice" in low:
            return "The point is that the mechanism treats every decision like a permanent threat."
    return "The point is that you can make a workable decision without solving every future outcome."


def _default_exercise(reflection: str) -> str:
    return (
        "Try this now.\n"
        "1. Exhale once, slowly.\n"
        "2. Name the predicted cost in one sentence.\n"
        "3. Choose the smallest next move and do it for three minutes.\n"
        "This retrains your system to act with uncertainty instead of waiting for certainty."
    )


def compose_chapter(plan: dict, chapter_index: int) -> str:
    rr = resolve_prose_for_plan(plan)
    slots = plan.get("chapter_slot_sequence", [])
    atom_ids = plan.get("atom_ids", [])
    if chapter_index < 0 or chapter_index >= len(slots):
        raise ValueError(f"chapter_index {chapter_index} out of range 0..{len(slots)-1}")

    start = sum(len(ch) for ch in slots[:chapter_index])
    end = start + len(slots[chapter_index])
    chapter_slots = slots[chapter_index]
    chapter_atoms = atom_ids[start:end]

    slot_text: dict[str, str] = {}
    for st, aid in zip(chapter_slots, chapter_atoms):
        slot_text[st] = _de_scaffold(rr.prose_map.get(aid, ""))

    hook = slot_text.get("HOOK", "")
    scene = slot_text.get("SCENE", "")
    story = slot_text.get("STORY", "")
    reflection_raw = slot_text.get("REFLECTION", "")
    reflection = _trim_reflection(reflection_raw)
    integration = slot_text.get("INTEGRATION", "")
    exercise = slot_text.get("EXERCISE", "") or _default_exercise(reflection_raw)
    thesis = _derive_thesis(reflection_raw)

    parts = [
        hook,
        scene,
        "That moment matters because it reveals the pattern before the label.",
        f"Principle: {thesis}",
        reflection,
        "So this is not just your private glitch. It is a repeatable mechanism, which means it can be worked with.",
        story,
        "In practice, we turn that understanding into a body-level action so the next decision is smaller and safer.",
        exercise,
    ]
    if integration:
        parts.extend(
            [
                "What this means going forward is simple.",
                integration,
            ]
        )
    return "\n\n".join([p for p in parts if p]).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose one cohesive chapter from a compiled plan.")
    parser.add_argument("--plan", required=True, help="Path to compiled plan JSON")
    parser.add_argument("--chapter-index", type=int, default=0, help="0-based chapter index")
    parser.add_argument("--out", required=True, help="Output .txt path")
    parser.add_argument("--report", required=True, help="Output .json gate report path")
    args = parser.parse_args()

    plan_path = Path(args.plan)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    chapter = compose_chapter(plan, args.chapter_index)
    flow = evaluate_chapter_flow(chapter)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(chapter, encoding="utf-8")

    report = {
        "status": flow.status,
        "score": flow.score,
        "errors": flow.errors,
        "warnings": flow.warnings,
        "metrics": flow.metrics,
        "plan": str(plan_path),
        "chapter_index": args.chapter_index,
        "output_path": str(out_path),
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if flow.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
