#!/usr/bin/env python3
"""
Validate asset store against manifest: file exists, non-empty; format-specific rules.
Authority: V4 Freebies + Immersion Ecosystem plan §3.4.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Validate asset store against manifest")
    ap.add_argument("--store", type=Path, required=True, help="Asset store root")
    ap.add_argument("--manifest", type=Path, required=True, help="manifest.jsonl path")
    ap.add_argument("--formats", type=str, default=None, help="Comma-separated formats to validate (e.g. html,pdf). Default: all manifest formats")
    ap.add_argument("--rules", type=Path, default=None, help="Optional validation rules YAML")
    args = ap.parse_args()

    if not args.manifest.exists():
        print(f"Manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    rules = load_yaml(args.rules) if args.rules else {}
    format_rules = rules.get("validation_rules") or rules.get("format_rules") or {}

    manifest_rows: list[dict] = []
    with open(args.manifest, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            manifest_rows.append(json.loads(line))

    formats_wanted: set[str] | None = None
    if args.formats:
        formats_wanted = {f.strip().lower() for f in args.formats.split(",") if f.strip()}

    errors: list[str] = []
    for row in manifest_rows:
        topic = row.get("topic") or ""
        persona = row.get("persona") or ""
        freebie_id = row.get("freebie_id") or ""
        fmt = (row.get("format") or "html").strip().lower()
        if formats_wanted is not None and fmt not in formats_wanted:
            continue
        ext = "html" if fmt == "html" else "pdf" if fmt == "pdf" else "epub" if fmt == "epub" else "mp3"
        path = args.store / fmt / topic / persona / f"{freebie_id}.{ext}"
        if not path.exists():
            errors.append(f"Missing: {path}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"Empty: {path}")
            continue
        # Format-specific
        if fmt == "mp3":
            r = format_rules.get("mp3") or {}
            min_sec = r.get("duration_min_seconds")
            max_sec = r.get("duration_max_seconds")
            min_mb = r.get("file_size_min_mb")
            if min_mb and path.stat().st_size < min_mb * 1024 * 1024:
                errors.append(f"Too small: {path} (min {min_mb} MB)")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("Asset store validation passed.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
