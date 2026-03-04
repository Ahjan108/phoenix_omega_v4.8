#!/usr/bin/env python3
"""
Marketing Config CI Validator
Validates config/marketing/ YAML files for referential integrity and cross-file consistency.

Checks:
1. consumer_language_by_topic.yaml structure and content
2. invisible_scripts_by_persona_topic.yaml structure and content
3. Cross-file consistency (topics, personas)
4. Brand archetype registry compliance
5. Platform compliance (GLOBAL_FLAGGED terms)

Exit codes:
  0: PASS
  1: ERROR (validation failed)
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Hardcoded fallback topic IDs
CANONICAL_TOPICS_FALLBACK = {
    "anxiety", "burnout", "overthinking", "imposter_syndrome", "sleep_anxiety",
    "financial_stress", "grief", "boundaries", "somatic_healing", "depression",
    "compassion_fatigue", "courage", "self_worth", "social_anxiety"
}

# Hardcoded fallback persona IDs
CANONICAL_PERSONAS_FALLBACK = {
    "millennial_women_professionals", "tech_finance_burnout", "entrepreneurs",
    "working_parents", "gen_x_sandwich", "corporate_managers", "gen_z_professionals",
    "healthcare_rns", "gen_alpha_students", "first_responders"
}

# Global flagged terms from title engine compliance
GLOBAL_FLAGGED_TERMS = {
    "cure", "treatment", "therapy program", "clinical protocol", 
    "diagnosis", "guaranteed", "instant", "proven to reduce"
}


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class ValidationWarning(Exception):
    """Raised for non-blocking warnings (can be promoted to errors with --strict)."""
    pass


def load_yaml(path: Path) -> Dict:
    """Load YAML file with error handling."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise ValidationError(f"File not found: {path}")
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML in {path}: {e}")


def load_canonical_topics(config_dir: Path) -> Set[str]:
    """Load canonical topics from config or use fallback."""
    canonical_path = config_dir.parent / "catalog_planning" / "canonical_topics.yaml"
    
    if canonical_path.exists():
        try:
            data = load_yaml(canonical_path)
            topics = set(data.get("topics", []))
            if topics:
                return topics
        except Exception:
            pass
    
    return CANONICAL_TOPICS_FALLBACK


def load_canonical_personas(config_dir: Path) -> Set[str]:
    """Load canonical personas from config or use fallback."""
    canonical_path = config_dir.parent / "catalog_planning" / "canonical_personas.yaml"
    
    if canonical_path.exists():
        try:
            data = load_yaml(canonical_path)
            personas = set(data.get("personas", []))
            if personas:
                return personas
        except Exception:
            pass
    
    return CANONICAL_PERSONAS_FALLBACK


def load_brand_registry(registry_path: Path) -> Dict:
    """Load brand archetype registry."""
    if not registry_path.exists():
        return {}
    return load_yaml(registry_path)


