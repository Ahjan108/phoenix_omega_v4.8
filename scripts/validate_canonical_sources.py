#!/usr/bin/env python3
"""
Validate canonical_topics and canonical_personas against runtime configs.
Ensures canonical lists stay in sync with topic_engine_bindings and identity_aliases.
Authority: V4 Freebies + Immersion Ecosystem plan §2.1.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        raise SystemExit("Required: pip install pyyaml (PyYAML)")
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate canonical_topics and canonical_personas against runtime configs"
    )
    ap.add_argument(
        "--against",
        action="append",
        default=[],
        help="Paths to validate against (default: topic_engine_bindings, identity_aliases)",
    )
    ap.add_argument(
        "--canonical-dir",
        type=Path,
        default=REPO_ROOT / "config" / "catalog_planning",
        help="Directory containing canonical_topics.yaml and canonical_personas.yaml",
    )
    ap.add_argument(
        "--config-dir",
        type=Path,
        default=REPO_ROOT / "config",
        help="Directory containing topic_engine_bindings.yaml and identity_aliases.yaml",
    )
    ap.add_argument("--warn-only", action="store_true", help="Warn on drift instead of failing")
    args = ap.parse_args()

    canonical_dir = args.canonical_dir
    config_dir = args.config_dir

    topics_path = canonical_dir / "canonical_topics.yaml"
    personas_path = canonical_dir / "canonical_personas.yaml"
    bindings_path = config_dir / "topic_engine_bindings.yaml"
    aliases_path = config_dir / "identity_aliases.yaml"

    errors: list[str] = []

    # Load canonical
    canonical_topics_data = load_yaml(topics_path)
    canonical_personas_data = load_yaml(personas_path)
    canonical_topics = set(canonical_topics_data.get("topics") or [])
    canonical_personas = set(canonical_personas_data.get("personas") or [])

    if not canonical_topics and topics_path.exists():
        errors.append(f"No 'topics' list in {topics_path}")
    if not canonical_personas and personas_path.exists():
        errors.append(f"No 'personas' list in {personas_path}")

    # Derive from topic_engine_bindings
    bindings = load_yaml(bindings_path)
    if bindings:
        # Top-level keys that are not YAML directives (e.g. anxiety, boundaries)
        binding_topics = {k for k in bindings if isinstance(bindings[k], dict) and "allowed_engines" in bindings[k]}
        missing_in_canonical = binding_topics - canonical_topics
        extra_in_canonical = canonical_topics - binding_topics
        if missing_in_canonical:
            errors.append(
                f"topic_engine_bindings has topics not in canonical_topics: {sorted(missing_in_canonical)}"
            )
        if extra_in_canonical:
            errors.append(
                f"canonical_topics has topics not in topic_engine_bindings: {sorted(extra_in_canonical)}"
            )
    elif canonical_topics:
        errors.append(f"Cannot validate topics: {bindings_path} missing or empty")

    # Derive from identity_aliases (canonical personas = unique values of persona_aliases)
    aliases = load_yaml(aliases_path)
    if aliases:
        persona_aliases = aliases.get("persona_aliases") or {}
        runtime_personas = set(persona_aliases.values())
        missing_in_canonical = runtime_personas - canonical_personas
        extra_in_canonical = canonical_personas - runtime_personas
        if missing_in_canonical:
            errors.append(
                f"identity_aliases has persona values not in canonical_personas: {sorted(missing_in_canonical)}"
            )
        if extra_in_canonical:
            errors.append(
                f"canonical_personas has personas not in identity_aliases values: {sorted(extra_in_canonical)}"
            )
    elif canonical_personas:
        errors.append(f"Cannot validate personas: {aliases_path} missing or empty")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        if args.warn_only:
            print("Validation reported drift (warn-only).", file=sys.stderr)
            return 0
        return 1
    print("Canonical sources validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
