# Pearl News Youth-Signal Capture Pipeline

**Purpose:** Practical system for gathering provenance-tagged youth-interpretation evidence so article writers can legitimately use meaning-layer language ("Gen Z is framing this as...", "students are saying...") per the Generational Writer Spec §6.
**Authority:** Implements requirements from [PEARL_NEWS_GENERATIONAL_INTELLIGENCE_TECH_SPEC.md](./PEARL_NEWS_GENERATIONAL_INTELLIGENCE_TECH_SPEC.md) §4 (Youth-Signal Sourcing Contract) and [PEARL_NEWS_GENERATIONAL_WRITER_SPEC.md](./PEARL_NEWS_GENERATIONAL_WRITER_SPEC.md) §6 (Provenance Honesty in Writing).
**Date:** 2026-03-10

---

## 1. The problem

Pearl News articles need three provenance tiers to write at full power:

| Tier | Provenance kinds | What it unlocks in writing |
|------|-----------------|---------------------------|
| **Institutional** | `rss_news`, `official_report`, `survey_data` | Event facts, policy impact, material youth effect |
| **Secondary youth** | `secondary_report` | Attributed youth data ("Deloitte found that 46% of Gen Z..."), survey contradictions, behavioral statistics |
| **Direct youth** | `platform_native`, `manual_research_capture` | "Gen Z is saying...", "students are framing this as...", behavior loops observed in the wild, platform-specific interpretation patterns |

Without Tier 3, the writer is stuck in institutional voice. The article sounds like a UN brief, not Pearl News.

---

## 2. Three capture channels

### Channel A: Survey-mined youth voice (secondary_report)

**What it is:** Large-scale surveys that include verbatim youth quotes and behavioral contradiction data.

**Priority sources (updated annually):**

| Source | Sample size | Countries | Cadence | Youth quotes? |
|--------|-----------|-----------|---------|---------------|
| Deloitte Gen Z & Millennial Survey | 23,482 | 44 | Annual (May) | Yes — open-ended + qualitative interviews |
| Morning Consult Gen Z Tracker | Ongoing panel | US primary | Monthly | Behavioral data, framing patterns |
| Pew Research Gen Z Reports | Varies | US + global | Quarterly | Some verbatim |
| Yale Climate Communication | 20,000+ | US | Bi-annual | Emotional register data |
| UNICEF Changing Childhood | 21,000 | 21 | Periodic | Yes — verbatim youth voice |
| Gallup Global Youth | Varies | 140+ | Annual | Limited verbatim |
| Cabinet Office Youth White Paper (Japan) | National | Japan | Annual | Behavioral data |
| CASS Youth Reports (China) | National | China | Periodic | Limited |

**Capture method:**
1. When a Pearl News topic is assigned (climate, mental_health, education, etc.), search for the latest survey from these sources that covers that topic
2. Extract: (a) headline statistic, (b) behavioral contradiction, (c) any verbatim youth quote, (d) sample size and methodology
3. Tag as `secondary_report` with `reliability: high`

**What this unlocks:** "According to Deloitte's 2025 survey of 14,751 Gen Z respondents, 46% have received a formal mental health diagnosis — yet 44% said their ideal career includes being a content creator." This is a provenance-honest contradiction that creates article energy.

### Channel B: Platform-native capture via browser (platform_native)

**What it is:** Direct observation of how Gen Z discusses events on their platforms. Not scraping — reading.

**Priority platforms:**

| Platform | Best for | How to access | Signal quality |
|----------|---------|---------------|----------------|
| Reddit r/GenZ, r/teenagers, r/ClimateActionPlan | Framing language, contradictions, lived reality | Browser — sort by relevance to topic | High — long-form, self-identified cohort |
| YouTube comments | Emotional register, reaction patterns | Browser — top comments on relevant videos | Medium — less curated than Reddit |
| TikTok | Trend language, behavior loops, humor as coping | Browser — search by hashtag | High for cultural signal, low for depth |
| Discord | Niche communities, education/work channels | Requires server access | High when available |

