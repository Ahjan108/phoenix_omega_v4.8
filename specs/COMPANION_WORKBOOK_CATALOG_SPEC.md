# Companion Workbook — Catalog Planning & Platform Content Spec

**Authority:** This document extends `PHOENIX_FREEBIE_SYSTEM_SPEC.md §10.5` for companion workbooks specifically.
**Scope:** 100-book catalog — which books get workbooks, what type, and exactly what content the platform listing must include at book creation time.
**EI V2 note:** The EI V2 system must be aware of `companion_workbook_type` when generating book content so it can calibrate exercise density, reflection prompt depth, and INTEGRATION slot weight accordingly.

---

## 1. Why Companion Workbooks Are a Sales Driver (Not Just a Freebie)

A companion workbook changes the commercial position of the book:

- **Bundle pricing**: a $9.99 ebook becomes a $27–47 bundle without changing the core book. The workbook justifies the price increase.
- **Reader stickiness**: workbook users take longer to finish, return to material, and buy subsequent books at higher rates than passive readers.
- **CTA engine**: the workbook IS the freebie; the Proof Loop funnel (exercise in book → deeper exercise in workbook → email sequence) is the natural path. The CTA writes itself.
- **Social proof acceleration**: readers who do the exercises get results faster and generate better reviews.

The catalog planner must weight companion workbook assignment as a commercial decision, not just a content decision.

---

## 2. Workbook Type Classification

Three types. Assigned at planning time by the freebie planner based on domain, engine, and book duration.

| Type | Description | ~Catalog % | Trigger |
|---|---|---|---|
| `full` | 80–120 page workbook; marketed as a bundle; own listing on platform | ~20–25 books | Duration ≥ 90 min AND domain in `full_workbook_domains` |
| `light_guide` | 30–50 page practice guide; attached as download freebie; not a separate listing | ~15–20 books | Duration 60–89 min OR duration ≥ 90 min AND domain NOT in `full_workbook_domains` |
| `none` | No workbook | ~50–60 books | Duration < 60 min OR domain in `no_workbook_domains` |

**Domain classification** (config: `config/freebies/freebie_selection_rules.yaml §companion_workbook_type_rules`):

```
full_workbook_domains:
  - shame_cluster          # somatic, healing — high exercise content
  - grief_cluster          # guided practice essential
  - anxiety_cluster        # structured tools work for this audience

light_guide_domains:
  - spiritual_general      # some exercises, not full program
  - leadership_general     # shorter application sections

no_workbook_domains:
  - narrative_spiritual    # story-driven; workbook doesn't fit
  - topic_primers          # reference/informational; short-form
```

**Series rule**: For a series, only installments 1, 3, and 5 get a `full` workbook. Other installments get `light_guide` or `none` per the standard rules. Config key: `companion_rule.required_installments_full`.

---

## 3. CTA Placement Architecture (Canonical)

This replaces the single back-matter rule in §10.5 for all books that have a workbook. The pipeline must inject CTAs at each placement point appropriate to the format.

### 3a. Audiobook CTA Placement

| Slot | Timing | Content | Mandatory? |
|---|---|---|---|
| **Post-intro spoken CTA** | Immediately after intro chapter narration ends | Short form (15–20 sec) | Yes, all workbook books |
| **Back matter spoken CTA** | Final chapter / outro narration | Long form (30–45 sec) | Yes, all workbook books |

The narrator reads both. Platform description must echo the same URL.

**Short form template (post-intro, ≤20 seconds narrated):**
```
"This audiobook has a companion {workbook_label} with all the exercises
and reflection prompts. You can get it free at
PhoenixProtocolBooks.com/free/{slug}."
```

**Long form template (back matter, ≤45 seconds narrated):**
```
"To go deeper and actually do the work from this book, download the
companion {workbook_label} at PhoenixProtocolBooks.com/free/{slug}.
You'll find guided exercises, journaling pages, and tools you can
return to. It's free — designed to go with exactly this book."
```

### 3b. Ebook / Print CTA Placement

