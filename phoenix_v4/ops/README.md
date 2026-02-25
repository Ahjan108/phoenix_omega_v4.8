# Phoenix V4 — Ops tooling

Ops-owned. Content team reacts; ops runs.

## Coverage health report (Phase 2 + 2.5)

**Tuple universe:** Tuples are discovered from **catalog** (personas from `config/catalog_planning/canonical_personas.yaml` × topics × allowed_engines from `config/topic_engine_bindings.yaml` × formats from `config/gates.yaml` → `coverage_health.formats`). This ensures **NO_ARC** appears for tuples that have no arc file yet (catalog viability), not only “arc health.” Spec: [docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md](../../docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md).

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

## Cross-Brand Divergence Index (Phase 10 — CBDI)

System-level guard against **brands slowly collapsing into each other structurally**. Measures identity separation across brands over a rolling window (default 90 days).

**Metrics (per brand pair):** Jensen-Shannon Divergence (JSD) on five dimensions — arc distribution, slot_sig distribution, band_sig distribution, engine distribution, volatility bucket (low/med/high). Weighted combination: `0.30*D_arc + 0.20*D_slot + 0.20*D_band + 0.15*D_engine + 0.15*D_vol`. CBDI in [0,1]; 0 = identical, 1 = maximally different.

**Inputs:** `--history-index` (JSONL with `publish_date`/`release_week`, `brand_id`, `arc_id`, `slot_sig`, `band_sig`, `engine_id`) and/or `--plans-dir` (plan JSONs; file mtime = date). Only brands with ≥ `minimum_books_per_brand` (default 20) in the window are evaluated.

**Outputs:** `artifacts/ops/cross_brand_divergence_{report_date}.json` — `brands_evaluated`, `pairwise_scores` (brand_a, brand_b, score, components), `alerts` (BRAND_CONVERGENCE_LOW / BRAND_CONVERGENCE_CRITICAL).

**CLI (from repo root):**

```bash
PYTHONPATH=. python3 phoenix_v4/ops/cross_brand_divergence.py \
  --report-date 2026-03-04 \
  --window-days 90 \
  --history-index artifacts/catalog_similarity/index.jsonl \
  --plans-dir artifacts/plans \
  --out-dir artifacts/ops \
  --config config/cross_brand_divergence.yaml
```

- **Exit 0** — PASS (no alerts)  
- **Exit 2** — WARN (CBDI < warn_below)  
- **Exit 1** — FAIL (CBDI < fail_below)

**Config:** `config/cross_brand_divergence.yaml` — `thresholds.warn_below` (default 0.18), `thresholds.fail_below` (default 0.12), `minimum_books_per_brand`, `weights`, `recommendations` (BRAND_CONVERGENCE_LOW, BRAND_CONVERGENCE_CRITICAL). Recommendations are deterministic; no content changes — adjust scheduling only.

## Brand Identity Stability Index (Phase 11 — BISI)

Tracks **structural drift of a single brand over time**. Compares current window (last 90 days) vs previous window (90 days before that). Ensures brand personality and emotional signature stay within intended bounds.

**Metrics (per brand):** Same five dimensions as CBDI (arc, slot, band, engine, volatility). BISI_drift(B) = weighted JSD(P_current, P_previous). 0 = no change; \> 0.15 = noticeable shift; \> 0.25 = identity instability.

**Inputs:** Same as Phase 10 — `--history-index` and/or `--plans-dir`. A brand is evaluated only if it has ≥ `minimum_books_per_brand` in **both** windows.

**Outputs:** `artifacts/ops/brand_identity_stability_{report_date}.json` — `brands_evaluated`, `results` (brand_id, drift_score, components), `alerts` (BRAND_IDENTITY_DRIFT_HIGH / BRAND_IDENTITY_DRIFT_CRITICAL).

**CLI (from repo root):**

```bash
PYTHONPATH=. python3 phoenix_v4/ops/brand_identity_stability.py \
  --report-date 2026-03-04 \
  --window-days 90 \
  --history-index artifacts/catalog_similarity/index.jsonl \
  --plans-dir artifacts/plans \
  --out-dir artifacts/ops \
  --config config/brand_identity_stability.yaml
```

- **Exit 0** — PASS  
- **Exit 2** — WARN (drift \> warn_above)  
- **Exit 1** — FAIL (drift \> fail_above)

**Config:** `config/brand_identity_stability.yaml` — `thresholds.warn_above` (0.18), `thresholds.fail_above` (0.25), `minimum_books_per_brand`, `weights`, `recommendations`. CBDI protects brands from each other; BISI protects each brand from itself (temporal integrity).

