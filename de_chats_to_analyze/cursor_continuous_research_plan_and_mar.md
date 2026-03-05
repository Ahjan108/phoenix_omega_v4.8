# Continuous research plan and marketing resources
_Exported on 3/5/2026 at 17:53:34 GMT+8 from Cursor (2.5.25)_

---

**User**

i need to have a continuous deep reseach plan happening in github. 

what's a continuouse research plane we can use with this: [Google Gemini offers a free tier for its API, but it's limited and not ideal for heavy deep research workloads. Deep Research, the agentic feature for multi-step web browsing and analysis, is available via the Gemini API (now part of the Interactions API powered by models like Gemini 3.1 Pro), following a pay-as-you-go pricing model based on compute usage rather than being fully free.

]. for gen z and gen alpha infor for pearl_news stuff

for marketing stuff is there free marking feeds or sources for audiobooks sales help? 

---

**Cursor**


Exploring the codebase to understand the project structure, pearl_news, and any existing research or marketing setup so we can draft a continuous deep-research plan that fits Gemini's constraints and your goals.



Checking ML/research workflows and Pearl News writer spec for Gen Z/Gen Alpha.



Creating a plan that ties together continuous research in GitHub, Gemini constraints, Pearl News Gen Z/Gen Alpha needs, and free audiobook marketing sources.


---

**User**

new plan. no gemini. I have qwen in github: Qwen3-14B-GGUF is a powerful quantized model from the Qwen3 series, excelling in reasoning, agent tasks, multilingual support (100+ languages), and mode-switching between thinking (for logic/math/coding) and non-thinking (for chat). Since you want to disable tool use entirely, we'll focus on prompting it locally via llama.cpp or Ollama to simulate internet searches and website info extraction purely through clever system/user prompts—no external APIs or functions.

## Local Setup Without Tools
Run it tool-free with your existing GGUF files:
- **llama.cpp**: `./llama-cli -hf Qwen/Qwen3-14B-GGUF:Q8_0 --jinja --color -ngl 99 -fa -sm row --temp 0.6 --top-k 20 --top-p 0.95 --min-p 0 --presence-penalty 1.5 -c 40960 -n 32768`
- **Ollama**: `ollama run hf.co/Qwen/Qwen3-14B-GGUF:Q8_0`
This keeps everything offline, using the model's internal knowledge (trained up to mid-2025 cutoff).

## Simulating Web Searches via Prompts
Instruct Qwen3 to "search" its knowledge base like a search engine. Use `/think` for detailed reasoning or `/no_think` for quick summaries. Example system prompt:

```
You are a web search engine simulator. For any query, respond as if searching the internet: List top 3-5 "results" with made-up but realistic URLs/titles/snippets based on your training data (up to 2025). Then summarize key facts with citations like [web:1]. Never claim real-time access. Query: {user_query}
```

