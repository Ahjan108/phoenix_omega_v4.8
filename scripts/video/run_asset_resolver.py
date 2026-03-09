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

from scripts.video._config import load_yaml, load_json, config_snapshot_hash, write_atomically, should_skip_output, REPO_ROOT, PIPELINE_VERSION


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


def _matching_assets(shot: dict, assets: list[dict], aspect_key: str, threshold: float) -> list[str]:
    """Return list of asset_ids that match this shot's intent and compat, in stable order."""
    intent = shot.get("visual_intent", "")
    out = []
    for a in assets:
        if a.get("visual_intent") != intent:
            continue
        compat = (a.get("composition_compat") or {}).get(aspect_key)
        if compat is not None and compat >= threshold:
            aid = a.get("asset_id")
            if aid:
                out.append(aid)
    return out


def _intent_to_slug(visual_intent: str) -> str:
    """Map visual_intent to a short slug for placeholder IDs (e.g. HOOK_VISUAL -> hook_visual)."""
    s = (visual_intent or "generic").strip().lower().replace(" ", "_").replace("-", "_")
    return s if s else "generic"


def run_asset_resolver(
    shot_plan: dict,
    bank_path: Path | None,
    variant_id: str,
    segment_index: dict | None = None,
    allow_placeholders: bool = False,
) -> dict:
    # When segment_index is provided, each shot gets the asset for its segment_id (LLM-derived, script-specific).
    segment_id_to_asset = (segment_index or {}).get("segment_id_to_asset") or {}

    priority_config = load_yaml("config/video/asset_selection_priority.yaml")
    threshold = priority_config.get("composition_compat_threshold", 0.5)
    assets = _load_bank(bank_path) if bank_path else []
    aspect_key = "16:9"
    resolved = {}
    prev_asset_id: str | None = None
    used_asset_ids: set[str] = set()
    intent_count: dict[str, int] = {}
    for shot in shot_plan.get("shots", []):
        shot_id = shot["shot_id"]
        seg_id = shot.get("segment_id", "")
        if segment_id_to_asset and seg_id in segment_id_to_asset:
            asset_id = segment_id_to_asset[seg_id]
            resolved[shot_id] = {"asset_id": asset_id}
            prev_asset_id = asset_id
            continue
        if not assets:
            if not allow_placeholders:
                raise RuntimeError(
                    "Asset resolver strict mode: no image bank assets available and no segment-index mapping."
                )
            slug = _intent_to_slug(shot.get("visual_intent", ""))
            intent_count[slug] = intent_count.get(slug, 0) + 1
            asset_id = f"placeholder_{slug}_{intent_count[slug]:03d}"
        else:
            candidates = _matching_assets(shot, assets, aspect_key, threshold)
            if not candidates:
                if not allow_placeholders:
                    raise RuntimeError(
                        f"Asset resolver strict mode: no compatible assets for shot_id={shot_id}, visual_intent={shot.get('visual_intent','')}"
                    )
                slug = _intent_to_slug(shot.get("visual_intent", ""))
                intent_count[slug] = intent_count.get(slug, 0) + 1
                asset_id = f"placeholder_{slug}_{intent_count[slug]:03d}"
            else:
                # Rule: every clip different — prefer one not used yet, then one != previous
                not_used = [a for a in candidates if a not in used_asset_ids]
                available = not_used or [a for a in candidates if a != prev_asset_id] or candidates
                asset_id = available[0]
            used_asset_ids.add(asset_id)
        resolved[shot_id] = {"asset_id": asset_id}
        prev_asset_id = asset_id
    return {
        "plan_id": shot_plan["plan_id"],
        "variant_id": variant_id,
        "config_hash": config_snapshot_hash(),
        "pipeline_version": PIPELINE_VERSION,
        "resolved": resolved,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve assets for each shot from Image Bank or placeholders")
    ap.add_argument("shot_plan", help="Path to shot_plan.json")
    ap.add_argument("-o", "--out", required=True, help="Output resolved_assets.json path")
    ap.add_argument("--bank", help="Optional path to image bank index (JSON array or JSONL)")
    ap.add_argument("--segment-index", help="Optional path to segment_asset_index.json (LLM-derived, one image per segment)")
    ap.add_argument("--variant-id", default="default", help="Variant for logging")
    ap.add_argument("--allow-placeholders", action="store_true", help="Allow placeholder_* asset_ids when no compatible assets are available")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists")
    args = ap.parse_args()

    path = Path(args.shot_plan)
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1
    shot_plan = json.loads(path.read_text(encoding="utf-8"))
    bank_path = Path(args.bank) if args.bank else None
    segment_index = None
    if args.segment_index:
        seg_path = Path(args.segment_index)
        if seg_path.exists():
            segment_index = json.loads(seg_path.read_text(encoding="utf-8"))
        else:
            print(f"Warning: segment-index not found: {seg_path}", file=sys.stderr)

    out_path = Path(args.out)
    if should_skip_output(out_path, ["plan_id", "resolved", "config_hash"], args.force, config_snapshot_hash()):
        print(f"Skip (output exists, use --force to overwrite): {out_path}")
        return 0
    result = run_asset_resolver(
        shot_plan,
        bank_path,
        args.variant_id,
        segment_index=segment_index,
        allow_placeholders=args.allow_placeholders,
    )
    write_atomically(out_path, result)
    print(f"Wrote resolved assets for {len(result['resolved'])} shots to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
