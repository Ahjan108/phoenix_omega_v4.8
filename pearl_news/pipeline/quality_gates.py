"""
Pearl News — structured quality gates (fail-hard). See config/quality_gates.yaml, legal_boundary.yaml.

Checks: blocklist phrases, basic structure. Full gates (fact-check, youth specificity, etc.)
require more context; MVP enforces legal_boundary blocklist only.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


def _load_legal_boundary(config_path: Path) -> dict[str, Any]:
    if not config_path.exists() or yaml is None:
        return {"blocklist_phrases": []}
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def _check_blocklist(text: str, blocklist: list[str]) -> tuple[bool, str | None]:
    """Return (passed, failed_phrase). Passed if no blocklist phrase in text."""
    if not text:
        return True, None
    text_lower = text.lower()
    for phrase in blocklist or []:
        if phrase.lower() in text_lower:
            return False, phrase
    return True, None


def run_quality_gates(
    items: list[dict[str, Any]],
    legal_boundary_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Run quality gates on items. Failed items are marked with qc_failed=True and qc_fail_reason.

    MVP: only legal_boundary blocklist. Items that pass have qc_passed=True.

    :param items: Feed items or assembled articles (must have title, content/summary).
    :param legal_boundary_path: Path to legal_boundary.yaml.
    :return: Same items with qc_passed, qc_failed, qc_fail_reason added.
    """
    root = Path(__file__).resolve().parent.parent
    path = Path(legal_boundary_path) if legal_boundary_path else root / "config" / "legal_boundary.yaml"
    legal = _load_legal_boundary(path)
    blocklist = legal.get("blocklist_phrases") or []

    result: list[dict[str, Any]] = []
    for item in items:
        text = " ".join(
            str(item.get(k, ""))
            for k in ("title", "content", "summary", "raw_summary", "raw_title")
            if item.get(k)
        )
        passed, failed_phrase = _check_blocklist(text, blocklist)
        out = {
            **item,
            "qc_passed": passed,
            "qc_failed": not passed,
            "qc_fail_reason": f"Blocklist phrase: {failed_phrase}" if failed_phrase else None,
        }
        result.append(out)

    failed_count = sum(1 for i in result if i.get("qc_failed"))
    logger.info("Quality gates: %d passed, %d failed", len(result) - failed_count, failed_count)
    return result


def filter_passed(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only items that passed quality gates."""
    return [i for i in items if i.get("qc_passed", True) and not i.get("qc_failed")]