User example: "Latest on AI agents" → It outputs simulated results like " arxiv.org/ai-agents-2025 → Summary of trends..." [qwenlm.github](https://qwenlm.github.io/qwen-code-docs/en/developers/tools/web-search/)

For multi-turn: Add `/think` mid-convo for deeper "research."

## Website Info Extraction Prompts
Paste website text/content into prompts (copy-paste manually since no fetching). Example prompt for analysis:

```
<website_content>{paste full text or key sections here}</website_content>
Analyze this webpage: Extract main facts, summarize in 200 words, list key entities, and answer: {your_question}. Use thinking mode if complex. /think
```

This leverages Qwen-Agent-like reasoning (built into Qwen3) without actual tools—great for your audiobook/TTS workflows or nonprofit data processing.

## Best Prompt Tweaks for Your Use
- Thinking mode: `--temp 0.6 --top-p 0.95 --presence-penalty 1.5`
- Non-thinking: `--temp 0.7 --top-p 0.8`
- Long context: Add `--rope-scaling yarn --rope-scale 4 --yarn-orig-ctx 32768` for 131k tokens (e.g., full scraped sites).
- Chain prompts: "First simulate search on X, then extract from this pasted content Y."

This keeps it fully local, disable-tools compliant, and taps Qwen3's agent strengths for your Python/automation needs in Tainan. Test with strawberries riddle to verify modes!

---

**Cursor**


Creating a revised plan that uses only local Qwen3 (llama.cpp/Ollama), no Gemini: prompt design for search simulation and paste-and-extract, and how to run it continuously from GitHub.



Creating a new plan that uses only local Qwen3 (no Gemini): search-simulation prompts, paste-and-extract workflow, and how it fits into GitHub.


---

**User**

look at continue_gen_research.rft and continue_gen_research2.rft editor1 :[I reviewed the two documents you uploaded. Here is a **clear architectural analysis** of what they contain, what is strong, what is weak, and what you should change if your goal is **true generational deep research for Pearl News**.

I will reference them directly so you can trace the analysis.

---

# 1. Overall Assessment

Your system design is **very advanced conceptually**.

It is essentially proposing a:

**Generational Intelligence Engine**

rather than a simple research tool.

The architecture combines:

* sociological modeling
* psychological modeling
* narrative analysis
* platform intelligence
* editorial generation

That is **far more sophisticated than normal media pipelines**.

The core idea is described well:

> the system interprets news through identity-centered milestones, generational traumas, and invisible scripts. 

This is exactly the correct framing if you want to cover **Gen Z and Gen Alpha news properly**.

However there are **three major structural problems**.

---

# 2. Major Structural Problem #1

## Overly complex architecture

The system currently proposes:

* multiple Qwen models
* recursive chains
* sociological frameworks
* narrative intelligence
* platform intelligence
* six research dimensions
* editorial synthesis layers

This is **intellectually impressive but operationally fragile**.

You do **not need six dimensions** to produce good generational research.

In practice you only need **three core intelligence layers**:

### Layer 1 — Generational Psychology

How the generation thinks.

### Layer 2 — Life Problems & Aspirations

What they struggle with and want.

### Layer 3 — Event Impact

How world events affect them.

Everything else should support these three.

---

# 3. Major Structural Problem #2

## Excessive prompt complexity

Many prompts in the system are **too academic**.

Example:

> apply the Proppian Formula and archetypal audit to detect narrative homogenization. 

This is interesting but unnecessary.

What you actually want is:

**youth interpretation of events**

Example:

* how do Gen Z interpret Gaza war
* how do Gen Z interpret AI job threats
* how do Gen Z interpret climate change

The system should focus on **real-world interpretation**, not literary theory.

---

# 4. Major Structural Problem #3

## The pipeline is missing real youth signals

Your architecture focuses heavily on:

* RSS feeds
* academic sources
* news sources

But Gen Z narratives actually come from:

| Platform         | Importance     |
| ---------------- | -------------- |
| TikTok           | extremely high |
| Reddit           | high           |
| YouTube comments | high           |
| Discord          | medium         |
| Instagram        | medium         |

Without these signals the system will miss **90% of youth conversation**.

---

# 5. What the System Gets Very Right

Despite the issues, several things in the design are **excellent**.

---

## A. The Generational Lens

This is exactly correct:

> world events are filtered through invisible scripts that shape identity formation. 

That insight is crucial.

Example:

Same event:

| Event   | Gen Z reaction       | Gen Alpha reaction |
| ------- | -------------------- | ------------------ |
| AI jobs | fear of displacement | opportunity        |
| War     | activism identity    | digital exposure   |

Your system should always analyze events through this lens.

---

## B. YAML structured outputs

Very smart design.

Structured outputs allow:

* trend tracking
* editorial generation
* longitudinal analysis

Example structure from the file:

```yaml
psychology_dimension:
  target_cohort: GenZ
  identity_dynamics:
  resilience_profile:
```

This is the right direction.

---

## C. GitHub research memory

The pipeline idea is strong.

Your repo becomes a **generational intelligence database**.

Example structure described in the doc:

```
data/
  artifacts/
    psychology/
    pain-points/
    world-events/
    narrative/
    platform/
```

This allows **longitudinal generational research**.

---

# 6. The Best Simplified Architecture

Instead of the current complex system, the best architecture is:

```
feeds + social media
        ↓
Qwen extraction
        ↓
3 intelligence layers
        ↓
datasets
        ↓
story generation
```

---

# 7. The Three Core Research Dimensions (Your Real Goal)

You originally asked for:

1 psychology
2 problems/aspirations
3 world event impact

That is correct.

Below is the **clean research model**.

---

# Dimension 1 — Generational Psychology

You want to understand:

* identity formation
* emotional states
* trust in institutions
* relationship with technology

Example output:

```yaml
generation_psychology:

  GenZ:
    dominant_emotions:
      anxiety: high
      anger: medium

    identity_drivers:
      activism
      self-expression
      financial independence
```

---

# Dimension 2 — Problems and Aspirations

Identify what they struggle with.

Example:

```yaml
youth_problem_map:

  mental_health:
    - anxiety
    - burnout
    - loneliness

  economic:
    - housing costs
    - unstable careers
```

Aspirations:

```yaml
youth_aspirations:

  career:
    - creative entrepreneurship
    - digital independence

  lifestyle:
    - freedom
    - flexible work
```

---

# Dimension 3 — World Event Impact

Analyze how events affect them.

Example:

```yaml
event_impact:

  event: Gaza War

  direct_effects:
    - campus protests

  psychological_effects:
    - moral outrage
    - anxiety

  identity_effects:
    - activism identity
```

---

# 8. The Missing Intelligence Layer

Your system should also track **youth narratives**.

Example:

```yaml
youth_narratives:

  gaza_war:
    - humanitarian crisis
    - colonialism debate
    - campus activism

  ai_jobs:
    - automation fear
    - entrepreneurial opportunity
```

This is what drives article engagement.

---

# 9. Editorial Output

Your pipeline should generate **story briefs**.

Example:

```yaml
story_angle:

  title: Why Gen Z Feels Personally Connected to the Gaza War

  hook:
    activism identity

  emotional_driver:
    moral outrage

  platform_strategy:
    TikTok explainer
```

---

# 10. Final Strategic Insight

Your system is actually building something rare:

**A generational intelligence engine.**

Instead of:

```
news → article
```

you will have:

```
world events
      ↓
generation psychology
      ↓
identity impact
      ↓
story angles
```

That is **a completely different kind of journalism**.

---

# 11. The Single Biggest Improvement I Recommend

Add **narrative detection from youth conversations**.

Without this, your system will miss:

* activist narratives
* identity conflicts
* cultural framing

Which is where **Gen Z news actually lives**.

---

If you want, I can also show you **the intelligence-agency style generational analysis framework** (used by geopolitical analysts).

It breaks generations into **12 psychological dimensions** and would make your Pearl News system dramatically deeper.
]. editor 2: Let me read both files first.Good — I have both. Here's my honest comparison:

---

**File 1 (continue_gen_research.rtf) — Gemini's output**
**File 2 (continue_gen_research2.rtf) — Second version (also Gemini)**

Both are strong but they excel in different areas. Here's the breakdown:

---

## What File 1 does better

**The prompts are more immediately usable.** The "Psych-Pulse Researcher," "Econ-Script Analyst," and "Semantic Trend-Spotter" prompts have tight, specific system instructions with clear persona definitions. They're ready to copy-paste into Qwen today.

**The concept of "vibration points"** — intersections where a world event triggers a generational trauma — is a genuinely sharp editorial framework that doesn't appear in File 2.

**The linguistic dimension (Dimension 3)** is unique to File 1 and valuable. Tracking "brainrot," "slop," and semantic drift as a dedicated research dimension gives Pearl News a real vocabulary edge over mainstream outlets.

**The "Social Trivialization" concept** — tracking when youth struggles get meme-ified and romanticized — is a sharp editorial alert system no one else is monitoring.

---

## What File 2 does better

**The three-tier architecture (Ingestion → Contextual Triangulation → Synthesis) is superior** and more implementable. Using smaller Qwen 7B for signal detection, mid-size for comparison, and large model for synthesis is smart resource management your dev will appreciate.

**The chaining logic is more explicit.** "Longitudinal Contrast," "Script Deconstruction," "Contradiction Audit," "Historical Resonance Chaining" — these are concrete patterns your dev can actually code, not just describe.

**The "Contradiction Audit"** in Dimension 2 is gold — where a cohort's behavior contradicts their stated fears (spending on luxury while fearing poverty). That tension IS the story every time.

**"Persona Switching"** in Dimension 3 — analyzing the same event from a Gen Z male in a high-income country vs. a Gen Alpha child in a conflict zone — directly serves Pearl News's global angle.

**The GitHub folder structure** in File 2 is more complete and production-ready.

---

## What both miss that my earlier research added

Neither file has the **two-pass architecture fix** for Qwen's known bug where thinking mode breaks YAML output. This is a real technical problem your dev will hit immediately — use thinking mode for analysis, non-thinking mode for structured output generation.

Neither has the **RSS feed source list** with specific URLs for youth-focused feeds (UNICEF, Pew, Teen Vogue Politics, etc.).

Neither addresses **Qwen's censorship problem** for politically sensitive topics like Gaza — which is literally Pearl News's core coverage area.

---

## The synthesis recommendation

**Build with File 2's architecture, populate it with File 1's prompts.**

Specifically:
- Use File 2's three-tier pipeline and chaining patterns as the technical backbone
- Drop File 1's Dimensions 1-5 prompts into that architecture — they're sharper
- Add File 1's linguistic dimension as a **7th dimension** not in File 2
- Add my earlier research's two-pass YAML fix and RSS source list
- Keep File 2's "Contradiction Audit" and "Persona Switching" as mandatory elements in every analysis prompt

Want me to merge the best of all three into one final master document your dev can build from directly? thier work is at: continue_gen_research3.md

---

**Cursor**


Locating and reading the three files to incorporate the editor analyses and the synthesis doc into the plan.


)
   - YAML outputs throughout

