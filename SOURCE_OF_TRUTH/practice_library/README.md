# Practice Library

Normalized store for practice items from:
- **9×34 library_34 JSONs** (sensory_grounding, gratitude_practices, integration_bridges, self_inquiry, meditations, affirmations, reflections, thought_experiments, body_awareness)
- **Optional:** exercises_ab_tady_37_PRODUCTION_READY.json (37 breath/somatic)
- **Manual** entries

## Layout

- **inbox/** — Drop raw `*_library_34.json` and optional breath JSON here. Run ingest to produce raw JSONL.
- **tmp/** — Raw JSONL output from ingest (intermediate).
- **store/practice_items.jsonl** — Final validated store (one PracticeItem per line).
- **index/by_content_type/** — Lists of practice_id per content_type for fast lookup.

## Pipeline

1. `python -m scripts.practice.ingest_practice_libraries --input-dir SOURCE_OF_TRUTH/practice_library/inbox --output-raw SOURCE_OF_TRUTH/practice_library/tmp/raw_practice_items.jsonl`
2. `python -m scripts.practice.normalize_practice_items --input .../tmp/raw_practice_items.jsonl --output .../store/practice_items.jsonl --validation-config config/practice/validation.yaml`
3. `python -m scripts.practice.validate_practice_store --input .../store/practice_items.jsonl --validation-config config/practice/validation.yaml`

## Usage

- **EXERCISE backstop:** When `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` is missing, assembly can fill EXERCISE slots from this store (see config/practice/selection_rules.yaml, EXERCISE_BACKSTOP).
- **Teacher fallback:** Teachers with insufficient approved EXERCISE atoms can use practice items with a doctrine wrapper (see docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md).