| Slot | Location | Content | Mandatory? |
|---|---|---|---|
| **Front matter pointer** | After title/copyright page; before intro chapter | One-line: URL + what it is | Yes, `full` workbooks; Optional `light_guide` |
| **Post-intro CTA block** | After intro chapter INTEGRATION slot | Full CTA block (3–4 sentences) | Yes, all workbook books |
| **Mid-book CTA** | After highest-EXERCISE-density chapter | One-line reminder only | Optional; `full` workbooks only; ≤1 per book |
| **Back matter CTA** | After last chapter / final INTEGRATION | Final upsell block (existing §10.5) | Yes, all workbook books |

**Front matter pointer (one line):**
```
A companion {workbook_label} is available for this book at
PhoenixProtocolBooks.com/free/{slug}. You may want to have it
alongside you as you read.
```

**Post-intro CTA block (mandatory for all workbook books):**
```
[COMPANION WORKBOOK CTA BLOCK]
--- pipeline-injected, not hand-written ---

A companion {workbook_label} is available for this book.
It deepens every exercise with guided practice pages, reflection
prompts, and tools you can return to.
Get it free at PhoenixProtocolBooks.com/free/{slug}.

[CHAPTER 1 BEGINS]
```

**Mid-book one-liner (optional, `full` only):**
```
"[Download the companion {workbook_label} at PhoenixProtocolBooks.com/free/{slug}
to work through these exercises in depth.]"
```

### 3c. `workbook_label` by type

| Type | `workbook_label` |
|---|---|
| `full` | `"workbook"` |
| `light_guide` | `"practice guide"` |

---

## 4. Platform Content Required at Book Creation

**This is the complete set of content fields that must be generated and stored in the book plan at creation time.** Assembly and platform upload steps read from these fields. No field should be left empty or contain an unreplaced placeholder when the book is submitted to any platform.

### 4.1 Core identification fields

| Field | Source | Notes |
|---|---|---|
| `companion_workbook_type` | Freebie planner output | `full` \| `light_guide` \| `none` |
| `companion_workbook_slug` | Freebie planner (`freebie_slug`) | e.g. `burnout-gen-z-workbook` |
| `companion_workbook_url` | Constructed from slug | `PhoenixProtocolBooks.com/free/{slug}` |
| `workbook_label` | Derived from type | `workbook` or `practice guide` |

### 4.2 Platform description content

These go into the book listing description on KDP, Findaway, ACX, etc. The platform description must include the workbook sentence for every book that has a workbook (`type != none`).

| Field | Content |
|---|---|
| `platform_description_workbook_line` | "Includes a free companion {workbook_label} with guided exercises and reflection prompts. Download at PhoenixProtocolBooks.com/free/{slug}." |
| `platform_description_bundle_line` | (`full` only) "Available as a bundle with the companion workbook at a reduced price." |
| `platform_keywords_workbook` | `["companion workbook", "workbook", "practice guide", "exercises", "reflection prompts"]` (trim to platform keyword limit) |

**Platform description template (where to insert):**
```
[Book hook / main description — 150-300 words]

[platform_description_workbook_line injected here as a standalone paragraph]

[Author bio / series note if applicable]
```

### 4.3 Audiobook-specific content

| Field | Content |
|---|---|
| `audiobook_post_intro_cta_spoken` | Short form narration text (≤20 sec) — fully rendered, no placeholders |
| `audiobook_back_matter_cta_spoken` | Long form narration text (≤45 sec) — fully rendered, no placeholders |
| `audiobook_description_workbook_line` | Same as `platform_description_workbook_line` — echoed in ACX/Findaway description |

### 4.4 Ebook/Print-specific content

| Field | Content |
|---|---|
| `ebook_front_matter_pointer` | One-line front matter text — fully rendered, no placeholders |
| `ebook_post_intro_cta_block` | 3–4 sentence CTA block — fully rendered, pipeline injects after intro INTEGRATION |
| `ebook_mid_book_cta_line` | One-liner for mid-book (`full` type only; null otherwise) |
| `ebook_back_matter_cta_block` | Final upsell block (existing §10.5 rendering) |

### 4.5 Bundle / subtitle metadata

| Field | Applies to | Content |
|---|---|---|
| `subtitle_workbook_tag` | `full` workbooks only | `"with Companion Workbook"` — appended to subtitle when the book is marketed as a bundle |
| `bundle_listing_name` | `full` workbooks only | `"{Book Title} + Companion Workbook Bundle"` |
| `bundle_price_tier` | `full` workbooks only | Config-driven; typically 2.5–3× ebook price |

