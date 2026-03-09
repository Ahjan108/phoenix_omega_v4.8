# Catalog Architecture at Scale

**Purpose:** Operational guidance so platforms see **many independent publishing programs**, not one automated content network. Applicable when targeting high annual volume (e.g. 10k–30k+ books/year across many brands).

**Status:** Risk heuristic and operational checklist. Treat as **guidance**, not confirmed platform policy—unless you have direct policy text, do not assume every claim is guaranteed platform behavior.

**Related:** [specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md](../specs/TEACHER_PORTFOLIO_PLANNING_SPEC.md) §13 (scale stance), [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md) (velocity and rollout).

---

## 1. Principle

Large publishers that release tens of thousands of books per year use a different catalog shape than typical indie or single-pipeline systems:

> **Platforms must see many independent publishing programs, not one automated content network.**

The safest structural rule:

- **Many editorial programs, few books per program** — not few brands with massive output per brand.

---

## 2. Editorial program layer (brand ≠ program)

A **program** is a semi-independent line with its own:

- Editorial theme
- Authors / teachers
- Release schedule
- Narrator pool (audio)
- Metadata style (title grammar, description tone)

**Target hierarchy:**

```
publisher network
   └── brand
          └── editorial program
                 └── series
                        └── book
```

Example:

```
Stillness Press (brand)
   Mindfulness Classics (program)
      Calm Mind Series (series)
         Book, Book, Book
```

**Phoenix implementation:** **Editorial program is a first-class planning key** (`program_id`). It is resolved in the teacher portfolio planner from `config/catalog_planning/editorial_programs.yaml` (teacher domain: which program a teacher belongs to per brand), attached to every allocation and BookSpec, and carried through the pipeline into the compiled plan. Downstream can use `program_id` for metadata style, narrator pool, and cover style (config supplies optional `metadata_style_family`, `narrator_pool_id`, `cover_style` per program). See **§2a Catalog planner** below.

---

### 2a. Catalog planner: program_id as first-class key

The single highest-impact change for spam-pattern risk at scale is **adding editorial_program as a first-class planning key** in portfolio, recommender, and pipeline metadata. Implemented as follows:

| Layer | What |
|-------|------|
| **Config** | `config/catalog_planning/editorial_programs.yaml` — programs per brand with `theme`, `teachers` (teacher domain), optional `max_books_per_week`, `metadata_style_family`, `narrator_pool_id`, `cover_style`. |
| **Portfolio planner** | `phoenix_v4/planning/teacher_portfolio_planner.py` — `TeacherAllocation.program_id` resolved from (brand_id, teacher_id) via `resolve_program_id()`; fallback `brand_id` when no program config. |
| **Catalog planner** | `phoenix_v4/planning/catalog_planner.py` — `BookSpec.program_id`; `produce_single(..., program_id=...)` passes through. |
| **Full catalog** | `scripts/generate_full_catalog.py` — passes `alloc.program_id` into `produce_single`; spec and compiled plan carry `program_id`. |
| **Pipeline** | `scripts/run_pipeline.py` — compiled plan output includes `program_id` when present in book_spec. |

Downstream (title engine, narrator selection, cover art) can key off `program_id` to apply program-specific metadata grammar, narrator pool, and cover style. This one change reduces spam-pattern risk more than tweaking individual title rules alone.

---

## 3. Teacher distribution across programs

Instead of the same teachers everywhere, use **teacher domains**: each teacher appears in **specific editorial contexts** (programs), not across all brands uniformly.

| Teacher   | Programs (example)     |
|-----------|-------------------------|
| Master Wu | Mindfulness Classics    |
| Sai Maa    | Emotional Healing       |
| Ahjan     | Dharma & leadership    |

Config: `config/catalog_planning/brand_teacher_matrix.yaml` already constrains which teachers belong to which brands. The editorial-program layer would further narrow **which series/program** within a brand each teacher appears in, reinforcing “curated publishing” rather than “algorithmic output.”

---

## 4. Operational checklist (risk heuristic)

Use the following as an **operational checklist** to reduce catalog fingerprint and clustering. These are **risk heuristics**, not confirmed platform policy.

| Area | Guidance |
|------|----------|
| **Metadata diversity** | Different title/description grammar and keyword families per program (or per brand cluster). Avoid one template pattern across the whole catalog. See §14 (metadata uniformity risk); rotate title structures, description frameworks, subtitle styles; config/catalog_planning/metadata_diversity_policy.yaml. |
| **Release staggering** | Stagger by program/day (e.g. Mon: program A, Tue: program B) so the platform does not see “many accounts release same day.” |
| **Cover identity** | Distinct visual system per program (e.g. Zen brush vs modern science vs bold cinematic). |
| **Narrator pool** | Segment narrators/voices by program (calm vs energetic vs warm therapeutic) to avoid voice fingerprint clustering. |
| **Category spread** | Spread across Self-Help, Health & Wellness, Psychology, Religion, Philosophy, Leadership, etc. Avoid concentration in a single category (e.g. >35% in one). |
| **Series architecture** | Prefer series → volumes over many standalone titles; platforms treat series as structured publishing. |
| **Pacing per program** | Cap books per teacher per month, per series per month, per program per week (e.g. max_books_per_teacher_per_month: 10, max_books_per_series_per_month: 8, max_books_per_program_per_week: 5). |

Do **not** treat every item as guaranteed platform behavior; use as defensive design and audit triggers.

---

## 5. Strongest actionable: four hard caps and audits

The most actionable steps are to implement **hard caps and audits** for these four areas (not just per-brand guards, but **network-level** where relevant):

| # | Area | What to implement |
|---|------|-------------------|
| 1 | **Cross-network teacher share** | Cap the fraction of total allocation from any single teacher across the catalog (or per lane). **Implemented:** `config/catalog_planning/diversity_guards.yaml` → `max_share_per_teacher` (e.g. 8%); enforced in `scripts/generate_full_catalog.py`. |
| 2 | **Title/description template similarity** | Audit and cap reuse of the same title/description template across brands or programs. **Status:** Operational audit / future gate. Track template families per brand/program; fail or warn when similarity exceeds threshold (e.g. same template > N times in one wave or cluster). |
| 3 | **Keyword overlap per brand cluster** | Audit keyword overlap across books in the same brand (or program). **Status:** Operational audit / future gate. Cap shared keywords between titles in a cluster; avoid keyword stuffing and identical keyword sets. |
| 4 | **Same-day multi-account release bursts** | Avoid many accounts releasing on the same day. **Status:** Schedule and process guard. When building the weekly schedule, stagger release days by brand/cohort so the same day does not have a large fraction of all brands releasing; document in release process and optionally enforce in `generate_weekly_schedule.py`. |

Implementing (1) is done; (2)–(4) are required as **caps or audits** (process, config, or script) and should be added to the release and catalog checklist.

---

### 5a. Scale differentiation before volume (worldview)

**The biggest mistake at scale:** scaling generation before scaling catalog differentiation. The catalog then looks algorithmic (same structure, same topics, same metadata) and gets throttled or reviewed.

**Rule:** **Topic overlap, worldview separation.** Many books about the same topic, but each from a **different intellectual lens** (neuroscience, somatic, buddhist, stoic, leadership, etc.). Platforms see separate book ecosystems.

**Implemented:**

