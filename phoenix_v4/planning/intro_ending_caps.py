"""
Intro/ending signature caps and duplicate gate. Authority: Controlled Intro/Conclusion Variation plan.
Calendar quarter in brand locale time; 15% intro cap, 20% ending cap; max_retries then fail with candidate alternatives.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_SOT = REPO_ROOT / "config" / "source_of_truth"
INTRO_ENDING_VARIATION = CONFIG_SOT / "intro_ending_variation.yaml"


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_quarter_for_brand(brand_id: str, config_root: Optional[Path] = None) -> str:
    """
    Canonical calendar quarter in brand locale time. For now use UTC; can later resolve
    brand_id -> territory -> timezone from locale_registry. Format: YYYY-Q1 | Q2 | Q3 | Q4.
    """
    config_root = config_root or REPO_ROOT / "config"
    # Optional: load brand locale/territory and use that TZ; for parity across runners use UTC.
    now = datetime.utcnow()
    month = now.month
    q = (month - 1) // 3 + 1
    return f"{now.year}-Q{q}"


def load_intro_ending_config(config_root: Optional[Path] = None) -> dict:
    """Load intro_ending_variation.yaml."""
    config_root = config_root or CONFIG_SOT
    path = config_root / "intro_ending_variation.yaml"
    return _load_yaml(path)


def load_signature_index(artifact_path: Path) -> list[dict[str, Any]]:
    """Load JSONL of {brand_id, quarter, pre_intro_signature?, ending_signature?}."""
    if not artifact_path.exists():
        return []
    rows = []
    for line in artifact_path.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


@dataclass
class CapCheckResult:
    ok: bool
    error: Optional[str] = None
    candidate_alternatives: Optional[list[str]] = None


def check_intro_cap_and_duplicate(
    brand_id: str,
    quarter: str,
    pre_intro_signature: str,
    signature_index: list[dict[str, Any]],
    cap_share: float = 0.15,
) -> CapCheckResult:
    """
    Check pre_intro_signature: under cap (<= cap_share of brand/quarter) and not duplicate in quarter.
    If over cap or duplicate, return ok=False with error and candidate_alternatives (up to 3 suggestions).
    """
    in_quarter = [r for r in signature_index if r.get("brand_id") == brand_id and r.get("quarter") == quarter]
    total = len(in_quarter)
    sig_count = sum(1 for r in in_quarter if r.get("pre_intro_signature") == pre_intro_signature)
    is_duplicate = any(r.get("pre_intro_signature") == pre_intro_signature for r in in_quarter)

    # Only enforce cap when quarter has enough books that 15% is meaningful (avoid failing first book)
    if total >= 1 / max(cap_share, 0.01) and (sig_count + 1) / (total + 1) > cap_share:
        return CapCheckResult(
            ok=False,
            error=f"Pre-intro signature would exceed {cap_share:.0%} cap for brand {brand_id!r} in {quarter} (current: {sig_count}/{total}).",
            candidate_alternatives=[
                "Try a different seed or run at a different time.",
                "Use pattern_bank_overrides_yaml=false to prefer YAML values.",
                "Add more variants to pre_intro banks for this brand.",
            ],
        )
    if is_duplicate:
        return CapCheckResult(
            ok=False,
            error=f"Pre-intro signature duplicate for brand {brand_id!r} in {quarter}.",
            candidate_alternatives=[
                "Reselect by varying selector_key (e.g. append retry index).",
                "Add more variants to narrator_intro_variants or transition_line_variants.",
                "Use a different book seed.",
            ],
        )
    return CapCheckResult(ok=True)


def check_ending_cap_and_duplicate(
    brand_id: str,
    quarter: str,
    ending_signature: str,
    signature_index: list[dict[str, Any]],
    cap_share: float = 0.20,
) -> CapCheckResult:
    """Same as intro but for ending_signature and 20% cap."""
    in_quarter = [r for r in signature_index if r.get("brand_id") == brand_id and r.get("quarter") == quarter]
    total = len(in_quarter)
    sig_count = sum(1 for r in in_quarter if r.get("ending_signature") == ending_signature)
    is_duplicate = any(r.get("ending_signature") == ending_signature for r in in_quarter)

    if total >= 1 / max(cap_share, 0.01) and (sig_count + 1) / (total + 1) > cap_share:
        return CapCheckResult(
            ok=False,
            error=f"Ending signature would exceed {cap_share:.0%} cap for brand {brand_id!r} in {quarter} (current: {sig_count}/{total}).",
            candidate_alternatives=[
                "Try a different seed or integration_ending_style / carry_line_style.",
                "Add more lines to carry_line_styles or integration_ending_styles.",
                "Run at a different time (next quarter).",
            ],
        )
    if is_duplicate:
        return CapCheckResult(
            ok=False,
            error=f"Ending signature duplicate for brand {brand_id!r} in {quarter}.",
            candidate_alternatives=[
                "Reselect ending_style_id or carry_line_style_id.",
                "Add more variants to carry_line_styles.yaml.",
                "Use a different book seed.",
            ],
        )
    return CapCheckResult(ok=True)
