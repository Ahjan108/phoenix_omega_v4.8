#!/usr/bin/env python3
"""
Check whether a metadata candidate file passes the promotion gates.
Gate: delta thresholds from config/research_metadata/promotion_criteria.yaml.

Usage:
  python scripts/research/check_metadata_promotion_gate.py \
    --candidates artifacts/ei_v2/metadata_candidates/20260306_kb_derived.json

Exit codes: 0=PASS, 1=FAIL, 2=ERROR
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
CRITERIA_PATH = REPO_ROOT / "config" / "research_metadata" / "promotion_criteria.yaml"


def _load_criteria(criteria_path: Path) -> dict:
    if not criteria_path.exists() or yaml is None:
        logger.warning("Promotion criteria not found at %s; using defaults", criteria_path)
        return {
            "max_terms_per_patch": 20,
            "max_patches_per_run": 30,
            "min_kb_entries_used": 5,
            "require_shadow_status": True,
        }
    with open(criteria_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_candidates(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Candidates file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def check_gate(candidates: dict, criteria: dict) -> tuple[bool, list[str]]:
    """Run all gates. Returns (passed, list of failure reasons)."""
    failures = []

    # Gate 1: status must be shadow_pending
    if criteria.get("require_shadow_status", True):
        if candidates.get("status") != "shadow_pending":
            failures.append(f"status must be 'shadow_pending', got '{candidates.get('status')}'")

    # Gate 2: KB entries used
    min_entries = int(criteria.get("min_kb_entries_used") or 5)
    used = int(candidates.get("kb_entries_used") or 0)
    if used < min_entries:
        failures.append(f"kb_entries_used={used} < min_kb_entries_used={min_entries}")

    # Gate 3: patch count ceiling
    max_patches = int(criteria.get("max_patches_per_run") or 30)
    patch_count = int(candidates.get("patch_count") or 0)
    if patch_count > max_patches:
        failures.append(f"patch_count={patch_count} > max_patches_per_run={max_patches}")

    # Gate 4: terms per patch ceiling
    max_terms = int(criteria.get("max_terms_per_patch") or 20)
    for patch in candidates.get("patches") or []:
        terms = patch.get("add_terms") or patch.get("add_entries") or []
        if len(terms) > max_terms:
            failures.append(
                f"patch '{patch.get('patch_type')}→{patch.get('target')}' "
                f"has {len(terms)} terms > max {max_terms}"
            )

    # Gate 5: no unknown patch types
    known_types = {"topic_vocabulary_add", "persona_vocabulary_add", "invisible_scripts_add"}
    for patch in candidates.get("patches") or []:
        pt = patch.get("patch_type")
        if pt and pt not in known_types:
            failures.append(f"Unknown patch_type: {pt}")

    # Gate 6: confidence threshold
    min_conf = float(criteria.get("min_candidate_confidence") or 0.0)
    if min_conf > 0 and float(candidates.get("min_confidence") or 0) < min_conf:
        failures.append(
            f"candidate min_confidence={candidates.get('min_confidence')} < required {min_conf}"
        )

    return len(failures) == 0, failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Check metadata candidate promotion gate")
    ap.add_argument("--candidates", required=True, help="Path to candidates JSON file")
    ap.add_argument("--criteria", default=None, help="Path to promotion criteria YAML (default: config/research_metadata/promotion_criteria.yaml)")
    args = ap.parse_args()

    criteria_path = Path(args.criteria) if args.criteria else CRITERIA_PATH
    criteria = _load_criteria(criteria_path)

    try:
        candidates = _load_candidates(Path(args.candidates))
    except Exception as e:
        logger.error("Failed to load candidates: %s", e)
        return 2

    passed, failures = check_gate(candidates, criteria)

    if passed:
        print(f"✅ GATE PASS — candidates from {args.candidates} are promotion-ready")
        print(f"   {candidates.get('patch_count')} patches from {candidates.get('kb_entries_used')} KB entries")
        print(f"   Next: python scripts/research/promote_metadata_candidates.py --candidates {args.candidates}")
        return 0
    else:
        print(f"❌ GATE FAIL — {len(failures)} issue(s):")
        for f in failures:
            print(f"   - {f}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
