# Intro/Conclusion Variation Spec (Controlled)

**Authority:** Controlled Intro/Conclusion Variation plan.  
**Purpose:** Canonical description of pre-intro block variation, opening/ending styles, caps, signatures, and delivery gates. Subordinate to [PHOENIX_V4_5_WRITER_SPEC.md](./PHOENIX_V4_5_WRITER_SPEC.md) §23 (Identity & Audiobook) and arc rules (first chapter = recognition, last = integration).

**See also:** [../docs/INTRO_AND_CONCLUSION_SYSTEM.md](../docs/INTRO_AND_CONCLUSION_SYSTEM.md) (how book title, series, author, narrator intro work); [../docs/authoring/AUTHOR_ASSET_WORKBOOK.md](../docs/authoring/AUTHOR_ASSET_WORKBOOK.md) (stable vs dynamic blocks).

---

## 1. Invariants (unchanged)

- **§23.4 block order** is fixed and never reordered:  
  `narrator_intro → book_title_line → series_line? → author_intro → author_background → why_this_book → transition_line`.
- **First chapter** = recognition (arc rule); **last chapter** = integration; **STILL-HERE** once, final chapter only (emotional_governance_rules).
- **No chapter-order language** ("next chapter", "final chapter") — banned in format_rules.
- Variation is **inside** each block (wording patterns), not reordering blocks.
- **One narrator voice** for the whole pre-intro (AI voice per narrator_id); variation is textual only unless configured per locale/brand.

---

## 2. Pre-intro: stable vs dynamic blocks

| Block             | Stable (author/brand) | Dynamic (per book) | Notes |
|-------------------|------------------------|--------------------|--------|
| narrator_intro    | —                      | Optional           | 8–12 variants per brand when variation enabled. |
| book_title_line   | —                      | Yes                | Prefer runtime from naming engine; validate vs YAML. |
| series_line       | —                      | Yes                | Only when series_id set and include_series_line=True. |
| author_intro      | Yes                    | —                  | Always from audiobook_pre_intro.yaml. |
| author_background | Yes                    | —                  | Always from audiobook_pre_intro.yaml. |
| why_this_book     | —                      | Yes                | From pattern bank (pre_intro_frames) or YAML. |
| transition_line   | —                      | Yes                | 8–12 variants per brand. |

**Stable** = single value per author, loaded from author assets.  
**Dynamic** = may be chosen from per-brand pattern banks (deterministic pick) or runtime (e.g. book title).

---

## 3. Source-of-truth precedence

- **Global flag:** `pattern_bank_overrides_yaml` (in `config/source_of_truth/intro_ending_variation.yaml`).
- When **true:** if both `audiobook_pre_intro.yaml` and the pattern bank have a value for a dynamic block, the **pattern bank** selection wins.
- When **false:** the **YAML** value wins.
- Enforced globally; no per-brand override of this flag.

---

## 4. Hard fallback behavior

- If **pattern bank is missing** for a brand/block: use the value from `audiobook_pre_intro.yaml` for that block.
- If **YAML value is also missing** for that block: **fail** for required blocks (narrator_intro, book_title_line, author_intro, author_background, why_this_book, transition_line); **never** silently emit empty strings for required blocks.
- Optional blocks (e.g. series_line) may be omitted when missing.

---

## 5. Title/series handling

- **book_title_line:** Prefer runtime injection from naming engine (e.g. after Stage 3 or format selection). If YAML contains a fixed `book_title_line` and runtime supplies a different title, **fail** with a clear conflict message (no silent override). Document in AUTHOR_ASSET_WORKBOOK: either supply dynamic title at compile time or use one fixed line per asset.
- **series_line:** Include only when `series_id` is set and `include_series_line=True`. Content may be fixed per series; pattern bank does not replace when fixed per series.

---

## 6. Signatures (scoped; do not mix)

- **pre_intro_signature:** Hash of the **full resolved pre-intro text** (all blocks in §23.4 order, concatenated). SHA256, first 16 chars. Used only for intro caps and duplicate gate.
- **ending_signature:** Hash of **final integration slot content + chosen carry line** (final chapter only). SHA256, first 16 chars. Used only for ending caps and duplicate gate.
- Do **not** combine intro and ending into one cap key; caps and duplicate checks use the two signatures separately.

---

## 7. Caps and duplicate gate

- **Window:** Calendar quarter in brand locale time (canonical; e.g. from config/localization or brand territory). Format: `YYYY-Qn`. Same window for all runners so 15%/20% do not vary by env.
- **Intro cap:** Same `pre_intro_signature` ≤ 15% of books in that brand in the quarter.
- **Ending cap:** Same `ending_signature` ≤ 20% of books in that brand in the quarter.
- **Implementation:** `artifacts/pre_intro_signatures.jsonl` records per book: `brand_id`, `quarter`, `pre_intro_signature`, `ending_signature`. When resolving, if adding this book would exceed cap: **reselect** (e.g. next variant by seed) up to **max_retries** (e.g. 5). If after max retries the signature is still over cap: **fail** with an **explicit error** and **candidate alternatives** (e.g. up to 3 suggestions). No silent fallback; no deadlock loop.
- **Duplicate gate:** If `pre_intro_signature` (or `ending_signature`) already appears in the quarter window for that brand, reselect up to max_retries; then fail with explicit message and candidate alternatives.

