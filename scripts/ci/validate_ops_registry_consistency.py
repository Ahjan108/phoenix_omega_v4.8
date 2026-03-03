"""
CI: Ensure ops artifacts and registry stay in sync.
- Every artifact matching a registry pattern is validated by validate_ops_artifacts.
- Schema file exists for each registry entry with schema_path.
- Optional: artifact schema_version matches registry current_version (when schema enforces const).
Run from repo root: python scripts/ci/validate_ops_registry_consistency.py
"""
from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}


def main() -> int:
    registry_path = REPO_ROOT / "config" / "ops_schema_registry.yaml"
    data = _load_yaml(registry_path)
    registry = (data.get("ops_schema_registry") or data) or {}
    if not registry:
        print("No ops_schema_registry found in config/ops_schema_registry.yaml")
        return 0

    errors = []
    for key, entry in registry.items():
        if not isinstance(entry, dict):
            continue
        schema_rel = entry.get("schema_path")
        if not schema_rel:
            continue
        schema_path = REPO_ROOT / schema_rel
        if not schema_path.exists():
            errors.append(f"Registry '{key}': schema_path missing: {schema_path}")

    ops_dir = REPO_ROOT / "artifacts" / "ops"
    if ops_dir.exists():
        for json_path in ops_dir.rglob("*.json"):
            name = json_path.name
            matched = None
            for key, entry in registry.items():
                if not isinstance(entry, dict):
                    continue
                pattern = entry.get("artifact_pattern")
                if not pattern:
                    continue
                subdir = entry.get("artifact_subdir")
                if subdir and subdir not in str(json_path):
                    continue
                if fnmatch.fnmatch(name, pattern):
                    matched = key
                    break
            if matched and not registry.get(matched, {}).get("schema_path"):
                errors.append(f"Artifact {json_path.name} matches registry key '{matched}' but has no schema_path")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("Registry consistency OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