2. **File 2 (continue_gen_research2.rtf):**
   - Three-chain: Ingestion (7B signals) → Contextual Triangulation (mid-size, compare to baselines) → Synthesis (Max)
   - Six dimensions with different framing: Psychology/Identity, Pain Points/Economic, World Event Trauma, Narrative Intelligence (Proppian, archetypal), Platform/Content Intelligence, Daily Story Angle
   - Chaining: Longitudinal Contrast, Script Deconstruction, Contradiction Audit, Historical Resonance, Persona Switching, Cross-Platform Triangulation
   - Folder structure: data/raw, data/artifacts (psychology, pain-points, world-events, narrative, platform, manifests), engine/prompts, schemas, scripts
   - YAML validation turn (smaller model), knowledge injection template (current date + recent headlines)

Editor 1's recommendations:
- Simplify to 3 core layers: Generational Psychology, Life Problems & Aspirations, Event Impact
- Reduce prompt complexity (drop Proppian/archetypal for "youth interpretation of events")
- Add real youth signals: TikTok, Reddit, YouTube comments, Discord, Instagram
- Keep: generational lens, YAML outputs, GitHub research memory
- Add: youth narratives (gaza_war, ai_jobs, etc.), story briefs

Editor 2's recommendations:
- Build with File 2's architecture (three-tier pipeline, chaining)
- Populate with File 1's prompts (sharper)
- Add File 1's linguistic dimension as 7th
- Add two-pass YAML fix (thinking for analysis, non-thinking for YAML output) and RSS source list
- Keep Contradiction Audit and Persona Switching as mandatory