- **`worldview_id`** — Required in planning/metadata. Each program has `worldview_id` in `editorial_programs.yaml`; portfolio planner resolves it to every allocation; BookSpec and compiled plan carry it.
- **Diversity cap by worldview** — `diversity_guards.yaml` → `max_share_per_worldview` (e.g. 0.25 = 25%); enforced in `generate_full_catalog.py`.
- **Registry** — `config/catalog_planning/catalog_worldviews.yaml` defines worldview IDs with optional `category_anchor`, `title_grammar_family` for downstream.
- **Downstream** — Generate titles/descriptions per worldview grammar family; distribute categories/keywords by worldview; stagger releases by worldview-program.

---

### 5b. Release topology (wave scheduler, same-day blocker)

Platforms expect **irregular growth** (waves, burst + silence), not constant mass release. Use **distributed release topology** tied to **editorial logic** (programs, series, seasonality), not pure randomness.

**Implemented:**

- **`config/release_velocity/release_scheduler.yaml`** — `weekly_target`, `variance` (variability band, e.g. ±40%); `wave_sizes` (small 2–3, medium 4–6, large 7–10); `brand_days` (which weekdays per brand); **`same_day_cross_brand_max`** (e.g. 3 = block if more than 3 brands release same day).
- **Process:** `generate_weekly_schedule.py` (or downstream) should consume this when fully wired: enforce per-brand/per-program cadence caps, apply variability within guardrails, enforce same-day cross-brand sync blocker.
- **Release-shape KPI (operational):** Track burst score, sync score, topic drift (e.g. dashboard or monthly report); rebalance when drift exceeds threshold.

---

### 5c. Catalog breadth (core / adjacent / niche)

Natural catalogs mix **high-demand**, **related expansion**, and **exploratory/niche** titles. Uniform optimization looks artificial.

**Implemented:**

- **`config/catalog_planning/tier_targets.yaml`** — `tier_targets`: `core_pct: 70`, `adjacent_pct: 20`, `niche_pct: 10`. Optional `topic_tier` mapping (core | adjacent | niche).
- **Enforce** at brand + program + quarterly levels (planning gates or audits).
- **Track** drift and rebalance monthly (operational; not yet automated in code).

---

## 6. Adoptions to use now (practical program layer)

Most useful pieces to adopt:

1. **Brand → Program → Series → Book hierarchy** — Implemented via `program_id` in allocation and BookSpec; config in `editorial_programs.yaml`.
2. **Per-program release caps and staggered calendar** — Config supports `max_books_per_week` per program; schedule/process can stagger by program/day (see RELEASE_VELOCITY_AND_SCHEDULE.md).
3. **Teacher domaining by program** — Each program lists `teachers`; portfolio planner resolves `program_id` from (brand_id, teacher_id). Teachers appear in specific editorial contexts, not everywhere.
4. **Program-specific metadata grammar, narrator pools, cover systems** — Config supports `metadata_style_family`, `narrator_pool_id`, `cover_style` per program; downstream can key off `program_id` when present.
5. **Global pacing caps** — Teacher/program/series caps in `brand_teacher_matrix.yaml`, `diversity_guards.yaml`, and optional per-program `max_books_per_week` in `editorial_programs.yaml`.

---

## 7. How Phoenix compares

**Already in place (more sophisticated than many publishers):**

- Topic and persona diversity (canonical topics/personas, diversity_guards)
- Teacher constraints (max_books_per_topic, max_books_per_persona; brand_teacher_matrix)
- Catalog planner and teacher portfolio planner
- Brand matrix and release velocity caps
- Catalog-wide teacher-share cap (max_share_per_teacher)

- **Editorial program as first-class key** — `program_id` in allocation, BookSpec, and compiled plan; config in `editorial_programs.yaml` with teacher domains and optional style/caps.
- **Worldview** — `worldview_id` on program, allocation, BookSpec; diversity cap `max_share_per_worldview`; `catalog_worldviews.yaml` registry. Title/description grammar and category by worldview.
- **Release scheduler** — `release_scheduler.yaml`: wave sizes, brand_days, same_day_cross_brand_max, variability band.
- **Tier targets** — `tier_targets.yaml`: core 70% / adjacent 20% / niche 10%; enforce at brand+program+quarterly; track monthly.

---

## 8. Safe architecture for scale (target)

For 30k+ books/year, the safer structure is:

```
publisher network
   ├── brand
   │      ├── editorial program
   │      │       ├── series
   │      │       │       ├── book
   │      │       │       ├── book
   │      │       │       └── book
   │      │       └── series …
   │      └── editorial program …
   └── brand …
```

This creates a **natural catalog shape** that mimics curated human publishing. Phoenix already contains most building blocks (portfolio planner, brand matrices, topic/series); the main addition is the **editorial program layer** and the **four hard caps/audits** above.

---

## 9. Volume and catalog legitimacy: operational heuristics only

**Do not treat the following as platform policy or guaranteed thresholds.** They are **operational heuristics** forming an **operating playbook** for normal trade-publishing-like behavior—**not a guaranteed compliance standard**. Use **"lower risk if differentiation is real"**; avoid claiming a structure "does not look like spam" in absolute terms.

### Operating playbook: what to keep

1. **Series progression > many isolated Book 1 launches.** Prefer Series A book 1, 2, 3 then Series B book 1, 2, 3 over many "Book 1" launches at once. Platforms favor series with clear progression; clustered releases improve read-through signals.
2. **Brand segmentation by audience/topic.** Each brand should feel like its own imprint (e.g. Brand A: anxiety/mental wellness, Brand B: productivity, Brand C: mindfulness). Avoid the same topic/series duplicated across every brand.
3. **Distinct metadata, covers, and descriptions per imprint.** Different title/description grammar, cover systems, and keyword families per brand/program. Real series progression, distinct covers, varied topics, consistent brand identity per brand.
4. **Mix of series + standalone is healthy.** 60/40 or 65–75% series / 25–35% standalone is a reasonable mix for nonfiction/self-help (see [config/catalog_planning/series_mix_targets.yaml](../config/catalog_planning/series_mix_targets.yaml)). Full-length books, distinct titles, coherent series, spaced releases.

**Red flags** (checklist, not exhaustive policy): dozens of almost identical titles; keyword-only differences; very short books (e.g. 10–20 pages); mass uploads all on the same day; many Book 1s with no continuation; keyword-stuffed series; multiple brands with identical books (catalog duplication).

### Use with caution

- **Exact percentages and weekly/monthly numbers** (e.g. 6–12/week, 25–40/month, or "safe" volume bands) are **heuristics**, not platform rules. Do **not** treat them as guaranteed compliance thresholds.
- **"Does not look like spam"** → use **"lower risk if differentiation is real"** instead. Risk is lower when metadata, content, and release patterns are diverse and brands are differentiated.
- Our internal caps (e.g. `config/release_velocity/safe_velocity.yaml`) are **guardrails for schedule generation**; they are not confirmed platform thresholds. See [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md).

**Bottom line:** This is useful as an **operating playbook** for structuring catalogs and releases—**not a guaranteed compliance standard**. Lower risk depends on **real differentiation** (metadata, content, release patterns, brand segmentation), not on hitting specific percentages or weekly numbers.

---

## 10. Catalog fingerprint: risk management heuristics

**Top internal QA policy:** **No near-duplicate content/metadata across catalog.** This is the single catalog mistake that gets large publishers suppressed fastest on major stores and distributors—not release volume, not number of titles. Duplicate or near-duplicate content patterns are the primary risk. Platforms run similarity analysis across entire catalogs (text, title, description, chapter structure, metadata). Use this as your **top internal QA policy** and drive detection (CTSS, n-gram, metadata clustering) and advisory alerts from it.

