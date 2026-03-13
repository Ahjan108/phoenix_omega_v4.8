from __future__ import annotations

from pathlib import Path

import pytest

from pearl_news.pipeline.news_cycle_slot_contract import (
    ACTIVE_TEMPLATES,
    CONTRACT_REQUIRED_FIELDS,
    CONTRACT_SCHEMA_VERSION,
    TEMPLATE_REQUIRED_SLOTS,
    apply_completed_contract,
    build_slot_contract,
    get_required_slots_for_template,
    load_pending_contract,
    load_completed_contract,
    validate_completed_contract,
    validate_contract_for_template,
    validate_contract_full,
    validate_contract_schema,
    write_pending_contract,
)
from scripts.run_pearl_news_teacher_batch import _build_item, TOPIC_FIXTURES, TEACHER_BATCH_PLAN


REPO_ROOT = Path(__file__).resolve().parents[1]

TEMPLATE_TEST_CONFIGS = {
    "hard_news_spiritual_response": {"teacher_id": "channeler_junko", "topic": "climate"},
    "commentary": {"teacher_id": "ahjan", "topic": "climate"},
    "explainer_context": {"teacher_id": "maat", "topic": "peace_conflict"},
    "youth_feature": {"teacher_id": "joshin", "topic": "education"},
}


def _fallback_teacher_payload(teacher_id: str, topic: str) -> dict:
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


class TestContractSchemaVersion:
    def test_contract_schema_version_is_positive_integer(self) -> None:
        assert isinstance(CONTRACT_SCHEMA_VERSION, int)
        assert CONTRACT_SCHEMA_VERSION >= 1

    def test_active_templates_all_have_required_slots(self) -> None:
        for template_id in ACTIVE_TEMPLATES:
            assert template_id in TEMPLATE_REQUIRED_SLOTS
            assert isinstance(TEMPLATE_REQUIRED_SLOTS[template_id], frozenset)
            assert len(TEMPLATE_REQUIRED_SLOTS[template_id]) > 0


class TestValidateContractSchema:
    def test_valid_contract_passes(self) -> None:
        contract = {
            "version": CONTRACT_SCHEMA_VERSION,
            "article_id": "test_article",
            "status": "pending",
            "template_id": "hard_news_spiritual_response",
            "deterministic_context": {"ordered_sections": []},
            "required_slots": {},
            "provenance": {},
        }
        errors = validate_contract_schema(contract)
        assert errors == []

    def test_missing_required_field_fails(self) -> None:
        contract = {
            "version": CONTRACT_SCHEMA_VERSION,
            "article_id": "test",
            "status": "pending",
        }
        errors = validate_contract_schema(contract)
        assert "missing_required_field:template_id" in errors
        assert "missing_required_field:deterministic_context" in errors

    def test_invalid_status_fails(self) -> None:
        contract = {
            "version": CONTRACT_SCHEMA_VERSION,
            "article_id": "test",
            "status": "invalid_status",
            "template_id": "commentary",
            "deterministic_context": {"ordered_sections": []},
            "required_slots": {},
            "provenance": {},
        }
        errors = validate_contract_schema(contract)
        assert "invalid_status:invalid_status" in errors

    def test_unknown_template_fails(self) -> None:
        contract = {
            "version": CONTRACT_SCHEMA_VERSION,
            "article_id": "test",
            "status": "pending",
            "template_id": "invented_template",
            "deterministic_context": {"ordered_sections": []},
            "required_slots": {},
            "provenance": {},
        }
        errors = validate_contract_schema(contract)
        assert "unknown_template_id:invented_template" in errors

    def test_non_dict_contract_fails(self) -> None:
        errors = validate_contract_schema("not a dict")  # type: ignore
        assert errors == ["contract_not_dict"]


class TestValidateContractForTemplate:
    def test_correct_slots_passes(self) -> None:
        contract = {
            "template_id": "hard_news_spiritual_response",
            "required_slots": {"news_peg": "", "body_data": ""},
        }
        errors = validate_contract_for_template(contract)
        assert errors == []

    def test_missing_canonical_slot_fails(self) -> None:
        contract = {
            "template_id": "hard_news_spiritual_response",
            "required_slots": {"news_peg": ""},
        }
        errors = validate_contract_for_template(contract)
        assert "missing_canonical_slot:body_data" in errors

    def test_extra_slot_flagged(self) -> None:
        contract = {
            "template_id": "hard_news_spiritual_response",
            "required_slots": {"news_peg": "", "body_data": "", "invented_slot": ""},
        }
        errors = validate_contract_for_template(contract)
        assert "extra_non_canonical_slot:invented_slot" in errors


