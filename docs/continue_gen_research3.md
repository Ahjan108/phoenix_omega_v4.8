# Generational Deep Research — Master Spec (Pearl News)

**Purpose:** Single buildable spec for the Pearl News generational intelligence engine. Merges File 1 (continue_gen_research.rtf), File 2 (continue_gen_research2.rtf), and editor feedback. **Runtime:** Local Qwen3-14B-GGUF only (llama.cpp/Ollama). No Gemini. No external APIs for inference.

**Related:** [CONTINUOUS_RESEARCH_PLAN.md](CONTINUOUS_RESEARCH_PLAN.md), [PEARL_NEWS_WRITER_SPEC.md](PEARL_NEWS_WRITER_SPEC.md), [MARKETING_DEEP_RESEARCH_PROMPTS.md](MARKETING_DEEP_RESEARCH_PROMPTS.md).

---

## 1. Overview

World events are interpreted through **invisible scripts**—cultural beliefs and psychological predispositions that shape youth identity. This system:

- Runs **three pipeline stages**: Ingestion → Contextual Triangulation → Synthesis.
- Uses **three core intelligence layers**: Generational Psychology, Life Problems & Aspirations, Event Impact (plus optional Narrative, Linguistic, Platform/Story).
- Enforces **two-pass YAML**: reasoning with `/think` first; then a separate call with `/no_think` to output valid YAML (avoids Qwen thinking-mode YAML breakage).
- Injects **knowledge context**: today’s date and last N headlines/snippets from ingested feeds so the model prefers fresh over training-date facts.
- Writes all outputs under `artifacts/research/` with provenance (run_date, model, prompt_id).

---

## 2. Three core layers + optional dimensions

| Layer | Purpose | File 1 prompt(s) | Chaining |
|-------|--------|-------------------|----------|
| **1. Generational Psychology** | How the generation thinks (identity, emotions, trust, tech) | Psych-Pulse Researcher | Longitudinal Contrast; delta shifts |
| **2. Life Problems & Aspirations** | What they struggle with and want (economic, career, money scripts) | Econ-Script Analyst | Script Deconstruction; **Contradiction Audit** (mandatory) |
| **3. Event Impact** | How world events affect them (formative trauma, activism) | Identity-Conflict Researcher; Theory-Lens | Historical Resonance; **Persona Switching** (mandatory) |

**Optional dimensions:**

- **4. Youth Narratives** — Live stories (e.g. gaza_war, ai_jobs); one prompt or section in synthesis.
- **5. Linguistic / Semantic** — Semantic Trend-Spotter (brainrot, slop, media mistranslation).
- **6. Platform / Story angle** — Platform Strategist + Daily Editorial Manifest for story briefs.

**Concepts to keep:** Vibration points (event × generational trauma/aspiration); Social Trivialization (flag when youth struggles are meme-ified); invisible scripts.

---

## 3. Pipeline backbone

```
Feeds + youth signals (RSS / paste)
  → Ingestion (extract signals: entities, themes, sentiment)
  → Contextual Triangulation (compare to baselines; Contradiction Audit; Persona Switching)
  → Synthesis (two-pass: /think then /no_think YAML + story briefs)
  → artifacts/research/
```

- **Ingestion:** Fetch RSS and/or paste youth/social content; Qwen3-14B with `/no_think` (or short prompt) extracts “signals.”
- **Contextual Triangulation:** Load previous week’s YAML from `artifacts/research/`; prompt with `/think` to compare, run **Contradiction Audit** (Layer 2), **Persona Switching** (Layer 3).
- **Synthesis:** Pass 1 with `/think` (full analysis); Pass 2 with `/no_think`, lower temp, “Output only valid YAML from this schema.” Optional: parse YAML and re-prompt on syntax error.
- **Knowledge cutoff:** Inject “Today’s date” and “Last 10 headlines/snippets” from ingested feeds into context.

With only Qwen3-14B, the three tiers are three **prompt stages**; if you add 7B/72B later, map ingest → 7B, triangulate → 14B, synthesis → 72B.

