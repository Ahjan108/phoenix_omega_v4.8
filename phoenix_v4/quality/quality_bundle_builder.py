#!/usr/bin/env python3
"""
phoenix_v4/quality/quality_bundle_builder.py

Build a single, schema-validated Ops artifact per book: runs transformation_heatmap,
memorable_line_detector, marketing_assets_from_lines (in-process), computes CSI,
writes artifacts/ops/book_quality_bundle_<book_id>_<YYYYMMDD>.json, validates, exits 0/1/2.

Exit: 0 PASS, 1 FAIL, 2 WARN. --fail-on-warn makes WARN → 1.

Usage:
  PYTHONPATH=. python3 -m phoenix_v4.quality.quality_bundle_builder \
    --rendered-text artifacts/rendered/book_001/book.txt \
    --compiled-plan artifacts/book_001.plan.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from phoenix_v4.quality.base import EXIT_FAIL, EXIT_PASS, EXIT_WARN, status_to_exit_code
from phoenix_v4.quality.transformation_heatmap import load_from_file as heatmap_load_from_file
from phoenix_v4.quality.transformation_heatmap import run_heatmap_from_path
from phoenix_v4.quality.memorable_line_detector import (
    load_chapters_from_rendered_file,
    detect_lines,
)
from phoenix_v4.quality.marketing_assets_from_lines import generate_assets

# CSI weights (sum = 1.0)
CSI_WEIGHTS = {
    "transformation": 0.30,
    "ending_strength": 0.25,
    "memorable_lines": 0.20,
    "quote_density": 0.15,
    "cta_fitness": 0.10,
}

CSI_BANDS = [(90, "A"), (80, "B"), (70, "C"), (60, "D")]
FAIL_ENDING_THRESHOLD = 55
FAIL_TRANSFORMATION_THRESHOLD = 55
WARN_CSI_THRESHOLD = 75

CTA_PATTERNS = [
    r"\bnext step\b",
    r"\btry this\b",
    r"\bstart (with|by)\b",
    r"\bdo this\b",
]
CTA_ANTI_SALESY = [r"\bbuy now\b", r"\blimited time\b", r"\bact now\b", r"https?://"]


def load_plan_metadata(compiled_plan_path: Path) -> Dict[str, Any]:
    """Extract book_id, plan_id, arc_id, teacher_id, brand_id, persona_id, topic_id."""
    if not compiled_plan_path.exists():
        return {}
    try:
        data = json.loads(compiled_plan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    stem = compiled_plan_path.stem
    if stem.endswith(".plan"):
        stem = stem[: -len(".plan")]
    book_id = data.get("book_id") or data.get("plan_id") or data.get("id") or stem
    return {
        "book_id": book_id,
        "plan_id": data.get("plan_id") or data.get("book_id") or "",
        "arc_id": data.get("arc_id") or "",
        "teacher_id": data.get("teacher_id"),
        "brand_id": data.get("brand_id"),
        "persona_id": data.get("persona_id"),
        "topic_id": data.get("topic_id"),
    }


def run_transformation(rendered_text_path: Path) -> dict:
    """Run transformation heatmap from rendered text; return bundle-shaped tool result."""
    return run_heatmap_from_path(rendered_text_path)


def run_memorable_lines(rendered_text_path: Path) -> Tuple[dict, dict]:
    """Run memorable line detector; return (bundle-shaped tool result, raw detect_lines dict for marketing)."""
    book_id, chapters = load_chapters_from_rendered_file(rendered_text_path)
    raw = detect_lines(book_id, chapters, min_score=3.0, max_lines=80)
    total_words = raw.get("total_words", 1)
    candidates = raw.get("candidates", [])
    memorable_line_count = len(candidates)
    strong_quote_count = sum(1 for c in candidates if (c.get("score") or 0) >= 5.0)
    quote_density_per_1k_words = round(raw.get("highlight_density_per_1000_words", 0.0), 3)
    lines = []
    for c in candidates:
        sc = c.get("score", 0)
        strength = "great" if sc >= 6.0 else ("good" if sc >= 4.0 else "ok")
        lines.append({
            "text": c.get("text", ""),
            "strength": strength,
            "chapter_index": c.get("chapter_index", 0),
            "tags": c.get("tags", []),
        })
    tool_result = {
        "status": "pass",
        "metrics": {
            "memorable_line_count": memorable_line_count,
            "strong_quote_count": strong_quote_count,
            "quote_density_per_1k_words": quote_density_per_1k_words,
        },
        "lines": lines,
    }
    return tool_result, raw


def run_marketing_assets(memorable_raw: dict, plan_meta: Dict[str, Any], top_n: int = 25) -> dict:
    """Generate marketing assets from memorable-line raw dict; return bundle-shaped tool result."""
    brand = str(plan_meta.get("brand_id") or "phoenix")
    topic = str(plan_meta.get("topic_id") or "topic")
    persona = str(plan_meta.get("persona_id") or "persona")
    return generate_assets(memorable_raw, brand, topic, persona, top_n=top_n)


def compute_cta_fitness(rendered_text: str) -> float:
    """Deterministic CTA heuristic 0–100. Penalize missing CTA, salesy, vague."""
    text = (rendered_text or "").lower()
    score = 100.0
    has_cta = any(re.search(p, text, re.IGNORECASE) for p in CTA_PATTERNS)
    if not has_cta:
        score -= 40
    for p in CTA_ANTI_SALESY:
        if re.search(p, text, re.IGNORECASE):
            score -= 30
            break
    if len(text) > 500 and not has_cta:
        score -= 20
    return max(0.0, min(100.0, score))


def compute_csi(
    transformation: dict,
    memorable: dict,
    marketing: dict,
    rendered_text: str,
    num_chapters: int = 1,
) -> dict:
    """
    Compute Creative Strength Index (0–100), band, components, weights, notes.
    Deterministic; no LLM.
    """
    components: Dict[str, float] = {}
    notes: List[str] = []

    # Ending strength (0–100)
    end_score = transformation.get("metrics", {}).get("ending_strength_score", 0.0)
    components["ending_strength"] = end_score * 100.0

    # Transformation (0–100): weighted counts normalized by chapters
    rec = transformation.get("metrics", {}).get("recognition_count", 0)
    ref = transformation.get("metrics", {}).get("reframe_count", 0)
    rel = transformation.get("metrics", {}).get("relief_count", 0)
    ident = transformation.get("metrics", {}).get("identity_shift_count", 0)
    raw_trans = 20 * rec + 30 * ref + 20 * rel + 30 * ident
    norm = max(num_chapters, 1) * 10
    components["transformation"] = min(100.0, max(0.0, (raw_trans / norm) * 100.0))

    # Memorable lines (0–100)
    strong = memorable.get("metrics", {}).get("strong_quote_count", 0)
    mem_count = memorable.get("metrics", {}).get("memorable_line_count", 0)
    target = max(num_chapters * 8, 10)
    components["memorable_lines"] = min(100.0, max(0.0, (10 * strong + 4 * mem_count) / target * 100.0))

    # Quote density (0–100) with anti-spam taper
    density = memorable.get("metrics", {}).get("quote_density_per_1k_words", 0.0)
    if density <= 0:
        components["quote_density"] = 0.0
    elif density >= 2.0:
        components["quote_density"] = 85.0
    elif density >= 1.5:
        components["quote_density"] = 95.0
    elif density >= 1.0:
        components["quote_density"] = 85.0
    elif density >= 0.5:
        components["quote_density"] = 60.0
    else:
        components["quote_density"] = density * 120.0

    # CTA fitness (0–100)
    components["cta_fitness"] = compute_cta_fitness(rendered_text)

    # Weighted CSI
    score = sum(CSI_WEIGHTS[k] * components.get(k, 0) for k in CSI_WEIGHTS)
    score = max(0.0, min(100.0, score))

    # Band
    band = "F"
    for thresh, b in CSI_BANDS:
        if score >= thresh:
            band = b
            break

    return {
        "score": round(score, 1),
        "band": band,
        "components": {k: round(components.get(k, 0), 1) for k in components},
        "weights": dict(CSI_WEIGHTS),
        "notes": notes,
    }


def bundle_status(csi: dict) -> Tuple[str, List[str], List[str]]:
    """Return (status, warnings, errors) from CSI and thresholds."""
    warnings: List[str] = []
    errors: List[str] = []
    comp = csi.get("components", {})
    score = csi.get("score", 0)

    if (comp.get("ending_strength", 0) or 0) < FAIL_ENDING_THRESHOLD:
        errors.append("ending_strength below minimum (55)")
    if (comp.get("transformation", 0) or 0) < FAIL_TRANSFORMATION_THRESHOLD:
        errors.append("transformation below minimum (55)")
    if score < WARN_CSI_THRESHOLD and not errors:
        warnings.append(f"CSI {score} below recommend threshold (75)")

    if errors:
        status = "fail"
    elif warnings:
        status = "warn"
    else:
        status = "pass"
    return status, warnings, errors


def write_bundle(bundle: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")


def validate_bundle(out_path: Path, schema_path: Path) -> List[str]:
    """Validate bundle JSON against schema. Return list of error messages."""
    errors: List[str] = []
    try:
        import jsonschema
        Validator = getattr(jsonschema, "Draft202012Validator", None) or getattr(jsonschema, "Draft7Validator", None)
        if not Validator:
            return ["jsonschema Draft202012 or Draft7 not available"]
    except ImportError:
        return ["jsonschema not installed. pip install jsonschema"]

    if not schema_path.exists():
        return [f"Schema not found: {schema_path}"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"Invalid schema: {e}"]
    try:
        data = json.loads(out_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"Invalid JSON: {e}"]

    validator = Validator(schema)
    for err in validator.iter_errors(data):
        path_str = ".".join(str(p) for p in err.path) if err.path else "(root)"
        errors.append(f"{path_str}: {err.message}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Build book quality bundle (transformation + memorable + marketing + CSI)")
    ap.add_argument("--rendered-text", type=Path, required=True, help="Rendered Stage 6 .txt")
    ap.add_argument("--compiled-plan", type=Path, required=True, help="Compiled plan JSON for metadata")
    ap.add_argument("--atoms-root", type=Path, default=None, help="Atoms root for provenance (optional)")
    ap.add_argument("--out-dir", type=Path, default=None, help="Output directory (default artifacts/ops)")
    ap.add_argument("--schema", type=Path, default=None, help="Bundle schema path")
    ap.add_argument("--date", type=str, default=None, help="YYYYMMDD (default today)")
    ap.add_argument("--fail-on-warn", action="store_true", help="Exit 1 on WARN")
    ap.add_argument("--tool-config-fingerprint", type=str, default=None, help="Optional sha256 of config")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing bundle file")
    args = ap.parse_args()

    rendered_path = args.rendered_text
    plan_path = args.compiled_plan
    if not rendered_path.exists():
        print(f"Error: rendered text not found: {rendered_path}", file=sys.stderr)
        return EXIT_FAIL
    if not plan_path.exists():
        print(f"Error: compiled plan not found: {plan_path}", file=sys.stderr)
        return EXIT_FAIL

    plan_meta = load_plan_metadata(plan_path)
    book_id = plan_meta.get("book_id", rendered_path.stem)
    date_str = args.date or datetime.now(timezone.utc).strftime("%Y%m%d")
    out_dir = args.out_dir or REPO_ROOT / "artifacts" / "ops"
    schema_path = args.schema or REPO_ROOT / "schemas" / "book_quality_bundle_v1.schema.json"

    # Run tools (all from rendered text; no hidden rendering)
    try:
        transformation = run_transformation(rendered_path)
        print("  transformation_heatmap:", transformation.get("status", "?"))
    except Exception as e:
        print(f"Error: transformation_heatmap failed: {e}", file=sys.stderr)
        return EXIT_FAIL

    try:
        memorable, memorable_raw = run_memorable_lines(rendered_path)
        print("  memorable_line_detector:", memorable.get("status", "?"))
    except Exception as e:
        print(f"Error: memorable_line_detector failed: {e}", file=sys.stderr)
        return EXIT_FAIL

    try:
        marketing = run_marketing_assets(memorable_raw, plan_meta)
        print("  marketing_assets_from_lines:", marketing.get("status", "?"))
    except Exception as e:
        print(f"Error: marketing_assets_from_lines failed: {e}", file=sys.stderr)
        return EXIT_FAIL

    # Rendered text for CTA scan
    rendered_text = rendered_path.read_text(encoding="utf-8", errors="replace")
    num_chapters = len(transformation.get("chapter_signals", []) or [1])

    csi = compute_csi(transformation, memorable, marketing, rendered_text, num_chapters=num_chapters)
    status, warnings, errors = bundle_status(csi)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    bundle_id = hashlib.sha256(f"{book_id}|{plan_meta.get('plan_id') or ''}|{plan_meta.get('arc_id') or ''}|{generated_at}".encode()).hexdigest()[:32]

    inputs: Dict[str, Any] = {
        "rendered_text_path": str(rendered_path.resolve()),
        "compiled_plan_path": str(plan_path.resolve()),
        "atoms_root": str(args.atoms_root.resolve()) if args.atoms_root and args.atoms_root.exists() else None,
    }

    bundle = {
        "schema_version": "1.0",
        "bundle_id": bundle_id,
        "book_id": book_id,
        "plan_id": plan_meta.get("plan_id"),
        "arc_id": plan_meta.get("arc_id"),
        "teacher_id": plan_meta.get("teacher_id"),
        "brand_id": plan_meta.get("brand_id"),
        "persona_id": plan_meta.get("persona_id"),
        "topic_id": plan_meta.get("topic_id"),
        "generated_at": generated_at,
        "inputs": inputs,
        "tool_results": {
            "transformation_heatmap": transformation,
            "memorable_line_detector": memorable,
            "marketing_assets_from_lines": marketing,
        },
        "csi": csi,
        "status": status,
        "warnings": warnings,
        "errors": errors,
    }

    out_path = out_dir / f"book_quality_bundle_{book_id}_{date_str}.json"
    if out_path.exists() and not args.overwrite:
        v = 2
        while (out_dir / f"book_quality_bundle_{book_id}_{date_str}_v{v}.json").exists():
            v += 1
        out_path = out_dir / f"book_quality_bundle_{book_id}_{date_str}_v{v}.json"

    write_bundle(bundle, out_path)
    print(f"  bundle path: {out_path}")

    val_errors = validate_bundle(out_path, schema_path)
    if val_errors:
        print("Validation failed:", file=sys.stderr)
        for e in val_errors:
            print(f"  {e}", file=sys.stderr)
        return EXIT_FAIL
    print("  validation: OK")

    if status == "fail":
        return EXIT_FAIL
    if status == "warn" and args.fail_on_warn:
        return EXIT_FAIL
    if status == "warn":
        return EXIT_WARN
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
