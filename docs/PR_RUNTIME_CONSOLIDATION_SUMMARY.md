# PR: Runtime consolidation (Phase 1) — PR-ready summary

**Branch:** `codex/runtime-consolidation` (from `origin/main`)  
**Scope:** PR A — phoenix_omega consolidation + governance + drift-audit

---

## Execution rules applied

1. **Migrate from Qwen-Agent `origin/main` only** — no destructive branches (`codex/pearl-news-option-b`, `codex/pearl-news-pr`).
2. **Strict path allowlist** — only approved paths copied; no broad sync.
3. **Cutover in two PRs** — this is PR A; PR B (Qwen-Agent) will disable cron and keep `workflow_dispatch` only.

---

## Commits on `codex/runtime-consolidation`

1. **feat(runtime): consolidate Qwen runtime into phoenix_omega (allowlist only)**  
   - Workflows: audiobook_manual/regression/scheduled, locale_max_agents, pearl_news_scheduled/manual_expand, runner_artifacts_cleanup, catalog-book-pipeline, marketing-briefs-and-proposals  
   - Scripts: lm_studio_lock, localization (run_locale_batches, translate_atoms_all_locales, validate_translations), pearl_news_article_judge, runner (cleanup, watchdog, heavy_window_guard, install_watchdog_launchd)  
   - Config: content_type_registry.yaml, runner/heavy_windows.yaml  
   - Docs: RUNTIME_CONSOLIDATION_MIGRATION_MANIFEST, LOCALIZATION_100_PERCENT_RUNBOOK  
   - Prompts: article_judge/judge_pearl_news_v1.txt  
   - Path wiring: catalog-book-pipeline and marketing-briefs use `scripts/lm_studio_lock.py` first; queue worker prefers same.

2. **docs(governance): OWNERSHIP_MATRIX, registry, framework + drift-audit workflow**  
   - docs/OWNERSHIP_MATRIX.md — single production repo (phoenix_omega), Qwen-Agent backup only  
   - config/governance/github_repos_registry.yaml — migrated workflows listed; Qwen-Agent `production_schedules: false`  
   - docs/GITHUB_OPERATIONS_FRAMEWORK.md — single production repo wording, migrated workflow matrix, canonical ownership  
   - .github/workflows/drift-audit.yml — nightly + workflow_dispatch; validates allowlist paths  
   - scripts/ci/drift_audit.py — required paths check; writes artifacts/drift_report.json

---

## Smoke checks (run on this branch)

| Check | Result |
|-------|--------|
| `scripts.lm_studio_lock` import + lock acquire/release | OK |
| `scripts/pearl_news_article_judge.py --dry-run` | OK |
| Workflow YAML parse (drift-audit, pearl_news_scheduled, locale_max_agents) | OK |
| `scripts/ci/drift_audit.py` (all 22 required paths present) | OK |

---

## 4 hard actions before merging PR A

1. **Legacy broken workflow removed** — `.github/workflows/audiobook-regression.yml` (dash) deleted. Canonical is `audiobook_regression.yml` (underscore). No duplicate scheduled jobs; only underscore workflow files are active.
2. **Secrets in phoenix_omega** — Before enabling schedules, add in repo Settings → Secrets: `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`, `QWEN_BASE_URL`, `QWEN_API_KEY`, `QWEN_MODEL`.
3. **Branch protection** — Required checks on `main` must include consolidated gates (Core tests, Release gates, EI V2 gates, Change impact).
4. **PR B patch set** — Exact file-by-file schedule removals for Qwen-Agent are in [PR_B_QWEN_AGENT_DISABLE_CRON_PATCH.md](PR_B_QWEN_AGENT_DISABLE_CRON_PATCH.md). Apply in Qwen-Agent repo on branch `codex/disable-prod-schedules` after PR A is merged.

---

## Next steps

1. **Open PR** from `codex/runtime-consolidation` to `main` in phoenix_omega (Ahjan108/phoenix_omega_v4.8).  
2. **Before/after merge:** Add secrets (see above); ensure self-hosted runner is available for workflows that need it.  
3. **PR B (Qwen-Agent):** Follow [PR_B_QWEN_AGENT_DISABLE_CRON_PATCH.md](PR_B_QWEN_AGENT_DISABLE_CRON_PATCH.md) — remove `schedule:` from pearl_news_scheduled, audiobook_scheduled, runner_artifacts_cleanup only (locale_max_agents has no schedule). Merge so Qwen-Agent no longer runs production cron.

---

## Key docs

- [docs/RUNTIME_CONSOLIDATION_MIGRATION_MANIFEST.md](RUNTIME_CONSOLIDATION_MIGRATION_MANIFEST.md) — allowlist and guardrails  
- [docs/OWNERSHIP_MATRIX.md](OWNERSHIP_MATRIX.md) — path/capability ownership  
- [docs/GITHUB_OPERATIONS_FRAMEWORK.md](GITHUB_OPERATIONS_FRAMEWORK.md) — workflow matrix and canonical ownership  
- [docs/PR_B_QWEN_AGENT_DISABLE_CRON_PATCH.md](PR_B_QWEN_AGENT_DISABLE_CRON_PATCH.md) — exact PR B patch (remove schedule in Qwen-Agent)
