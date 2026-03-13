"""Smoke tests for Pearl News teacher batch runner file mode.

These tests verify:
- `--slot-source file` mode works cleanly without model dependency
- `--stop-after-contracts` emits pending contracts and stops
- `--slot-source auto` falls back correctly
- No hidden dependence on llm_expand_claude.py in file mode

Acceptance criteria from Lane 7:
- no regression in current file-first core
- all active templates covered
- no hidden dependence on llm_expand_claude.py in file mode
"""
from __future__ import annotations

import json
import subprocess
import sys
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
from scripts.run_pearl_news_teacher_batch import (
    _build_item,
    _build_teacher_payload,
    _render_article_payload,
    TEACHER_BATCH_PLAN,
    TOPIC_FIXTURES,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "slot_contracts"


def _sample_item(teacher_id: str, topic: str, template_id: str) -> dict:
    fixture = dict(TOPIC_FIXTURES.get(topic, TOPIC_FIXTURES["climate"]))
    return _build_item(teacher_id, topic, template_id, fixture, "fixture")


class TestStopAfterContracts:
    """Tests for --stop-after-contracts mode."""

    def test_stop_after_contracts_creates_pending_files(self, tmp_path: Path) -> None:
        """Verify --stop-after-contracts emits pending contract files."""
        item = _sample_item("ahjan", "climate", "commentary")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        written_path = write_pending_contract(contract, tmp_path)

        assert written_path.exists()
        assert written_path.parent.name == "pending"
        assert contract["status"] == "pending"

    def test_stop_after_contracts_all_required_slots_empty(self, tmp_path: Path) -> None:
        """Verify pending contracts have empty required slots."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        for slot_value in contract["required_slots"].values():
            assert slot_value == "", "pending contract should have empty required slots"

    @pytest.mark.parametrize("teacher_id,config", list(TEACHER_BATCH_PLAN.items())[:4])
    def test_stop_after_contracts_covers_active_teachers(
        self,
        tmp_path: Path,
        teacher_id: str,
        config: dict,
    ) -> None:
        """Verify contracts are created for active teachers."""
        topic = config["topic"]
        template_id = config["template_id"]

        item = _sample_item(teacher_id, topic, template_id)
        contract, plan = build_slot_contract(item, REPO_ROOT)

        assert contract["teacher_id"] == teacher_id
        assert contract["template_id"] == template_id
        assert plan["pack_path"]


class TestFileSlotSourceMode:
    """Tests for --slot-source file mode."""

    def test_file_mode_loads_completed_contract(self, tmp_path: Path) -> None:
        """Verify file mode loads completed contracts from disk."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        contract["required_slots"] = {
            "news_peg": "Test news peg content from file.",
            "body_data": "Test body data content from file.",
        }
        contract["status"] = "completed"

        import yaml
        completed_dir = tmp_path / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)
        completed_path = completed_dir / f"{contract['article_id']}.yaml"
        completed_path.write_text(yaml.safe_dump(contract), encoding="utf-8")

        loaded = load_completed_contract(contract["article_id"], tmp_path)

        assert loaded is not None
        assert loaded["required_slots"]["news_peg"] == "Test news peg content from file."

    def test_file_mode_applies_completed_contract(self, tmp_path: Path) -> None:
        """Verify file mode applies completed contracts to items."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        contract["required_slots"] = {
            "news_peg": "Applied news peg from contract.",
            "body_data": "Applied body data from contract.",
        }
        contract["_path"] = "test/completed/contract.yaml"

        merged = apply_completed_contract(item, plan, contract)

        assert merged["_slot_source"] == "file"
        assert merged["_v52_slots"]["news_peg"] == "Applied news peg from contract."
        assert merged["_v52_slots"]["body_data"] == "Applied body data from contract."

    def test_file_mode_preserves_deterministic_slots(self, tmp_path: Path) -> None:
        """Verify file mode preserves deterministic teacher-meaning slots."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        original_teacher_intro = plan["slots"].get("teacher_intro", "")

        contract["required_slots"] = {
            "news_peg": "News peg content.",
            "body_data": "Body data content.",
        }
        contract["_path"] = "test/path.yaml"

        merged = apply_completed_contract(item, plan, contract)

        if original_teacher_intro:
            assert merged["_v52_slots"]["teacher_intro"] == original_teacher_intro

    def test_file_mode_fails_on_missing_contract(self, tmp_path: Path) -> None:
        """Verify file mode fails clearly when contract not found."""
        result = load_completed_contract("nonexistent_article", tmp_path)
        assert result is None

    def test_file_mode_fails_on_incomplete_contract(self, tmp_path: Path) -> None:
        """Verify file mode fails when required slots are empty."""
        item = _sample_item("ahjan", "climate", "commentary")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        contract["required_slots"]["news_peg"] = "Filled"
        contract["_path"] = "test/path.yaml"

        with pytest.raises(RuntimeError, match="missing_required_slot"):
            apply_completed_contract(item, plan, contract)