### 4.6 UTM tracking (GA4)

All workbook URLs must include UTM parameters so GA4 can attribute conversions by format and book:

| Format | URL |
|---|---|
| Audiobook (spoken post-intro) | `PhoenixProtocolBooks.com/free/{slug}?utm_source=audiobook&utm_medium=spoken_cta&utm_campaign={book_id}&utm_content=post_intro` |
| Audiobook (back matter) | `PhoenixProtocolBooks.com/free/{slug}?utm_source=audiobook&utm_medium=spoken_cta&utm_campaign={book_id}&utm_content=back_matter` |
| Ebook (front matter) | `PhoenixProtocolBooks.com/free/{slug}?utm_source=ebook&utm_medium=front_matter&utm_campaign={book_id}` |
| Ebook (post-intro) | `PhoenixProtocolBooks.com/free/{slug}?utm_source=ebook&utm_medium=post_intro_cta&utm_campaign={book_id}` |
| Ebook (back matter) | `PhoenixProtocolBooks.com/free/{slug}?utm_source=ebook&utm_medium=back_matter&utm_campaign={book_id}` |

**Note:** The short spoken URL (no UTM) is used in narration. The UTM URL is placed in ebook hyperlinks, platform description links, and the metadata landing page. Use a redirect at the clean URL that appends UTM when needed, or maintain both.

---

## 5. EI V2 Awareness: What the Content System Needs to Know

When EI V2 generates book content, it must receive `companion_workbook_type` from the plan so it can:

- **`full` workbook**: maximize EXERCISE slot density (≥3 per book); write reflection prompts that reference the workbook explicitly ("the workbook has a deeper version of this exercise"); ensure INTEGRATION slots land strongly so the post-intro CTA placement makes sense.
- **`light_guide`**: ≥1 EXERCISE slot minimum; write at least one reflection prompt; integration landing is softer.
- **`none`**: no workbook references in content; EXERCISE slots driven by engine/domain only.

The `companion_workbook_type` field must be present in the BookSpec/plan dict passed into the EI V2 engine loader.

---

## 6. Delivery Gate Extension (§10.6 addition)

The existing §10.6 delivery gate (no unreplaced placeholders) must be extended to cover all new fields:

- `audiobook_post_intro_cta_spoken` must not contain `{slug}`, `{workbook_label}`, or `{book_id}` — must be fully rendered
- `platform_description_workbook_line` must not contain raw placeholders
- All UTM URLs must contain a resolved `book_id` and `slug`

Gate: `scripts/ci/check_book_output_no_placeholders.py` — extend pattern list to include these new fields.

---

## 7. Implementation Checklist

- [ ] `config/freebies/freebie_selection_rules.yaml` — add `companion_workbook_type_rules` block (§2 domain lists + duration thresholds)
- [ ] `config/freebies/companion_workbook_platform_content.yaml` — CTA text templates with `{workbook_label}`, `{slug}`, `{book_id}` tokens
- [ ] `phoenix_v4/planning/catalog_planner.py` — add `companion_workbook_type: Optional[str]` to `BookSpec`
- [ ] `phoenix_v4/planning/freebie_planner.py` — resolve `companion_workbook_type` and `companion_workbook_url` and emit in plan output; render all platform content fields
- [ ] Assembly/rendering step — inject `ebook_post_intro_cta_block` after intro INTEGRATION; inject `ebook_front_matter_pointer` before Chapter 1; inject `ebook_back_matter_cta_block` at back matter
- [ ] Audiobook script builder — inject `audiobook_post_intro_cta_spoken` after intro chapter narration block; inject `audiobook_back_matter_cta_spoken` in outro
- [ ] Platform upload step — pull `platform_description_workbook_line` and `platform_keywords_workbook` into KDP/ACX/Findaway metadata payload
- [ ] `scripts/ci/check_book_output_no_placeholders.py` — extend to cover new fields
- [ ] Gate 16b (`cta_signature_caps.py`) — no change needed; workbook CTA uses same signature system

---

*Authority: specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md §10.5 (extended), docs/EI_V2_MARKETING_INTEGRATION_SPEC.md*
*Owner: Phoenix Omega pipeline — pearl_prime branch*
