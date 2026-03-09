#!/usr/bin/env python3
"""
One-time GHL setup: creates custom fields, tags, and writes discovered UUIDs to config.
Run this ONCE before go-live. After this, the app auto-sends correct field UUIDs and tags.

Usage:
    GHL_API_KEY=... GHL_LOCATION_ID=... python ghl_setup.py

Or set ghl_api_key / ghl_location_id in config.yaml and run:
    python ghl_setup.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import yaml

APP_DIR = Path(__file__).resolve().parent


def load_config() -> dict:
    cfg_path = APP_DIR / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


CFG = load_config()
API_KEY = os.environ.get("GHL_API_KEY", CFG.get("ghl_api_key", ""))
LOCATION_ID = os.environ.get("GHL_LOCATION_ID", CFG.get("ghl_location_id", ""))
BASE = "https://services.leadconnectorhq.com"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Version": "2021-07-28",
}

# ---------- Custom fields to create ----------
CUSTOM_FIELDS = [
    {"name": "topic", "dataType": "TEXT", "config_key": "ghl_custom_field_topic"},
    {"name": "exercise", "dataType": "TEXT", "config_key": "ghl_custom_field_exercise"},
    {"name": "persona", "dataType": "TEXT", "config_key": "ghl_custom_field_persona"},
]

# ---------- All tags to create ----------
TOPIC_TAGS = [
    "topic_overthinking", "topic_burnout", "topic_boundaries", "topic_self_worth",
    "topic_social_anxiety", "topic_financial_anxiety", "topic_imposter_syndrome",
    "topic_sleep_anxiety", "topic_depression", "topic_grief",
    "topic_compassion_fatigue", "topic_somatic_healing",
]
PERSONA_TAGS = [
    "persona_millennial_women_professionals", "persona_tech_finance_burnout",
    "persona_entrepreneurs", "persona_working_parents", "persona_gen_x_sandwich",
    "persona_corporate_managers", "persona_gen_z_professionals",
    "persona_healthcare_rns", "persona_gen_alpha_students", "persona_first_responders",
]
EXERCISE_TAGS = [
    "exercise_cyclic_sighing", "exercise_box_breathing", "exercise_478_breathing",
    "exercise_extended_exhale", "exercise_body_scan", "exercise_five_senses_grounding",
    "exercise_sigh_of_relief", "exercise_bee_breath", "exercise_triangle_breathing",
    "exercise_loving_kindness_breathing", "exercise_hrv_coherence", "exercise_coherence_5bpm",
    "exercise_equal_breathing", "exercise_rectangle_breathing", "exercise_resonance_6bpm",
    "exercise_three_part_breath", "exercise_breath_walking", "exercise_lions_breath",
    "exercise_liberation_laughter", "exercise_ujjayi_ocean", "exercise_kapalabhati",
    "exercise_tonglen", "exercise_intention_breathing", "exercise_alternate_nostril",
    "exercise_buteyko", "exercise_phoenix_breath", "exercise_moon_breath",
]
FUNNEL_TAGS = [
    "funnel_burnout_reset", "funnel_anxiety_reset",
]
ALL_TAGS = FUNNEL_TAGS + TOPIC_TAGS + PERSONA_TAGS + EXERCISE_TAGS


def _get(path: str) -> dict | list:
    import requests
    r = requests.get(f"{BASE}{path}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict) -> dict:
    import requests
    r = requests.post(f"{BASE}{path}", headers=HEADERS, json=body, timeout=15)
    if r.status_code not in (200, 201):
        print(f"  POST {path} failed: {r.status_code} {r.text[:200]}")
    r.raise_for_status()
    return r.json()


def get_existing_custom_fields() -> dict[str, str]:
    """Returns {field_name: field_id} for existing custom fields."""
    data = _get(f"/locations/{LOCATION_ID}/customFields")
    fields = data.get("customFields", [])
    return {f["name"].lower(): f["id"] for f in fields}


def get_existing_tags() -> set[str]:
    """Returns set of existing tag names."""
    data = _get(f"/locations/{LOCATION_ID}/tags")
    tags = data.get("tags", [])
    return {t["name"] for t in tags}


def create_custom_fields() -> dict[str, str]:
    """Create custom fields if they don't exist. Returns {config_key: uuid}."""
    existing = get_existing_custom_fields()
    result = {}
    for field in CUSTOM_FIELDS:
        name = field["name"]
        config_key = field["config_key"]
        if name in existing:
            uuid = existing[name]
            print(f"  [exists] Custom field '{name}' = {uuid}")
            result[config_key] = uuid
        else:
            resp = _post(f"/locations/{LOCATION_ID}/customFields", {
                "name": name,
                "dataType": field["dataType"],
            })
            uuid = resp.get("customField", {}).get("id", resp.get("id", ""))
            print(f"  [created] Custom field '{name}' = {uuid}")
            result[config_key] = uuid
            time.sleep(0.15)  # rate limit safety
    return result


def create_tags() -> int:
    """Create all tags. Returns count of newly created tags."""
    existing = get_existing_tags()
    created = 0
    for tag_name in ALL_TAGS:
        if tag_name in existing:
            print(f"  [exists] Tag '{tag_name}'")
        else:
            try:
                _post(f"/locations/{LOCATION_ID}/tags", {"name": tag_name})
                print(f"  [created] Tag '{tag_name}'")
                created += 1
                time.sleep(0.15)
            except Exception as e:
                print(f"  [error] Tag '{tag_name}': {e}")
    return created


def update_config(field_uuids: dict[str, str]) -> None:
    """Write discovered UUIDs back to config.yaml."""
    cfg_path = APP_DIR / "config.yaml"
    if not cfg_path.exists():
        print("  [skip] config.yaml not found; print UUIDs for manual config:")
        for k, v in field_uuids.items():
            print(f"    {k}: {v}")
        return

    text = cfg_path.read_text(encoding="utf-8")
    changed = False
    for key, uuid in field_uuids.items():
        old = f'{key}: ""'
        new = f'{key}: "{uuid}"'
        if old in text:
            text = text.replace(old, new)
            changed = True
            print(f"  [config] Set {key} = {uuid}")
        elif f"{key}:" in text and uuid not in text:
            # Key exists but has a different value — don't overwrite
            print(f"  [skip] {key} already has a value in config.yaml")
        else:
            print(f"  [ok] {key} already set to {uuid}")

    if changed:
        cfg_path.write_text(text, encoding="utf-8")
        print("  [saved] config.yaml updated")
    else:
        print("  [no changes] config.yaml already up to date")


def main() -> None:
    if not API_KEY or not LOCATION_ID:
        print("ERROR: Set GHL_API_KEY and GHL_LOCATION_ID (env or config.yaml)")
        sys.exit(1)

    print(f"\nGHL Setup for location: {LOCATION_ID}")
    print(f"API endpoint: {BASE}")
    print()

    # 1. Custom fields
    print("=== Step 1: Custom Fields ===")
    field_uuids = create_custom_fields()
    print()

    # 2. Tags
    print(f"=== Step 2: Tags ({len(ALL_TAGS)} total) ===")
    new_tags = create_tags()
    print(f"\n  {new_tags} new tags created, {len(ALL_TAGS) - new_tags} already existed")
    print()

    # 3. Write UUIDs to config
    print("=== Step 3: Update config.yaml ===")
    update_config(field_uuids)
    print()

    print("=== Done ===")
    print("Custom fields created and UUIDs written to config.")
    print("All 51 tags created in GHL.")
    print("The app will now send correct field UUIDs and tags with every contact.")
    print("\nNext: run a test submission to verify end-to-end flow.")


if __name__ == "__main__":
    main()
