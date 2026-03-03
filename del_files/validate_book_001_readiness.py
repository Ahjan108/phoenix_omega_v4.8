#!/usr/bin/env python3
"""
Book_001 Readiness Validator
Usage: python scripts/validate_book_001_readiness.py --persona gen_z_professional --topic self_worth --engine shame --chapters 6
"""

import argparse
import os
import re
import sys
from collections import Counter

# --- Config ---

VALID_ROLES = {"RECOGNITION", "MECHANISM_PROOF", "TURNING_POINT", "EMBODIMENT"}

BANNED_TERMS = [
    "embarrassed", "humiliated", "ashamed", "self-esteem",
    "owned it", "no one cares", "confidence", "laughed it off",
    "everyone makes mistakes"
]

ANXIETY_BLEED_PATTERNS = [
    r"what if (i|they|she|he|we)",
    r"get fired",
    r"lose (my|the) job",
    r"spiral",
    r"catastroph",
]

TENTATIVE_LANGUAGE = [
    "perhaps", "you might", "maybe", "it's possible",
    "could be", "consider trying", "sometimes it helps",
    "do whatever feels right"
]

INTEGRATION_MODES = {
    "BODY-LANDED", "COST-VISIBLE", "QUESTION-OPEN",
    "STILL-HERE", "FMT", "SOMEONE-ELSE"
}

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
WARN = "\033[93m⚠\033[0m"


