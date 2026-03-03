#!/usr/bin/env python3
"""
Build one thesis-threaded proof chapter and run the chapter flow gate.

Usage:
  PYTHONPATH=. python3 scripts/build_proof_chapter.py \
    --out artifacts/proof_chapter/chapter_01.txt \
    --report artifacts/proof_chapter/chapter_01_report.json \
    --seed demo-01
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow


def _pick(options: list[str], key: str) -> str:
    if not options:
        return ""
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(options)
    return options[idx]


def build_chapter(seed: str) -> str:
    thesis = "depletion looks like laziness from the outside but feels like static from the inside"

    hooks = [
        "The task is small. The resistance is not.",
        "You are not avoiding the work. You are bracing for the feeling before the work.",
        "The assignment is open on your screen. Your hand is still on the trackpad.",
    ]
    scenes = [
        (
            "Third period starts in eight minutes. Your backpack is open on the chair, "
            "your worksheet is half done, and your chest feels tight for no clear reason. "
            "You read the first prompt again. You know how to do it. You still cannot start."
        ),
        (
            "The group project slide is on the board. Your name is next to the intro section. "
            "You practiced last night. Now your jaw is locked and your hands are cold. "
            "You are not confused. You are overloaded."
        ),
    ]
    teach_openers = [
        "Principle: your nervous system does not measure effort by difficulty; it measures threat by cost.",
        "Principle: when anxiety predicts social loss, your body spends energy before the task begins.",
    ]
    bridge_1 = [
        "That moment matters, because it tells us where the spiral starts.",
        "That pause is not a character flaw. It is data.",
    ]
    bridge_2 = [
        "Which means the right question is not, \"Why am I lazy?\" The right question is, \"What cost am I predicting?\"",
        "So when you freeze in a simple task, do not diagnose motivation first. Diagnose perceived risk.",
    ]
    stories = [
        (
            "Jaden stared at a one-page reading response for forty minutes. "
            "He kept opening a new tab, then another, then another. "
            "His brain said the same line on loop: if this sounds dumb, everyone will know. "
            "When he finally wrote two sentences, the teacher marked them clear and thoughtful. "
            "No one laughed. No one called him out. The predicted disaster did not happen, "
            "but his body had already paid for it."
        ),
        (
            "Maya would rewrite the first sentence of an assignment until the period ended. "
            "At home she called it procrastination. In session she named the real fear: "
            "if I start and it is bad, I prove what I worry is true. "
            "Once she could name that fear, she could work with it. "
            "She wrote a rough first line on purpose, kept it, and finished the draft."
        ),
    ]
    bridge_3 = [
        "This is why scene and story match: both are the same mechanism wearing different clothes.",
        "For example, your freeze and their freeze are one pattern with different details.",
    ]
    exercises = [
        (
            "In practice, try the sixty-second cost check.\n"
            "1. Exhale fully once.\n"
            "2. Write one sentence: \"My brain predicts this will cost me _____.\"\n"
            "3. Write one sentence: \"The smallest safe start is _____.\"\n"
            "4. Do only that start for three minutes.\n"
            "You are training your system to separate predicted pain from actual task size."
        ),
        (
            "In practice, run a body reset before the first sentence.\n"
            "1. Exhale longer than you inhale for three breaths.\n"
            "2. Unclench your jaw and drop your shoulders.\n"
            "3. Say out loud: \"I can do a rough start without solving the whole thing.\"\n"
            "4. Write one imperfect line and keep moving.\n"
            "This shifts you from defense mode to work mode."
        ),
    ]
    bridge_4 = [
        "Here is the point: you do not win by forcing confidence. You win by lowering entry cost.",
        "What this means in real life is simple: reduce cost first, then ask for performance.",
    ]
    integrations = [
        (
            "You are not behind because you are weak. "
            "You are tired of paying full emotional price for every small task. "
            "Today you stop paying full price. "
            "Name the cost. Lower the first step. Practice the smaller start. "
            "Momentum is not hype. Momentum is repeated safe entries."
        ),
        (
            "This is not about becoming fearless. "
            "It is about becoming accurate. "
            "Your alarm can fire and you can still choose a smaller opening move. "
            "If the spiral says, do not start, answer with one line and one breath. "
            "That is enough to change the chapter of your day."
        ),
    ]

    parts = [
        _pick(hooks, f"{seed}:hook"),
        _pick(scenes, f"{seed}:scene"),
        _pick(bridge_1, f"{seed}:bridge1"),
        _pick(teach_openers, f"{seed}:teach"),
        (
            "The point is not to feel brave before beginning. "
            f"The point is to see that {thesis}. "
            "Once you name the predicted cost, your brain has a target it can test instead of a fog it can fear."
        ),
        _pick(bridge_2, f"{seed}:bridge2"),
        _pick(stories, f"{seed}:story"),
        _pick(bridge_3, f"{seed}:bridge3"),
        _pick(exercises, f"{seed}:exercise"),
        _pick(bridge_4, f"{seed}:bridge4"),
        _pick(integrations, f"{seed}:integration"),
    ]
    return "\n\n".join(parts).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one proof chapter and gate it.")
    parser.add_argument("--out", required=True, help="Output .txt path for chapter")
    parser.add_argument("--report", required=True, help="Output .json path for gate report")
    parser.add_argument("--seed", default="proof-01", help="Deterministic selection seed")
    args = parser.parse_args()

    chapter = build_chapter(args.seed)
    result = evaluate_chapter_flow(chapter)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(chapter, encoding="utf-8")

    report = {
        "status": result.status,
        "score": result.score,
        "errors": result.errors,
        "warnings": result.warnings,
        "metrics": result.metrics,
        "seed": args.seed,
        "output_path": str(out_path),
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
