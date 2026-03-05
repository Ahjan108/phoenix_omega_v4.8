#!/usr/bin/env python3
"""
Check golden translation regression: compare outputs to config/localization/quality_contracts/golden_translation_regression.yaml.
Stub: implement when locale gate is ready.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("Stub: check_golden_translation not yet implemented.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
