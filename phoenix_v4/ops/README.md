# Phoenix V4 — Ops tooling

Ops-owned. Content team reacts; ops runs.

## Coverage health report (Phase 2 + 2.5)

**Schema:** v1.0 (stable contract) → v1.1 (velocity by persona/topic, deficit trend, risk trend). See `docs/COVERAGE_HEALTH_JSON_SCHEMA.md`.

**Outputs:** `artifacts/ops/coverage_health_weekly_{date}.{md,csv,json}`. JSON is the dashboard contract; when previous week exists, v1.1 adds `velocity_by_persona`, `velocity_by_topic`, `deficit_trend_delta`, `tuple_risk_trend`, and indices for stagnation/decay visibility.

## Release-wave similarity & burst controls (Phase 6)

Validates a **batch** of compiled plan JSONs (e.g. a week’s release wave) for:

- **Weekly caps** — max same topic, persona, arc, band_sig, slot_sig, variation_signature, teacher_id, wave fingerprint
- **Exact clusters** — same structural fingerprint (arc|slot_sig|band_sig|variation) → fail if cluster size exceeds cap
- **Near clusters** — Jaccard similarity on token set (arc, slot, band, var, ex, role) ≥ threshold → fail if cluster size ≥ min
- **Anti-homogeneity score** — normalized entropy over topic/persona/arc/band/slot/variation; fail if below `min_score`
- **Sliding window** (optional) — share caps over last N weeks when `--history-index` is provided (index rows should have `release_week` or `publish_date`)

**CLI (from repo root):**

```bash
PYTHONPATH=. python3 phoenix_v4/ops/check_release_wave.py \
  --plans-dir artifacts/plans/wave_2026_02_25 \
  --calendar-week 2026-W09 \
  --history-index artifacts/catalog_similarity/index.jsonl \
  --out-dir artifacts/ops/release_wave_checks \
  --config config/release_wave_controls.yaml
```

- **Exit 0** — PASS  
- **Exit 1** — FAIL (default on any violation)  
- **Exit 2** — WARN-only (when `--warn-only` and violations present)

**Outputs:** `release_wave_check_{week}.json`, `release_wave_check_{week}.md` in `--out-dir`.

**Config:** `config/release_wave_controls.yaml` — `release_wave_controls.weekly_caps`, `clustering`, `sliding_window`, `anti_homogeneity`, `reporting`.

**Integration:** Run after wave orchestrator selects candidate set; if FAIL, reselect or move books. Pre-export gate: no wave export without wave pass.

## Catalog Emotional Distribution (Phase 9 — standalone)

90-day rolling **macro telemetry**: catalog-level emotional flattening and brand/persona drift. Cheap (daily cache), incremental, deterministic.

**Inputs:** `--history-index` (JSONL with `publish_date`/`release_week`, `band_sig` or `band_seq`) and/or `--plans-dir` (plan JSONs; file mtime as date proxy).

**Daily cache:** `artifacts/ops/cache/catalog_emotional_daily_{YYYY-MM-DD}.jsonl` — one line per book (date, book_id, brand_id, persona_id, topic_id, band_sig, max_band, min_band, volatility). Build step fills missing dates from index or plans.

**Volatility (per book):** `0.7 * transition_energy + 0.3 * range_util` from band sequence (transition_energy = Σ|b_i − b_{i−1}| / T_max, range_util = (max−min)/4).

**Outputs:** `artifacts/ops/catalog_emotional_distribution_{report_date}.json` — `global`, `by_brand`, `by_persona`, `drift` (vs previous window), `alerts` (GLOBAL_ENTROPY_LOW, DRIFT_BAND5_DROP, etc.). Optional: `--md` for a short `.md` summary.

**CLI (from repo root):**

```bash
PYTHONPATH=. python3 phoenix_v4/ops/catalog_emotional_distribution.py \
  --report-date 2026-03-04 \
  --window-days 90 \
  --history-index artifacts/catalog_similarity/index.jsonl \
  --plans-dir artifacts/plans \
  --cache-dir artifacts/ops/cache \
  --out-dir artifacts/ops \
  --config config/catalog_emotional_distribution.yaml
```

- **Exit 0** — PASS (no alerts)  
- **Exit 2** — WARN (warn-level alerts)  
- **Exit 1** — FAIL (any alert in `hard_fail_codes`)

**Config:** `config/catalog_emotional_distribution.yaml` — `thresholds` (entropy, volatility, band5_share), `drift` (entropy_drop, band5_drop, etc.), `alert_policy` (default_severity, hard_fail_codes), `minimums` (brand_min_books, persona_min_books), **`recommendations`** (Phase 9 contract: one fixed remediation string per alert code; no freeform; ops executes as written).

**Recommendation contract:** Every alert code maps to a single remediation in YAML. Policy is auditable; code does not embed prose. If brand_emotional_range conflicts with a recommendation, brand range wins.
