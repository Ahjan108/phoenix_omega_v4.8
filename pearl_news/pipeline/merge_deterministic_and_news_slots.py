"""Deterministic Merge Engine for Pearl News slot-file architecture.

This module enforces the core contract: deterministic teacher-meaning slots
always win over provider-filled slots. Providers (file or Qwen) can only
fill slots explicitly marked as "prompted" in the deterministic plan.

Lane 2 deliverable for the 8-dev parallel build.
"""
from __future__ import annotations

from typing import Any


PROMPTED_SLOTS_BY_TEMPLATE: dict[str, frozenset[str]] = {
    "hard_news_spiritual_response": frozenset({"news_peg", "body_data"}),
    "commentary": frozenset({"headline_layer_1", "news_peg", "body_data"}),
    "explainer_context": frozenset({
        "headline_layer_1",
        "news_peg",
        "body_data",
    }),
    "youth_feature": frozenset({
        "headline_layer_1",
        "news_peg",
        "body_data",
    }),
    "interfaith_dialogue_report": frozenset({"headline_layer_1", "event_summary"}),
    "unsay_dialogue": frozenset({"headline_layer_1", "event_summary", "news_peg", "body_data"}),
}

STANDARD_V52_SLOTS: tuple[str, ...] = (
    "headline_layer_1",
    "headline_layer_2",
    "hook_personal",
    "hook_big_picture",
    "news_peg",
    "teacher_intro",
    "youth_somatic",
    "teacher_witness",
    "body_data",
    "turnaround",
    "bridge",
    "teacher_perspective",
    "practice_announce",
    "forward_look",
)


class MergeError(Exception):
    """Raised when merge validation fails."""

    def __init__(self, article_id: str, errors: list[str]) -> None:
        self.article_id = article_id
        self.errors = errors
        super().__init__(f"{article_id}: merge failed with {len(errors)} error(s): {', '.join(errors)}")


class DeterministicSlotOverwriteAttempt(MergeError):
    """Raised when a provider attempts to overwrite a deterministic slot."""

    def __init__(self, article_id: str, slot: str, deterministic_value: str, attempted_value: str) -> None:
        self.slot = slot
        self.deterministic_value = deterministic_value
        self.attempted_value = attempted_value
        super().__init__(
            article_id,
            [f"provider attempted to overwrite deterministic slot '{slot}' "
             f"(original: '{deterministic_value[:50]}...', attempted: '{attempted_value[:50]}...')"],
        )


def get_prompted_slots(template_id: str) -> frozenset[str]:
    """Return the set of prompted (provider-fillable) slots for a template."""
    return PROMPTED_SLOTS_BY_TEMPLATE.get(template_id, frozenset())


def get_deterministic_slots(template_id: str, deterministic_plan: dict[str, Any]) -> set[str]:
    """Return the set of deterministic (teacher-meaning) slots for a template.

    These are all slots in the deterministic plan that are NOT prompted slots.
    Provider must never overwrite these.
    """
    prompted = get_prompted_slots(template_id)
    plan_slots = set(deterministic_plan.get("slots", {}).keys())
    return plan_slots - prompted


def validate_no_deterministic_overwrites(
    article_id: str,
    template_id: str,
    deterministic_plan: dict[str, Any],
    provider_slots: dict[str, str],
    *,
    strict: bool = True,
) -> list[str]:
    """Validate that provider has not attempted to overwrite deterministic slots.

    Args:
        article_id: Article identifier for error messages.
        template_id: Template type to determine prompted vs deterministic.
        deterministic_plan: The plan containing authoritative slot values.
        provider_slots: Slots filled by the provider (file or Qwen).
        strict: If True, raise DeterministicSlotOverwriteAttempt on violation.

    Returns:
        List of warning messages for attempted overwrites (when strict=False).

    Raises:
        DeterministicSlotOverwriteAttempt: If strict=True and overwrite attempted.
    """
    warnings: list[str] = []
    deterministic_slots = get_deterministic_slots(template_id, deterministic_plan)
    plan_values = deterministic_plan.get("slots") or {}

    for slot in deterministic_slots:
        deterministic_value = str(plan_values.get(slot) or "").strip()
        provider_value = str(provider_slots.get(slot) or "").strip()

        if not deterministic_value:
            continue

        if provider_value and provider_value != deterministic_value:
            if strict:
                raise DeterministicSlotOverwriteAttempt(
                    article_id, slot, deterministic_value, provider_value
                )
            warnings.append(
                f"provider attempted to overwrite deterministic slot '{slot}' "
                f"(ignored, using deterministic value)"
            )

    return warnings


def validate_required_slots_filled(
    article_id: str,
    required_slots: dict[str, str],
) -> list[str]:
    """Validate that all required slots have been filled by provider.

    Returns:
        List of error messages for missing required slots.
    """
    errors: list[str] = []
    for slot, value in required_slots.items():
        if not str(value or "").strip():
            errors.append(f"missing_required_slot:{slot}")
    return errors