I'll update the Local Qwen3 plan to incorporate:
1. Simplified three intelligence layers (Psychology, Problems/Aspirations, Event Impact) + optional 4th (Youth Narratives) and optional 5th (Linguistic) from File 1
2. File 2's pipeline backbone: Ingestion → Contextual Triangulation → Synthesis (with Qwen3-14B single model, or 7B/14B/Max if they have multiple)
3. File 1's prompts (Psych-Pulse, Econ-Script, Semantic Trend-Spotter, etc.) adapted for local Qwen3
4. Two-pass fix: /think for analysis, then non-thinking for YAML output
5. Contradiction Audit and Persona Switching in prompts
6. Youth signal sources: document TikTok, Reddit, YouTube, Discord, Instagram (and RSS list)
7. Folder structure from File 2 aligned with phoenix_omega (artifacts/research/...)
8. continue_gen_research3 as the master doc (create continue_gen_research3.md as the merged spec)

I'll create an updated plan that merges the two RTFs with both editors' feedback and the existing local Qwen3 plan.
`</think>`
Having reviewed both RTF files and the two editors' feedback: no `continue_gen_research3.md` exists (only `continue_gen_research3.textClipping`). Creating an updated plan that merges File 1's prompts, File 2's architecture, both editors' recommendations, and the local Qwen3 (no Gemini) setup.



