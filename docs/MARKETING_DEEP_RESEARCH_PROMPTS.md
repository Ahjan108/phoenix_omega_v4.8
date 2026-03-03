# Marketing Deep Research Prompts

**Purpose:** One-to-many deep research prompts to fill Phoenix marketing planning gaps.  
**Use:** Run each prompt (or the master) through your deep research workflow; output feeds brand registry, title engine, persona metadata, and content briefs.  
**Last updated:** 2026-03-03

---

## Master Prompt (spawns all sub-research)

```
Do deep research to produce a complete marketing intelligence brief for a multi-brand self-help audiobook publisher (Phoenix) launching 1,008 titles across 24 brands on Google Play, Spotify, and Audible in 2025–2026.

Scope: US market, English-language, self-help/wellness/mental fitness categories. Target personas: burned-out professionals, high-efficiency achievers, insomniacs, mid-career stalled, neurodivergent young adults, working parents, Gen X sandwich, Gen Z professionals, healthcare RNs, first responders, entrepreneurs, corporate managers.

Produce research outputs for ALL of the following sub-topics. Each sub-topic should be a self-contained research deliverable with sources, data, and actionable recommendations:

1. **Per-brand GTM & audience funnel** — For each of 24 brand archetypes (nervous system regulation, sleep repair, ADHD/focus, career transition, grief, burnout, boundaries, etc.): who is the primary buyer, what moment triggers purchase, which discovery channels (Google Play search, Spotify recommendations, YouTube clips) drive conversion, and what keyword clusters (primary + secondary) they actually search. Include search volume estimates where available.

2. **Controlled emotional vocabulary** — Which emotional trigger words in self-help audiobook titles drive conversion vs. trigger spam detection? Map high-performing words by topic (burnout, anxiety, sleep, focus, grief, boundaries) and by audience. Include: "reset," "calm," "clarity," "grounded," "release," "safety," "momentum," "regulation," and 15–20 more. For each: conversion signal, platform risk, recommended quota (global max, per-brand max, release cadence).

3. **Consumer language vs. clinical** — How do self-help buyers phrase their problems in search vs. how clinicians/therapists phrase them? Map consumer search language to topics: anxiety, burnout, overthinking, imposter syndrome, sleep anxiety, financial stress, grief, boundaries, somatic healing. Include culture-specific phrases (e.g., involution anxiety, Sunday scaries, age-35 career crisis). Output: consumer-language keyword list per topic, banned/clinical terms to avoid in titles.

4. **Persona × topic invisible scripts** — For each persona (NYC executive, healthcare worker, Gen Z, working parent, entrepreneur, corporate manager, first responder, etc.) and each topic (anxiety, burnout, boundaries, grief, etc.): what is the hidden operating belief the reader holds before they've named it? One sentence per persona×topic. Format: "You've [X] before you've [Y]" or equivalent. These feed title philosophy and HOOK atoms.

5. **Duration bands & consumption behavior** — What duration do self-help audiobook listeners actually prefer in 2025–2026? Micro-sessions (15–30 min) vs. mid-form (45–90 min) vs. deep dives (3–6 hr). By use case: commute, gym, wind-down, Audible credit. Include completion rates, perceived value, and platform-specific behavior (Google Play vs. Audible vs. Spotify). Recommend allocation % per format type.

6. **Cover design language by audience** — What cover art styles, color palettes, and visual cues convert for each audience segment (burnout, focus/ADHD, sleep, career, grief, relationships)? Minimalist vs. bold typography vs. abstract shapes. Include platform thumbnail requirements and what gets clicked vs. ignored.

7. **Pricing topology & discount psychology** — Tiered pricing for micro / mid / deep formats. Google Play bundle rules (15/25/35% off). What discount ratios and price points maximize conversion without devaluing? Include competitor benchmarks for self-help audiobooks.

Cite sources. Output in structured format (YAML or JSON) where possible for direct ingestion into config.
```

---

## Sub-Prompts (run individually if needed)

### 1. Per-brand GTM & audience funnel

