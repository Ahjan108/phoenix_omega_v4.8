"""
EI V2 structured warnings — replaces silent except:pass with logged warnings.

Writes to artifacts/ei_v2/ei_warnings.jsonl (append-only).
Call log_ei_warning() when catching recoverable errors instead of pass.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DEFAULT_PATH = _REPO_ROOT / "artifacts" / "ei_v2" / "ei_warnings.jsonl"
_error_count: Dict[str, int] = {}


def log_ei_warning(
    component: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    path: Optional[Path] = None,
) -> None:
    """Log a warning to the EI warnings artifact. Increments error counter for component."""
    global _error_count
    _error_count[component] = _error_count.get(component, 0) + 1

    p = path or _DEFAULT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": component,
        "message": message,
        "context": context or {},
    }
    try:
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        pass  # Avoid recursion; cannot log failure to log


def get_error_counts() -> Dict[str, int]:
    """Return current session error counts per component."""
    return dict(_error_count)


def reset_error_counts() -> None:
    """Reset error counts (e.g. for tests)."""
    global _error_count
    _error_count.clear()
