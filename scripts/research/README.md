# Generational research scripts

Run two-pass Qwen3 generational research locally. See [docs/continue_gen_research3.md](../../docs/continue_gen_research3.md).

## Prerequisites

- **Ollama** with Qwen3-14B: `ollama run hf.co/Qwen/Qwen3-14B-GGUF:Q8_0` (or pull and set `OLLAMA_MODEL`).
- Python 3.9+ with `requests`: `pip install requests`.

## Usage

```bash
# From repo root
python scripts/research/run_research.py --prompt-id psychology --paste artifacts/research/raw/sample.txt
python scripts/research/run_research.py --prompt-id pain_points --paste -
python scripts/research/run_research.py --prompt-id event_impact --skip-yaml-pass
```

- **--prompt-id:** `psychology` | `pain_points` | `event_impact`
- **--paste:** Path to raw data file, or `-` to read from stdin.
- **--skip-yaml-pass:** Only run the reasoning pass (writes `.reasoning.md` only).
- **--model:** Ollama model name (default: `qwen3:14b` or `OLLAMA_MODEL`).
- **--out-dir:** Override output directory (default: `artifacts/research/<layer>/`).

Outputs:

- `artifacts/research/<layer>/<timestamp>_reasoning.md` — Pass 1 (thinking) response.
- `artifacts/research/<layer>/<timestamp>.yaml` — Pass 2 YAML with provenance header.
