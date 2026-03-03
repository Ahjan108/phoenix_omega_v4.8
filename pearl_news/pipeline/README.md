# Pearl News pipeline

- **feed_ingest.py** — **Implemented.** Loads `feeds.yaml`, fetches RSS/Atom with `feedparser`, normalizes to schema (id, title, url, pub_date, summary, source_feed_id, source_feed_title). Requires `feedparser` (see repo `requirements.txt`).
- **run_article_pipeline.py** — Entry point. Runs ingest → classify → select → assemble → quality gates → QC. Writes drafts to `--out-dir` and appends metadata to `artifacts/pearl_news/article_metadata.jsonl`.
- **topic_sdg_classifier.py** — **Implemented.** Maps item → topic, primary_sdg, sdg_labels, un_body via `sdg_news_topic_mapping.yaml` (keyword match).
- **template_selector.py** — **Implemented.** Picks 1 of 5 templates by topic from `article_templates_index.yaml`.
- **article_assembler.py** — **Implemented.** Fills template slots from feed item; outputs draft with teacher_ids, stressor_tags, region passthrough.
- **quality_gates.py** — **Implemented.** Blocklist, phrase repetition, teacher saturation, template rotation.
- **qc_checklist.py** — Implemented. 5-point editorial checklist.

**Run full pipeline:**
```bash
python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts --limit 10
```

**Output:**
- `artifacts/pearl_news/drafts/` — article JSON files, feed_item JSON, ingest_manifest.json
- `artifacts/pearl_news/article_metadata.jsonl` — one JSON line per article (schema: docs/PEARL_NEWS_ARTICLE_METADATA_SCHEMA.md)

Optional: LLM step (local Qwen3 or API) for summarization or section expansion — see docs/PEARL_NEWS_ARCHITECTURE_SPEC.md §5.