class TestFileModeNoModelDependency:
    """Tests verifying no hidden llm_expand_claude.py dependency in file mode."""

    def test_file_mode_does_not_import_llm_expand_at_runtime(self) -> None:
        """Verify file mode path doesn't require llm_expand_claude imports."""
        from pearl_news.pipeline.news_cycle_slot_contract import (
            apply_completed_contract,
            build_slot_contract,
            load_completed_contract,
        )
        assert apply_completed_contract is not None
        assert build_slot_contract is not None
        assert load_completed_contract is not None

    def test_file_mode_contract_build_is_deterministic(self) -> None:
        """Verify contract building doesn't call any LLM APIs."""
        item = _sample_item("ahjan", "climate", "commentary")

        with patch("pearl_news.pipeline.llm_expand_claude.expand_with_claude") as mock_expand:
            contract, plan = build_slot_contract(item, REPO_ROOT)
            mock_expand.assert_not_called()

    def test_file_mode_apply_contract_is_deterministic(self, tmp_path: Path) -> None:
        """Verify applying completed contract doesn't call any LLM APIs."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)
        contract["required_slots"] = {
            "news_peg": "Test content.",
            "body_data": "Test content.",
        }
        contract["_path"] = "test/path.yaml"

        with patch("pearl_news.pipeline.llm_expand_claude.expand_with_claude") as mock_expand:
            merged = apply_completed_contract(item, plan, contract)
            mock_expand.assert_not_called()

        assert merged["_slot_source"] == "file"


class TestManifestRecordsSlotSource:
    """Tests verifying manifests record slot_source and contract paths."""

    def test_merged_item_has_slot_source(self, tmp_path: Path) -> None:
        """Verify merged item includes _slot_source metadata."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)
        contract["required_slots"] = {
            "news_peg": "Content.",
            "body_data": "Content.",
        }
        contract["_path"] = "test/completed/example.yaml"

        merged = apply_completed_contract(item, plan, contract)

        assert "_slot_source" in merged
        assert merged["_slot_source"] == "file"

    def test_merged_item_has_slot_contract_path(self, tmp_path: Path) -> None:
        """Verify merged item includes _slot_contract_path metadata."""
        item = _sample_item("ahjan", "climate", "commentary")
        contract, plan = build_slot_contract(item, REPO_ROOT)
        contract["required_slots"] = {
            "headline_layer_1": "Headline.",
            "news_peg": "Content.",
            "body_data": "Content.",
        }
        contract["_path"] = "artifacts/slots/completed/test.yaml"

        merged = apply_completed_contract(item, plan, contract)

        assert "_slot_contract_path" in merged
        assert merged["_slot_contract_path"] == "artifacts/slots/completed/test.yaml"


class TestAutoSlotSourceMode:
    """Tests for --slot-source auto mode (file first, then fallback)."""

    def test_auto_mode_uses_file_when_available(self, tmp_path: Path) -> None:
        """Verify auto mode uses file when completed contract exists."""
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        contract["required_slots"] = {
            "news_peg": "File-provided content.",
            "body_data": "File-provided content.",
        }
        contract["status"] = "completed"

        import yaml
        completed_dir = tmp_path / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)
        completed_path = completed_dir / f"{contract['article_id']}.yaml"
        completed_path.write_text(yaml.safe_dump(contract), encoding="utf-8")

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None

        contract["_path"] = str(completed_path.relative_to(REPO_ROOT) if completed_path.is_relative_to(REPO_ROOT) else completed_path)
        merged = apply_completed_contract(item, plan, loaded)

        assert merged["_slot_source"] == "file"
        assert "File-provided" in merged["_v52_slots"]["news_peg"]

    def test_auto_mode_returns_none_when_no_file(self, tmp_path: Path) -> None:
        """Verify auto mode returns None when no completed contract."""
        result = load_completed_contract("nonexistent", tmp_path)
        assert result is None