---

## 4. Mandatory prompt elements

- **Contradiction Audit (Layer 2):** Every Layer 2 run must ask: “Where does this cohort’s behavior contradict their stated fears (e.g. spending on luxury vs fear of poverty)? Explain the bridge.”
- **Persona Switching (Layer 3):** Every Layer 3 run must ask: “Analyze the same event from: (a) Gen Z male, high-income country; (b) Gen Alpha child, conflict zone. Output both perspectives.”

---

## 5. Two-pass YAML fix

- **Pass 1:** Run Qwen3 **with /think**. Ask for full analysis (vibration points, invisible scripts, editorial hooks, etc.). Save full response to e.g. `.reasoning.md`.
- **Pass 2:** Run Qwen3 **with /no_think**, temp 0.3–0.5. Input: “Using only the following analysis, output a single valid YAML object that conforms to this schema. No thinking, no markdown fences, only YAML.” Paste Pass 1 summary or key bullets. Parse result; if invalid, re-prompt with “YAML parse error: …”.
- **Script:** `scripts/research/run_research.py` implements both passes and writes reasoning + YAML to `artifacts/research/<layer>/` with provenance header.

---

## 6. Youth signal sources

| Source | Importance | Use |
|--------|------------|-----|
| TikTok | Extremely high | Curated link list or manual paste of trend/comment snippets into paste-and-extract prompts |
| Reddit | High | Subreddit RSS or manual paste → `artifacts/research/youth_feed_snapshots/` |
| YouTube comments | High | Manual paste or script-fetched text → paste-and-extract |
| Discord | Medium | Manual paste of server summaries or quotes |
| Instagram | Medium | Manual paste or link list |

**RSS list:** UNICEF, Pew, UN Youth, Teen Vogue Politics, etc. (see `config/research/youth_feed_sources.yaml` and [RESEARCH_FEED_SOURCES.md](RESEARCH_FEED_SOURCES.md)). Ingest to `artifacts/research/raw/` or `youth_feed_snapshots/`; paste or inject into prompts.

---

## 7. Folder structure

```
artifacts/research/
  raw/                    # Ingested RSS/snapshots (by date)
  youth_feed_snapshots/   # Youth-focused feed text for paste
  psychology/             # Layer 1 YAMLs
  pain_points/            # Layer 2 YAMLs (Contradiction Audit)
  world_events/           # Layer 3 YAMLs (Persona Switching)
  narrative/              # Youth narratives (optional)
  platform/               # Platform/story-angle (optional)
  manifests/              # Daily editorial/story briefs
  marketing_sources/      # APA, PW, etc. snapshots (optional)

research/prompts/
  system/                 # Persona definitions (Psych-Pulse, Econ-Script, etc.)
  tasks/                  # Exact prompt text per dimension
  schemas/                # YAML schema references (or inline in doc)

config/research/
  youth_feed_sources.yaml
  marketing_feed_sources.yaml  # optional
```

---

## 8. Prompts (File 1, adapted for Qwen3)

### Layer 1 — Psych-Pulse Researcher (Generational Psychology)

**System:** You are a Senior AI Research Architect and Youth Psychologist. Analyze raw news feeds for psychological stressors for Gen Z (1997–2012) and Gen Alpha (2013–present). Focus on: (1) Digital Overload (phantom pings, doomscrolling); (2) Vicious Cycle of Isolation (anxiety → social avoidance); (3) Social Trivialization (mental health portrayed as quirky/trendy). Use <think> to evaluate “Latent Dysfunctions” and compare to 83% fear-driven anxiety conversations. Output in the prescribed YAML schema.

**User (Pass 1, with /think):** Analyze the following raw data for psychological impact: {{RAW_DATA}}

**YAML output (Pass 2, /no_think):** anxiety_score (1–10), trigger_mechanism, generational_difference (Gen Z therapy vs Gen Alpha digital/AI support), editorial_hook.

---

### Layer 2 — Econ-Script Analyst (Life Problems & Aspirations)

