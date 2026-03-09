# Pearl News — Minimal Production Checklist (Phase 1)

**Definition of Done:** Code/tests are 100% when all Must-Pass Criteria pass. **Production-go-live is 100%** only when all 6 Operational Gates are confirmed on `main` with evidence links.

---

## Must-Pass Criteria (Code/Tests — 100%)

### 1. No Import Errors

```bash
python -m pearl_news.pipeline.run_article_pipeline --limit 1
```

Pipeline must start without `ImportError` or missing module.

### 2. Metadata JSONL Emitted

After running the pipeline:

- `artifacts/pearl_news/` directory exists
- `artifacts/pearl_news/article_metadata.jsonl` exists (or is created on first article)
- Each assembled article appends one JSON line with required keys: `article_id`, `date`, `topic`, `primary_sdg`, `template_id`, `teacher_ids`, `stressor_tags`, `region`, `phrase_flags`

### 3. Four Test Files Green

```bash
PYTHONPATH=. python -m pytest \
  tests/test_topic_sdg_classifier.py \
  tests/test_template_selector.py \
  tests/test_pearl_news_quality_gates_minimal.py \
  tests/test_pearl_news_pipeline_e2e.py \
  -v
```

All tests must pass.

### 4. CI Green

Pearl News workflow runs in **Ahjan108/Qwen-Agent** must succeed on push/PR to `main`.

---

## Operational Gates (Production 100%)

These 6 must be confirmed **on `main`** with evidence links before declaring Pearl News production-ready. Rollback validation is recommended before go-live.

| # | Gate | Evidence link |
|---|------|---------------|
| 1 | **Merge to `main`** | PR URL: _______________ |
| 2 | **Pearl News workflow suite green on `main` (Qwen-Agent)** | [Qwen-Agent Actions](https://github.com/Ahjan108/Qwen-Agent/actions) run URL: _______________ |
| 3 | **Networked pipeline smoke run passes on `main`** | Run URL or artifact: _______________ |
| 4 | **Scheduled workflow run passes (Qwen-Agent)** | [Qwen-Agent Actions](https://github.com/Ahjan108/Qwen-Agent/actions) run URL: _______________ |
| 5 | **WordPress draft-post flow verified with real secrets** | Post URL or draft ID: _______________ |
| 6 | **Checklist doc completed with evidence links** | All above cells filled; Evidence Lock (below) signed |

**Writer Spec compliance:** Before publishing any article, confirm it passes all 6 quality gates (including `writer_spec_forbidden_phrases`). See [PEARL_NEWS_GO_NO_GO_CHECKLIST.md](PEARL_NEWS_GO_NO_GO_CHECKLIST.md) item 9 and [PEARL_NEWS_ARTICLE_QUALITY_PLAN.md](PEARL_NEWS_ARTICLE_QUALITY_PLAN.md).

---

## Pre-Merge Verification

1. [ ] Run `python -m pearl_news.pipeline.run_article_pipeline --limit 5`
2. [ ] Confirm `artifacts/pearl_news/article_metadata.jsonl` has new lines
3. [ ] Run `pytest tests/test_topic_sdg_classifier.py tests/test_template_selector.py tests/test_pearl_news_quality_gates_minimal.py tests/test_pearl_news_pipeline_e2e.py -v`
4. [ ] Push branch and verify Pearl News workflows pass in Qwen-Agent

---

## Rollback Procedure (recommended before go-live)

Validate **at least once** before go-live. Document date and outcome.

1. **Disable scheduler** — In Qwen-Agent Actions, disable the Pearl News scheduled workflow.
2. **Rotate/revoke WP app password** — In WordPress admin, revoke the application password used by `WORDPRESS_APP_PASSWORD`. Set `WORDPRESS_APP_PASSWORD` empty in repo secrets to force dry-run mode.
3. **Dry-run mode until fixed** — With `WORDPRESS_APP_PASSWORD` unset, workflow runs in dry-run; no posts are published.

| Step | Validated | Date | Owner |
|------|-----------|------|-------|
| Disable scheduler | [ ] | | |
| Rotate WP app password | [ ] | | |
| Dry-run mode confirmed | [ ] | | |

---

## Incident Ownership

Assign before go-live. Required for Pearl News 100%.

| Role | Name | Contact |
|------|------|---------|
| On-call owner | _TBD_ | _TBD_ |
| Backup | _TBD_ | _TBD_ |

**Response SLA:**
- Triage: within 30 minutes of failed scheduled run
- Fix or rollback: within 2 hours

---

## Evidence Lock

Store one signed go-live record before declaring Pearl News production-ready. Fill with real values (run URLs, outputs, commit SHA, owner/date). Links to GitHub Actions runs: `https://github.com/OWNER/REPO/actions/runs/RUN_ID`.

```
Go-Live Record — Pearl News
===========================
Date: _______________
Commit SHA: _______________
Signed by: _______________

Operational gates (evidence links):
1. Merge PR: _______________
2. Qwen-Agent Pearl News workflow run: _______________
3. Networked smoke run: _______________ (or artifact link)
4. Qwen-Agent Pearl News scheduled run: _______________
5. WordPress draft-post: _______________
6. This checklist completed: ✓

Rollback validated (recommended):
- [ ] Disable scheduled workflow
- [ ] Rotate/revoke WP app password
- [ ] Dry-run mode until fixed
```

---

## Phase 2 (Deferred)

- Predictive drift model
- Entropy optimizer
- Multilingual sync
- Dashboard UI
