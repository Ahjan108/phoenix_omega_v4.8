# Title and Catalog Marketing System

**Purpose:** Single system reference for audiobook title philosophy, catalog marketing rules, title generation engine, and the full 24-brand catalog.  
**Audience:** Content, marketing, pipeline, release.  
**Authority:** Ops manual (templates, imprints, validation rules); [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) (invisible_script, belief flip); deep research brief (keyword/subtitle, consumer language).  
**Last updated:** 2026-02-26

---

## 1. Title philosophy (four goals)

A Phoenix title must do four things:

| Goal | Meaning |
|------|--------|
| **Search keyword ownership** | Title owns a search keyword the persona actually types; consumer language, not internal slugs. |
| **Invisible script** | Names the reader's hidden operating belief before they've named it; "precisely called out, not vaguely inspired." |
| **Brand voice** | Word choice carries imprint/brand (Calm vs Edge vs Rise vs Root) without stating the brand name. |
| **Locale when applicable** | For city-specific editions, the location name (e.g. NYC, LA, SF/Bay/Silicon Valley, Chicago, Boston, DC) appears in the title. |

- **US universal:** For `market=us` with no city, no location in title.  
- **US city-specific:** When a book is pinned to a city, the city (or persona-flavor phrase, e.g. "in Silicon Valley" for SF + tech persona) is guaranteed in the title.

---

## 2. Deep research integration

Three sources define how titles should behave:

- **Hooks / invisible script (all_deep_research_omega, Integration Spec):**  
  - Invisible script = name the hidden belief.  
  - Belief flip = counter-intuitive reframe in the language.  
  - Persona-specific invisible scripts (e.g. NYC Executive, Healthcare Worker, Gen Z) are title-caliber seeds; the **invisible_script** HOOK subtype in [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) should feed naming, not only in-book hooks.

- **Marketing brief (deep_research_deepseek_marketing):**  
  - **"Titles own a search keyword; subtitles signal the persona."**  
  - Consumer language vs clinical; culture-specific topic language (e.g. involution anxiety, age-35 career crisis).

- **Writer / Identity & Self-Worth family:**  
  - Observer-author voice; no motivational cliché; topic-specific framing (e.g. grief never "How to Feel Confident").

**Synthesis:** A good Phoenix title = (1) owns a search keyword, (2) names an invisible script, (3) carries brand voice. Raw slugs (e.g. "at work", "sudden loss") and placeholders ("for Readers") are invalid.

---

## 3. Ops manual dimensions (title and catalog)

From the audiobook ops manual:

- **11 book templates:** Phoenix Drop, Morning Weapon, Somatic Rescue, Identity Claim, Quiet Protocol, Silent Authority, Relationship Repair, Money Mirror, Micro Reset, Night Dissolve, Habit Engine — each with runtimes, price points, conversion profiles. Titles and catalog are template-aware.
- **4 imprints:** Calm, Edge, Rise, Root — distinct templates, personas, visual identity; 24 brands map to these imprints.
- **Validation rules:**  
  - Any two titles must differ by **≥3 words**.  
  - **No formulaic repetition:** no single structural pattern across >5 titles.  
  - **Subtitle must not repeat title words.**  
  - **Max 2 keywords in title, 2 in subtitle** (no stuffing).  
- **Release waves:** Seed Wave = 50–75 Phoenix Drop first; then depth/premium/volume/scale. Catalog is wave-tagged.
- **Category distribution:** No single category >15% of catalog; category_id per book with caps.
- **Compliance:** Safe vs flagged terms by topic (e.g. no "anxiety disorder", "PTSD", "trauma therapy", "clinical" in consumer-facing title/subtitle where prohibited).
- **Localization tiers:** Tier 1 (NYC, LA, Chicago), Tier 2 (SF, Seattle, Austin, Houston), Tier 3 (Miami, Boston, Denver, DC, Atlanta); personas and templates qualify per tier.

---

## 4. US cities (when location appears)

For **US market**, location is omitted unless the book is **city-specific**. The supported **US cities** are:

- **NYC** (New York)  
- **LA** (Los Angeles)  
- **San Francisco / Bay Area / Silicon Valley** (persona-aware: e.g. tech_finance_burnout → "Silicon Valley", entrepreneurs → "Bay Area", gen_z → "San Francisco")  
- **Chicago**  
- **Boston**  
- **DC** (Washington DC)

When `city` is set (e.g. `--city nyc`), the title must include the locale phrase (e.g. "New York", "NYC", "in NYC") per engine behavior.

---

## 5. Title engine (v2 → v4)

- **v2:** Rich vocabulary banks, persona/topic/brand; no template/imprint/wave; no ops-manual validation.  
- **v3:** System-aligned dimensions (canonical topics, round-robin); still no full ops-manual rules.  
- **v4 (current):**  
  - **Template-aware allocation** (11 templates), **imprint mapping** (4 imprints), **release_wave**, **category_id** with caps.  
  - Validation: 3-word minimum difference, no pattern >5x, **no subtitle–title word overlap**, keyword limits, compliance filter.  
  - **1,008 unique titles** for full US catalog; brand voice and persona in every title/subtitle.

**Implementation:** See `phoenix_title_engine.py`, `phoenix_title_engine_v3.py`, and the v4 engine (e.g. `phoenix_title_engine_v4.py` or equivalent in repo). CLI supports `--market`, `--city` for city-specific US titles.

---

## 6. Full 24-brand catalog (1,008 books)

- **Dimensions:** 24 brands × 15 topics × 10 personas; round-robin and constraints produce **1,008 books** for the US full catalog.  
- **No assembly:** Catalog build can be **plan-only** (BookSpec/title generation only, no compile/assembly) via e.g. `generate_full_catalog.py` with appropriate flags (e.g. `--plan-only`).  
- **Per-book record fields (example):** `book_id`, `template_id`, `imprint_id`, `brand_id`, `topic_id`, `persona_id`, `series_id`, `angle_id`, `category_id`, `release_wave`, `title`, `subtitle`, `search_keyword`, `invisible_script`, `market`, `locale_name`, `city`, `primary_channel`.

---

## 7. Where to read more

| Area | Doc |
|------|-----|
| System architecture and pipeline | [docs/SYSTEMS_V4.md](SYSTEMS_V4.md) |
| Catalog planning and full catalog script | [docs/SYSTEMS_V4.md §4](SYSTEMS_V4.md), [scripts/generate_full_catalog.py](../scripts/generate_full_catalog.py) |
| Deep research (invisible_script, belief_flip) | [specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) |
| Book title/subtitle in pre-intro | [docs/INTRO_AND_CONCLUSION_SYSTEM.md](INTRO_AND_CONCLUSION_SYSTEM.md) |