```
Do deep research on go-to-market and audience discovery for 24 self-help audiobook brand archetypes in the US market (2025–2026). For each brand type below, identify:

- Primary buyer persona (demographics, psychographics, moment of need)
- Emotional job and functional job (JTBD)
- Discovery channels that drive conversion (Google Play search, Spotify, YouTube, etc.)
- Primary and secondary keyword clusters with search intent
- Funnel stages: awareness → consideration → purchase

Brand types: nervous system regulation, somatic reset, sleep repair, panic first aid, emotional resilience, grief companion, gentle recovery, inner security, breathwork, focus training, ADHD systems, dopamine balance, habit building, clarity/decision, high efficiency, energy return, movement flow, metabolic stability, boundaries, attachment repair, communication clarity, Gen Z anxiety, identity rebuild, shadow work.

Output: structured GTM brief per brand with sources. Format suitable for brand_archetype_registry gtm_identity and discovery_contract fields.
```

---

### 2. Controlled emotional vocabulary

```
Do deep research on emotional trigger words in self-help audiobook titles: which words drive conversion vs. trigger platform spam detection (Google Play, Audible, Spotify) in 2025–2026?

For each word, provide:
- Conversion performance signal (high / medium / low / unknown)
- Platform risk (safe / monitor / flagged / banned)
- Recommended quota: global max across 1,008 titles, per-brand max, minimum release gap (weeks)
- Topic affinity (burnout, anxiety, sleep, focus, grief, boundaries, etc.)

Words to analyze: reset, calm, clarity, grounded, regulation, safety, release, momentum, focus, discipline, rest, repair, anchor, steady, flow, clarity, choice, unstuck, repair, restore, reclaim, rewire, regulate, settle, soothe, trust, enough, worthy, seen, held, supported.

Also identify: words that are currently overused (saturation risk) and words that are underused but high-converting (opportunity).
```

---

### 3. Consumer language vs. clinical

```
Do deep research on how self-help audiobook buyers phrase their problems in search vs. clinical/therapeutic language. Map consumer search queries to these topics:

- anxiety, burnout, overthinking, imposter syndrome, sleep anxiety, financial stress, grief, boundaries, somatic healing, depression, compassion fatigue, courage, self-worth, social anxiety

For each topic:
1. Top 10–15 consumer search phrases (how real people type)
2. Clinical terms to AVOID in consumer-facing titles (e.g., "anxiety disorder," "PTSD," "trauma therapy")
3. Culture-specific or generation-specific phrases (e.g., involution anxiety, Sunday scaries, age-35 career crisis, quiet quitting, burnout culture)
4. Subtitle patterns that signal persona ("for overthinkers," "when you can't sleep," etc.)

Output: consumer-language keyword list per topic, banned terms list, persona-signaling subtitle patterns. Format for title engine and compliance filter.
```

---

### 4. Persona × topic invisible scripts

```
Do deep research to produce "invisible script" statements for self-help content. An invisible script names the reader's hidden operating belief before they've consciously named it—one precise sentence that creates recognition.

For each combination of persona and topic, write ONE invisible script statement. Personas: millennial_women_professionals, tech_finance_burnout, entrepreneurs, working_parents, gen_x_sandwich, corporate_managers, gen_z_professionals, healthcare_rns, gen_alpha_students, first_responders. Topics: anxiety, burnout, boundaries, grief, overthinking, imposter_syndrome, sleep_anxiety, financial_stress, compassion_fatigue, self_worth, somatic_healing, social_anxiety, courage, depression.

Format: "You've [X] before you've [Y]" or "You learned to [X] before you learned to [Y]" or equivalent. Must be specific to persona + topic, not generic. Examples:
- NYC Executive × anxiety: "You've optimized everything except the part that's quietly costing you."
- Healthcare Worker × burnout: "You learned to carry everyone else's pain before you learned to carry your own."
- Gen Z × anxiety: "You've spent so long performing okayness that you've lost track of what okay actually feels like."

Output: YAML or table with persona_id, topic_id, invisible_script. 10 personas × 14 topics = 140 statements. Skip combinations that don't make sense; note why.
```

---

### 5. Duration bands & consumption behavior

