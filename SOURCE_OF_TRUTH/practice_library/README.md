# Practice Library

Normalized store for practice items from:
- **9×34 library_34 JSONs** (sensory_grounding, gratitude_practices, integration_bridges, self_inquiry, meditations, affirmations, reflections, thought_experiments, body_awareness)
- **Optional:** exercises_ab_tady_37_PRODUCTION_READY.json (37 breath/somatic)
- **Manual** entries

## Layout

- **inbox/** — Drop raw `*_library_34.json` and optional breath JSON here. Run ingest to produce raw JSONL.
- **tmp/** — Raw JSONL output from ingest (intermediate).
- **store/practice_items.jsonl** — Final validated store (one PracticeItem per line).
- **index/by_content_type/** — (Optional) Lists of practice_id per content_type for fast lookup.

## Scripts

| Script | Purpose |
|--------|---------|
| **scripts/practice/ingest_practice_libraries.py** | Read inbox `*_library_34.json` (+ optional ab_tady_37); write tmp/raw_practice_items.jsonl. |
| **scripts/practice/normalize_practice_items.py** | Apply validation (duration, text length, banned_phrases), whitespace; write store/practice_items.jsonl. Exit 1 on any violation. |
| **scripts/practice/validate_practice_store.py** | CI gate: re-check schema, enums, unique practice_id, banned phrases; output counts by content_type. |
| **scripts/practice/extract_libraries_from_rtf.py** | Extract `*_library_34.json` from specs/34_exercises.rtf into inbox (optional when JSON is embedded in RTF). |
| **phoenix_v4/qa/practice_safety_lint.py** | Lint a JSONL file with config/practice/validation.yaml (banned phrases, duration). Used by normalize and CI. |

**Runtime:** `phoenix_v4/planning/practice_selector.py` — `load_store()`, `get_backstop_pool()` (for pool_index when EXERCISE canonical empty), `get_practice_prose_map()` (for prose_resolver).

## Pipeline

1. `python -m scripts.practice.ingest_practice_libraries --input-dir SOURCE_OF_TRUTH/practice_library/inbox --output-raw SOURCE_OF_TRUTH/practice_library/tmp/raw_practice_items.jsonl`
2. `python -m scripts.practice.normalize_practice_items --input .../tmp/raw_practice_items.jsonl --output .../store/practice_items.jsonl --validation-config config/practice/validation.yaml`
3. `python -m scripts.practice.validate_practice_store --input .../store/practice_items.jsonl --validation-config config/practice/validation.yaml`

(Optional) To populate inbox from RTF:  
`python -m scripts.practice.extract_libraries_from_rtf --rtf specs/34_exercises.rtf --out-dir SOURCE_OF_TRUTH/practice_library/inbox`

## Usage

- **EXERCISE backstop:** When `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` is missing or empty, assembly fills EXERCISE slots from this store (`config/practice/selection_rules.yaml`, EXERCISE_BACKSTOP). Slot resolver picks deterministically; Stage 6 resolves prose for practice_id (lib34_*, ab37_*) from the store.
- **Teacher fallback:** Teachers with insufficient approved EXERCISE atoms can use practice items with a doctrine wrapper (see docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md).

## Config

- **config/practice/selection_rules.yaml** — EXERCISE_BACKSTOP (enabled, allowed_content_types, preferred_content_types); SLOT_07_PRACTICE (opt-in); no distribution mix in this file.
- **config/practice/validation.yaml** — Required fields, enums, duration 30–1200s, text length, banned_phrases, optional TTS rhythm.

## Specs & docs

- **specs/PRACTICE_ITEM_SCHEMA.md** — Canonical PracticeItem schema, store layout, integration (backstop, teacher fallback, rendering).
- **docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md** — When teacher has too few EXERCISE atoms; supplement from store with teacher wrapper (intro/close).
- **docs/SYSTEMS_V4.md** — §4 Stage 3/6, §9 config table (Practice library row), §11 doc map.
- **specs/PHOENIX_V4_5_WRITER_SPEC.md** — §4.5 EXERCISE (where content comes from), §20 Config (Practice library).