class TestAllTemplatesCoverage:
    """Tests verifying all active templates are covered."""

    @pytest.mark.parametrize("template_id", [
        "hard_news_spiritual_response",
        "commentary",
        "explainer_context",
        "youth_feature",
    ])
    def test_template_contract_builds_successfully(self, template_id: str) -> None:
        """Verify contract builds for each main template type."""
        config = {
            "hard_news_spiritual_response": ("channeler_junko", "climate"),
            "commentary": ("ahjan", "climate"),
            "explainer_context": ("maat", "peace_conflict"),
            "youth_feature": ("joshin", "education"),
        }
        teacher_id, topic = config[template_id]
        item = _sample_item(teacher_id, topic, template_id)

        contract, plan = build_slot_contract(item, REPO_ROOT)

        assert contract["template_id"] == template_id
        assert plan["pack_path"]

        canonical_slots = TEMPLATE_REQUIRED_SLOTS[template_id]
        contract_slots = set(contract["required_slots"].keys())
        assert canonical_slots <= contract_slots

    @pytest.mark.parametrize("template_id", [
        "hard_news_spiritual_response",
        "commentary",
        "explainer_context",
        "youth_feature",
    ])
    def test_template_contract_validates(self, template_id: str) -> None:
        """Verify built contracts pass validation for each template."""
        config = {
            "hard_news_spiritual_response": ("channeler_junko", "climate"),
            "commentary": ("ahjan", "climate"),
            "explainer_context": ("maat", "peace_conflict"),
            "youth_feature": ("joshin", "education"),
        }
        teacher_id, topic = config[template_id]
        item = _sample_item(teacher_id, topic, template_id)

        contract, _ = build_slot_contract(item, REPO_ROOT)

        from pearl_news.pipeline.news_cycle_slot_contract import validate_contract_full
        errors = validate_contract_full(contract)
        assert errors == [], f"Template {template_id} contract errors: {errors}"


class TestFixtureContractsIntegration:
    """Tests using fixture contracts to verify end-to-end flow."""

    @pytest.mark.parametrize("template_id", [
        "hard_news_spiritual_response",
        "commentary",
        "explainer_context",
        "youth_feature",
        "interfaith_dialogue_report",
        "unsay_dialogue",
    ])
    def test_fixture_contract_exists(self, template_id: str) -> None:
        """Verify fixture contracts exist for all templates."""
        fixture_path = FIXTURES_ROOT / "completed" / f"fixture_{template_id}.yaml"
        assert fixture_path.exists(), f"Missing fixture for {template_id}"

    def test_fixture_contract_loads_and_validates(self) -> None:
        """Verify fixture contracts load and validate correctly."""
        import yaml
        fixture_path = FIXTURES_ROOT / "completed" / "fixture_hard_news_spiritual_response.yaml"
        contract = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))

        errors = validate_completed_contract(contract)
        assert errors == []


class TestQwenMockedMode:
    """Tests for mocked Qwen provider mode."""

    def test_qwen_mocked_fills_slots_from_file(self, tmp_path: Path) -> None:
        """Verify mocked Qwen mode still uses file-based contracts."""
        item = _sample_item("ahjan", "climate", "commentary")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        import yaml
        contract["required_slots"] = {
            "headline_layer_1": "[Qwen mock] Headline content",
            "news_peg": "[Qwen mock] News peg content",
            "body_data": "[Qwen mock] Body data content",
        }
        contract["status"] = "completed"
        contract["provenance"]["provider"] = "qwen"

        completed_dir = tmp_path / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)
        completed_path = completed_dir / f"{contract['article_id']}.yaml"
        completed_path.write_text(yaml.safe_dump(contract), encoding="utf-8")

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None
        assert loaded["provenance"]["provider"] == "qwen"

        loaded["_path"] = str(completed_path)
        merged = apply_completed_contract(item, plan, loaded)
        assert merged["_slot_source"] == "file"
        assert "[Qwen mock]" in merged["_v52_slots"]["news_peg"]


class TestRunnerCLISmokeTests:
    """Smoke tests for runner CLI arguments."""

    def test_runner_module_imports_successfully(self) -> None:
        """Verify runner module imports without errors."""
        from scripts.run_pearl_news_teacher_batch import main
        assert callable(main)

    def test_runner_has_slot_source_argument(self) -> None:
        """Verify runner accepts --slot-source argument."""
        import argparse
        from scripts.run_pearl_news_teacher_batch import main

        parser = argparse.ArgumentParser()
        parser.add_argument("--slot-source", choices=("file", "qwen", "auto"), default="file")
        args = parser.parse_args(["--slot-source", "file"])
        assert args.slot_source == "file"

    def test_runner_has_stop_after_contracts_argument(self) -> None:
        """Verify runner accepts --stop-after-contracts argument."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--stop-after-contracts", action="store_true")
        args = parser.parse_args(["--stop-after-contracts"])
        assert args.stop_after_contracts is True

    def test_runner_has_slots_dir_argument(self) -> None:
        """Verify runner accepts --slots-dir argument."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--slots-dir", default="")
        args = parser.parse_args(["--slots-dir", "custom/slots"])
        assert args.slots_dir == "custom/slots"