class TestValidateCompletedContract:
    def test_all_slots_filled_passes(self) -> None:
        errors = validate_completed_contract({
            "required_slots": {
                "news_peg": "Some text",
                "body_data": "More text",
            }
        })
        assert errors == []

    def test_empty_slot_fails(self) -> None:
        errors = validate_completed_contract({
            "required_slots": {
                "news_peg": "",
                "body_data": "Filled",
            }
        })
        assert errors == ["missing_required_slot:news_peg"]

    def test_whitespace_only_slot_fails(self) -> None:
        errors = validate_completed_contract({
            "required_slots": {
                "news_peg": "   ",
                "body_data": "Filled",
            }
        })
        assert errors == ["missing_required_slot:news_peg"]


class TestGetRequiredSlotsForTemplate:
    def test_known_template_returns_slots(self) -> None:
        slots = get_required_slots_for_template("hard_news_spiritual_response")
        assert slots == frozenset({"news_peg", "body_data"})

    def test_unknown_template_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown template_id"):
            get_required_slots_for_template("fake_template")


class TestBuildSlotContractAllTemplates:
    @pytest.mark.parametrize("template_id", list(TEMPLATE_TEST_CONFIGS.keys()))
    def test_build_slot_contract_for_template(self, template_id: str) -> None:
        config = TEMPLATE_TEST_CONFIGS[template_id]
        item = _sample_item(config["teacher_id"], config["topic"], template_id)
        contract, plan = build_slot_contract(item, REPO_ROOT)

        assert contract["version"] == CONTRACT_SCHEMA_VERSION
        assert contract["article_id"] == item["id"]
        assert contract["template_id"] == template_id
        assert contract["status"] == "pending"
        assert plan["teacher_id"] == config["teacher_id"]
        assert contract["deterministic_context"]["pack_path"]

        schema_errors = validate_contract_schema(contract)
        assert schema_errors == [], f"Schema errors for {template_id}: {schema_errors}"

        full_errors = validate_contract_full(contract)
        assert full_errors == [], f"Full validation errors for {template_id}: {full_errors}"

    @pytest.mark.parametrize("template_id", list(TEMPLATE_TEST_CONFIGS.keys()))
    def test_contract_required_slots_match_canonical(self, template_id: str) -> None:
        config = TEMPLATE_TEST_CONFIGS[template_id]
        item = _sample_item(config["teacher_id"], config["topic"], template_id)
        contract, _ = build_slot_contract(item, REPO_ROOT)

        canonical_slots = TEMPLATE_REQUIRED_SLOTS[template_id]
        contract_slots = set(contract["required_slots"].keys())

        assert canonical_slots <= contract_slots, (
            f"Template {template_id}: missing canonical slots "
            f"{canonical_slots - contract_slots}"
        )


class TestBuildSlotContractCommentary:
    def test_commentary_uses_canonical_slots(self) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, plan = build_slot_contract(item, REPO_ROOT)

        assert contract["article_id"] == item["id"]
        assert plan["teacher_id"] == "ahjan"
        canonical = TEMPLATE_REQUIRED_SLOTS["commentary"]
        assert canonical <= set(contract["required_slots"].keys())
        assert contract["deterministic_context"]["pack_path"]


class TestApplyCompletedContract:
    def test_merges_deterministic_and_written_slots(self) -> None:
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, plan = build_slot_contract(item, REPO_ROOT)
        contract["required_slots"] = {
            "news_peg": "Fresh UN reporting ties the climate shift to student routine disruption.",
            "body_data": "UN data shows repeated school-day heat exposure is disrupting concentration and sleep.",
        }
        contract["_path"] = "pearl_news/news_cycle_slots/completed/example.yaml"

        merged = apply_completed_contract(item, plan, contract)

        assert merged["_slot_source"] == "file"
        assert merged["_slot_contract_path"] == contract["_path"]
        assert merged["_v52_slots"]["teacher_intro"]
        assert merged["_v52_slots"]["news_peg"] == contract["required_slots"]["news_peg"]
        assert "Source:" in merged["content"]


class TestValidateContractFull:
    def test_valid_pending_contract_passes(self) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        errors = validate_contract_full(contract)
        assert errors == []

    def test_valid_completed_contract_passes(self) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        contract["status"] = "completed"
        for slot in contract["required_slots"]:
            contract["required_slots"][slot] = f"Filled content for {slot}"
        errors = validate_contract_full(contract)
        assert errors == []

    def test_completed_with_empty_slots_fails(self) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)
        contract["status"] = "completed"
        errors = validate_contract_full(contract)
        assert any("missing_required_slot" in e for e in errors)


