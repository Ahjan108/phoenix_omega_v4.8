# Quality — Standalone Creative QA Tools

**Purpose:** Directly increase book quality. Not governance, not telemetry, not compliance.

These tools are:

- **Lightweight** — deterministic heuristics, no deep NLP
- **Human-usable** — run manually or in review cycles
- **Standalone** — no system coupling; do not add to CI or wave solver

If integrated too deeply, you risk over-optimizing style.

---

## Tools

| Tool | Module | Use |
|------|--------|-----|
| **Story Atom Lint** | `story_atom_lint.py` | Catch weak STORY atoms before scaling (specificity, conflict, cost, pivot). |
| **Transformation Heatmap** | `transformation_heatmap.py` | Per-chapter recognition/reframe/challenge/relief/identity signals; ending strength. |
| **Memorable Line Detector** | `memorable_line_detector.py` | Highlight-density; editorial enhancement and marketing extraction. |
| **Marketing Assets from Lines** | `marketing_assets_from_lines.py` | Turn memorable-line JSON → quotes.csv, pin_captions, landing hooks, trailer lines, email subjects. |
| **Quality Bundle Builder** | `quality_bundle_builder.py` | Single artifact per book: runs heatmap + memorable + marketing in-process, computes CSI, writes schema-validated `book_quality_bundle_<book_id>_<date>.json`. |

---

## CLI

```bash
# Story Atom Lint (file or directory of .txt / .md atoms)
PYTHONPATH=. python3 phoenix_v4/quality/story_atom_lint.py --path atoms/... --json-out artifacts/ops/story_lint.json --fail-on FAIL

# Transformation Heatmap (--file compiled.txt OR --plan plan.json)
PYTHONPATH=. python3 phoenix_v4/quality/transformation_heatmap.py --plan artifacts/book_002.plan.json --json-out artifacts/ops/heatmap.json --ascii

# Memorable Line Detector (--file or --plan)
PYTHONPATH=. python3 phoenix_v4/quality/memorable_line_detector.py --plan artifacts/book_002.plan.json --json-out artifacts/ops/mem_lines.json

# Marketing assets from memorable lines
PYTHONPATH=. python3 phoenix_v4/quality/marketing_assets_from_lines.py \
  --mem-lines artifacts/ops/mem_lines.json \
  --brand phoenix --topic overthinking --persona nurses \
  --out-dir artifacts/marketing/book_002

# Quality bundle (one artifact per book: heatmap + memorable + marketing + CSI)
PYTHONPATH=. python3 -m phoenix_v4.quality.quality_bundle_builder \
  --rendered-text artifacts/rendered/book_001/book.txt \
  --compiled-plan artifacts/book_001.plan.json
```

---

## Recommended order

1. **Story Atom Lint** — story quality  
2. **Memorable Line Detector** — line quality  
3. **Transformation Heatmap** — chapter transformation  

Story quality → Line quality → Chapter transformation.

---

## Exit Codes (Quality Tools)

All quality tools use the same convention (see `base.py`):

| Code | Meaning | CI behavior |
|------|---------|-------------|
| **0** | PASS | Safe to publish — continue. |
| **1** | FAIL | Hard quality/structural violation — **must fix**. Automation should treat 1 as **blocking**. |
| **2** | WARN | Soft creative degradation — review recommended; continue but flag. |

- **story_atom_lint:** Exits by overall status: 1 if any atom FAIL, 2 if any WARN and no FAIL, 0 otherwise. Writes an ops artifact (schema `story_atom_lint_v1`) to `artifacts/ops/story_atom_lint_summary_<timestamp>.json` unless `--json-out` is set.
- **transformation_heatmap:** Returns 2 when `ending_weak`; else 0. Use rendered .txt when plan JSON has no chapter text.
- **memorable_line_detector / marketing_assets_from_lines:** Return 0 on success, 1 on input/error.

---

## Input contract

- **Story Atom Lint:** For files named `CANONICAL.txt`, the linter **parses per-atom blocks** (`## ROLE vNN --- metadata --- prose`) and lints each block separately. One strong atom no longer masks weak ones. Other `.txt`/`.md` files are linted as a single blob.
- **Transformation Heatmap & Memorable Line Detector:** **Rendered .txt is the preferred input** (Stage 6: `run_pipeline --render-book` or `render_plan_to_txt.py`). Plan JSON is supported only when it contains chapter text (`compiled_book.chapters[].text`). If plan JSON has no chapter text, the tool exits with a clear error directing you to use rendered .txt.

---

*See docs: [High-Impact Story Atom Upgrade Rubric](../../docs/HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md), [Narrative Tension Validator](../../docs/NARRATIVE_TENSION_VALIDATOR.md), [Insight Density Analyzer](../../docs/INSIGHT_DENSITY_ANALYZER.md), [Creative Quality Validation Checklist](../../docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md).*
