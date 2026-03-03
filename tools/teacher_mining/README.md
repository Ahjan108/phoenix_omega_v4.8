# Teacher mining tools

- **intake_normalize.py** — **LLM intake pass (Teacher Authoring Layer).** Reads `raw/`, produces doctrine assets: `main_teaching_atoms.yaml`, `story_helpers.yaml`, `exercise_helpers.yaml`, `signature_vibe.yaml`, `content_audit.yaml`. Run once per teacher at intake; human review then downstream tools use these. See **specs/TEACHER_AUTHORING_LAYER_SPEC.md**.
- **build_kb.py** — Build teacher KB from `raw/` (RTF, txt, md) → `kb/index.json` with documents and chunks. Run after intake (or first if no authoring layer yet).
- **mine_kb_to_atoms.py** — Mine the KB into STORY, EXERCISE, QUOTE, and TEACHING atom banks.

## LLM intake pass (Authoring Layer)

Run first when onboarding a teacher so gap-fill and normalizers have doctrine-layer assets:

```bash
# Stub only (no API): writes placeholder YAML for all 5 assets + intake_manifest.json
python3 tools/teacher_mining/intake_normalize.py --teacher ahjan --dry-run

# With Anthropic API key: full extraction from raw/
export ANTHROPIC_API_KEY=...
python3 tools/teacher_mining/intake_normalize.py --teacher ahjan
```

Outputs go to `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/`. Content lead must set `reviewed_by` and `review_date` before downstream tools treat assets as authoritative.

## Mine KB to atoms

Requires KB built for the teacher (`python3 build_kb.py --teacher <id>`).

```bash
# Write to candidate_atoms/ (review then promote to approved_atoms)
python3 tools/teacher_mining/mine_kb_to_atoms.py --teacher ahjan

# Write directly to approved_atoms/ for immediate use in assembly
python3 tools/teacher_mining/mine_kb_to_atoms.py --teacher ahjan --approve
```

**Classification (heuristic):**

- **STORY** — Narrative markers (e.g. Angulimala, Buddha and salt, two brothers at river, tigress, Prince Siddhartha). Consecutive story chunks are merged into one atom.
- **EXERCISE** — Practice language (meditation, focus, breathe, mindfulness, sit and, step one, etc.).
- **QUOTE** — Short attributed quotes; known canonical quotes (Dhammapada, “three things matter”, “I have already stopped, Angulimala”) are also extracted from full docs.
- **TEACHING** — Core doctrinal content (Buddhism teaches, central to, path involves, inner light, right livelihood, etc.). All substantive doctrinal chunks not classified as STORY/EXERCISE/QUOTE go here; “core” teachings can be refined by human curation or a later tag.

**Output:** YAML atoms with `atom_id`, `body`, `band` (STORY only), and `teacher.source_refs` (doc_id, span, quote_hash) for provenance.

**Slot dirs:** STORY, EXERCISE, QUOTE, TEACHING. Format plans that use QUOTE or TEACHING slots will pull from these banks when teacher_mode is set.

**STORY band assignment:** STORY atoms get a band (1–5) from deterministic structural heuristics (tension/cost/crisis keywords), not sentiment. Use `--force-band N` to override all STORY bands. Target band distribution for arc flexibility: Band 1 ~15%, 2 ~20%, 3 ~30%, 4 ~20%, 5 ~15%.

---

## Identify core teachings (post-mining)

After mining TEACHING atoms, run:

```bash
python3 tools/teacher_mining/identify_core_teachings.py --teacher ahjan
```

- Reads `approved_atoms/TEACHING/*.yaml` and `doctrine/doctrine.yaml` (glossary).
- Identifies core teachings by glossary frequency, cross-atom phrase repetition, and doc spread (no NLP/embeddings).
- Writes `doctrine/core_teachings.yaml` with `core_teachings` (id, canonical_phrase, atom_ids, frequency, glossary_term).
- Updates each TEACHING atom with `tags: [core: <id>, ...]` for concept anchoring and TPS/vocabulary stability.

Use `--no-update-atoms` to only generate `core_teachings.yaml` without modifying atom files.

---

## Narrative expansion pass (STORY)

After mining, expand short or low-band STORY atoms to improve Arc coverage (band 2–4):

```bash
python3 tools/teacher_mining/expand_story_atoms.py --teacher ahjan
```

- **Input:** `candidate_atoms/STORY/*.yaml` (or `--stories <dir>`).
- **Eligibility:** length &lt; 180 words, band ≤ 3, has escalation keyword or low band, has protagonist; never expand crisis or sacred/historical stories.
- **Expansion:** Deterministic templates only: pattern amplification, cost clarification, teaching anchor (glossary). Max +120 words; additions marked `[EXPANDED]` in body.
- **Output:** New candidate atoms with `synthesis_method: narrative_expand_v1`, `expanded_from`, preserved `source_refs`. Still requires approval.

Pipeline order: `build_kb` → `mine_kb_to_atoms` → `identify_core_teachings` → `expand_story_atoms` → `normalize_story_atoms` → `normalize_exercise_atoms` → candidate review → approval → compile. CI: `scripts/ci/check_structural_entropy.py` (Teacher Mode). See specs/TEACHER_MODE_NORMALIZATION_SPEC.md.

---

## Simulate band distribution

Check current (or post-expansion) STORY band distribution vs target ratios:

```bash
python3 tools/teacher_mining/simulate_band_distribution.py --stories SOURCE_OF_TRUTH/teacher_banks/ahjan/candidate_atoms/STORY
```

Target (teacher-dependent): Band 1: 10–15%, 2: 20%, 3: 30–35%, 4: 20–25%, 5: 5–10%.

---

## Normalize STORY and EXERCISE atoms

After mining (and optional expansion), normalize for length, tension, teacher anchor, and structure family:

```bash
python3 tools/teacher_mining/normalize_story_atoms.py --teacher ahjan
python3 tools/teacher_mining/normalize_exercise_atoms.py --teacher ahjan
```

- **STORY:** `structure_family` (NARRATIVE|CASE_STUDY|PARABLE|DIALOGUE), 120–450 words, tension/teacher anchor if missing, optional intro/outro.
- **EXERCISE:** `exercise_family` (GROUNDING|BREATH|ACTIVATION|COMPASSION|INTENTION), 90–280 words, steps/time/closure if missing. Use `--no-framing` to skip author/teacher framing.

---

## Structural entropy CI (Teacher Mode)

Before publish:

```bash
python3 scripts/ci/check_structural_entropy.py --plan <compiled-plan.json> [--book-spec <book-spec.json>]
```

Fails if STORY &lt; 120 words, EXERCISE &lt; 90 words, family concentration &gt; 60%, or core anchors &lt; 4. See specs/TEACHER_MODE_NORMALIZATION_SPEC.md.
