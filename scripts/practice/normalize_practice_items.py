"""
Normalize raw practice items: whitespace, safety lint, duration bounds.
Outputs validated practice_items.jsonl to store.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def _load_validation_config(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _safety_lint(text: str, banned: list[str]) -> list[str]:
    """Return list of violations (banned phrases found)."""
    t = text.lower()
    errs = []
    for phrase in banned:
        if phrase.lower() in t:
            errs.append(f"banned_phrase:{phrase}")
    return errs


def _normalize_text(text: str) -> str:
    """Whitespace normalization only."""
    if not text:
        return ""
    return " ".join(text.split())


def main() -> None:
    ap = argparse.ArgumentParser(description="Normalize and lint practice items")
    ap.add_argument("--input", type=Path, required=True, help="Raw JSONL path")
    ap.add_argument("--output", type=Path, required=True, help="Output store JSONL path")
    ap.add_argument("--validation-config", type=Path, default=Path("config/practice/validation.yaml"))
    args = ap.parse_args()
    cfg = _load_validation_config(args.validation_config.resolve())
    banned = cfg.get("banned_phrases") or []
    duration_min = (cfg.get("duration_seconds") or {}).get("min", 30)
    duration_max = (cfg.get("duration_seconds") or {}).get("max", 1200)
    text_min = (cfg.get("text") or {}).get("min_chars", 120)

    out_path = args.output.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    out_items = []
    errors = []

    with open(args.input, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"json_error:{e}")
                continue
            pid = item.get("practice_id")
            if not pid:
                errors.append("missing practice_id")
                continue
            if pid in seen:
                errors.append(f"duplicate_id:{pid}")
                continue
            seen.add(pid)
            text = _normalize_text(item.get("text") or "")
            if len(text) < text_min:
                errors.append(f"{pid}:text_too_short:{len(text)}")
                continue
            item["text"] = text
            item["duration_seconds"] = max(duration_min, min(duration_max, int(item.get("duration_seconds") or 90)))
            item["intensity_band"] = max(1, min(5, int(item.get("intensity_band") or 3)))
            errs = _safety_lint(text, banned)
            if errs:
                errors.extend([f"{pid}:{e}" for e in errs])
                continue
            out_items.append(item)

    if errors:
        for e in errors[:50]:
            print(f"Validation: {e}")
        if len(errors) > 50:
            print(f"... and {len(errors) - 50} more")
        raise SystemExit(1)
    with open(out_path, "w", encoding="utf-8") as out:
        for item in out_items:
            out.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Wrote {len(out_items)} practice items to {out_path}")


if __name__ == "__main__":
    main()
