# Pearl News prompts

- **expansion_system.txt** — System prompt for LLM expansion (target word count ~1000). **Operationalizes** [docs/PEARL_NEWS_WRITER_SPEC.md](../../docs/PEARL_NEWS_WRITER_SPEC.md): explicitly references §4 Lede, §5 Per-Template, §6 Teacher layer, §7 Youth specificity, §8 SDG, §9 Forward look, §11 What we never write. Used when the pipeline is run with `--expand` and `config/llm_expansion.yaml` has `enabled: true`. The API must be OpenAI-compatible (e.g. local Qwen via LM Studio or Ollama, or a GitHub/remote endpoint).
