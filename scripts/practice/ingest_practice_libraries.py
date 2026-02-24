"""
Ingest practice libraries from inbox JSONs into raw JSONL.
Reads *_library_34.json and optional exercises_ab_tady_37*.json.
Deterministic: no LLM, no mutation of source prose.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _canonical_order(item: dict) -> dict:
    """Return item with fields in canonical order for PracticeItem."""
    order = [
        "practice_id", "source", "content_type", "duration_seconds", "intensity_band",
        "text", "blocks", "allowed_personas", "allowed_topics", "angle_affinity", "tags", "version",
    ]
    out = {}
    for k in order:
        if k in item:
            out[k] = item[k]
    for k, v in item.items():
        if k not in out:
            out[k] = v
    return out


def _ingest_library_34(path: Path, content_type: str) -> list[dict]:
    """Load a *_library_34.json and yield normalized PracticeItems."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    exercises = raw.get("exercises") or []
    out = []
    for i, ex in enumerate(exercises):
        ex_id = ex.get("id") or f"{content_type}_{i+1:03d}"
        practice_id = f"lib34_{content_type}_{i+1:02d}"
        duration = int(ex.get("duration_seconds") or 90)
        text = (ex.get("text") or "").strip()
        if len(text) < 50:
            continue
        item = {
            "practice_id": practice_id,
            "source": "library_34",
            "content_type": content_type,
            "duration_seconds": max(30, min(1200, duration)),
            "intensity_band": 3,
            "text": text,
            "blocks": {"setup": None, "instruction": None, "prompt": None, "close": None},
            "allowed_personas": [],
            "allowed_topics": [],
            "angle_affinity": [],
            "tags": list(ex.get("tags") or [])[:50],
            "version": 1,
        }
        out.append(_canonical_order(item))
    return out


def _ingest_ab_tady_37(path: Path) -> list[dict]:
    """Load exercises_ab_tady_37*.json and yield PracticeItems (content_type breath_regulation or from payload)."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    exercises = raw.get("exercises") if isinstance(raw.get("exercises"), list) else raw.get("items") or []
    if not exercises and isinstance(raw, list):
        exercises = raw
    out = []
    for i, ex in enumerate(exercises):
        if isinstance(ex, str):
            continue
        ex_id = ex.get("id") or ex.get("exercise_id") or f"ab37_{i+1:03d}"
        practice_id = f"ab37_breath_regulation_{i+1:02d}"
        duration = int(ex.get("duration_seconds") or ex.get("duration") or 120)
        text = (ex.get("text") or ex.get("body") or ex.get("script") or "").strip()
        if not text or len(text) < 50:
            continue
        item = {
            "practice_id": practice_id,
            "source": "ab_tady_37",
            "content_type": "breath_regulation",
            "duration_seconds": max(30, min(1200, duration)),
            "intensity_band": 3,
            "text": text,
            "blocks": {"setup": None, "instruction": None, "prompt": None, "close": None},
            "allowed_personas": [],
            "allowed_topics": [],
            "angle_affinity": [],
            "tags": list(ex.get("tags") or [])[:50],
            "version": 1,
        }
        out.append(_canonical_order(item))
    return out


CONTENT_TYPE_FROM_FILENAME = {
    "sensory_grounding_library_34.json": "sensory_grounding",
    "gratitude_practices_library_34.json": "gratitude_practices",
    "integration_bridges_library_34.json": "integration_bridges",
    "self_inquiry_library_34.json": "self_inquiry",
    "meditations_library_34.json": "meditations",
    "affirmations_library_34.json": "affirmations",
    "reflections_library_34.json": "reflections",
    "thought_experiments_library_34.json": "thought_experiments",
    "body_awareness_library_34.json": "body_awareness",
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest practice libraries from inbox to raw JSONL")
    ap.add_argument("--input-dir", type=Path, default=Path("SOURCE_OF_TRUTH/practice_library/inbox"), help="Inbox directory")
    ap.add_argument("--output-raw", type=Path, default=Path("SOURCE_OF_TRUTH/practice_library/tmp/raw_practice_items.jsonl"), help="Output raw JSONL")
    args = ap.parse_args()
    input_dir = args.input_dir
    output_raw = args.output_raw

    input_dir = input_dir.resolve()
    output_raw = output_raw.resolve()
    output_raw.parent.mkdir(parents=True, exist_ok=True)

    all_items: list[dict] = []
    seen_ids: set[str] = set()

    for f in sorted(input_dir.glob("*.json")):
        name = f.name
        if "library_34" in name and name in CONTENT_TYPE_FROM_FILENAME:
            content_type = CONTENT_TYPE_FROM_FILENAME[name]
            items = _ingest_library_34(f, content_type)
            for it in items:
                if it["practice_id"] in seen_ids:
                    it["practice_id"] = f"{it['practice_id']}_{len(seen_ids)}"
                seen_ids.add(it["practice_id"])
                all_items.append(it)
        elif "ab_tady_37" in name or "exercises_ab_tady" in name or name.startswith("exercises_") and "37" in name:
            items = _ingest_ab_tady_37(f)
            for it in items:
                if it["practice_id"] in seen_ids:
                    it["practice_id"] = f"ab37_breath_regulation_{len(seen_ids):02d}"
                seen_ids.add(it["practice_id"])
                all_items.append(it)

    all_items.sort(key=lambda x: (x["content_type"], x["practice_id"]))

    with open(output_raw, "w", encoding="utf-8") as out:
        for item in all_items:
            out.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote {len(all_items)} practice items to {output_raw}")


if __name__ == "__main__":
    main()
