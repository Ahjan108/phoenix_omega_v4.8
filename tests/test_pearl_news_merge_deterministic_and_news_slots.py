"""Tests for the Deterministic Merge Engine (Lane 2).

Acceptance criteria:
- deterministic slots always win
- missing required file slots fail clearly
- merged result produces valid _v52_slots
"""
from __future__ import annotations

import pytest

from pearl_news.pipeline.merge_deterministic_and_news_slots import (
    DeterministicSlotOverwriteAttempt,
    MergeError,
    PROMPTED_SLOTS_BY_TEMPLATE,
    STANDARD_V52_SLOTS,
    build_v52_slots,
    get_deterministic_slots,
    get_prompted_slots,
    merge_and_validate,
    merge_deterministic_and_provider_slots,
    validate_no_deterministic_overwrites,
    validate_required_slots_filled,
    validate_v52_slots,
)


class TestGetPromptedSlots:
    def test_hard_news_prompted_slots(self) -> None:
        slots = get_prompted_slots("hard_news_spiritual_response")
        assert slots == frozenset({"news_peg", "body_data"})

    def test_commentary_prompted_slots(self) -> None:
        slots = get_prompted_slots("commentary")
        assert slots == frozenset({"headline_layer_1", "news_peg", "body_data"})

    def test_explainer_prompted_slots(self) -> None:
        slots = get_prompted_slots("explainer_context")
        assert slots == frozenset({"headline_layer_1", "news_peg", "body_data"})

    def test_youth_feature_prompted_slots(self) -> None:
        slots = get_prompted_slots("youth_feature")
        assert slots == frozenset({"headline_layer_1", "news_peg", "body_data"})

    def test_interfaith_prompted_slots(self) -> None:
        slots = get_prompted_slots("interfaith_dialogue_report")
        assert slots == frozenset({"headline_layer_1", "event_summary"})

    def test_unsay_prompted_slots(self) -> None:
        slots = get_prompted_slots("unsay_dialogue")
        assert "headline_layer_1" in slots
        assert "event_summary" in slots
        assert "news_peg" in slots
        assert "body_data" in slots

    def test_unknown_template_returns_empty(self) -> None:
        slots = get_prompted_slots("unknown_template")
        assert slots == frozenset()


class TestGetDeterministicSlots:
    def test_deterministic_slots_exclude_prompted(self) -> None:
        plan = {
            "slots": {
                "teacher_intro": "Intro text",
                "youth_somatic": "Somatic text",
                "news_peg": "",
                "body_data": "",
            }
        }
        det_slots = get_deterministic_slots("hard_news_spiritual_response", plan)
        assert "teacher_intro" in det_slots
        assert "youth_somatic" in det_slots
        assert "news_peg" not in det_slots
        assert "body_data" not in det_slots


