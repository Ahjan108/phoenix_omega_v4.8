# Pearl News — Research to Articles

**Purpose:** How generational research flows from research runs into article drafts (assembler and expansion). Single place to follow the path so research-backed content reaches Pearl News articles.

**Related:** [CONTINUOUS_RESEARCH_PLAN.md](research/CONTINUOUS_RESEARCH_PLAN.md), [continue_gen_research3.md](research/continue_gen_research3.md), [PEARL_NEWS_WRITER_SPEC.md](PEARL_NEWS_WRITER_SPEC.md), [PEARL_NEWS_ARTICLE_QUALITY_PLAN.md](PEARL_NEWS_ARTICLE_QUALITY_PLAN.md).

---

## One-line flow

**Research run → build_research_kb → KB (artifacts/research/kb/) → get_research_excerpt(topic, language) → assembler (youth_impact slot) and/or expansion (research block in prompt).**

---

## 1. Where research is produced

- **Script:** [scripts/research/run_research.py](../scripts/research/run_research.py) — two-pass Qwen3 (reasoning + YAML). Writes to `artifacts/research/psychology/`, `pain_points/`, `world_events/`, etc. See [continue_gen_research3.md](research/continue_gen_research3.md) and [CONTINUOUS_RESEARCH_PLAN.md](research/CONTINUOUS_RESEARCH_PLAN.md).
- **Optional append:** [scripts/research/kb_append.py](../scripts/research/kb_append.py) — can append single entries to the KB (e.g. from manual runs or one-off YAML).

---

## 2. How research becomes KB entries

- **Script:** [scripts/research/build_research_kb.py](../scripts/research/build_research_kb.py) scans `artifacts/research/{psychology,pain_points,world_events,narrative,platform}/` for YAML outputs from run_research.py, normalizes them into KB entries, and writes:
  - `artifacts/research/kb/entries.jsonl` — append-friendly JSONL
  - `artifacts/research/kb/index.json` — topic/cohort/region/layer lookup

**Commands:**
```bash
python scripts/research/build_research_kb.py              # incremental
python scripts/research/build_research_kb.py --rebuild  # clear and reseed
python scripts/research/build_research_kb.py --dry-run   # show what would be ingested
```

After running `run_research.py` and committing new YAML under `artifacts/research/`, run `build_research_kb.py` so the KB is updated. Expansion and (when enabled) assembler then see the new content.

---

## 3. How the pipeline uses the KB

### Retrieval

- **Module:** [pearl_news/research_kb/retrieval.py](../pearl_news/research_kb/retrieval.py)
- **Function:** `get_research_excerpt(topic, language=..., n=3, max_words=400, repo_root=...)` returns formatted text for a given Pearl News topic (e.g. `mental_health`, `climate`, `peace_conflict`) and language (`en`, `ja`, `zh-cn`). Maps language to region (e.g. `ja` → japan) and merges with global entries. Used by:
  1. **Assembler (pre-expansion):** The pipeline attaches `_research_excerpt` to each item before assembly. If no youth_impact atom exists for the topic, the assembler injects this excerpt into the youth_impact slot so drafts start with research-backed content when the KB is populated.
  2. **Expansion:** [pearl_news/pipeline/llm_expand.py](../pearl_news/pipeline/llm_expand.py) calls `get_research_excerpt` (via `_get_research_excerpt`) per item and injects it into the user message as "GEN Z / GEN ALPHA RESEARCH EXCERPT". The model is instructed to use it to add specific data points and anchors (Writer Spec §7).

### Fallback when KB is empty or missing

- **Expansion:** [llm_expand.py](../pearl_news/pipeline/llm_expand.py) uses hardcoded `_RESEARCH_SNIPPETS` by topic (mental_health, climate, peace_conflict, education, economy_work, inequality, partnerships) when KB returns nothing.
- **Assembler:** If no KB excerpt and no youth atom, the youth_impact slot uses a neutral stub (see [PEARL_NEWS_WRITER_SPEC.md](PEARL_NEWS_WRITER_SPEC.md) §7); expansion is expected to fill it from research or snippets.

---

## 4. Checklist for “research in articles”

1. Run research (e.g. `run_research.py`) and commit YAML under `artifacts/research/<layer>/`.
2. Build KB: `python scripts/research/build_research_kb.py`.
3. Run article pipeline: `python -m pearl_news.pipeline.run_article_pipeline --feeds ... --out-dir ...` (add `--expand` for LLM expansion). The pipeline attaches `_research_excerpt` before assembly when the KB is available.
4. Verify: drafts in `--out-dir` should have youth_impact content that passes the youth_impact_specificity gate (anchors present) when research or atoms are available.
