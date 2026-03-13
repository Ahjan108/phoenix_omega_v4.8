# Hard-News Beat Map Transition Requirements

**Owner:** Dev 8 (beat-map and transition authoring lane)  
**Subordinate to:** specs/PEARL_NEWS_DETERMINISTIC_BEAT_MAP_SPEC.md

## Purpose

Transitions between major stages of a hard-news article must be **deterministic** so that:

1. The same payload can render coherently across 2–3 beat maps.
2. Changing beat map does not produce weak or generic glue between blocks.
3. Rhythm and causal spine stay intact regardless of slot order.

Do **not** rely on prompted glue for reordered articles. Use deterministic transition lines from packs or map-specific transition guidance.

---

## Required Transition Families

Every hard-news beat map uses these six transition families at the following boundaries:

| Transition family | When used | Purpose |
|-------------------|-----------|---------|
| loop_to_scale | After youth loop / teacher witness, before scale (news_peg, body_data) | Move from personal/somatic loop to the scale is public now without dropping the reader. |
| scale_to_action | After body_data, before turnaround | Move from scale/stats to youth action evidence so the shift feels earned. |
| action_to_hidden_capacity | After turnaround, before bridge | Move from visible action to the hidden capacity the bridge names. |
| teaching_to_practice | After teacher_perspective, before practice_announce | Move from teacher diagnosis to the concrete practice without sounding like a list. |
| practice_to_sdg | After practice_announce, before sdg_un_tie | Move from practice to UN framework without breaking tone. |
| sdg_to_cta | After sdg_un_tie, before forward_look | Move from framework to door-in / CTA so the reader has a clear next step. |

Each map in hard_news_spiritual_response.yaml defines these via the transitions block (e.g. before_bridge: action_to_hidden_capacity). The payload stays the same; the order of slots changes by map. Transition copy in teacher-topic packs is keyed by these family IDs so the same line can be used across maps where the boundary is the same.

---

## Legal Dependency Order

Beat maps must preserve causal order. No map may:

- Place bridge before turnaround (bridge reframes the action; action must exist first).
- Place practice_announce before teacher_perspective (practice grows out of the teacher diagnosis).
- Place sdg_un_tie before practice_announce (SDG tie follows the practice handoff).

Each map's constraints.requires lists slots that must appear in the sequence. Each map's constraints.forbids lists illegal orderings. Runtime or validation can use these to reject invalid maps or to validate that a sequence obeys dependencies.

---

## Rhythm and Cohesion

- **One causal spine:** pressure/event, youth landing, scale/action, hidden capacity, teacher diagnosis, usable practice, real-world path.
- **Transitions are part of the payload:** Author transition options in teacher-topic packs under the transitions section, keyed by transition family (and optionally by beat_map_id for map-specific lines).
- **No generic glue:** Do not use model-written glue. Use short, deterministic lines that still read well when the preceding block varies by beat map.

Writers should author transitions with beat-map reuse in mind: the same transition line may sit after different preceding content depending on the map, so it should not assume a single fixed predecessor.
