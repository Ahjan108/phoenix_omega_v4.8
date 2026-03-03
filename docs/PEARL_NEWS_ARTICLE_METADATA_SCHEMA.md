# Pearl News — Article Metadata Schema

**Purpose:** Frozen contract for article metadata emitted by the pipeline. Used for governance checks (teacher saturation, template rotation) and analytics.

**Output path:** `artifacts/pearl_news/article_metadata.jsonl` — one JSON object per line (JSONL).

---

## Required Keys

| Key | Type | Description |
|-----|------|-------------|
| `article_id` | string | Stable ID (from feed item or generated) |
| `date` | string | Publication date (ISO 8601) |
| `topic` | string | Classified topic (e.g. `mental_health`, `climate`, `general`) |
| `primary_sdg` | string | Primary SDG number (e.g. `"3"`, `"17"`) |
| `template_id` | string | Selected template (e.g. `hard_news_spiritual_response`, `youth_feature`) |
| `teacher_ids` | list[str] | IDs of teachers featured in the article |
| `stressor_tags` | list[str] | Stressor categories (e.g. `academic_pressure`, `digital_overload`) |
| `region` | string | Geographic region or feed source region |
| `phrase_flags` | list[str] | Transition phrases flagged by repetition check (e.g. `"Now, let's…"`) |

---

## Optional Keys (Future)

- `secondary_sdgs` — list of additional SDG numbers
- `source_feed_id` — feed that produced the item
- `qc_passed` — whether article passed quality gates

---

## Example Line

```json
{"article_id": "a1b2c3d4e5f6", "date": "2026-03-03T12:00:00+00:00", "topic": "mental_health", "primary_sdg": "3", "template_id": "youth_feature", "teacher_ids": [], "stressor_tags": [], "region": "", "phrase_flags": []}
```

---

## Governance Use

- **Teacher saturation:** `check_teacher_saturation(history, window=20, cap=0.30)` reads `article_metadata.jsonl` to enforce per-teacher and top-2 caps.
- **Template rotation:** `check_template_rotation(history, max_consecutive=3)` fails if 4+ same template in a row.
- **Phrase repetition:** `check_transition_phrase_repetition(text)` populates `phrase_flags` per article.