class TestValidateNoDeterministicOverwrites:
    def test_no_overwrite_passes(self) -> None:
        plan = {"slots": {"teacher_intro": "Original teacher intro"}}
        provider = {"news_peg": "News content"}
        warnings = validate_no_deterministic_overwrites(
            "article_1",
            "hard_news_spiritual_response",
            plan,
            provider,
            strict=True,
        )
        assert warnings == []

    def test_overwrite_attempt_raises_in_strict_mode(self) -> None:
        plan = {"slots": {"teacher_intro": "Original teacher intro"}}
        provider = {"teacher_intro": "Attempted overwrite"}
        with pytest.raises(DeterministicSlotOverwriteAttempt) as exc_info:
            validate_no_deterministic_overwrites(
                "article_1",
                "hard_news_spiritual_response",
                plan,
                provider,
                strict=True,
            )
        assert exc_info.value.slot == "teacher_intro"
        assert "Original teacher intro" in exc_info.value.deterministic_value
        assert "Attempted overwrite" in exc_info.value.attempted_value

    def test_overwrite_attempt_warns_in_non_strict_mode(self) -> None:
        plan = {"slots": {"teacher_intro": "Original teacher intro"}}
        provider = {"teacher_intro": "Attempted overwrite"}
        warnings = validate_no_deterministic_overwrites(
            "article_1",
            "hard_news_spiritual_response",
            plan,
            provider,
            strict=False,
        )
        assert len(warnings) == 1
        assert "teacher_intro" in warnings[0]
        assert "overwrite" in warnings[0]

    def test_empty_deterministic_slot_can_be_filled(self) -> None:
        plan = {"slots": {"teacher_intro": ""}}
        provider = {"teacher_intro": "Filled value"}
        warnings = validate_no_deterministic_overwrites(
            "article_1",
            "hard_news_spiritual_response",
            plan,
            provider,
            strict=True,
        )
        assert warnings == []

    def test_same_value_not_flagged(self) -> None:
        plan = {"slots": {"teacher_intro": "Same value"}}
        provider = {"teacher_intro": "Same value"}
        warnings = validate_no_deterministic_overwrites(
            "article_1",
            "hard_news_spiritual_response",
            plan,
            provider,
            strict=True,
        )
        assert warnings == []


class TestValidateRequiredSlotsFilled:
    def test_all_filled_passes(self) -> None:
        required = {"news_peg": "News content", "body_data": "Body content"}
        errors = validate_required_slots_filled("article_1", required)
        assert errors == []

    def test_empty_slot_fails(self) -> None:
        required = {"news_peg": "", "body_data": "Body content"}
        errors = validate_required_slots_filled("article_1", required)
        assert errors == ["missing_required_slot:news_peg"]

    def test_whitespace_only_slot_fails(self) -> None:
        required = {"news_peg": "   ", "body_data": "Body content"}
        errors = validate_required_slots_filled("article_1", required)
        assert errors == ["missing_required_slot:news_peg"]

    def test_multiple_missing_reported(self) -> None:
        required = {"news_peg": "", "body_data": ""}
        errors = validate_required_slots_filled("article_1", required)
        assert len(errors) == 2
        assert "missing_required_slot:news_peg" in errors
        assert "missing_required_slot:body_data" in errors


class TestMergeDeterministicAndProviderSlots:
    def test_deterministic_slots_always_win(self) -> None:
        plan = {
            "slots": {
                "teacher_intro": "Deterministic intro",
                "youth_somatic": "Deterministic somatic",
            }
        }
        contract = {
            "required_slots": {
                "news_peg": "Provider news peg",
                "body_data": "Provider body data",
            }
        }
        merged, warnings = merge_deterministic_and_provider_slots(
            "article_1",
            "hard_news_spiritual_response",
            plan,
            contract,
        )
        assert merged["teacher_intro"] == "Deterministic intro"
        assert merged["youth_somatic"] == "Deterministic somatic"
        assert merged["news_peg"] == "Provider news peg"
        assert merged["body_data"] == "Provider body data"

    def test_missing_required_slot_raises(self) -> None:
        plan = {"slots": {"teacher_intro": "Intro"}}
        contract = {"required_slots": {"news_peg": "", "body_data": "Content"}}
        with pytest.raises(MergeError) as exc_info:
            merge_deterministic_and_provider_slots(
                "article_1",
                "hard_news_spiritual_response",
                plan,
                contract,
            )
        assert "missing_required_slot:news_peg" in exc_info.value.errors

    def test_provider_cannot_overwrite_deterministic_in_strict_mode(self) -> None:
        plan = {"slots": {"teacher_intro": "Deterministic intro"}}
        contract = {
            "required_slots": {
                "news_peg": "Provider peg",
                "body_data": "Provider body",
            },
            "optional_slots": {"teacher_intro": "Attempted override"},
        }
        with pytest.raises(DeterministicSlotOverwriteAttempt):
            merge_deterministic_and_provider_slots(
                "article_1",
                "hard_news_spiritual_response",
                plan,
                contract,
                strict_overwrite_check=True,
            )

    def test_provider_overwrite_ignored_in_non_strict_mode(self) -> None:
        plan = {"slots": {"teacher_intro": "Deterministic intro"}}
        contract = {
            "required_slots": {
                "news_peg": "Provider peg",
                "body_data": "Provider body",
            },
            "optional_slots": {"teacher_intro": "Attempted override"},
        }
        merged, warnings = merge_deterministic_and_provider_slots(
            "article_1",
            "hard_news_spiritual_response",
            plan,
            contract,
            strict_overwrite_check=False,
        )
        assert merged["teacher_intro"] == "Deterministic intro"
        assert len(warnings) == 1
        assert "teacher_intro" in warnings[0]


