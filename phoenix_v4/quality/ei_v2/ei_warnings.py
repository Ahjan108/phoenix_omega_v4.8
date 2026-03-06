"""
EI V2 warning logger — optional observability for config/learner failures.

Used by config loader and learner when YAML parse or feedback parse fails.
Does not raise; logs for debugging and optional collection by POLES.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict


def log_ei_warning(component: str, message: str, context: Dict[str, Any] | None = None) -> None:
    """Log a warning from an EI V2 component (config, learner, etc.)."""
    context = context or {}
    payload = {"component": component, "message": message, **context}
    line = json.dumps(payload, default=str) + "\n"
    sys.stderr.write(f"[ei_v2] {line}")
