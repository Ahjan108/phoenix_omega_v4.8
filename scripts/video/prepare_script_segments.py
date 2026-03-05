#!/usr/bin/env python3
"""
Script Preparer: render_manifest + optional plan/metadata -> script_segments.
Validates render manifest contract; outputs timed segments for Shot Planner.
Usage: python scripts/video/prepare_script_segments.py <render_manifest.json> -o <script_segments.json> [--content-type therapeutic] [--wpm 140] [--metadata <plan_or_metadata.json>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _word_count(text: str) -> int:
    return len(text.split())


def _duration_from_wpm(words: int, wpm: float) -> float:
    return (words / wpm) * 60.0 if wpm else 0.0


def prepare_segments(manifest: dict, content_type: str, wpm: float, metadata_by_segment: dict | None) -> dict:
    plan_id = manifest["plan_id"]
    segments_in = manifest["segments"]
    out_segments = []
    t = 0.0
    for i, seg in enumerate(segments_in):
        text = seg.get("text", "")
        words = _word_count(text)
        duration_s = _duration_from_wpm(words, wpm)
        end_time_s = t + duration_s
        meta = metadata_by_segment.get(seg["segment_id"]) if metadata_by_segment else None
        if not meta:
            meta = {"arc_role": "hook" if i == 0 else "build", "emotional_band": "calm" if i == 0 else "subdued"}
        out_segments.append({
            "segment_id": seg["segment_id"],
            "text": text,
            "start_time_s": round(t, 2),
            "end_time_s": round(end_time_s, 2),
            "slot_id": seg.get("slot_id", ""),
            "primary_atom_id": seg.get("primary_atom_id", ""),
            "metadata": meta,
        })
        t = end_time_s
    return {
        "plan_id": plan_id,
        "content_type": content_type,
        "segments": out_segments,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare script segments from render manifest")
    ap.add_argument("render_manifest", help="Path to render_manifest.json")
    ap.add_argument("-o", "--out", required=True, help="Output script_segments.json path")
    ap.add_argument("--content-type", default="therapeutic", help="content_type for pacing (default: therapeutic)")
    ap.add_argument("--wpm", type=float, default=140.0, help="Words per minute for timing (default: 140)")
    ap.add_argument("--metadata", help="Optional JSON with segment_id -> { arc_role, emotional_band } or plan with atom metadata")
    args = ap.parse_args()

    path = Path(args.render_manifest)
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if "plan_id" not in manifest or "segments" not in manifest:
        print("Error: render manifest must have plan_id and segments", file=sys.stderr)
        return 1

    metadata_by_segment = None
    if args.metadata:
        meta_path = Path(args.metadata)
        if meta_path.exists():
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "segments" in data:
                metadata_by_segment = {s["segment_id"]: s.get("metadata", {}) for s in data["segments"] if "metadata" in s}
            elif isinstance(data, dict):
                metadata_by_segment = data

    result = prepare_segments(manifest, args.content_type, args.wpm, metadata_by_segment)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {len(result['segments'])} segments to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
