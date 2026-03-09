#!/usr/bin/env python3
"""
QC: Validates shot_plan, timeline, resolved_assets (no consecutive same asset_id, duration/resolution sane).
Always runs (no skip). Optionally writes qc_summary.json for provenance to reference.
Usage: python scripts/video/run_qc.py <shot_plan.json> <resolved_assets.json> <timeline.json> [--content-type therapeutic] [--out qc_summary.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, write_atomically, REPO_ROOT, PIPELINE_VERSION


def run_qc(
    shot_plan: dict,
    resolved: dict,
    timeline: dict,
    content_type: str,
    allow_consecutive_same_asset: bool = False,
    captions: dict | None = None,
    caption_policies_path: str | None = None,
    require_captions: bool = False,
    max_placeholder_ratio: float = 0.0,
    script_segments: dict | None = None,
    segment_scenes: dict | None = None,
) -> tuple[bool, list[str]]:
    errors = []
    clips = timeline.get("clips", [])
    # No two consecutive shots with same asset_id (unless relaxed for small image bank)
    if not allow_consecutive_same_asset:
        for i in range(1, len(clips)):
            if clips[i].get("asset_id") == clips[i - 1].get("asset_id"):
                errors.append(f"Consecutive clips share asset_id: {clips[i]['asset_id']}")
    # Visual rhythm: max N consecutive clips with same visual_intent. No overrides — similar is not OK.
    motion_policy = load_yaml("config/video/motion_policy.yaml")
    max_same_intent = int(motion_policy.get("max_consecutive_same_visual_intent", 3))
    shot_id_to_intent = {s["shot_id"]: (s.get("visual_intent") or "generic") for s in shot_plan.get("shots", [])}
    run_len = 0
    prev_intent: str | None = None
    for c in clips:
        intent = shot_id_to_intent.get(c.get("shot_id", ""), "generic")
        if intent == prev_intent:
            run_len += 1
            if run_len > max_same_intent:
                errors.append(f"Visual rhythm: more than {max_same_intent} consecutive clips with same visual_intent ({intent})")
                break
        else:
            prev_intent = intent
            run_len = 1
    # Visual Stillness Ratio: therapeutic/long_form must have >= min_static_ratio of clips with motion=static (skip for very short plans)
    min_static = float(motion_policy.get("min_static_ratio", 0.70))
    content_types_enforcing_stillness = ("therapeutic", "long_form")
    if len(clips) >= 3 and content_type in content_types_enforcing_stillness:
        static_count = sum(1 for c in clips if (c.get("motion") or "static").strip().lower() == "static")
        static_ratio = static_count / len(clips)
        if static_ratio < min_static:
            errors.append(f"Visual Stillness Ratio {static_ratio:.2f} below {min_static} (static clips: {static_count}/{len(clips)})")
    # Caption overflow: adapted captions must fit safe zone (max_chars_per_line * max_lines per policy)
    if require_captions:
        if captions is None:
            errors.append("Captions required but captions.json is missing or unreadable")
        else:
            adapted = captions.get("captions") if isinstance(captions, dict) else None
            if not isinstance(adapted, dict) or len(adapted) == 0:
                errors.append("Captions required but captions payload has no adapted caption entries")
    if captions is not None:
        policies = {}
        if caption_policies_path:
            try:
                policies = load_yaml(caption_policies_path) or {}
            except Exception:
                policies = load_yaml("config/video/caption_policies.yaml") or {}
        else:
            policies = load_yaml("config/video/caption_policies.yaml") or {}
        default_policy = (policies.get("default") or {})
        max_chars = int(default_policy.get("max_chars_per_line", 42))
        max_lines = int(default_policy.get("max_lines", 2))
        max_chars_total = max_chars * max_lines
        caption_block = captions.get("adapted") or captions.get("captions") or {}
        for ref_id, block in caption_block.items():
            if isinstance(block, dict):
                text = (block.get("text") or "").strip()
            else:
                text = str(block).strip()
            if not text:
                continue
            # Heuristic: assume worst-case one char per line wrap
            if len(text) > max_chars_total:
                errors.append(f"Caption overflow: ref {ref_id} has {len(text)} chars, safe zone allows {max_chars_total} (max_chars_per_line={max_chars}, max_lines={max_lines})")
    # Duration sanity
    duration_s = timeline.get("duration_s", 0)
    if duration_s <= 0 or duration_s > 3600:
        errors.append(f"Timeline duration_s out of range: {duration_s}")
    pacing = load_yaml("config/video/pacing_by_content_type.yaml")
    ct = (pacing.get("content_types") or {}).get(content_type) or {}
    max_d = ct.get("max_duration_s", 600)
    if duration_s > max_d:
        errors.append(f"Duration {duration_s}s exceeds content_type max {max_d}s")
    # Resolution
    res = timeline.get("resolution", {})
    w, h = res.get("width", 0), res.get("height", 0)
    if w < 100 or h < 100:
        errors.append(f"Invalid resolution: {w}x{h}")
    # Placeholder budget: if too many placeholder assets survive resolver, fail.
    if clips:
        placeholder_count = sum(1 for c in clips if str(c.get("asset_id", "")).startswith("placeholder_"))
        placeholder_ratio = placeholder_count / len(clips)
        if placeholder_ratio > max_placeholder_ratio:
            errors.append(
                f"Placeholder ratio {placeholder_ratio:.2f} exceeds max {max_placeholder_ratio:.2f} "
                f"({placeholder_count}/{len(clips)} clips)"
            )
    # Semantic coherence: require one valid scene per script segment and disallow fallback-marked scenes.
    if script_segments is not None and segment_scenes is not None:
        segs = script_segments.get("segments") or []
        scenes = segment_scenes.get("segments") or []
        if len(segs) != len(scenes):
            errors.append(f"Scene/script count mismatch: script_segments={len(segs)} segment_scenes={len(scenes)}")
        scene_by_id = {s.get("segment_id"): s for s in scenes if s.get("segment_id")}
        for seg in segs:
            sid = seg.get("segment_id")
            text = (seg.get("text") or "").strip().lower()
            sc = scene_by_id.get(sid)
            if not sc:
                errors.append(f"Missing scene metadata for segment_id={sid}")
                continue
            if sc.get("source") == "fallback":
                errors.append(f"Scene metadata uses fallback for segment_id={sid}")
            desc = (sc.get("scene_description") or "").strip().lower()
            if not desc:
                errors.append(f"Empty scene_description for segment_id={sid}")
                continue
            text_words = {w for w in text.split() if len(w) > 3}
            desc_words = {w for w in desc.split() if len(w) > 3}
            if text_words and desc_words:
                overlap = len(text_words.intersection(desc_words)) / max(1, len(desc_words))
                if overlap < 0.15:
                    errors.append(
                        f"Low text-scene overlap for {sid} (overlap={overlap:.2f}); scene may not match script meaning"
                    )
    passed = len(errors) == 0
    return passed, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Run QC on shot plan, resolved assets, timeline")
    ap.add_argument("shot_plan", help="Path to shot_plan.json")
    ap.add_argument("resolved_assets", help="Path to resolved_assets.json")
    ap.add_argument("timeline", help="Path to timeline.json")
    ap.add_argument("--content-type", default="therapeutic")
    ap.add_argument("--allow-consecutive-same-asset", action="store_true", help="Allow same asset_id on consecutive clips (e.g. small image bank)")
    ap.add_argument("-o", "--out", help="Write qc_summary.json (passed, errors, checks) for provenance to reference")
    ap.add_argument("--captions", help="Path to captions.json for caption overflow check (optional)")
    ap.add_argument("--caption-policies", default="config/video/caption_policies.yaml", help="Caption policies YAML for max_chars_per_line/max_lines")
    ap.add_argument("--require-captions", action="store_true", help="Fail if captions are missing or empty")
    ap.add_argument("--max-placeholder-ratio", type=float, default=0.0, help="Fail if placeholder assets exceed this clip ratio (0.0 = none allowed)")
    ap.add_argument("--script-segments", help="Path to script_segments.json for semantic coherence checks")
    ap.add_argument("--segment-scenes", help="Path to segment_scenes.json for semantic coherence checks")
    args = ap.parse_args()

    paths = [Path(args.shot_plan), Path(args.resolved_assets), Path(args.timeline)]
    if not all(p.exists() for p in paths):
        print("Error: one or more inputs not found", file=sys.stderr)
        return 1
    shot_plan = json.loads(paths[0].read_text(encoding="utf-8"))
    resolved = json.loads(paths[1].read_text(encoding="utf-8"))
    timeline = json.loads(paths[2].read_text(encoding="utf-8"))
    captions = None
    if args.captions and Path(args.captions).exists():
        captions = json.loads(Path(args.captions).read_text(encoding="utf-8"))
    script_segments = None
    segment_scenes = None
    if args.script_segments and Path(args.script_segments).exists():
        script_segments = json.loads(Path(args.script_segments).read_text(encoding="utf-8"))
    if args.segment_scenes and Path(args.segment_scenes).exists():
        segment_scenes = json.loads(Path(args.segment_scenes).read_text(encoding="utf-8"))

    passed, errors = run_qc(
        shot_plan, resolved, timeline, args.content_type, args.allow_consecutive_same_asset,
        captions=captions, caption_policies_path=args.caption_policies,
        require_captions=args.require_captions,
        max_placeholder_ratio=max(0.0, min(1.0, float(args.max_placeholder_ratio))),
        script_segments=script_segments,
        segment_scenes=segment_scenes,
    )
    if args.out:
        summary = {
            "pipeline_version": PIPELINE_VERSION,
            "passed": passed,
            "errors": errors,
            "checks": ["consecutive_asset_id", "visual_rhythm", "stillness_ratio", "caption_presence", "caption_overflow", "duration", "resolution", "placeholder_ratio", "semantic_coherence"],
        }
        write_atomically(Path(args.out), summary)
    if errors:
        for e in errors:
            print(f"QC: {e}", file=sys.stderr)
        return 0 if passed else 1
    print("QC passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
