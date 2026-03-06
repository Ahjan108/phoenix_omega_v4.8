from pearl_prime.modular_format_freeze import (
    FREEZE_CONFIG_PATH,
    apply_output_format_to_plan,
    load_freeze_settings,
)


def test_freeze_config_loads():
    settings = load_freeze_settings(FREEZE_CONFIG_PATH)
    assert settings.enabled is True
    assert "five_min_practice" in settings.formats
    assert "protocol_library" in settings.formats


def test_apply_output_format_to_plan_rewrites_slot_shape():
    settings = load_freeze_settings(FREEZE_CONFIG_PATH)
    base = {
        "format_structural_id": "F006",
        "format_runtime_id": "standard_book",
        "chapter_count": 12,
        "slot_definitions": [["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]] * 12,
    }
    out = apply_output_format_to_plan(
        base,
        output_format_id="myth_vs_mechanism",
        chapter_count=8,
        settings=settings,
    )
    assert out["format_structural_id"] == "MOD_myth_vs_mechanism"
    assert out["format_runtime_id"] == "short_book_30"
    assert out["chapter_count"] == 8
    assert len(out["slot_definitions"]) == 8
    assert out["slot_definitions"][0] == ["HOOK", "SCENE", "STORY", "PIVOT", "REFLECTION", "EXERCISE", "TAKEAWAY", "INTEGRATION", "THREAD"]
    assert out["output_format_id"] == "myth_vs_mechanism"

