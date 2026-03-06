# Pearl News prompts

- **expansion_system.txt** — System prompt for LLM expansion (target word count ~1000). Implements the writing craft rules from [docs/PEARL_NEWS_WRITER_SPEC.md](../../docs/PEARL_NEWS_WRITER_SPEC.md) (lede, youth impact, teacher layer, forward look, SDG, what we never write). Used when the pipeline is run with `--expand` and `config/llm_expansion.yaml` has `enabled: true`. The API must be OpenAI-compatible (e.g. local Qwen via LM Studio or Ollama, or a GitHub/remote endpoint).