## Unified Platform Health Scorecard (Phase 12 — UPHS)

**Read-only aggregation.** Does not recompute. Loads the four ops artifacts (Coverage Health v1.1, Catalog Emotional Distribution, Cross-Brand Divergence, Brand Identity Stability) and produces a single composite score 0–1 and tier.

**Scoring:** CHS (coverage: GREEN/BLOCKER/RED ratios + velocity), EDS (entropy + volatility + band_5_share), CBD_score (min pairwise divergence), BISI_score (min stability across brands). Composite = 0.35×CHS + 0.25×EDS + 0.20×CBD + 0.20×BISI. Penalties applied when alerts fire. Tiers: **STABLE** (≥0.85), **WATCH** (0.70–0.84), **RISK** (0.55–0.69), **CRITICAL** (&lt;0.55).

**Outputs:** `artifacts/ops/platform_health_scorecard_{report_date}.json` (components, composite_score, tier, sources_loaded, alerts_summary). Optional `--md` for a short .md summary.

**CLI (from repo root):**

```bash
PYTHONPATH=. python3 phoenix_v4/ops/platform_health_scorecard.py \
  --report-date 2026-03-04 \
  --ops-dir artifacts/ops \
  --config config/platform_health_scorecard.yaml
```

- **Exit 0** — STABLE or WATCH  
- **Exit 2** — RISK  
- **Exit 1** — CRITICAL  

**Config:** `config/platform_health_scorecard.yaml` — weights, velocity_delta_threshold, band_5_share_target, tiers, penalties. Run after the four upstream reports; single executive artifact for “Is the platform structurally healthy this week?”

## Deterministic Constraint Solver Wave Optimizer (Phase 13-C — DWO-CS)

**Fully deterministic** wave optimizer: satisfies hard constraints (weekly caps, cross-brand separation when CBDI convergent, brand-identity new-arc cap when BISI drift critical) and maximizes a deterministic objective. No randomness; no ML.

**Inputs:** Candidate items JSON (compiled plan candidates for the target wave), target wave size `N`, ops-dir (for CBDI/BISI alerts), config.

**Hard constraints:** Release-wave caps (max_same_topic, max_same_persona, topic_persona_pair, arc, engine, band_sig, slot_sig, variation, wave_fingerprint, teacher_mode, teacher_id); eligibility (exclude BLOCKER/RED); cross-brand no arc overlap when CBDI convergent; cap on "new" arc_id per brand when BISI drift critical.

**Outputs:**

- **Solved:** `artifacts/ops/wave_optimizer/wave_optimizer_solution_{wave_id}.json` and `.md`
- **Infeasible:** `artifacts/ops/wave_optimizer/wave_optimizer_infeasible_{wave_id}.json` (blocking reasons, recommended ops actions)

**Exit codes:** `0` SOLVED, `1` INFEASIBLE, `2` SOLVED_WITH_WARN (if warn-level constraints allowed).

**CLI (from repo root):**

```bash
PYTHONPATH=. python3 phoenix_v4/ops/wave_optimizer_constraint_solver.py   --wave-id 2026-W10   --target-size 90   --candidates-json artifacts/ops/wave_candidates_2026-W10.json   --ops-dir artifacts/ops   --config config/wave_optimizer_constraint_solver.yaml   --out-dir artifacts/ops/wave_optimizer
```

**Config:** `config/wave_optimizer_constraint_solver.yaml` — eligibility (exclude_risks, allow_yellow), hard_constraints.weekly_caps (Phase 6 parity), cross_brand (enforce_no_arc_overlap_when_convergent), brand_identity (max_new_arcs_per_brand_when_critical), objective weights and volatility_bins, determinism.tie_breaker.

**Pipeline order (wave build):**

1. Generate candidate set (e.g. wave candidates JSON).
2. Run **wave_optimizer_constraint_solver.py** (Phase 13-C).
3. Run **check_release_wave.py** (Phase 6) as final verification.
4. Export wave.

Phase 6 remains the final gate to prevent drift; constraints in 13-C mirror it for selection.

**Schemas & blocking codes:** Wave and solution/infeasible contracts: `schemas/wave_candidates.schema.json`, `schemas/wave_optimizer_solution.schema.json`, `schemas/wave_optimizer_infeasible.schema.json`. Canonical blocking reason codes and Slack/Jira routing: `config/wave_optimizer_blocking_codes.yaml`. See [docs/PHASE_13_C_WAVE_OPTIMIZER.md](../../docs/PHASE_13_C_WAVE_OPTIMIZER.md) §12.

