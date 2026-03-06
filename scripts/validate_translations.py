#!/usr/bin/env python3
"""
Validate translations against quality contracts and glossary.
Stub: implement when locale gate is ready.
See config/localization/quality_contracts/ and .github/workflows/locale-gate.yml.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("Stub: validate_translations not yet implemented.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
