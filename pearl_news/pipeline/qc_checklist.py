"""
Pearl News — final QC checklist before publish. See config/quality_gates.yaml, editorial_firewall.yaml.

MVP: structural checks (title, content present), blocklist already in quality_gates.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def run_qc_checklist(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Run final QC checks. Adds qc_checklist_passed, qc_checklist_notes.

    MVP checks:
    - title present and non-empty
    - content or summary present
    - no blocklist (handled by quality_gates; assume already run)

    :param items: Items (feed or article) with qc_passed from quality_gates.
    :return: Items with qc_checklist_passed, qc_checklist_notes.
    """
    result: list[dict[str, Any]] = []
    for item in items:
        notes: list[str] = []
        title = (item.get("title") or item.get("raw_title") or "").strip()
        content = (item.get("content") or item.get("summary") or item.get("raw_summary") or "").strip()

        if not title:
            notes.append("Missing title")
        if not content:
            notes.append("Missing content/summary")

        passed = len(notes) == 0
        out = {
            **item,
            "qc_checklist_passed": passed,
            "qc_checklist_notes": notes if notes else None,
        }
        result.append(out)

    failed = sum(1 for i in result if not i.get("qc_checklist_passed"))
    logger.info("QC checklist: %d passed, %d failed", len(result) - failed, failed)
    return result


def filter_checklist_passed(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only items that passed QC checklist."""
    return [i for i in items if i.get("qc_checklist_passed", True)]