**System:** You are a Geopolitical Economist specializing in youth labor markets. Analyze news on AI displacement and global economic shifts. Apply “Equity over Equality”; evaluate Gen Z’s Stability Script vs Gen Alpha’s Entrepreneurial Script. In <think> analyze invisible scripts of scarcity. **Mandatory: Contradiction Audit**—where does this cohort’s behavior contradict their stated fears (e.g. luxury spending vs fear of poverty)? Explain the bridge.

**User (Pass 1):** Process this economic data: {{RAW_DATA}}

**YAML output (Pass 2):** career_impact_matrix (gen_z, gen_alpha), financial_trauma_risk, contradiction_audit, recommended_content_format.

---

### Layer 3 — Identity-Conflict Researcher + Theory-Lens (Event Impact)

**System:** You are an Identity Psychologist and Geopolitical Trauma Analyst. Analyze news on global conflict through youth identity formation. Apply Functionalist, Conflict, and Symbolic Interactionist perspectives. Link biography to history; evaluate eco-anxiety vs conflict-cynicism. **Mandatory: Persona Switching**—analyze the same event from (a) Gen Z male, high-income country; (b) Gen Alpha child, conflict zone. Output both perspectives.

**User (Pass 1):** Analyze the identity impact of this conflict: {{RAW_DATA}}

**YAML output (Pass 2):** identity_fracture_score (1–10), activism_profile, narrative_pivot, persona_switching (gen_z_high_income, gen_alpha_conflict_zone).

---

### Optional — Semantic Trend-Spotter (Linguistic)

**System:** You are a Computational Linguist. Scan for linguistic shifts in Gen Z/Gen Alpha vocabulary: 2025 word candidates (e.g. Rage bait, Slop, 67); semantic shifts (Sigma, Aura, Rizz); Media Mistranslation risks. In <think> evaluate the Brevity Principle.

**User:** Analyze this social transcript for new slang: {{RAW_DATA}}

**YAML output:** term, meaning_2025, cultural_significance, authenticity_check.

---

### Optional — Platform Strategist + Daily Editorial Manifest

**System:** You are a Digital Media Strategist. Contrast Gen Z (mobile-first, authenticity) vs Gen Alpha (AI-native, immersive, gamified). Evaluate Authenticity vs Pandering. For Daily Manifest: synthesize research into 5 story angles with Magnetic Hook, Data Backbone, Authenticity Filter, Multi-Modal Suggestion.

**YAML output:** primary_platform, format_recommendation, engagement_hook; or daily_editorial_manifest with top_stories.

---

## 9. Qwen3 run details

- **llama.cpp:** `./llama-cli -hf Qwen/Qwen3-14B-GGUF:Q8_0 --jinja --color -ngl 99 -fa -sm row --temp 0.6 --top-k 20 --top-p 0.95 --min-p 0 --presence-penalty 1.5 -c 40960 -n 32768`
- **Ollama:** `ollama run hf.co/Qwen/Qwen3-14B-GGUF:Q8_0`
- **Thinking pass:** Use `/think` in user message; temp 0.6, top_p 0.95.
- **YAML pass:** Use `/no_think`; temp 0.3–0.5; prompt “Output only valid YAML…”
- **Long context:** Optional `--rope-scaling yarn --rope-scale 4 --yarn-orig-ctx 32768` for 131k tokens. For reliability, keep dimension analysis within ~32K token chunks.

---

## 10. Provenance

Every artifact must include a header:

```yaml
# provenance
run_date: YYYY-MM-DD
model: Qwen3-14B-GGUF
prompt_id: "<layer_or_task_id>"
source: reasoning | yaml_pass
```

---

## 11. References

- Source docs: `continue_gen_research.rtf`, `continue_gen_research2.rtf`
- Plan: Generational Deep Research — Merged Spec and Implementation Plan (gen_research_merged_spec_and_plan)
- Feed config: [config/research/youth_feed_sources.yaml](../config/research/youth_feed_sources.yaml), [RESEARCH_FEED_SOURCES.md](RESEARCH_FEED_SOURCES.md)
