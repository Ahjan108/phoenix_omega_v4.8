# Research feed sources (youth + marketing)

**Purpose:** Single list of free feeds and sources for the generational deep-research pipeline. Content is fetched or copy-pasted into Qwen3 prompts (paste-and-extract). No Gemini; no paid APIs.

**Config:** [config/research/youth_feed_sources.yaml](../config/research/youth_feed_sources.yaml), [config/research/marketing_feed_sources.yaml](../config/research/marketing_feed_sources.yaml).

---

## Youth and generational (Gen Z / Gen Alpha)

| Source | What it provides | How to use |
|--------|------------------|------------|
| **UNICEF** | News, youth-focused content | RSS in `youth_feed_sources.yaml`; fetch to `artifacts/research/raw/` or paste into prompts |
| **UN Youth Envoy** | UN youth initiatives | RSS; same as above |
| **Pew Research (Gen Z)** | Demographics, attitudes | Manual or link in config; paste key findings into Qwen3 |
| **Teen Vogue Politics** | Youth political/civic coverage | Manual; paste articles or summaries |
| **TikTok** | Extremely high — trend/comment snippets | Manual paste into paste-and-extract prompts |
| **Reddit** | High — subreddit discussions | Subreddit RSS or manual paste → `artifacts/research/youth_feed_snapshots/` |
| **YouTube** | High — comments, transcripts | Manual paste or script-fetched text |
| **Discord** | Medium — server summaries | Manual paste |
| **Instagram** | Medium | Manual paste or link list |

Refresh: RSS via [.github/workflows/research_feeds_ingest.yml](../.github/workflows/research_feeds_ingest.yml) (optional) or local script; platforms = manual paste.

---

## Marketing and audiobook (free)

| Source | What it provides | Refresh |
|--------|------------------|---------|
| **APA (audiopub.org)** | Research FAQ, 5-year industry data, annual survey ($2.22B 2024, 13% growth, 51% US adults listened) | Quarterly |
| **Publishers Weekly** | Audiobook/industry articles, Spotify 2025 data, genre growth | Weekly |
| **Spotify** | Year-end listening data, blog posts | Manual |
| **Library Journal / infoDOCKET** | Summaries of APA and industry reports | Manual |

Use: Fetch or copy text → paste into Qwen3 extract prompt → output to `artifacts/research/marketing_sources/` or into marketing config per [MARKETING_DEEP_RESEARCH_PROMPTS.md](MARKETING_DEEP_RESEARCH_PROMPTS.md).

---

## Related

- [continue_gen_research3.md](continue_gen_research3.md) — Generational research master spec
- [CONTINUOUS_RESEARCH_PLAN.md](CONTINUOUS_RESEARCH_PLAN.md) — How the research plane runs (local Qwen3, feed ingest, artifacts)
