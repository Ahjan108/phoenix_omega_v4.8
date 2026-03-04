# Research artifacts (generational deep research)

Outputs from the Pearl News generational research pipeline. See [docs/continue_gen_research3.md](../../docs/continue_gen_research3.md).

| Directory | Contents |
|-----------|----------|
| `raw/` | Ingested RSS/snapshots by date (from research_feeds_ingest or manual) |
| `youth_feed_snapshots/` | Youth-focused feed text for paste-and-extract |
| `psychology/` | Layer 1 YAMLs (Generational Psychology) |
| `pain_points/` | Layer 2 YAMLs (Life Problems & Aspirations; Contradiction Audit) |
| `world_events/` | Layer 3 YAMLs (Event Impact; Persona Switching) |
| `narrative/` | Youth narratives (optional) |
| `platform/` | Platform/story-angle (optional) |
| `manifests/` | Daily editorial/story briefs |
| `marketing_sources/` | APA, PW, etc. snapshots (optional) |

All YAML artifacts include a provenance header: `run_date`, `model`, `prompt_id`, `source`.
