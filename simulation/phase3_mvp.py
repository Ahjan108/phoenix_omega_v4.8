"""
Phase 3 MVP: Content-aware emotional force validation.
Four engines: volatility reality, cognitive overload, consequence authenticity, reassurance repetition.
Runs on actual chapter text (or synthetic for simulation). Heuristic only; no LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# --- Lexicons (heuristic) ---
ESCALATION_VERBS = {
    "snap", "slam", "cry", "send", "delete", "confront", "lock", "leave", "say", "hit",
    "throw", "walk", "close", "open", "turn", "push", "pull", "break", "drop", "cut",
}
SENSORY_STRESS = {
    "jaw", "breath", "throat", "chest", "heat", "silence", "stare", "shaking", "tight",
    "shoulders", "stomach", "hands", "heart", "pulse", "cold", "sweat", "tears",
}
REACTION_MARKERS = {
    "looked", "paused", "didn't reply", "walked away", "door", "seen", "silence",
    "nobody", "nothing", "didn't answer", "left", "gone", "reply", "read", "seen",
    "stared", "waited", "stopped", "froze",
}
COGNITIVE_VERBS = {
    "think", "realize", "understand", "notice", "believe", "predict", "analyze", "explain",
    "know", "feel", "wonder", "decide", "remember", "forget", "consider", "recognize",
}
BODY_WORDS = {
    "breath", "jaw", "chest", "shoulders", "stomach", "throat", "heat", "shaking", "tight",
    "hands", "body", "heart", "pulse", "cold", "sweat", "tears", "back", "neck",
}
ACTION_VERBS = {
    "send", "say", "leave", "lock", "post", "confront", "delete", "text", "call",
    "walk", "close", "open", "hit", "slam", "throw", "write", "reply",
}
REASSURANCE_PHRASES = [
    "you are not broken",
    "still here",
    "the alarm is real",
    "your nervous system",
    "you are enough",
    "it's okay",
    "you've got this",
    "trust the process",
]

# --- Thresholds ---
VOLATILE_MIN_ESCALATION = 3
VOLATILE_MIN_SENSORY = 2
VOLATILE_MIN_REACTION = 1
COGNITIVE_RATIO_WARN = 3.0
COGNITIVE_RATIO_FAIL = 5.0
REASSURANCE_WARN_SHARE = 0.4
REASSURANCE_FAIL_SHARE = 0.6
CONSEQUENCE_PARAGRAPH_WINDOW = 3  # paragraphs to look for reaction after action


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z']+\b", text.lower())


def _count_lexeme(text: str, lex: set[str]) -> int:
    tokens = _tokenize(text)
    return sum(1 for t in tokens if t in lex)


def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


# --- Engine 1: Volatility Reality Check ---
def check_volatility_strength(chapter_text: str, marked_volatile: bool) -> tuple[bool, list[str], float]:
    """If chapter marked volatile, require escalation + sensory + reaction density. Returns (passed, errors, score 0-10)."""
    errors: list[str] = []
    if not marked_volatile:
        return True, [], 10.0
    esc = _count_lexeme(chapter_text, ESCALATION_VERBS)
    sens = _count_lexeme(chapter_text, SENSORY_STRESS)
    react = _count_lexeme(chapter_text, REACTION_MARKERS)
    if esc < VOLATILE_MIN_ESCALATION:
        errors.append(f"volatile chapter: escalation verbs {esc} < {VOLATILE_MIN_ESCALATION}")
    if sens < VOLATILE_MIN_SENSORY:
        errors.append(f"volatile chapter: sensory stress words {sens} < {VOLATILE_MIN_SENSORY}")
    if react < VOLATILE_MIN_REACTION:
        errors.append(f"volatile chapter: reaction markers {react} < {VOLATILE_MIN_REACTION}")
    score = min(10.0, (esc / VOLATILE_MIN_ESCALATION + sens / VOLATILE_MIN_SENSORY + react / VOLATILE_MIN_REACTION) / 3 * 10)
    return len(errors) == 0, errors, round(score, 1)


# --- Engine 2: Cognitive Overload Detector ---
def check_cognitive_balance(chapter_text: str) -> tuple[bool, list[str], float]:
    """cognitive_count / body_count > 3 → warning, > 5 → fail. Returns (passed, errors/warnings, score 0-10)."""
    errors: list[str] = []
    cog = _count_lexeme(chapter_text, COGNITIVE_VERBS)
    body = _count_lexeme(chapter_text, BODY_WORDS)
    if body == 0:
        ratio = 10.0
    else:
        ratio = cog / body
    if ratio > COGNITIVE_RATIO_FAIL:
        errors.append(f"cognitive_overload: ratio {ratio:.1f} > {COGNITIVE_RATIO_FAIL} (cognitive/body)")
        score = 4.0
    elif ratio > COGNITIVE_RATIO_WARN:
        errors.append(f"cognitive_heavy: ratio {ratio:.1f} > {COGNITIVE_RATIO_WARN} (warning)")
        score = 6.0
    else:
        score = min(10.0, 10.0 - ratio)
    return ratio <= COGNITIVE_RATIO_FAIL, errors, round(score, 1)


# --- Engine 3: Consequence Authenticity ---
def check_consequence_authenticity(chapter_text: str) -> tuple[bool, list[str], float]:
    """If action verbs present, reaction markers should appear within paragraph window. Returns (passed, errors, score)."""
    errors: list[str] = []
    paras = _paragraphs(chapter_text)
    if not paras:
        return True, [], 7.0
    action_count = sum(_count_lexeme(p, ACTION_VERBS) for p in paras)
    if action_count == 0:
        return True, [], 7.0
    reaction_count = sum(_count_lexeme(p, REACTION_MARKERS) for p in paras)
    # Simple heuristic: if we have action, we want at least one reaction somewhere in chapter
    if action_count >= 1 and reaction_count < 1:
        errors.append("consequence_weak: action verbs present but no reaction markers in chapter")
        score = 4.0
    else:
        score = min(10.0, 5.0 + reaction_count * 2)
    return len(errors) == 0, errors, round(score, 1)


# --- Engine 4: Reassurance Repetition (across stack) ---
def check_reassurance_repetition(book_texts: list[str], phrase_counts: dict[str, int] | None = None) -> tuple[bool, list[str], float]:
    """Across stack, if a reassurance phrase appears in >40% → warning, >60% → fail. Returns (passed, errors, score)."""
    errors: list[str] = []
    n = len(book_texts)
    if n == 0:
        return True, [], 10.0
    if phrase_counts is None:
        phrase_counts = {}
        for phrase in REASSURANCE_PHRASES:
            count = sum(1 for t in book_texts if phrase in t.lower())
            phrase_counts[phrase] = count
    worst_share = 0.0
    for phrase, count in phrase_counts.items():
        share = count / n
        if share >= REASSURANCE_FAIL_SHARE:
            errors.append(f"reassurance_repetition: '{phrase}' in {count}/{n} books (>{REASSURANCE_FAIL_SHARE:.0%})")
            worst_share = max(worst_share, share)
        elif share >= REASSURANCE_WARN_SHARE:
            errors.append(f"reassurance_frequent: '{phrase}' in {count}/{n} books (warning)")
            worst_share = max(worst_share, share)
    score = 10.0 - (worst_share * 10) if worst_share else 10.0
    passed = not any(e.startswith("reassurance_repetition:") for e in errors)
    return passed, errors, round(max(0, score), 1)


# --- Full book validation ---
@dataclass
class ChapterInput:
    text: str
    volatile: bool = False
    interrupt: bool = False


def validate_book_phase3(
    chapters: list[ChapterInput],
    book_id: str = "",
) -> dict[str, Any]:
    """
    Run all 4 engines on one book. Returns phase3_passed, phase3_errors, phase3_scores.
    """
    errors: list[str] = []
    warnings: list[str] = []
    scores: dict[str, float] = {}
    full_text = " ".join(c.text for c in chapters)
    volatile_chapters = [c.text for c in chapters if c.volatile]

    for i, ch in enumerate(chapters):
        v_ok, v_err, v_score = check_volatility_strength(ch.text, ch.volatile)
        if not v_ok:
            errors.extend([f"ch{i+1}: {e}" for e in v_err])
        c_ok, c_err, c_score = check_cognitive_balance(ch.text)
        if not c_ok:
            errors.extend([f"ch{i+1}: {e}" for e in c_err])
        elif c_err:
            warnings.extend([f"ch{i+1}: {e}" for e in c_err])
        cons_ok, cons_err, cons_score = check_consequence_authenticity(ch.text)
        if not cons_ok:
            errors.extend([f"ch{i+1}: {e}" for e in cons_err])
    scores["volatility_strength"] = min(
        (check_volatility_strength(t, True)[2] for t in volatile_chapters),
        default=10.0,
    )
    scores["embodiment_balance"] = sum(check_cognitive_balance(c.text)[2] for c in chapters) / len(chapters) if chapters else 7.0
    scores["consequence_authenticity"] = sum(check_consequence_authenticity(c.text)[2] for c in chapters) / len(chapters) if chapters else 7.0
    # Repetition is per-stack; caller adds stack-level check
    scores["reassurance_repetition"] = 10.0
    overall = sum(scores.values()) / len(scores) if scores else 0
    scores["overall"] = round(overall, 1)
    return {
        "phase3_passed": len(errors) == 0,
        "phase3_errors": errors,
        "phase3_warnings": warnings,
        "phase3_scores": scores,
    }


def generate_synthetic_chapters(
    num_chapters: int,
    tier: str,
    seed: int,
    force_flat: bool = False,
) -> list[ChapterInput]:
    """
    Generate synthetic chapter text for simulation. If force_flat=False, ~80% get dense (pass) text.
    """
    import random
    rng = random.Random(seed)
    chapters: list[ChapterInput] = []
    # 1 volatile chapter for narrative tiers
    n = max(1, num_chapters)
    volatile_idx = rng.randint(0, n - 1) if n and tier != "E" else -1
    for i in range(n):
        is_volatile = i == volatile_idx and tier in ("S", "A", "B", "C")
        if force_flat:
            # Flat: cognitive-heavy, few body/sensory
            text = (
                "You think about what happened. You realize that you need to understand "
                "your pattern. You notice how often you believe it will be different. "
                "You analyze the situation and explain it to yourself. You wonder what "
                "would happen if you decided to remember instead of forget."
            )
        else:
            # Dense: escalation + sensory + reaction
            text = (
                "Your jaw tightens. You send the text and wait. Your chest is tight. "
                "Nobody replies. The silence stretches. You slam the door. Your breath "
                "is shallow. They looked at you and walked away. Your throat closes. "
                "You say it anyway. The door shuts. Your hands are shaking."
            )
        chapters.append(ChapterInput(text=text, volatile=is_volatile, interrupt=(is_volatile and i == num_chapters - 1)))
    return chapters


def run_phase3_on_stack(
    stack: list[list[ChapterInput]],
    book_ids: list[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Run Phase 3 on a stack of books. Per-book validation + stack-wide reassurance check.
    stack[i] = list of ChapterInput for book i.
    """
    book_ids = book_ids or [f"book_{i}" for i in range(len(stack))]
    results: list[dict[str, Any]] = []
    all_texts: list[str] = []
    for i, chapters in enumerate(stack):
        out = validate_book_phase3(chapters, book_ids[i] if i < len(book_ids) else "")
        out["request_id"] = book_ids[i]
        results.append(out)
        all_texts.append(" ".join(c.text for c in chapters))
    rep_ok, rep_err, rep_score = check_reassurance_repetition(all_texts)
    for r in results:
        r["phase3_scores"]["reassurance_repetition"] = rep_score
        r["phase3_scores"]["overall"] = round(
            (r["phase3_scores"]["volatility_strength"] + r["phase3_scores"]["embodiment_balance"]
             + r["phase3_scores"]["consequence_authenticity"] + rep_score) / 4, 1,
        )
        if not rep_ok:
            r["phase3_passed"] = False
            r["phase3_errors"] = r.get("phase3_errors", []) + rep_err
    summary = {
        "phase3_books_passed": sum(1 for r in results if r.get("phase3_passed")),
        "phase3_books_failed": sum(1 for r in results if not r.get("phase3_passed")),
        "reassurance_stack_ok": rep_ok,
    }
    return results, summary


