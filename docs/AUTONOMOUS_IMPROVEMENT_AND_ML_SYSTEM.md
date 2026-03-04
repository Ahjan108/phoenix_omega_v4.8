# Autonomous Improvement & ML System — Document All

**Purpose:** Single inventory of every doc, config, script, workflow, and artifact for the autonomous improvement loop (24/7 + daily + weekly), observability, operations board, agent PRs, auto-merge, weekly pipeline, KPI triggers, ML editorial, and ML autonomous loop.  
**Use:** Navigate from here or from [DOCS_INDEX.md](DOCS_INDEX.md) § [Autonomous improvement & ML system (document all)](#).  
**Last updated:** 2026-03-04

---

## 1. Docs & specs

| Doc | Purpose |
|-----|---------|
| [PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md](PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md) | Observe, document, elevate/auto-fix, learn; signal registry, collector, evidence_log, elevated_failures, KPI evaluator, operations board |
| [AUTO_MERGE_POLICY.md](AUTO_MERGE_POLICY.md) | Low-risk agent PR auto-merge: scope, allowed paths, label `bot-fix`, required checks |
| [ML_EDITORIAL_MARKET_LOOP_SPEC.md](ML_EDITORIAL_MARKET_LOOP_SPEC.md) | Section quality, variant ranking, reader-fit, rewrite recs, market router; data contracts; marketing 02/03/04 integration |
| [ML_EDITORIAL_SAFETY_AND_GOVERNANCE.md](ML_EDITORIAL_SAFETY_AND_GOVERNANCE.md) | ML editorial kill switch, allowlist, audit log, rollback, calibration gate |
| [ML_AUTONOMOUS_LOOP_SPEC.md](ML_AUTONOMOUS_LOOP_SPEC.md) | 24/7 continuous loop, daily promotion, weekly market recalibration; agent roles; data contracts; safety; UI contract; optional proof (§15) |
| [BRANCH_PROTECTION_REQUIREMENTS.md](BRANCH_PROTECTION_REQUIREMENTS.md) | Required checks; auto-merge (optional) subsection |
| [GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md](GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md) | Detect, owner, rollback, communication, postmortem |

---

## 2. Config

| Config | Purpose |
|--------|---------|
| [config/observability_production_signals.yaml](../config/observability_production_signals.yaml) | Signal registry for collect_signals (gate_production_readiness, systems_test, atoms_coverage, etc.) |
| [config/observability_kpi_targets.yaml](../config/observability_kpi_targets.yaml) | KPI targets and trigger_job (e.g. systems_test_pass_rate → weekly_pipeline) |
| [config/governance/required_checks.yaml](../config/governance/required_checks.yaml) | Required status checks for branch protection (used by verify_github_governance) |
| [config/ml_editorial/ml_editorial_config.yaml](../config/ml_editorial/ml_editorial_config.yaml) | ML editorial paths, thresholds, allowlist, marketing_sources, audit_log_path |
| [config/ml_editorial/kpi_targets.yaml](../config/ml_editorial/kpi_targets.yaml) | ML editorial KPI targets and calibration max drift |
| [config/ml_loop/promotion_policy.yaml](../config/ml_loop/promotion_policy.yaml) | autonomy_enabled, allowlist_paths, confidence floors, queue paths, fast/slow gates, agent_open_fix_pr_script |
| [config/ml_loop/kpi_targets.yaml](../config/ml_loop/kpi_targets.yaml) | Autonomous loop KPIs (weak_section_rate, variant_win_rate, etc.); weekly_report_path, baseline_path |
| [config/ml_loop/drift_thresholds.yaml](../config/ml_loop/drift_thresholds.yaml) | max_drift per dimension; calibration_block_rollout; baseline_source |

---

## 3. Scripts — Observability & operations board

| Script | Purpose |
|--------|---------|
| [scripts/observability/collect_signals.py](../scripts/observability/collect_signals.py) | Collect production signals; write snapshot, evidence_log, elevated_failures; call write_operations_board |
| [scripts/observability/write_operations_board.py](../scripts/observability/write_operations_board.py) | Build operations_board.jsonl from evidence_log + elevated_failures |
| [scripts/observability/evaluate_kpi_targets.py](../scripts/observability/evaluate_kpi_targets.py) | Evaluate snapshot vs config/observability_kpi_targets.yaml; write kpi_trigger.json; emit triggered jobs |
| [scripts/observability/agent_open_fix_pr.py](../scripts/observability/agent_open_fix_pr.py) | Read elevated_failures; apply safe dependency fix; branch, push, gh pr create; append to operations board |
| [scripts/ci/verify_github_governance.py](../scripts/ci/verify_github_governance.py) | Verify ruleset, required checks, no token files (--mode local | api) |

---

## 4. Scripts — Weekly pipeline & release

| Script | Purpose |
|--------|---------|
| [scripts/release/weekly_pipeline_with_marketing.py](../scripts/release/weekly_pipeline_with_marketing.py) | Optional marketing signal; run canary + systems test; write weekly_pipeline_result_{date}.json + operations board row |
| [scripts/release/run_weekly_ml_editorial.py](../scripts/release/run_weekly_ml_editorial.py) | N/A (weekly ML editorial is under scripts/ml_editorial/) |
| [scripts/ml_editorial/run_weekly_ml_editorial.py](../scripts/ml_editorial/run_weekly_ml_editorial.py) | Run section scoring → variant ranking → reader fit → rewrite recs → market router; audit log |

---

## 5. Scripts — ML editorial

| Script | Purpose |
|--------|---------|
| [scripts/ml_editorial/run_section_scoring.py](../scripts/ml_editorial/run_section_scoring.py) | Section quality (clarity, pacing, arc_drift); write section_scores.jsonl |
| [scripts/ml_editorial/run_variant_ranking.py](../scripts/ml_editorial/run_variant_ranking.py) | Variant ranking (title/subtitle/opening); optional marketing lexicons; write variant_rankings.jsonl |
| [scripts/ml_editorial/run_reader_fit.py](../scripts/ml_editorial/run_reader_fit.py) | Reader-fit scores; write reader_fit_scores.jsonl |
| [scripts/ml_editorial/run_rewrite_recs.py](../scripts/ml_editorial/run_rewrite_recs.py) | Rewrite recommendations from section_scores weak_flags; write rewrite_recs.jsonl |
| [scripts/ml_editorial/run_market_router.py](../scripts/ml_editorial/run_market_router.py) | Market actions from section/reader_fit/variant; write market_actions.jsonl |
| [scripts/ml_editorial/run_weekly_ml_editorial.py](../scripts/ml_editorial/run_weekly_ml_editorial.py) | Orchestrate all five above; audit log |
| [scripts/dashboard/ml_editorial_tab.py](../scripts/dashboard/ml_editorial_tab.py) | get_ml_editorial_summary(); render_ml_editorial_tab() for Streamlit |

---

## 6. Scripts — ML autonomous loop (24/7 + daily + weekly)

| Script | Purpose |
|--------|---------|
| [scripts/ml_loop/run_continuous_loop.py](../scripts/ml_loop/run_continuous_loop.py) | Hourly: section scoring, fast gates; queue pass candidates; failures → operations board |
| [scripts/ml_loop/run_daily_promotion.py](../scripts/ml_loop/run_daily_promotion.py) | Read promotion queue; apply confidence/drift; call agent_open_fix_pr; log to operations board |
| [scripts/ml_loop/run_weekly_market_recalibration.py](../scripts/ml_loop/run_weekly_market_recalibration.py) | Run ML editorial weekly; write weekly_report.json, baseline.json |
| [scripts/ml_loop/agent_open_fix_pr.py](../scripts/ml_loop/agent_open_fix_pr.py) | Delegate to scripts/observability/agent_open_fix_pr.py |
| [scripts/ml_loop/verify_workflows_and_artifacts.sh](../scripts/ml_loop/verify_workflows_and_artifacts.sh) | Run all three loop scripts; verify artifacts; optional --trigger for gh workflow run |

---

## 7. Schemas

| Schema | Purpose |
|--------|---------|
| [schemas/operations_board.schema.json](../schemas/operations_board.schema.json) | Row: timestamp, signal_id, status, suggested_fix, pr_url, merged, impact; ts, book_id, source, decision, confidence, evidence_path |
| [schemas/ml_editorial/section_scores_v1.schema.json](../schemas/ml_editorial/section_scores_v1.schema.json) | section_scores.jsonl row |
| [schemas/ml_editorial/variant_rankings_v1.schema.json](../schemas/ml_editorial/variant_rankings_v1.schema.json) | variant_rankings.jsonl row |
| [schemas/ml_editorial/reader_fit_scores_v1.schema.json](../schemas/ml_editorial/reader_fit_scores_v1.schema.json) | reader_fit_scores.jsonl row |
| [schemas/ml_editorial/rewrite_recs_v1.schema.json](../schemas/ml_editorial/rewrite_recs_v1.schema.json) | rewrite_recs.jsonl row |
| [schemas/ml_editorial/market_actions_v1.schema.json](../schemas/ml_editorial/market_actions_v1.schema.json) | market_actions.jsonl row |

---

## 8. Artifacts

| Artifact | Purpose |
|----------|---------|
| artifacts/observability/signal_snapshot*.json | Latest signal run results |
| artifacts/observability/evidence_log.jsonl | Success rows per signal |
| artifacts/observability/elevated_failures.jsonl | Failure rows (for agent_open_fix_pr) |
| artifacts/observability/operations_board.jsonl | Issue → fix → PR → merged → impact |
| artifacts/observability/kpi_trigger.json | KPI evaluator output; triggers list |
| artifacts/ml_editorial/section_scores.jsonl | Section quality per book/chapter |
| artifacts/ml_editorial/variant_rankings.jsonl | Variant rankings |
| artifacts/ml_editorial/reader_fit_scores.jsonl | Reader-fit scores |
| artifacts/ml_editorial/rewrite_recs.jsonl | Rewrite recommendations |
| artifacts/ml_editorial/market_actions.jsonl | Market positioning actions |
| artifacts/ml_editorial/audit_log.jsonl | ML editorial audit trail |
| artifacts/ml_loop/continuous_candidates.jsonl | Pass candidates from continuous loop |
| artifacts/ml_loop/promotion_queue.jsonl | Daily promotion queue |
| artifacts/ml_loop/weekly_report.json | Weekly recalibration report |
| artifacts/ml_loop/baseline.json | Baseline for drift/KPI |
| artifacts/ei_v2/marketing_integration.log | EI V2 marketing lexicon events |

---

## 9. GitHub workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| [.github/workflows/production-observability.yml](../.github/workflows/production-observability.yml) | schedule 0 7 * * *; workflow_dispatch | Collect signals; write operations board; evaluate KPI targets; run KPI-triggered jobs (e.g. weekly_pipeline); agent-fix-pr job (download artifact, run agent_open_fix_pr) |
| [.github/workflows/github-governance-check.yml](../.github/workflows/github-governance-check.yml) | pull_request | Verify governance (required checks, ruleset, no token files) |
| [.github/workflows/core-tests.yml](../.github/workflows/core-tests.yml) | push/PR to main | Pytest + production readiness gates + marketing config validate |
| [.github/workflows/auto-merge-bot-fix.yml](../.github/workflows/auto-merge-bot-fix.yml) | pull_request (labeled bot-fix) | Enable squash auto-merge when merge state CLEAN |
| [.github/workflows/weekly-pipeline.yml](../.github/workflows/weekly-pipeline.yml) | schedule 0 8 * * 1; workflow_dispatch | Run weekly_pipeline_with_marketing; upload result |
| [.github/workflows/ml-editorial-weekly.yml](../.github/workflows/ml-editorial-weekly.yml) | schedule 0 9 * * 1; workflow_dispatch | Run run_weekly_ml_editorial; upload ml_editorial artifacts |
| [.github/workflows/ml-loop-continuous.yml](../.github/workflows/ml-loop-continuous.yml) | schedule 0 * * * *; workflow_dispatch | Run run_continuous_loop; upload ml_loop + operations_board |
| [.github/workflows/ml-loop-daily-promotion.yml](../.github/workflows/ml-loop-daily-promotion.yml) | schedule 0 8 * * *; workflow_dispatch | Download ml-loop-continuous artifact; run run_daily_promotion |
| [.github/workflows/ml-loop-weekly-recalibration.yml](../.github/workflows/ml-loop-weekly-recalibration.yml) | schedule 0 10 * * 1; workflow_dispatch | Run run_weekly_market_recalibration; upload weekly_report.json |

---

## 10. Data flow (summary)

- **Continuous (hourly):** collect_signals / section scoring → fast gates → pass candidates → promotion_queue; failures → operations_board.
- **Daily:** promotion_queue → confidence/drift check → agent_open_fix_pr (if enabled) → operations_board.
- **Weekly:** ML editorial full run → weekly_report + baseline; weekly_pipeline_with_marketing; observability collects signals and evaluates KPIs (can trigger weekly_pipeline).
- **Operations board:** Written by collect_signals (via write_operations_board), run_continuous_loop (failures), run_daily_promotion (pr_opened/fail), agent_open_fix_pr (pr_url), weekly_pipeline (impact_recorded).

---

## 11. How to run (local proof)

```bash
# Observability + operations board + KPI evaluation
PYTHONPATH=. python scripts/observability/collect_signals.py --signals gate_production_readiness atoms_coverage
PYTHONPATH=. python scripts/observability/write_operations_board.py
PYTHONPATH=. python scripts/observability/evaluate_kpi_targets.py --snapshot artifacts/observability/signal_snapshot.json

# ML editorial (weekly)
PYTHONPATH=. python scripts/ml_editorial/run_weekly_ml_editorial.py

# Autonomous loop (all three)
PYTHONPATH=. python scripts/ml_loop/run_continuous_loop.py
PYTHONPATH=. python scripts/ml_loop/run_daily_promotion.py --dry-run
PYTHONPATH=. python scripts/ml_loop/run_weekly_market_recalibration.py

# Single verification script
bash scripts/ml_loop/verify_workflows_and_artifacts.sh
# With workflow trigger (requires gh): bash scripts/ml_loop/verify_workflows_and_artifacts.sh --trigger
```
