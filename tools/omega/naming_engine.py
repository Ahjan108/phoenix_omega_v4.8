#!/usr/bin/env python3
"""
Thin wrapper for Phoenix V4 Naming Engine. Calls phoenix_v4.naming.cli.
Usage:
  python tools/omega/naming_engine.py --book-spec path/to/book_spec.json --output title_output.json
  python tools/omega/naming_engine.py --topic relationship_anxiety --persona nyc_exec --series social_anxiety_arc --angle at_work --brand stabilizer --seed test_seed_001 --trace
"""
from __future__ import annotations

import sys
from pathlib import Path

# Repo root: tools/omega -> tools -> repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.naming.cli import main

if __name__ == "__main__":
    sys.exit(main())
