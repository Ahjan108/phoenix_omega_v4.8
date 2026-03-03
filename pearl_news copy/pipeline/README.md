# Pearl News pipeline

- **feed_ingest.py** — **Implemented.** Loads `feeds.yaml`, fetches RSS/Atom with `feedparser`, normalizes to schema (id, title, url, pub_date, summary, source_feed_id, source_feed_title). Requires `feedparser` (see repo `requirements.txt`).
- **run_article_pipeline.py** — Entry point. Runs ingest → writes `ingest_manifest.json` and per-item `feed_item_<id>.json` to `--out-dir`. Next steps (classify, template select, assemble, quality gates, QC) are stubbed.
- **topic_sdg_classifier.py** — *Not yet implemented.* Map item → topic, SDG(s), suggested template (use `sdg_news_topic_mapping.yaml` + keyword or LLM).
- **template_selector.py** — *Not yet implemented.* Pick 1 of 5 templates by topic/event type.
- **article_assembler.py** — *Not yet implemented.* Fill template slots from feed item + atoms; output draft.
- **quality_gates.py** — *Not yet implemented.* Fail-hard checks (legal_boundary, editorial_firewall, quality_gates config).
- **qc_checklist.py** — *Not yet implemented.* 5-point editorial checklist.

**Run step 1 (ingest only):**
```bash
python -m pearl_news.pipeline.run_article_pipeline --feeds pearl_news/config/feeds.yaml --out-dir artifacts/pearl_news/drafts --limit 10
```

Optional: LLM step (local Qwen3 or API) for summarization or section expansion — see docs/PEARL_NEWS_ARCHITECTURE_SPEC.md §5.