Platforms may analyze catalog-wide patterns (e.g. title similarity, description similarity, series structure, release velocity, author patterns, content length, topic clustering) to form a **publisher fingerprint**. Treat this as **heuristic guidance**, not proven platform internals—we do **not** claim to know how platforms score or weight these signals. Use it as an **internal operating guide** and as input to **internal QA checks and advisory alerts**, not as external policy claims.

### Near-duplicate as primary risk; angle-based differentiation + series as the fix

**What “near-duplicate” means:** Books that look like **variants of the same book**—e.g. same title stem with only audience suffix ("Overcoming Anxiety," "Overcoming Anxiety for Women/Teens/Professionals") and chapters mostly the same. That triggers content-duplication risk. **Safe catalogs** ensure **real conceptual differences** between books: distinct focus, unique description, meaningful content differences. Same topic is fine; same book with a different label is not.

**The fix:** (1) **Angle-based differentiation** — Use **topic angles**, not keyword variants. Each book explores **one angle deeply** (e.g. understanding anxiety, nervous system regulation, cognitive patterns, emotional resilience, lifestyle changes). That produces genuine differences. (2) **Series progression** — Series naturally create unique books; each installment has a distinct place in the reader journey (e.g. Calm Mind Series: Book 1 Understanding, Book 2 Quieting the Inner Alarm, Book 3 Nervous System Reset, Book 4 Rewiring Stress Patterns). Platforms view clear progression as legitimate publishing behavior. (3) **Metadata diversity** — Different hooks, positioning, and description tone per book; avoid the same title/subtitle/description template repeated across many books.

**Simple publisher test:** *"Would a human editor consider these books meaningfully different?"* If yes, the catalog usually passes algorithm checks. Use this as an internal gate for planning and QA.

**Numeric thresholds (e.g. title &lt;40% structural similarity, description ≥70% unique, content 50–60% conceptual difference):** Treat as **internal heuristics** or publisher safeguards only—**not** platform rules or official policy. If you use numeric limits in QA, label them clearly as internal.

### What to operationalize

1. **Near-duplicate detection** — Titles, descriptions, and content. The #1 trigger cited in practice is **near-duplicate books** (e.g. same title stem with only audience suffix; same content). Use structural similarity (e.g. CTSS in `check_platform_similarity.py`), prose/ngram checks, and metadata similarity as **internal QA**; emit **AdvisoryIssue** (info/warn/critical) when risk is elevated. See [docs/CATALOG_GROWTH_AND_ADVISORY_POLICY.md](./CATALOG_GROWTH_AND_ADVISORY_POLICY.md) (advisory, not block by default).
2. **Series continuity checks** — Avoid many orphaned Book 1s (series that never reach Book 2/3). Prefer series progression; use as a planning and audit heuristic. Config: [config/catalog_planning/series_mix_targets.yaml](../config/catalog_planning/series_mix_targets.yaml) (`complete_series_clusters`).
3. **Release staggering** — Stagger uploads across brands/days; avoid mass same-day spikes. Config: `release_scheduler.yaml` (brand_days, same_day_cross_brand_max); [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md).
4. **Brand/topic identity separation** — Each brand/imprint should have distinct focus (audience/topic); distinct metadata, covers, descriptions per brand/program. §9 and §4.
5. **Advisory alerts in UI for fingerprint risk** — Surface **AdvisoryIssue** (e.g. high title/description similarity, many Book 1s in wave, bursty release shape) so operators can review. Practical protection without overclaiming what platform algorithms do.

### Patterns to avoid (heuristic checklist)

- Title keyword permutations (e.g. "How to Stop X Fast / Quickly / Today").
- Description duplication (e.g. 95% identical with one paragraph changed).
- Excessive Book 1s with no Book 2s (fake-series signal).
- Mass upload spikes (e.g. many books same day).
- Multiple brands with identical or near-identical books.

### What healthy looks like (heuristic)

- Title and description **diversity** (theme overlap but structurally different phrasing).
- **Real series progression** (e.g. Book 1, 2, 3, 4).
- **Consistent brand identity** per brand (distinct focus, distinct metadata/covers).

### Catalog risk checklist: seven signals (UI advisory)

Use the following as your **internal catalog risk checklist** and as sources for **UI advisory signals** (AdvisoryIssue). Focus on **pattern quality**, not just volume. Do **not** state that "platforms use X threshold" unless you have a sourced policy; treat all as heuristics. Structuring titles, descriptions, series, and release cadence like a traditional publisher usually reduces risk; platforms tend to flag catalogs whose **patterns look synthetic**.

| # | Signal | What tends to trigger suspicion (heuristic) | How to avoid (operational) | UI advisory |
|---|--------|---------------------------------------------|----------------------------|-------------|
| 1 | **Title pattern repetition** | Title templates with small keyword swaps (e.g. "Stop X Today / Fast / Quickly"). Linguistically nearly identical structure. | Structurally different titles; same theme but different sentence form (e.g. "Quieting the Overthinking Mind," "The Calm Nervous System Method"). | Warn when title similarity in wave/catalog is high. |
| 2 | **Description similarity** | Descriptions that are largely identical across many books (e.g. same paragraphs with one changed). | Unique summaries, different narrative hooks, varied marketing language per book even when topics overlap. | Warn when description similarity exceeds internal QA limit (internal limit only; not a stated platform rule). |
| 3 | **Series without progression** | Many "Book 1" titles with no Book 2/3. Looks like series only for marketing. | Release series in clusters (Book 1, 2, 3); complete_series_clusters. Real reader pathways. | Warn when wave has many Book 1s and few continuations. |
| 4 | **Sudden release spikes** | Large batches in a single day (e.g. many books same day). | Stagger releases across days/brands; natural release rhythm. release_scheduler.yaml, same_day_cross_brand_max. | Warn on bursty release shape. |
| 5 | **Keyword farming topics** | Catalogs built around search permutations (e.g. "X for Women / Men / Teens") with similar content. | Topic ecosystems: same topic from different angles, not just keyword variants. | Advisory when topic/keyword pattern looks permutation-heavy. |
| 6 | **Author identity patterns** | Many authors appearing suddenly; no history; identical metadata patterns across authors. | Consistent author identities; repeated authors across series; coherent author–topic mapping per brand/program. | Optional: advisory when author-catalog pattern is anomalous. |
| 7 | **Content length outliers** | Books that are extremely short (e.g. a few thousand words or 10–20 pages), suggesting mass production. | Typical nonfiction lengths vary by format and genre. Use **genre heuristics** for internal QA (e.g. short vs standard nonfiction word ranges), **not** as hard platform rules. | Warn when many books in wave/catalog fall far below expected length band. |

**Word-count / length:** Treat any numeric ranges (e.g. "short 20k–30k words," "standard 35k–60k words," "audiobook 3–7 hours") as **genre heuristics** for internal QA and advisory signals, **not** as hard rules or confirmed platform thresholds.

**Healthy pattern (summary):** Clear series progression, topic clusters, unique titles, varied descriptions, steady release cadence, realistic book lengths, stable author identities. When those exist, high volume can still look like normal publisher behavior. Use this checklist to drive **internal QA checks and UI advisory signals**; avoid claiming that platforms use these exact criteria or thresholds unless sourced.

### Use with caution

- **Specific numeric thresholds** (e.g. "no more than 30–40% title overlap" or "70–80% unique descriptions") are **not** official platform standards. If used at all, treat as **internal QA limits** or publisher practice, not confirmed policy.
- Do **not** state how platforms "score" or "weight" fingerprint signals; phrase as **risk management heuristics** only.

