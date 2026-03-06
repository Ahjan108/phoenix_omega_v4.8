#!/usr/bin/env python3
"""
Add band atoms from systems test report failures.
Parses 'Arc required BAND X for chapter Y' errors and adds atoms to the affected pools.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _atom_block(role: str, ver: int, band: int, persona: str, topic: str, engine: str, prose: str) -> str:
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
    import re as re_mod
    pattern = rf"^##\s+{role}\s+v(\d+)\s*$"
    max_v = 0
    for m in re_mod.finditer(pattern, text, re_mod.MULTILINE):
        try:
            max_v = max(max_v, int(m.group(1)))
        except ValueError:
            pass
    return max_v + 1


BAND_PROSE = {
    1: "A moment of calm. The intensity drops. Space opens.",
    2: "The pattern surfaces. Mild tension. Awareness grows.",
    3: "The mechanism deepens. Stakes rise. The cost becomes clear.",
    4: "Peak tension. The turning point approaches. Everything shifts.",
    5: "Crisis. Breakthrough. The moment of maximum intensity.",
}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Add atoms from systems test report failures")
    ap.add_argument("--report", type=Path, required=True, help="Report JSON path")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--atoms-per-band", type=int, default=5, help="Atoms to add per band per pool")
    args = ap.parse_args()

    if not args.report.exists():
        print(f"Report not found: {args.report}", file=sys.stderr)
        return 1

    data = json.loads(args.report.read_text())
    results = data.get("results") or []
    band_re = re.compile(r"Arc required BAND (\d) for chapter \d+")

    # Collect (persona, topic, engine) -> set of bands needed
    needs: dict[tuple[str, str, str], set[int]] = {}
    for r in results:
        if not r.get("passed") and r.get("category") == "pipeline_fail":
            msg = r.get("message") or ""
            check_id = r.get("check_id") or ""
            m = re.search(r"phase3_pipeline_([a-z0-9_]+)__([a-z0-9_]+)__([a-z0-9_]+)__F\d+", check_id)
            if not m:
                continue
            persona, topic, engine = m.group(1), m.group(2), m.group(3)
            for bm in band_re.finditer(msg):
                band = int(bm.group(1))
                key = (persona, topic, engine)
                needs.setdefault(key, set()).add(band)

    atoms_root = REPO_ROOT / "atoms"
    added_total = 0
    for (persona, topic, engine), bands in needs.items():
        path = atoms_root / persona / topic / engine / "CANONICAL.txt"
        if not path.exists():
            print(f"Skip (no file): {path}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        next_ver = _next_ver(text)
        bands_to_add = []
        for b in sorted(bands):
            bands_to_add.extend([b] * args.atoms_per_band)
        blocks = []
        for i, band in enumerate(bands_to_add):
            ver = next_ver + i
            prose = BAND_PROSE.get(band, BAND_PROSE[3])
            blocks.append(_atom_block("RECOGNITION", ver, band, persona, topic, engine, prose))
        append_text = "\n" + "\n".join(blocks)
        if args.dry_run:
            print(f"Would append {len(blocks)} atom(s) to {path} (bands {sorted(bands)})", file=sys.stderr)
        else:
            with open(path, "a", encoding="utf-8") as f:
                f.write(append_text)
            added_total += len(blocks)
            print(f"Added {len(blocks)} atom(s) to {path} (bands {sorted(bands)})", file=sys.stderr)
    if not args.dry_run:
        print(f"Total atoms added: {added_total}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
