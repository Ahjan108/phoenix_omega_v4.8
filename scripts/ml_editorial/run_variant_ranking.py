#!/usr/bin/env python3
"""
ML Editorial — Variant ranker (title/subtitle/opening).
Consumes marketing lexicons (04 invisible_scripts, 03 consumer). Writes variant_rankings.jsonl.
See docs/ML_EDITORIAL_MARKET_LOOP_SPEC.md
Usage:
  python scripts/ml_editorial/run_variant_ranking.py
  python scripts/ml_editorial/run_variant_ranking.py --index artifacts/catalog_similarity/index.jsonl
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


def load_marketing_lexicons(config: dict) -> tuple[dict, dict] | None:
    """Load persona/topic lexicons from EI V2 marketing when enabled. Returns (persona_lexicons, topic_lexicons) or None."""
    ms = (config.get("marketing_sources") or {}).get("enabled", False)
    if not ms:
        return None
    try:
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
        from phoenix_v4.quality.ei_v2.marketing_lexicons import load_marketing_lexicons as load_lex
        cfg = load_ei_v2_config()
        out = load_lex(cfg, REPO_ROOT)
        if out is None:
            return None
        persona_lex, topic_lex, _banned, _forbidden, _hashes = out
        return (persona_lex or {}, topic_lex or {})
    except Exception:
        return None


def load_config() -> dict:
    path = REPO_ROOT / "config" / "ml_editorial" / "ml_editorial_config.yaml"
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def run_variant_ranking(index_path: Path | None, out_path: Path, config: dict) -> int:
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    confidence_floor = (config.get("variant_ranker") or {}).get("confidence_floor", 0.7)
    variant_types = (config.get("variant_ranker") or {}).get("variant_types") or ["title", "subtitle", "opening"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    books_seen = set()
    lexicons = load_marketing_lexicons(config)
    if index_path and index_path.exists():
        with index_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    book_id = row.get("book_id") or row.get("plan_id") or row.get("plan_hash")
                    if not book_id:
                        continue
                    if book_id in books_seen:
                        continue
                    books_seen.add(book_id)
                    persona_id = row.get("persona_id", "")
                    topic_id = row.get("topic_id", "")
                    locale = row.get("locale", "en")
                    rank_base = 0.8
                    if lexicons and (persona_id or topic_id):
                        rank_base = min(0.95, rank_base + 0.05)
                    for vt in variant_types:
                        rec = {
                            "book_id": book_id,
                            "variant_type": vt,
                            "variant_id": f"{book_id}_{vt}_1",
                            "rank_score": rank_base,
                            "confidence": confidence_floor,
                            "ts": ts,
                            "persona_id": persona_id,
                            "topic_id": topic_id,
                            "locale": locale,
                        }
                        with out_path.open("a", encoding="utf-8") as f:
                            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        count += 1
                except json.JSONDecodeError:
                    continue
    if count == 0:
        with out_path.open("a", encoding="utf-8") as f:
            f.write("")
    print(f"Variant ranking: {count} rows -> {out_path}")
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="ML Editorial variant ranking")
    ap.add_argument("--index", default=None, help="Plans index JSONL")
    ap.add_argument("--out", default=None, help="Output JSONL path")
    args = ap.parse_args()
    config = load_config()
    paths = config.get("paths") or {}
    index_path = Path(args.index) if args.index else REPO_ROOT / (paths.get("plans_index") or "artifacts/catalog_similarity/index.jsonl")
    out_dir = Path(paths.get("output_dir") or "artifacts/ml_editorial")
    out_path = Path(args.out) if args.out else REPO_ROOT / out_dir / "variant_rankings.jsonl"
    run_variant_ranking(index_path, out_path, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