**Bottom line:** Use catalog-fingerprint concepts for **internal QA checks and advisory alerts** (near-duplicate detection, series continuity, staggering, brand separation, **seven-signal risk checklist**, UI advisories). That gives practical protection without overclaiming how platform algorithms work.

---

## 11. Series Tree: Universe → Family → Series → Book

Large digital publishers (e.g. 5,000–20,000+ titles) often organize catalogs as a **Series Tree** (sometimes called a **Series Universe**). Use this as your **internal architecture pattern** for **lower risk, editorially structured** catalogs—**not** as a claim that the catalog is "algorithm-safe" (we do not guarantee platform outcomes).

### Hierarchy

```
Topic Universe
   ├── Series Family
   │      ├── Series
   │      │      ├── Book
   │      │      ├── Book
   │      │      └── Book
   │      └── Series
   │             ├── Book
   │             └── Book
   └── Series Family
          ├── Series
          └── Series
```

- **Level 1 — Topic Universes:** Major topic domains (e.g. Mental Wellness, Productivity, Relationships, Spiritual Growth, Career Growth). In Phoenix terms these can align with **worldview** or topic clusters; distinct universes support topic authority.
- **Level 2 — Series Families:** Within each universe, families of related series (e.g. Anxiety Family, Burnout Family, Overthinking Family). Semantic clusters that algorithms can interpret as topical coherence.
- **Level 3 — Series:** Each family contains multiple series; typical series length 3–7 books (see [config/catalog_planning/series_mix_targets.yaml](../config/catalog_planning/series_mix_targets.yaml)). Strong read-through signals.
- **Level 4 — Books:** Books sit inside series (and some standalones). Clear progression (Book 1, 2, 3…) supports store recommendation and binge behavior.

### What to keep

- **Release in branch clusters** — Release clusters within a branch (e.g. Calm Mind Series book 1, 2, 3 in one week; then another family/series), not random scatter. Looks like editorial planning, not automation.
- **Cross-series linking** — Interconnect related series (e.g. Calm Mind, Ending Overthinking, Nervous System Reset) via recommendations or metadata so the catalog has internal discovery loops.
- **Series-first with some standalones** — Majority of output in series (65–75%); minority standalone for discovery and SEO. See §9 and series_mix_targets.yaml.

### Scale example (heuristic)

Example shape for a large catalog: **5–8 universes → 20–30 families → 150–300 series → 5,000–10,000+ books**. Exact numbers are **heuristics**; the tree structure is what matters. At ~520 books/year (e.g. 10 books/week, 6 series / 4 standalone), you might grow toward ~5 topic universes, ~20 series families, ~80 series over time—a **mid-size digital publisher ecosystem** shape.

### Implementation

If you implement the Series Tree in **planner metadata** (e.g. `universe_id`, `series_family_id`, `series_id` on allocations/BookSpecs) and in the **release scheduler** (e.g. schedule by family/series branch, cluster releases within a branch), it is a **strong scale model** for editorially structured, lower-risk catalogs. Today Phoenix has **brand → program → series → book**; a Series Tree can map **universe** to worldview or topic cluster, **family** to program or a new config layer, **series** to existing series_id, **book** to plan. No guarantee of platform outcome—**lower risk when structure is editorial and differentiated**.

---

## 12. Angle Matrix: Topic × Angle × Series (anti-duplication engine)

Large publishers scale to 5,000–10,000+ titles without triggering duplication by generating books from **topic × angle combinations**, not from one topic with keyword variants. Each cell is a **distinct editorial concept**. Operationalize as follows.

### 1. Make `angle_id` mandatory in planning and metadata

- **BookSpec** and compiled plan must carry a non-empty **angle_id** (Stage 1 derives from topic+persona+series when not supplied). Contract: [specs/OMEGA_LAYER_CONTRACTS.md](../specs/OMEGA_LAYER_CONTRACTS.md); [config/angles/angle_registry.yaml](../config/angles/angle_registry.yaml).
- Downstream (naming, metadata, similarity index) use **angle_id** so every book has a defined angle.

### 2. Block same (topic + angle) reuse within a recent window unless intentionally sequenced

- Config: [config/catalog_planning/angle_matrix_policy.yaml](../config/catalog_planning/angle_matrix_policy.yaml) → `block_same_topic_angle_within_books` (e.g. 24), `allow_sequenced_reuse: true`.
- **Rule:** Within the last N books (or wave), the same `(topic_id, angle_id)` may not repeat **unless** it is the same series (e.g. Book 2, 3 of same series = intentional sequence). Enforced in catalog generation (e.g. `generate_full_catalog.py`) or as a prepublish check; emit advisory or fail per config.

### 3. Track similarity by (topic + angle) family, not only global

- Similarity index rows include **topic_id** and **angle_id** so we can compute or cap similarity **within** a (topic_id, angle_id) family as well as globally. Reduces false positives and supports angle-based differentiation. Config: `angle_matrix_policy.yaml` → `track_similarity_by_topic_angle_family: true`.

### 4. Use angle-specific title/description templates

- Naming engine and metadata writer should select **title/description template family** by **angle_id** (and optionally program_id/worldview_id). Avoids one template repeated across all books. Config: `angle_registry.yaml`; extend or add `angle_metadata_templates` when needed.

### Weekly pattern for 500–1,000 books/year (heuristic)

- **8–20 books per week**, spread across multiple days, with **series clusters** and **standalone discovery titles**. Example: 5–8 series continuations, 2–4 new series starters, 2–4 standalones per week; rotate across imprints/brands. Treat as **operational guidance**, not platform guarantee. See [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md); caps in `safe_velocity.yaml` are internal guardrails.

---

## 13. Series seeding and read-through acceleration

Stores reward **reader engagement chains** (purchase → completion → next purchase → series continuation). Releasing **multiple books in the same series close together** (e.g. Book 1, 2, 3 within 1–2 weeks) can produce stronger read-through and completion signals than spreading them over many weeks. Treat this as a **likely engagement pattern**, not guaranteed algorithm behavior—do not overstate as confirmed platform logic.

**What’s strong:** Launching series in small clusters (not isolated Book 1s); optimizing for read-through chains; building related series webs (topic clusters so series recommend each other). Audiobook platforms (e.g. Findaway Voices) often see higher completion and listening hours when series are bingeable.

**Implementation:**

1. **Default new series launches to 2–3 books close together.** When starting a new series, release Book 1 + Book 2 (and optionally Book 3) within 1–2 weeks so readers can binge. Config: [config/release_velocity/series_launch_policy.yaml](../config/release_velocity/series_launch_policy.yaml) → `new_series_launch_cluster_min/max`, `new_series_launch_window_weeks`. Planner/scheduler should prefer this pattern when assigning release dates.
2. **Keep the weekly mix:** Continuations (5–8) + few new series cluster books (2–4) + standalones (2–4). Example: Week 1 = Series A book 1–3 + standalone; Week 2 = Series B book 1–3 + standalone; Week 3 = Series A book 4, Series B book 4, Series C book 1–2; etc. Config: `series_launch_policy.yaml` → `weekly_mix_*_target` (advisory).
3. **Cap simultaneous new series starts per brand.** Limit how many distinct series can have a “Book 1” (or new start) in the same week per brand so the catalog doesn’t look synthetic. Config: `series_launch_policy.yaml` → `max_new_series_starts_per_brand_per_week` (e.g. 3). Enforce in schedule generation or as an advisory check.
4. **Use advisory dashboards to confirm read-through before boosting volume.** Trust Signal Score and read-through/completion metrics should inform wave-size or velocity decisions. Do not assume algorithms have picked up the catalog; confirm engagement is improving before increasing output. Config: `confirm_read_through_before_volume_boost: true`.

