# Tuple Viability and Coverage Health — System Spec

**Purpose:** Single source of truth for the tuple (catalog) viability preflight gate and the weekly coverage health report.  
**Audience:** Ops, release, engineers.  
**Authority:** This doc defines accepted behavior and implementation status.  
**Last updated:** 2026-02-25

---

## 1. Tuple definition and scope

A **tuple** is the atomic production unit:

```
(persona, topic, engine, format)
```

- **persona:** Active persona ID (source: `config/catalog_planning/canonical_personas.yaml`; must align with `unified_personas.md`).
- **topic:** Topic ID present in `config/topic_engine_bindings.yaml` (bindings define allowed engines per topic).
- **engine:** Engine ID listed in `allowed_engines` for that topic (e.g. `false_alarm`, `spiral`, `watcher`, `overwhelm`, `shame`, `comparison`, `grief`).
- **format:** Format structural ID (e.g. `F006`), from coverage/release format policy.

**Tuple universe (catalog scope):** The set of all tuples that *should* be considered for coverage and viability is:

- **personas** × **topics** × **allowed_engines per topic** × **formats**

where personas come from canonical config, topics from bindings keys that define `allowed_engines`, and formats from coverage-health format policy (e.g. `config/gates.yaml` → `coverage_health.formats`). The coverage report must evaluate this full universe so that **missing arcs** (NO_ARC) appear as deficit tuples, not only tuples that already have an arc file.

---

## 2. Tuple viability preflight gate (Phase 1)

Runs **before Stage 1** (hard entry gate). Not during compile, not after planner.

### Module and CLI

| Item | Value |
|------|--------|
| **Module** | `phoenix_v4/gates/check_tuple_viability.py` |
| **CLI** | `python3 phoenix_v4/gates/check_tuple_viability.py --persona <id> --topic <id> --engine <id> --format <id>` |

Optional: `--teacher-mode`, `--teacher <id>`, `--brand <id>`, `--repo <path>`, `--json`.

### Checks (in order)

| Check | Source | Error if missing |
|-------|--------|-------------------|
| Binding exists | `config/topic_engine_bindings.yaml`: topic key (with `_bindings_topic_key` mapping, e.g. `grief_topic` → `grief`), engine in `allowed_engines` | `NO_BINDING` |
| Arc exists | `config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__{format}.yaml` (flat file per tuple, not nested folders) | `NO_ARC` |
| STORY pool exists | `atoms/{persona}/{topic}/{engine}/CANONICAL.txt` non-empty | `NO_STORY_POOL` |
| Min STORY depth | `len(pool) >= min_story_pool_size` (from `config/gates.yaml` → `tuple_viability.min_story_pool_size`) | `POOL_TOO_SHALLOW` |
| Required bands | Arc `emotional_curve` bands covered by pool bands | `BAND_DEFICIT` |
| Teacher Mode (optional) | When `--teacher-mode`: approved EXERCISE count ≥ min (from gates.yaml) | `TEACHER_EXERCISE_DEFICIT` |
| Brand emotional range (optional) | When `--brand`: arc required bands within brand `[min_band, max_band]` from `config/catalog_planning/brand_emotional_range.yaml` | `ARC_OUTSIDE_BRAND_EMOTIONAL_RANGE` |

Exit: **0** PASS, **1** FAIL. No override.

### Integration

Pipeline calls the gate before Stage 1 (e.g. `scripts/run_pipeline.py`). Tuple viability is not re-checked during compile; it is a preflight only.

---

## 3. Weekly coverage health report (Phase 2)

Ops-owned. Run on schedule (cron or CI).

### Module and outputs

| Item | Value |
|------|--------|
| **Module** | `phoenix_v4/ops/generate_coverage_health_report.py` |
| **Outputs** | `artifacts/ops/coverage_health_weekly_{date}.md`, `.csv`, `.json` |

### Tuple universe (required behavior)

The report must evaluate **catalog viability**, not only “arc health.” Therefore:

