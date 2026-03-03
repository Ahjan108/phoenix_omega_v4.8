# Pearl News Hardening Slice — 100% Checklist

**Slice:** URL normalization, one-command runner, CI preflight.  
**Branch:** `codex/harden-pearl-news-pipeline`  
**Files:** `wordpress_client.py`, `test_wordpress_and_article.py`, `pearl_news_do_it.sh`, `pearl_news_scheduled.yml`, `pearl_news/README.md`

**Rule:** If any must-have item is pending, it is not 100%.

---

## Must-Have (5 items)

| # | Item | How to verify |
|---|------|---------------|
| 1 | **Clean branch diff** — Only these 5 files in the PR: | |
| | `pearl_news/publish/wordpress_client.py` | `git diff main --name-only` |
| | `test_pearl_news/test_wordpress_and_article.py` | |
| | `scripts/pearl_news_do_it.sh` | |
| | `.github/workflows/pearl_news_scheduled.yml` | |
| | `pearl_news/README.md` | |
| 2 | **PR merged to `main`** | Merge `codex/harden-pearl-news-pipeline` |
| 3 | **GitHub Actions green** | `pearl_news_scheduled` workflow passes on `main` |
| 4 | **Runtime smoke checks** | |
| | `scripts/pearl_news_do_it.sh` (no-post) succeeds | Run locally |
| | `scripts/pearl_news_do_it.sh --post` (draft-post) succeeds | Run locally with WP secrets |
| 5 | **Secrets verified** | Settings → Secrets and variables → Actions |
| | `WORDPRESS_SITE_URL` | |
| | `WORDPRESS_USERNAME` | |
| | `WORDPRESS_APP_PASSWORD` | |

---

## Optional Ops Add-Ons

These are not required for 100% but are recommended for operations.

### 1. Rollback note

**Purpose:** Quick recovery if something goes wrong.

**Steps:**

1. **Disable scheduler**  
   - GitHub: **Actions → Pearl News scheduled → ⋮ → Disable workflow**  
   - Or edit `.github/workflows/pearl_news_scheduled.yml` and remove/comment the `schedule:` block.

2. **Revoke WP app password**  
   - WP Admin → **Users → Profile**  
   - **Application Passwords** → Revoke the password used for Pearl News.

3. **Dry-run mode**  
   - Remove or empty `WORDPRESS_APP_PASSWORD` in repo secrets.  
   - Workflow will run in dry-run only (no posts).

**Store this note** in a runbook or ops doc so anyone can execute it.

---

### 2. Evidence bundle

**Purpose:** Audit trail for go-live and troubleshooting.

**What to archive:**

| Item | Where to get it |
|------|-----------------|
| Workflow run URL | Actions → Pearl News scheduled → [run] → copy URL |
| Smoke command outputs | `scripts/pearl_news_do_it.sh` and `scripts/pearl_news_do_it.sh --post` stdout |
| Commit SHA | `git rev-parse HEAD` after merge |

**Template:**

```
Pearl News Hardening — Evidence Bundle
=====================================
Date: _______________
Commit SHA: _______________

Workflow run:
- pearl_news_scheduled: _______________ (URL)

Smoke outputs:
- pearl_news_do_it.sh (no-post): _______________ (or paste/link)
- pearl_news_do_it.sh --post: _______________ (or paste/link)

Secrets verified: [ ] WORDPRESS_SITE_URL [ ] WORDPRESS_USERNAME [ ] WORDPRESS_APP_PASSWORD
```

---

## Quick reference

**Local run (no post):**
```bash
scripts/pearl_news_do_it.sh
```

**Local run + post draft:**
```bash
scripts/pearl_news_do_it.sh --post
```

**Rollback (if needed):**
1. Disable workflow scheduler.
2. Revoke WP app password.
3. Set `WORDPRESS_APP_PASSWORD` empty for dry-run mode.

---

## Related docs

- [PEARL_NEWS_GITHUB_SCHEDULING.md](PEARL_NEWS_GITHUB_SCHEDULING.md) — Scheduling, secrets, Qwen move
- [pearl_news/README.md](../pearl_news/README.md) — Quick start, one-command usage
- [pearl_news/publish/README.md](../pearl_news/publish/README.md) — WordPress credentials, article format
