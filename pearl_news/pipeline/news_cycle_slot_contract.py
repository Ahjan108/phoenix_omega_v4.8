from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - runtime dependency in repo
    yaml = None

from pearl_news.pipeline.deterministic_teacher_topic import (
    build_commentary_deterministic_plan,
    build_explainer_deterministic_plan,
    build_hard_news_deterministic_plan,
    build_interfaith_deterministic_plan,
    build_unsay_deterministic_plan,
    build_youth_feature_deterministic_plan,
)
from pearl_news.pipeline.merge_deterministic_and_news_slots import (
    DeterministicSlotOverwriteAttempt,
    MergeError,
    merge_and_validate,
)


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

CONTRACT_SCHEMA_VERSION = 2
_CONTRACT_VERSION = CONTRACT_SCHEMA_VERSION

ACTIVE_TEMPLATES: tuple[str, ...] = (
    "hard_news_spiritual_response",
    "commentary",
    "explainer_context",
    "interfaith_dialogue_report",
    "youth_feature",
    "unsay_dialogue",
)

TEMPLATE_REQUIRED_SLOTS: dict[str, frozenset[str]] = {
    "hard_news_spiritual_response": frozenset({"news_peg", "body_data"}),
    "commentary": frozenset({"headline_layer_1", "news_peg", "body_data"}),
    "explainer_context": frozenset({
        "headline_layer_1",
        "news_peg",
        "body_data",
    }),
    "interfaith_dialogue_report": frozenset({"headline_layer_1", "event_summary"}),
    "youth_feature": frozenset({
        "headline_layer_1",
        "news_peg",
        "body_data",
    }),
    "unsay_dialogue": frozenset({"headline_layer_1", "event_summary", "news_peg", "body_data"}),
}

CONTRACT_REQUIRED_FIELDS: tuple[str, ...] = (
    "version",
    "article_id",
    "status",
    "template_id",
    "deterministic_context",
    "required_slots",
    "provenance",
)

CONTRACT_OPTIONAL_FIELDS: tuple[str, ...] = (
    "topic",
    "teacher_id",
    "teacher_name",
    "source_url",
    "source_title",
    "source_published_at",
    "optional_slots",
    "writer_notes",
)

VALID_CONTRACT_STATUSES: tuple[str, ...] = ("pending", "completed", "failed")


def _plan_dispatch(item: dict[str, Any], repo_root: Path) -> dict[str, Any] | None:
    template_id = item.get("template_id") or "hard_news_spiritual_response"
    if template_id == "hard_news_spiritual_response":
        return build_hard_news_deterministic_plan(item, repo_root)
    if template_id == "commentary":
        return build_commentary_deterministic_plan(item, repo_root)
    if template_id == "explainer_context":
        return build_explainer_deterministic_plan(item, repo_root)
    if template_id == "interfaith_dialogue_report":
        return build_interfaith_deterministic_plan(item, repo_root)
    if template_id == "youth_feature":
        return build_youth_feature_deterministic_plan(item, repo_root)
    if template_id == "unsay_dialogue":
        return build_unsay_deterministic_plan(item, repo_root)
    return None


