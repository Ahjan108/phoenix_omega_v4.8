#!/usr/bin/env python3
"""
Simulate STORY band distribution from mined (and optionally expanded) atoms.
Structural only; no prose scoring. Use to check Arc coverage and target ratios.
"""
from __future__ import annotations

import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Must match mine_kb_to_atoms and expand_story_atoms
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
MILD_INDICATORS = {
    "once", "one day", "at one time", "a student asked",
    "a monk said", "consider the story",
}

TARGET_RATIOS = {
    1: (10, 15),
    2: (20, 20),
    3: (30, 35),
    4: (20, 25),
    5: (5, 10),
}


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def assign_story_band(body: str) -> int:
    """Deterministic band; must match mine_kb_to_atoms."""
    text = body.lower()
    escalation_hits = sum(1 for k in ESCALATION_KEYWORDS if k in text)
    cost_hits = sum(1 for k in COST_KEYWORDS if k in text)
    crisis_hits = sum(1 for k in CRISIS_KEYWORDS if k in text)
    mild_hits = sum(1 for k in MILD_INDICATORS if k in text)
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


def run_simulation(story_dir: Path) -> dict[int, int]:
    """Load all STORY YAMLs; return band -> count (using stored band or heuristic)."""
    bands: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for path in sorted(story_dir.glob("*.yaml")):
        atom = _load_yaml(path)
        if not atom or not atom.get("body"):
            continue
        body = (atom.get("body") or "").strip()
        band = atom.get("band")
        if band is None:
            band = assign_story_band(body)
        if 1 <= band <= 5:
            bands[band] = bands.get(band, 0) + 1
    return bands


def main() -> int:
    ap = argparse.ArgumentParser(description="Simulate STORY band distribution")
    ap.add_argument("--stories", required=True, help="Path to STORY atom dir (e.g. candidate_atoms/STORY)")
    ap.add_argument("--repo", default=None, help="Repo root")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT
    story_dir = Path(args.stories)
    if not story_dir.is_absolute():
        story_dir = repo / story_dir
    if not story_dir.exists():
        print(f"Dir not found: {story_dir}", file=__import__("sys").stderr)
        return 1

    bands = run_simulation(story_dir)
    total = sum(bands.values())
    print("STORY band distribution (simulated)")
    print(f"  Total atoms: {total}")
    if total == 0:
        print("  No STORY atoms found.")
        return 0
    print("  Band  Count   %    Target %")
    for b in range(1, 6):
        c = bands.get(b, 0)
        pct = 100 * c / total
        lo, hi = TARGET_RATIOS.get(b, (0, 0))
        print(f"  {b}     {c:3}   {pct:5.1f}   {lo}–{hi}")
    print()
    print("Target ratios (teacher-dependent): Band 1: 10–15%, 2: 20%, 3: 30–35%, 4: 20–25%, 5: 5–10%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
