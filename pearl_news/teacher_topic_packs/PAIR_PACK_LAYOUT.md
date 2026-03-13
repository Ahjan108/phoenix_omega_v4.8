# Pair-Pack File Layout and Convergence Schema

**Owner:** Dev 11 (Interfaith and UNSAY pair-pack lane)  
**Status:** Design and fixture work; not live in pipeline.  
**Spec alignment:** [PEARL_NEWS_DETERMINISTIC_TEACHER_TOPIC_PACK_SPEC](../../specs/PEARL_NEWS_DETERMINISTIC_TEACHER_TOPIC_PACK_SPEC.md) §4.3, §4.4, §9.4, §9.6.

## 1. File layout

### 1.1 Interfaith pair packs

One file per teacher-pair per topic. Filename: `teacher_a_id__teacher_b_id.yaml` (double underscore). Topic is the directory name.

```
pearl_news/teacher_topic_packs/
  interfaith/
    peace_conflict/
      maat__ahjan.yaml
    climate/
      master_wu__ahjan.yaml
```

- Path pattern: `interfaith/<topic>/<teacher_a_id>__<teacher_b_id>.yaml`
- Order of teacher IDs in the filename is canonical for that file (teacher_a vs teacher_b in the pack schema).

### 1.2 UNSAY pair packs

Same idea: one file per pair per topic, with stricter convergence fields.

```
pearl_news/teacher_topic_packs/
  unsay/
    climate/
      ahjan__maat.yaml
    mental_health/
      ahjan__sai_ma.yaml
```

- Path pattern: `unsay/<topic>/<teacher_a_id>__<teacher_b_id>.yaml`

### 1.3 Triad packs (optional)

If needed later, triad packs can use a similar layout, e.g.:

```
interfaith/
  peace_conflict/
    maat__ahjan__master_wu.yaml   # optional future
```

Not required for Dev 11 deliverables; documented here for schema usage only.

## 2. Interfaith pair-pack schema (deterministic convergence blocks)

Each interfaith pair-pack file must be valid YAML and include:

| Section | Required | Description |
|--------|----------|-------------|
| `schema_version` | yes | Integer (e.g. `1`) |
| `teacher_a_id` | yes | First teacher (matches filename segment) |
| `teacher_b_id` | yes | Second teacher |
| `topic` | yes | Topic key (e.g. `peace_conflict`, `climate`) |
| `active` | yes | Boolean; only `true` packs are eligible |
| `identity` | optional | Short ref or inline; both traditions for the pair |
| `leaders_present` | yes | Deterministic block: options for who was present / how to introduce the pair |
| `themes_discussed` | yes | Deterministic block: options for themes/convergence themes |
| `youth_commitments` | yes | Deterministic block: youth-focused commitments from the dialogue |
| `sdg_alignment` | yes | Deterministic block: SDG alignment line(s) |
| `convergence` | yes | Deterministic convergence blocks: cross-tradition overlap, not generic agreement |
| `cross_teacher_quote_mapping` | optional | Maps slot or moment to which teacher; for assembly |

Convergence blocks must be **specific** (named overlap, not “both care about healing”). Validation rules (see tests):

- Pair has distinct traditions (teacher_a_id ≠ teacher_b_id; doctrine fit is per single-teacher packs).
- Convergence options are present and non-empty.
- No generic spiritual filler in convergence text.

## 3. UNSAY pair-pack schema (deterministic convergence blocks)

UNSAY packs use the same file layout but stricter, non-live payload design. Each file must include:

| Section | Required | Description |
|--------|----------|-------------|
| `schema_version` | yes | Integer (e.g. `1`) |
| `teacher_a_id` | yes | First teacher |
| `teacher_b_id` | yes | Second teacher |
| `topic` | yes | Topic key |
| `active` | yes | Boolean |
| `teacher_a_diagnosis` | yes | Deterministic options: Teacher A’s diagnosis of the same event (distinct vocabulary) |
| `teacher_b_diagnosis` | yes | Deterministic options: Teacher B’s diagnosis (distinct from A) |
| `convergence_bridge` | yes | Deterministic options: name the exact overlap (40–60 words) |
| `shared_agreement` | yes | Deterministic options: state agreement and shared practice (60–80 words) |
| `practice_announce` | yes | Shared practice name, duration, sidebar pointer |
| `practice_why_a` | yes | Teacher A’s authentic endorsement in A’s vocabulary |
| `practice_why_b` | yes | Teacher B’s authentic endorsement in B’s vocabulary |
| `disagreement_boundary` | optional | Open tension or disagreement; what is *not* conflated |

Validation (non-live):

- Both diagnoses present; distinct (no copy-paste of one into the other).
- Convergence is specific (same hidden burden / structural gap / capacity), not vague.
- Shared practice and both `practice_why_*` are present and authentic to each tradition.

## 4. Usage (non-live)

- **Interfaith / UNSAY pair-packs are not wired into the live pipeline in this lane.** Dev 11 delivers layout, schema, deterministic convergence block definitions, and non-live fixtures + tests.
- Runtime selector and renderer changes (e.g. loading pair-packs in `deterministic_teacher_topic.py`) are owned by Dev 1; this lane only defines the pack layout and content schema.
- Fixtures under `interfaith/` and `unsay/` are for validation and tests only until the integration owner enables them.

## 5. References

- Single-teacher pack schema: [PEARL_NEWS_DETERMINISTIC_TEACHER_TOPIC_PACK_SPEC](../../specs/PEARL_NEWS_DETERMINISTIC_TEACHER_TOPIC_PACK_SPEC.md) §5
- Interfaith slot mapping: §9.4 Interfaith Dialogue
- UNSAY slot mapping: §9.6 UNSAY
- UNSAY product spec: [PEARL_NEWS_UNSAY_DIALOGUE_SPEC](../../specs/PEARL_NEWS_UNSAY_DIALOGUE_SPEC.md)
