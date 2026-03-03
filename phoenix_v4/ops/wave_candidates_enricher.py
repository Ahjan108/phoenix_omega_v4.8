#!/usr/bin/env python3
"""
phoenix_v4/ops/wave_candidates_enricher.py

Augment wave candidate entries with quality metrics from validated book_quality_bundle
artifacts. Does not recompute quality; only reads bundles. Used before Wave Optimizer.

Exit: 0 success, 1 fatal error, 2 warnings only (e.g. missing bundles but continuing).

Usage:
  PYTHONPATH=. python3 -m phoenix_v4.ops.wave_candidates_enricher \
    --wave-candidates artifacts/waves/wave_01_candidates.json \
    --quality-bundles-dir artifacts/ops \
    --out artifacts/waves/wave_01_candidates_enriched.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _validate_bundle(data: dict, schema_path: Path) -> List[str]:
    """Validate bundle dict against schema. Return list of error messages."""
    errors: List[str] = []
    try:
        import jsonschema
        Validator = getattr(jsonschema, "Draft202012Validator", None) or getattr(jsonschema, "Draft7Validator", None)
        if not Validator:
            return ["jsonschema Draft202012 or Draft7 not available"]
    except ImportError:
        return ["jsonschema not installed"]

    if not schema_path.exists():
        return [f"Schema not found: {schema_path}"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"Invalid schema: {e}"]

    validator = Validator(schema)
    for err in validator.iter_errors(data):
        path_str = ".".join(str(p) for p in err.path) if err.path else "(root)"
        errors.append(f"{path_str}: {err.message}")
    return errors


def discover_bundles(bundles_dir: Path) -> Dict[str, Path]:
    """
    Scan bundles_dir for book_quality_bundle_<book_id>_*.json.
    For each book_id, pick latest by date suffix then by _v2/_v3.
    Return { book_id: path }.
    """
    pattern = re.compile(r"^book_quality_bundle_(.+?)_(\d{8})(?:_v(\d+))?\.json$")
    by_book: Dict[str, List[Tuple[str, int, int, Path]]] = {}  # book_id -> [(date_str, v, -, path)]
    if not bundles_dir.exists():
        return {}

    for f in bundles_dir.glob("book_quality_bundle_*.json"):
        m = pattern.match(f.name)
        if not m:
            continue
        book_id, date_str, v_str = m.group(1), m.group(2), m.group(3)
        v = int(v_str) if v_str else 1
        key = (date_str, v)
        by_book.setdefault(book_id, []).append((date_str, v, 0, f))

    out: Dict[str, Path] = {}
    for book_id, candidates in by_book.items():
        # Sort by date desc, then v desc; take first
        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        out[book_id] = candidates[0][3]
    return out


def load_and_validate_bundles(
    bundles_dir: Path,
    schema_path: Path,
) -> Tuple[Dict[str, dict], List[str]]:
    """
    Discover bundles, load each, validate. Return (bundles_by_book_id, errors for missing/invalid).
    """
    bundles_by_book_id: Dict[str, dict] = {}
    errors: List[str] = []
    discovered = discover_bundles(bundles_dir)
    for book_id, path in discovered.items():
        data = _load_json(path)
        if not data:
            errors.append(f"Could not load bundle: {path}")
            continue
        val_errors = _validate_bundle(data, schema_path)
        if val_errors:
            errors.append(f"Bundle invalid for {book_id} ({path}): {'; '.join(val_errors[:2])}")
            continue
        bundles_by_book_id[book_id] = data
    return bundles_by_book_id, errors


def enrich_candidate(candidate: dict, bundle: Optional[dict], warn_on_missing: bool) -> dict:
    """Return candidate with quality field added (copy; do not mutate input)."""
    out = dict(candidate)
    if bundle:
        csi = bundle.get("csi") or {}
        comp = csi.get("components") or {}
        out["quality"] = {
            "csi_score": csi.get("score"),
            "csi_band": csi.get("band"),
            "ending_strength": comp.get("ending_strength"),
            "transformation": comp.get("transformation"),
            "memorable_lines": comp.get("memorable_lines"),
            "quote_density": comp.get("quote_density"),
            "cta_fitness": comp.get("cta_fitness"),
            "status": bundle.get("status"),
        }
        # Diversity proxy: line_type_buckets from memorable lines if tags present
        lines = (bundle.get("tool_results") or {}).get("memorable_line_detector") or {}
        line_list = lines.get("lines") or []
        buckets: Dict[str, int] = {}
        for item in line_list:
            for tag in (item.get("tags") or []):
                tag_lower = tag.lower()
                if tag_lower in ("identity", "reframe", "relief", "directive"):
                    buckets[tag_lower] = buckets.get(tag_lower, 0) + 1
        out["quality"]["line_type_buckets"] = buckets
    elif warn_on_missing:
        out["quality"] = {"status": "missing"}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Enrich wave candidates with quality metrics from bundle artifacts")
    ap.add_argument("--wave-candidates", type=Path, required=True, help="Wave candidates JSON path")
    ap.add_argument("--quality-bundles-dir", type=Path, required=True, help="Directory of book_quality_bundle_*.json")
    ap.add_argument("--schema-registry", type=Path, default=None, help="Ops schema registry YAML (unused for now)")
    ap.add_argument("--bundle-schema", type=Path, default=None, help="Bundle JSON schema path")
    ap.add_argument("--out", type=Path, default=None, help="Output path (default: overwrite input)")
    ap.add_argument("--require-quality-pass", action="store_true", help="Exclude candidates with status=fail")
    ap.add_argument("--min-ending-strength", type=float, default=None, help="Exclude books below this (0-100)")
    ap.add_argument("--warn-on-missing", action="store_true", help="Inject quality.status=missing when bundle missing")
    args = ap.parse_args()

    schema_path = args.bundle_schema or REPO_ROOT / "schemas" / "book_quality_bundle_v1.schema.json"
    candidates_path = args.wave_candidates
    if not candidates_path.exists():
        print(f"Error: wave-candidates not found: {candidates_path}", file=sys.stderr)
        return 1

    data = _load_json(candidates_path)
    if data is None:
        print("Error: invalid or unreadable wave candidates JSON", file=sys.stderr)
        return 1

    if isinstance(data, list):
        candidates = data
    else:
        candidates = data.get("candidates") or data.get("items") or []
    if not isinstance(candidates, list):
        print("Error: no candidates list in JSON", file=sys.stderr)
        return 1

    bundles_by_book_id, load_errors = load_and_validate_bundles(args.quality_bundles_dir, schema_path)
    for e in load_errors:
        print(f"Warning: {e}", file=sys.stderr)

    loaded_count = len(bundles_by_book_id)
    print(f"Loaded bundles: {loaded_count}")

    enriched: List[dict] = []
    missing = 0
    for c in candidates:
        book_id = c.get("book_id")
        if not book_id:
            enriched.append(dict(c))
            continue
        bundle = bundles_by_book_id.get(str(book_id))
        if bundle is None:
            missing += 1
        enriched.append(enrich_candidate(c, bundle, args.warn_on_missing))

    print(f"Candidates: {len(candidates)}")
    print(f"Missing quality: {missing}")

    # Optional filters
    excluded_fail = 0
    excluded_ending = 0
    if args.require_quality_pass or args.min_ending_strength is not None:
        filtered: List[dict] = []
        for c in enriched:
            q = c.get("quality") or {}
            status = q.get("status")
            if args.require_quality_pass and status == "fail":
                excluded_fail += 1
                continue
            if args.min_ending_strength is not None:
                es = q.get("ending_strength")
                if es is not None and float(es) < args.min_ending_strength:
                    excluded_ending += 1
                    continue
            filtered.append(c)
        enriched = filtered
        print(f"Excluded (fail): {excluded_fail}")
        print(f"Excluded (ending<{args.min_ending_strength}): {excluded_ending}")

    print(f"Final candidates: {len(enriched)}")

    out_path = args.out or candidates_path
    if isinstance(data, list):
        out_data = {"candidates": enriched}
    else:
        out_data = {k: v for k, v in data.items() if k not in ("candidates", "items")}
        out_data["candidates"] = enriched

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written: {out_path}")

    if load_errors or missing:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
