from __future__ import annotations

import phoenix_title_engine_v4 as title_engine
from phoenix_v4.qa import validate_marketing_config as marketing_validator


def test_marketing_validator_passes_current_config() -> None:
    config_dir = marketing_validator.Path("config/marketing")
    consumer = config_dir / "consumer_language_by_topic.yaml"
    scripts = config_dir / "invisible_scripts_by_persona_topic.yaml"

    consumer_errors, consumer_topics = marketing_validator.validate_consumer_language(consumer)
    script_errors = marketing_validator.validate_invisible_scripts(scripts, consumer_topics)
    all_errors = consumer_errors + script_errors

    assert not all_errors, f"marketing config validation failed: {all_errors[:3]}"


def test_generate_invisible_script_uses_persona_topic_config() -> None:
    gen = title_engine.TitleGenerator()
    persona_id = "millennial_women_professionals"
    topic_id = "anxiety"
    brand_id = "stabilizer"

    configured_scripts = gen.marketing_config.get_invisible_scripts(persona_id, topic_id)
    assert configured_scripts, "expected configured scripts for persona/topic"

    selected_script = gen.generate_invisible_script(brand_id, topic_id, persona_id)
    assert selected_script in configured_scripts


def test_generate_title_uses_config_search_cluster_for_keyword() -> None:
    gen = title_engine.TitleGenerator()
    brand_id = "stabilizer"
    topic_id = "anxiety"
    persona_id = "millennial_women_professionals"

    expected_keyword = gen.marketing_config.get_primary_search_keyword(topic_id)
    assert expected_keyword, "expected config-driven primary search keyword"

    _, subtitle, _ = gen.generate_title(brand_id, topic_id, persona_id)
    assert subtitle.endswith(expected_keyword), subtitle


def test_check_compliance_blocks_banned_term_and_logs_monitor_term() -> None:
    gen = title_engine.TitleGenerator()
    topic_id = "anxiety"

    banned_terms = gen.marketing_config.get_banned_clinical_terms(topic_id)
    assert banned_terms, "expected banned clinical terms from config"
    blocked = gen.check_compliance("Title", f"Subtitle {banned_terms[0]}", topic_id)
    assert blocked is False

    risk_terms = gen.marketing_config.get_platform_risk_terms(topic_id)
    assert risk_terms, "expected monitor-tier risk terms from config"
    before = len(gen.validation_errors)
    monitor_pass = gen.check_compliance("Title", f"Subtitle {risk_terms[0]}", topic_id)
    after = len(gen.validation_errors)

    assert monitor_pass is True
    assert after == before + 1
    assert "monitor_risk_term" in gen.validation_errors[-1]
