# PATCH — PHOENIX_V4_5_WRITER_SPEC.md
# Append Section 23 at end of file. Do not modify any existing section.
# Last updated: 2026-02-20
# Authority: Subordinate to Arc-First Canonical Spec, PHOENIX_V4_5_WRITER_SPEC §1–22, and TEACHER_MODE_V4_CANONICAL_SPEC.

---

# 23. Identity & Audiobook Governance Layer

---

## 23.0 Purpose

This section introduces governance for pen-name authors, brand-bound narrators, and audiobook front-matter assembly. It does not alter any existing canonical rule.

---

## 23.1 Scope Clarification

**Applies to:**
- Pen-name authors
- Brand-bound authors
- Audiobook narrator front matter

**Does NOT apply to or modify:**
- Teacher Mode Pre-Intro (governed by TEACHER_MODE_V4_CANONICAL_SPEC; 900–1200 words, 4 paragraphs, "I was not a direct student…" structure)
- STORY tense (third-person present remains canonical and unchanged)
- EXERCISE, BREATH, ANCHOR, REFLECTION, BRIDGE atom types
- Arc rules and emotional band definitions
- Six Atom Types
- TTS constraints (§5–§9)
- Persona definitions (§17)

If any rule in this section conflicts with §1–22 of this spec, §1–22 governs.

---

## 23.2 Author Registry Requirement (Pen-Name Authors Only)

All non-teacher pen-name authors must be registered in:

```
config/authoring/author_authority_registry.yaml
```

Each author entry must define:

```yaml
author_id:           # snake_case unique ID
pen_name:            # display name used in audiobook
brand_id:            # must match entry in brand_registry.yaml
allowed_personas:    # list — must match persona IDs in config/catalog_planning/
allowed_topics:      # list — must match topic IDs in domain_definitions
disallowed_topics:   # list — hard block; compile fails if violated
authority_boundary:  # plain-language description of what this author speaks on
resolution_compatibility:
  - grounded_shift
  - partial_resolution
  # identity_shift, full_resolution — only if explicitly allowed
assets_path:         # e.g. assets/authors/{author_id}/
status:              # draft | approved
```

**Compile fails if:**
- Author ID not found in registry
- Author topic not in `allowed_topics`
- Author persona not in `allowed_personas`
- Author `status` is not `approved`

No silent fallback. No default author.

---

## 23.3 Author Asset Contract

Each pen-name author must supply all four assets before compile is permitted. Assets live at:

```
assets/authors/{author_id}/
    bio.yaml
    why_this_book.yaml
    authority_position.yaml
    audiobook_pre_intro.yaml
```

**No asset may be runtime-generated.**
All assets must be human-written and approved before `status: approved` is set in the registry.

Asset word limits:

| Asset                   | Word Range  | Tone                  |
|-------------------------|-------------|-----------------------|
| bio.yaml                | 120–180     | Grounded authority    |
| why_this_book.yaml      | 150–250     | Origin story, specific|
| authority_position.yaml | 100–150     | Boundary-clear        |
| audiobook_pre_intro.yaml| 500–900     | Narrator-read framing |

---

## 23.4 Audiobook Pre-Intro Layer (Narrator Front Matter)

**Separate from Teacher Mode Pre-Intro.** Applies to pen-name books only.

The narrator reads the following blocks in order before Chapter 1:

```yaml
# audiobook_pre_intro.yaml — required structure

narrator_intro:        # Narrator self-introduction; 1–2 sentences
book_title_line:       # "{pen_name}'s [Book Title]"
series_line:           # "[Series name]" — omit block if no series
author_intro:          # "This book was written by {pen_name}."
author_background:     # 2–4 sentences; experience anchor, no credential inflation
why_this_book:         # 3–5 sentences; observed pattern, persona pain, emotional cost
transition_line:       # Final line handing off to Chapter 1; e.g. "Let's begin."
```

**Content rules for pre_intro:**
- No marketing language
- No transformation promises ("this book will change your life" = hard fail)
- No invented credentials
- No first-person emotional appeals on behalf of the author beyond lived context
- Must be persona-aware in `author_background` and `why_this_book`

**Assembly location:** Stage 2.5 (Identity Binding), before arc compile. See OMEGA_LAYER_CONTRACTS.md for schema extension.