## Ops schema registry and CI validation

All ops JSON artifacts are contract-bound to a JSON Schema. **Registry:** `config/ops_schema_registry.yaml` — artifact type, schema_path, artifact_pattern, current_version. **CI scripts (run from repo root):**

- `python scripts/ci/validate_ops_artifacts.py` — Validates every ops JSON (under `artifacts/ops`) that matches a registry pattern against its schema. Requires `jsonschema` (see `requirements.txt`). Exit 1 on any validation failure.
- `python scripts/ci/validate_ops_registry_consistency.py` — Ensures schema files exist for each registry entry and that matched artifacts have a schema. Exit 1 on mismatch.

Schema changes require a version bump, registry update, and entry in [docs/SCHEMA_CHANGELOG.md](../../docs/SCHEMA_CHANGELOG.md).

## Memorable Line Registry (cross-catalog duplication guard)

Tracks extracted “strong” memorable lines (good/great) across the catalog to avoid duplication risk from quality optimization.

**Canonical:** `artifacts/ops/memorable_line_registry_v1.jsonl` (append-only events).  
**Snapshot:** `artifacts/ops/memorable_line_registry_snapshot_v1.json` (compacted state).  
**Config:** `config/quality/memorable_line_registry_policy.yaml` — `max_occurrences_global`, `max_occurrences_per_brand`, `max_occurrences_per_wave`, `strength_levels_tracked`, `block_on_violation`.

**Pipeline hooks:**

1. **After** `quality_bundle_builder.py` writes a bundle:
   ```bash
   PYTHONPATH=. python3 -m phoenix_v4.ops.update_memorable_line_registry --bundle artifacts/ops/book_quality_bundle_<book_id>_<date>.json
   ```
2. **Before** export (e.g. Gate #49 / pre_export_check):
   ```bash
   PYTHONPATH=. python3 -m phoenix_v4.ops.check_memorable_line_registry --wave artifacts/ops/wave_optimizer/wave_optimizer_solution_<wave_id>.json
   ```

**Exit:** `update_*` → 0; `check_*` → 0 pass, 1 fail (blocking), 2 warn.  
**Violation report:** `artifacts/ops/memorable_line_registry_violations_<YYYYMMDD>.json`.  
**Schemas:** `schemas/memorable_line_registry_snapshot_v1.schema.json`, `schemas/memorable_line_registry_violations_v1.schema.json`.

## Catalog Health Dashboard

Operator-facing summary from validated ops artifacts: quality (CSI, pass/warn/fail, ending strength), duplication risk (collision counts), coverage, release readiness.

**Builder:** `phoenix_v4/ops/catalog_health_dashboard_builder.py`  
**Outputs:** `artifacts/ops/catalog_health_summary_<YYYYMMDD>.json` (and optional `--md`).  
**Schema:** `schemas/catalog_health_summary_v1.schema.json`.

```bash
PYTHONPATH=. python3 -m phoenix_v4.ops.catalog_health_dashboard_builder --ops-dir artifacts/ops --waves-dir artifacts/waves --md
```

## Quality bundle postprocessor (duplication-safe CSI)

Adds `duplication_safety` (0–100) to an existing `book_quality_bundle` using the registry snapshot; recomputes CSI with weight 0.10 for duplication_safety. Run after registry update when snapshot exists.

```bash
PYTHONPATH=. python3 -m phoenix_v4.ops.quality_bundle_postprocessor --bundle artifacts/ops/book_quality_bundle_<book_id>_<date>.json [--registry-snapshot path] [--out path]
```

---

## Creative Quality Gate v1 (post-compile)

Read-only gate on **compiled book** prose (after Stage 3 compile; before release-wave). Increases probability of emotional impact via deterministic heuristics only (no LLM).

**Module:** `phoenix_v4/gates/check_creative_quality_v1.py`  
**Config:** `config/creative_quality_v1.yaml`  
**Output:** `artifacts/ops/book_quality_summary_{book_id}_{date}.json` (optional `--md` for .md summary)  
**Exit:** 0 PASS, 2 WARN, 1 FAIL  

**Signals:** Arc emotional motion (distinct bands, rise/fall, flat warn), transformation density (insight/reframe/identity markers), specificity (concrete vs abstract), ending strength (compression, identity, action in last N chapters), lexical rhythm (sentence-length variance). Schema: `schemas/book_quality_summary_v1.schema.json`. See [docs/CREATIVE_QUALITY_GATE_V1.md](../../docs/CREATIVE_QUALITY_GATE_V1.md).
