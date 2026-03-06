# Continuous research plan (local Qwen3, no Gemini)

**Purpose:** How the Pearl News continuous research “plane” runs: versioned prompts, feed ingest, local Qwen3 two-pass flow, youth signal sources, and artifact storage. **No Gemini; no external APIs for inference.**

**Generational research spec:** [continue_gen_research3.md](continue_gen_research3.md) is the single buildable spec for the generational intelligence engine (three core layers, two-pass YAML fix, Contradiction Audit, Persona Switching, youth sources).

---

## 1. Runtime and scope

- **Model:** Local **Qwen3-14B-GGUF** only (llama.cpp or Ollama). No Gemini. No cloud inference APIs.
- **Continuity:** Versioned prompts in the repo + optional scheduled **feed-ingest-only** workflow + local runs (or self-hosted runner with Ollama) that write to `artifacts/research/`. Repo history = research ledger.

---

## 2. Two-pass flow (YAML fix)

Qwen3 thinking mode can break valid YAML output. The pipeline uses two passes:

1. **Pass 1 (reasoning):** Run with `/think`. Full analysis (vibration points, invisible scripts, editorial hooks). Save to `artifacts/research/<layer>/<timestamp>_reasoning.md`.
2. **Pass 2 (YAML):** Run with `/no_think`, lower temp. Input: “Using only the following analysis, output a single valid YAML…” Paste Pass 1 summary. Save to `artifacts/research/<layer>/<timestamp>.yaml` with provenance header.

**Script:** [scripts/research/run_research.py](../scripts/research/run_research.py) implements both passes. See [scripts/research/README.md](../scripts/research/README.md).

---

## 3. Youth signal sources

Real youth conversation lives on TikTok, Reddit, YouTube, Discord, Instagram—not only RSS. The pipeline:

- **RSS:** UNICEF, UN Youth, Pew, Teen Vogue Politics, etc. Listed in [config/research/youth_feed_sources.yaml](../config/research/youth_feed_sources.yaml). Fetched to `artifacts/research/raw/` or `youth_feed_snapshots/` by [.github/workflows/research_feeds_ingest.yml](../.github/workflows/research_feeds_ingest.yml) (weekly) or manually.
- **Platforms:** Manual paste of trend/comment snippets or link lists into paste-and-extract prompts. Documented in [RESEARCH_FEED_SOURCES.md](RESEARCH_FEED_SOURCES.md).

---

## 4. Where things live

| Item | Location |
|------|----------|
| **Master spec** | [continue_gen_research3.md](continue_gen_research3.md) |
| **Prompts** | [research/prompts/](../research/prompts/) — system/, tasks/, schemas/ |
| **Run script** | [scripts/research/run_research.py](../scripts/research/run_research.py) |
| **Feed fetch script** | [scripts/research/fetch_feeds.py](../scripts/research/fetch_feeds.py) |
| **Feed config** | [config/research/youth_feed_sources.yaml](../config/research/youth_feed_sources.yaml), [config/research/marketing_feed_sources.yaml](../config/research/marketing_feed_sources.yaml) |
| **Feed docs** | [RESEARCH_FEED_SOURCES.md](RESEARCH_FEED_SOURCES.md), [MARKETING_FREE_SOURCES.md](MARKETING_FREE_SOURCES.md) |
| **Artifacts** | [artifacts/research/](../artifacts/research/) — raw/, youth_feed_snapshots/, psychology/, pain_points/, world_events/, narrative/, platform/, manifests/, marketing_sources/ |
| **Ingest workflow** | [.github/workflows/research_feeds_ingest.yml](../.github/workflows/research_feeds_ingest.yml) |

---

## 5. How to run continuously

- **Option A:** GitHub Action runs [research_feeds_ingest.yml](../.github/workflows/research_feeds_ingest.yml) on a schedule (e.g. weekly). You run Qwen3 locally (e.g. weekly): `run_research.py --prompt-id psychology --paste artifacts/research/raw/<date>/unicef_news.xml` (or paste preprocessed text). Commit new artifacts.
- **Option B:** Local cron runs `fetch_feeds.py` and/or `run_research.py`; you commit artifacts.
- **Option C:** Self-hosted GitHub runner with Ollama runs `run_research.py` on schedule and commits artifacts.

All options keep inference local (Qwen3 only); no Gemini.