**Capture method:**
1. For each article topic, open the browser and search 2–3 platforms
2. Find 3–5 posts/comments where Gen Z users discuss the event or its implications in their own language
3. Record: (a) platform, (b) subreddit/hashtag/channel, (c) paraphrased framing pattern (not verbatim copy), (d) approximate engagement (upvotes, likes), (e) date observed
4. Tag as `platform_native` with `reliability: medium`

**What this unlocks:** "On r/GenZ, the top-voted response to the Surgeon General's warning label proposal was not about mental health — it was about hypocrisy: users framing the advisory as adults who created the problem now telling kids to fix it." This is a genuine youth-interpretation signal that no institutional report captures.

**Privacy and ethics rules:**
- Never quote a specific user by username
- Paraphrase framing patterns; do not copy posts verbatim
- Report the pattern, not the person
- If a post is clearly from a minor, do not reference it at all
- Label provenance honestly — `platform_native` with platform name

### Channel C: Operator paste (manual_research_capture)

**What it is:** The human operator (you, Nihala) pastes in observations from platforms you browse naturally.

**Format:**

```yaml
- signal_type: manual_research_capture
  platform: tiktok
  topic: climate
  date_observed: "2026-03-10"
  summary: "Multiple creators framing the 1.5C breach as 'we knew and they lied' — anger directed at institutions, not despair"
  engagement_level: "high — 500k+ views across 3 creators"
  reliability: medium
  operator: nihala
```

**What this unlocks:** The richest signal. You see things on platforms daily that no automated system captures. The pipeline just needs a structured way to ingest it.

---

## 3. Research artifact integration

Each capture feeds into the research artifact contract (Tech Spec §3.1):

```json
{
  "youth_narrative_signals": [
    {
      "signal_type": "secondary_report",
      "source_name": "Deloitte 2025 Gen Z Survey",
      "summary": "46% have formal mental health diagnosis; 44% want content creation career",
      "contradiction": "diagnosed anxiety + aspirational digital labor",
      "reliability": "high"
    },
    {
      "signal_type": "platform_native",
      "platform": "reddit",
      "subreddit": "r/GenZ",
      "summary": "top posts frame surgeon general warning as institutional hypocrisy, not health concern",
      "date_observed": "2026-03-10",
      "reliability": "medium"
    },
    {
      "signal_type": "manual_research_capture",
      "platform": "tiktok",
      "summary": "creators framing 1.5C breach as betrayal narrative — 'we knew and they lied'",
      "engagement_level": "high",
      "reliability": "medium",
      "operator": "nihala"
    }
  ]
}
```

---

## 4. Writer unlocks by provenance tier

| What the writer can write | Required minimum provenance |
|--------------------------|---------------------------|
| "The WHO reported..." | `rss_news` or `official_report` |
| "46% of Gen Z respondents said..." | `secondary_report` with named source |
| "Gen Z is framing this as..." | `platform_native` OR `manual_research_capture` |
| "Students are saying..." | `platform_native` with platform named |
| "On TikTok, the dominant reaction was..." | `platform_native` with `platform: tiktok` |
| "The contradiction is visible online: ..." | `platform_native` with contradiction field |
| Behavior loop ("students plan around heat before homework") | `platform_native` OR `secondary_report` with behavioral data |
| Fabricated anecdote ("At 22, Priya deleted her alarm") | **NEVER** — use cohort pattern language instead |

---

## 5. Practical workflow per article

### Before writing starts:

