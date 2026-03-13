"""Tests for Qwen slot provider.

These tests mock the Qwen provider interface to verify:
- Provider only fills allowed slots (not deterministic teacher-meaning slots)
- Provider writes completed slot contract file
- Provider output is consumable by assembler exactly like file mode
- No direct model dependency bypasses slot file artifacts

Note: The actual provider implementation is in slot_provider_qwen.py (Dev 4).
These tests define the expected interface and behavior contract.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pearl_news.pipeline.news_cycle_slot_contract import (
    ACTIVE_TEMPLATES,
    TEMPLATE_REQUIRED_SLOTS,
    apply_completed_contract,
    build_slot_contract,
    load_completed_contract,
    validate_completed_contract,
    write_pending_contract,
)
from pearl_news.pipeline.slot_provider_qwen import _load_qwen_api_key_from_file
from scripts.run_pearl_news_teacher_batch import _build_item, TOPIC_FIXTURES


REPO_ROOT = Path(__file__).resolve().parents[1]


def _fallback_teacher_payload(teacher_id: str, topic: str) -> dict[str, Any]:
    display_name = teacher_id.replace("_", " ").title()
    framework = f"{topic.replace('_', ' ')} grounding"
    return {
        "teacher_id": teacher_id,
        "display_name": display_name,
        "tradition": "Test Tradition",
        "attribution": f"From within the Test Tradition, {display_name} teaches that",
        "atoms": [
            f"{display_name} names the pressure directly.",
            f"{display_name} points toward grounded action.",
            f"{display_name} refuses false helplessness.",
        ],
        "teacher_framework_term": framework,
        "teacher_diagnostic_claim": "The pressure is real and shaped by larger conditions.",
        "teacher_named_practice": "Return to one grounded breath and one next step.",
        "teacher_quotes": [
            f"{display_name} says the body is responding to real pressure.",
            f"{display_name} says practice should reduce confusion, not add to it.",
            f"{display_name} says truth should become action.",
        ],
        "teacher_safety_boundary": "This article is not medical, legal, or crisis advice.",
        "teacher_behavior_bridge": "Choose one concrete stabilizing action today.",
        "teacher_civic_bridge": "Take one local action with others where possible.",
    }


def _sample_item(teacher_id: str, topic: str, template_id: str) -> dict:
    fixture = dict(TOPIC_FIXTURES.get(topic, TOPIC_FIXTURES["climate"]))
    try:
        return _build_item(teacher_id, topic, template_id, fixture, "fixture")
    except RuntimeError as exc:
        if "no Pearl News teacher payload" not in str(exc):
            raise
        raw_title = fixture.get("raw_title") or fixture.get("title") or f"{topic.title()} update"
        raw_summary = fixture.get("raw_summary") or fixture.get("summary") or ""
        return {
            "id": f"teacher_{teacher_id}_{topic}_{template_id}",
            "template_id": template_id,
            "topic": topic,
            "primary_sdg": fixture.get("primary_sdg", "17"),
            "sdg_labels": fixture.get("sdg_labels") or {"17": "Partnerships for the Goals"},
            "un_body": fixture.get("un_body") or "United Nations",
            "raw_title": raw_title,
            "raw_summary": raw_summary,
            "title": raw_title,
            "summary": raw_summary,
            "url": fixture.get("url", ""),
            "pub_date": fixture.get("pub_date", ""),
            "language": "en",
            "source_feed_id": "fixture",
            "_teacher_resolved": _fallback_teacher_payload(teacher_id, topic),
            "_batch_source_mode": "fixture",
            "_batch_source_title": raw_title,
            "_news_actions": {},
        }


class TestQwenApiKeyFileLoading:
    def test_loads_api_key_from_docs_file_format(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        key_path = docs_dir / "qwen_api_key.txt"
        key_path.write_text('Api key= "sk-test-12345"\n', encoding="utf-8")

        loaded = _load_qwen_api_key_from_file(tmp_path)
        assert loaded == "sk-test-12345"

    def test_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        assert _load_qwen_api_key_from_file(tmp_path) == ""


class MockQwenSlotProvider:
    """Mock Qwen provider that fills slots with deterministic test content.

    This mock simulates the expected behavior of the real Qwen provider:
    - Reads pending slot contract
    - Fills only the required (prompted) slots
    - Writes completed slot contract to file
    - Does NOT overwrite deterministic slots
    """

    def __init__(self, slots_dir: Path) -> None:
        self.slots_dir = slots_dir
        self.api_calls: list[dict[str, Any]] = []

    def fill_contract(self, article_id: str) -> Path | None:
        """Fill a pending contract and write to completed directory.

        Returns path to completed contract, or None if pending not found.
        """
        pending_path = self.slots_dir / "pending" / f"{article_id}.yaml"
        if not pending_path.exists():
            return None

        import yaml
        contract = yaml.safe_load(pending_path.read_text(encoding="utf-8"))

        filled_slots = {}
        for slot_name in contract.get("required_slots", {}):
            filled_slots[slot_name] = f"[Qwen-generated content for {slot_name}]"
            self.api_calls.append({
                "slot": slot_name,
                "article_id": article_id,
            })

        contract["required_slots"] = filled_slots
        contract["status"] = "completed"
        contract["provenance"] = {
            "filled_by": "qwen_provider_mock",
            "filled_at": "2026-03-13T10:00:00+00:00",
            "provider": "qwen",
        }

        completed_dir = self.slots_dir / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)
        completed_path = completed_dir / f"{article_id}.yaml"
        completed_path.write_text(
            yaml.safe_dump(contract, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

        return completed_path


class TestMockQwenProviderInterface:
    def test_provider_reads_pending_contract(self, tmp_path: Path) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        completed_path = provider.fill_contract(contract["article_id"])

        assert completed_path is not None
        assert completed_path.exists()

    def test_provider_fills_only_required_slots(self, tmp_path: Path) -> None:
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        original_required_slots = set(contract["required_slots"].keys())
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        provider.fill_contract(contract["article_id"])

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None
        filled_slots = set(loaded["required_slots"].keys())
        assert filled_slots == original_required_slots

    def test_provider_writes_to_completed_directory(self, tmp_path: Path) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        completed_path = provider.fill_contract(contract["article_id"])

        assert completed_path is not None
        assert completed_path.parent.name == "completed"

    def test_provider_returns_none_for_missing_pending(self, tmp_path: Path) -> None:
        provider = MockQwenSlotProvider(tmp_path)
        result = provider.fill_contract("nonexistent_article")
        assert result is None

    def test_provider_sets_provenance_to_qwen(self, tmp_path: Path) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        provider.fill_contract(contract["article_id"])

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None
        assert loaded["provenance"]["provider"] == "qwen"


class TestQwenProviderCompletedContractValidation:
    def test_qwen_completed_contract_validates(self, tmp_path: Path) -> None:
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        provider.fill_contract(contract["article_id"])

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None
        errors = validate_completed_contract(loaded)
        assert errors == [], f"Qwen-filled contract has errors: {errors}"

    @pytest.mark.parametrize("template_id,teacher_id,topic", [
        ("hard_news_spiritual_response", "channeler_junko", "climate"),
        ("commentary", "ahjan", "climate"),
        ("explainer_context", "maat", "peace_conflict"),
        ("youth_feature", "joshin", "education"),
    ])
    def test_qwen_fills_all_canonical_slots(
        self,
        tmp_path: Path,
        template_id: str,
        teacher_id: str,
        topic: str,
    ) -> None:
        item = _sample_item(teacher_id, topic, template_id)
        contract, _ = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        provider.fill_contract(contract["article_id"])

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None

        canonical_slots = TEMPLATE_REQUIRED_SLOTS[template_id]
        filled_slots = set(loaded["required_slots"].keys())
        missing = canonical_slots - filled_slots
        assert not missing, f"Qwen provider missed canonical slots: {missing}"


class TestQwenProviderAssemblerIntegration:
    def test_qwen_output_usable_by_assembler(self, tmp_path: Path) -> None:
        """Verify Qwen-filled contract can be consumed by apply_completed_contract."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        provider.fill_contract(contract["article_id"])

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None

        merged = apply_completed_contract(item, plan, loaded)

        assert merged["_slot_source"] == "file"
        assert "_v52_slots" in merged
        assert "content" in merged
        assert merged["_v52_slots"]["news_peg"]
        assert merged["_v52_slots"]["body_data"]

    def test_qwen_output_preserves_deterministic_teacher_slots(self, tmp_path: Path) -> None:
        """Verify deterministic teacher-meaning slots are not overwritten."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        deterministic_teacher_intro = plan["slots"].get("teacher_intro", "")
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        provider.fill_contract(contract["article_id"])

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None

        merged = apply_completed_contract(item, plan, loaded)

        if deterministic_teacher_intro:
            assert merged["_v52_slots"]["teacher_intro"] == deterministic_teacher_intro


class TestQwenProviderDoesNotBypassSlotFile:
    def test_provider_does_not_inject_content_directly(self, tmp_path: Path) -> None:
        """Verify provider writes file, not returns content directly."""
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        result = provider.fill_contract(contract["article_id"])

        assert isinstance(result, Path)
        assert result.exists()

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None

    def test_assembler_reads_from_file_not_provider(self, tmp_path: Path) -> None:
        """Verify assembly uses load_completed_contract, not provider directly."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        provider.fill_contract(contract["article_id"])

        loaded = load_completed_contract(contract["article_id"], tmp_path)

        merged = apply_completed_contract(item, plan, loaded)
        assert merged["_slot_contract_path"]


