# Practice Item Schema (Canonical Data Model)

**Purpose:** Normalized schema for practice items from library_34 JSONs, ab_tady_37, or manual entries. Used by the practice library store and EXERCISE backstop.

**Authority:** Adapter layer spec; `config/practice/validation.yaml` enforces.

---

## 1. Canonical field order (for deterministic hashing)

Fields must appear in this order in JSON/JSONL:

1. `practice_id`
2. `source`
3. `content_type`
4. `duration_seconds`
5. `intensity_band`
6. `text`
7. `blocks`
8. `allowed_personas`
9. `allowed_topics`
10. `angle_affinity`
11. `tags`
12. `version`

---

## 2. Field definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| **practice_id** | string | ✅ | Stable unique id. Format: `<source_prefix>_<content_type>_<zero_padded_index>` (e.g. `lib34_sensory_grounding_01`). lowercase, snake_case, ≤80 chars. |
| **source** | enum | ✅ | `library_34` \| `ab_tady_37` \| `manual` |
| **content_type** | enum | ✅ | One of: affirmations, body_awareness, gratitude_practices, integration_bridges, meditations, reflections, self_inquiry, sensory_grounding, thought_experiments; or slot_07 types (breath_regulation, grounding_orientation, ...). |
| **duration_seconds** | int | ✅ | 30–1200 |
| **intensity_band** | int | ✅ | 1–5; default 3. 1=gentle, 2=mild, 3=neutral, 4=deep, 5=intense. |
| **text** | string | ✅ | Original prose; whitespace-normalized only. Must pass safety lint. |
| **blocks** | object | ✅ | Optional segmentation: `setup`, `instruction`, `prompt`, `close` (strings or null). May be all null. |
| **allowed_personas** | list[str] | ✅ | Empty = all. Otherwise only these personas may use. |
| **allowed_topics** | list[str] | ✅ | Empty = all. Otherwise only these topics. |
| **angle_affinity** | list[str] | ✅ | Optional angle ids for preference. Empty allowed. |
| **tags** | list[str] | ✅ | Free tags; max 50. |
| **version** | int | ✅ | Schema version; start at 1. |

---

## 3. Store layout

- **Store:** `SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl` (one PracticeItem per line).
- **Index:** `SOURCE_OF_TRUTH/practice_library/index/by_content_type/<content_type>.json` (list of practice_id).
- **Inbox:** `SOURCE_OF_TRUTH/practice_library/inbox/` — raw `*_library_34.json` and optional `exercises_ab_tady_37_PRODUCTION_READY.json`.

---

## 4. Integration

- **EXERCISE backstop:** When `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` is missing or empty, pool can be filled from practice store (selection_rules.EXERCISE_BACKSTOP).
- **Teacher fallback:** When a teacher has insufficient EXERCISE atoms, they may pull from practice store with a **teacher wrapper** (doctrine-aligned intro/frame); see docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md.
- **Rendering:** Prose resolver resolves `atom_id` when it matches a practice_id (e.g. `lib34_*`, `ab37_*`) by loading from practice store.
