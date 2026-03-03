#!/usr/bin/env python3
"""
CI check: fail if any registered export script does not call prepare_wave_for_export.

Ensures no export path bypasses the release entrypoint. Registry: export_scripts_registry.yaml
in this directory. Each listed script must reference "prepare_wave_for_export" (e.g. subprocess
call or PREPARE_WAVE variable).

Exit 0 if all export scripts reference the release entrypoint; 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY = Path(__file__).resolve().parent / "export_scripts_registry.yaml"
REQUIRED_STRING = "prepare_wave_for_export"


def main() -> int:
    if not REGISTRY.exists():
        print(f"Registry not found: {REGISTRY}", file=sys.stderr)
        return 1

    try:
        import yaml
    except ImportError:
        print("PyYAML required to read export_scripts_registry.yaml", file=sys.stderr)
        return 1

    data = yaml.safe_load(REGISTRY.read_text()) or {}
    scripts = data.get("export_scripts") or []
    if not scripts:
        return 0

    failures = []
    for rel_path in scripts:
        path = REPO_ROOT / rel_path
        if not path.exists():
            failures.append(f"{rel_path}: file not found")
            continue
        text = path.read_text()
        if REQUIRED_STRING not in text:
            failures.append(f"{rel_path}: does not reference {REQUIRED_STRING!r} (export bypass risk)")

    if failures:
        for f in failures:
            print(f, file=sys.stderr)
        print("Export scripts must call prepare_wave_for_export. See PREPUBLISH_CHECKLIST.md.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