- **Tuple discovery:** Tuples are taken from the **catalog universe**: personas (from `config/catalog_planning/canonical_personas.yaml`) × topics (from `config/topic_engine_bindings.yaml` keys that have `allowed_engines`) × allowed_engines per topic × formats (from `config/gates.yaml` → `coverage_health.formats`, default e.g. `["F006"]`).
- **Then** for each tuple: check binding, **arc existence** (file at `config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__{format}.yaml`), STORY pool, bands, depth, timestamps, and compute risk and deficit codes.
- **NO_ARC** must appear for any tuple in the universe that does not have an arc file. Missing arcs are not invisible.

### Per-tuple metrics

For each (persona, topic, engine, format) in the universe:

| Metric | Source |
|--------|--------|
| Binding exists | topic_engine_bindings (topic key + engine in allowed_engines) |
| Arc exists | `master_arcs/{persona}__{topic}__{engine}__{format}.yaml` |
| Story count | `atoms/{persona}/{topic}/{engine}/CANONICAL.txt` (parsed) |
| Band counts | From STORY atom metadata |
| Required bands missing | Arc emotional_curve vs pool bands |
| Min depth satisfied | story_count >= min_story_pool_size |
| Last story update | CANONICAL.txt mtime |
| Risk | BLOCKER / RED / YELLOW / GREEN (see below) |
| Deficit codes | NO_BINDING, NO_ARC, NO_STORY_POOL, POOL_TOO_SHALLOW, BAND_DEFICIT |

### Risk model

- **BLOCKER:** no binding or no arc.
- **RED:** arc exists but story_count < min_depth or any required band missing.
- **YELLOW:** depth and bands OK but band distribution skew > threshold.
- **GREEN:** otherwise.

### Summary and alerts

Report includes: total tuples, viable (GREEN), blocked (BLOCKER), RED, YELLOW, total STORY atoms, top risk tuples, top deficit codes, aging (stale pools), velocity vs previous week when available, and optional alerts (stagnation, decay, catalog emotional). Content team may only act when risk in {BLOCKER, RED}; backlog CSV updated by ops only.

---

## 4. Paths and config (canonical)

| Concept | Path or config |
|--------|-----------------|
| Arc file (single file per tuple) | `config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__{format}.yaml` |
| STORY pool | `atoms/{persona}/{topic}/{engine}/CANONICAL.txt` |
| Topic–engine bindings | `config/topic_engine_bindings.yaml` |
| Canonical personas | `config/catalog_planning/canonical_personas.yaml` (align with unified_personas.md) |
| Gate / coverage config | `config/gates.yaml` (tuple_viability, coverage_health, coverage_health.formats) |
| Brand emotional range | `config/catalog_planning/brand_emotional_range.yaml` (optional, for gate when --brand) |

Engine IDs are those in bindings (e.g. `false_alarm`, `spiral`, `watcher`, `overwhelm`, `shame`, `comparison`, `grief`), not placeholders like `E1`.

---

## 5. Implementation status

| Component | Status | Notes |
|-----------|--------|--------|
| Tuple viability gate | **Implemented** | `phoenix_v4/gates/check_tuple_viability.py`; binding, arc, STORY depth, bands, teacher, brand range. |
| Pipeline preflight | **Implemented** | Gate invoked before Stage 1 in run_pipeline. |
| Coverage report (arc-only discovery) | **Deprecated** | Previous implementation discovered tuples only from existing arc filenames; NO_ARC could not appear for missing tuples. |
| Coverage report (catalog universe) | **Implemented** | Tuple universe from personas × bindings (topics × allowed_engines) × formats; then arc existence and other checks. NO_ARC appears for missing arcs. |
| Format policy for coverage | **Config** | `config/gates.yaml` → `coverage_health.formats` (default `["F006"]`). |

---

## 6. Related docs

- **docs/SYSTEMS_V4.md** — Canonical systems overview; CI and release gates.
- **phoenix_v4/ops/README.md** — Ops tooling index; coverage health report.
- **unified_personas.md** — Source of truth for active personas and topics; canonical config must align.
