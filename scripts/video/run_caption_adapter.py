#!/usr/bin/env python3
"""
CaptionAdapter: timeline + script_segments + caption_policies -> caption content per segment (reflow/truncate).
Outputs a captions JSON keyed by segment_id with adapted text and truncation_flag if > threshold.
Usage: python scripts/video/run_caption_adapter.py <timeline.json> <script_segments.json> -o <captions.json> [--format 16:9] [--lang en]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, REPO_ROOT


def _last_complete_clause_boundary(text: str, max_chars: int) -> int:
    if len(text) <= max_chars:
        return len(text)
    chunk = text[: max_chars + 1]
    for sep in [". ", "! ", "? ", "; ", ", "]:
        idx = chunk.rfind(sep)
        if idx != -1:
            return idx + len(sep)
    idx = chunk.rfind(" ")
    return idx + 1 if idx != -1 else max_chars


def adapt_caption(text: str, max_chars_per_line: int, max_lines: int, strategy: str, flag_threshold_pct: float) -> tuple[str, bool]:
    max_total = max_chars_per_line * max_lines
    if len(text) <= max_total:
        return text, False
    if strategy == "truncate" or strategy == "reflow_then_truncate":
        cut = _last_complete_clause_boundary(text, max_total)
        out = text[:cut].rstrip()
        if cut < len(text) and out and not out.endswith((".", "!", "?")):
            out += "…"
        truncated_pct = (1 - len(out) / len(text)) * 100 if text else 0
        return out, truncated_pct > flag_threshold_pct
    return text[:max_total], len(text) > max_total


def run_caption_adapter(timeline: dict, script_segments: dict, fmt: str, lang: str) -> dict:
    policies = load_yaml("config/video/caption_policies.yaml")
    default = policies.get("default") or {}
    by_lang = (policies.get("by_language") or {}).get(lang) or default
    max_chars = by_lang.get("max_chars_per_line", default.get("max_chars_per_line", 42))
    max_lines = by_lang.get("max_lines", default.get("max_lines", 2))
    strategy = default.get("strategy", "reflow")
    flag_pct = default.get("truncation_flag_threshold_pct", 50)
    segment_text = {s["segment_id"]: s["text"] for s in script_segments.get("segments", [])}
    captions = {}
    for clip in timeline.get("clips", []):
        seg_id = clip.get("caption_ref", "")
        text = segment_text.get(seg_id, "")
        adapted, flag = adapt_caption(text, max_chars, max_lines, strategy, flag_pct)
        captions[seg_id] = {"text": adapted, "truncation_flagged": flag}
    return {
        "plan_id": timeline.get("plan_id", ""),
        "format": fmt,
        "language": lang,
        "captions": captions,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Adapt captions per format/language from caption_policies")
    ap.add_argument("timeline", help="Path to timeline.json")
    ap.add_argument("script_segments", help="Path to script_segments.json")
    ap.add_argument("-o", "--out", required=True, help="Output captions.json path")
    ap.add_argument("--format", default="16:9", help="Aspect format for policy")
    ap.add_argument("--lang", default="en", help="Language code")
    args = ap.parse_args()

    tl_path = Path(args.timeline)
    seg_path = Path(args.script_segments)
    if not tl_path.exists() or not seg_path.exists():
        print("Error: timeline or script_segments not found", file=sys.stderr)
        return 1
    timeline = json.loads(tl_path.read_text(encoding="utf-8"))
    script_segments = json.loads(seg_path.read_text(encoding="utf-8"))

    result = run_caption_adapter(timeline, script_segments, args.format, args.lang)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote captions for {len(result['captions'])} segments to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
