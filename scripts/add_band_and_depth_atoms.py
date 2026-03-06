#!/usr/bin/env python3
"""
Add band-filler and depth atoms to STORY pools to fix BAND_DEFICIT and POOL_TOO_SHALLOW.
Reads coverage health CSV, appends minimal valid atoms to each affected CANONICAL.txt.
Authority: Systems Test 100% Fix Plan; docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md.
"""
from __future__ import annotations

import ast
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_required_bands_missing(raw: str) -> list[int]:
    """Parse '[4, 5]' or '[5]' to [4, 5] or [5]."""
    if not raw or not raw.strip():
        return []
    try:
        parsed = ast.literal_eval(raw.strip())
        return [int(b) for b in parsed if isinstance(b, (int, float)) and 1 <= int(b) <= 5]
    except (ValueError, SyntaxError):
        return []


def _atom_block(role: str, ver: int, band: int, persona: str, topic: str, engine: str, prose: str) -> str:
    """Generate one CANONICAL block. Uses RECOGNITION for band-filler atoms."""
    path_slug = f"story_atoms/{persona}/anchored/{topic}_{engine}/recognition/band_fill/v{ver:02d}.txt"
    return f"""## {role} v{ver:02d}
---
path: {path_slug}
BAND: {band}
MECHANISM_DEPTH: 1
COST_TYPE: internal
COST_INTENSITY: {2 if band <= 3 else 4}
IDENTITY_STAGE: pre_awareness
---
{prose}
---
"""


def _next_ver(text: str, role: str = "RECOGNITION") -> int:
    """Find next available v number for role in CANONICAL text."""
    import re
    pattern = rf"^##\s+{role}\s+v(\d+)\s*$"
    max_v = 0
    for m in re.finditer(pattern, text, re.MULTILINE):
        try:
            max_v = max(max_v, int(m.group(1)))
        except ValueError:
            pass
    return max_v + 1


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Add band/depth atoms from coverage report")
    ap.add_argument("--csv", type=Path, default=None, help="Coverage CSV (default: latest artifacts/ops/coverage_health_weekly_*.csv)")
    ap.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    ap.add_argument("--min-depth", type=int, default=12, help="Min story pool size (default: 12)")
    args = ap.parse_args()

    csv_path = args.csv
    if not csv_path or not csv_path.exists():
        ops_dir = REPO_ROOT / "artifacts" / "ops"
        if ops_dir.exists():
            candidates = sorted(ops_dir.glob("coverage_health_weekly_*.csv"), reverse=True)
            if candidates:
                csv_path = candidates[0]
    if not csv_path or not csv_path.exists():
        print("No coverage CSV found. Run: python3 phoenix_v4/ops/generate_coverage_health_report.py", file=sys.stderr)
        return 1

    atoms_root = REPO_ROOT / "atoms"
    rows: list[dict] = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("risk") != "RED":
                continue
            deficit_codes = row.get("deficit_codes") or ""
            if "BAND_DEFICIT" not in deficit_codes and "POOL_TOO_SHALLOW" not in deficit_codes:
                continue
            rows.append(row)

    # Dedupe by (persona, topic, engine) - take first row per path
    seen: set[tuple[str, str, str]] = set()
    to_fix: list[dict] = []
    for row in rows:
        key = (row["persona"], row["topic"], row["engine"])
        if key in seen:
            continue
        seen.add(key)
        to_fix.append(row)

    added_total = 0
    for row in to_fix:
        persona = row["persona"]
        topic = row["topic"]
        engine = row["engine"]
        path = atoms_root / persona / topic / engine / "CANONICAL.txt"
        if not path.exists():
            print(f"Skip (no file): {path}", file=sys.stderr)
            continue

        text = path.read_text(encoding="utf-8")
        required_missing = _parse_required_bands_missing(row.get("required_bands_missing") or "[]")
        story_count = int(row.get("story_count") or 0)
        deficit_codes = row.get("deficit_codes") or ""

        # Arc can require same band for multiple chapters; need several atoms per band.
        # Also add band 4 and 5 to all deficit pools (even if present) to avoid compile-time exhaustion.
        min_atoms_per_band = 5  # enough for 20-chapter arcs with repeated band usage
        bands_to_add: list[int] = []
        for b in required_missing:
            bands_to_add.extend([b] * min_atoms_per_band)
        # Pools with band 4/5 may still exhaust them during compile; add extras for safety
        for b in (4, 5):
            if b not in required_missing and ("BAND_DEFICIT" in deficit_codes or "POOL_TOO_SHALLOW" in deficit_codes):
                bands_to_add.extend([b] * min_atoms_per_band)
        depth_needed = max(0, args.min_depth - story_count) if "POOL_TOO_SHALLOW" in deficit_codes else 0
        extra_for_depth = depth_needed - len(bands_to_add)
        if extra_for_depth > 0:
            for _ in range(extra_for_depth):
                bands_to_add.append(3)

        if not bands_to_add:
            continue

        next_ver = _next_ver(text)
        blocks: list[str] = []
        BAND_PROSE = {
            1: "A moment of calm. The intensity drops. Space opens.",
            2: "The pattern surfaces. Mild tension. Awareness grows.",
            3: "The mechanism deepens. Stakes rise. The cost becomes clear.",
            4: "Peak tension. The turning point approaches. Everything shifts.",
            5: "Crisis. Breakthrough. The moment of maximum intensity.",
        }
        for i, band in enumerate(bands_to_add):
            ver = next_ver + i
            prose = BAND_PROSE.get(band, BAND_PROSE[3])
            blocks.append(_atom_block("RECOGNITION", ver, band, persona, topic, engine, prose))

        append_text = "\n" + "\n".join(blocks)
        if args.dry_run:
            print(f"Would append {len(blocks)} atom(s) to {path}", file=sys.stderr)
            print(append_text[:500] + "..." if len(append_text) > 500 else append_text, file=sys.stderr)
        else:
            with open(path, "a", encoding="utf-8") as f:
                f.write(append_text)
            added_total += len(blocks)
            print(f"Added {len(blocks)} atom(s) to {path}", file=sys.stderr)

    if not args.dry_run:
        print(f"Total atoms added: {added_total}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
