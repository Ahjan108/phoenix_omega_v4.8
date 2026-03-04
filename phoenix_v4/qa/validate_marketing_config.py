#!/usr/bin/env python3
"""
Validate marketing config files used by title generation.

Files:
  - config/marketing/consumer_language_by_topic.yaml
  - config/marketing/invisible_scripts_by_persona_topic.yaml

Exit code:
  0 = pass
  1 = fail
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


REQUIRED_TOPICS = {
    "anxiety",
    "burnout",
    "overthinking",
    "imposter_syndrome",
    "sleep_anxiety",
    "financial_stress",
    "grief",
    "boundaries",
    "somatic_healing",
    "depression",
    "compassion_fatigue",
    "courage",
    "self_worth",
    "social_anxiety",
}

REQUIRED_PERSONAS = {
    "millennial_women_professionals",
    "tech_finance_burnout",
    "entrepreneurs",
    "working_parents",
    "gen_x_sandwich",
    "corporate_managers",
    "gen_z_professionals",
    "healthcare_rns",
    "gen_alpha_students",
    "first_responders",
}

TOPIC_FIELD_SPECS = {
    "consumer_phrases": (8, 10),
    "banned_clinical_terms": (5, 8),
    "culture_specific_phrases": (3, 5),
    "bridge_language": (5, 7),
    "search_clusters": (3, 5),
    "persona_subtitle_patterns": (2, 3),
    "platform_risk_terms": (3, 5),
}


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with: pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must load as a YAML mapping")
    return data


def _validate_list_field(errors: list[str], topic_id: str, entry: dict, field: str, min_n: int, max_n: int) -> None:
    value = entry.get(field)
    if not isinstance(value, list):
        errors.append(f"topic={topic_id}: field '{field}' must be a list")
        return
    if not (min_n <= len(value) <= max_n):
        errors.append(
            f"topic={topic_id}: field '{field}' has {len(value)} items; expected {min_n}-{max_n}"
        )
    for i, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"topic={topic_id}: field '{field}' index {i} must be a non-empty string")


def validate_consumer_language(path: Path) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    data = _load_yaml(path)
    topics = data.get("topics")
    if not isinstance(topics, list):
        return [f"{path}: top-level 'topics' must be a list"], set()

    seen: set[str] = set()
    for i, entry in enumerate(topics):
        if not isinstance(entry, dict):
            errors.append(f"topics[{i}] must be a mapping")
            continue
        topic_id = entry.get("topic_id")
        if not isinstance(topic_id, str) or not topic_id:
            errors.append(f"topics[{i}]: missing/invalid topic_id")
            continue
        if topic_id in seen:
            errors.append(f"duplicate topic_id: {topic_id}")
            continue
        seen.add(topic_id)
        for field, (min_n, max_n) in TOPIC_FIELD_SPECS.items():
            _validate_list_field(errors, topic_id, entry, field, min_n, max_n)

    if seen != REQUIRED_TOPICS:
        missing = sorted(REQUIRED_TOPICS - seen)
        extra = sorted(seen - REQUIRED_TOPICS)
        if missing:
            errors.append(f"consumer topics missing required IDs: {missing}")
        if extra:
            errors.append(f"consumer topics contain unexpected IDs: {extra}")
    return errors, seen


def validate_invisible_scripts(path: Path, consumer_topics: set[str]) -> list[str]:
    errors: list[str] = []
    data = _load_yaml(path)
    scripts = data.get("scripts")
    if not isinstance(scripts, list):
        return [f"{path}: top-level 'scripts' must be a list"]

    seen_pairs: set[tuple[str, str]] = set()
    seen_personas: set[str] = set()
    seen_topics: set[str] = set()

    for i, entry in enumerate(scripts):
        if not isinstance(entry, dict):
            errors.append(f"scripts[{i}] must be a mapping")
            continue
        persona_id = entry.get("persona_id")
        topic_id = entry.get("topic_id")
        values = entry.get("scripts")

        if not isinstance(persona_id, str) or not persona_id:
            errors.append(f"scripts[{i}]: missing/invalid persona_id")
            continue
        if not isinstance(topic_id, str) or not topic_id:
            errors.append(f"scripts[{i}]: missing/invalid topic_id")
            continue
        if persona_id not in REQUIRED_PERSONAS:
            errors.append(f"scripts[{i}]: unknown persona_id '{persona_id}'")
        if topic_id not in REQUIRED_TOPICS:
            errors.append(f"scripts[{i}]: unknown topic_id '{topic_id}'")

        pair = (persona_id, topic_id)
        if pair in seen_pairs:
            errors.append(f"duplicate persona/topic pair: {persona_id} x {topic_id}")
        seen_pairs.add(pair)
        seen_personas.add(persona_id)
        seen_topics.add(topic_id)

        if not isinstance(values, list) or len(values) != 2:
            errors.append(f"scripts[{i}] ({persona_id} x {topic_id}): 'scripts' must contain exactly 2 items")
            continue
        for j, script in enumerate(values):
            if not isinstance(script, str) or not script.strip():
                errors.append(f"scripts[{i}] ({persona_id} x {topic_id}) script[{j}] must be a non-empty string")

    if seen_personas != REQUIRED_PERSONAS:
        missing = sorted(REQUIRED_PERSONAS - seen_personas)
        extra = sorted(seen_personas - REQUIRED_PERSONAS)
        if missing:
            errors.append(f"invisible scripts missing personas: {missing}")
        if extra:
            errors.append(f"invisible scripts have unexpected personas: {extra}")

    if seen_topics != REQUIRED_TOPICS:
        missing = sorted(REQUIRED_TOPICS - seen_topics)
        extra = sorted(seen_topics - REQUIRED_TOPICS)
        if missing:
            errors.append(f"invisible scripts missing topics: {missing}")
        if extra:
            errors.append(f"invisible scripts have unexpected topics: {extra}")

    expected_pairs = {(p, t) for p in REQUIRED_PERSONAS for t in REQUIRED_TOPICS}
    if seen_pairs != expected_pairs:
        missing_pairs = sorted(expected_pairs - seen_pairs)
        extra_pairs = sorted(seen_pairs - expected_pairs)
        if missing_pairs:
            errors.append(f"invisible scripts missing persona/topic pairs: {len(missing_pairs)}")
        if extra_pairs:
            errors.append(f"invisible scripts have unexpected persona/topic pairs: {len(extra_pairs)}")

    if consumer_topics and seen_topics != consumer_topics:
        errors.append("topic mismatch between consumer_language_by_topic.yaml and invisible_scripts_by_persona_topic.yaml")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate marketing config files.")
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "config" / "marketing",
        help="Path to config/marketing directory",
    )
    args = parser.parse_args()

    config_dir = args.config_dir
    consumer_path = config_dir / "consumer_language_by_topic.yaml"
    scripts_path = config_dir / "invisible_scripts_by_persona_topic.yaml"

    errors: list[str] = []
    if not consumer_path.exists():
        errors.append(f"missing file: {consumer_path}")
    if not scripts_path.exists():
        errors.append(f"missing file: {scripts_path}")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    try:
        consumer_errors, consumer_topics = validate_consumer_language(consumer_path)
        errors.extend(consumer_errors)
        errors.extend(validate_invisible_scripts(scripts_path, consumer_topics))
    except Exception as exc:
        print(f"validation crashed: {exc}", file=sys.stderr)
        return 1

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