def build_slot_contract(item: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build a pending slot contract for an article item.

    Returns (contract, deterministic_plan) tuple.
    The contract conforms to the canonical schema defined by CONTRACT_SCHEMA_VERSION.
    Required slots are derived from TEMPLATE_REQUIRED_SLOTS for the template.
    """
    template_id = item.get("template_id") or "hard_news_spiritual_response"

    if template_id not in ACTIVE_TEMPLATES:
        raise RuntimeError(
            f"template_id '{template_id}' not in ACTIVE_TEMPLATES: {ACTIVE_TEMPLATES}"
        )

    deterministic_plan = _plan_dispatch(item, repo_root)
    if not deterministic_plan:
        raise RuntimeError(
            f"no deterministic plan for template={template_id} topic={item.get('topic')}"
        )

    teacher = item.get("_teacher_resolved") or {}

    canonical_required_slots = TEMPLATE_REQUIRED_SLOTS.get(template_id, frozenset())
    plan_prompted_slots = {
        section["slot"]
        for section in deterministic_plan.get("ordered_sections") or []
        if section.get("source") == "prompted"
    }
    required_slots_set = canonical_required_slots | plan_prompted_slots

    contract = {
        "version": CONTRACT_SCHEMA_VERSION,
        "article_id": item.get("id"),
        "status": "pending",
        "template_id": template_id,
        "topic": item.get("topic"),
        "teacher_id": teacher.get("teacher_id"),
        "teacher_name": teacher.get("display_name"),
        "source_url": item.get("url") or "",
        "source_title": item.get("raw_title") or item.get("title") or "",
        "source_published_at": item.get("pub_date") or "",
        "deterministic_context": {
            "pack_path": deterministic_plan.get("pack_path"),
            "beat_map_id": deterministic_plan.get("beat_map_id"),
            "ordered_sections": deterministic_plan.get("ordered_sections") or [],
        },
        "required_slots": {slot: "" for slot in sorted(required_slots_set)},
        "optional_slots": {},
        "writer_notes": {
            "constraints": [
                "Use source facts already attached to this contract.",
                "Do not rewrite deterministic teacher-voice slots.",
                "Only fill the listed required slots.",
            ],
        },
        "provenance": {
            "filled_by": "",
            "filled_at": "",
            "provider": "file",
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
        },
    }

    schema_errors = validate_contract_schema(contract)
    if schema_errors:
        raise RuntimeError(f"built contract failed schema validation: {schema_errors}")

    return contract, deterministic_plan


def write_pending_contract(contract: dict[str, Any], slots_root: Path) -> Path:
    pending_dir = slots_root / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    path = pending_dir / f"{contract['article_id']}.yaml"
    if yaml is not None:
        path.write_text(yaml.safe_dump(contract, sort_keys=False, allow_unicode=True), encoding="utf-8")
    else:
        path.write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_pending_contract(article_id: str, slots_root: Path) -> dict[str, Any] | None:
    candidates = [
        slots_root / "pending" / f"{article_id}.yaml",
        slots_root / "pending" / f"{article_id}.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        if path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        elif yaml is not None:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        else:
            continue
        if isinstance(data, dict):
            data["_path"] = str(path)
            return data
    return None


def load_completed_contract(article_id: str, slots_root: Path) -> dict[str, Any] | None:
    candidates = [
        slots_root / "completed" / f"{article_id}.yaml",
        slots_root / "completed" / f"{article_id}.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        if path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        elif yaml is not None:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        else:
            continue
        if isinstance(data, dict):
            data["_path"] = str(path)
            return data
    return None


def validate_contract_schema(contract: dict[str, Any]) -> list[str]:
    """Validate contract structure against the canonical schema.

    Returns list of error strings. Empty list means valid.
    """
    errors: list[str] = []

    if not isinstance(contract, dict):
        return ["contract_not_dict"]

    for field in CONTRACT_REQUIRED_FIELDS:
        if field not in contract:
            errors.append(f"missing_required_field:{field}")

    version = contract.get("version")
    if version is not None and not isinstance(version, int):
        errors.append("version_not_integer")
    elif version is not None and version < 1:
        errors.append("version_invalid")

    status = contract.get("status")
    if status is not None and status not in VALID_CONTRACT_STATUSES:
        errors.append(f"invalid_status:{status}")

    template_id = contract.get("template_id")
    if template_id is not None and template_id not in ACTIVE_TEMPLATES:
        errors.append(f"unknown_template_id:{template_id}")

    required_slots = contract.get("required_slots")
    if required_slots is not None and not isinstance(required_slots, dict):
        errors.append("required_slots_not_dict")

    optional_slots = contract.get("optional_slots")
    if optional_slots is not None and not isinstance(optional_slots, dict):
        errors.append("optional_slots_not_dict")

    deterministic_context = contract.get("deterministic_context")
    if deterministic_context is not None:
        if not isinstance(deterministic_context, dict):
            errors.append("deterministic_context_not_dict")
        else:
            if "ordered_sections" not in deterministic_context:
                errors.append("deterministic_context_missing_ordered_sections")

    provenance = contract.get("provenance")
    if provenance is not None and not isinstance(provenance, dict):
        errors.append("provenance_not_dict")

    return errors


def validate_contract_for_template(contract: dict[str, Any]) -> list[str]:
    """Validate that contract's required_slots match the template's canonical slots.

    Returns list of error strings. Empty list means valid.
    """
    errors: list[str] = []

    template_id = contract.get("template_id")
    if not template_id:
        errors.append("template_id_missing")
        return errors

    if template_id not in TEMPLATE_REQUIRED_SLOTS:
        errors.append(f"unknown_template:{template_id}")
        return errors

    canonical_slots = TEMPLATE_REQUIRED_SLOTS[template_id]
    contract_slots = set((contract.get("required_slots") or {}).keys())

    missing_canonical = canonical_slots - contract_slots
    if missing_canonical:
        for slot in sorted(missing_canonical):
            errors.append(f"missing_canonical_slot:{slot}")

    extra_slots = contract_slots - canonical_slots
    if extra_slots:
        for slot in sorted(extra_slots):
            errors.append(f"extra_non_canonical_slot:{slot}")

    return errors


def validate_completed_contract(contract: dict[str, Any]) -> list[str]:
    """Validate that all required slots have non-empty values.

    Returns list of error strings. Empty list means valid.
    """
    errors: list[str] = []
    required_slots = contract.get("required_slots") or {}
    if not isinstance(required_slots, dict):
        return ["required_slots_missing"]
    for slot, value in required_slots.items():
        if not str(value or "").strip():
            errors.append(f"missing_required_slot:{slot}")
    return errors


def validate_contract_full(contract: dict[str, Any]) -> list[str]:
    """Run all contract validations: schema, template conformance, and completion.

    Returns list of error strings. Empty list means valid.
    """
    errors: list[str] = []
    errors.extend(validate_contract_schema(contract))
    if not errors:
        errors.extend(validate_contract_for_template(contract))
    if not errors and contract.get("status") == "completed":
        errors.extend(validate_completed_contract(contract))
    return errors


def get_required_slots_for_template(template_id: str) -> frozenset[str]:
    """Return the canonical required slots for a template.

    Raises ValueError if template_id is unknown.
    """
    if template_id not in TEMPLATE_REQUIRED_SLOTS:
        raise ValueError(f"Unknown template_id: {template_id}. Active templates: {ACTIVE_TEMPLATES}")
    return TEMPLATE_REQUIRED_SLOTS[template_id]


def _to_html_paragraph(text: str) -> str:
    stripped = (text or "").strip()
    if not stripped:
        return ""
    if stripped.startswith("<"):
        return stripped
    return f"<p>{stripped}</p>"


def _merged_values(deterministic_plan: dict[str, Any], completed_contract: dict[str, Any]) -> dict[str, str]:
    """Legacy merge helper - prefer merge_and_validate() for new code."""
    values = dict(deterministic_plan.get("slots") or {})
    required_slots = completed_contract.get("required_slots") or {}
    for slot, value in required_slots.items():
        if slot in values and str(values.get(slot) or "").strip():
            continue
        values[slot] = str(value or "").strip()
    return values


def apply_completed_contract(
    item: dict[str, Any],
    deterministic_plan: dict[str, Any],
    completed_contract: dict[str, Any],
    *,
    strict_overwrite_check: bool = True,
) -> dict[str, Any]:
    """Apply completed slot contract to item, producing _v52_slots.

    Uses the hardened merge engine that:
    1. Ensures deterministic teacher-meaning slots always win.
    2. Prevents providers from overwriting deterministic slots.
    3. Validates all required prompted slots are filled.

    Args:
        item: The article item being built.
        deterministic_plan: Plan containing pre-filled deterministic slots.
        completed_contract: Contract with provider-filled required_slots.
        strict_overwrite_check: Raise error if provider tries to overwrite
            deterministic slots. Default True for safety.

    Returns:
        Updated item with _v52_slots and merge metadata.

    Raises:
        MergeError: If required slots are missing or validation fails.
        DeterministicSlotOverwriteAttempt: If provider overwrites deterministic
            slots and strict_overwrite_check is True.
        RuntimeError: Legacy error format for backwards compatibility.
    """
    article_id = item.get("id") or "unknown"
    template_id = item.get("template_id") or "hard_news_spiritual_response"

    include_non_standard = template_id in ("interfaith_dialogue_report", "unsay_dialogue")

    try:
        v52_slots, merge_warnings = merge_and_validate(
            article_id,
            template_id,
            deterministic_plan,
            completed_contract,
            strict_overwrite_check=strict_overwrite_check,
            include_non_standard_slots=include_non_standard,
        )
    except MergeError as e:
        raise RuntimeError(str(e)) from e
    except DeterministicSlotOverwriteAttempt as e:
        raise RuntimeError(str(e)) from e

    item["_deterministic_teacher_topic_pack"] = deterministic_plan.get("pack_path")
    item["_deterministic_beat_map"] = deterministic_plan.get("beat_map_id")
    item["_deterministic_article_plan"] = deterministic_plan.get("ordered_sections")
    item["_slot_contract_path"] = completed_contract.get("_path", "")
    item["_slot_source"] = "file"
    if merge_warnings:
        item["_merge_warnings"] = merge_warnings

    headline = " ".join(
        part.strip().rstrip(".")
        for part in [v52_slots.get("headline_layer_1", ""), v52_slots.get("headline_layer_2", "")]
        if str(part or "").strip()
    ).strip()
    if not headline:
        headline = item.get("raw_title") or item.get("title") or article_id

    body_parts = [f"<h1>{headline}</h1>"]
    for slot in STANDARD_V52_SLOTS[2:]:
        text = v52_slots.get(slot, "")
        if text:
            body_parts.append(_to_html_paragraph(text))
    source_url = item.get("url") or ""
    if source_url:
        body_parts.append(f'<p><em>Source: <a href="{source_url}">{source_url}</a></em></p>')
    item["content"] = "\n\n".join(part for part in body_parts if part.strip())

    item["_v52_slots"] = v52_slots
    return item
