# Coverage Health JSON — Dashboard Schema

**Output:** `artifacts/ops/coverage_health_weekly_{date}.json`  
**Owner:** Ops. Content team reacts; ops runs the report.

---

## Schema versioning

- **1.0** — Stable contract: config snapshot, repo/git, summary (risk_counts, aging, velocity total), tuples (binding/arc/story_pool/bands/deficit_codes/risk), indices (by_risk, by_persona, by_topic).
- **1.1** — Backwards-compatible expansion: `previous_report`, `deltas` (global, by_persona, by_topic, by_tuple), `alerts` (stagnation, decay, catalog_emotional), velocity/trend in summary, indices `by_persona_risk`, `by_topic_risk`, `velocity_by_persona`, `velocity_by_topic`, `risk_transitions`, and **Phase 9** `catalog_emotional_distribution` (macro drift detection).

---

## v1.1 top-level contract

| Key | Description |
|-----|-------------|
| `schema_version` | `"1.1"` |
| `previous_report` | `{ expected_report_date, loaded, path, git_commit }` — metadata for prior week report; `loaded` false if file missing. |
| `deltas` | Present only when previous report loaded. Cross-week deltas: `global`, `by_persona`, `by_topic`, `by_tuple`. |
| `alerts` | `{ stagnation: { by_persona, by_topic }, decay: { global }, catalog_emotional: [ ] }` — ops-actionable; driven by `config/gates.yaml`. |
| `catalog_emotional_distribution` | **Phase 9.** Rolling-window (concept 90d) band distribution, entropy, persona volatility, drift vs previous run. |

---

## previous_report

- **expected_report_date** — `report_date - 7` (YYYY-MM-DD).
- **loaded** — `true` if that report JSON was found and parsed.
- **path** — Relative path to expected report file.
- **git_commit** — From that report’s `repo.git.commit` when loaded.

---

## deltas

When `previous_report.loaded` is false, `deltas` is omitted or empty.

- **global** — `story_count_total`, `risk_counts`, `stale_counts`; each has `current`, `previous`, `delta`. Stale keys: `over_14`, `over_30`, `over_60`.
- **by_persona** — `{ persona_id: { story_count_total: { current, previous, delta }, risk_counts_delta, stale_over_30_delta } }`.
- **by_topic** — Same shape as by_persona, keyed by `topic_id`.
- **by_tuple** — `{ tuple_id: { risk: { current, previous }, story_count: { current, previous, delta }, missing_bands: { current, previous }, deficit_codes: { added, removed } } }`.

---

## alerts

### stagnation

Config: `coverage_health_alerts.stagnation` (e.g. `enabled`, `window_weeks`, `min_story_delta_total`, `require_risk_not_green`).

- **by_persona** — List of `{ persona_id, window_weeks, weeks_loaded, story_delta_total, red_or_blocker_tuples, top_deficit_codes, recommendation }`. Fired when 4-week story delta &lt; threshold and (if required) persona has RED/BLOCKER tuples.
- **by_topic** — Same shape, keyed by `topic_id`.

### decay

Config: `coverage_health_alerts.decay` (e.g. `stale_over_30_wow_increase_threshold`, `stale_over_60_absolute_threshold`, `red_blocker_wow_increase_threshold`, `green_wow_decrease_threshold`).

- **global** — List of `{ code, ... }`. Codes include `STALE_OVER_30_SPIKE`, `STALE_OVER_60_CAP`, `RISK_REGRESSION`, `GREEN_DECREASE`; each includes threshold and recommendation.

### catalog_emotional (Phase 9)

Config: `catalog_emotional_distribution.alerts` (e.g. `entropy_below_threshold`, `band_5_share_drop_above`, `persona_volatility_below_threshold`).

- **catalog_emotional** — List of `{ code, ... }`. Codes: `ENTROPY_BELOW_THRESHOLD`, `BAND_5_SHARE_DROP`, `PERSONA_VOLATILITY_LOW`; each includes threshold and recommendation. Detects emotional flattening and band convergence.

---

## catalog_emotional_distribution (Phase 9)

Macro-level drift detection: emotional diversity across the catalog, not per-wave or per-tuple.

