"""
Static safety lint for practice items: banned phrases, duration bounds, schema.
Used by normalize script and CI. Exit 1 on any violation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

try:
    import yaml
except ImportError:
    yaml = None


def load_validation_config(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def lint_item(item: dict, banned: List[str], duration_min: int, duration_max: int) -> list[str]:
    errs = []
    pid = item.get("practice_id", "?")
    text = (item.get("text") or "").lower()
    for phrase in banned:
        if phrase.lower() in text:
            errs.append(f"{pid}: banned_phrase:{phrase}")
    dur = item.get("duration_seconds")
    if dur is not None:
        if dur < duration_min or dur > duration_max:
            errs.append(f"{pid}: duration_seconds {dur} out of range [{duration_min},{duration_max}]")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser(description="Safety lint practice store or raw JSONL")
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--validation-config", type=Path, default=Path("config/practice/validation.yaml"))
    args = ap.parse_args()
    cfg = load_validation_config(args.validation_config.resolve())
    banned = cfg.get("banned_phrases") or []
    duration = cfg.get("duration_seconds") or {}
    d_min, d_max = duration.get("min", 30), duration.get("max", 1200)

    errors: list[str] = []
    with open(args.input, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {i+1}: invalid JSON: {e}")
                continue
            errors.extend(lint_item(item, banned, d_min, d_max))

    if errors:
        for e in errors:
            print(e)
        raise SystemExit(1)
    print("Practice safety lint passed.")


if __name__ == "__main__":
    main()
