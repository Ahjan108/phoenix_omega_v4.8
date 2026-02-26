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


def _polish_scene(scene: str) -> str:
    s = (scene or "").strip()
    if not s:
        return s
    # Fix common fallback-template collision in outdoor scenes.
    s = s.replace("The gray light through the window afternoon", "The afternoon light is flat and gray")
    s = s.replace("through the window afternoon", "afternoon")
    s = s.replace("through the window", "")
    s = s.replace(
        "The afternoon light is flat and gray stretches long and empty ahead of you.",
        "The afternoon light is flat and gray. The road ahead feels long and empty.",
    )
    s = re.sub(
        r"The\s+[A-Za-z ]*afternoon stretches long and empty ahead of you\.",
        "The afternoon light is flat and gray. The road ahead feels long and empty.",
        s,
    )
    # Clean double spaces created by removals.
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


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


def _warm_reflection(reflection_raw: str) -> str:
    low = (reflection_raw or "").lower()
    if "perfect choice" in low or ("regret" in low and "choice" in low):
        return (
            "You are not broken for feeling this. Your brain is trying to protect you from future pain, "
            "but it is using impossible standards. Useful decisions are not perfect decisions. "
            "Useful decisions are adjustable decisions."
        )
    return (
        "You are not failing this moment. You are in a normal human conflict between uncertainty and control. "
        "The move is not to erase uncertainty. The move is to act inside it."
    )


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


def _mechanism_rewrite(reflection_raw: str, thesis: str) -> str:
    low = (reflection_raw or "").lower()
    if "regret" in low and "choice" in low:
        return (
            "Here is what is actually happening: anxiety predicts regret so loudly that it drowns out your ability "
            "to make a useful decision. The mechanism is simple and brutal. The moment you choose one thing, your "
            "brain starts mourning everything you did not choose. It tries to find a perfect option with zero loss, "
            "but that option does not exist. Every path closes other paths. So the system freezes you, or lets you "
            "choose and then punishes you for choosing."
        )
    return (
        "Here is what is actually happening: " + thesis.replace("The point is that ", "") + " "
        "When the alarm runs the decision, your brain treats uncertainty like danger and asks for impossible certainty. "
        "That is why small choices feel heavy."
    )


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
    scene = _polish_scene(slot_text.get("SCENE", ""))
    story = slot_text.get("STORY", "")
    reflection_raw = slot_text.get("REFLECTION", "")
    reflection = _warm_reflection(reflection_raw)
    integration = slot_text.get("INTEGRATION", "")
    exercise = slot_text.get("EXERCISE", "") or _default_exercise(reflection_raw)
    thesis = _derive_thesis(reflection_raw)
    mechanism = _mechanism_rewrite(reflection_raw, thesis)

    # Avoid stitched immersive openings: prefer one coherent scene.
    opening = scene or hook

    parts = [
        opening,
        "That moment matters because it reveals the pattern before you have language for it.",
        mechanism,
        reflection,
        "So this is not just your private glitch. It is a repeatable mechanism, which means it can be worked with.",
        story,
        "So here is what you can actually do with this. Right now. Not someday, now.",
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