| Field | Description |
|-------|-------------|
| `window_days` | 90 (concept); drift is computed vs previous report run (minimal compute path). |
| `global_band_distribution` | `{ "1".."5": proportion }` — band frequency from current story pools. |
| `global_band_entropy` | Shannon entropy of band distribution, normalized 0..1 (max = log2(5)). Low → flattening. |
| `brand_band_entropy` | `{ brand_id: entropy }` — per-brand (currently global until brand_id per tuple). |
| `persona_volatility_index` | `{ persona_id: 0..1 }` — normalized entropy of that persona’s band mix. Low → persona content emotionally flat. |
| `drift_vs_previous_window` | Present when previous report had this block. `band_1_share_delta` … `band_5_share_delta` (current − previous). |

**Alerts:** entropy below threshold, band_5 share drop above threshold, personas with volatility below threshold.

---

## v1.1 summary additions

| Field | Type | Description |
|-------|------|-------------|
| `velocity_by_persona` | `{ persona_id: { story_count_this_week, story_count_last_week, delta } }` | Per-persona story pool delta (week over week). Present when previous week report exists. |
| `velocity_by_topic` | `{ topic_id: { story_count_this_week, story_count_last_week, delta } }` | Per-topic story pool delta. Present when previous week report exists. |
| `deficit_trend_delta` | `[ { code, count_this_week, count_last_week, delta } ]` | Deficit code counts vs last week; sorted by \|delta\| desc. |
| `tuple_risk_trend` | `{ transition_counts: { "RED_to_GREEN": n, ... }, improved_count, worsened_count }` | Count of tuples that changed risk (improved = lower risk rank, worsened = higher). |
| `velocity.week_over_week_story_delta_median` | number \| null | Median per-tuple story count delta when previous week exists. |

---

## v1.1 indices

| Key | Description |
|-----|-------------|
| `by_persona_risk` | `{ persona_id: { BLOCKER: [tuple_id, ...], RED: [...], YELLOW: [...], GREEN: [...] } }` — no client-side grouping. |
| `by_topic_risk` | `{ topic_id: { BLOCKER: [...], RED: [...], YELLOW: [...], GREEN: [...] } }` |
| `velocity_by_persona` | Same structure as summary; quick lookup for dashboard heatmaps (persona stagnation). |
| `velocity_by_topic` | Same structure as summary; quick lookup (topic stagnation). |
| `risk_transitions` | `{ "RED_to_GREEN": [tuple_id, ...], "GREEN_to_RED": [...], ... }` — tuple_ids that changed risk category. |

---

## Config (gates.yaml)

**coverage_health_alerts**

- **stagnation** — `enabled`, `window_weeks`, `min_story_delta_total`, `require_risk_not_green`.
- **aging** — `stale_days_threshold`, `stale_share_threshold` (for future use).
- **decay** — `enabled`, `stale_over_30_wow_increase_threshold`, `stale_over_60_absolute_threshold`, `red_blocker_wow_increase_threshold`, `green_wow_decrease_threshold`.

**catalog_emotional_distribution** (Phase 9, embedded in coverage report)

- **window_days** — 90 (rolling-window concept).
- **alerts** — `enabled`, `entropy_below_threshold`, `band_5_share_drop_above`, `persona_volatility_below_threshold`.

**Standalone Phase 9 report** (90-day rolling, daily cache, history-index/plans-dir): see `phoenix_v4/ops/catalog_emotional_distribution.py`. Output: `artifacts/ops/catalog_emotional_distribution_{date}.json` with `global`, `by_brand`, `by_persona`, `drift`, `alerts` (GLOBAL_ENTROPY_LOW, DRIFT_BAND5_DROP, etc.). Config: `config/catalog_emotional_distribution.yaml`. The embedded block in the coverage report is a current-snapshot view; the standalone report is the full rolling-window telemetry.

---

## Stagnation / decay / emotional drift use

- **alerts.decay.global** → Pause releases; resolve backlog deficits.
- **alerts.stagnation.by_persona / by_topic** → Reopen content only for tuples with explicit deficit codes per backlog CSV.
- **indices.by_persona_risk** / **by_topic_risk** → Heatmaps by tuple risk and aging without client-side grouping.
- **catalog_emotional_distribution** + **alerts.catalog_emotional** → Macro drift: entropy drop, band_5 share drop, low persona volatility → review arc curves and band mix to avoid emotional flattening.

When previous week report is missing, `deltas` is empty and velocity/trend summary fields may be omitted; `schema_version` remains `"1.1"` and base fields are still present.
