#!/usr/bin/env python3
"""
Promote approved metadata candidates into live config.
Only run after check_metadata_promotion_gate.py passes.

Applies patches to:
  config/research_metadata/topic_vocabulary.yaml
  config/research_metadata/persona_vocabulary.yaml
  config/research_metadata/invisible_scripts.yaml

Writes a promotion log to artifacts/ei_v2/metadata_candidates/promotion_log.jsonl.
Marks the candidates file status: 'promoted'.

Usage:
  python scripts/research/promote_metadata_candidates.py \
    --candidates artifacts/ei_v2/metadata_candidates/20260306_kb_derived.json
"""
from __future__ import annotations

import argparse
import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
RESEARCH_META_DIR = REPO_ROOT / "config" / "research_metadata"
PROMOTION_LOG_PATH = REPO_ROOT / "artifacts" / "ei_v2" / "metadata_candidates" / "promotion_log.jsonl"


def _load_or_create_yaml(path: Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and yaml:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _write_yaml(path: Path, data: dict) -> None:
    if yaml is None:
        # Fallback: write as JSON with .yaml extension
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _apply_topic_vocabulary_patch(patch: dict) -> dict:
    """Apply topic_vocabulary_add patch."""
    target = patch.get("target") or ""
    # Extract topic from target string: "domain_embeddings._TOPIC_LEXICONS.mental_health"
    topic = target.split(".")[-1] if "." in target else target
    add_terms = patch.get("add_terms") or []

    voc_path = RESEARCH_META_DIR / "topic_vocabulary.yaml"
    data = _load_or_create_yaml(voc_path)
    if "schema_version" not in data:
        data["schema_version"] = "1.0"
        data["topics"] = {}
    if topic not in data["topics"]:
        data["topics"][topic] = []
    existing = set(data["topics"][topic])
    new_terms = [t for t in add_terms if t not in existing]
    data["topics"][topic].extend(new_terms)
    _write_yaml(voc_path, data)
    logger.info("topic_vocabulary: added %d new terms to topic '%s'", len(new_terms), topic)
    return {"added": new_terms, "topic": topic}


def _apply_persona_vocabulary_patch(patch: dict) -> dict:
    """Apply persona_vocabulary_add patch."""
    target = patch.get("target") or ""
    persona = target.split(".")[-1] if "." in target else target
    add_terms = patch.get("add_terms") or []

    voc_path = RESEARCH_META_DIR / "persona_vocabulary.yaml"
    data = _load_or_create_yaml(voc_path)
    if "schema_version" not in data:
        data["schema_version"] = "1.0"
        data["personas"] = {}
    if persona not in data["personas"]:
        data["personas"][persona] = []
    existing = set(data["personas"][persona])
    new_terms = [t for t in add_terms if t not in existing]
    data["personas"][persona].extend(new_terms)
    _write_yaml(voc_path, data)
    logger.info("persona_vocabulary: added %d new terms to persona '%s'", len(new_terms), persona)
    return {"added": new_terms, "persona": persona}


def _apply_invisible_scripts_patch(patch: dict) -> dict:
    """Apply invisible_scripts_add patch."""
    add_entries = patch.get("add_entries") or []

    scripts_path = RESEARCH_META_DIR / "invisible_scripts.yaml"
    data = _load_or_create_yaml(scripts_path)
    if "schema_version" not in data:
        data["schema_version"] = "1.0"
        data["scripts"] = []
    existing_texts = {s.get("text") for s in data["scripts"] if isinstance(s, dict)}
    new_entries = [e for e in add_entries if e.get("text") not in existing_texts]
    data["scripts"].extend(new_entries)
    _write_yaml(scripts_path, data)
    logger.info("invisible_scripts: added %d new entries", len(new_entries))
    return {"added_count": len(new_entries)}


PATCH_HANDLERS = {
    "topic_vocabulary_add": _apply_topic_vocabulary_patch,
    "persona_vocabulary_add": _apply_persona_vocabulary_patch,
    "invisible_scripts_add": _apply_invisible_scripts_patch,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote metadata candidates to live config")
    ap.add_argument("--candidates", required=True, help="Path to candidates JSON file")
    ap.add_argument("--force", action="store_true", help="Promote even if already promoted (re-promote)")
    args = ap.parse_args()

    candidates_path = Path(args.candidates)
    if not candidates_path.exists():
        logger.error("Candidates file not found: %s", candidates_path)
        return 1

    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))

    if candidates.get("status") == "promoted" and not args.force:
        logger.warning("Candidates already promoted. Use --force to re-promote.")
        return 0

    if candidates.get("status") != "shadow_pending" and not args.force:
        logger.error(
            "Candidates status is '%s' (not shadow_pending). Run gate check first.", candidates.get("status")
        )
        return 1

    RESEARCH_META_DIR.mkdir(parents=True, exist_ok=True)
    PROMOTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    patches = candidates.get("patches") or []
    results = []
    errors = []

    for patch in patches:
        pt = patch.get("patch_type")
        handler = PATCH_HANDLERS.get(pt)
        if not handler:
            errors.append(f"Unknown patch_type: {pt}")
            continue
        try:
            result = handler(patch)
            results.append({"patch_type": pt, "target": patch.get("target"), "result": result})
        except Exception as e:
            errors.append(f"{pt}: {e}")
            logger.error("Failed to apply patch %s: %s", pt, e)

    # Mark candidates as promoted
    candidates["status"] = "promoted"
    candidates["promoted_at"] = datetime.now(timezone.utc).isoformat()
    candidates["promotion_results"] = results
    candidates["promotion_errors"] = errors
    candidates_path.write_text(json.dumps(candidates, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write promotion log
    log_entry = {
        "promoted_at": datetime.now(timezone.utc).isoformat(),
        "candidates_file": str(candidates_path),
        "patch_count": len(patches),
        "applied": len(results),
        "errors": len(errors),
        "error_details": errors,
    }
    with open(PROMOTION_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    if errors:
        logger.warning("%d errors during promotion: %s", len(errors), errors)

    print(f"✅ Promotion complete: {len(results)}/{len(patches)} patches applied")
    if errors:
        print(f"⚠️  {len(errors)} errors: {errors}")
    print(f"Config files updated in: {RESEARCH_META_DIR}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