**Bottom line:** Series seeding (launch with 2–3 books, then continue) + read-through-friendly weekly mix + cap on new series starts per brand + dashboard-led volume decisions. This gives a concrete release pattern without claiming guaranteed algorithm behavior.

---

## 14. Metadata uniformity risk and internal diversity standard

One of the **most common hidden risks** in high-volume publishing on Google Play Books and distributors like Findaway Voices is **metadata pattern uniformity**—not duplication or volume alone. When title structure, subtitle format, descriptions, categories, keywords, and series naming follow **the same structural pattern across hundreds of books**, the catalog fingerprint can look **machine-generated**, even when content is legitimate. **Metadata diversity matters as much as content diversity.** Use this as your **internal architecture standard and QA checklist**, not as external policy claims.

### What platforms may analyze (heuristic)

| Field | What tends to be analyzed |
|-------|----------------------------|
| Title structure | Grammar pattern repetition (e.g. "Verb + Topic + Today" everywhere). |
| Subtitle format | Identical keyword stacking or template. |
| Descriptions | Template reuse (same paragraph shape, same hook type). |
| Categories | Identical BISAC or category usage. |
| Keywords | Repeated keyword clusters. |
| Series naming | Formulaic patterns. |

### Risky vs healthy patterns

**Risky:** Hundreds of titles with one syntax (e.g. "Stop X Today"); descriptions with identical structure (intro → promise → bullets → CTA). **Healthy:** Rotate **multiple metadata styles**—e.g. action titles, concept titles, journey titles, scientific titles, question titles; description frameworks that vary hook type (story, scientific, practical) and paragraph structure. Different sentence types (gerund, noun phrase, verb action) reduce clustering.

### Internal diversity standard (QA checklist)

- **Title structures:** Rotate across several distinct grammar families (e.g. 5–10+). Naming engine and metadata should key off program_id, worldview_id, angle_id so formats vary by imprint and topic angle. Config: [config/catalog_planning/metadata_diversity_policy.yaml](../config/catalog_planning/metadata_diversity_policy.yaml).
- **Description frameworks:** Multiple description templates (e.g. 6–12+ variations) by program/angle; avoid one template repeated across the catalog.
- **Subtitle styles:** Several subtitle styles (e.g. 4–8+); avoid identical format everywhere.

**Caution:** Exact counts (e.g. "6–12 title formats", "8–15 description frameworks") are **internal heuristics** for QA and planning, not platform rules. Use as **internal architecture standard + QA checklist**; do not cite as confirmed platform policy.

### Architecture alignment

The safest structure for large catalogs is **multi-imprint (brands) → topic universes → series families → series → books**, with **topic × angle** as the anti-duplication backbone for each book. This produces topic authority clusters, series progression signals, metadata diversity per imprint, and editorial identity—signals associated with legitimate publishers. See §11 (Series Tree), §12 (Angle Matrix), §2 (editorial program). Typical scale heuristics: 8–15 imprints, 30–60 universes, 600–1,000 series, 5k–20k books; treat ratios as internal guidance only.

---

## 15. Topic expansion and concept_id (10k+ scale)

At 10,000–20,000+ books, **topic exhaustion** is the main practical problem: a flat list of topics (anxiety, stress, burnout, focus, …) yields only 30–50 topics. Large publishers use a **Topic Expansion Framework**: instead of **topic → book**, they use **multiple expansion dimensions** so each book is a distinct **editorial concept**, not a keyword variant.

### Six dimensions (concept design)

| Dimension | Example | In Phoenix |
|-----------|---------|------------|
| Core topic | anxiety, burnout, focus | topic_id |
| Mechanism | nervous system, cognitive, habits, lifestyle | angle_id (or mechanism_id) |
| Situation | work, relationships, parenting, school | angle_id (or situation_id) |
| Audience | young professionals, parents, students | persona_id |
| Depth level | intro, practical, advanced | depth_level (optional on BookSpec) |
| Format | guide, workbook, reflection, science | optional; can be Stage 2 format_structural_id |

A book concept becomes **topic × mechanism × situation × audience × level** (× format when present). This produces thousands of legitimate editorial combinations and avoids both duplication and topic exhaustion.

### Required concept_id in planning

- **concept_id** = deterministic composite of (topic_id, angle_id, persona_id, depth_level). When concept expansion policy is enabled, **concept_id is required** in planning and metadata. It is computed from these dimensions (e.g. `topic_id|angle_id|persona_id|depth_level`) so every book has a unique conceptual slot. Config: [config/catalog_planning/concept_expansion_policy.yaml](../config/catalog_planning/concept_expansion_policy.yaml).
- **Uniqueness window:** Enforce uniqueness of concept_id within a recent window (e.g. last N books) **unless** the repeat is intentional (same series_id = Book 2, 3, …). Prevents catalog cloning; allows series progression. Same policy pattern as topic+angle (§12): `block_same_concept_id_within_books`, `allow_sequenced_reuse`.
- **Series from concept progression:** Series should be built from **concept progression** (Book 1, 2, 3 of the same concept/series), not from keyword variants. concept_id plus series continuity (complete_series_clusters, series_mix_targets) implement this.

### Implementation

- **BookSpec:** Carries `concept_id` (required when policy enabled) and optional `depth_level`. Planner computes concept_id from topic_id, angle_id, persona_id, depth_level (default `"default"` if absent).
- **Uniqueness check:** In catalog generation or prepublish, ensure the same concept_id does not appear twice within the configured window except when the same series_id applies (allow_sequenced_reuse).
- **Scale:** With 30–50 topics × 5–8 mechanisms × 4–6 situations × 3–5 audiences × 3 levels, the system supports **tens of thousands of distinct concepts** before series expansion. This is the right planning model for 10k+ scale.

### Three production controls (Topic Expansion Matrix)

To make topic expansion **operational**, not just strategic, three controls are required:

1. **Unique key per concept:** `topic|mechanism|situation|audience|depth` (and optionally `format`). In Phoenix this is **concept_id** (topic_id|angle_id|persona_id|depth_level); format can be added for full **concept_key**. No new concept is approved unless this key is **unique in the active pipeline** (see §16 enforcement rule).
2. **Similarity check at planning time:** Before writing, block or flag **near-duplicate concepts** (e.g. semantic or angle overlap above a threshold). Prevents "same idea, different label" from entering the pipeline. Config: `concept_expansion_policy.yaml` → `similarity_check_enabled`, `similarity_block_threshold`; enforced in catalog generation or a pre-pipeline planning step.
3. **Coverage targets:** Balance output across axes (mechanism, situation, audience). Caps or minimum percentages per dimension prevent one mechanism/situation from dominating. Config: `concept_expansion_policy.yaml` or `catalog_planning_matrix.yaml` → coverage targets; used when selecting or validating the next concepts to produce.

---

## 16. Catalog Planning Matrix (10k+ scale)

Large publishers plan **10,000+ books without duplication** by maintaining a **Catalog Planning Matrix** before any writing begins: a master spreadsheet or database where **every book is one row**. This produces a catalog that looks **editorially planned** rather than randomly generated, which aligns with what platforms (e.g. Google Play Books, Findaway Voices) associate with legitimate publishers.

