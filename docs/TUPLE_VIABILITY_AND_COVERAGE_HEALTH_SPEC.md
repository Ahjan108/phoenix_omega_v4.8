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
| 100% atoms coverage sim test | **Implemented** | `tests/test_atoms_coverage_100_percent.py`; see §7. |

---

## 7. 100% atoms coverage sim test (STORY + non-STORY)

**Purpose:** Assert that (1) every (persona, topic, engine) has a non-empty STORY pool, and (2) every (persona, topic) has non-empty canonical pools for HOOK, SCENE, REFLECTION, EXERCISE, and INTEGRATION, so all US-English books can be built without relying on fallbacks.

**Module:** `tests/test_atoms_coverage_100_percent.py`. Authority: this spec and **docs/UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md**.

### Contract

**STORY (tuple-level):**

- **Tuple universe:** Personas from `config/catalog_planning/canonical_personas.yaml` × topics (and their `allowed_engines`) from `config/topic_engine_bindings.yaml`. Same universe as the coverage health report (no format dimension; one check per (persona, topic, engine)).
- **Requirement:** For each (persona, topic, engine), `atoms/{persona}/{topic}/{engine}/CANONICAL.txt` must **exist** and be **non-empty** (at least one valid STORY atom). Parsing uses `phoenix_v4.planning.assembly_compiler._parse_canonical_txt` (same as tuple viability gate). If the file fails validation or parse, the tuple is treated as missing (no STORY pool).

**Non-STORY (persona–topic-level):**

- **Pair universe:** Same personas × same topics (no engine dimension); one check per (persona, topic) per slot type.
- **Requirement:** For each (persona, topic) and each slot type in **HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION**, `atoms/{persona}/{topic}/{slot_type}/CANONICAL.txt` must **exist** and be **non-empty** (at least one block matching the canonical block format). Same rigor as STORY: any gap fails the test. EXERCISE is checked for canonical content only (no fallback to practice library).

- **Path:** Run from repo root. The module inserts `REPO_ROOT` into `sys.path` at load so `phoenix_v4` imports work when the script is run from any working directory. Optional env **`ATOMS_ROOT`** overrides the atoms directory (e.g. for CI or alternate content roots).

### Behavior

| Condition | Effect |
|-----------|--------|
| **BLOCKER** | Any (persona, topic, engine) missing STORY file or with no parseable STORY atom → test **fails**; prints missing paths and coverage percentage. |
| **BLOCKER** | Any (persona, topic, slot_type) missing non-STORY file or with no parseable block (HOOK/SCENE/REFLECTION/EXERCISE/INTEGRATION) → test **fails**; prints missing paths per slot type. |
| **RED (report only)** | STORY pools with `story_count < min_story_pool_size` (from `config/gates.yaml` → `tuple_viability.min_story_pool_size`) are **reported** only; they do **not** fail the test. |

### How to run

| Mode | Command |
|------|--------|
| Script (no pytest) | `python3 tests/test_atoms_coverage_100_percent.py` |
| Pytest | `python3 -m pytest tests/test_atoms_coverage_100_percent.py -v` |

**Exit code:** **0** only when both STORY and non-STORY coverage are 100%; **1** if either fails.

### Pytest entry points

| Test | Purpose |
|------|--------|
| `test_100_percent_atoms_for_all_books` | Asserts no missing STORY pools; fails with missing paths and percentage if not 100%. |
| `test_100_percent_non_story_atoms_for_all_books` | Asserts no missing HOOK/SCENE/REFLECTION/EXERCISE/INTEGRATION pools for any (persona, topic); fails on any gap. |
| `test_atoms_coverage_summary` | Prints STORY coverage percentage and up to 20 missing paths; does not fail (useful for CI logs). |
| `test_non_story_coverage_summary` | Prints non-STORY coverage percentage and missing counts per slot type; does not fail (useful for CI logs). |

### Programmatic API

- **`run_sim_test() -> tuple[bool, str]`** — STORY only. Returns `(passed, message)`. `passed` is True only when every (persona, topic, engine) has a non-empty STORY pool.
- **`run_non_story_sim_test() -> tuple[bool, str]`** — Non-STORY only. Returns `(passed, message)`. `passed` is True only when every (persona, topic) has non-empty canonical pools for HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION.

When run as script (`if __name__ == "__main__"`), both are executed; exit 1 if either fails.

### Getting to 100%

- **STORY:** Add or fix missing `atoms/{persona}/{topic}/{engine}/CANONICAL.txt` so each has at least one valid STORY atom (and ideally ≥ `min_story_pool_size` per `config/gates.yaml`). See **docs/UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md** for personas/topics and what’s needed for full books.
- **Non-STORY:** Add or fix missing `atoms/{persona}/{topic}/{slot_type}/CANONICAL.txt` for each slot_type in HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION so each file has at least one block (same block format as `pool_index._parse_block_file_canonical`).

### Implementation summary (from chat)

- **File:** `tests/test_atoms_coverage_100_percent.py`. Catalog from `canonical_personas.yaml` × `topic_engine_bindings.yaml` (topics with `allowed_engines`). STORY pool check: path exists and `_parse_canonical_txt` returns ≥1 atom; parse/validation errors count as missing. Non-STORY: path exists and block regex returns ≥1 block per (persona, topic) per slot type; CI fails on any gap.
- **Run:** Script (exit 0/1) or pytest (all four tests). Repo root added to `sys.path` at import so `phoenix_v4` works from any cwd. Optional `ATOMS_ROOT` env for override.
- **Cross-references:** docs/PLANNING_STATUS.md (playbook + doc status), docs/SYSTEMS_V4.md (coverage row + doc map), docs/UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md (sim test paragraph), specs/V4_5_PRODUCTION_READINESS_CHECKLIST.md (§2 optional), specs/README.md (content coverage), REPO_FILES.md (atoms section), docs/SYSTEMS_AUDIT.md (CI/tools table).

---

## 8. Related docs

- **docs/SYSTEMS_V4.md** — Canonical systems overview; CI and release gates; 100% atoms coverage test.
- **docs/UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md** — Personas/topics and what’s needed for full books; STORY coverage.
- **phoenix_v4/ops/README.md** — Ops tooling index; coverage health report.
- **unified_personas.md** — Source of truth for active personas and topics; canonical config must align.
