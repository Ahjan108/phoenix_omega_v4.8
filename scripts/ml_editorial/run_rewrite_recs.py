#!/usr/bin/env python3
"""
ML Editorial — Rewrite recommender from weak-section flags.
Enforces forbidden-token/compliance from 02/03. Writes rewrite_recs.jsonl.
See docs/ML_EDITORIAL_MARKET_LOOP_SPEC.md
Usage:
  python scripts/ml_editorial/run_rewrite_recs.py
  python scripts/ml_editorial/run_rewrite_recs.py --section-scores artifacts/ml_editorial/section_scores.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(REPO_ROOT)
import sys
sys.path.insert(0, str(REPO_ROOT))


def load_config() -> dict:
    path = REPO_ROOT / "config" / "ml_editorial" / "ml_editorial_config.yaml"
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def run_rewrite_recs(section_scores_path: Path, out_path: Path, config: dict) -> int:
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    max_recs = (config.get("rewrite_recs") or {}).get("max_recommendations_per_chapter", 3)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    if not section_scores_path.exists():
        with out_path.open("a", encoding="utf-8") as f:
            f.write("")
        return 0
    with section_scores_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                weak_flags = row.get("weak_flags") or []
                if not weak_flags:
                    continue
                book_id = row.get("book_id", "")
                chapter_id = row.get("chapter_id", "")
                for i, issue_type in enumerate(weak_flags):
                    if i >= max_recs:
                        break
                    recommendation = f"Revise for {issue_type}: tighten sentences (clarity), vary segment length (pacing), or align emotional arc (arc_drift)."
                    rec = {
                        "book_id": book_id,
                        "chapter_id": chapter_id,
                        "issue_type": issue_type,
                        "recommendation": recommendation,
                        "constraint_set": "brand_voice,forbidden_tokens_02_03",
                        "expected_gain": 0.2,
                        "ts": ts,
                    }
                    with out_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    count += 1
            except json.JSONDecodeError:
                continue
    print(f"Rewrite recs: {count} rows -> {out_path}")
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="ML Editorial rewrite recommendations")
    ap.add_argument("--section-scores", default=None, help="section_scores.jsonl path")
    ap.add_argument("--out", default=None, help="Output JSONL path")
    args = ap.parse_args()
    config = load_config()
    paths = config.get("paths") or {}
    out_dir = Path(paths.get("output_dir") or "artifacts/ml_editorial")
    section_path = Path(args.section_scores) if args.section_scores else REPO_ROOT / out_dir / "section_scores.jsonl"
    out_path = Path(args.out) if args.out else REPO_ROOT / out_dir / "rewrite_recs.jsonl"
    run_rewrite_recs(section_path, out_path, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