Creating an updated plan that merges the two RTF specs with both editors' feedback and the local Qwen3 setup.


---

**User**

Generational Deep Research — Merged Spec and Implementation Plan

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**


Implementing the plan step by step. Checking existing to-dos and the codebase.



Creating the master spec document.



Summary of what was implemented:

**1. Master spec — [docs/research/continue_gen_research3.md](../docs/research/continue_gen_research3.md)**  
- Single generational-research spec: 3 core layers (Psychology, Problems/Aspirations, Event Impact) plus optional Narrative, Linguistic, Platform.  
- Pipeline: Ingestion → Contextual Triangulation → Synthesis; two-pass YAML; Contradiction Audit and Persona Switching; youth signal sources; folder layout; Qwen3 run details and provenance.

**2. Prompts — [research/prompts/](research/prompts/)**  
- **system/:** `psych_pulse_researcher.txt`, `econ_script_analyst.txt`, `identity_conflict_researcher.txt`, `semantic_trend_spotter.txt`, `platform_strategist.txt`, `theory_lens_researcher.txt`.  
- **tasks/:** `psychology_task.txt`, `psychology_yaml_instruction.txt`, `pain_points_task.txt`, `pain_points_yaml_instruction.txt`, `event_impact_task.txt`, `event_impact_yaml_instruction.txt` (with Contradiction Audit and Persona Switching).  
- **schemas/README.md** for YAML schema references.

**3. Run script — [scripts/research/run_research.py](scripts/research/run_research.py)**  
- Two-pass: Pass 1 calls Ollama with `/think`, writes `*_reasoning.md`; Pass 2 calls with `/no_think` and YAML instruction, writes timestamped `.yaml` with provenance.  
- Args: `--prompt-id` (psychology | pain_points | event_impact), `--paste` (file or `-` for stdin), `--model`, `--skip-yaml-pass`, `--out-dir`.  
- [scripts/research/README.md](scripts/research/README.md) documents usage.

**4. Feed config and docs**  
- [config/research/youth_feed_sources.yaml](config/research/youth_feed_sources.yaml): RSS (e.g. UNICEF, UN Youth) and platform list (TikTok, Reddit, YouTube, Discord, Instagram).  
- [config/research/marketing_feed_sources.yaml](config/research/marketing_feed_sources.yaml): APA, PW, Spotify, Library Journal.  
- [docs/research/RESEARCH_FEED_SOURCES.md](../docs/research/RESEARCH_FEED_SOURCES.md): Youth + marketing sources and how to use them.  
- [docs/MARKETING_FREE_SOURCES.md](docs/MARKETING_FREE_SOURCES.md): Free audiobook/marketing sources.