```
Do deep research on self-help audiobook listener preferences for duration in 2025–2026. Answer:

1. What duration bands do listeners actually prefer? Micro (15–30 min), mid (45–90 min), deep (3–6 hr)?
2. By use case: commute, gym, wind-down/sleep prep, Audible credit, weekend deep listen
3. Completion rates by duration band
4. Perceived value: do listeners equate longer = better value, or do micro-sessions have higher completion and satisfaction?
5. Platform differences: Google Play vs. Audible vs. Spotify consumption patterns
6. Market bifurcation claim: is the middle (45–90 min) underperforming vs. micro and deep? Cite data.

Output: recommended allocation % for micro_sessions, deep_dives, mid_form across a 1,008-title catalog. Include sources and confidence level.
```

---

### 6. Cover design language by audience

```
Do deep research on audiobook cover art that converts for self-help/wellness audiences in 2025–2026. By audience segment (burnout professionals, focus/ADHD seekers, sleep/anxiety, career transition, grief, relationships):

1. What visual styles convert? (minimalist gradient, bold typography, abstract shapes, dark minimal, geometric anchor, etc.)
2. Color palette preferences by segment
3. What gets clicked vs. ignored on Google Play, Audible, Spotify
4. Platform thumbnail requirements (aspect ratio, text legibility)
5. Trends: what's oversaturated vs. emerging

Output: style_pool and color_palette recommendations per audience/segment. Format for brand_archetype_registry cover_art_identity. Include 2–3 banned styles per segment (what to avoid).
```

---

### 7. Pricing topology & discount psychology

```
Do deep research on pricing and discount strategy for self-help audiobooks on Google Play, Audible, and Spotify (2025–2026).

1. Tiered pricing: what price points for micro (15–30 min), mid (45–90 min), deep (3–6 hr)?
2. Google Play bundle rules: 15%, 25%, 35% off tiers—how do they affect conversion?
3. Discount ratio: what % of catalog should be discounted? 20%? More?
4. Price anchoring: does a higher base price with discount outperform a lower everyday price?
5. Competitor benchmarks: self-help audiobook pricing by format and platform
6. Price sensitivity by audience (burnout vs. ADHD vs. career vs. sleep)

Output: pricing_posture recommendations (micro_sessions range, deep_dives range, discount_ratio) for brand registry. Include Google Play parity constraint (price there ≤ elsewhere).
```

---

## Output locations (after research)

| Research area | Config / artifact to update |
|---------------|----------------------------|
| Per-brand GTM | `config/catalog_planning/brand_archetype_registry.yaml` (gtm_identity, discovery_contract) |
| Emotional vocabulary | `brand_archetype_registry.yaml` emotional_vocabulary, global_constraints; title engine |
| Consumer language | New: `config/marketing/consumer_language_by_topic.yaml`; title engine; compliance filter |
| Invisible scripts | `specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md`; HOOK atoms; title engine seeds |
| Duration bands | `brand_archetype_registry.yaml` duration_strategy |
| Cover design | `brand_archetype_registry.yaml` cover_art_identity |
| Pricing | `brand_archetype_registry.yaml` pricing_posture |

---

## 1. Evidence + provenance block (required)

Every research run **must** produce a provenance block. Attach it to the output artifact (e.g. `artifacts/marketing_research/<prompt_id>_<date>.yaml` or as a header in the deliverable).

```yaml
# REQUIRED — attach to every research output
provenance:
  run_date: YYYY-MM-DD
  model: "e.g. claude-sonnet-4, gpt-4o, deepseek-chat"
  temperature: 0.0  # or value used
  prompt_id: "1"    # sub-prompt number or "master"
  source_links:     # URLs, reports, or citations used
    - "https://..."
    - "Report: [name] (internal)"
  confidence: "high | medium | low"  # overall confidence in findings
  reviewer: "name or TBD"
  notes: ""         # optional: caveats, gaps, follow-up needed
```

**Purpose:** Prevents unverifiable "research drift." If findings are later contradicted or config changes fail, provenance enables audit and re-run.

---

## 2. Decision-to-config contract

For each prompt output, the following contract defines **what may change** and **what must not**. Patch only the allowed fields; never edit canonical IDs or structural keys.

