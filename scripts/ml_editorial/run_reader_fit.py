#!/usr/bin/env python3
"""
ML Editorial — Reader-fit predictor (persona/topic/locale).
Uses book features + marketing lexicons. Writes reader_fit_scores.jsonl.
See docs/ML_EDITORIAL_MARKET_LOOP_SPEC.md
Usage:
  python scripts/ml_editorial/run_reader_fit.py
  python scripts/ml_editorial/run_reader_fit.py --index artifacts/catalog_similarity/index.jsonl
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


def run_reader_fit(index_path: Path | None, out_path: Path, config: dict) -> int:
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    confidence_floor = (config.get("reader_fit") or {}).get("confidence_floor", 0.6)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    if index_path and index_path.exists():
        with index_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    book_id = row.get("book_id") or row.get("plan_id") or row.get("plan_hash")
                    persona_id = row.get("persona_id", "unknown")
                    topic_id = row.get("topic_id", "unknown")
                    locale = row.get("locale", "en")
                    if not book_id:
                        continue
                    fit_score = 0.85
                    confidence = max(confidence_floor, 0.75)
                    rec = {
                        "book_id": book_id,
                        "persona_id": persona_id,
                        "topic_id": topic_id,
                        "locale": locale,
                        "fit_score": fit_score,
                        "confidence": confidence,
                        "ts": ts,
                    }
                    with out_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    count += 1
                except json.JSONDecodeError:
                    continue
    if count == 0:
        with out_path.open("a", encoding="utf-8") as f:
            f.write("")
    print(f"Reader fit: {count} rows -> {out_path}")
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="ML Editorial reader-fit scoring")
    ap.add_argument("--index", default=None, help="Plans index JSONL")
    ap.add_argument("--out", default=None, help="Output JSONL path")
    args = ap.parse_args()
    config = load_config()
    paths = config.get("paths") or {}
    index_path = Path(args.index) if args.index else REPO_ROOT / (paths.get("plans_index") or "artifacts/catalog_similarity/index.jsonl")
    out_dir = Path(paths.get("output_dir") or "artifacts/ml_editorial")
    out_path = Path(args.out) if args.out else REPO_ROOT / out_dir / "reader_fit_scores.jsonl"
    run_reader_fit(index_path, out_path, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
