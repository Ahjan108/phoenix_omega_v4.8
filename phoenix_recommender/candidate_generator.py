"""Candidate generator — cross-product of valid book combinations."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent

# Hardcoded v1 values
LANGUAGES = ["en", "ja-JP", "zh-CN", "zh-TW", "zh-HK", "zh-SG", "ko-KR"]

# Topic mapping cache
_TOPIC_MAPPING_CACHE = None
FORMATS = ["core", "companion", "workbook"]
CITY_OVERLAYS = ["nyc", "london", "tokyo", "shanghai", "seoul", "taipei", "singapore", "sydney"]

# Language-to-city mappings for v1 hard gate
LANGUAGE_CITY_AFFINITY = {
    "en": {"nyc", "london", "sydney"},
    "ja-JP": {"tokyo"},
    "zh-CN": {"shanghai"},
    "zh-TW": {"taipei"},
    "zh-HK": {"hong_kong"},  # Note: not in hardcoded list, so will be skipped
    "zh-SG": {"singapore"},
    "ko-KR": {"seoul"},
}


def load_canonical_personas() -> List[str]:
    """Load canonical personas from config."""
    config_file = REPO_ROOT / "config" / "catalog_planning" / "canonical_personas.yaml"
    if not config_file.exists():
        print(f"WARNING: Personas file not found at {config_file}")
        return []
    with open(config_file) as f:
        data = yaml.safe_load(f) or {}
    return data.get("personas", [])


def load_canonical_topics() -> List[str]:
    """Load canonical topics from config."""
    config_file = REPO_ROOT / "config" / "catalog_planning" / "canonical_topics.yaml"
    if not config_file.exists():
        print(f"WARNING: Topics file not found at {config_file}")
        return []
    with open(config_file) as f:
        data = yaml.safe_load(f) or {}
    return data.get("topics", [])


def load_topic_mapping() -> dict:
    """Load canonical topic -> pearl_news atom topic mapping."""
    global _TOPIC_MAPPING_CACHE
    if _TOPIC_MAPPING_CACHE is not None:
        return _TOPIC_MAPPING_CACHE

    mapping_file = REPO_ROOT / "config" / "recommender" / "topic_mapping.yaml"
    if not mapping_file.exists():
        _TOPIC_MAPPING_CACHE = {}
        return _TOPIC_MAPPING_CACHE

    try:
        with open(mapping_file) as f:
            data = yaml.safe_load(f) or {}
        _TOPIC_MAPPING_CACHE = data.get("mappings", {})
        return _TOPIC_MAPPING_CACHE
    except Exception as e:
        print(f"ERROR loading topic mapping: {e}")
        _TOPIC_MAPPING_CACHE = {}
        return _TOPIC_MAPPING_CACHE


def load_teachers_for_topic(topic: str) -> List[str]:
    """Load teacher names for a given topic from pearl_news atoms.

    Uses topic_mapping.yaml to translate canonical topics to pearl_news atom topics.
    If mapping exists, loads teachers from mapped atom topic file.
    """
    mapping = load_topic_mapping()
    atom_topic = mapping.get(topic)

    if not atom_topic:
        # No mapping for this canonical topic
        return []

    topic_file = REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices" / f"topic_{atom_topic}.yaml"
    if not topic_file.exists():
        return []

    try:
        with open(topic_file) as f:
            data = yaml.safe_load(f) or {}
        teachers = data.get("teachers", {})
        return list(teachers.keys())
    except Exception as e:
        print(f"ERROR loading teachers for topic {topic}: {e}")
        return []


def generate_candidate_id(persona: str, topic: str, teacher: str, language: str,
                         format_: str, city: str) -> str:
    """Generate deterministic candidate ID from components."""
    components = f"{persona}|{topic}|{teacher}|{language}|{format_}|{city}"
    return hashlib.md5(components.encode()).hexdigest()[:12]


def check_language_city_affinity(language: str, city: str) -> bool:
    """Check if language-city pairing is reasonable for v1."""
    affinity = LANGUAGE_CITY_AFFINITY.get(language, set())
    return city in affinity


def generate_candidates() -> List[Dict[str, Any]]:
    """
    Generate all valid book candidates via cross-product with hard gates applied.

    Returns:
        List of candidate dicts with id, persona, topic, teacher, language, format, city, gate_results.
    """
    personas = load_canonical_personas()
    topics = load_canonical_topics()

    if not personas:
        print("ERROR: No personas loaded")
        return []
    if not topics:
        print("ERROR: No topics loaded")
        return []

    candidates = []

    for persona in personas:
        for topic in topics:
            teachers = load_teachers_for_topic(topic)

            # Hard gate: teacher must have atoms for topic
            if not teachers:
                continue

            for teacher in teachers:
                for language in LANGUAGES:
                    for format_ in FORMATS:
                        for city in CITY_OVERLAYS:
                            # Hard gate: language-city affinity
                            if not check_language_city_affinity(language, city):
                                continue

                            candidate_id = generate_candidate_id(persona, topic, teacher, language, format_, city)

                            candidate = {
                                "candidate_id": candidate_id,
                                "persona": persona,
                                "topic": topic,
                                "teacher": teacher,
                                "language": language,
                                "format": format_,
                                "city_overlay": city,
                                "gate_results": {
                                    "teacher_topic_coverage": True,
                                    "language_city_affinity": True,
                                }
                            }
                            candidates.append(candidate)

    return candidates


def main():
    """Print summary of generated candidates."""
    candidates = generate_candidates()

    print(f"\n=== Candidate Generation Summary ===")
    print(f"Total candidates generated: {len(candidates)}")

    if candidates:
        print(f"\nFirst 5 candidates:")
        for candidate in candidates[:5]:
            print(f"  {candidate['candidate_id']}: "
                  f"{candidate['persona']} × {candidate['topic']} × "
                  f"{candidate['teacher']} × {candidate['language']} × "
                  f"{candidate['format']} × {candidate['city_overlay']}")

        # Stats
        unique_personas = set(c["persona"] for c in candidates)
        unique_topics = set(c["topic"] for c in candidates)
        unique_teachers = set(c["teacher"] for c in candidates)
        unique_languages = set(c["language"] for c in candidates)

        print(f"\nDiversity metrics:")
        print(f"  Unique personas: {len(unique_personas)}")
        print(f"  Unique topics: {len(unique_topics)}")
        print(f"  Unique teachers: {len(unique_teachers)}")
        print(f"  Unique languages: {len(unique_languages)}")


if __name__ == "__main__":
    main()