def run_phase3_on_results(results: list[dict[str, Any]], stack_size: int = 20, flat_fraction: float = 0.12) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Run Phase 3 on Phase 1/2 results. Generates synthetic chapter text per book (from request_id + chapters + tier),
    runs volatility/cognitive/consequence per book, then reassurance repetition on stacks of stack_size.
    flat_fraction: fraction of books given flat (cognitive-heavy) text so Phase 3 can fail them (default 12%).
    """
    for r in results:
        if not r.get("passed"):
            r["phase3_passed"] = False
            r["phase3_errors"] = ["phase1/2 failed"]
            r["phase3_scores"] = {}
            r["phase3_skipped"] = True
            continue
        chapters = r.get("chapters", 1)
        tier = r.get("tier", "B")
        seed = hash(r.get("request_id", "")) % (2**31)
        force_flat = (seed % 100) / 100.0 < flat_fraction
        ch_list = generate_synthetic_chapters(chapters, tier, seed, force_flat=force_flat)
        out = validate_book_phase3(ch_list, r.get("request_id", ""))
        r["phase3_passed"] = out["phase3_passed"]
        r["phase3_errors"] = out.get("phase3_errors", [])
        r["phase3_warnings"] = out.get("phase3_warnings", [])
        r["phase3_scores"] = out.get("phase3_scores", {})
        r["phase3_skipped"] = False
        r["_phase3_full_text"] = " ".join(c.text for c in ch_list)
    # Stack-wise reassurance
    n = len([r for r in results if not r.get("phase3_skipped") and r.get("_phase3_full_text")])
    for start in range(0, len(results) - stack_size + 1, stack_size):
        stack_results = results[start : start + stack_size]
        texts = [r.get("_phase3_full_text", "") for r in stack_results if r.get("_phase3_full_text")]
        if len(texts) < 2:
            continue
        rep_ok, rep_err, _ = check_reassurance_repetition(texts)
        if not rep_ok:
            for r in stack_results:
                r["phase3_passed"] = False
                r["phase3_errors"] = r.get("phase3_errors", []) + rep_err
    for r in results:
        r.pop("_phase3_full_text", None)
    summary = {
        "phase3_passed": sum(1 for r in results if r.get("phase3_passed")),
        "phase3_failed": sum(1 for r in results if not r.get("phase3_skipped") and not r.get("phase3_passed")),
        "phase3_skipped": sum(1 for r in results if r.get("phase3_skipped")),
    }
    return results, summary
