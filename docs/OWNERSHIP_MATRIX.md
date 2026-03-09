# Ownership matrix (runtime consolidation)

**Purpose:** One place to see which repo owns which paths and capabilities. Prevents drift and duplicate ownership.

**Rules:** (1) Migrate from Qwen-Agent `origin/main` only. (2) Copy via strict path allowlist. (3) Cutover in two PRs: phoenix_omega consolidation, then Qwen-Agent disable cron.

---

## Single production repo

phoenix_omega is the **only** production repo. Qwen-Agent is **dispatch-only** (no production traffic, no production writes).

| Repo | Role | Production schedules? |
|------|------|------------------------|
| **phoenix_omega (Ahjan108/phoenix_omega_v4.8)** | Single production repo for v4, video, pearl_prime, EI v2, ML, localization, pearl_news (assembly mode) | Yes |
| **Qwen-Agent (Ahjan108/Qwen-Agent)** | Backup / experiment only; manual dispatch only after PR B | No (cron disabled in PR B) |

---

## Path ownership (phoenix_omega)

| Path / domain | Owner | Workflows / notes |
|---------------|--------|-------------------|
| `.github/workflows/core-tests.yml`, `release-gates.yml`, `ei-v2-gates.yml`, `change-impact.yml`, etc. | phoenix_omega | Core tests, Release, EI V2, Change impact, Teacher, Brand, governance, docs-ci, simulation, marketing-config-gate, production-observability, production-alerts, auto-merge-bot-fix, weekly-pipeline, ml-*, locale-gate, translate-atoms-qwen-matrix, research_feeds_ingest, pages |
| `.github/workflows/audiobook_*.yml`, `locale_max_agents.yml`, `pearl_news_*.yml`, `runner_artifacts_cleanup.yml` | phoenix_omega | Migrated from Qwen-Agent; run in this repo |
| `.github/workflows/catalog-book-pipeline.yml`, `marketing-briefs-and-proposals.yml` | phoenix_omega | Use `scripts/lm_studio_lock.py` (canonical) |
| `scripts/lm_studio_lock.py` | phoenix_omega | Canonical LM Studio job lock; workflows and queue worker load this first |
| `scripts/localization/` | phoenix_omega | run_locale_batches, translate_atoms_all_locales, validate_translations |
| `scripts/pearl_news_article_judge.py` | phoenix_omega | Pearl News article quality judge |
| `scripts/runner/` | phoenix_omega | runner_cleanup.sh, heavy_window_guard.py, runner_watchdog.sh, install_watchdog_launchd.sh |
| `config/content_type_registry.yaml`, `config/runner/heavy_windows.yaml` | phoenix_omega | Judge and runner window config |
| `pearl_news/`, `prompts/article_judge/` | phoenix_omega | Pearl News assembly mode assets and judge prompt |
| Video, v4, pearl_prime, EI v2, marketing, queue_orchestrator | phoenix_omega | All in this repo |

---

## Qwen-Agent (backup only)

| Path / domain | Owner | Notes |
|---------------|--------|--------|
| Same workflow names as above | Qwen-Agent | After PR B: `schedule:` removed; `workflow_dispatch` only. Not used for production cron. |
| Scripts/config that were migrated | phoenix_omega | Canonical copy lives in phoenix_omega; Qwen-Agent may retain copy for backup/experiment only |

---

## Drift audit

The workflow `.github/workflows/drift-audit.yml` compares critical paths in phoenix_omega against the allowlist and fails if any required path is missing. See that file and [RUNTIME_CONSOLIDATION_MIGRATION_MANIFEST.md](./RUNTIME_CONSOLIDATION_MIGRATION_MANIFEST.md) for the allowlist.
