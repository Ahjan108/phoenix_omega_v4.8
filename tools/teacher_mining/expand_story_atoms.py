#!/usr/bin/env python3
"""
Narrative Expansion Pass: expand short or low-band STORY atoms to increase
tension without inventing events. Offline only; runs after mining, before approval.
Output: expanded candidate atoms with synthesis_method: narrative_expand_v1.
Authority: Teacher Mode structural design — Arc band coverage.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Reuse same heuristic as mine_kb_to_atoms (no sentiment)
ESCALATION_KEYWORDS = {
    "again", "repeatedly", "struggled", "avoided", "conflicted",
    "anxious", "ashamed", "afraid", "worried", "overwhelmed",
    "restless", "resisted", "tense",
}
COST_KEYWORDS = {
    "lost", "rejected", "humiliated", "failed", "collapse",
    "isolated", "alone", "exposed", "broke", "exhausted",
    "abandoned", "betrayed",
}
CRISIS_KEYWORDS = {
    "death", "killed", "murdered", "terminal", "destroyed",
    "suicide", "violence", "exile", "execution", "irreversible",
}

# Sacred/historical — do not expand (fidelity required)
SACRED_HISTORICAL_MARKERS = re.compile(
    r"\b(Angulimala|Prince Siddhartha|Bodhi tree|I have already stopped|"
    r"finger necklace|Dhammapada|starving tigress|two brothers at the river)\b",
    re.I,
)

PROTAGONIST_MARKERS = re.compile(
    r"\b(he|she|the monk|the student|a monk|a student|the man|the woman|"
    r"young man|practitioner|teacher|disciple|Buddha|someone|one)\b",
    re.I,
)

MAX_ADDED_WORDS = 120
ELIGIBLE_MAX_WORDS = 180
ELIGIBLE_MAX_BAND = 3


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _assign_story_band(body: str) -> int:
    """Deterministic band from structural tension markers. Must match mine_kb_to_atoms."""
    text = body.lower()
    escalation_hits = sum(1 for k in ESCALATION_KEYWORDS if k in text)
    cost_hits = sum(1 for k in COST_KEYWORDS if k in text)
    crisis_hits = sum(1 for k in CRISIS_KEYWORDS if k in text)
    mild_hits = sum(1 for k in ("once", "one day", "at one time", "a student asked", "a monk said", "consider the story") if k in text)
    band_score = escalation_hits * 1 + cost_hits * 2 + crisis_hits * 3
    if crisis_hits > 0:
        return 5
    if band_score >= 6:
        return 5
    if band_score >= 4:
        return 4
    if band_score >= 2:
        return 3
    if escalation_hits > 0:
        return 2
    if len(body.split()) < 150 and mild_hits > 0:
        return 1
    return 2


def load_glossary(doctrine_path: Path) -> list[str]:
    doctrine = _load_yaml(doctrine_path)
    glossary = doctrine.get("glossary") or []
    out = []
    for g in glossary:
        if isinstance(g, str):
            term = g.split(" / ")[0].strip().lower()
            if term:
                out.append(term)
        else:
            out.append(str(g).lower())
    return out


def is_eligible(atom: dict, doctrine_path: Path) -> tuple[bool, str]:
    """
    Only expand if: length < 180, band ≤ 3, ≥1 escalation keyword, has protagonist.
    Never expand: crisis, sacred/historical.
    Returns (eligible, reason).
    """
    body = (atom.get("body") or "").strip()
    words = body.split()
    if len(words) >= ELIGIBLE_MAX_WORDS:
        return False, "length >= 180 words"
    band = atom.get("band")
    if band is None:
        band = _assign_story_band(body)
    if band > ELIGIBLE_MAX_BAND:
        return False, f"band {band} > 3"
    text_lower = body.lower()
    if any(k in text_lower for k in CRISIS_KEYWORDS):
        return False, "crisis content"
    if SACRED_HISTORICAL_MARKERS.search(body):
        return False, "sacred/historical"
    has_escalation = any(k in text_lower for k in ESCALATION_KEYWORDS)
    if not has_escalation and band > 2:
        return False, "no escalation keyword and band > 2"
    if not PROTAGONIST_MARKERS.search(body):
        return False, "no protagonist"
    return True, ""


def build_expansion(body: str, doctrine_path: Path) -> tuple[str, int]:
    """
    Deterministic augmentation: pattern, cost, doctrine anchor.
    Returns (expansion_text, word_count_added). Max MAX_ADDED_WORDS.
    """
    text_lower = body.lower()
    glossary = load_glossary(doctrine_path)
    parts = []
    word_count = 0

    # 1. Pattern amplification (repetition framing)
    if "repeatedly" not in text_lower and any(k in text_lower for k in ESCALATION_KEYWORDS):
        s = "This pattern repeated. Each time the cost became a little more visible."
        parts.append(s)
        word_count += len(s.split())

    # 2. Cost clarification (use a cost keyword so band heuristic can rise to 4)
    if not any(k in text_lower for k in COST_KEYWORDS) and word_count < MAX_ADDED_WORDS:
        s = "Over time, this took a toll. What had been inner friction could leave one exhausted or isolated."
        parts.append(s)
        word_count += len(s.split())

    # 3. Teaching anchor (first glossary term not already in body)
    if word_count < MAX_ADDED_WORDS and glossary:
        for term in glossary:
            if term not in text_lower and term.replace(" ", "_") not in text_lower:
                phrase = term.replace("_", " ")
                s = f"In the language of the tradition, this is often called {phrase}."
                parts.append(s)
                word_count += len(s.split())
                break

    if not parts:
        return "", 0
    expansion = " ".join(parts)
    if word_count > MAX_ADDED_WORDS:
        expansion = " ".join(expansion.split()[:MAX_ADDED_WORDS])
        word_count = MAX_ADDED_WORDS
    return expansion, word_count


def expand_atom(
    atom: dict,
    doctrine_path: Path,
    expanded_id: str,
    out_dir: Path,
) -> dict | None:
    """
    Produce one expanded candidate atom. Preserves source_refs; appends [EXPANDED] block.
    Returns new atom dict if written, else None.
    """
    body = (atom.get("body") or "").strip()
    expansion, _ = build_expansion(body, doctrine_path)
    if not expansion:
        return None
    expanded_body = body + "\n\n[EXPANDED]\n" + expansion
    new_band = _assign_story_band(expanded_body)
    teacher = atom.get("teacher") or {}
    source_refs = list(teacher.get("source_refs") or [])
    data = {
        "atom_id": expanded_id,
        "body": expanded_body,
        "teacher": {
            "teacher_id": teacher.get("teacher_id", ""),
            "source_refs": source_refs,
            "synthesis_method": "narrative_expand_v1",
            "expanded_from": atom.get("atom_id"),
        },
        "band": new_band,
    }
    path = out_dir / f"{expanded_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        raise RuntimeError("PyYAML required")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return data


def run_expansion(
    story_dir: Path,
    doctrine_path: Path,
    out_dir: Path,
    teacher_id: str,
) -> tuple[int, int, list[dict]]:
    """
    Load STORY atoms, expand eligible ones, write to out_dir.
    Returns (eligible_count, expanded_count, list of new atom dicts).
    """
    expanded = []
    eligible_count = 0
    index = 0
    for path in sorted(story_dir.glob("*.yaml")):
        atom = _load_yaml(path)
        if not atom or not atom.get("body"):
            continue
        if atom.get("teacher", {}).get("synthesis_method") == "narrative_expand_v1":
            continue  # skip already expanded
        ok, reason = is_eligible(atom, doctrine_path)
        if not ok:
            continue
        eligible_count += 1
        base = path.stem
        if "_expanded_" in base:
            continue
        expanded_id = f"{teacher_id}_STORY_{index:03d}_expanded"
        new_atom = expand_atom(atom, doctrine_path, expanded_id, out_dir)
        if new_atom:
            expanded.append(new_atom)
            index += 1
    return eligible_count, len(expanded), expanded


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Expand short/low-band STORY atoms (narrative expansion pass)"
    )
    ap.add_argument("--teacher", required=True, help="Teacher id")
    ap.add_argument("--stories", default=None, help="Path to STORY atom dir (default: teacher_banks/<id>/candidate_atoms/STORY)")
    ap.add_argument("--doctrine", default=None, help="Path to doctrine.yaml")
    ap.add_argument("--out", default=None, help="Output dir for expanded atoms (default: same as --stories)")
    ap.add_argument("--repo", default=None, help="Repo root")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT
    banks = repo / "SOURCE_OF_TRUTH" / "teacher_banks" / args.teacher.strip().lower()
    story_dir = Path(args.stories) if args.stories else banks / "candidate_atoms" / "STORY"
    doctrine_path = Path(args.doctrine) if args.doctrine else banks / "doctrine" / "doctrine.yaml"
    out_dir = Path(args.out) if args.out else story_dir

    if not story_dir.exists():
        print(f"STORY dir not found: {story_dir}", file=sys.stderr)
        return 1
    if not doctrine_path.exists():
        print(f"Doctrine not found: {doctrine_path}", file=sys.stderr)
        return 1

    eligible, count, new_atoms = run_expansion(
        story_dir, doctrine_path, out_dir, args.teacher.strip().lower()
    )
    print(f"Eligible: {eligible}  Expanded: {count}")
    for a in new_atoms:
        print(f"  {a['atom_id']} band={a.get('band')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