### Planning hierarchy

```
Publisher
  → Imprint (brand)
     → Topic Universe (domain cluster)
        → Series Family
           → Series
              → Book
```

Example: **CalmMind Press** (imprint) → **Anxiety** (universe) → **Calm Mind Series** (series) → Book 1, 2, 3. Phoenix maps this via **brand_id** (imprint), **domain_id** (universe/family), **series_id**, and book position (**installment_number**).

### Master matrix structure (one row = one book)

Core columns plus **three must-have columns for scale + control** (without hard blocking): **concept_key**, **similarity_score**, **human_decision**.

| Field | Example | In Phoenix |
|-------|---------|------------|
| book_id | B-1042 | plan hash / external id |
| **concept_key** | topic\|angle\|persona\|depth\|format | concept_id (Stage 1); concept_id + \| + format_structural_id when format known (Stage 2+) |
| imprint | CalmMind Press | brand_id |
| universe | Mental Wellness | domain_id (or topic cluster) |
| family | Anxiety | domain_id / series family |
| series | Calm Mind Series | series_id |
| series_book | 3 | installment_number |
| angle | nervous system | angle_id |
| audience | professionals | persona_id |
| situation | workplace | encoded in angle_id |
| depth_level | practical | depth_level |
| format | guide | format_structural_id (Stage 2) |
| status | planned | pipeline stage |
| **similarity_score** | 0.0–1.0 | advisory; set by similarity check at planning time |
| **human_decision** | approve \| hold \| override | production gate; override = human approved despite advisory |

### Supporting sheets (operating schema)

- **SERIES_REGISTRY:** series_id, family, planned_books, current_books.
- **ANGLE_REGISTRY:** angle_id, topic/family, used_count (avoid angle overuse).
- **TOPIC_MATRIX:** rows = potential concepts (topic, mechanism, situation, audience, depth).
- **RELEASE_SCHEDULE:** week, book_id, imprint, series, series_book (smooth cadence).
- **METADATA_LIBRARY:** title styles, description templates (rotate for diversity).
- **DUPLICATION_CHECK:** e.g. COUNTIFS on family+angle+audience to detect overlap.

See **§16a Operating schema and immutable keys** below for production-ready column set.

### Topic coverage map and series capacity

- **Topic coverage grid:** e.g. Anxiety 60 books, Burnout 48, Focus 42 — ensures no single topic dominates. Enforced via diversity_guards (max_share_per_topic) and optional coverage targets.
- **Series capacity:** Short series 3–4, standard 5–7, flagship 8–12. Config: series_templates, capacity_constraints; avoids too many unfinished series.

### Enforcement rule (active pipeline)

**No new concept unless the concept key is unique in the active pipeline.**

- **Concept key** = `topic|mechanism|situation|audience|depth|format` (immutable). Phoenix **concept_id** = topic_id|angle_id|persona_id|depth_level; format can be appended for full key when format is known at planning time.
- **Active pipeline** = the current catalog generation run (and optionally any persisted "already planned" set). Uniqueness is enforced by the **concept_id sliding window** in `generate_full_catalog.py`: same concept_id is blocked within the last N books unless it is the same series (allow_sequenced_reuse). This makes the matrix **production-safe**, not just theoretical.

### Example planning scale (10k catalog)

| Layer | Typical count |
|-------|----------------|
| Imprints | 10 |
| Topic universes | 40 |
| Series families | 200 |
| Series | 800 |
| Books | 10,000 |

Each layer feeds the next; the matrix is the **blueprint for the entire publishing program**.

---

### 16a. Operating schema: immutable keys and MASTER_CATALOG quality columns

To turn the planning matrix into **full production control**, use immutable keys and quality columns.

**Immutable keys:**

- **concept_key** = `topic|mechanism|situation|audience|depth|format`. Uniqueness in active pipeline is required. In Phoenix, concept_id is this without format; add format when available (e.g. from format_structural_id in compiled plan).
- **series_key** = `imprint|universe|family|series`. In Phoenix: brand_id|domain_id|family|series_id (family can be derived from domain_id or series metadata).

**MASTER_CATALOG quality columns (per book row):**

| Column | Purpose |
|--------|---------|
| similarity_score | Set by similarity check at planning time; high value = near-duplicate risk. |
| metadata_style_id | Links to METADATA_LIBRARY for title/description rotation. |
| release_wave_id | Which wave/week this book is scheduled for. |
| advisory_status | info \| warn \| critical (e.g. overlap risk, coverage imbalance). |
| human_decision | approve \| hold \| override (production gate; override = human approved despite advisory). |

These columns support **production control**: similarity and advisory drive holds; human_decision gates release. BookSpec and compiled plan can carry optional `metadata_style_id`, `release_wave_id`, `advisory_status`, `human_decision`; `similarity_score` is set when the similarity check runs (catalog generation or prepublish).

---

## 17. Automation layer (planning → production)

When catalogs scale to 10k–20k+ titles, the spreadsheet/planning DB is the **control center**; an **automation layer** turns the catalog plan into books, metadata, and release schedules. Use **four stacked layers** with one critical rule: **metadata is constrained rotation, not pure random.**

### Four layers

| Layer | Purpose | Phoenix alignment |
|-------|---------|-------------------|
| **1. Catalog planning DB** | Source of truth: MASTER_CATALOG, SERIES_REGISTRY, ANGLE_REGISTRY, TOPIC_MATRIX, RELEASE_SCHEDULE. Answers: what books exist, what’s coming, where they fit. | Config + BookSpec + generate_full_catalog; concept_key uniqueness in active pipeline. |
| **2. Book generation pipeline** | Deterministic assembly from **concept keys**. Catalog row → outline → manuscript → metadata → cover → publication package. Each row = production job. | run_pipeline: BookSpec (concept_id/series_key) → format selection → assembly → compiled plan. |
| **3. Metadata generator** | **Constrained rotation:** rule-based selection by **concept + style quotas + anti-reuse windows**. Do **not** use pure `random()` template selection—it produces detectable patterns. | metadata_diversity_policy.yaml; naming/metadata key off program_id, worldview_id, angle_id; style quotas and anti-reuse in downstream metadata writer. |
| **4. Release scheduler** | Wave-based pacing with **imprint caps**. Max books per week, max per imprint per week, series cluster size. Prevents upload spikes. | release_scheduler.yaml, series_launch_policy.yaml; wave_orchestrator; same_day_cross_brand_max. |
| **Health monitor** | Advisory alerts + **human override**. Title similarity, angle repetition, series completion, release spikes. Alerts planners; human_decision (approve/hold/override) gates release. | advisory_policy.yaml; similarity_score, advisory_status, human_decision on BookSpec/compiled plan; catalog health goals (§19). |

### Critical rule: no pure random metadata

- **Avoid:** `title = random(title_templates)` across the catalog. That still produces detectable clustering.
- **Use:** Rule-based selection by **concept** (topic/angle/persona) + **style quotas** (e.g. no style >20% in a wave) + **anti-reuse windows** (e.g. same title structure not repeated within last N books). Config: metadata_diversity_policy.yaml; downstream metadata and naming engines should key off program_id, worldview_id, angle_id and apply quotas/windows.

Result: **scale + control**—spreadsheet = source of truth, pipeline = deterministic from concept keys, metadata = constrained rotation, scheduler = wave-based with caps, health = advisory + human override.

---

## 18. Capacity planning (theoretical → feasible → scheduled)

