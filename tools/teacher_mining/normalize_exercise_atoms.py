#!/usr/bin/env python3
"""
Normalize EXERCISE atoms: exercise_family, length (90–280 words), clear steps, time marker, closure.
Deterministic; no LLM. Run after mining, before approval.
Authority: Teacher Mode structural design — anti-fragment, platform diversity.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

EXERCISE_FAMILIES = ["E1_BREATH", "E2_REFLECTION", "E3_MICRO_EXPERIMENT", "E4_BODY_SCAN", "E5_REFRAME"]
MIN_WORDS = 90
MAX_WORDS = 280

# Instruction / time / closure detection
ACTION_VERBS = re.compile(
    r"\b(sit|breathe|notice|feel|place|close|allow|observe|focus|rest|pause|try|practice)\b",
    re.I,
)
TIME_MARKERS = re.compile(
    r"\b(minute|minutes|second|breath|breaths|moment|while|when you're ready)\b",
    re.I,
)
CLOSURE_PHRASES = re.compile(
    r"\b(when you finish|when you're done|gently open|notice what (changed|shifted)|take a moment)\b",
    re.I,
)


def _sha_int(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16)

EXERCISE_INTROS = [
    "Let's try something.",
    "Here's a practice.",
    "This is going to feel simple.",
    "Stay with me here.",
    "It might feel strange at first.",
]
CLOSING_LINES = [
    "When you finish, notice what shifted. Even slightly.",
    "Take a moment before moving on.",
    "When you're done, allow the practice to settle.",
    "Gently return when you're ready.",
]


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _save_yaml(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", (text or "").strip()) if w])


def _exercise_family(atom_id: str) -> str:
    return EXERCISE_FAMILIES[_sha_int(atom_id) % len(EXERCISE_FAMILIES)]


def _has_time_marker_strict(s: str) -> bool:
    return bool(re.search(r"\b(\d+\s*(seconds?|minutes?)|one minute|two minutes|five minutes)\b", s.lower()))


def _has_step_language(s: str) -> bool:
    t = s.lower()
    step_markers = ["step", "first", "second", "third", "now", "then", "next"]
    return any(m in t for m in step_markers)


def _ensure_min_length(body: str, min_words: int = MIN_WORDS) -> str:
    if _word_count(body) >= min_words:
        return body.strip()
    return (body.strip() + "\n\n" + "Try this gently for a few minutes, and notice what changes even slightly.").strip()


def _ensure_structure(body: str) -> str:
    """Ensure basic exercise rhythm: setup -> instruction -> close."""
    parts = [p.strip() for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
    if len(parts) >= 2 and (_has_step_language(body) or _has_time_marker_strict(body)):
        return body.strip()
    setup = "Take a moment to get comfortable."
    instr = body.strip()
    close = "When you finish, pause and notice what your body is doing now."
    return f"{setup}\n\n{instr}\n\n{close}".strip()


def _has_clear_instruction(body: str) -> bool:
    return bool(ACTION_VERBS.search(body))


def _has_time_marker(body: str) -> bool:
    return bool(TIME_MARKERS.search(body))


def _has_closure(body: str) -> bool:
    return bool(CLOSURE_PHRASES.search(body))


def _inject_intro(body: str, atom_id: str) -> str:
    h = int(hashlib.sha256(atom_id.encode()).hexdigest(), 16) % len(EXERCISE_INTROS)
    return EXERCISE_INTROS[h] + " " + body.lstrip()


def _inject_time(body: str) -> str:
    return body.rstrip() + "\n\nGive it at least a few breaths—or two to three minutes if you have them."


def _inject_closure(body: str, atom_id: str) -> str:
    h = int(hashlib.sha256((atom_id + "close").encode()).hexdigest(), 16) % len(CLOSING_LINES)
    return body.rstrip() + "\n\n" + CLOSING_LINES[h]


def _expand_exercise_to_min(body: str, min_words: int) -> str:
    wc = _word_count(body)
    if wc >= min_words:
        return body
    add = " Set aside a few minutes. Sit comfortably. When you're ready, gently return your attention to the room."
    return body.rstrip() + add


def _compress_to_max(body: str, max_words: int) -> str:
    words = body.split()
    if len(words) <= max_words:
        return body
    truncated = " ".join(words[: max_words])
    last_period = truncated.rfind(". ")
    if last_period > max_words // 2:
        return truncated[: last_period + 1]
    return truncated + "."


def _inject_teacher_context(body: str, teacher_id: str, tags: list) -> str:
    concept = "awareness"
    for tag in tags or []:
        if isinstance(tag, str) and tag.startswith("core:"):
            concept = tag.replace("core:", "").replace("_", " ")
            break
    prefix = f"This practice comes from the emphasis on {concept} in this tradition. "
    return prefix + body.lstrip()


def normalize_exercise(atom: dict, add_framing: bool = True) -> dict:
    """Return normalized exercise atom: cohesion, exercise_family, style IDs. Optional framing."""
    atom_id = atom.get("atom_id") or atom.get("id") or ""
    if not atom_id:
        raise ValueError("Missing atom_id")
    body = (atom.get("body") or "").strip()
    if not body:
        raise ValueError(f"{atom_id}: empty body")
    tags = atom.get("tags") or []
    teacher_id = (atom.get("teacher") or {}).get("teacher_id", "")

    body = _ensure_min_length(body, min_words=MIN_WORDS)
    body = _ensure_structure(body)
    if _word_count(body) > MAX_WORDS:
        body = _compress_to_max(body, MAX_WORDS)

    out = dict(atom)
    out["exercise_family"] = _exercise_family(atom_id)
    out.setdefault("exercise_intro_style_id", f"ei_{_sha_int(atom_id + ':intro') % 7}")
    out.setdefault("exercise_outro_style_id", f"eo_{_sha_int(atom_id + ':outro') % 7}")

    if not _has_clear_instruction(body):
        body = "Sit comfortably and bring your attention to your breath. " + body
    if not _has_time_marker(body):
        body = _inject_time(body)
    if not _has_closure(body):
        body = _inject_closure(body, atom_id)
    if teacher_id and add_framing:
        body = _inject_teacher_context(body, teacher_id, tags)
        body = _inject_intro(body, atom_id)

    out["body"] = body
    return out


def run_normalization(exercise_dir: Path, out_dir: Path, add_framing: bool = True) -> int:
    count = 0
    for path in sorted(exercise_dir.glob("*.yaml")):
        atom = _load_yaml(path)
        if not atom or not atom.get("body") or not (atom.get("atom_id") or atom.get("id")):
            continue
        try:
            normalized = normalize_exercise(atom, add_framing=add_framing)
        except ValueError:
            continue
        out_path = out_dir / path.name
        _save_yaml(out_path, normalized)
        count += 1
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize EXERCISE atoms (family, cohesion, style IDs)")
    ap.add_argument("--in-dir", default=None, help="Directory containing EXERCISE YAML atoms")
    ap.add_argument("--out-dir", default=None, help="Where to write normalized EXERCISE YAML atoms")
    ap.add_argument("--teacher", default=None, help="Teacher id (sets in-dir/out-dir to approved_atoms/EXERCISE)")
    ap.add_argument("--exercises", default=None, help="Path to EXERCISE dir (alternative to --in-dir)")
    ap.add_argument("--out", default=None, help="Output dir (alternative to --out-dir)")
    ap.add_argument("--no-framing", action="store_true", help="Do not add teacher context or intro")
    ap.add_argument("--repo", default=None, help="Repo root")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT
    if args.in_dir:
        exercise_dir = Path(args.in_dir)
        out_dir = Path(args.out_dir) if args.out_dir else exercise_dir
    elif args.teacher:
        banks = repo / "SOURCE_OF_TRUTH" / "teacher_banks" / args.teacher.strip().lower()
        exercise_dir = Path(args.exercises) if args.exercises else banks / "approved_atoms" / "EXERCISE"
        out_dir = Path(args.out) if args.out else Path(args.out_dir) if args.out_dir else exercise_dir
    else:
        exercise_dir = Path(args.exercises) if args.exercises else None
        out_dir = Path(args.out) if args.out else (Path(args.out_dir) if args.out_dir else None)
        if not exercise_dir or not out_dir:
            print("Error: need --in-dir and --out-dir, or --teacher", file=sys.stderr)
            return 1

    if not exercise_dir.exists():
        print(f"EXERCISE dir not found: {exercise_dir}", file=sys.stderr)
        return 1

    n = run_normalization(exercise_dir, out_dir, add_framing=not args.no_framing)
    print(f"Normalized {n} EXERCISE atoms -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
