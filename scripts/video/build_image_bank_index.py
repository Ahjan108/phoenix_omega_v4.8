#!/usr/bin/env python3
"""
Build image_bank/index.json from existing PNGs in the bank directory.
Expects filenames like {topic}_{visual_intent}.png (e.g. anxiety_HOOK_VISUAL.png).
Usage: python scripts/video/build_image_bank_index.py [--bank-dir image_bank] -o index.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Known visual_intents from shot planner / flux_bank_scenes
KNOWN_INTENTS = ["HOOK_VISUAL", "CHARACTER_EMOTION", "SYMBOLIC_METAPHOR", "ENVIRONMENT_ATMOSPHERE"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Build image bank index from existing PNGs")
    ap.add_argument("--bank-dir", type=Path, default=None, help="Bank directory (default: repo image_bank/)")
    ap.add_argument("-o", "--out", type=Path, default=None, help="Output index path (default: bank_dir/index.json)")
    args = ap.parse_args()

    bank_dir = args.bank_dir or (REPO_ROOT / "image_bank")
    bank_dir = Path(bank_dir)
    out_path = args.out or (bank_dir / "index.json")
    out_path = Path(out_path)

    if not bank_dir.exists():
        print(f"Bank directory does not exist: {bank_dir}", file=sys.stderr)
        return 1

    index_entries = []
    for png in sorted(bank_dir.glob("*.png")):
        stem = png.stem
        # Match stem ending with _VISUAL or _EMOTION etc.
        visual_intent = None
        for intent in KNOWN_INTENTS:
            if stem.endswith("_" + intent) or stem == intent:
                visual_intent = intent
                break
        if not visual_intent:
            # Treat whole stem as asset_id, use CHARACTER_EMOTION as fallback so resolver can still pick it
            visual_intent = "CHARACTER_EMOTION"
        index_entries.append({
            "visual_intent": visual_intent,
            "composition_compat": {"16:9": 1.0, "9:16": 1.0},
            "asset_id": stem,
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index_entries, indent=2), encoding="utf-8")
    print(f"Wrote {len(index_entries)} entries to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