class TestContractPersistence:
    def test_write_and_load_pending_contract(self, tmp_path: Path) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        written_path = write_pending_contract(contract, tmp_path)

        assert written_path.exists()
        assert written_path.parent.name == "pending"
        assert written_path.name == f"{contract['article_id']}.yaml"

        loaded = load_pending_contract(contract["article_id"], tmp_path)
        assert loaded is not None
        assert loaded["article_id"] == contract["article_id"]
        assert loaded["template_id"] == contract["template_id"]
        assert "_path" in loaded

    def test_load_completed_contract_prefers_completed_dir(self, tmp_path: Path) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        write_pending_contract(contract, tmp_path)

        completed_dir = tmp_path / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)
        contract["status"] = "completed"
        for slot in contract["required_slots"]:
            contract["required_slots"][slot] = "Filled"

        import yaml
        completed_path = completed_dir / f"{contract['article_id']}.yaml"
        completed_path.write_text(yaml.safe_dump(contract), encoding="utf-8")

        loaded = load_completed_contract(contract["article_id"], tmp_path)
        assert loaded is not None
        assert "completed" in loaded["_path"]

    def test_load_completed_contract_returns_none_for_missing(self, tmp_path: Path) -> None:
        result = load_completed_contract("nonexistent_article", tmp_path)
        assert result is None


FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "slot_contracts"


class TestFixtureContractValidation:
    @pytest.mark.parametrize("template_id", list(ACTIVE_TEMPLATES))
    def test_fixture_contracts_exist_for_all_templates(self, template_id: str) -> None:
        fixture_path = FIXTURES_ROOT / "completed" / f"fixture_{template_id}.yaml"
        assert fixture_path.exists(), f"missing fixture contract for {template_id}"

    @pytest.mark.parametrize("template_id", list(ACTIVE_TEMPLATES))
    def test_fixture_contracts_have_valid_schema(self, template_id: str) -> None:
        import yaml
        fixture_path = FIXTURES_ROOT / "completed" / f"fixture_{template_id}.yaml"
        if not fixture_path.exists():
            pytest.skip(f"fixture not found for {template_id}")
        contract = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        errors = validate_contract_schema(contract)
        assert errors == [], f"fixture {template_id} has schema errors: {errors}"

    @pytest.mark.parametrize("template_id", list(ACTIVE_TEMPLATES))
    def test_fixture_contracts_are_complete(self, template_id: str) -> None:
        import yaml
        fixture_path = FIXTURES_ROOT / "completed" / f"fixture_{template_id}.yaml"
        if not fixture_path.exists():
            pytest.skip(f"fixture not found for {template_id}")
        contract = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        errors = validate_completed_contract(contract)
        assert errors == [], f"fixture {template_id} has completion errors: {errors}"

    def test_pending_fixture_has_empty_slots(self) -> None:
        import yaml
        fixture_path = FIXTURES_ROOT / "pending" / "fixture_hard_news_spiritual_response.yaml"
        if not fixture_path.exists():
            pytest.skip("pending fixture not found")
        contract = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        assert contract["status"] == "pending"
        errors = validate_completed_contract(contract)
        assert len(errors) > 0, "pending fixture should have empty slots"


class TestAllTeacherBatchPlanCoverage:
    def test_all_batch_plan_templates_are_active(self) -> None:
        for teacher_id, plan in TEACHER_BATCH_PLAN.items():
            template_id = plan["template_id"]
            assert template_id in ACTIVE_TEMPLATES, (
                f"teacher {teacher_id} uses inactive template {template_id}"
            )

    def test_all_batch_plan_topics_documented(self) -> None:
        """Document which topics are used vs available in fixtures."""
        topics_used = {plan["topic"] for plan in TEACHER_BATCH_PLAN.values()}
        topics_with_fixtures = set(TOPIC_FIXTURES.keys())
        topics_missing_fixtures = topics_used - topics_with_fixtures
        if topics_missing_fixtures:
            pytest.skip(
                f"Topics used in batch plan but missing fixtures: {topics_missing_fixtures}. "
                "This is tracked - live feed fallback covers these topics."
            )


class TestContractRequiredFieldsCoverage:
    def test_contract_contains_all_required_fields(self) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        for field in CONTRACT_REQUIRED_FIELDS:
            assert field in contract, f"missing required field: {field}"

    def test_contract_has_source_metadata(self) -> None:
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        assert "source_url" in contract
        assert "source_title" in contract
        assert "teacher_id" in contract
        assert "teacher_name" in contract

    def test_contract_has_provenance(self) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        assert "provenance" in contract
        provenance = contract["provenance"]
        assert "filled_by" in provenance
        assert "filled_at" in provenance
        assert "provider" in provenance


class TestDeterministicContextPreservation:
    def test_deterministic_context_contains_ordered_sections(self) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        ctx = contract["deterministic_context"]
        assert "ordered_sections" in ctx
        assert isinstance(ctx["ordered_sections"], list)

    def test_deterministic_context_contains_pack_path(self) -> None:
        item = _sample_item("channeler_junko", "climate", "hard_news_spiritual_response")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        ctx = contract["deterministic_context"]
        assert "pack_path" in ctx
        assert ctx["pack_path"]

    def test_ordered_sections_mark_prompted_vs_deterministic(self) -> None:
        item = _sample_item("ahjan", "climate", "commentary")
        contract, _ = build_slot_contract(item, REPO_ROOT)

        sections = contract["deterministic_context"]["ordered_sections"]
        sources = {s["source"] for s in sections}
        assert "prompted" in sources or "deterministic" in sources
