# Runtime consolidation migration manifest (allowlist)

**Guardrails (mandatory):**

1. **Never merge from destructive branches.** Only import from phoenix_omega `origin/main` (+ selected commits from `origin/codex/github-no-failure-enforcement-v3`) and Qwen-Agent `origin/main`. Do not use `codex/pearl-news-option-b` or `codex/pearl-news-pr`.
2. **Copy via allowlist, not broad sync.** Migrate only the paths listed below. No full-tree copy.
3. **Cutover in two PRs:** PR A (phoenix_omega) = consolidation + docs + drift-audit; PR B (Qwen-Agent) = disable cron, keep workflow_dispatch only.

---

## Allowlist: Qwen-Agent (origin/main) → phoenix_omega

### Workflows (copy to `.github/workflows/`)

| Source (Qwen-Agent) | Destination (phoenix_omega) | Notes |
|--------------------|-----------------------------|--------|
| `.github/workflows/audiobook_manual.yml` | `.github/workflows/audiobook_manual.yml` | Adapt script paths to repo root = phoenix_omega |
| `.github/workflows/audiobook_regression.yml` | `.github/workflows/audiobook_regression.yml` | Same |
| `.github/workflows/audiobook_scheduled.yml` | `.github/workflows/audiobook_scheduled.yml` | Same |
| `.github/workflows/locale_max_agents.yml` | `.github/workflows/locale_max_agents.yml` | Same |
| `.github/workflows/pearl_news_scheduled.yml` | `.github/workflows/pearl_news_scheduled.yml` | Same |
| `.github/workflows/pearl_news_manual_expand.yml` | `.github/workflows/pearl_news_manual_expand.yml` | Same |
| `.github/workflows/runner_artifacts_cleanup.yml` | `.github/workflows/runner_artifacts_cleanup.yml` | Same; script path `scripts/runner/runner_cleanup.sh` |

### Scripts

| Source (Qwen-Agent) | Destination (phoenix_omega) | Notes |
|--------------------|-----------------------------|--------|
| `scripts/lm_studio_lock.py` | `scripts/lm_studio_lock.py` | Canonical location; update all refs from `Qwen-Agent/scripts/lm_studio_lock.py` to `scripts/lm_studio_lock.py` |
| `scripts/localization/run_locale_batches.py` | `scripts/localization/run_locale_batches.py` | REPO_ROOT = phoenix_omega root |
| `scripts/localization/translate_atoms_all_locales.py` | `scripts/localization/translate_atoms_all_locales.py` | Same |
| `scripts/localization/validate_translations.py` | `scripts/localization/validate_translations.py` | Same |
| `scripts/pearl_news_article_judge.py` | `scripts/pearl_news_article_judge.py` | Expects `config/content_type_registry.yaml` |
| `scripts/runner/runner_cleanup.sh` | `scripts/runner/runner_cleanup.sh` | Set REPO_DIR default to phoenix_omega root when run from here |
| `scripts/runner/heavy_window_guard.py` | `scripts/runner/heavy_window_guard.py` | Optional runner tooling |
| `scripts/runner/runner_watchdog.sh` | `scripts/runner/runner_watchdog.sh` | Optional |
| `scripts/runner/install_watchdog_launchd.sh` | `scripts/runner/install_watchdog_launchd.sh` | Optional |

### Config

| Source (Qwen-Agent) | Destination (phoenix_omega) | Notes |
|--------------------|-----------------------------|--------|
| `config/runner/heavy_windows.yaml` | `config/runner/heavy_windows.yaml` | If present |
| `config/audiobook_script/comparator_config.yaml` | `config/audiobook_script/comparator_config.yaml` | Merge if phoenix_omega already has audiobook config |
| (create if missing) | `config/content_type_registry.yaml` | Required by pearl_news_article_judge; minimal `content_types: {}` for --dry-run |

### Docs

| Source (Qwen-Agent) | Destination (phoenix_omega) | Notes |
|--------------------|-----------------------------|--------|
| `docs/LOCALIZATION_100_PERCENT_RUNBOOK.md` | `docs/LOCALIZATION_100_PERCENT_RUNBOOK.md` | Link from DOCS_INDEX |
| `docs/LM_STUDIO_CONFIG.md` | `docs/LM_STUDIO_CONFIG.md` | Merge or copy if not duplicate |
| `docs/RUNNER_TRIAGE_ONE_PAGER.md` | `docs/RUNNER_TRIAGE_ONE_PAGER.md` | Optional |

### Pearl News assembly-mode assets

| Source (Qwen-Agent) | Destination (phoenix_omega) | Notes |
|--------------------|-----------------------------|--------|
| `pearl_news/pipeline/teacher_onboarding.py` | `pearl_news/pipeline/teacher_onboarding.py` | Only if not already in phoenix_omega |
| `prompts/article_judge/judge_pearl_news_v1.txt` | `prompts/article_judge/judge_pearl_news_v1.txt` | Required for pearl_news_article_judge --dry-run and LLM judge |

---

## Path wiring after copy

- All workflow `run:` steps that invoke scripts: use paths relative to phoenix_omega root (e.g. `scripts/localization/run_locale_batches.py`, `scripts/lm_studio_lock.py`). No `Qwen-Agent/` prefix.
- Existing phoenix_omega workflows that reference `Qwen-Agent/scripts/lm_studio_lock.py`: change to `scripts/lm_studio_lock.py` (and ensure they run with repo root = phoenix_omega).
- `scripts/runner/runner_cleanup.sh`: set `REPO_DIR="${REPO_DIR:-$GITHUB_WORKSPACE}"` or equivalent so cleanup runs against phoenix_omega.
- `scripts/queue_orchestrator/worker.py` and any other code that loads `Qwen-Agent/scripts/lm_studio_lock.py`: update to load `scripts/lm_studio_lock.py`.

---

## Out of scope (do not copy)

- Full Qwen-Agent tree.
- Any file not on this allowlist.
- Branches `codex/pearl-news-option-b`, `codex/pearl-news-pr`.