**5. Ingest workflow — [.github/workflows/research_feeds_ingest.yml](.github/workflows/research_feeds_ingest.yml)**  
- Weekly (Monday 12:00 UTC) + `workflow_dispatch`. Runs [scripts/research/fetch_feeds.py](scripts/research/fetch_feeds.py) to fetch RSS from `youth_feed_sources.yaml` into `artifacts/research/raw/<date>/` and uploads artifact (14-day retention).

**6. Artifacts layout — [artifacts/research/](artifacts/research/)**  
- Subdirs with `.gitkeep`: `raw/`, `youth_feed_snapshots/`, `psychology/`, `pain_points/`, `world_events/`, `narrative/`, `platform/`, `manifests/`, `marketing_sources/`.  
- [artifacts/research/README.md](artifacts/research/README.md) describes each dir.

**7. Continuous research plan — [docs/research/CONTINUOUS_RESEARCH_PLAN.md](../docs/research/CONTINUOUS_RESEARCH_PLAN.md)**  
- Describes local Qwen3-only setup, two-pass flow, youth signal sources, where everything lives, and options for running continuously (scheduled ingest, local cron, self-hosted runner).

**8. DOCS_INDEX**  
- New generational and research docs added under “Marketing & deep research (document all)”.

---

**User**

document everything use @docs/DOCS_INDEX.md 

---

**Cursor**


Reading DOCS_INDEX.md to understand its structure and add any missing entries for the new research assets and other undocumented items.



Reading the Marketing & deep research section and the rest of the inventory to add the generational research assets.



Adding the generational research subsection (prompts, scripts, config, artifacts, workflow) and inventory entries.



Summary of what was added to **docs/DOCS_INDEX.md**:

**1. Marketing & deep research (document all)**  
- **New subsection: “Generational research (Pearl News)”**  
  - **Prompts:** `research/prompts/system/` (6 persona files), `research/prompts/tasks/` (6 task + yaml_instruction files), `research/prompts/schemas/README.md`  
  - **Scripts:** `scripts/research/run_research.py`, `scripts/research/fetch_feeds.py`, `scripts/research/README.md`  
  - **Config:** `config/research/youth_feed_sources.yaml`, `config/research/marketing_feed_sources.yaml`  
  - **Artifacts:** `artifacts/research/` (dirs + README)  
  - **Workflow:** `.github/workflows/research_feeds_ingest.yml`  

- **Scripts / code table:** Generational research runner, Research feed fetcher.  

- **Use flow:** Step 5 for generational research (local Qwen3, two-pass, optional feed ingest).  

- **Domain-specific subsections table:** Marketing row updated to include generational research (prompts, scripts, config, artifacts, research_feeds_ingest).  

**2. Document all — complete inventory**  
- **Docs:** `continue_gen_research3.md`, `CONTINUOUS_RESEARCH_PLAN.md`, `RESEARCH_FEED_SOURCES.md`, `MARKETING_FREE_SOURCES.md`  
- **Config:** `config/research/youth_feed_sources.yaml`, `config/research/marketing_feed_sources.yaml`  
- **Workflows:** `.github/workflows/research_feeds_ingest.yml`  
- **Scripts & code:** `scripts/research/run_research.py`, `scripts/research/fetch_feeds.py`, `scripts/research/README.md`  
- **Root & other:** `artifacts/research/README.md`, `research/prompts/schemas/README.md`  

**3. Video pipeline**  
- Pipeline scripts row updated to include `run_flux_generate.py` (FLUX T2I for image bank).  

**4. Last updated**  
- Set to 2026-03-05 with a short note that generational research and the full inventory were updated.