class TestBuildV52Slots:
    def test_only_standard_slots_included_by_default(self) -> None:
        merged = {
            "teacher_intro": "Intro",
            "news_peg": "Peg",
            "custom_slot": "Custom",
            "sdg_un_tie": "SDG tie",
        }
        v52 = build_v52_slots(merged)
        assert "teacher_intro" in v52
        assert "news_peg" in v52
        assert "custom_slot" not in v52
        assert "sdg_un_tie" not in v52

    def test_non_standard_slots_included_when_requested(self) -> None:
        merged = {
            "teacher_intro": "Intro",
            "custom_slot": "Custom",
        }
        v52 = build_v52_slots(merged, include_non_standard=True)
        assert "teacher_intro" in v52
        assert "custom_slot" in v52

    def test_empty_slots_excluded(self) -> None:
        merged = {
            "teacher_intro": "Intro",
            "news_peg": "",
            "body_data": "   ",
        }
        v52 = build_v52_slots(merged)
        assert "teacher_intro" in v52
        assert "news_peg" not in v52
        assert "body_data" not in v52


class TestValidateV52Slots:
    def test_valid_slots_pass(self) -> None:
        plan = {
            "ordered_sections": [
                {"slot": "teacher_intro", "source": "deterministic", "content": "Intro"},
                {"slot": "news_peg", "source": "prompted", "content": ""},
            ]
        }
        v52 = {"teacher_intro": "Intro", "news_peg": "Peg content"}
        errors = validate_v52_slots("article_1", "hard_news", v52, plan)
        assert errors == []

    def test_missing_deterministic_slot_fails(self) -> None:
        plan = {
            "ordered_sections": [
                {"slot": "teacher_intro", "source": "deterministic", "content": "Intro"},
            ]
        }
        v52 = {}
        errors = validate_v52_slots("article_1", "hard_news", v52, plan)
        assert "missing_deterministic_slot:teacher_intro" in errors

    def test_missing_prompted_slot_fails(self) -> None:
        plan = {
            "ordered_sections": [
                {"slot": "news_peg", "source": "prompted", "content": ""},
            ]
        }
        v52 = {}
        errors = validate_v52_slots("article_1", "hard_news", v52, plan)
        assert "missing_prompted_slot:news_peg" in errors

    def test_non_standard_slots_skipped_by_default(self) -> None:
        plan = {
            "ordered_sections": [
                {"slot": "sdg_un_tie", "source": "deterministic", "content": "SDG"},
            ]
        }
        v52 = {}
        errors = validate_v52_slots("article_1", "hard_news", v52, plan)
        assert errors == []

    def test_non_standard_slots_checked_when_enabled(self) -> None:
        plan = {
            "ordered_sections": [
                {"slot": "sdg_un_tie", "source": "deterministic", "content": "SDG"},
            ]
        }
        v52 = {}
        errors = validate_v52_slots(
            "article_1", "hard_news", v52, plan, include_non_standard=True
        )
        assert "missing_deterministic_slot:sdg_un_tie" in errors


