"""
Structural Variation V4: check reframe repetition and banned phrases.
Per-book repetition ceiling for identical reframe line; banned_patterns from profile.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_SOT = REPO_ROOT / "config" / "source_of_truth"
MAX_SAME_REFRAME_LINE_PER_BOOK = 3


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_reframe_diversity(
    plan: Union[dict, Any],
    config_root: Optional[Path] = None,
) -> ValidationResult:
    """
    If plan has reframe_injections, fail when same line text repeats above ceiling or contains banned phrase.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if hasattr(plan, "get"):
        plan_dict = plan
    else:
        plan_dict = getattr(plan, "__dict__", {})

    injections = plan_dict.get("reframe_injections") or []
    if not injections:
        return ValidationResult(valid=True, errors=[], warnings=[])

    # Repetition ceiling
    text_counts: dict[str, int] = {}
    for inj in injections:
        t = (inj.get("text") or "").strip()
        if t:
            text_counts[t] = text_counts.get(t, 0) + 1
    for text, count in text_counts.items():
        if count > MAX_SAME_REFRAME_LINE_PER_BOOK:
            errors.append(
                f"Reframe diversity: identical line repeated {count} times (max {MAX_SAME_REFRAME_LINE_PER_BOOK}). "
                f"First 50 chars: {text[:50]!r}..."
            )

    # Banned patterns from profile
    config_root = config_root or CONFIG_SOT
    reframe_cfg = _load_yaml(config_root / "reframe_line_bank.yaml")
    profile_id = plan_dict.get("reframe_profile_id") or "balanced"
    profiles = reframe_cfg.get("profiles") or {}
    profile = profiles.get(profile_id) or {}
    banned = profile.get("banned_patterns") or []
    for inj in injections:
        t = (inj.get("text") or "").lower()
        for bp in banned:
            if bp.lower() in t:
                errors.append(f"Reframe banned pattern: profile {profile_id} forbids {bp!r}; found in reframe line.")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
