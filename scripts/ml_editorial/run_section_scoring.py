#!/usr/bin/env python3
"""
ML Editorial — Section quality scoring (clarity, pacing, arc drift).
Writes artifacts/ml_editorial/section_scores.jsonl.
See docs/ML_EDITORIAL_MARKET_LOOP_SPEC.md
Usage:
  python scripts/ml_editorial/run_section_scoring.py
  python scripts/ml_editorial/run_section_scoring.py --plans-dir artifacts/rendered --out artifacts/ml_editorial/section_scores.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import re
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


def _heuristic_clarity(text: str) -> float:
    """Simple clarity proxy: inverse of sentence-length variance (normalized)."""
    if not text or not text.strip():
        return 0.5
    sentences = re.split(r"[.!?]+", text.strip())
    lengths = [len(s.split()) for s in sentences if s.strip()]
    if not lengths:
        return 0.5
    mean_len = sum(lengths) / len(lengths)
    var = sum((x - mean_len) ** 2 for x in lengths) / len(lengths) if lengths else 0
    # High variance -> lower clarity; cap and normalize to 0-1
    import math
    sigma = math.sqrt(var) if var > 0 else 0
    if sigma > 20:
        return max(0, 0.5 - (sigma - 20) / 80)
    return min(1.0, 0.5 + (20 - sigma) / 40)


def _heuristic_pacing(segment_lengths: list[int]) -> float:
    """Pacing: prefer moderate, similar segment lengths."""
    if not segment_lengths:
        return 0.5
    mean_len = sum(segment_lengths) / len(segment_lengths)
    if mean_len < 30:
        return 0.6
    if mean_len > 500:
        return 0.4
    return 0.7


def _heuristic_arc_drift(plan: dict | None) -> float:
    """Arc drift: deviation from expected BAND progression (if present). Uses dominant_band_sequence."""
    bands = []
    if plan and isinstance(plan, dict):
        seq = plan.get("dominant_band_sequence") or plan.get("emotional_temperature_sequence")
        if isinstance(seq, list):
            for b in seq:
                if b is not None:
                    bands.append(int(b) if isinstance(b, (int, float)) else 3)
    if len(bands) < 2:
        return 0.0
    # Simple: monotonic rise then fall is ideal; flat or erratic = drift
    changes = [bands[i + 1] - bands[i] for i in range(len(bands) - 1)]
    same = sum(1 for c in changes if c == 0)
    return min(1.0, same / max(1, len(changes)) * 1.5)


def run_section_scoring(plans_dir: Path, out_path: Path, config: dict) -> int:
    thresholds = (config.get("section_quality") or {}).get("thresholds") or {}
    th_clarity = float(thresholds.get("clarity", 0.5))
    th_pacing = float(thresholds.get("pacing", 0.5))
    th_arc = float(thresholds.get("arc_drift", 0.4))
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    if not plans_dir.exists():
        with out_path.open("a", encoding="utf-8") as f:
            f.write("")
        return 0
    for plan_dir in plans_dir.iterdir():
        if not plan_dir.is_dir():
            continue
        book_id = plan_dir.name
        plan_file = plan_dir / "plan.json"
        if not plan_file.exists():
            plan_file = REPO_ROOT / "artifacts" / f"{book_id}.plan.json"
        text_file = plan_dir / "book.txt"
        if not text_file.exists():
            text_file = plan_dir / "book" / "book.txt"
        plan_obj = None
        if plan_file.exists():
            try:
                plan_obj = json.loads(plan_file.read_text())
            except Exception:
                pass
        chapter_texts = []
        if text_file.exists():
            raw = text_file.read_text(encoding="utf-8", errors="replace")
            for block in re.split(r"\n#{1,3}\s+", raw):
                if block.strip():
                    chapter_texts.append(block.strip())
        if not chapter_texts:
            chapter_texts = [""]
        arc_drift = _heuristic_arc_drift(plan_obj)
        for i, seg in enumerate(chapter_texts):
            chapter_id = f"ch_{i+1}"
            clarity = _heuristic_clarity(seg)
            seg_lens = [len(s.split()) for s in re.split(r"[.!?]+", seg) if s.strip()]
            pacing = _heuristic_pacing(seg_lens) if seg_lens else 0.5
            weak_flags = []
            if clarity < th_clarity:
                weak_flags.append("clarity")
            if pacing < th_pacing:
                weak_flags.append("pacing")
            if arc_drift > th_arc:
                weak_flags.append("arc_drift")
            row = {
                "book_id": book_id,
                "chapter_id": chapter_id,
                "clarity_score": round(clarity, 4),
                "pacing_score": round(pacing, 4),
                "arc_drift_score": round(arc_drift, 4),
                "weak_flags": weak_flags,
                "ts": ts,
            }
            with out_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description="ML Editorial section scoring")
    ap.add_argument("--plans-dir", default=None, help="Plans/rendered dir (default from config)")
    ap.add_argument("--out", default=None, help="Output JSONL path")
    args = ap.parse_args()
    config = load_config()
    paths = config.get("paths") or {}
    base = paths.get("compiled_plans_dir") or "artifacts/rendered"
    plans_dir = Path(args.plans_dir) if args.plans_dir else REPO_ROOT / base
    out_dir = Path(paths.get("output_dir") or "artifacts/ml_editorial")
    out_path = Path(args.out) if args.out else REPO_ROOT / out_dir / "section_scores.jsonl"
    n = run_section_scoring(plans_dir, out_path, config)
    print(f"Section scoring: {n} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