class TestQwenProviderAPICallTracking:
    def test_provider_tracks_api_calls_per_slot(self, tmp_path: Path) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        write_pending_contract(contract, tmp_path)

        provider = MockQwenSlotProvider(tmp_path)
        provider.fill_contract(contract["article_id"])

        assert len(provider.api_calls) == len(contract["required_slots"])
        slots_called = {call["slot"] for call in provider.api_calls}
        assert slots_called == set(contract["required_slots"].keys())


class TestQwenProviderErrorHandling:
    def test_provider_handles_invalid_yaml_gracefully(self, tmp_path: Path) -> None:
        pending_dir = tmp_path / "pending"
        pending_dir.mkdir(parents=True, exist_ok=True)
        invalid_path = pending_dir / "invalid_article.yaml"
        invalid_path.write_text("invalid: yaml: content: [", encoding="utf-8")

        provider = MockQwenSlotProvider(tmp_path)

        with pytest.raises(Exception):
            provider.fill_contract("invalid_article")

    def test_provider_handles_missing_required_slots_key(self, tmp_path: Path) -> None:
        import yaml

        pending_dir = tmp_path / "pending"
        pending_dir.mkdir(parents=True, exist_ok=True)
        malformed_contract = {
            "version": 2,
            "article_id": "malformed_article",
            "status": "pending",
            "template_id": "commentary",
        }
        malformed_path = pending_dir / "malformed_article.yaml"
        malformed_path.write_text(yaml.safe_dump(malformed_contract), encoding="utf-8")

        provider = MockQwenSlotProvider(tmp_path)
        result = provider.fill_contract("malformed_article")

        assert result is not None
        loaded = load_completed_contract("malformed_article", tmp_path)
        assert loaded is not None
        assert loaded["required_slots"] == {}
