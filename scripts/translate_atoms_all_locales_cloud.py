#!/usr/bin/env python3
"""
Translate atoms for all configured locales (cloud/Qwen matrix).
Stub: implement when translation pipeline is ready.
See config/localization/content_roots_by_locale.yaml and docs/DOCS_INDEX.md § Translation.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print("Stub: translate_atoms_all_locales_cloud not yet implemented.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