Large publishers plan 20k+ catalogs using **catalog capacity math**: universes × topics × angle families × series × books × imprints. Raw multiplication **overestimates** real capacity; apply **feasibility filters** before counting a slot as valid.

### Three slot types

| Slot type | Meaning |
|-----------|---------|
| **Theoretical slots** | Raw capacity from architecture (e.g. 10 universes × 6 topics × 6 angle families × 3 series × 5 books × 4 imprints = 21,600). |
| **Approved slots** | Slots that pass filters: demand/performance fit, duplication/similarity risk, teacher/brand coherence, metadata diversity balance, compliance. |
| **Scheduled slots** | Approved slots assigned to a wave/week in RELEASE_SCHEDULE; these become production jobs. |

### Feasibility filters (before counting approved capacity)

- **Demand/performance fit** — topic/angle/persona fit to audience and performance data where available.
- **Duplication/similarity risk** — concept_key unique in active pipeline; similarity_score below threshold or human_decision override.
- **Teacher/brand coherence** — teacher in brand matrix, program_id resolved; no cross-brand spill.
- **Metadata diversity balance** — style quotas and anti-reuse so the wave does not cluster on one title/description pattern.
- **Compliance** — category/keyword/territory and any platform-specific rules.

Use capacity math for **long-range architecture** (how many slots exist) and **slot filling** (“what slot in the catalog architecture needs to be filled?”). Then filter to approved slots and schedule to waves. Config: concept_expansion_policy (coverage targets, similarity); diversity_guards; series_templates and capacity_constraints.

---

## 19. Catalog health ratios (five metrics)

Large publishers monitor **five health ratios** so the catalog looks like a **real editorial ecosystem**, not a content farm. These affect how platforms (e.g. Google Play Books, Findaway Voices) perceive the catalog.

| # | Ratio | Healthy range | Purpose |
|---|-------|----------------|---------|
| 1 | **Series depth** | Avg 4–6 books per series; ≥80% of series with ≥3 books | Stores reward reader progression; many unfinished series = low quality. |
| 2 | **Topic spread** | Largest topic &lt;15% of catalog; top 5 topics &lt;50% | One topic dominating (e.g. 40% anxiety) = keyword farming. |
| 3 | **Release velocity** | 8–20 releases/week; single-day uploads ≤30% of weekly output | Prevents sudden spikes that resemble automated publishing. |
| 4 | **Author spread** | 10–80 books per author typical; catalog with ≥10 authors preferred | One author with 1,000 books looks artificial. |
| 5 | **Metadata diversity** | ≥6 title structures; 8–15 description frameworks; 5–10 subtitle formats | Prevents uniform patterns (“Stop X Today” everywhere). |

### Dashboard goals (summary)

| Metric | Goal |
|--------|------|
| Series depth | 4–6 books per series |
| Topic spread | &lt;15% per topic |
| Release velocity | 8–20/week |
| Author spread | ≥10 authors |
| Metadata diversity | ≥6 title styles (and varied description/subtitle) |

Config: [config/catalog_planning/catalog_health_goals.yaml](../config/catalog_planning/catalog_health_goals.yaml) defines target ranges for audits and dashboards. Health monitor = **advisory alerts + human override**; these ratios are internal heuristics, not guaranteed platform policy.

---

## 20. Publisher growth curve (100 → 1k → 10k)

Large catalogs grow by **adding structural layers**, not by scaling output volume alone. The **publisher growth curve** describes how catalogs expand from ~100 → ~1,000 → ~10,000 books while staying **lower-risk when quality and diversity signals stay healthy** (treat as risk heuristic, not “algorithm-safe” guarantee).

**Cautions:** (1) Stage counts and ranges below are **planning heuristics**, not external standards. (2) Prefer wording “lower-risk if quality/diversity signals stay healthy” over “algorithm-safe/friendly.”

### Five structural stages

| Stage | Book range | Main focus | New layer |
|-------|------------|------------|-----------|
| **1. Early catalog** | 0–100 | Topic discovery, series testing | Topics 5–10; series 10–20; 3–4 books/series; 30–40% standalones. Market research through publishing. |
| **2. Expansion** | 100–1k | Series families | Topic → Series Family → Series. Topics 20–30; families 60–120; series 200–300. “What series should this topic support?” |
| **3. Multi-imprint** | 1k–5k | Imprint specialization | Publisher → Imprints → Topics → Families → Series → Books. Same topic universes, different audiences per imprint. |
| **4. Ecosystem** | 5k–10k | Knowledge network | Imprints 8–15; topics 50–80; series 800–1,200. Topic proximity and series progression drive recommendations. |
| **5. Mature network** | 10k–20k | Content ecosystem | Fill matrix gaps, expand successful series, add topic universes. Structure: imprints → topics → families → series → books. |

### Release velocity (heuristic)

| Stage | Weekly releases (heuristic) |
|-------|-----------------------------|
| Startup | 2–4 |
| Growth | 5–10 |
| Mid-size | 10–20 |
| Large | 20–40 |

### Key insight

Scale by **adding layers**: Books → Series → Series Families → Topic Universes → Imprints. Each layer multiplies possible books **without duplication**. Use this as a **roadmap anchor** for where the catalog is and what to add next.

---

## 21. Series ladder (scale from proven concepts)

Instead of one linear series, a **series ladder** expands one successful series into **specialized → audience → situation** series so a single concept supports many books without repeating content. Fits the goal: scale from proven concepts without cloning.

### Ladder structure

```
Core Series (foundation)
   ↓
Specialized Series (angle/mechanism expansion)
   ↓
Audience Series (persona expansion)
   ↓
Situation Series (context expansion)
```

Example: Calm Mind Series (5 books) → Nervous System / Overthinking / Stress Biology series (each 4–6) → Calm Mind for Professionals / Students / Parents (each 3–5) → Workplace Stress / Relationship Anxiety / Digital Overload series (each 3–4). One concept can support dozens of books.

### Three safety rules (required for safe use)

1. **Distinct rung objective:** Each ladder rung must have a distinct **angle**, **audience**, or **situation** objective (no rung that is only a clone of another). Enforced via concept_id/angle_id/persona_id and series_key.
2. **Cross-rung similarity checks:** Enforce **concept + metadata** similarity checks across rungs so ladder expansion does not produce near-duplicate concepts or metadata. Use the same similarity_check and coverage_targets as in concept_expansion_policy.
3. **Evidence-driven expansion:** Trigger ladder expansion **only after performance evidence** from the core series (e.g. read-through, completion, engagement). Do not spin new series from a concept before the core has signals. Operational: track core-series metrics; add “ladder expansion” as a gated step after evidence threshold.

Config: [config/catalog_planning/series_ladder_policy.yaml](../config/catalog_planning/series_ladder_policy.yaml) (rung uniqueness, similarity checks, evidence gate). Expansion is **evidence-driven and uniqueness-checked**.

---

## 22. Topic authority clusters

Stores (e.g. Google Play Books, Findaway Voices) use **behavioral recommendation graphs**. When multiple books appear related and readers move between them, the store can group them in “related titles,” “similar books,” or “customers also enjoyed.” A **topic authority cluster** is a group of books around one tightly defined topic that reinforce each other in that graph—think in **topic ecosystems**, not isolated titles.

**Caution:** Specific thresholds (e.g. “12–20 books triggers grouping”) are **heuristics**, not guaranteed platform behavior. Use as planning guidance; validate with your own data.

### Practical use

