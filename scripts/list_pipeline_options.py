#!/usr/bin/env python3
"""
Emit pipeline options as JSON for UI (Run one book / QA tab).
Output: single JSON object to stdout with arcs, angles, topics, personas, output_formats.
Usage: python scripts/list_pipeline_options.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:
    yaml = None


def main() -> int:
    out: dict = {
        "arcs": [],
        "angles": [],
        "topics": [],
        "personas": [],
        "output_formats": [],
        "structural_formats": ["F006", "compact", "express", "deep"],
        "runtime_formats": ["standard_book", "micro_book_15", "micro_book_20", "short_book_30", "deep_book_6h"],
    }

    # Master arcs: list YAML files under config/source_of_truth/master_arcs/
    arcs_dir = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
    if arcs_dir.exists():
        for f in sorted(arcs_dir.glob("*.yaml")):
            rel = f.relative_to(REPO_ROOT)
            out["arcs"].append({"id": f.stem, "path": str(rel)})

    # Angles: from config/angles/angle_registry.yaml
    if yaml:
        reg = REPO_ROOT / "config" / "angles" / "angle_registry.yaml"
        if reg.exists():
            data = yaml.safe_load(reg.read_text()) or {}
            angles = data.get("angles") or {}
            out["angles"] = [{"id": k, "label": k.replace("_", " ").title()} for k in sorted(angles.keys())]
    if not out["angles"]:
        out["angles"] = [{"id": "WRONG_PROBLEM", "label": "Wrong Problem"}, {"id": "MAP_PROMISE", "label": "Map Promise"}, {"id": "HIDDEN_TRUTH", "label": "Hidden Truth"}, {"id": "ONE_LEVER", "label": "One Lever"}]

    # Canonical topics
    try:
        topics_file = REPO_ROOT / "config" / "catalog_planning" / "canonical_topics.yaml"
        if topics_file.exists() and yaml:
            data = yaml.safe_load(topics_file.read_text()) or {}
            out["topics"] = list(data.get("topics") or [])
    except Exception:
        out["topics"] = ["anxiety", "burnout", "self_worth", "grief", "boundaries"]

    # Canonical personas
    try:
        personas_file = REPO_ROOT / "config" / "catalog_planning" / "canonical_personas.yaml"
        if personas_file.exists() and yaml:
            data = yaml.safe_load(personas_file.read_text()) or {}
            out["personas"] = list(data.get("personas") or [])
    except Exception:
        out["personas"] = ["corporate_managers", "gen_z_professionals", "working_parents"]

    # Output formats (V4 freeze)
    try:
        freeze_file = REPO_ROOT / "pearl_prime" / "config" / "v4_freeze_modular_formats.yaml"
        if freeze_file.exists() and yaml:
            data = yaml.safe_load(freeze_file.read_text()) or {}
            formats = data.get("output_formats") or {}
            out["output_formats"] = [
                {"id": k, "label": (v.get("name") or k).replace("_", " ")}
                for k, v in sorted(formats.items())
            ]
    except Exception:
        out["output_formats"] = [{"id": "pocket_guide", "label": "Pocket Guide"}, {"id": "myth_vs_mechanism", "label": "Myth vs Mechanism"}]

    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
