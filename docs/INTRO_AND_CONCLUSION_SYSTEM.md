# Intro and Conclusion System

**Purpose:** Single reference for how book title/subtitle, series mention, author intro, narrator intro (AI voice), and first/last chapter behavior work in Phoenix V4.  
**Authority:** [PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) §23 (Identity & Audiobook), [INTRO_CONCLUSION_VARIATION_SPEC.md](../specs/INTRO_CONCLUSION_VARIATION_SPEC.md) (controlled variation).

---

## 1. Pre-intro: what the listener hears before Chapter 1

The **narrator** (AI voice identified by `narrator_id`) reads a single, ordered set of blocks before Chapter 1. This is the **audiobook pre-intro** (Writer Spec §23.4). Order is fixed and never reordered:

1. **narrator_intro** — Narrator introduces themselves (e.g. “My name is X, and I will be guiding you through this audiobook”).
2. **book_title_line** — States the book title and author name (e.g. “You are listening to *Title*, written by Pen Name”). Subtitle may be included when supplied (e.g. from naming engine).
3. **series_line** — (Optional.) States series name. Only included when the book is part of a series (`series_id` set and `include_series_line=True`).
4. **author_intro** — One sentence: “This book was written by {pen_name}.”
5. **author_background** — 2–4 sentences from author’s bio (condensed for audio; persona-aware).
6. **why_this_book** — 3–5 sentences from why_this_book asset (condensed; specific, not marketed).
7. **transition_line** — One sentence handing off to Chapter 1 (e.g. “Chapter One.”).

**Voice:** One narrator voice (AI) for the **whole** pre-intro. The narrator is chosen by `narrator_id` (resolved from brand when not supplied). Variation is **textual** (wording of blocks), not voice-switching, unless explicitly configured per locale/brand.

**Source of text:**  
- Author-facing blocks come from author assets: `assets/authors/{author_id}/audiobook_pre_intro.yaml` (or registry `assets_path`).  
- When **Controlled Intro/Conclusion Variation** is enabled, some blocks (narrator_intro, book_title_line, why_this_book, transition_line, and optionally series_line) may be chosen from per-brand pattern banks instead of or in addition to YAML; see [INTRO_CONCLUSION_VARIATION_SPEC.md](../specs/INTRO_CONCLUSION_VARIATION_SPEC.md) and [authoring/AUTHOR_ASSET_WORKBOOK.md](authoring/AUTHOR_ASSET_WORKBOOK.md) (stable vs dynamic blocks).

---

## 2. Book title and subtitle

- **book_title_line** is the spoken line that states the book title (and usually the author).  
- **Preferred:** Runtime injection from the naming engine (e.g. after format selection or Stage 3). If the pipeline supplies a runtime title (and optional subtitle), that is used to build the spoken line.  
- **Conflict rule:** If `audiobook_pre_intro.yaml` has a **fixed** `book_title_line` and the runtime supplies a **different** title, the build **fails** with a clear conflict message (no silent override). Content team must either supply a dynamic title at compile time or use one fixed line per asset (see AUTHOR_ASSET_WORKBOOK).  
- Chapter title naming is a separate system (naming engine / chapter titles); when it produces book-level title/subtitle, that output can feed this pre-intro block.

---

## 3. Series mention

- **series_line** is included only when:
  - The book has a `series_id`, and  
  - `include_series_line=True` (e.g. from format or series policy).  
- When included, it states the series name (and optionally position). Content may be fixed per series or from pattern banks when variation is enabled; see INTRO_CONCLUSION_VARIATION_SPEC.

---

## 4. Author intro and background

- **author_intro** and **author_background** are **stable** per author: they always come from `audiobook_pre_intro.yaml` (author assets). They are not chosen from pattern banks.  
- author_intro: one sentence naming the author.  
- author_background: 2–4 sentences from the author’s bio, condensed for audio and persona-aware.

---

## 5. Narrator intro (AI voice)

- The **narrator** is the AI voice that reads the entire pre-intro (and typically the rest of the audiobook).  
- Narrator identity is set by **narrator_id** (from BookSpec; resolved from `config/brand_narrator_assignments.yaml` when not supplied).  
- **narrator_intro** is the block where the narrator introduces themselves (e.g. name and role). When Controlled Intro/Conclusion Variation is enabled, this block may be chosen from per-brand narrator intro variants (8–12); otherwise it comes from author’s `audiobook_pre_intro.yaml`.  
- Voice behavior (engine, locale) is governed by narrator registry and TTS config, not by this doc.

---

## 6. First and last chapter (recognition and integration)

- **First chapter** is always **recognition** (arc rule). The opening chapter’s emotional role is recognition; slot structure (HOOK, STORY, REFLECTION, etc.) is unchanged. Optional **opening recognition style** (e.g. sensory cold-open, question-led) is applied as a **soft ranking bias** for chapter 0 only (see INTRO_CONCLUSION_VARIATION_SPEC).  
- **Last chapter** is always **integration**. The closing chapter’s emotional role is integration.  
- **STILL-HERE** (or equivalent closing beat) appears **once per book**, in the **final chapter** only (emotional_governance_rules).  
- **No chapter-order language:** Phrases like “next chapter” or “final chapter” are banned in format_rules so we don’t expose position.

---

## 7. Conclusion: integration ending and carry line

- The **final chapter** closes with the **INTEGRATION** slot. Optional **integration ending style** (e.g. stillness close, witness close) is applied as a soft ranking bias for which INTEGRATION atom is chosen.  
- A **carry line** (one short phrase per book, from a chosen carry-line style) may be appended to or used with the final INTEGRATION content. It contributes to **ending_signature** for cap/duplicate gates. See INTRO_CONCLUSION_VARIATION_SPEC for caps and signatures.

---

## 8. Where to read more

| Topic | Doc / Spec |
|-------|------------|
| Pre-intro block order, content rules | Writer Spec §23.4 |
| Author assets (bio, why_this_book, audiobook_pre_intro) | [authoring/AUTHOR_ASSET_WORKBOOK.md](authoring/AUTHOR_ASSET_WORKBOOK.md) |
| Stable vs dynamic blocks, runtime title | AUTHOR_ASSET_WORKBOOK; INTRO_CONCLUSION_VARIATION_SPEC |
| Variation, caps, signatures, tests | [specs/INTRO_CONCLUSION_VARIATION_SPEC.md](../specs/INTRO_CONCLUSION_VARIATION_SPEC.md) |
| Pipeline, config locations | [SYSTEMS_V4.md](SYSTEMS_V4.md); [specs/OMEGA_LAYER_CONTRACTS.md](../specs/OMEGA_LAYER_CONTRACTS.md) |
| Chapter title / naming engine | (Separate naming engine docs/specs when present.) |
