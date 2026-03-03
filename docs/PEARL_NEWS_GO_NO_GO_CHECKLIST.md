# Pearl News — GO/NO-GO Checklist (100% Wired)

Use this checklist to close the “ingest-only” branch and confirm full end-to-end production chain is active and passing.

**Production 100%** requires all three of the following (code-chain is done; these are the remaining gates):

1. **One real networked run** from live feeds → final article drafts (evidence recorded).
2. **CI green on main** for Pearl News tests/workflows (evidence: CI run URL).
3. **GO/NO-GO checklist signed** with evidence links (below).

---

## 1. Pipeline components (all implemented and used)

| # | Component | Status | How to verify |
|---|-----------|--------|----------------|
| 1 | `topic_sdg_classifier.py` | ✅ Implemented | Used in `run_article_pipeline`; assigns topic, primary_sdg, sdg_labels, un_body from `sdg_news_topic_mapping.yaml`. |
| 2 | `template_selector.py` | ✅ Implemented | Used in pipeline; sets template_id per item from index + rules. |
| 3 | `article_assembler.py` | ✅ Implemented | Used in pipeline; fills template slots (news + teacher + youth + SDG refs); appends disclaimer. |
| 4 | `quality_gates.py` | ✅ Implemented | Used in pipeline; 5 gates (fact_check, youth_specificity, sdg_accuracy, promotional, un_endorsement); fail-hard. |
| 5 | `qc_checklist.py` | ✅ Implemented | Used in pipeline; runs gates and optionally filters to passed-only. |

---

## 2. Final article outputs (not just feed_item_*.json)

| # | Requirement | Status | How to verify |
|---|--------------|--------|----------------|
| 5 | Final article files written | ✅ | `--out-dir` contains `article_<id>.json` with `title`, `content`, `article_type`, `topic`, `primary_sdg`, `qc_results`. |
|   | Build manifest per run | ✅ | `ingest_manifest.json` and `build_manifests.json` in out-dir. |

---

## 3. CI green on main

| # | Requirement | Status | How to verify |
|---|--------------|--------|----------------|
| 6 | CI passes for Pearl News pipeline | Pending | Push to `main` (or PR that touches `pearl_news/**` or the two test files). Workflow: `.github/workflows/pearl_news_gates.yml`. Tests: `tests/test_pearl_news_quality_gates_minimal.py`, `tests/test_pearl_news_pipeline_e2e.py`. |

---

## 4. One real networked run (feeds → final drafts)

| # | Requirement | Status | How to verify |
|---|--------------|--------|----------------|
| 7 | Full flow from feeds to drafts | ✅ Done | Run pipeline with network (live UN feeds). Local: `pip install feedparser pyyaml` then `./scripts/pearl_news_networked_run_and_evidence.sh --limit 5` or `python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts --limit 5`. Or trigger `.github/workflows/pearl_news_scheduled.yml` (workflow_dispatch) and use uploaded artifact as evidence. |

---

## GO criteria (all must be YES)

- [x] 1. topic_sdg_classifier implemented and used in pipeline
- [x] 2. template_selector implemented and used
- [x] 3. article_assembler implemented and used (teacher + youth + SDG injected)
- [x] 4. quality_gates and qc_checklist implemented and enforced as blocking (filter_to_passed=True by default)
- [x] 5. Final article outputs written (article_<id>.json + build_manifests.json)
- [ ] 6. **CI green on main** for Pearl News tests/workflows
- [x] 7. **One real networked run** proving full flow from feeds → final article drafts
- [ ] 8. **Checklist signed** with evidence links (section below)

**NO-GO:** If any item above is unchecked, the system is not production 100%.

---

## Evidence (sign-off)

When the three production gates are done, paste links here and sign.

| Evidence | Link or value |
|----------|----------------|
| **CI run (green)** | *Paste after push to main: e.g. `https://github.com/ORG/REPO/actions/runs/XXXXX`* |
| **Networked run** | **Done.** Path: `artifacts/pearl_news/evaluation/networked_run_evidence.json`. Run: 2026-03-03; 5 items → 5 articles (ingest from live UN feeds → drafts). |
| **Signed by** | *Pending — paste name/date after CI run is green.* |

**Next step to reach production 100%:** Push this branch to `main` (or merge a PR). That triggers `.github/workflows/pearl_news_gates.yml`. Open the Actions run, confirm it’s green, then paste the run URL into the **CI run (green)** row above and add your name/date to **Signed by**.

---

## Quick verification commands

```bash
# From repo root (install feedparser first: pip install feedparser pyyaml)
python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts --limit 3
# Expect: Ingested N items → Classified → Selected templates → Assembled → Gates → QC → Wrote N article drafts

# Or use the evidence script (writes artifacts/pearl_news/evaluation/networked_run_evidence.json)
./scripts/pearl_news_networked_run_and_evidence.sh --limit 5

ls artifacts/pearl_news/drafts/article_*.json
# Expect: at least one article_<id>.json

# CI (local): run the same tests as pearl_news_gates.yml
PYTHONPATH=. python -m pytest tests/test_pearl_news_quality_gates_minimal.py tests/test_pearl_news_pipeline_e2e.py -v
```
