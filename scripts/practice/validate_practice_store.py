"""
Validate practice store JSONL: schema, enums, uniqueness, optional stats.
CI gate: exit non-zero on any failure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import defaultdict

try:
    import yaml
except ImportError:
    yaml = None


def _load_validation_config(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate practice store")
    ap.add_argument("--input", type=Path, required=True, help="store/practice_items.jsonl")
    ap.add_argument("--validation-config", type=Path, default=Path("config/practice/validation.yaml"))
    args = ap.parse_args()
    cfg = _load_validation_config(args.validation_config.resolve())
    required = set(cfg.get("required_top_level_fields") or ["practice_id", "source", "content_type", "duration_seconds", "text"])
    enums = cfg.get("enums") or {}
    duration = cfg.get("duration_seconds") or {}
    d_min, d_max = duration.get("min", 30), duration.get("max", 1200)
    banned = cfg.get("banned_phrases") or []

    seen_ids = set()
    by_type = defaultdict(int)
    total = 0
    failed = False

    with open(args.input, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"ERROR line {i+1}: invalid JSON: {e}")
                failed = True
                continue
            total += 1
            for r in required:
                if r not in item:
                    print(f"ERROR {item.get('practice_id', i)}: missing field {r}")
                    failed = True
            pid = item.get("practice_id")
            if pid in seen_ids:
                print(f"ERROR: duplicate practice_id {pid}")
                failed = True
            seen_ids.add(pid)
            if enums.get("source") and item.get("source") not in enums["source"]:
                print(f"ERROR {pid}: invalid source {item.get('source')}")
                failed = True
            if enums.get("content_type") and item.get("content_type") not in enums["content_type"]:
                print(f"ERROR {pid}: invalid content_type {item.get('content_type')}")
                failed = True
            dur = item.get("duration_seconds")
            if dur is not None and (dur < d_min or dur > d_max):
                print(f"ERROR {pid}: duration_seconds {dur} out of range [{d_min},{d_max}]")
                failed = True
            text = (item.get("text") or "").lower()
            for phrase in banned:
                if phrase.lower() in text:
                    print(f"ERROR {pid}: banned phrase '{phrase}'")
                    failed = True
            by_type[item.get("content_type", "?")] += 1

    print(f"Total items: {total}")
    print("By content_type:", dict(by_type))
    if failed:
        raise SystemExit(1)
    print("Validation passed.")


if __name__ == "__main__":
    main()