def validate_consumer_language(
    config_path: Path,
    canonical_topics: Set[str],
    strict: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Validate consumer_language_by_topic.yaml
    
    Returns: (errors, warnings)
    """
    errors = []
    warnings = []
    
    if not config_path.exists():
        raise ValidationError(f"consumer_language_by_topic.yaml not found at {config_path}")
    
    data = load_yaml(config_path)
    topics = data.get("topics", [])
    
    seen_topics = set()
    
    for i, topic_entry in enumerate(topics):
        # Check required fields
        required_fields = ["topic_id", "consumer_phrases", "banned_clinical_terms", 
                          "bridge_language", "search_clusters"]
        missing_fields = [f for f in required_fields if f not in topic_entry or topic_entry[f] is None]
        if missing_fields:
            errors.append(f"Topic entry {i}: missing fields {missing_fields}")
            continue
        
        topic_id = topic_entry.get("topic_id")
        
        # Check topic_id is canonical
        if topic_id not in canonical_topics:
            errors.append(f"Topic entry {i}: topic_id '{topic_id}' not in canonical topics")
        
        # Check for duplicates
        if topic_id in seen_topics:
            errors.append(f"Topic entry {i}: duplicate topic_id '{topic_id}'")
        seen_topics.add(topic_id)
        
        # Check consumer_phrases
        consumer_phrases = topic_entry.get("consumer_phrases", [])
        if len(consumer_phrases) < 5:
            errors.append(f"Topic '{topic_id}': consumer_phrases has {len(consumer_phrases)} items, need at least 5")
        if any(not phrase or not isinstance(phrase, str) or not phrase.strip() for phrase in consumer_phrases):
            errors.append(f"Topic '{topic_id}': consumer_phrases contains empty or invalid strings")
        
        # Check banned_clinical_terms
        banned_terms = topic_entry.get("banned_clinical_terms", [])
        if len(banned_terms) < 3:
            errors.append(f"Topic '{topic_id}': banned_clinical_terms has {len(banned_terms)} items, need at least 3")
        if any(not term or not isinstance(term, str) or not term.strip() for term in banned_terms):
            errors.append(f"Topic '{topic_id}': banned_clinical_terms contains empty or invalid strings")
        
        # Check bridge_language
        bridge_lang = topic_entry.get("bridge_language", [])
        if len(bridge_lang) < 3:
            errors.append(f"Topic '{topic_id}': bridge_language has {len(bridge_lang)} items, need at least 3")
        if any(not phrase or not isinstance(phrase, str) or not phrase.strip() for phrase in bridge_lang):
            errors.append(f"Topic '{topic_id}': bridge_language contains empty or invalid strings")
        
        # Check search_clusters
        search = topic_entry.get("search_clusters", [])
        if not search:
            errors.append(f"Topic '{topic_id}': search_clusters is empty")
        if any(not cluster or not isinstance(cluster, str) or not cluster.strip() for cluster in search):
            errors.append(f"Topic '{topic_id}': search_clusters contains empty or invalid strings")
    
    return errors, warnings


def validate_invisible_scripts(
    config_path: Path,
    canonical_personas: Set[str],
    canonical_topics: Set[str],
    strict: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Validate invisible_scripts_by_persona_topic.yaml
    
    Returns: (errors, warnings)
    """
    errors = []
    warnings = []
    
    if not config_path.exists():
        raise ValidationError(f"invisible_scripts_by_persona_topic.yaml not found at {config_path}")
    
    data = load_yaml(config_path)
    scripts_list = data.get("scripts", [])
    
    seen_persona_topic_pairs = set()
    persona_topic_coverage = set()
    
    for i, entry in enumerate(scripts_list):
        # Check required fields
        if "persona_id" not in entry:
            errors.append(f"Scripts entry {i}: missing persona_id")
            continue
        if "topic_id" not in entry:
            errors.append(f"Scripts entry {i}: missing topic_id")
            continue
        if "scripts" not in entry or entry["scripts"] is None:
            errors.append(f"Scripts entry {i}: missing scripts field")
            continue
        
        persona_id = entry.get("persona_id")
        topic_id = entry.get("topic_id")
        scripts = entry.get("scripts", [])
        
        # Validate persona_id
        if persona_id not in canonical_personas:
            errors.append(f"Entry {i}: persona_id '{persona_id}' not in canonical personas")
        
        # Validate topic_id
        if topic_id not in canonical_topics:
            errors.append(f"Entry {i}: topic_id '{topic_id}' not in canonical topics")
        
        # Check for duplicates
        pair = (persona_id, topic_id)
        if pair in seen_persona_topic_pairs:
            errors.append(f"Entry {i}: duplicate persona_id×topic_id pair ({persona_id}, {topic_id})")
        seen_persona_topic_pairs.add(pair)
        persona_topic_coverage.add(pair)
        
        # Check exactly 2 scripts
        if len(scripts) != 2:
            errors.append(f"Entry {i} ({persona_id}×{topic_id}): has {len(scripts)} scripts, need exactly 2")
        
        # Check no empty scripts
        if any(not script or not isinstance(script, str) or not script.strip() for script in scripts):
            errors.append(f"Entry {i} ({persona_id}×{topic_id}): contains empty or invalid scripts")
    
    # Check coverage: warn if fewer than expected entries (10 personas × 14 topics = 140)
    expected_coverage = len(canonical_personas) * len(canonical_topics)
    actual_coverage = len(persona_topic_coverage)
    if actual_coverage < expected_coverage:
        msg = f"Coverage check: {actual_coverage} persona×topic combos found, expected {expected_coverage} (10 personas × 14 topics)"
        if actual_coverage < 140:  # Warn if significantly below expected
            warnings.append(msg)
    
    return errors, warnings


def check_cross_file_consistency(
    consumer_lang_config: Dict,
    invisible_scripts_config: Dict,
    canonical_topics: Set[str],
    strict: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Cross-file consistency check:
    - No topic in invisible_scripts references a topic not in consumer_language
    
    Returns: (errors, warnings)
    """
    errors = []
    warnings = []
    
    # Get topics from consumer_language
    consumer_topics = set()
    for topic_entry in consumer_lang_config.get("topics", []):
        topic_id = topic_entry.get("topic_id")
        if topic_id:
            consumer_topics.add(topic_id)
    
    # Check invisible_scripts topics exist in consumer_language
    for script_entry in invisible_scripts_config.get("scripts", []):
        topic_id = script_entry.get("topic_id")
        if topic_id and topic_id not in consumer_topics:
            errors.append(f"invisible_scripts: topic '{topic_id}' not found in consumer_language_by_topic")
    
    return errors, warnings


def check_brand_compliance(
    brand_registry: Dict,
    consumer_lang_config: Dict,
    strict: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Check that brand allowed_tokens don't include banned_clinical_terms.
    
    Returns: (errors, warnings)
    """
    errors = []
    warnings = []
    
    if not brand_registry:
        return errors, warnings
    
    # Collect all banned clinical terms
    banned_terms = set()
    for topic_entry in consumer_lang_config.get("topics", []):
        banned = topic_entry.get("banned_clinical_terms", [])
        banned_terms.update(term.lower() for term in banned if isinstance(term, str))
    
    # Check each brand's allowed_tokens
    for brand in brand_registry.get("brand_archetypes", []):
        brand_id = brand.get("brand_id", "unknown")
        emotional_vocab = brand.get("emotional_vocabulary", {})
        allowed_tokens = emotional_vocab.get("allowed_tokens", [])
        
        for token in allowed_tokens:
            token_lower = token.lower() if isinstance(token, str) else ""
            if token_lower in banned_terms:
                errors.append(f"Brand '{brand_id}': allowed_token '{token}' is in banned_clinical_terms")
    
    return errors, warnings


def check_platform_compliance(
    consumer_lang_config: Dict,
    strict: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Check that GLOBAL_FLAGGED terms are not in consumer_phrases.
    Bridge language should replace them.
    
    Returns: (errors, warnings)
    """
    errors = []
    warnings = []
    
    for topic_entry in consumer_lang_config.get("topics", []):
        topic_id = topic_entry.get("topic_id", "unknown")
        consumer_phrases = topic_entry.get("consumer_phrases", [])
        
        for phrase in consumer_phrases:
            if not isinstance(phrase, str):
                continue
            phrase_lower = phrase.lower()
            for flagged_term in GLOBAL_FLAGGED_TERMS:
                if flagged_term in phrase_lower:
                    msg = f"Topic '{topic_id}': consumer_phrase contains GLOBAL_FLAGGED term '{flagged_term}'"
                    warnings.append(msg)
    
    return errors, warnings


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate marketing config files for referential integrity"
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path("config/marketing"),
        help="Path to config/marketing/ directory (default: config/marketing/)"
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("config/catalog_planning/brand_archetype_registry.yaml"),
        help="Path to brand_archetype_registry.yaml (default: config/catalog_planning/brand_archetype_registry.yaml)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Promote all WARNings to ERRORs"
    )
    
    args = parser.parse_args()
    
    all_errors = []
    all_warnings = []
    
    try:
        # Load canonical data
        canonical_topics = load_canonical_topics(args.config_dir)
        canonical_personas = load_canonical_personas(args.config_dir)
        
        # Paths
        consumer_lang_path = args.config_dir / "consumer_language_by_topic.yaml"
        invisible_scripts_path = args.config_dir / "invisible_scripts_by_persona_topic.yaml"
        
        # Load configs
        consumer_lang_config = load_yaml(consumer_lang_path)
        invisible_scripts_config = load_yaml(invisible_scripts_path)
        brand_registry = load_brand_registry(args.registry)
        
        # Run all validations
        errors, warnings = validate_consumer_language(consumer_lang_path, canonical_topics, args.strict)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        
        errors, warnings = validate_invisible_scripts(
            invisible_scripts_path, canonical_personas, canonical_topics, args.strict
        )
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        
        errors, warnings = check_cross_file_consistency(
            consumer_lang_config, invisible_scripts_config, canonical_topics, args.strict
        )
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        
        errors, warnings = check_brand_compliance(brand_registry, consumer_lang_config, args.strict)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        
        errors, warnings = check_platform_compliance(consumer_lang_config, args.strict)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        
        # Report results
        if all_errors:
            for error in all_errors:
                print(f"ERROR: {error}", file=sys.stderr)
        
        for warning in all_warnings:
            print(f"WARN: {warning}", file=sys.stderr)
        
        # Handle strict mode
        if args.strict and all_warnings:
            all_errors.extend(all_warnings)
        
        if all_errors:
            return 1
        
        print("PASS: marketing config validated")
        return 0
    
    except ValidationError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