def load_canonical(persona, topic, engine):
    path = f"atoms/{persona}/{topic}/{engine}/CANONICAL.txt"
    if not os.path.exists(path):
        print(f"{FAIL} CANONICAL.txt not found at: {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return f.read()


def parse_atoms(content):
    """Parse CANONICAL.txt into list of atom dicts."""
    atoms = []
    blocks = re.split(r"\n(?=## )", content.strip())
    for block in blocks:
        if not block.strip():
            continue
        header_match = re.match(r"## (\w+) (v\d+)", block)
        band_match = re.search(r"BAND:\s*(\d)", block)
        if not header_match:
            continue
        role = header_match.group(1)
        version = header_match.group(2)
        band = int(band_match.group(1)) if band_match else 3
        prose_start = block.find("---\n\n", block.find("BAND:"))
        prose = block[prose_start + 5:].strip() if prose_start != -1 else ""
        atoms.append({
            "id": f"{role}_{version}",
            "role": role,
            "version": version,
            "band": band,
            "prose": prose,
            "raw": block
        })
    return atoms


def check_structural(atoms, chapter_count):
    errors = []
    warnings = []

    # Minimum atoms
    story_atoms = [a for a in atoms if a["role"] in VALID_ROLES]
    if len(story_atoms) < chapter_count:
        errors.append(f"Need {chapter_count} STORY atoms for {chapter_count} chapters. Found {len(story_atoms)}.")
    else:
        print(f"{PASS} STORY atom count: {len(story_atoms)} (need {chapter_count})")

    # BAND presence
    missing_band = [a for a in story_atoms if "BAND:" not in a["raw"]]
    if missing_band:
        warnings.append(f"Atoms missing explicit BAND (will default to 3): {[a['id'] for a in missing_band]}")
    else:
        print(f"{PASS} All atoms have explicit BAND")

    # BAND diversity (minimum 3 distinct values)
    bands = [a["band"] for a in story_atoms]
    distinct_bands = set(bands)
    if len(distinct_bands) < 3:
        errors.append(f"Need 3+ distinct BAND values. Found: {distinct_bands}")
    else:
        print(f"{PASS} Band diversity: {sorted(distinct_bands)}")

    # Valid roles only
    invalid_roles = [a for a in atoms if a["role"] not in VALID_ROLES]
    if invalid_roles:
        errors.append(f"Invalid roles found: {[a['id'] for a in invalid_roles]}")
    else:
        print(f"{PASS} All roles valid: {sorted(set(a['role'] for a in story_atoms))}")

    # Duplicate IDs
    ids = [a["id"] for a in atoms]
    dupes = [k for k, v in Counter(ids).items() if v > 1]
    if dupes:
        errors.append(f"Duplicate atom IDs: {dupes}")
    else:
        print(f"{PASS} No duplicate atom IDs")

    return errors, warnings


def check_engine_purity(atoms):
    errors = []
    warnings = []

    for atom in atoms:
        prose = atom["prose"].lower()
        aid = atom["id"]

        # Banned terms
        hits = [t for t in BANNED_TERMS if t in prose]
        if hits:
            errors.append(f"{aid}: banned terms found: {hits}")

        # Anxiety bleed
        bleed = [p for p in ANXIETY_BLEED_PATTERNS if re.search(p, prose)]
        if bleed:
            warnings.append(f"{aid}: possible anxiety bleed pattern: {bleed}")

        # Body anchor check (rough)
        body_signals = ["face", "chest", "shoulder", "throat", "jaw", "hand", "still", "freeze", "heat"]
        has_anchor = any(s in prose for s in body_signals)
        if not has_anchor:
            errors.append(f"{aid}: no body anchor detected")

        # Resolution language
        resolution = ["it gets better", "you'll be okay", "you realized", "no one noticed",
                      "stood tall", "laughed it off", "owned it", "confidence"]
        hits = [r for r in resolution if r in prose]
        if hits:
            errors.append(f"{aid}: resolution/empowerment language: {hits}")

    if not errors and not warnings:
        print(f"{PASS} Engine purity: all atoms pass shame engine checks")

    return errors, warnings


def check_tts(atoms):
    errors = []
    warnings = []

    for atom in atoms:
        prose = atom["prose"]
        aid = atom["id"]

        # Rhetorical questions
        questions = re.findall(r"[^\"]\?", prose)
        if questions:
            errors.append(f"{aid}: {len(questions)} rhetorical question(s) found")

        # Tentative language
        hits = [t for t in TENTATIVE_LANGUAGE if t in prose.lower()]
        if hits:
            errors.append(f"{aid}: tentative language: {hits}")

        # Sentence length (rough)
        sentences = re.split(r"[.!?]\s+", prose)
        long_sentences = [s for s in sentences if len(s.split()) > 18]
        pct = len(long_sentences) / max(len(sentences), 1)
        if pct > 0.30:
            errors.append(f"{aid}: {pct:.0%} of sentences exceed 18 words (max 30%)")

        # Short sentence check (at least one <= 3 words)
        short = [s for s in sentences if 0 < len(s.split()) <= 3]
        if not short:
            warnings.append(f"{aid}: no sentence of 3 words or fewer found")

    if not errors and not warnings:
        print(f"{PASS} TTS compliance: all atoms pass basic checks")

    return errors, warnings


def check_duplication(atoms):
    """Basic 6-gram duplication check across atoms."""
    errors = []
    ngram_map = {}

    for atom in atoms:
        words = atom["prose"].lower().split()
        for i in range(len(words) - 5):
            gram = " ".join(words[i:i+6])
            if gram in ngram_map:
                if ngram_map[gram] != atom["id"]:
                    errors.append(
                        f"6-gram duplication between {atom['id']} and {ngram_map[gram]}: '{gram}'"
                    )
            else:
                ngram_map[gram] = atom["id"]

    if not errors:
        print(f"{PASS} No 6-gram duplication detected across atoms")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Book_001 Readiness Validator")
    parser.add_argument("--persona", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--chapters", type=int, default=6)
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"BOOK_001 READINESS VALIDATOR")
    print(f"Persona: {args.persona} | Topic: {args.topic} | Engine: {args.engine}")
    print(f"Chapters: {args.chapters}")
    print(f"{'='*60}\n")

    content = load_canonical(args.persona, args.topic, args.engine)
    atoms = parse_atoms(content)
    print(f"Loaded {len(atoms)} atoms from CANONICAL.txt\n")

    all_errors = []
    all_warnings = []

    print("--- STRUCTURAL ---")
    e, w = check_structural(atoms, args.chapters)
    all_errors += e
    all_warnings += w

    print("\n--- ENGINE PURITY ---")
    e, w = check_engine_purity(atoms)
    all_errors += e
    all_warnings += w

    print("\n--- TTS COMPLIANCE ---")
    e, w = check_tts(atoms)
    all_errors += e
    all_warnings += w

    print("\n--- DUPLICATION ---")
    e = check_duplication(atoms)
    all_errors += e

    print(f"\n{'='*60}")
    if all_errors:
        print(f"{FAIL} READINESS: FAIL — {len(all_errors)} error(s)\n")
        for err in all_errors:
            print(f"  {FAIL} {err}")
    else:
        print(f"{PASS} READINESS: PASS — ready for pipeline\n")

    if all_warnings:
        print(f"\n{WARN} Warnings ({len(all_warnings)}):")
        for w in all_warnings:
            print(f"  {WARN} {w}")

    print(f"{'='*60}\n")
    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
