# AUTHOR ASSET PRODUCTION WORKBOOK

**Path:** docs/authoring/AUTHOR_ASSET_WORKBOOK.md  
**Audience:** Content Team, Writers, Brand Leads  
**Authority:** Operational only. Subordinate to [PHOENIX_V4_5_WRITER_SPEC.md](../../specs/PHOENIX_V4_5_WRITER_SPEC.md) (including §23) and Arc-First Canonical Spec.  
**Last updated:** 2026-02-22

---

## 0. What This Document Is

This workbook tells the content team exactly how to produce pen-name author assets for Phoenix V4 audiobook production.

It is NOT canonical architecture. It does NOT govern atoms, arcs, emotional bands, or TTS.

It governs one thing: **how to create a credible, brand-safe, persona-aware author identity that can survive production compile.**

Every asset produced here must be human-written and human-approved. Runtime never generates these.

---

## 1. Before You Start — Registry Check

Before writing a single word, confirm with the content lead that the following are assigned:

| Field            | Assigned? | Notes                                      |
|------------------|-----------|--------------------------------------------|
| `author_id`      | [ ]       | snake_case, unique, matches registry       |
| `pen_name`       | [ ]       | Display name used in audiobook             |
| `brand_id`       | [ ]       | Must exist in brand registry               |
| `allowed_personas` | [ ]    | List confirmed with catalog planner        |
| `allowed_topics` | [ ]       | List confirmed with domain_definitions     |
| `disallowed_topics` | [ ]    | Hard block — be specific                   |
| `authority_source` | [ ]    | Real-world experience base, 1–2 sentences  |
| `resolution_compatibility` | [ ] | Which arc endings this author can close |

Do not begin writing assets until all fields above are confirmed. Author identity without registry entry cannot compile.

---

## 2. Author Identity Principles

### What makes a credible pen-name author

- **Specificity over prestige.** "12 years supporting young professionals navigating burnout" outperforms "expert in wellness."
- **Boundary clarity.** What the author does NOT claim is as important as what they do.
- **Persona rootedness.** The author's background must make sense to the target persona.
- **No credential inflation.** Do not invent degrees, certifications, or clinical titles.
- **No transformation promises.** Authors describe what they observed and why they wrote. They do not promise what the reader will become.

### Tonal range by brand

| Brand type        | Author tone target                    |
|-------------------|---------------------------------------|
| Somatic/wellness  | Grounded, warm, non-clinical          |
| Executive/leadership | Measured, precise, low-sentiment  |
| Healthcare        | Practical, direct, fatigue-aware      |
| Gen Z spiritual   | Honest, contemporary, non-preachy     |

---

## 3. Asset: bio.yaml

**Purpose:** The narrator reads a condensed version of this before Chapter 1. The full version may appear on product pages.

**Word range:** 120–180 words

**Required elements:**
1. What the author does (role anchor — not a job title)
2. How long / in what context (experience base — specific, not grandiose)
3. Who they work with (persona anchor)
4. What they observed that led to this book (1 sentence bridge to why_this_book)

**Disallowed:**
- Academic titles unless verifiable and approved
- Clinical claims ("heals trauma", "treats anxiety")
- Future-state promises
- Celebrity name-drops not approved by legal/compliance
- First-person voice (bio is written in third person)

**Template:**

```yaml
author_id: {author_id}
pen_name: "{Pen Name}"
bio: >
  {Pen Name} is a [role anchor] who has spent [X years] [doing what, with whom].
  Working primarily with [persona description], [he/she/they] has observed
  [specific pattern that led to writing].
  [One sentence on approach or philosophy — grounded, no superlatives.]
  [One sentence on geographic or community context if relevant — optional.]
word_count_target: 120–180
status: draft | approved
```

**Example (approved):**

```yaml
author_id: luna_hart
pen_name: "Luna Hart"
bio: >
  Luna Hart is a somatic psychology educator who has spent over a decade
  supporting young professionals navigating anxiety and the particular
  exhaustion that comes from performing ambition. Working primarily with
  people in their mid-twenties navigating first careers, she has watched
  capable people freeze between what they want and what they feel entitled
  to want. Her work focuses on restoring the body's capacity to regulate
  before the mind attempts to solve. She is based in Los Angeles.
status: approved
```

