# Creative Quality Gate v1

**Purpose:** Increase probability of emotional impact without bloating governance. Post-compile only; read-only; no planner/solver/release-wave changes.

**Placement:** Runs after Stage 3 compile, before release-wave gating.

**Module:** `phoenix_v4/gates/check_creative_quality_v1.py`

**Config:** `config/creative_quality_v1.yaml`

**Output:** `artifacts/ops/book_quality_summary_{book_id}_{date}.json` (optional `.md`)

---

## What It Measures (Deterministic Heuristics Only)

1. **Arc emotional motion** — distinct bands, rising/falling transitions, flat-segment count. FAIL if too few bands or no rise/fall; WARN if too many flat segments.
2. **Transformation density** — share of chapters containing insight markers, reframe patterns, or identity-shift phrases. FAIL if below configured minimum (default 60%).
3. **Specificity** — abstract vs concrete marker counts per chapter; WARN/FAIL when abstract-dominant share exceeds thresholds.
4. **Ending strength** — last N chapters must include compression, identity, and action-directive patterns. FAIL if any missing.
5. **Lexical rhythm** — sentence-length variance; WARN/FAIL if standard deviation below thresholds (flat rhythm = mechanical feel).

No LLM scoring, no rewriting, no semantic embeddings. Structural signals only.

---

## CLI

```bash
PYTHONPATH=. python3 phoenix_v4/gates/check_creative_quality_v1.py \
  --book artifacts/book_002.plan.json \
  --config config/creative_quality_v1.yaml \
  --out-dir artifacts/ops
```

Optional: `--md` to also write a markdown summary.

**Exit codes:** `0` PASS, `2` WARN, `1` FAIL.

---

## Input

Reads compiled book JSON. Chapter text is taken (in order) from:

- `compiled_book.chapters[*].text`
- `chapters[*].prose`
- `compiled_chapters[*].text`

Band sequence from top-level `dominant_band_sequence` or per-chapter `band`. If no chapter text found → `BOOK_INPUT_INVALID` (FAIL). If no band sequence → arc_motion fails with `MISSING_BAND_SEQUENCE`.

---

## Overall Logic

- Any FAIL in arc_motion, transformation, or ending_strength → overall **FAIL**
- Else if ≥2 WARN across signals → overall **WARN**
- Else **PASS**

---

## Schema

Output conforms to `schemas/book_quality_summary_v1.schema.json`. Summary includes `signals` (per-signal status and reasons), `warnings`, and `fails`.

---

## Do Not Add v2 Until…

Human reactions to shipped books have been observed. This is the last quality layer before shipping; keep it minimal.