1. **Topic assigned** (e.g., "climate" + "WMO 2025 hottest year")
2. **Institutional layer** — the RSS feed or news source is already in the pipeline
3. **Secondary youth layer** — search for the latest Deloitte/Pew/Yale/Morning Consult data on this topic. Extract 2–3 data points + any contradiction. Tag `secondary_report`. **Time: 5 minutes.**
4. **Platform-native layer** — open browser, search Reddit (r/GenZ + r/ClimateActionPlan) and TikTok (#climateanxiety, #1point5) for how Gen Z is framing the event. Record 3–5 framing patterns. Tag `platform_native`. **Time: 10 minutes.**
5. **Operator paste layer** — if you (Nihala) have seen relevant content on your own feeds, paste it in `manual_research_capture` format. **Time: 2 minutes.**

### Total additional time per article: ~15 minutes
### What it unlocks: The full meaning layer — the article sounds like Pearl News, not a UN brief.

---

## 6. Where it lives in the pipeline

### New directory:
```
artifacts/research/generational_intelligence/
  ├── climate_genz_en_20260310.json
  ├── mental_health_genz_en_20260310.json
  └── ...
```

### Pipeline integration point:
In `pearl_news/pipeline/llm_expand.py`, the expansion prompt's user message block (lines 223–281) currently includes:
- event facts
- teacher atoms
- framing question

**Add after teacher atoms:**
- `youth_narrative_signals` (from the research artifact)
- `contradiction_or_tension` (from the research artifact)
- `story_brief` (from the research artifact)

This gives the LLM the youth-signal evidence it needs to write meaning-layer prose without inventing it.

---

## 7. Validation gate additions

### New gate: `youth_signal_provenance`

**Fails if:**
- Article contains "Gen Z is saying..." or "students are framing..." language AND the research artifact has no `platform_native` or `manual_research_capture` entries
- Article implies platform-native observation ("on TikTok, the reaction was...") without a matching `platform_native` signal

### New gate: `contradiction_grounded`

**Fails if:**
- Article states a generational contradiction without a source — either survey data or platform observation
- Contradiction is editorial inference not tagged as such

### Add to: `pearl_news/pipeline/quality_gates.py`

```yaml
youth_signal_provenance:
  enabled: true
  severity: hard_fail
  description: "Meaning-layer claims require platform_native or manual_research_capture provenance"

contradiction_grounded:
  enabled: true
  severity: warn
  description: "Generational contradictions must be sourced from survey or platform evidence"
```

---

## 8. What this means for the 5 article types

| Template | Primary signal source | What changes in the writing |
|----------|----------------------|---------------------------|
| **Hard News** | Secondary survey data for the youth-impact paragraph | One contradiction sentence grounded in Deloitte/Pew data. Platform signal optional. |
| **Youth Feature** | Platform-native + operator paste | The opening shifts from fabricated anecdote to observed cohort behavior pattern. Reddit/TikTok framing patterns anchor the narrative. |
| **Commentary** | Secondary + platform for the thesis energy | The thesis gets sharper because the contradiction comes from data, not editorial instinct. Platform signals show how Gen Z actually interprets the event differently from the mainstream. |
| **Explainer** | Secondary survey for the "why this cohort interprets it differently" question | The meaning layer is grounded in named survey data. The question the tradition asks is sharpened by what the survey reveals. |
| **Interfaith** | Secondary + optional platform | Youth commitments section gets anchored to real behavioral data and at least one platform framing pattern. |

---

## 9. Implementation order

1. **Create the research artifact directory** (`artifacts/research/generational_intelligence/`)
2. **Build one research artifact by hand** for the next article topic — all three tiers
3. **Add the `youth_narrative_signals` block** to the expansion prompt in `llm_expand.py`
4. **Add the two new quality gates** to `quality_gates.py`
5. **Run one article** with the full pipeline and verify the meaning layer is provenance-honest
6. **Create a reusable capture template** (YAML) for operator paste so it's fast

---

## 10. The bottom line

The difference between "Pearl News sounds like a UN brief" and "Pearl News sounds like it was written for Gen Z" is exactly this pipeline. Fifteen minutes of research per article — searching one survey source and two platform sources — unlocks the full meaning layer that the Generational Writer Spec demands.

Without it, the writer is guessing what Gen Z thinks. With it, the writer is reporting what Gen Z is actually saying, with provenance tags that make the quality gates happy and the reader trust the voice.