---

## 8. Delivery safety gates

- **Unresolved placeholders:** Fail if resolved pre-intro text contains `{{...}}`, `{placeholder}`, or markdown artifacts (`#`, `**` as raw).
- **No-leak:** Fail if output contains literal `{}`, `---` (metadata block boundary), or metadata labels (e.g. `id:`, `path:`) as content.
- **Block order:** Emit only §23.4 block keys in order; no unknown keys.
- **Required blocks when author_id set:** narrator_intro, book_title_line, author_intro, author_background, why_this_book, transition_line must be present and non-empty after resolution. series_line optional.

Validator: `phoenix_v4/qa/validate_pre_intro.py`. Run after pre-intro resolution and before writing the plan.

---

## 9. Opening chapter (chapter 1 only)

- **Invariant:** First chapter remains **recognition**; no change to arc or slot structure.
- **Variation:** Opening recognition style (e.g. sensory cold-open, direct second-person, micro-story, question-led). Applied as **ranking bias** in chapter-0 slot resolution (e.g. boost HOOK/STORY atoms with matching `opening_style` metadata). Do **not** use hard filters; if no atom matches, fall back to default ranking.
- **Selection:** Deterministic (e.g. hash(seed + topic_id + persona_id) % len(styles)); store `opening_style_id` in plan. Cap: same opening_style_id ≤ 15% per brand/quarter (reuse signature index).

Config: `config/source_of_truth/opening_recognition_styles.yaml`.

---

## 10. Integration ending and carry-line (final chapter only)

- **Invariants:** Last chapter = integration; STILL-HERE once per book, final chapter only.
- **Integration ending style:** e.g. stillness close, action close, reframing close, witness close. **Soft bias:** rank INTEGRATION atoms for final chapter by matching `ending_style` metadata; if no match, fall back to default. Store `integration_ending_style_id` in plan. Contributes to ending cap (same ending_signature ≤ 20%).
- **Carry-line style:** e.g. declarative, permission, boundary, anti-spiral, body-anchor. One line per book from selected style, deterministically chosen. Final chapter only; contributes to **ending_signature** (final integration content + carry line).

Config: `config/source_of_truth/integration_ending_styles.yaml`, `config/source_of_truth/carry_line_styles.yaml`.

---

## 11. Feature flag (staged rollout)

- **Config:** `config/source_of_truth/intro_ending_variation.yaml`.
- **Flag:** `intro_ending_variation_enabled` (true/false).
- When **false:** Skip pattern-bank resolution and cap/duplicate gates; use only YAML values for pre-intro; do not compute pre_intro_signature / ending_signature; do not apply opening/ending/carry-line style selection.
- When **true:** Full behavior as in this spec. Enables staged rollout and rollback without code revert.

---

## 12. Required tests

- **Determinism:** Same inputs (seed, topic_id, persona_id, brand_id, author_assets, pattern banks) must produce the same resolved pre-intro blocks, pre_intro_signature, ending_signature, and style IDs.
- **No-leak:** Resolved pre-intro and final integration/carry text must not contain `{}`, `---`, metadata labels (`id:`, `path:`), or other internal tokens.
- **Cap/duplicate gate:** With a mock index at cap (15% intro or 20% ending), next book with same signature must trigger reselect; after max_retries with still-over-cap, assert failure with explicit error and non-empty candidate alternatives.
- **YAML vs runtime title conflict:** When audiobook_pre_intro.yaml has a fixed book_title_line and runtime supplies a different book_title, assert build fails with a clear conflict message.
- **Missing-bank fallback:** When pattern bank is missing for a brand/block but YAML has a value, assert that value is used. When both are missing for a required block, assert build fails (no empty string).

Tests: `tests/test_intro_ending_variation.py`.

---

## 13. Config and implementation reference

| Item | Location |
|------|----------|
| Feature flag & caps config | config/source_of_truth/intro_ending_variation.yaml |
| Per-brand pre-intro banks | config/source_of_truth/pre_intro/banks.yaml |
| Opening recognition styles | config/source_of_truth/opening_recognition_styles.yaml |
| Integration ending styles | config/source_of_truth/integration_ending_styles.yaml |
| Carry-line styles | config/source_of_truth/carry_line_styles.yaml |
| Pre-intro resolver | phoenix_v4/planning/pre_intro_resolver.py |
| Pre-intro validator | phoenix_v4/qa/validate_pre_intro.py |
| Render pre-intro | phoenix_v4/planning/author_asset_loader.py (render_audiobook_pre_intro) |
| Caps & quarter | phoenix_v4/planning/intro_ending_caps.py |
| Opening/ending/carry selection | phoenix_v4/planning/intro_ending_selector.py |
| Signature index artifact | artifacts/pre_intro_signatures.jsonl |

Pipeline: resolution and gates run in `scripts/run_pipeline.py` after loading author_assets and before writing the plan. Compiled plan carries resolved `author_assets["audiobook_pre_intro"]`, `pre_intro_signature`, `ending_signature`, `opening_style_id`, `integration_ending_style_id`, `carry_line_style_id`, `carry_line` when variation is enabled.
