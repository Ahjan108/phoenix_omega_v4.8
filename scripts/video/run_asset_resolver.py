#!/usr/bin/env python3
"""
Asset Resolver: ShotPlan + Image Bank index -> resolved assets per shot (shot_id -> asset_id).
Uses config/video/asset_selection_priority.yaml and composition_compat threshold.
If no bank path given, assigns deterministic placeholder asset_ids for testing.
Usage: python scripts/video/run_asset_resolver.py <shot_plan.json> -o <resolved_assets.json> [--bank <bank_index.json>] [--variant-id default]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, load_json, config_snapshot_hash, write_atomically, should_skip_output, REPO_ROOT


def _load_bank(bank_path: Path) -> list[dict]:
    if not bank_path.exists():
        return []
    text = bank_path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        return load_json(bank_path)
    assets = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        assets.append(json.loads(line))
    return assets


def _resolve_shot(shot: dict, assets: list[dict], aspect_key: str, threshold: float) -> str | None:
    intent = shot.get("visual_intent", "")
    for a in assets:
        if a.get("visual_intent") != intent:
            continue
        compat = (a.get("composition_compat") or {}).get(aspect_key)
        if compat is not None and compat >= threshold:
            return a.get("asset_id")
    return None


def run_asset_resolver(shot_plan: dict, bank_path: Path | None, variant_id: str) -> dict:
    priority_config = load_yaml("config/video/asset_selection_priority.yaml")
    threshold = priority_config.get("composition_compat_threshold", 0.5)
    assets = _load_bank(bank_path) if bank_path else []
    aspect_key = "16:9"
    resolved = {}
    for shot in shot_plan.get("shots", []):
        shot_id = shot["shot_id"]
        asset_id = _resolve_shot(shot, assets, aspect_key, threshold) if assets else None
        if not asset_id:
            asset_id = f"asset-{shot_id.replace('shot-', '')}-001"
        resolved[shot_id] = {"asset_id": asset_id}
    return {
        "plan_id": shot_plan["plan_id"],
        "variant_id": variant_id,
        "config_hash": config_snapshot_hash(),
        "resolved": resolved,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve assets for each shot from Image Bank or placeholders")
    ap.add_argument("shot_plan", help="Path to shot_plan.json")
    ap.add_argument("-o", "--out", required=True, help="Output resolved_assets.json path")
    ap.add_argument("--bank", help="Optional path to image bank index (JSON array or JSONL)")
    ap.add_argument("--variant-id", default="default", help="Variant for logging")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists")
    args = ap.parse_args()

    path = Path(args.shot_plan)
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1
    shot_plan = json.loads(path.read_text(encoding="utf-8"))
    bank_path = Path(args.bank) if args.bank else None

    out_path = Path(args.out)
    if should_skip_output(out_path, ["plan_id", "resolved", "config_hash"], args.force, config_snapshot_hash()):
        print(f"Skip (output exists, use --force to overwrite): {out_path}")
        return 0
    result = run_asset_resolver(shot_plan, bank_path, args.variant_id)
    write_atomically(out_path, result)
    print(f"Wrote resolved assets for {len(result['resolved'])} shots to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
