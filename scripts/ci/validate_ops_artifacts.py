"""
CI: Validate ops JSON artifacts against JSON Schema (Draft 2020-12).
Uses config/ops_schema_registry.yaml for artifact_pattern → schema mapping.
Missing required fields or schema version mismatch → exit 1.
Run from repo root: python scripts/ci/validate_ops_artifacts.py
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


def _load_registry() -> dict:
    path = REPO_ROOT / "config" / "ops_schema_registry.yaml"
    data = _load_yaml(path)
    return (data.get("ops_schema_registry") or data) or {}


def _get_validator():
    try:
        import jsonschema
        if hasattr(jsonschema, "Draft202012Validator"):
            return jsonschema.Draft202012Validator
        return jsonschema.Draft7Validator
    except ImportError:
        return None


def detect_artifact_type(path: Path, registry: dict) -> str | None:
    """Return registry key if path matches any artifact_pattern (and optional subdir)."""
    name = path.name
    for key, entry in registry.items():
        if not isinstance(entry, dict):
            continue
        pattern = entry.get("artifact_pattern")
        if not pattern:
            continue
        subdir = entry.get("artifact_subdir")
        if subdir and subdir not in str(path):
            continue
        if fnmatch.fnmatch(name, pattern):
            return key
    return None


def validate_file(path: Path, schema_path: Path, validator_cls) -> list[str]:
    """Validate JSON at path against schema. Return list of error messages."""
    errors = []
    if not schema_path.exists():
        return [f"Missing schema file: {schema_path}"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"Invalid schema {schema_path}: {e}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"Invalid JSON {path}: {e}"]

    validator = validator_cls(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: (list(e.path), e.message)):
        path_str = ".".join(str(p) for p in err.path) if err.path else "(root)"
        errors.append(f"  → {path_str}: {err.message}")
    return errors


def main() -> int:
    registry = _load_registry()
    validator_cls = _get_validator()
    if validator_cls is None:
        print("jsonschema not installed. pip install jsonschema", file=sys.stderr)
        return 1

    ops_dir = REPO_ROOT / "artifacts" / "ops"
    if not ops_dir.exists():
        print("No artifacts/ops directory; skipping validation.")
        return 0

    failed = []
    validated = 0
    for json_path in ops_dir.rglob("*.json"):
        artifact_type = detect_artifact_type(json_path, registry)
        if not artifact_type:
            continue
        entry = registry.get(artifact_type)
        if not isinstance(entry, dict):
            continue
        schema_rel = entry.get("schema_path")
        if not schema_rel:
            continue
        schema_path = REPO_ROOT / schema_rel
        errs = validate_file(json_path, schema_path, validator_cls)
        if errs:
            failed.append((json_path, errs))
        else:
            validated += 1

    if failed:
        print("SCHEMA VALIDATION FAILED", file=sys.stderr)
        for path, errs in failed:
            print(f"\n{path}", file=sys.stderr)
            for e in errs:
                print(e, file=sys.stderr)
        return 1
    print(f"All ops artifacts passed schema validation ({validated} file(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
