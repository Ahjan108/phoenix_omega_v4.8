#!/usr/bin/env python3
"""
Add duplication_safety to an existing book_quality_bundle using the memorable line registry snapshot.

Keeps the bundle builder pure (local signals only); this step adds a global, registry-based
component. Optional: use --registry-snapshot to point at snapshot path.

Usage:
  PYTHONPATH=. python3 -m phoenix_v4.ops.quality_bundle_postprocessor --bundle artifacts/ops/book_quality_bundle_book_001_20260225.json
  PYTHONPATH=. python3 -m phoenix_v4.ops.quality_bundle_postprocessor --bundle artifacts/ops/book_quality_bundle_book_001_20260225.json --registry-snapshot artifacts/ops/memorable_line_registry_snapshot_v1.json --out artifacts/ops/book_quality_bundle_book_001_20260225_v2.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from phoenix_v4.ops.memorable_line_registry import (
    normalize_line,
    line_hash,
    load_policy,
)

# Weights when duplication_safety is present (sum = 1.0)
CSI_WEIGHTS_WITH_DUP = {
    "transformation": 0.27,
    "ending_strength": 0.23,
    "memorable_lines": 0.18,
    "quote_density": 0.12,
    "cta_fitness": 0.10,
    "duplication_safety": 0.10,
}
CSI_BANDS = [(90, "A"), (80, "B"), (70, "C"), (60, "D")]


def _load_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def compute_duplication_safety(
    bundle: Dict[str, Any],
    snapshot: Dict[str, Any],
    max_global: int = 2,
) -> float:
    """
    Compute duplication_safety 0–100. Start at 100; subtract:
    -40 if any "great" line exceeds global threshold, -20 per extra collision (capped),
    -10 if within-book repetition (same normalized line appears >1 in this book).
    """
    score = 100.0
    tool = (bundle.get("tool_results") or {}).get("memorable_line_detector") or {}
    lines = tool.get("lines") or []
    by_hash: Dict[str, List[str]] = {}
    great_hashes: List[str] = []
    for item in lines:
        text = (item.get("text") or "").strip()
        if not text:
            continue
        norm = normalize_line(text)
        if not norm:
            continue
        h = line_hash(norm)
        by_hash.setdefault(h, []).append(norm)
        if (item.get("strength") or "").lower() == "great":
            great_hashes.append(h)

    snapshot_index = {ent["line_hash"]: ent for ent in (snapshot.get("lines") or [])}

    # Within-book repetition: same hash multiple times
    within_book_rep = sum(1 for v in by_hash.values() if len(v) > 1)
    if within_book_rep > 0:
        score -= 10

    # Global collisions for "great" lines
    collision_penalty = 0
    for h in great_hashes:
        ent = snapshot_index.get(h)
        occ = int(ent.get("occurrence_count", 0)) if ent else 0
        if occ > max_global:
            collision_penalty += 40 + min(60, 20 * (occ - max_global))
    score -= collision_penalty

    return max(0.0, min(100.0, score))


def main() -> int:
    ap = argparse.ArgumentParser(description="Add duplication_safety to bundle from registry snapshot")
    ap.add_argument("--bundle", type=Path, required=True, help="book_quality_bundle_*.json path")
    ap.add_argument("--registry-snapshot", type=Path, default=None, help="Default: artifacts/ops/memorable_line_registry_snapshot_v1.json")
    ap.add_argument("--out", type=Path, default=None, help="Output path (default: overwrite bundle)")
    ap.add_argument("--ops-dir", type=Path, default=None)
    args = ap.parse_args()

    bundle_path = args.bundle
    if not bundle_path.exists():
        print(f"Error: bundle not found: {bundle_path}", file=sys.stderr)
        return 1

    ops_dir = args.ops_dir or REPO_ROOT / "artifacts" / "ops"
    snapshot_path = args.registry_snapshot or ops_dir / "memorable_line_registry_snapshot_v1.json"
    bundle = _load_json(bundle_path)
    if not bundle:
        print("Error: invalid bundle JSON", file=sys.stderr)
        return 1

    snapshot = _load_json(snapshot_path) if snapshot_path.exists() else {"lines": []}
    if not snapshot:
        snapshot = {"lines": []}
    policy = load_policy()
    max_global = int(policy.get("max_occurrences_global", 2))

    dup_safety = round(compute_duplication_safety(bundle, snapshot, max_global), 1)
    csi = bundle.get("csi") or {}
    comp = dict(csi.get("components") or {})
    comp["duplication_safety"] = dup_safety
    csi["components"] = comp
    csi["weights"] = CSI_WEIGHTS_WITH_DUP
    new_score = sum(CSI_WEIGHTS_WITH_DUP.get(k, 0) * comp.get(k, 0) for k in CSI_WEIGHTS_WITH_DUP)
    new_score = max(0.0, min(100.0, new_score))
    band = "F"
    for thresh, b in CSI_BANDS:
        if new_score >= thresh:
            band = b
            break
    csi["score"] = round(new_score, 1)
    csi["band"] = band
    bundle["csi"] = csi

    out_path = args.out or bundle_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"duplication_safety={dup_safety}; new CSI={csi['score']} band={band}; written {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
