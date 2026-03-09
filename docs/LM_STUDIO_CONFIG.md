# LM Studio Configuration — Qwen3-14B Self-Hosted Runner

Recommended settings for the macOS M4 self-hosted runner serving Qwen3-14B-Q4_K_M (9 GB).

## Server Settings

| Setting | Current | Recommended | Why |
|---|---|---|---|
| Parallel slots | 4 | **2** | With 2600+ token prompts and 4096 ctx/slot, 4 slots exhausts KV cache (640 MB). 2 slots eliminates "failed to find memory slot" errors and slot purges. |
| Context per slot | 4096 | 4096 | Fine — matches max prompt + completion length. |
| Prompt cache limit | 8 GB | **4 GB** | 59 prompts with low similarity (0.02–0.23) means most cache entries are never reused. Halving the limit reduces memory pressure without meaningful cache hit loss. |
| Idle TTL | 60 min | **120 min** | Model unloads at ~23:28, but scheduled comparator window starts 00:00 UTC. 120 min bridges the gap and avoids a 20-second cold reload. |
| GPU offload | Full | Full | Keep full GPU offload for M4 — no change needed. |

## Thinking Mode

Qwen3-14B defaults to "thinking mode" where every response begins with a `<think>...</think>` block before producing actual content. This wastes tokens and time for structured output tasks (translation, judging, warmup).

All LLM call sites in this repo now explicitly disable thinking:

- **OpenAI Python SDK** calls use `extra_body={"enable_thinking": False}`
- **curl/HTTP** calls include `"enable_thinking": false` in the JSON body
- **Warmup** payloads use `max_tokens: 64` (was 8) so the model can actually produce "OK" without hitting the token limit

## Warmup Best Practices

The warmup call should:
1. Disable thinking mode (`enable_thinking: false`)
2. Use `max_tokens: 64` (enough for "OK" + margin, not enough to waste time)
3. Use `temperature: 0.0` for deterministic output
4. Check that the response content contains "OK" (not just a 200 status)

## Known Workflow Risks (Not Yet Fixed)

These were identified in audit but are lower priority / require design decisions:

1. **`marketing-briefs-and-proposals.yml`** — LM Studio lock acquired and released in a single step, so subsequent steps run without the lock. The lock should wrap the entire job or the LLM-calling steps need to be in the same step as the lock.

2. **`marketing_continuous.yml`** — No concurrency gate, no LM lock, no heavy-window guard. Could collide with audiobook/locale jobs.

3. **`catalog-book-pipeline.yml`** — 120-minute self-hosted jobs with no sharding. Consider breaking into teacher-level shards like `run_locale_batches.py`.

## Monitoring

Watch for these symptoms in LM Studio developer logs:

- `failed to find a memory slot for batch` — KV cache exhaustion. Reduce parallel slots.
- `slot was purged` — Active generation evicted. Same fix.
- `prompt cache update` taking > 2s — Cache thrashing. Reduce cache limit or deduplicate prompts.
- Client disconnections before completion — Timeout too short or thinking mode wasting tokens.
- `model unloaded` followed by cold load — Increase idle TTL.