---

## 23.5 Narrator Registry

All narrators must exist in:

```
config/narrators/narrator_registry.yaml
```

Each narrator entry:

```yaml
narrator_id:
display_name:
brand_compatibility:     # list of brand_ids this narrator is allowed for
persona_alignment:       # list of persona IDs
pacing_profile:          # e.g. gentle_steady, measured_calm, grounded_direct
voice_engine_id:         # ElevenLabs or equivalent voice ID
disallowed_topics:       # optional; hard block if set
status:                  # draft | approved
```

**Compile fails if:**
- Narrator not found in registry
- Narrator `brand_compatibility` does not include current `brand_id`
- Narrator `status` is not `approved`
- Narrator `disallowed_topics` overlaps current topic

---

## 23.6 Brand Registry Extension

The existing brand registry (`config/brands/brand_registry.yaml`) must include the following fields for identity binding to function:

```yaml
allowed_authors:       # list of author_ids; compile fails if current author not listed
default_narrators:     # list of narrator_ids in preference order
tone_constraints:      # e.g. [grounded, non-preachy, non-clinical]
audio_pacing_profile:  # must match a narrator pacing_profile
```

Brand registry is not new. These fields are additive. Do not remove existing brand fields.

---

## 23.7 Persona Specificity Enforcement (Additive)

Applies to all STORY and SCENE atoms. Does not change existing emotional band or TTS rules.

Every STORY and SCENE atom must contain:
- **≥ 1 micro-stake** — a small but socially meaningful consequence specific to the persona
- **≥ 1 environmental cue** — physical location, sound, artifact, or social hierarchy signal
- **Persona-realistic stressor** — language and context plausible for the declared persona

**STORY tense remains third-person present. Unchanged.**

Micro-stakes that are non-specific (e.g. "she felt nervous", "he worried about work") are insufficient. Atom must name the specific signal.

Examples of sufficient micro-stakes by persona:

```
gen_z_professional:  manager stops making eye contact; Slack message left unread
nyc_executive:       investor pauses mid-sentence; bonus cycle memo arrives late
healthcare_rn:       charge nurse doesn't make eye contact at shift change; chart backlog hits 12
```

Atoms failing persona specificity may not be promoted to `status: confirmed`. They remain `status: provisional_template` until upgraded.

---

## 23.8 Atom Promotion State (Operational Metadata Only)

Atoms may carry the following optional metadata field:

```yaml
status: provisional_template | confirmed
```

**Rules:**
- This field is **not** evaluated at runtime assembly
- It is enforced at content approval stage only
- `provisional_template` atoms may be used in development compile runs
- `confirmed` atoms only enter production waves
- Teacher Mode approval flow is unchanged; Teacher atoms continue to follow `SOURCE_OF_TRUTH/teacher_banks/` governance

**Promotion requires:**
1. Persona overlay applied
2. Micro-stake present and persona-specific
3. Environmental cue present
4. Repetition entropy acceptable (see GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md)
5. Human reviewer sets `status: confirmed`

No automated promotion. Human sign-off required.

---

## 23.9 Identity Binding Fail Conditions

Build fails (no silent fallback) if any of the following are true:

- Author not in `author_authority_registry.yaml`
- Author topic not in author's `allowed_topics`
- Author persona not in author's `allowed_personas`
- Author `status != approved`
- Any required asset file missing (`bio.yaml`, `why_this_book.yaml`, `authority_position.yaml`, `audiobook_pre_intro.yaml`)
- Narrator not in `narrator_registry.yaml`
- Narrator brand not compatible
- Narrator `status != approved`
- Brand registry missing `allowed_authors` or `default_narrators`
- Author not in brand's `allowed_authors`

---

## 23.10 What This Section Does Not Do

- Does not add a new atom type
- Does not change STORY to second person
- Does not change emotional band definitions
- Does not change arc structure
- Does not override Teacher Mode Pre-Intro
- Does not modify Stage 1, 2, or 3 schemas (Stage 2.5 Identity Binding is additive)
- Does not grant runtime prose generation rights

---

*End of Section 23.*
*Append after existing final section of PHOENIX_V4_5_WRITER_SPEC.md.*
*Do not modify any content above this section.*
