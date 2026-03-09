# Pearl News Architecture Spec

**Last updated:** 2026-03-09  
**Authority scope:** Pearl News article pipeline strategy, planning, creation, QC, and posting contracts in `phoenix_omega`.

---

## 1. System role

Pearl News is the article pipeline (not the book pipeline). It converts feed items into publish-ready civic/spiritual articles with youth + SDG framing, then hands off to WordPress posting.

Primary runtime entrypoint:  
- [`pearl_news/pipeline/run_article_pipeline.py`](../pearl_news/pipeline/run_article_pipeline.py)

---

## 2. Article creation strategy

### 2.1 Input strategy

- Feed ingest from configured RSS/Atom sources.
- Topic + SDG classification per item.
- One selected article template per item.
- Teacher context resolved per article.

Core modules:
- [`feed_ingest.py`](../pearl_news/pipeline/feed_ingest.py)
- [`topic_sdg_classifier.py`](../pearl_news/pipeline/topic_sdg_classifier.py)
- [`template_selector.py`](../pearl_news/pipeline/template_selector.py)
- [`teacher_resolver.py`](../pearl_news/pipeline/teacher_resolver.py)

### 2.2 Template planning strategy

Five templates are used:
1. `hard_news_spiritual_response`
2. `youth_feature`
3. `interfaith_dialogue_report`
4. `explainer_context`
5. `commentary`

Selection policy:
- Topic/source-driven default mapping.
- Deterministic diversity control.
- Group/USLF style (`interfaith_dialogue_report`) constrained to ~5%; single-teacher focus dominates.

Config:
- [`pearl_news/config/article_templates_index.yaml`](../pearl_news/config/article_templates_index.yaml)
- [`pearl_news/config/template_diversity.yaml`](../pearl_news/config/template_diversity.yaml)

### 2.3 Assembly strategy

Assembler fills section slots using:
- feed event summary,
- youth impact atoms,
- teacher/practice atoms,
- SDG references,
- controlled placeholders if atom content is missing.

Source line is appended at article end.

Module:
- [`article_assembler.py`](../pearl_news/pipeline/article_assembler.py)

---

## 3. Expansion and validation plan

### 3.1 Optional LLM expansion

When `--expand` is enabled, expansion injects:
- teacher identity + teaching atoms,
- research excerpt,
- language + audience,
- template context,
- SDG/topic metadata.

Module:
- [`llm_expand.py`](../pearl_news/pipeline/llm_expand.py)

### 3.2 Hard validation gates (post-expansion)

When `--validate` is enabled (with expansion), validator enforces structural and quality constraints, including:
- required sections,
- named teacher,
- teacher three points,
- SDG number/title,
- youth anchor,
- banned phrase exclusion,
- source line presence.

Module:
- [`article_validator.py`](../pearl_news/pipeline/article_validator.py)

### 3.3 QC gates

Fail-hard QC checks run before output filtering:
- fact-check completeness,
- youth specificity,
- SDG/UN accuracy,
- promotional tone,
- UN endorsement detector.

Modules:
- [`quality_gates.py`](../pearl_news/pipeline/quality_gates.py)
- [`qc_checklist.py`](../pearl_news/pipeline/qc_checklist.py)

---

## 4. Output contracts

Pipeline outputs under `artifacts/pearl_news/drafts/<language>/` include:
- `article_*.json` drafts,
- `ingest_manifest.json`,
- `build_manifests.json`.

The build manifest contains article-level audit trace fields (template, teacher, validation, signatures, qc).

---

## 5. Posting strategy (WordPress)

Posting is a separate step (manual or workflow-assisted) via REST API.

Posting script:
- [`scripts/pearl_news_post_to_wp.py`](../scripts/pearl_news_post_to_wp.py)

Client:
- [`pearl_news/publish/wordpress_client.py`](../pearl_news/publish/wordpress_client.py)

Credentials (env only):
- `WORDPRESS_SITE_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APP_PASSWORD`

Supported posting features:
- `draft` or `publish` status,
- optional author/category/tag,
- featured image upload by URL or local file.

---

## 6. Workflow plan

Production workflows in `phoenix_omega`:
- [`pearl_news_scheduled.yml`](../.github/workflows/pearl_news_scheduled.yml)
- [`pearl_news_manual_expand.yml`](../.github/workflows/pearl_news_manual_expand.yml)

Operational pattern:
- Scheduled run: publish-grade generation (`--expand --validate --select-image --strict-publish-grade`) with repair attempts and hard-fail on unresolved gate failures.
- Manual run: same publish-grade path with operator-selected language/limit.

---

## 7. Failure behavior

- Pipeline retries execution in workflow wrapper.
- Validation/QC failures mark items and can route to manual review.
- WordPress posting step is non-blocking in workflow (continue-on-error) to preserve draft artifact handoff.

---

## 8. Related docs

- [`docs/PEARL_NEWS_WRITER_SPEC.md`](./PEARL_NEWS_WRITER_SPEC.md)
- [`docs/PEARL_NEWS_GO_NO_GO_CHECKLIST.md`](./PEARL_NEWS_GO_NO_GO_CHECKLIST.md)
- [`docs/PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md`](./PEARL_NEWS_MINIMAL_PROD_CHECKLIST.md)
- [`pearl_news/README.md`](../pearl_news/README.md)
