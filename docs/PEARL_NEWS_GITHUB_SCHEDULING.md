# Pearl News — GitHub scheduling (run when laptop is off)

**Purpose:** Run the Pearl News pipeline (RSS ingest, minimal drafts, optional WordPress post) on a schedule using GitHub Actions, so articles can be produced even when your laptop is off.

**Workflow:** [.github/workflows/pearl_news_scheduled.yml](../.github/workflows/pearl_news_scheduled.yml)

---

## 1. What runs on schedule

- **Trigger:** Twice daily at 6:00 and 18:00 UTC (and on manual `workflow_dispatch`).
- **Steps:**
  1. Checkout repo, setup Python 3.11, install `feedparser`, `pyyaml`, `requests`.
  2. Run `pearl_news.pipeline.run_article_pipeline`: fetches RSS, classifies topics/SDGs, selects templates, assembles articles, runs quality gates and QC, writes `article_*.json` with `featured_image` when available.
  3. Upload `artifacts/pearl_news/drafts/` as a workflow artifact (retention 7 days).
  4. **WordPress step:** Post the first `article_*.json` as a **draft** if repository secrets are set; otherwise run a **dry-run** (validates env and payload only).

---

## 2. Enabling WordPress posting from GitHub

To have the workflow actually post drafts to your site (e.g. pearlnewsuna.org):

1. In the repo: **Settings → Secrets and variables → Actions**.
2. Add repository secrets (do **not** commit these):
   - `WORDPRESS_SITE_URL` — e.g. `https://pearlnewsuna.org` (no trailing slash).
   - `WORDPRESS_USERNAME` — WordPress username (Application Password holder).
   - `WORDPRESS_APP_PASSWORD` — Application password from **WP Admin → Users → Your Profile → Application Passwords**.

With these set, the “Test WordPress integration” step will post the first minimal draft as a **draft** post (you can review and publish from WP Admin).

---

## 3. Running the pipeline in other repos (Qwen / Qwen-Agent)

You can run the same pipeline from your forks [Ahjan108/Qwen](https://github.com/Ahjan108/Qwen) or [Ahjan108/Qwen-Agent](https://github.com/Ahjan108/Qwen-Agent) so that scheduling lives there.

**Option A — Keep code in phoenix_omega:**  
The scheduled workflow runs here. No move required.

**Option B — Move pipeline to Qwen or Qwen-Agent (step-by-step):**

**Full runbook:** [PEARL_NEWS_OPTION_B_RUNBOOK.md](./PEARL_NEWS_OPTION_B_RUNBOOK.md) — exact `cp` commands, self-hosted workflow for LM Studio, secrets, and verify steps.

1. **Clone the target repo** (e.g. Ahjan108/Qwen or Ahjan108/Qwen-Agent).

2. **Copy these from phoenix_omega:**
   - `pearl_news/` (entire folder: pipeline, publish, config, article_templates, atoms, governance, prompts, del_intake_pics)
   - `scripts/pearl_news_post_to_wp.py`
   - `tests/test_pearl_news_quality_gates_minimal.py`, `tests/test_pearl_news_pipeline_e2e.py`
   - `.github/workflows/pearl_news_scheduled.yml` — or use **`.github/workflows/pearl_news_scheduled_self_hosted.yml`** (copy as `pearl_news_scheduled.yml`) when running with LM Studio on a self-hosted runner.

3. **Create `.github/workflows/`** in the target repo if it doesn't exist. Add the workflow file.

4. **Adjust workflow paths** if the target repo structure differs:
   - `pearl_news/config/feeds.yaml` — should exist at repo root
   - `scripts/pearl_news_post_to_wp.py` — or move to `pearl_news/scripts/` and update the workflow `run` command

5. **Add repository secrets** in the target repo: Settings → Secrets and variables → Actions:
   - `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`
   - For LLM expansion on self-hosted runner: `QWEN_BASE_URL`, `QWEN_API_KEY`, `QWEN_MODEL` (e.g. LM Studio at `http://localhost:1234/v1`).

6. **Self-hosted runner:** If using LM Studio (localhost), the workflow must use `runs-on: self-hosted`; add a self-hosted runner on the machine where LM Studio runs. See [PEARL_NEWS_OPTION_B_RUNBOOK.md](./PEARL_NEWS_OPTION_B_RUNBOOK.md).

7. **Push to main.** The workflow will run on schedule (6:00 and 18:00 UTC) and on `workflow_dispatch`.

7. **Optional:** Add `pearl_news` to `.gitignore` in phoenix_omega if you no longer want it there, or keep both in sync.

---

## 4. Images and attribution

- Feed ingest extracts images from RSS (e.g. `media:content`, `media:thumbnail`, `enclosure`, first `<img>` in summary) and stores **attribution** (credit, source_url) per image.
- Minimal drafts include `featured_image: { url, credit, source_url }` when the feed item has at least one image.
- The WordPress post script uploads the image to the Media Library and sets it as the post **featured image**, with caption/credit for proper attribution.

---

## 5. Index

- **Architecture:** [PEARL_NEWS_ARCHITECTURE_SPEC.md](PEARL_NEWS_ARCHITECTURE_SPEC.md)
- **Publish (credentials, article JSON):** [pearl_news/publish/README.md](../pearl_news/publish/README.md)
- **Hardening 100% checklist (incl. optional ops):** [PEARL_NEWS_HARDENING_100_PERCENT.md](PEARL_NEWS_HARDENING_100_PERCENT.md)
- **Qwen forks and backup:** [QWEN_FORKS_AND_BACKUP.md](QWEN_FORKS_AND_BACKUP.md)