| Prompt | Target file(s) | May update | Must NOT change |
|--------|----------------|------------|------------------|
| **1. Per-brand GTM** | `config/catalog_planning/brand_archetype_registry.yaml` | `gtm_identity.*`, `discovery_contract.*` (persona, age_range, primary_moment, emotional_job, functional_job, primary_channels, keyword_clusters) | `brand_id`, `admin_id`, `structural_signature`, `voice_identity`, `cover_art_identity`, `pricing_posture`, `duration_strategy` |
| **2. Emotional vocabulary** | `config/catalog_planning/brand_archetype_registry.yaml` | `global_constraints.emotional_token_global_caps`, `global_constraints.forbidden_title_tokens`, per-brand `emotional_vocabulary.allowed_tokens`, `emotional_vocabulary.quota_exceptions` | `brand_id`, `admin_id`, `required_fields` |
| **3. Consumer language** | `config/marketing/consumer_language_by_topic.yaml` (new), title engine config | Create new file: `consumer_phrases`, `banned_terms`, `persona_subtitle_patterns` per topic | `config/catalog_planning/canonical_topics.yaml` topic IDs, `canonical_personas.yaml` persona IDs |
| **4. Invisible scripts** | `config/marketing/invisible_scripts_by_persona_topic.yaml` (new), HOOK atom seeds | Create new file: `persona_id`, `topic_id`, `invisible_script` | `unified_personas.md` persona IDs, `canonical_topics.yaml` topic IDs |
| **5. Duration bands** | `config/catalog_planning/brand_archetype_registry.yaml` | `duration_strategy.micro_sessions`, `duration_strategy.deep_dives`, `duration_strategy.mid_form`; `global_constraints.max_mid_form_ratio` | `brand_id`, `admin_id`, sum must = 1.0; mid_form ≤ max_mid_form_ratio |
| **6. Cover design** | `config/catalog_planning/brand_archetype_registry.yaml` | `cover_art_identity.style_pool`, `cover_art_identity.color_palette` | `brand_id`, `admin_id`; no 100% style_pool overlap with another brand (validator) |
| **7. Pricing** | `config/catalog_planning/brand_archetype_registry.yaml` | `pricing_posture.micro_sessions`, `pricing_posture.deep_dives`, `pricing_posture.discount_ratio` | `brand_id`, `admin_id`; discount_ratio ≥ 0.20 (validator) |

**Global rules (all prompts):**
- **Never edit:** `config/catalog_planning/canonical_personas.yaml` persona IDs, `config/catalog_planning/canonical_topics.yaml` topic IDs, `unified_personas.md` structure.
- **Never add/remove:** brand archetypes (24 fixed); required_fields in registry.
- **Always run:** `validate_brand_archetype_registry.py` after any registry patch.

---

## 3. Acceptance gates

Before merging research output into config, all of the following must pass:

| Gate | Check | Owner |
|------|-------|-------|
| **Schema-valid output** | Output conforms to target schema (YAML parses; required fields present; types correct). Run `validate_brand_archetype_registry.py` for registry changes. | Ops |
| **No contradiction with canonical specs** | No conflict with `unified_personas.md`, `BRAND_ARCHETYPE_VALIDATOR_SPEC.md`, `TITLE_AND_CATALOG_MARKETING_SYSTEM.md`. Persona/topic IDs match. | Ops |
| **A/B sanity test passed** | For title/vocabulary changes: generate 10–20 sample titles with new config; human review confirms no spam patterns, no clinical terms, brand voice preserved. | Marketing |
| **Owner sign-off** | Marketing + Ops both approve merge. Provenance block complete (date, model, sources, confidence, reviewer). | Marketing, Ops |

**Checklist (copy before merge):**
```
[ ] Provenance block attached to output
[ ] Schema validation passed
[ ] No canonical spec contradiction
[ ] A/B sanity test passed (if applicable)
[ ] Marketing sign-off
[ ] Ops sign-off
```

---

## Related docs

- [DOCS_INDEX.md](DOCS_INDEX.md) — Full doc index; this file is in [Marketing & deep research (document all)](DOCS_INDEX.md#marketing--deep-research-document-all)
- [TITLE_AND_CATALOG_MARKETING_SYSTEM.md](TITLE_AND_CATALOG_MARKETING_SYSTEM.md)
- [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md)
- [unified_personas.md](../unified_personas.md)
- [config/catalog_planning/brand_archetype_registry.yaml](../config/catalog_planning/brand_archetype_registry.yaml)
