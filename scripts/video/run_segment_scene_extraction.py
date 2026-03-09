#!/usr/bin/env python3
"""
Segment scene extraction (LLM): read script segments, have the LLM understand what each
segment is saying, and output metadata (scene_description, mood, avoid) to prompt the image.
So visuals are specific to the script — not generic "hands" or abstract symbols.

Uses an OpenAI-compatible chat API (config: config/video/segment_scene_llm.yaml; env:
QWEN_BASE_URL/QWEN_API_KEY/QWEN_MODEL preferred, with OPENAI_* aliases supported).
Can be pointed at Enlightened Intelligence V2 or any JSON-capable LLM.

Usage:
  python scripts/video/run_segment_scene_extraction.py script_segments.json -o segment_scenes.json
  python scripts/video/run_segment_scene_extraction.py script_segments.json -o segment_scenes.json --topic depression --platform tiktok
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def load_yaml(rel_path: str) -> dict:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        raise RuntimeError("PyYAML required; pip install pyyaml")


def call_llm_chat(messages: list[dict], config: dict) -> str:
    """Call OpenAI-compatible chat completions. Returns content of first choice."""
    base_url = (
        config.get("base_url")
        or os.environ.get("QWEN_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1")
    ).rstrip("/")
    api_key = (
        config.get("api_key")
        or os.environ.get("QWEN_API_KEY")
        or os.environ.get("OPENAI_API_KEY", "not-set")
    )
    model = (
        config.get("model")
        or os.environ.get("QWEN_MODEL")
        or os.environ.get("OPENAI_MODEL", "qwen2.5:latest")
    )
    max_tokens = config.get("max_tokens", 400)
    timeout = config.get("timeout_seconds", 30)

    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    headers = {"Content-Type": "application/json"}
    if api_key and api_key != "not-set":
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        import requests
    except ImportError:
        raise RuntimeError("requests required; pip install requests")

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("LLM returned no choices")
    content = (choices[0].get("message") or {}).get("content") or ""
    return content.strip()


def extract_json_from_response(text: str) -> dict:
    """Pull a single JSON object from LLM output (handle markdown code blocks)."""
    text = text.strip()
    # Strip markdown code block if present
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start) if "```" in text[start:] else len(text)
        text = text[start:end]
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start) if "```" in text[start:] else len(text)
        text = text[start:end]
    # Find first { ... }
    match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)


def _load_platform_video_rules(platform: str) -> dict:
    cfg = load_yaml("config/video/platform_video_story_rules.yaml")
    return (cfg.get("platforms") or {}).get(platform, {})


def build_user_prompt(
    seg: dict,
    topic: str,
    platform: str,
    platform_rules: dict,
    script_summary: str,
    repair_note: str = "",
) -> str:
    segment_id = seg.get("segment_id", "?")
    slot_id = seg.get("slot_id", "")
    text = (seg.get("text") or "").strip()
    meta = seg.get("metadata") or {}
    arc_role = meta.get("arc_role", "")
    emotional_band = meta.get("emotional_band", "")
    rules_text = "; ".join(platform_rules.get("scene_directives", []))
    repair_text = f"\nRepair note: {repair_note}\n" if repair_note else ""
    return (
        f"Platform: {platform}\n"
        f"Topic: {topic}\n"
        f"Segment ID: {segment_id}\n"
        f"Slot: {slot_id}\n"
        f"Arc role: {arc_role}\n"
        f"Emotional band: {emotional_band}\n"
        f"Full script summary: {script_summary}\n"
        f"Platform scene directives: {rules_text}\n\n"
        f"{repair_text}"
        f"Script segment:\n{text}\n\n"
        "Output a single JSON object with keys: scene_description (one short sentence for the image, concrete and filmable, specific to this script), mood (one word), avoid (list of 0–4 things to avoid)."
    )


def run_extraction(
    script_segments_path: Path,
    out_path: Path,
    topic: str,
    platform: str,
    config: dict,
    dry_run: bool,
    repair_note: str = "",
) -> int:
    if not script_segments_path.exists():
        print(f"Error: not found {script_segments_path}", file=sys.stderr)
        return 1

    data = json.loads(script_segments_path.read_text(encoding="utf-8"))
    segments = data.get("segments") or []
    plan_id = data.get("plan_id", "unknown")

    if not segments:
        print("No segments in script_segments.json", file=sys.stderr)
        return 1

    llm_config = {
        "base_url": (
            config.get("base_url")
            or os.environ.get("QWEN_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
        ),
        "api_key": (
            config.get("api_key")
            or os.environ.get("QWEN_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        ),
        "model": (
            config.get("model")
            or os.environ.get("QWEN_MODEL")
            or os.environ.get("OPENAI_MODEL", "qwen2.5:latest")
        ),
        "max_tokens": config.get("max_tokens", 400),
        "timeout_seconds": config.get("timeout_seconds", 30),
    }
    if not dry_run and not llm_config.get("base_url"):
        print(
            "Error: QWEN_BASE_URL/OPENAI_BASE_URL (or config base_url) is required for segment scene extraction.",
            file=sys.stderr,
        )
        return 1

    platform_rules = _load_platform_video_rules(platform)
    script_summary = " ".join((seg.get("text") or "").strip() for seg in segments)
    script_summary = re.sub(r"\s+", " ", script_summary)[:1200]
    system_hint = (config.get("system_hint") or "").strip()
    if not system_hint:
        system_hint = (
            "You are an expert at turning script copy into visual briefs for soft, contemplative illustrations. "
            "Understand what each segment is saying in context of the full script and output JSON: "
            "scene_description (one short sentence, specific and visual), mood (one word), avoid (list of things to avoid). "
            "Avoid generic abstractions."
        )

    results = []
    failures: list[str] = []
    for i, seg in enumerate(segments):
        segment_id = seg.get("segment_id", f"seg-{i+1}")
        user_content = build_user_prompt(seg, topic, platform, platform_rules, script_summary, repair_note=repair_note)
        messages = [
            {"role": "system", "content": system_hint},
            {"role": "user", "content": user_content},
        ]

        if dry_run:
            print(f"[dry-run] would call LLM for {segment_id}: {user_content[:200]}...")
            results.append({
                "segment_id": segment_id,
                "slot_id": seg.get("slot_id", ""),
                "text_preview": (seg.get("text") or "")[:120] + ("..." if len(seg.get("text") or "") > 120 else ""),
                "scene_description": "(dry-run)",
                "mood": "contemplative",
                "avoid": [],
            })
            continue

        try:
            content = call_llm_chat(messages, llm_config)
            obj = extract_json_from_response(content)
            scene_description = obj.get("scene_description") or obj.get("scene") or ""
            if not str(scene_description).strip():
                raise RuntimeError("scene_description missing from LLM response")
            mood = obj.get("mood") or "contemplative"
            avoid = obj.get("avoid")
            if not isinstance(avoid, list):
                avoid = [avoid] if avoid else []
            results.append({
                "segment_id": segment_id,
                "slot_id": seg.get("slot_id", ""),
                "text_preview": (seg.get("text") or "")[:120] + ("..." if len(seg.get("text") or "") > 120 else ""),
                "scene_description": scene_description,
                "mood": mood,
                "avoid": avoid,
            })
            print(f"  {segment_id}: {scene_description[:80]}...")
        except Exception as e:
            failures.append(f"{segment_id}: {e}")
            print(f"  {segment_id}: LLM error (hard fail mode)", file=sys.stderr)

    if failures:
        print("Error: segment scene extraction failed for one or more segments:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    out = {
        "plan_id": plan_id,
        "topic": topic,
        "platform": platform,
        "segments": results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} segment scenes to {out_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract per-segment image prompt metadata via LLM")
    ap.add_argument("script_segments", help="Path to script_segments.json")
    ap.add_argument("-o", "--out", required=True, help="Output segment_scenes.json path")
    ap.add_argument("--topic", default="depression", help="Topic for context (e.g. depression, anxiety)")
    ap.add_argument("--platform", default="tiktok", help="Target platform (tiktok, youtube, instagram_reels)")
    ap.add_argument("--config", default="config/video/segment_scene_llm.yaml", help="LLM config YAML")
    ap.add_argument("--repair-note", default="", help="Optional retry guidance injected into prompt for repair attempts")
    ap.add_argument("--dry-run", action="store_true", help="Print prompts and write placeholder output")
    args = ap.parse_args()

    config_path = REPO_ROOT / args.config
    config = load_yaml(args.config) if config_path.exists() else {}
    return run_extraction(
        Path(args.script_segments),
        Path(args.out),
        args.topic,
        args.platform,
        config,
        args.dry_run,
        args.repair_note,
    )


if __name__ == "__main__":
    sys.exit(main())