---

## 4. Asset: why_this_book.yaml

**Purpose:** Explains to the listener why this specific book exists. Narrator reads a condensed version in the pre-intro. Must feel earned, not marketed.

**Word range:** 150–250 words

**Required elements:**
1. The specific pattern observed (not a general problem statement)
2. What it cost the people the author watched (persona pain — emotional cost, not clinical label)
3. Why existing approaches were insufficient (1–2 sentences — optional but strengthens credibility)
4. What motivated writing (specific, not inspirational)
5. What the author is not offering (boundary line — 1 sentence)

**Disallowed:**
- "I wrote this to help you..."
- "This book will..."
- "In this journey, you will discover..."
- Statistics without sourcing approved by content lead
- Any promise of outcome

**Template:**

```yaml
author_id: {author_id}
topic_id: {topic_id}
why_this_book: >
  [Author] began writing this after [specific observation — not generic].
  [What the people they observed were experiencing — specific, not clinical.]
  [What they tried that didn't work, or what was missing — optional.]
  [What led to writing — not inspiration, but necessity or clarity.]
  This book does not offer [boundary statement].
  It offers [honest scope — small, specific, grounded].
word_count_target: 150–250
status: draft | approved
```

---

## 5. Asset: authority_position.yaml

**Purpose:** Governance document. Defines what the author does NOT do. Used at compile time to validate topic/persona alignment. Not narrator-read.

**Word range:** 100–150 words

**Required elements:**
1. What the author refuses to claim
2. What the author refuses to promise
3. What professional support they recommend instead (for therapeutic topics)
4. Which resolution types are compatible with this author's voice

**Template:**

```yaml
author_id: {author_id}
authority_position:
  does_not_claim:
    - clinical diagnosis
    - trauma reprocessing
    - medical advice
    - guaranteed outcomes
  does_not_promise:
    - recovery
    - transformation
    - cure
    - fixed timeline for change
  recommends_professional_support_for:
    - clinical trauma history
    - active mental health crises
    - medication-related questions
  resolution_compatibility:
    - grounded_shift
    - partial_resolution
    # Add 'identity_shift' only if explicitly approved by content lead
status: draft | approved
```

---

## 6. Asset: audiobook_pre_intro.yaml

**Purpose:** Narrator reads this before Chapter 1. This is the listener's first experience of the author's voice and the book's identity. It sets trust. It must be precise, calm, and specific.

**Word range (total):** 500–900 words across all blocks combined

**Required blocks (in order):**

```yaml
narrator_intro:        # 1–2 sentences. Narrator introduces themselves.
book_title_line:       # States the book title and author name.
series_line:           # States series name. Omit block entirely if no series.
author_intro:          # 1 sentence. "This book was written by {pen_name}."
author_background:     # 2–4 sentences. From bio.yaml — condensed for audio. Persona-aware.
why_this_book:         # 3–5 sentences. From why_this_book.yaml — condensed. Specific, not marketed.
transition_line:       # 1 sentence. Hands off to Chapter 1.
```

**Content rules:**
- No marketing language anywhere
- No "this book will..." constructions
- No transformation promises
- No first-person author voice (narrator describes author; author does not speak in pre_intro)
- `author_background` must mention the persona implicitly or explicitly
- `why_this_book` must contain the emotional cost (not just the topic)
- `transition_line` must be plain and direct — no inspirational send-off

**Full example (approved):**

```yaml
author_id: luna_hart
narrator_intro: >
  My name is Ava Reed, and I will be guiding you through this audiobook.
book_title_line: >
  You are listening to "The Silence Before You Speak," written by Luna Hart.
series_line: >
  This audiobook is part of the Phoenix Somatic Series.
author_intro: >
  This book was written by Luna Hart.
author_background: >
  Luna is a somatic psychology educator who has spent over a decade working
  with young professionals navigating anxiety and burnout. Her work focuses
  on the body's capacity to regulate before the mind attempts to solve.
  She is based in Los Angeles.
why_this_book: >
  Luna began writing this after watching a consistent pattern: people who
  were capable, working, and genuinely not okay — but who had no language
  for it that didn't feel like failure. Most available support told them
  to think differently. This book starts elsewhere. It starts with what
  the body already knows before the mind catches up.
transition_line: >
  Chapter One.
status: approved
```

