# Pearl News Option B — Run from Qwen or Qwen-Agent repo

**Purpose:** Copy Pearl News into Ahjan108/Qwen-Agent (or Ahjan108/Qwen) and run the scheduled pipeline there, with optional LLM expansion via LM Studio on a self-hosted runner.

**Authority:** [DOCS_INDEX.md](./DOCS_INDEX.md), [PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md).

---

## 1. Pick target repo

Use **one** of:

- **Ahjan108/Qwen-Agent** (recommended)
- **Ahjan108/Qwen**

Clone it locally if you haven’t:

```bash
git clone https://github.com/Ahjan108/Qwen-Agent.git
cd Qwen-Agent
# or: git clone https://github.com/Ahjan108/Qwen.git && cd Qwen
```

---

## 2. Copy Pearl News code into the target repo

From a directory that contains **both** `phoenix_omega` and the target repo (e.g. `Qwen-Agent`), run these from the **parent** of both (adjust `phoenix_omega` and `Qwen-Agent` if your names differ):

```bash
# Set paths (change Qwen-Agent to Qwen if using that repo)
PHOENIX="phoenix_omega"
TARGET="Qwen-Agent"

# pearl_news/ (entire folder)
cp -R "$PHOENIX/pearl_news" "$TARGET/"

# Scripts and tests
cp "$PHOENIX/scripts/pearl_news_post_to_wp.py" "$TARGET/scripts/"
cp "$PHOENIX/tests/test_pearl_news_quality_gates_minimal.py" "$TARGET/tests/"
cp "$PHOENIX/tests/test_pearl_news_pipeline_e2e.py" "$TARGET/tests/"

# Workflow: use self-hosted variant so the job can reach LM Studio on your machine
mkdir -p "$TARGET/.github/workflows"
cp "$PHOENIX/.github/workflows/pearl_news_scheduled_self_hosted.yml" "$TARGET/.github/workflows/pearl_news_scheduled.yml"
```

If the target repo has no `scripts/` or `tests/` yet, create them first:

```bash
mkdir -p "$TARGET/scripts" "$TARGET/tests"
# then run the cp commands above
```

The workflow you copied (`pearl_news_scheduled_self_hosted.yml` → `pearl_news_scheduled.yml`) uses `runs-on: self-hosted`, injects `QWEN_BASE_URL`, `QWEN_API_KEY`, `QWEN_MODEL` from secrets, installs `openai`, and runs the pipeline with `--expand`. If you prefer cloud runner only (no LLM expansion), copy `pearl_news_scheduled.yml` instead of the self-hosted variant.

---

## 3. Commit and push to target repo `main`

```bash
cd "$TARGET"
git add pearl_news/ scripts/pearl_news_post_to_wp.py tests/test_pearl_news_*.py .github/workflows/pearl_news_scheduled.yml
git status
git commit -m "Add Pearl News pipeline and scheduled workflow (Option B)"
git push origin main
```

---

## 4. Add GitHub secrets in the target repo

In the **target** repo (Qwen-Agent or Qwen):

1. Go to **Settings → Secrets and variables → Actions**.
2. Add **Repository secrets**:

| Secret | Example / notes |
|--------|------------------|
| `WORDPRESS_SITE_URL` | `https://pearlnewsuna.org` |
| `WORDPRESS_USERNAME` | WordPress username (e.g. `admin`) |
| `WORDPRESS_APP_PASSWORD` | Application password from WP Profile → Application Passwords |
| `QWEN_BASE_URL` | `http://localhost:1234/v1` (LM Studio) or your self-hosted Qwen API URL |
| `QWEN_API_KEY` | e.g. `lm-studio` or your API key |
| `QWEN_MODEL` | e.g. `Qwen2.5-14B-Instruct` (must match the model name in LM Studio) |

If you **don’t** set `QWEN_*`, the pipeline still runs but skips LLM expansion (no `--expand` effect). WordPress posting still works when the three `WORDPRESS_*` secrets are set.

---

## 5. Self-hosted runner (for LM Studio)

1. On the Mac (or machine) where LM Studio runs: **Settings → Actions → Runners → New self-hosted runner**, follow the instructions to add the runner to the **target** repo (or org).
2. Run the runner app so it’s online when the workflow triggers.
3. Ensure LM Studio is running and the model is loaded so `http://localhost:1234/v1` (or your `QWEN_BASE_URL`) is reachable when the job runs.

---

## 6. Trigger and verify

1. In the target repo: **Actions → “Pearl News scheduled” → Run workflow** (branch: `main`).
2. Wait for the run to finish.
3. Verify:
   - **Artifacts:** `pearl_news_drafts` is uploaded (contains `artifacts/pearl_news/drafts`).
   - **WordPress:** If secrets are set, a draft post is created (check WP Admin).
   - **Run:** Green check.

---

## 7. LM Studio reliability (self-hosted)

If the workflow runs but **LLM expansion times out**, use these practices.

**Already in this repo (copy to target):**

- **Job timeout:** `timeout-minutes: 30` so runs don’t hang indefinitely.
- **Safe-mode toggles:** `PEARL_NEWS_EXPAND` and `PEARL_NEWS_LIMIT` in the workflow `env`. Default: `PEARL_NEWS_EXPAND: "true"`, `PEARL_NEWS_LIMIT: "3"`.
- **Higher expansion timeout:** `pearl_news/config/llm_expansion.yaml` has `timeout: 240` (seconds per article).

**What you should do:**

1. **Let the current run finish** — Don’t cancel unless it exceeds the job timeout. Capture the run URL and step logs if it fails.
2. **Lower workload** — The workflow already uses `--limit 3`. For emergency stability, in the workflow set `PEARL_NEWS_EXPAND: "false"` (drafts only, no LLM expansion).
3. **LM Studio load** — Use 1–2 parallel slots; keep one model loaded (e.g. `qwen3-14b`). Avoid other heavy local jobs during workflow runs.
4. **Staged rollout:**
   - Run with `PEARL_NEWS_LIMIT: "1"` and `PEARL_NEWS_EXPAND: "true"` (smoke test).
   - Then `limit=3`, `expand=true`.
   - If stable, keep the schedule; if not, set `PEARL_NEWS_EXPAND: "false"` for scheduled runs and run expansion manually or less often.
5. **Acceptance:** Workflow green 3 runs in a row; `pearl_news_drafts` artifact each run; expansion timeouts rare or zero in safe mode; WP step succeeds or dry-runs cleanly.

**Optional:** To flip expand without editing YAML, use repo variables: e.g. `PEARL_NEWS_EXPAND: ${{ vars.PEARL_NEWS_EXPAND || 'true' }}` and set the variable in Settings → Variables.

---

## Quick reference

| Step | Action |
|------|--------|
| 1 | Choose Ahjan108/Qwen-Agent or Ahjan108/Qwen |
| 2 | Copy `pearl_news/`, post script, two tests, self-hosted workflow (see §2) |
| 3 | Commit and push to `main` |
| 4 | Add 6 secrets (3 WordPress + 3 Qwen) in target repo |
| 5 | Install and run self-hosted runner; keep LM Studio up |
| 6 | Run workflow from Actions and check artifacts + WP draft |
| 7 | If LLM times out: see §7 (limit 3, expand toggle, timeout 240, LM Studio load) |

---

## Index

- [PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md) — Scheduling overview, Option A vs B
- [TRANSLATE_QWEN_PIPELINE_CLI.md](./TRANSLATE_QWEN_PIPELINE_CLI.md) — Running from Qwen/Qwen-Agent
- [DOCS_INDEX.md](./DOCS_INDEX.md) — Pearl News (document all)