def merge_deterministic_and_provider_slots(
    article_id: str,
    template_id: str,
    deterministic_plan: dict[str, Any],
    completed_contract: dict[str, Any],
    *,
    strict_overwrite_check: bool = True,
) -> tuple[dict[str, str], list[str]]:
    """Merge deterministic plan slots with provider-filled slots.

    This is the core merge engine. It enforces:
    1. Deterministic slots ALWAYS win (teacher meaning is sacred).
    2. Provider can only fill slots marked as "prompted" for this template.
    3. All required prompted slots must be filled.

    Args:
        article_id: Article identifier for error messages.
        template_id: Template type to determine slot rules.
        deterministic_plan: Plan containing pre-filled deterministic slots.
        completed_contract: Contract with provider-filled required_slots.
        strict_overwrite_check: Raise exception on overwrite attempt if True.

    Returns:
        Tuple of (merged_slots, warnings).

    Raises:
        MergeError: If required slots are missing.
        DeterministicSlotOverwriteAttempt: If provider tries to overwrite
            deterministic slots (when strict_overwrite_check=True).
    """
    warnings: list[str] = []
    merged: dict[str, str] = {}

    deterministic_values = dict(deterministic_plan.get("slots") or {})
    provider_values = completed_contract.get("required_slots") or {}
    optional_values = completed_contract.get("optional_slots") or {}
    prompted_slots = get_prompted_slots(template_id)

    overwrite_warnings = validate_no_deterministic_overwrites(
        article_id,
        template_id,
        deterministic_plan,
        {**provider_values, **optional_values},
        strict=strict_overwrite_check,
    )
    warnings.extend(overwrite_warnings)

    for slot, value in deterministic_values.items():
        value_str = str(value or "").strip()
        if value_str:
            merged[slot] = value_str

    for slot, value in provider_values.items():
        value_str = str(value or "").strip()
        if not value_str:
            continue
        if slot in merged and slot not in prompted_slots:
            continue
        merged[slot] = value_str

    for slot, value in optional_values.items():
        value_str = str(value or "").strip()
        if not value_str:
            continue
        if slot in merged and slot not in prompted_slots:
            continue
        merged[slot] = value_str

    required_errors = validate_required_slots_filled(article_id, provider_values)
    if required_errors:
        raise MergeError(article_id, required_errors)

    return merged, warnings


def build_v52_slots(
    merged_slots: dict[str, str],
    *,
    include_non_standard: bool = False,
) -> dict[str, str]:
    """Build the final _v52_slots dict from merged slots.

    By default, only includes slots from STANDARD_V52_SLOTS.
    Set include_non_standard=True to include template-specific slots
    (e.g., interfaith or unsay slots).

    Args:
        merged_slots: The merged slot values.
        include_non_standard: Whether to include non-standard slots.

    Returns:
        Dict of slot names to values for _v52_slots.
    """
    if include_non_standard:
        return {k: v for k, v in merged_slots.items() if v}

    return {
        slot: merged_slots[slot]
        for slot in STANDARD_V52_SLOTS
        if str(merged_slots.get(slot) or "").strip()
    }


def validate_v52_slots(
    article_id: str,
    template_id: str,
    v52_slots: dict[str, str],
    deterministic_plan: dict[str, Any],
    *,
    include_non_standard: bool = False,
) -> list[str]:
    """Validate that v52_slots are complete and valid.

    Checks:
    1. All non-empty deterministic slots that should appear in output are present.
    2. Required prompted slots are present.
    3. Only validates slots in STANDARD_V52_SLOTS unless include_non_standard=True.

    Returns:
        List of validation errors.
    """
    errors: list[str] = []
    ordered_sections = deterministic_plan.get("ordered_sections") or []
    valid_output_slots = set(STANDARD_V52_SLOTS) if not include_non_standard else None

    for section in ordered_sections:
        slot = section.get("slot")
        source = section.get("source")
        expected_content = section.get("content", "")

        if valid_output_slots is not None and slot not in valid_output_slots:
            continue

        if source == "deterministic" and expected_content:
            if slot not in v52_slots or not v52_slots[slot]:
                errors.append(f"missing_deterministic_slot:{slot}")

        if source == "prompted":
            if slot not in v52_slots or not v52_slots[slot]:
                errors.append(f"missing_prompted_slot:{slot}")

    return errors


def merge_and_validate(
    article_id: str,
    template_id: str,
    deterministic_plan: dict[str, Any],
    completed_contract: dict[str, Any],
    *,
    strict_overwrite_check: bool = True,
    include_non_standard_slots: bool = False,
) -> tuple[dict[str, str], list[str]]:
    """Full merge-and-validate pipeline producing valid _v52_slots.

    This is the recommended entry point for the merge engine.

    Args:
        article_id: Article identifier for error messages.
        template_id: Template type to determine slot rules.
        deterministic_plan: Plan containing pre-filled deterministic slots.
        completed_contract: Contract with provider-filled required_slots.
        strict_overwrite_check: Raise exception on overwrite attempt if True.
        include_non_standard_slots: Include template-specific slots in output.

    Returns:
        Tuple of (v52_slots, warnings).

    Raises:
        MergeError: If validation fails.
        DeterministicSlotOverwriteAttempt: If provider tries to overwrite
            deterministic slots (when strict_overwrite_check=True).
    """
    merged, warnings = merge_deterministic_and_provider_slots(
        article_id,
        template_id,
        deterministic_plan,
        completed_contract,
        strict_overwrite_check=strict_overwrite_check,
    )

    v52_slots = build_v52_slots(merged, include_non_standard=include_non_standard_slots)

    validation_errors = validate_v52_slots(
        article_id,
        template_id,
        v52_slots,
        deterministic_plan,
        include_non_standard=include_non_standard_slots,
    )
    if validation_errors:
        raise MergeError(article_id, validation_errors)

    return v52_slots, warnings
