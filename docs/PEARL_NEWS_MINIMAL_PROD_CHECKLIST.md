# Pearl News — Minimal Production Checklist (Phase 1)

**Definition of Done:** All items below must pass before merge to main.

---

## Must-Pass Criteria

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

`.github/workflows/pearl_news_gates.yml` runs on push/PR to `main` when Pearl News files change. Workflow must succeed.

---

## Pre-Merge Verification

1. [ ] Run `python -m pearl_news.pipeline.run_article_pipeline --limit 5`
2. [ ] Confirm `artifacts/pearl_news/article_metadata.jsonl` has new lines
3. [ ] Run `pytest tests/test_topic_sdg_classifier.py tests/test_template_selector.py tests/test_pearl_news_quality_gates_minimal.py tests/test_pearl_news_pipeline_e2e.py -v`
4. [ ] Push branch and verify `pearl_news_gates` workflow passes

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

Store one signed go-live record before declaring Pearl News production-ready. Copy this template and fill with real values.

```
Go-Live Record — Pearl News
===========================
Date: _______________
Commit SHA: _______________
Signed by: _______________

Workflow run links:
- pearl_news_gates: _______________
- pearl_news_scheduled: _______________

Smoke-test output: _______________ (or link to artifact)

Rollback confirmed: [ ] Disable scheduled workflow
                    [ ] Rotate/revoke WP app password
                    [ ] Dry-run mode until fixed
```

---

## Phase 2 (Deferred)

- Predictive drift model
- Entropy optimizer
- Multilingual sync
- Dashboard UI
