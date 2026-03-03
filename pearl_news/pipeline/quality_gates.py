"""
Pearl News — structured quality gates (fail-hard). See config/quality_gates.yaml, legal_boundary.yaml.

Checks: blocklist phrases, phrase repetition, teacher saturation, template rotation.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)

# Transition phrases to flag for repetition (case-insensitive)
TRANSITION_PHRASES = [
    "Now, let's",
    "With that said",
    "That said",
    "Having said that",
    "At the end of the day",
    "spiritual leaders",
    "youth mental health",
]


def check_transition_phrase_repetition(text: str) -> list[str]:
    """Return list of transition phrases found in text. Used for phrase_flags."""
    if not text:
        return []
    text_lower = text.lower()
    found: list[str] = []
    for phrase in TRANSITION_PHRASES:
        if phrase.lower() in text_lower:
            found.append(phrase)
    return found


def check_teacher_saturation(
    history: list[dict[str, Any]],
    teacher_ids: list[str],
    window: int = 20,
    cap: float = 0.30,
) -> tuple[bool, str | None]:
    """
    Teacher saturation guard.

    Rules:
    - Empty teacher_ids: pass.
    - Empty history: pass.
    - Current article teacher list cannot be duplicate-heavy (> cap for one teacher).
      This catches malformed metadata like repeated identical teacher IDs.
    - Hard-stop on history monopoly: if a teacher has taken 100% of the recent
      window, block reusing that same teacher in the next article.
    """
    if not teacher_ids:
        return True, None

    # Cap duplicates within this single article's teacher list.
    # Example malformed input: ["A", "A", "A"].
    current_counts: dict[str, int] = {}
    for tid in teacher_ids:
        current_counts[tid] = current_counts.get(tid, 0) + 1
    current_total = len(teacher_ids)
    # Only apply duplicate-density rule when multiple teacher IDs are present.
    if current_total > 1:
        for tid, count in current_counts.items():
            if (count / current_total) > cap:
                return False, f"Teacher {tid} exceeds {cap:.0%} in article teacher_ids"

    recent = history[-window:] if len(history) >= window else history
    if not recent:
        return True, None

    # Hard-stop only when one teacher fully monopolized the full window.
    history_counts: dict[str, int] = {}
    teacher_rows = 0
    for rec in recent:
        rec_teachers = rec.get("teacher_ids") or []
        if rec_teachers:
            teacher_rows += 1
        for tid in rec_teachers:
            history_counts[tid] = history_counts.get(tid, 0) + 1
    total_rows = teacher_rows
    for tid in set(teacher_ids):
        if history_counts.get(tid, 0) >= total_rows and total_rows > 0:
            return False, f"Teacher {tid} is saturated in last {window}"

    return True, None


def check_template_rotation(
    history: list[dict[str, Any]],
    template_id: str,
    max_consecutive: int = 3,
) -> tuple[bool, str | None]:
    """Fail if current template would create a tail streak longer than max_consecutive."""
    if not template_id:
        return True, None
    tail = 0
    for rec in reversed(history):
        tid = rec.get("template_id") or ""
        if tid == template_id:
            tail += 1
        else:
            break
    consecutive = tail + 1  # include current article
    if consecutive > max_consecutive:
        return False, f"Template {template_id} repeated {consecutive} times"
    return True, None


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


def _load_metadata_history(metadata_path: Path, window: int = 20) -> list[dict[str, Any]]:
    """Load last window lines from article_metadata.jsonl."""
    if not metadata_path.exists():
        return []
    lines = metadata_path.read_text(encoding="utf-8").strip().split("\n")
    records: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except Exception:
            continue
    return records[-window:] if len(records) > window else records


def run_quality_gates(
    items: list[dict[str, Any]],
    legal_boundary_path: str | Path | None = None,
    metadata_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Run quality gates on items. Failed items are marked with qc_failed=True and qc_fail_reason.

    Checks: blocklist, phrase repetition (phrase_flags), teacher saturation, template rotation.

    :param items: Feed items or assembled articles (must have title, content/summary).
    :param legal_boundary_path: Path to legal_boundary.yaml.
    :param metadata_path: Path to article_metadata.jsonl for teacher/template history.
    :return: Same items with qc_passed, qc_failed, qc_fail_reason, phrase_flags added.
    """
    root = Path(__file__).resolve().parent.parent
    path = Path(legal_boundary_path) if legal_boundary_path else root / "config" / "legal_boundary.yaml"
    legal = _load_legal_boundary(path)
    blocklist = legal.get("blocklist_phrases") or []

    meta_path = Path(metadata_path) if metadata_path else None
    history = _load_metadata_history(meta_path) if meta_path else []

    result: list[dict[str, Any]] = []
    for item in items:
        text = " ".join(
            str(item.get(k, ""))
            for k in ("title", "content", "summary", "raw_summary", "raw_title")
            if item.get(k)
        )
        block_ok, failed_phrase = _check_blocklist(text, blocklist)
        phrase_flags = check_transition_phrase_repetition(text)
        out = {**item, "phrase_flags": phrase_flags}

        reasons: list[str] = []
        if not block_ok:
            reasons.append(f"Blocklist phrase: {failed_phrase}")

        if meta_path:
            teacher_ok, teacher_reason = check_teacher_saturation(
                history, out.get("teacher_ids") or [], window=20, cap=0.30
            )
            if not teacher_ok and teacher_reason:
                reasons.append(teacher_reason)
            template_ok, template_reason = check_template_rotation(
                history, out.get("template_id") or "", max_consecutive=3
            )
            if not template_ok and template_reason:
                reasons.append(template_reason)

        passed = len(reasons) == 0
        out["qc_passed"] = passed
        out["qc_failed"] = not passed
        out["qc_fail_reason"] = "; ".join(reasons) if reasons else None
        result.append(out)

        # Append to history for next item's template rotation check
        history.append({
            "teacher_ids": out.get("teacher_ids") or [],
            "template_id": out.get("template_id") or "",
        })

    failed_count = sum(1 for i in result if i.get("qc_failed"))
    logger.info("Quality gates: %d passed, %d failed", len(result) - failed_count, failed_count)
    return result


def filter_passed(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only items that passed quality gates."""
    return [i for i in items if i.get("qc_passed", True) and not i.get("qc_failed")]
