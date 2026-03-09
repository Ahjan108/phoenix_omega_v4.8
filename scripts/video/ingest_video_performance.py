#!/usr/bin/env python3
"""
Ingest video performance feedback: read video_performance_v1 records (JSON/JSONL or directory),
validate against schemas/video/video_performance_v1.schema.json, write to output path.
No platform API calls — file-in, validate, file-out only.
Usage:
  python scripts/video/ingest_video_performance.py --input performance_records.jsonl --output artifacts/video/performance_feedback/ingested.jsonl
  python scripts/video/ingest_video_performance.py --input-dir data/performance/ --output artifacts/video/performance_feedback/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
SCHEMA_PATH = REPO_ROOT / "schemas" / "video" / "video_performance_v1.schema.json"


def _load_schema() -> dict:
    if not SCHEMA_PATH.exists():
        return {}
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate_record(record: dict, schema: dict) -> list[str]:
    """Simple required-field validation. Returns list of error messages."""
    errors = []
    required = schema.get("required", [])
    for key in required:
        if key not in record:
            errors.append(f"missing required field: {key}")
    props = schema.get("properties", {})
    for key, spec in props.items():
        if key not in record:
            continue
        val = record[key]
        if spec.get("type") == "string":
            if not isinstance(val, str):
                errors.append(f"{key}: expected string")
        elif spec.get("type") == "integer":
            if not isinstance(val, int):
                errors.append(f"{key}: expected integer")
        elif spec.get("type") == "number":
            if not isinstance(val, (int, float)):
                errors.append(f"{key}: expected number")
        elif spec.get("type") == "array":
            if not isinstance(val, list):
                errors.append(f"{key}: expected array")
        if "minimum" in spec and val is not None and val < spec["minimum"]:
            errors.append(f"{key}: below minimum {spec['minimum']}")
        if "maximum" in spec and val is not None and val > spec["maximum"]:
            errors.append(f"{key}: above maximum {spec['maximum']}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest and validate video_performance_v1 records")
    ap.add_argument("--input", help="Input JSON array or JSONL file")
    ap.add_argument("--input-dir", help="Directory of JSON/JSONL files to read")
    ap.add_argument("--output", required=True, help="Output path (file or directory if --input-dir)")
    ap.add_argument("--strict", action="store_true", help="Fail on first validation error")
    args = ap.parse_args()

    schema = _load_schema()
    if not schema:
        print("Warning: schema not found at", SCHEMA_PATH, file=sys.stderr)

    records = []
    if args.input:
        p = Path(args.input)
        if not p.exists():
            print("Error: input file not found:", p, file=sys.stderr)
            return 1
        raw = p.read_text(encoding="utf-8").strip()
        if raw.startswith("["):
            records = json.loads(raw)
        else:
            for line in raw.splitlines():
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    elif args.input_dir:
        inp = Path(args.input_dir)
        if not inp.is_dir():
            print("Error: input-dir not found:", inp, file=sys.stderr)
            return 1
        for f in sorted(inp.glob("*.json")) + sorted(inp.glob("*.jsonl")):
            text = f.read_text(encoding="utf-8").strip()
            if f.suffix == ".jsonl" or (f.suffix == ".json" and not text.startswith("[")):
                for line in text.splitlines():
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            else:
                records.extend(json.loads(text) if text else [])
    else:
        print("Error: provide --input or --input-dir", file=sys.stderr)
        return 1

    validated = []
    errors_all = []
    for i, rec in enumerate(records):
        errs = _validate_record(rec, schema) if schema else []
        if errs:
            errors_all.append((i, rec.get("video_id", "?"), errs))
            if args.strict:
                print("Validation failed at record", i, errs, file=sys.stderr)
                return 1
            continue
        validated.append(rec)

    out_path = Path(args.output)
    if out_path.suffix not in (".json", ".jsonl"):
        out_path = out_path / "ingested.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for rec in validated:
            f.write(json.dumps(rec) + "\n")
    print(f"Wrote {len(validated)} records to {out_path}")

    if errors_all:
        print(f"Validation warnings: {len(errors_all)} records skipped", file=sys.stderr)
        for i, vid, errs in errors_all[:5]:
            print(f"  record {i} video_id={vid}: {errs}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