1. **Define cluster targets per topic/program.** For each major topic (or program), set a target book count for the cluster (e.g. 12–20 as internal planning range). Config: optional [config/catalog_planning/topic_cluster_targets.yaml](../config/catalog_planning/topic_cluster_targets.yaml) (topic_id or program_id → target_min/target_max books).
2. **Build internal cross-links across related series.** In descriptions, “Readers of this book may also enjoy: [titles from same cluster]” to encourage reader movement within the cluster. Cross-series linking (§11) and series ladders (§21) naturally form clusters.
3. **Track actual cross-title recommendation lift and read-through before expanding.** Treat cluster expansion as **evidence-driven**: measure cross-title click-through, read-through to second/third title, and organic internal discovery share; expand clusters when your data shows lift, not only when a count threshold is hit.

Clusters often form from **series ladders** (core + specialized + audience + situation series). Multiple pathways between books make the catalog behave like a topic ecosystem. Strategy is strong as long as it stays **evidence-driven in your own data**.

---

## 23. Catalog flywheel

Once a catalog reaches a certain size and structure, discovery can start to **accelerate** because the catalog behaves like a **network** (entry points + clusters + series read-through) rather than a collection of isolated books. Emphasis: **structure**, not just volume.

**What to keep:** Network-effect framing (more books → more entry points → more recommendations → more cross-book discovery → more sales/data → better recommendations). Series read-through amplifies the loop.

**What to soften:** A fixed threshold like “300–500 books” varies by niche, quality, and metadata discipline. Do not treat it as a universal trigger.

### Best use: measurable milestone in your own data

Treat the flywheel as a **measurable milestone**, not an assumed stage:

- **Rising cross-title click-through** — readers moving from one book to another within the catalog.
- **Increasing read-through** into second/third title (series or cluster).
- **Growing share of organic internal discovery** — traffic from “related”/“also enjoyed” rather than only search or external.

When these metrics improve, the catalog is acting like a **content network** (each book helps discover the others). Use the flywheel as strategy direction with **data-based validation** rather than assumed thresholds. Optional: track flywheel metrics in dashboards and set internal targets (e.g. % of sessions with cross-title click, read-through rate) to know when the effect is real in your catalog.

---

## Summary

| Item | Where / action |
|------|----------------|
| Principle | Many programs, few books per program; not one content network |
| Editorial program | **First-class:** `program_id` in TeacherAllocation, BookSpec, compiled plan; config `editorial_programs.yaml` (§2a) |
| Teacher domains | Teachers assigned to programs per brand in editorial_programs.yaml; portfolio planner resolves program_id |
| Operational checklist | Risk heuristic only; see §4 (metadata, staggering, cover, narrator, category, series, pacing) |
| Four hard caps/audits | (1) Teacher share ✓; (2) Template similarity — audit; (3) Keyword overlap — audit; (4) Same-day bursts — release_scheduler same_day_cross_brand_max |
| Worldview | §5a: worldview_id required; max_share_per_worldview; catalog_worldviews.yaml; scale differentiation before volume |
| Release topology | §5b: release_scheduler.yaml (wave sizes, brand_days, same_day_cross_brand_max, variance); tie to editorial logic |
| Catalog breadth | §5c: tier_targets.yaml (core 70 / adjacent 20 / niche 10); enforce brand+program+quarterly; track monthly |
| Phoenix | program_id, worldview_id, release_scheduler, tier_targets implemented; downstream wiring optional |
| Volume & legitimacy (§9) | Operating playbook, not compliance standard; series progression, brand segmentation, distinct metadata; lower risk if differentiation real; no universal "safe" volume |
| Catalog fingerprint (§10) | **Top QA policy:** no near-duplicate content/metadata across catalog. Near-duplicate = primary risk; fix = angle-based differentiation + series progression + metadata diversity. Seven-signal checklist → UI advisory; numeric thresholds = internal heuristics only. See config/governance/advisory_policy.yaml. |
| Series Tree (§11) | Internal architecture: Universe → Family → Series → Book; release in branch clusters; cross-series linking; series-first + standalones; lower risk, editorially structured (not "algorithm-safe" guarantee); implement in planner metadata + release scheduler for strong scale model |
| Angle Matrix (§12) | Topic × Angle × Series; angle_id mandatory; block same topic+angle within window unless sequenced; track similarity by topic+angle family; angle-specific title/description templates; config/catalog_planning/angle_matrix_policy.yaml; weekly 8–20 books heuristic for 500–1k/year |
| Series seeding (§13) | Launch new series with 2–3 books close together; weekly mix = continuations + new clusters + standalones; cap new series starts per brand; confirm read-through in dashboards before boosting volume; config/release_velocity/series_launch_policy.yaml; likely engagement pattern, not guaranteed algorithm |
| Metadata uniformity (§14) | Major hidden risk: metadata pattern uniformity (title/subtitle/description/category/keyword/series). Internal diversity standard + QA checklist; rotate title structures, description frameworks, subtitle styles; config/catalog_planning/metadata_diversity_policy.yaml; numeric targets = heuristics only, not platform rules |
| Topic expansion (§15) | 6-dimension concept design (topic × mechanism × situation × audience × level × format); required concept_id in planning; uniqueness window on concept_id; series from concept progression; **3 controls:** unique key, similarity check at planning, coverage targets; config/catalog_planning/concept_expansion_policy.yaml; planning model for 10k+ scale |
| Catalog Planning Matrix (§16) | Master matrix: one row = one book; hierarchy Imprint → Universe → Family → Series → Book; SERIES_REGISTRY, ANGLE_REGISTRY, TOPIC_MATRIX, RELEASE_SCHEDULE, METADATA_LIBRARY, DUPLICATION_CHECK; **enforcement:** no new concept unless concept key unique in active pipeline (§15 concept_id window) |
| Operating schema (§16a) | Immutable keys: concept_key, series_key; MASTER_CATALOG must-have: concept_key, similarity_score, human_decision (approve\|hold\|override); production control, not planning-only |
| Automation layer (§17) | Four layers: planning DB = source of truth; pipeline = deterministic from concept keys; metadata = **constrained rotation** (rule-based by concept + style quotas + anti-reuse), **not pure random**; scheduler = wave-based + imprint caps; health = advisory + human override |
| Capacity planning (§18) | Theoretical slots → feasible (filters: demand, duplication, teacher/brand, metadata balance, compliance) → scheduled slots; “fill slot in architecture” not ad-hoc titles |
| Catalog health ratios (§19) | Five metrics: series depth (4–6), topic spread (&lt;15% per topic), release velocity (8–20/week), author spread (≥10 authors), metadata diversity (≥6 title styles); config/catalog_planning/catalog_health_goals.yaml |
| Publisher growth curve (§20) | Scale by adding layers (series → families → imprints), not just volume; five stages 100→1k→10k; stage counts = planning heuristics; “lower-risk if quality/diversity stay healthy”; roadmap anchor |
| Series ladder (§21) | Core → specialized → audience → situation series; one concept → many books without cloning; **3 rules:** distinct angle/audience/situation per rung, cross-rung similarity checks, evidence-driven expansion; config/catalog_planning/series_ladder_policy.yaml |
| Topic authority clusters (§22) | Think in topic ecosystems (clusters), not isolated titles; define cluster targets per topic/program; build internal cross-links; track cross-title recommendation lift and read-through; evidence-driven expansion; thresholds (e.g. 12–20 books) = heuristics only |
| Catalog flywheel (§23) | Network effect: entry points + clusters + series read-through; structure not just volume; treat as measurable milestone (cross-title CTR, read-through, organic internal discovery); no fixed “300–500” threshold—validate in your own data |
