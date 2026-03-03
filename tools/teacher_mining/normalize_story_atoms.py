#!/usr/bin/env python3
"""
Normalize STORY atoms: structure_family, length (120–450 words), tension, teacher anchor.
Deterministic; no LLM. Run after mining/expansion, before approval.
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

STRUCTURE_FAMILIES = ["NARRATIVE", "CASE_STUDY", "PARABLE", "DIALOGUE"]
MIN_WORDS = 120
MAX_WORDS = 450

# Friction/cost detection (must match mine_kb_to_atoms / expand_story_atoms)
COST_KEYWORDS = {
    "lost", "rejected", "humiliated", "failed", "collapse",
    "isolated", "alone", "exposed", "broke", "exhausted",
    "abandoned", "betrayed", "toll",
}
FRICTION_PHRASES = re.compile(
    r"\b(struggled|avoided|resisted|overwhelmed|anxious|ashamed|conflicted|tension|cost)\b",
    re.I,
)

AUTHOR_INTROS = [
    "In the tradition this teacher speaks from, a story like this one often points to something we'd rather not see.",
    "What follows is a pattern many of us recognize.",
    "Consider how this lands when we're honest with ourselves.",
    "This kind of moment shows up again and again.",
]
AUTHOR_OUTROS = [
    "When they practiced this, something shifted. Not overnight. But enough.",
    "The teaching here is not the drama—it's what becomes possible when we stop feeding the pattern.",
    "That's the move: not to fix it, but to see it clearly.",
    "The work is to stay with what's already there, without adding a story.",
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


def _sha_int(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16)


def _structure_family(atom_id: str) -> str:
    return STRUCTURE_FAMILIES[_sha_int(atom_id) % len(STRUCTURE_FAMILIES)]


def _ensure_min_length(body: str, min_words: int = MIN_WORDS) -> str:
    """One-line cohesion patch if too short. Not a template."""
    if _word_count(body) >= min_words:
        return body
    return body.strip() + "\n\n" + "Notice what the moment reveals about the pattern, not just the event."


def _ensure_paragraphs(body: str) -> str:
    """Ensure at least 3 paragraphs (audio-friendly rhythm)."""
    parts = [p.strip() for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
    if len(parts) >= 3:
        return body.strip()
    sentences = re.split(r"(?<=[.!?])\s+", body.strip())
    if len(sentences) >= 6:
        p1 = " ".join(sentences[:2]).strip()
        p2 = " ".join(sentences[2:4]).strip()
        p3 = " ".join(sentences[4:]).strip()
        return f"{p1}\n\n{p2}\n\n{p3}".strip()
    mid = max(1, len(sentences) // 2)
    p1 = " ".join(sentences[:mid]).strip()
    p2 = " ".join(sentences[mid:]).strip()
    p3 = "Stay with what you felt there—this is where the teaching becomes real."
    return f"{p1}\n\n{p2}\n\n{p3}".strip()


def _has_friction(body: str) -> bool:
    t = body.lower()
    if any(k in t for k in COST_KEYWORDS):
        return True
    return bool(FRICTION_PHRASES.search(body))


def _has_teacher_anchor(body: str, tags: list) -> bool:
    if not tags:
        return False
    for tag in tags:
        if isinstance(tag, str) and tag.startswith("core:"):
            return True
    return False


def _inject_tension_sentence(body: str) -> str:
    return body.rstrip() + "\n\nOver time, this took a toll that could no longer be ignored."


def _inject_teacher_anchor(body: str, tags: list, fallback_phrase: str = "awareness") -> str:
    concept = fallback_phrase
    for tag in tags or []:
        if isinstance(tag, str) and tag.startswith("core:"):
            concept = tag.replace("core:", "").replace("_", " ")
            break
    return body.rstrip() + f"\n\nIn this teacher's language, that pattern is often called {concept}."


def _expand_to_min(body: str, min_words: int) -> str:
    """Add one deterministic sentence until word count >= min_words (cap at 2 sentences)."""
    wc = _word_count(body)
    if wc >= min_words:
        return body
    add = " This pattern repeated. Each time the cost became a little more visible."
    return body.rstrip() + add


def _compress_to_max(body: str, max_words: int) -> str:
    """Truncate at sentence boundary to max_words."""
    words = body.split()
    if len(words) <= max_words:
        return body
    truncated = " ".join(words[: max_words])
    last_period = truncated.rfind(". ")
    if last_period > max_words // 2:
        return truncated[: last_period + 1]
    return truncated + "."


def _author_intro(atom_id: str) -> str:
    h = int(hashlib.sha256(atom_id.encode()).hexdigest(), 16) % len(AUTHOR_INTROS)
    return AUTHOR_INTROS[h]


def _author_outro(atom_id: str) -> str:
    h = int(hashlib.sha256((atom_id + "outro").encode()).hexdigest(), 16) % len(AUTHOR_OUTROS)
    return AUTHOR_OUTROS[h]


def normalize_story(atom: dict, add_framing: bool = True) -> dict:
    """
    Return normalized atom: cohesion (min length, 3 paragraphs), structure_family, style IDs.
    Optional: tension/teacher anchor injection and literal intro/outro when add_framing=True.
    """
    atom_id = atom.get("atom_id") or atom.get("id") or ""
    if not atom_id:
        raise ValueError("Missing atom_id")
    body = (atom.get("body") or "").strip()
    if not body:
        raise ValueError(f"{atom_id}: empty body")
    tags = atom.get("tags") or []

    # 1. Cohesion guards (deterministic, minimal)
    body = _ensure_min_length(body, min_words=MIN_WORDS)
    body = _ensure_paragraphs(body)

    # 2. Length cap
    if _word_count(body) > MAX_WORDS:
        body = _compress_to_max(body, MAX_WORDS)

    # 3. Structure family
    family = _structure_family(atom_id)
    out = dict(atom)
    out["structure_family"] = family

    # 4. Style IDs only (for CI spam-signature control; actual text from authoring layer)
    out.setdefault("author_intro_style_id", f"ti_{_sha_int(atom_id + ':intro') % 7}")
    out.setdefault("author_outro_style_id", f"to_{_sha_int(atom_id + ':outro') % 7}")

    # 5. Optional tension + teacher anchor + literal intro/outro
    if add_framing:
        if not _has_friction(body):
            body = _inject_tension_sentence(body)
        if not _has_teacher_anchor(body, tags):
            body = _inject_teacher_anchor(body, tags)
        intro = _author_intro(atom_id)
        outro = _author_outro(atom_id)
        body = intro + "\n\n" + body + "\n\n" + outro

    out["body"] = body
    out["persona_overlay"] = True
    out["topic_overlay"] = True
    out["teacher_framed"] = True
    return out


def run_normalization(story_dir: Path, out_dir: Path, add_framing: bool = True) -> int:
    """Normalize all STORY YAMLs in story_dir; write to out_dir. Returns count."""
    count = 0
    for path in sorted(story_dir.glob("*.yaml")):
        atom = _load_yaml(path)
        if not atom or not atom.get("body") or not (atom.get("atom_id") or atom.get("id")):
            continue
        try:
            normalized = normalize_story(atom, add_framing=add_framing)
        except ValueError:
            continue
        out_path = out_dir / path.name
        _save_yaml(out_path, normalized)
        count += 1
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize STORY atoms (structure_family, cohesion, style IDs)")
    ap.add_argument("--in-dir", default=None, help="Directory containing STORY YAML atoms")
    ap.add_argument("--out-dir", default=None, help="Where to write normalized STORY YAML atoms")
    ap.add_argument("--teacher", default=None, help="Teacher id (sets in-dir/out-dir to approved_atoms/STORY)")
    ap.add_argument("--stories", default=None, help="Path to STORY dir (alternative to --in-dir)")
    ap.add_argument("--out", default=None, help="Output dir (alternative to --out-dir)")
    ap.add_argument("--no-framing", action="store_true", help="Do not add literal author intro/outro or tension/anchor")
    ap.add_argument("--repo", default=None, help="Repo root")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT
    if args.in_dir:
        story_dir = Path(args.in_dir)
        out_dir = Path(args.out_dir) if args.out_dir else story_dir
    elif args.teacher:
        banks = repo / "SOURCE_OF_TRUTH" / "teacher_banks" / args.teacher.strip().lower()
        story_dir = Path(args.stories) if args.stories else banks / "approved_atoms" / "STORY"
        out_dir = Path(args.out) if args.out else Path(args.out_dir) if args.out_dir else story_dir
    else:
        story_dir = Path(args.stories) if args.stories else None
        out_dir = Path(args.out) if args.out else (Path(args.out_dir) if args.out_dir else None)
        if not story_dir or not out_dir:
            print("Error: need --in-dir and --out-dir, or --teacher", file=sys.stderr)
            return 1

    if not story_dir.exists():
        print(f"STORY dir not found: {story_dir}", file=sys.stderr)
        return 1

    n = run_normalization(story_dir, out_dir, add_framing=not args.no_framing)
    print(f"Normalized {n} STORY atoms -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
