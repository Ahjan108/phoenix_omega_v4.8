# Translation quality contracts

Quality contracts for locale translation pipelines: glossary, release thresholds, golden regression.

- **glossary.yaml** — Canonical terms and preferred translations per locale.
- **release_thresholds.yaml** — Minimum quality scores and coverage to allow release.
- **golden_translation_regression.yaml** — Golden segments used for regression tests.

See docs/DOCS_INDEX.md § Translation and locale gate workflow.

## When enabling locales (added 2026-03-06)

The following content was added as part of the Pearl Prime structural upgrade and must be
included in any locale implementation:

**New slot types requiring translation:**
- `PIVOT` — 2–3 sentences naming what a story revealed (before teaching). Short; translate whole.
- `TAKEAWAY` — One thesis sentence per chapter, derived from `chapter_thesis[ch]` in the arc YAML.
  Source sentences are in `docs/CHAPTER_THESIS_BANK.md`. Translate those sentences per locale.
- `THREAD` — 1–2 sentences at close of INTEGRATION planting forward pull. Translate whole.
- `PERMISSION` — 2–4 second-person sentences giving chapter-specific emotional permission.
  Requires cultural review per locale. Permission language is culturally variable.

**Arc thesis sentences:**
All 457 master arcs now have (or will have) a `chapter_thesis` field — 20 thesis sentences per arc.
These must be translated and stored per locale alongside the arc. The TAKEAWAY slot text at
render time = the translated `chapter_thesis[ch]` for that chapter.

**Glossary priorities:**
Add translations for core brand terms used in thesis sentences across all engines:
`nervous system`, `the alarm`, `the mask`, `the pattern`, `the strategy`, `the cost`,
`somatic`, `watcher`, `false alarm`, `the thread`. These appear in TAKEAWAY and PIVOT text
at high frequency.

**Golden segments:**
When populating `golden_translation_regression.yaml`, include at least 2 examples each from
PIVOT, TAKEAWAY, and THREAD slot types so the regression covers the new slot content.