class TestMergeAndValidate:
    def test_full_pipeline_produces_valid_v52_slots(self) -> None:
        plan = {
            "slots": {
                "teacher_intro": "Teacher introduction",
                "youth_somatic": "Youth somatic experience",
            },
            "ordered_sections": [
                {"slot": "teacher_intro", "source": "deterministic", "content": "Teacher introduction"},
                {"slot": "youth_somatic", "source": "deterministic", "content": "Youth somatic experience"},
                {"slot": "news_peg", "source": "prompted", "content": ""},
                {"slot": "body_data", "source": "prompted", "content": ""},
            ],
        }
        contract = {
            "required_slots": {
                "news_peg": "Fresh UN report links climate to youth disruption.",
                "body_data": "Data shows 40% of students report heat-related focus issues.",
            }
        }
        v52_slots, warnings = merge_and_validate(
            "test_article",
            "hard_news_spiritual_response",
            plan,
            contract,
        )
        assert v52_slots["teacher_intro"] == "Teacher introduction"
        assert v52_slots["youth_somatic"] == "Youth somatic experience"
        assert v52_slots["news_peg"] == "Fresh UN report links climate to youth disruption."
        assert v52_slots["body_data"] == "Data shows 40% of students report heat-related focus issues."
        assert warnings == []

    def test_deterministic_slots_preserved_over_provider(self) -> None:
        plan = {
            "slots": {"teacher_intro": "Sacred teacher meaning"},
            "ordered_sections": [
                {"slot": "teacher_intro", "source": "deterministic", "content": "Sacred teacher meaning"},
                {"slot": "news_peg", "source": "prompted", "content": ""},
                {"slot": "body_data", "source": "prompted", "content": ""},
            ],
        }
        contract = {
            "required_slots": {
                "news_peg": "News peg",
                "body_data": "Body data",
            },
            "optional_slots": {"teacher_intro": "Attempted provider override"},
        }
        with pytest.raises(DeterministicSlotOverwriteAttempt) as exc_info:
            merge_and_validate(
                "test_article",
                "hard_news_spiritual_response",
                plan,
                contract,
                strict_overwrite_check=True,
            )
        assert exc_info.value.slot == "teacher_intro"
        assert "Sacred teacher meaning" in exc_info.value.deterministic_value

    def test_missing_required_slots_fail_clearly(self) -> None:
        plan = {
            "slots": {"teacher_intro": "Intro"},
            "ordered_sections": [
                {"slot": "teacher_intro", "source": "deterministic", "content": "Intro"},
                {"slot": "news_peg", "source": "prompted", "content": ""},
                {"slot": "body_data", "source": "prompted", "content": ""},
            ],
        }
        contract = {"required_slots": {"news_peg": "", "body_data": "Data"}}
        with pytest.raises(MergeError) as exc_info:
            merge_and_validate(
                "test_article",
                "hard_news_spiritual_response",
                plan,
                contract,
            )
        assert exc_info.value.article_id == "test_article"
        assert "missing_required_slot:news_peg" in exc_info.value.errors


class TestAllTemplatesCovered:
    """Verify all active templates have prompted slot definitions."""

    def test_all_templates_have_prompted_slots(self) -> None:
        expected_templates = {
            "hard_news_spiritual_response",
            "commentary",
            "explainer_context",
            "youth_feature",
            "interfaith_dialogue_report",
            "unsay_dialogue",
        }
        assert set(PROMPTED_SLOTS_BY_TEMPLATE.keys()) == expected_templates

    def test_prompted_slots_are_subset_of_standard_slots_or_known(self) -> None:
        standard_set = set(STANDARD_V52_SLOTS)
        known_non_standard = {"event_summary"}
        for template_id, prompted in PROMPTED_SLOTS_BY_TEMPLATE.items():
            for slot in prompted:
                assert slot in standard_set or slot in known_non_standard, (
                    f"Template {template_id} has unknown prompted slot: {slot}"
                )
