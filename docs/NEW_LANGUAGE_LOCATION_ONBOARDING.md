# New Language / Location Onboarding

**Purpose:** Single, market-driven process and deep research prompts for onboarding a **new language, location, topic, or persona** (or any combination). Ensures writing spec, metadata, marketing, platforms, personas, topics, and authors are researched together and stay interwoven.  
**Authority:** Use this doc whenever adding a new locale, expanding to a new market, or introducing a new persona/topic in an existing locale.  
**Last updated:** 2026-03-04

---

## Status report: framework vs execution

**Looks good structurally, but not automatically 100%.**

| Dimension | Meaning | When it's 100% |
|-----------|--------|----------------|
| **Framework (planning/onboarding)** | Process, prompts, output locations, provenance, gates, and related docs/links. | **100%** when this doc and all linked docs/configs exist in repo as stated and the structure is complete. |
| **Execution (operational completion)** | Real outputs, config merges, and runtime evidence for target locale(s). | **Not 100%** until the evidence below exists. |

**Framework = 100%** ✓ as a planning/onboarding framework if those docs and links are actually in repo as stated.

**Execution = only 100% after evidence.** Operational completion for a given locale requires:

1. **Real per-locale outputs** — Research artifacts produced from all 7 prompts (§3.1–§3.7) for that locale (e.g. in `artifacts/marketing_research/<locale>_*` or equivalent), with provenance blocks.
2. **Config updates merged and passing** — All touched configs (locale_registry, content_roots_by_locale, brand_registry_locale_extension, consumer_language_by_topic, author_registry, etc.) updated from research outputs, merged to main, and passing validators and gates (e.g. `validate_brand_archetype_registry.py`, gate #49).
3. **Runtime evidence** — Catalog runs, metadata/distribution checks, and release evidence for the target locale(s) (e.g. plans generated, locale/territory gate green, export or release checklist run).

**Summary:** Use this doc as the single onboarding framework; treat **framework** as complete when the repo matches the doc. Treat **execution** as complete per locale only when the three evidence items above are done for that locale.

---

## 1. Scope: What “onboarding” means

Onboarding can mean one or more of:

| Dimension | Meaning | Config / artifacts touched |
|-----------|--------|----------------------------|
| **New language/locale** | New locale code (e.g. `pt-BR`, `it-IT`) with its own script, TTS, storefronts | `locale_registry.yaml`, `content_roots_by_locale.yaml`, `brand_registry_locale_extension.yaml` |
| **New location/territory** | New geographic market (same or new language) with its own distribution and discovery | `locale_registry.yaml`, storefront_ids, distribution rules |
| **New topic (in locale)** | New topic or topic-family in a locale; how locals name and search for it | `canonical_topics.yaml` (if net-new), consumer_language, topic_family mapping |
| **New persona (in locale)** | New audience segment for that locale; must tie to topics and brands | `LOCALE_PERSONAS.md`, `canonical_personas.yaml` (if net-new), brand `persona_affinity` |
| **New author (in locale)** | New pen-name/author identity for that locale or brand | `author_registry.yaml`, `author_positioning_profiles.yaml`, author assets |

**Rule:** Everything is **market-driven**. Research must answer: Who are they? What do they search? What do they believe before they’ve named it? What platforms do they use? What words convert vs. trigger filters? Only then do we write spec, metadata, and content.

---

## 2. High-level process

Order is important. Each step consumes outputs of prior steps.

```
1. Market & platform deep research (locale/territory)
       ↓
2. Persona deep research (who, moment of need, invisible scripts)
       ↓
3. Topic & topic-family deep research (consumer language ↔ canonical topics)
       ↓
4. Author & voice deep research (positioning, trust, locale appropriateness)
       ↓
5. Marketing & title deep research (GTM, emotional vocabulary, compliance)
       ↓
6. Writing spec & story deep research (voice, scenarios, forbidden markers)
       ↓
7. Config & spec updates (registry, extension, personas, prompts)
       ↓
8. Validation & gates (schema, locale-persona lock, gate #49)
```

**Dependencies:**

- **Personas** depend on: market (who buys, where), topic resonance (which topics matter in that locale).
- **Topics** depend on: market (what people search), topic families (mapping to our canonical list).
- **Authors** depend on: personas and brands (who they speak for), locale voice norms.
- **Marketing / titles** depend on: consumer language, invisible scripts, persona × topic, platform rules.
- **Writing spec** depends on: persona voice, forbidden markers, locale framing rules (e.g. no “mental health” in ja-JP).

---

## 3. Deep research prompts

Run these in order (or in parallel where no dependency). Each prompt should produce **structured output** (YAML or JSON) and a **provenance block** (see §6). Locale-specific prompts use `{locale}`, `{language}`, `{territory}` placeholders; replace with the target (e.g. `ja-JP`, `Japanese`, `JP`).

---

### 3.1 Market & platform (locale/territory)

**Purpose:** Size the opportunity, choose storefronts, set pricing and distribution constraints. Feeds: `locale_registry.yaml`, `content_roots_by_locale.yaml`, distribution rules, pricing_posture.

```
Do deep research on the self-help / wellness / mental-fitness audiobook and audio market for {territory} in {language} ({locale}) for 2025–2026.

1. **Market size and behavior**
   - Audiobook and podcast consumption (hours per week, titles per year) for self-help/wellness.
   - Demographics: age, income, urban vs rural, device (mobile-first?).
   - Willingness to pay: price bands (local currency) that convert; sensitivity to discounts.

2. **Platforms and storefronts**
   - Which platforms matter: Google Play, Apple Books, Audible (local?), Kobo, Spotify, Findaway, or local-only (e.g. Ximalaya, Naver, Kakao).
   - For each: availability in {territory}, catalog rules, payment, and content policies.
   - Any hard blockers (e.g. Google Play not in mainland China; Findaway does not distribute to CN).

3. **Discovery**
   - Where do listeners discover audiobooks: search, recommendations, social (IG, Line, WeChat, etc.), podcasts, YouTube.
   - Primary keyword language: {language} search behavior; any English mixing in search.

4. **Competition and positioning**
   - Local and international competitors in self-help/wellness audio.
   - Gaps: underserved personas or topics; positioning that resonates (e.g. “nervous system” vs “mental health” in high-stigma markets).

5. **TTS and production**
   - Preferred TTS provider for {locale}: ElevenLabs, Google Neural2, or other. Voice availability and quality for {language}.
   - Any locale-specific requirement (e.g. politeness register in Japanese; Cantonese for zh-HK).

Output: Structured brief suitable for locale_registry and content_roots_by_locale (storefront_ids, distribution_blocker, tts_notes, price_sensitivity, primary_platforms, discovery_channels). Cite sources.
```

---

### 3.2 Persona deep research (locale-specific)

**Purpose:** Define who we speak to in this locale; moment of need, invisible scripts, topic resonance. Feeds: `LOCALE_PERSONAS.md`, `brand_registry_locale_extension.yaml` persona_affinity, topic_resonance per persona.

```
Do deep research to define 3–6 primary audience personas for self-help/wellness audiobooks in {territory} ({locale}, {language}), market-driven and specific to this locale.

For each persona:

1. **Identity**
   - Label (e.g. “burned_out_professional_tw”, “salaryman_burnout_jp”). Demographics and life context (age band, work context, family, geography within {territory}).

2. **Moment of need**
   - When do they search or buy? Trigger events (e.g. panic attack, sleepless streak, career crisis, caregiving overload).
   - Emotional job and functional job (JTBD) in their own words.

3. **Invisible scripts**
   - One to three “hidden operating beliefs” before they’ve named the problem. Format: “You’ve [X] before you’ve [Y]” or equivalent in {language}.
   - Locale-specific beliefs (e.g. filial duty and grief in Taiwan; karoshi and 社畜 in Japan; 躺平 in mainland China).

4. **Topic resonance**
   - Map to our canonical topic list: anxiety, burnout, boundaries, grief, overthinking, imposter_syndrome, sleep_anxiety, financial_stress, compassion_fatigue, self_worth, somatic_healing, social_anxiety, courage, depression.
   - Rank top 5 topics per persona. Note how this locale names those topics (consumer language).

5. **Voice and constraints**
   - Formality level (0–1), slang tolerance, tone (warm, direct, scientific, philosophical).
   - Forbidden markers for this locale (e.g. “mental health” in Japan; “therapy” in high-stigma markets; spiritual language in evidence-only markets).
   - Domain jargon and metaphor styles that resonate (in {language}).

6. **Market data**
   - Rough addressable segment size, primary_platforms, discovery_channels, price_sensitivity, audiobook_consumption.

Output: One structured persona block per persona (YAML-friendly), with persona_id, display_name, locale, territory, topic_resonance (ordered list), invisible_script seeds, voice_tone, formality, forbidden_markers, domain_jargon, market_data. Ensure persona_id matches our naming: {locale_suffix} (e.g. _tw, _jp, _kr).
```

---

### 3.3 Topic & topic-family deep research

**Purpose:** Map how this locale talks and searches about our topic families; consumer language vs clinical; topic-family → canonical_topics. Feeds: `config/marketing/consumer_language_by_topic.yaml` (per locale), title engine, compliance filter, topic_family mapping.

```
Do deep research on how self-help/wellness buyers in {territory} ({locale}, {language}) talk and search about the following topic areas. Map every item to our canonical topic list and to locale-specific consumer language.

Our canonical topics: anxiety, boundaries, burnout, compassion_fatigue, courage, depression, financial_anxiety, financial_stress, grief, imposter_syndrome, overthinking, self_worth, sleep_anxiety, social_anxiety, somatic_healing.

For each canonical topic (and any locale-specific topic that doesn’t map 1:1):

1. **Consumer search language**
   - Top 10–15 phrases people actually type when searching for help (in {language}).
   - Synonyms and colloquial terms; generation-specific or region-specific variants.

2. **Clinical vs consumer**
   - Terms to AVOID in consumer-facing titles and copy (e.g. “anxiety disorder”, “PTSD”, “trauma therapy”, diagnostic labels). List in {language}.

3. **Topic-family mapping**
   - If this locale uses different “topic families” (e.g. “nervous system” as umbrella, or “stress” vs “burnout”), map them to our canonical topics.
   - Any new topic that should be added to canonical_topics for this locale only (or globally if we expand).

4. **Subtitle and persona-signaling**
   - Subtitle patterns that signal “for whom” (e.g. “for overthinkers”, “when you can’t sleep”) in {language}.
   - How to signal persona without being clinical.

Output: Per-topic blocks: canonical_topic_id, consumer_phrases (list), banned_terms (list), topic_family_notes, persona_subtitle_patterns. Format for consumer_language_by_topic with locale key. Include provenance.
```

---

### 3.4 Author & voice deep research

**Purpose:** Decide whether to use existing author positioning or define locale-specific authors; trust posture and voice. Feeds: `author_registry.yaml`, `author_positioning_profiles.yaml`, author assets (bio, why_this_book, pre_intro).

```
Do deep research on author identity and trust for self-help/wellness audiobooks in {territory} ({locale}, {language}).

1. **Trust anchors in this market**
   - What kind of authority converts: lived experience, professional credentials, research-synthesizer, elder/wisdom figure?
   - Any strong aversion (e.g. “coach” vs “therapist”; “scientist” vs “spiritual” in evidence-focused markets).

2. **Pen names and positioning**
   - Do listeners prefer local-sounding names or neutral/international? Examples of successful local authors or narrators in self-help/wellness.
   - How to position “author” for this locale: same author across locales or locale-specific pen names?

3. **Positioning profiles**
   - Map to our profiles: somatic_companion (lived experience, companion), research_guide (research synthesizer), elder_stabilizer (seasoned practitioner). Which profile(s) fit this locale?
   - Any new profile needed (e.g. “cultural bridge”, “peer guide”) and its allowed/forbidden language.

4. **Author-level copy**
   - Tone for bio and “why this book” in {language}: length, formality, vulnerability band.
   - Pre-intro / audiobook intro: duration, register (formal vs casual), any locale taboos.

Output: Recommended positioning_profile(s) per brand or persona; optional new profile definition (authority_type, trust_anchor_style, allowed_language, forbidden_language); locale-specific author copy guidelines. Format for author_registry and author_positioning_profiles.
```

---

### 3.5 Marketing & title deep research (locale)

**Purpose:** GTM, emotional vocabulary, title/subtitle rules, platform compliance. Feeds: `brand_archetype_registry.yaml` (gtm_identity, discovery_contract, emotional_vocabulary), title engine, compliance filter.

```
Do deep research on marketing and titles for self-help/wellness audiobooks in {territory} ({locale}, {language}), 2025–2026.

1. **Per-brand GTM (if we have brand list for this locale)**
   - For each pilot brand: primary buyer persona, moment of need, discovery channels, primary and secondary keyword clusters (in {language}), funnel stages.

2. **Emotional vocabulary**
   - Which emotional trigger words in titles drive conversion vs. trigger platform filters? Words to analyze (translate/localize as needed): reset, calm, clarity, grounded, regulation, safety, release, momentum, focus, rest, repair, anchor, steady, flow, settle, soothe, trust, enough, worthy, seen, held, supported.
   - For each: conversion signal, platform risk (safe/monitor/flagged/banned), recommended quota if applicable.
   - Locale-specific high-converting and banned terms.

3. **Consumer language in titles**
   - Reuse output from Topic & topic-family research: consumer phrases for each topic; banned clinical terms.
   - Title length and structure norms (words, characters) for {language} and key storefronts.

4. **Compliance**
   - Platform-specific rules (Google Play, Apple, Audible, Spotify, local platforms) for {territory}: prohibited words, medical claims, therapeutic claims.
   - Category and keyword stuffing limits.

5. **Pricing and discount**
   - Price bands (local currency) for micro / mid / deep formats; discount psychology; bundle rules if applicable.

Output: gtm_identity and discovery_contract per brand; emotional_vocabulary with allowed_tokens and forbidden_title_tokens; pricing_posture; compliance notes. Format for brand_registry_locale_extension and brand_archetype_registry. Ensure no conflict with TITLE_AND_CATALOG_MARKETING_SYSTEM.md.
```

---

### 3.6 Writing spec & story deep research

**Purpose:** Voice, scenario library, forbidden markers, story patterns. Feeds: Writer spec, HOOK atoms, persona scenario_library, rewrite_config, format_rules.

```
Do deep research to define writing and story guidelines for self-help/wellness content in {territory} ({locale}, {language}).

1. **Voice and register**
   - Narrative “voice” that fits this locale: formality, directness, use of “you” vs “we”, warmth vs authority.
   - Pace and rhythm expectations (e.g. faster in “빨리빨리” cultures; more reflective in philosophical markets).
   - Breathing and exercise frequency in audio: acceptable range for this audience.

2. **Scenario library (persona × topic)**
   - For each persona and topic combination that we will serve: 5–10 concrete scenarios (situations, moments, environments) that feel real in this locale. Use local detail (place, ritual, work context).
   - These feed story injection and HOOK atoms; must be recognizable and non-generic.

3. **Invisible scripts and hooks**
   - Refine invisible script statements from Persona research into one-sentence hooks (in {language}) that can appear in HOOK atoms and title philosophy.
   - Belief flip: counter-intuitive reframe that fits this culture.

4. **Forbidden markers**
   - Expand from Persona research: words, themes, and tones to avoid (e.g. toxic positivity, clinical labels, spiritual claims in secular markets, gendered or culturally insensitive phrasing).
   - Format_rules: any locale-specific structural rules (e.g. no “next chapter” language; no crisis hotline auto-insert).

5. **Story and metaphor**
   - Narrative patterns that work: personal story vs. parable vs. research-backed. Metaphor styles (e.g. system/overload, container/overflow, anchor/ground) in {language}.
   - What feels authentic vs. imported or tone-deaf.

Output: rewrite_config (style_notes, forbidden_markers, title_rules) per persona; scenario_library per persona × topic; invisible_script and belief_flip seeds; format_rules addendum for locale. Format for Writer Spec and LOCALE_PERSONAS persona blocks.
```

---

### 3.7 Platforms, metadata & distribution (locale)

**Purpose:** Storefront-specific metadata, categories, keywords, ASIN/ID handling. Feeds: distribution pipeline, metadata templates, gate #49.

```
Do deep research on platform and metadata requirements for audiobook distribution in {territory} ({locale}, {language}).

1. **Storefront metadata**
   - For each platform (Google Play, Apple Books, Audible, Kobo, Spotify, Findaway, and any local platforms): required and optional fields (title, subtitle, author, narrator, description, category, keywords, length, language code).
   - Character limits for title, subtitle, description. Category trees for self-help/wellness/mental fitness in {language}.

2. **Keywords and discoverability**
   - How search works on each platform (keyword-based, algorithmic). Best practices for {language} keywords; stuffing limits.
   - Local category names and how they map to our internal categories.

3. **Distribution rules**
   - Which storefronts accept {locale} content; territory restrictions; any “book locale must match storefront” rule.
   - Handling of multiple languages (e.g. bilingual description or separate editions).

4. **Identifiers**
   - ASIN, ISBN, or other ID requirements per platform for {territory}.
   - Narrator and author name display rules.

Output: Metadata schema per platform (required fields, max lengths, category IDs); keyword and category mapping; distribution_rules addendum for locale_registry. Ensure consistency with gate #49 (locale/territory consistency).
```

---

## 4. Output locations (config and artifacts)

| Research area | Primary config / artifact | May update | Must NOT change |
|---------------|---------------------------|------------|----------------|
| Market & platform | `config/localization/locale_registry.yaml`, `content_roots_by_locale.yaml` | New locale entry: language, region, script, TTS, storefront_ids, distribution_blocker, notes | Existing locale keys; schema_version |
| Personas | `docs/LOCALE_PERSONAS.md`, `brand_registry_locale_extension.yaml` | New persona blocks; persona_affinity, topic_coverage per brand | en-US canonical persona IDs in canonical_personas.yaml (unless adding net-new global persona) |
| Topic & topic-family | `config/marketing/consumer_language_by_topic.yaml` (per locale), topic_family mapping | consumer_phrases, banned_terms, persona_subtitle_patterns, locale key | canonical_topics.yaml topic IDs (unless adding net-new topic globally) |
| Author & voice | `config/author_registry.yaml`, `config/authoring/author_positioning_profiles.yaml` | New author entries; new profile if needed | Structural contract of author_registry |
| Marketing & title | `config/catalog_planning/brand_archetype_registry.yaml`, `brand_registry_locale_extension.yaml` | gtm_identity, discovery_contract, emotional_vocabulary, pricing_posture per locale brand | brand_id and admin_id; required_fields |
| Writing & story | Writer Spec, `LOCALE_PERSONAS.md` (persona blocks), HOOK seeds | rewrite_config, scenario_library, format_rules, invisible_script seeds | Core Writer Spec structural rules |
| Platforms & metadata | `locale_registry.yaml` distribution_rules, metadata templates (in pipeline) | storefront_ids, distribution_blocker; metadata schema docs | Gate #49 logic (locale/territory consistency) |

---

## 5. Process checklist (execution order)

Use this when onboarding a **new locale** (language + location). For only a new topic or persona in an existing locale, run the relevant subset.

- [ ] **1. Add locale to registry**  
  Add entry to `locale_registry.yaml` (language, region, script, TTS, storefront_ids, distribution_blocker). Add entry to `content_roots_by_locale.yaml` (atoms_root, translation_source_locale, rollout_phase, notes).

- [ ] **2. Run Market & platform deep research (§3.1)**  
  Output: locale and content_roots updates; distribution and pricing notes.

- [ ] **3. Run Persona deep research (§3.2)**  
  Output: LOCALE_PERSONAS.md section; persona_ids for this locale.

- [ ] **4. Run Topic & topic-family deep research (§3.3)**  
  Output: consumer_language_by_topic for this locale; topic_family mapping.

- [ ] **5. Run Author & voice deep research (§3.4)**  
  Output: author_registry and author_positioning_profiles if new authors; profile recommendations.

- [ ] **6. Run Marketing & title deep research (§3.5)**  
  Output: brand_registry_locale_extension (GTM, pricing, emotional vocabulary) for new locale brands.

- [ ] **7. Run Writing spec & story deep research (§3.6)**  
  Output: persona rewrite_config, scenario_library, invisible_script seeds; Writer Spec addendum.

- [ ] **8. Run Platforms, metadata & distribution (§3.7)**  
  Output: metadata schema and distribution_rules; confirm gate #49 compatibility.

- [ ] **9. Add locale brands**  
  Add brands to `brand_registry_locale_extension.yaml` with locale, territory, persona_affinity, topic_coverage, gtm_identity, voice_identity, pricing_posture. Use naming: `{brand_name}_{locale_suffix}`.

- [ ] **10. Validate**  
  Run `validate_brand_archetype_registry.py` (if applicable); run gate #49 (locale/territory consistency); schema validation on all touched YAML.

---

## 6. Provenance and acceptance gates

**Provenance block (required for every research run):**

Attach to each research output (e.g. in `artifacts/marketing_research/<locale>_<prompt_id>_<date>.yaml` or as header in the deliverable).

```yaml
provenance:
  run_date: YYYY-MM-DD
  model: "e.g. claude-sonnet-4, gpt-4o"
  temperature: 0.0
  prompt_id: "3.2"   # section number from this doc
  locale: "ja-JP"    # or target locale
  source_links: []
  confidence: "high | medium | low"
  reviewer: "TBD"
  notes: ""
```

**Acceptance gates before merging:**

| Gate | Check | Owner |
|------|--------|------|
| Schema-valid | All YAML parses; required fields present; types correct. Run validators. | Ops |
| No canonical conflict | Persona/topic IDs match canonical_personas.yaml and canonical_topics.yaml (or doc why net-new). | Ops |
| Locale-persona lock | Brands for locale X only reference personas tagged for X (LOCALE_PERSONAS). | Ops |
| Gate #49 | locale and territory consistent for distribution; no cross-storefront mismatch. | Ops |
| A/B sanity (titles) | For title/vocabulary changes: generate 10–20 sample titles; human review for spam and brand voice. | Marketing |
| Sign-off | Marketing + Ops approve; provenance complete. | Marketing, Ops |

---

## 7. Related docs

- **[MARKETING_DEEP_RESEARCH_PROMPTS.md](MARKETING_DEEP_RESEARCH_PROMPTS.md)** — US/English master and sub-prompts; extend with locale-specific runs from this doc.
- **[LOCALE_PERSONAS.md](LOCALE_PERSONAS.md)** — Authority for locale-specific personas; add new locale sections from §3.2 output.
- **[LOCALE_CATALOG_MARKETING_PLAN.md](LOCALE_CATALOG_MARKETING_PLAN.md)** — Catalog and brand rollout per locale.
- **[del_location_plan/locale_strategy.md](../del_location_plan/locale_strategy.md)** — One brand = one locale; rollout phases; distribution routing.
- **[TITLE_AND_CATALOG_MARKETING_SYSTEM.md](TITLE_AND_CATALOG_MARKETING_SYSTEM.md)** — Title philosophy, validation rules, deep research integration.
- **Config:** `config/localization/locale_registry.yaml`, `content_roots_by_locale.yaml`, `brand_registry_locale_extension.yaml`; `config/catalog_planning/canonical_topics.yaml`, `canonical_personas.yaml`; `config/author_registry.yaml`, `config/authoring/author_positioning_profiles.yaml`.