**Stable vs dynamic blocks (intro/ending variation):** When Controlled Intro/Conclusion Variation is enabled (`config/source_of_truth/intro_ending_variation.yaml`), the following blocks are **stable** (always from this YAML): `author_intro`, `author_background`. The following are **dynamic** (may be chosen from per-brand pattern banks): `book_title_line`, `series_line`, `why_this_book`, `transition_line`; optionally `narrator_intro`. If the pipeline supplies a runtime book title (e.g. from the naming engine), it is used for `book_title_line`; if your YAML has a fixed `book_title_line` that would differ from the runtime title, the build **fails** (no silent override). Either supply a dynamic title at compile time or use one fixed line per asset. Pattern banks supply variants for dynamic blocks; see SYSTEMS_V4 and the intro/outro variation section.

---

## 7. Brand Binding Checklist

Before submitting assets for approval, confirm:

| Check                                              | Pass? |
|----------------------------------------------------|-------|
| Author ID exists in author_authority_registry.yaml | [ ]   |
| Author brand_id matches brand registry entry       | [ ]   |
| Author appears in brand's `allowed_authors` list   | [ ]   |
| All 4 asset files exist at correct path            | [ ]   |
| bio.yaml within 120–180 words                      | [ ]   |
| why_this_book.yaml within 150–250 words             | [ ]   |
| authority_position.yaml within 100–150 words       | [ ]   |
| audiobook_pre_intro.yaml within 500–900 words      | [ ]   |
| No marketing language in pre_intro                 | [ ]   |
| No transformation promises in any asset            | [ ]   |
| No clinical claims in any asset                    | [ ]   |
| Persona reference present in author_background     | [ ]   |
| Emotional cost present in why_this_book            | [ ]   |
| authority_position.yaml resolution types confirmed | [ ]   |
| Content lead review complete                       | [ ]   |
| Status set to `approved` in registry               | [ ]   |

---

## 8. Approval Workflow

```
Writer drafts all 4 assets
        ↓
Content lead reviews against checklist (§7)
        ↓
Edits returned if any checklist item fails
        ↓
Approved assets committed to:
  assets/authors/{author_id}/
  (or path set in config/author_registry.yaml → assets_path for this author_id)
        ↓
Registry entry status updated:
  status: approved  (in author_registry; positioning_profile required)
        ↓
Author available for compile
```

Content lead is final approver. No compile without `status: approved`.

### Pipeline integration

When the pipeline runs with `--author <author_id>` (or author is resolved from brand via `config/brand_author_assignments.yaml`), it loads these four assets via `phoenix_v4/planning/author_asset_loader.py` from `assets/authors/{author_id}/` or from the registry’s `assets_path`. If any required asset is missing, the pipeline **fails** (Writer Spec §23.9). The compiled plan JSON includes `author_assets`; freebie and export templates may use placeholders: `{{author_pen_name}}`, `{{author_bio}}`, `{{author_why_this_book}}`, `{{author_audiobook_pre_intro}}`. See [SYSTEMS_V4.md](../SYSTEMS_V4.md) and [OMEGA_LAYER_CONTRACTS.md](../../specs/OMEGA_LAYER_CONTRACTS.md).

---

## 9. What This Workbook Does Not Cover

- Atom writing (see [PHOENIX_V4_5_WRITER_SPEC.md](../../specs/PHOENIX_V4_5_WRITER_SPEC.md))
- Persona specificity and micro-stakes (see [GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md](../writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md))
- Teacher Mode author assets (see [TEACHER_MODE_AUTHORING_PLAYBOOK.md](../../specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md) — separate system)
- Arc design (see [ARC_AUTHORING_PLAYBOOK.md](../../specs/ARC_AUTHORING_PLAYBOOK.md))
- Narrator assets (narrator registry is maintained by dev; narrator intro templates follow same format rules as §6)

---

*Operational document — content team use only. Does not modify canonical specs.*
