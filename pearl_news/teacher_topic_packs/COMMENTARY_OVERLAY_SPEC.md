# Commentary Deterministic Overlay Spec (Dev 9)

**Status:** Scaffold only — commentary is **not live** until hard news deterministic path is proven.  
**Ownership:** Dev 9 (commentary overlay lane)  
**Subordinate to:** [PEARL_NEWS_DETERMINISTIC_TEACHER_TOPIC_PACK_SPEC](../../specs/PEARL_NEWS_DETERMINISTIC_TEACHER_TOPIC_PACK_SPEC.md), [PEARL_NEWS_DETERMINISTIC_BEAT_MAP_SPEC](../../specs/PEARL_NEWS_DETERMINISTIC_BEAT_MAP_SPEC.md)

---

## 1. Purpose

Define the **commentary** article-type overlay for deterministic teacher-topic packs:

- Overlay schema for `overlays/commentary/{teacher_id}__{topic}.yaml`
- Mapping from commentary template slots to deterministic payload fields vs prompted (factual compression) slots
- Rules so that when commentary is enabled, prompted slots remain limited to factual compression only

Commentary is **scaffolded only**. It must **not** be wired into the live pipeline until the hard-news deterministic path is proven and accepted.

---

## 2. Commentary Overlay Schema

Overlays live under:

```text
pearl_news/teacher_topic_packs/overlays/commentary/
  ahjan__climate.yaml
  maat__peace_conflict.yaml
  ...
```

File naming: `{teacher_id}__{topic}.yaml` (double underscore). The runtime loads the base pack from `teachers/{teacher_id}/{topic}.yaml`, then deep-merges the overlay when `template_id == "commentary"`.

### 2.1 Overlay structure

An overlay is a YAML fragment that **adds or overrides** keys on the merged pack. It does **not** need to repeat identity, persona, or topic_fit unless overriding.

Allowed top-level keys:

| Key | Required in overlay? | Description |
|-----|----------------------|-------------|
| `thesis` | Recommended | Commentary-specific: thesis options for the piece. |
| `teaching_interpretation` | Recommended | Full-block options for teaching interpretation (commentary-specific block). |
| `civic_recommendation` | Recommended | Civic recommendation options. |
| `teacher_intro` | Optional | Override or add options with `article_types: ["commentary"]`. |
| `teacher_witness` | Optional | Override or add options. |
| `turnaround` | Optional | Override or add options. |
| `bridge` | Optional | Override or add options. |
| `teacher_perspective` | Optional | Override or add options. |
| `practice` | Optional | Override or add options. |
| `sdg` | Optional | Override or add. |
| `title_system.headline_layer_2` | Optional | Override or add options for commentary. |

Schema version and identifiers:

```yaml
# Optional; if present, must match overlay usage
schema_version: 1
# Optional; overlay applies to this teacher/topic (for validation)
teacher_id: ahjan
topic: climate
```

### 2.2 Option shape (same as base pack)

Each section that has `options` follows the same shape as the base pack:

- `default_id`: optional, used when filtering leaves no valid option
- `options`: list of `{ id, line? }` or `{ id, header?, paragraphs?, ... }` plus `metadata` / inline metadata (`article_types`, `semantic_family`, `tone`, etc.)

Every option used **only** for commentary should include `article_types: ["commentary"]` in metadata (or equivalent) so the selector can filter.

### 2.3 Validation rules

- Overlay YAML must be valid and mergeable with the base pack (no conflicting types).
- If `thesis`, `teaching_interpretation`, or `civic_recommendation` are present, they must have at least one option or a `default_id` pointing to an option.
- No new top-level keys other than those listed above (and schema_version, teacher_id, topic) unless the canonical pack spec is extended.

---

## 3. Commentary Slot Mapping (Deterministic vs Prompted)

Mapping from commentary **template slots** to **payload source**. Prompted slots are limited to **factual compression** only.

| Template slot | Source | Deterministic? | Notes |
|---------------|--------|----------------|-------|
| `label` | fixed | N/A | Value: `"Commentary"`. |
| `headline` | composite | Layer 1 optional prompt; Layer 2 deterministic | `headline_layer_1` may be prompted; `headline_layer_2` from pack/overlay. |
| `thesis` | pack/overlay | **Yes** | From overlay or base pack `thesis.options`. |
| `event_reference` | news_event / prompt | **No** | Factual compression only (what happened, event summary). |
| `teaching_interpretation` | pack/overlay | **Yes** | From overlay or base pack `teaching_interpretation.options`. |
| `civic_recommendation` | pack/overlay | **Yes** | From overlay or base pack `civic_recommendation.options`. |
| `sdg_reference` | pack/overlay | **Yes** | From pack `sdg` (primary + fallback_un_tie). |

Shared teacher blocks (when used in commentary) come from base pack + overlay merge, with `article_types: ["commentary"]` filtering:

- `teacher_intro`
- `teacher_witness`
- `turnaround`
- `bridge`
- `teacher_perspective`
- `practice_announce`

So: **deterministic** = thesis, teaching_interpretation, civic_recommendation, sdg_reference, plus shared teacher blocks above. **Prompted** = headline_layer_1 (optional), event_reference / news_peg / body_data (factual compression only). No prompted generation of teacher meaning, bridge logic, or civic/SDG framing.

---

## 4. Beat-map alignment (when commentary is enabled)

Commentary beat maps (from beat map spec) are:

- `cm_thesis_then_bridge`: headline → thesis → event reference → teacher witness → bridge → interpretation → civic recommendation → SDG
- `cm_thesis_then_data`: headline → thesis → event reference → body data → teacher witness → interpretation → civic recommendation → SDG

Payload fields that must be available for these maps:

- thesis (deterministic)
- event_reference (prompted / factual)
- teacher_witness (deterministic)
- bridge (deterministic)
- teaching_interpretation (deterministic)
- civic_recommendation (deterministic)
- sdg_reference (deterministic)
- body_data (prompted, factual) — only for `cm_thesis_then_data`

Order is determined by the beat map; payload content is determined by pack + overlay + factual slots.

---

## 5. “Not live” policy

- **Commentary deterministic path is not wired** in the current pipeline. The runtime does **not** call a `build_commentary_deterministic_plan` (or equivalent) or prefill commentary slots from packs/overlays in production.
- This spec and the overlay schema/fixtures exist so that:
  1. Commentary slots are **mapped** to deterministic payload fields.
  2. Overlay schema and fixtures are in place for when hard news is proven.
  3. When commentary is enabled, **prompted slots stay limited to factual compression** (event_reference, optional headline_layer_1, body_data where applicable).
- Enabling commentary deterministically is a **later step** (integration owner / Dev 1) after hard-news deterministic path is stable and accepted.

---

## 6. Summary

- **Overlay schema:** `overlays/commentary/{teacher_id}__{topic}.yaml` adds/overrides thesis, teaching_interpretation, civic_recommendation, and optional shared blocks; same option shape as base pack.
- **Slot mapping:** thesis, teaching_interpretation, civic_recommendation, sdg_reference, and shared teacher blocks = deterministic; event_reference and optional headline/body_data = prompted factual only.
- **Commentary is scaffold only:** do not make commentary live until hard news is proven.
