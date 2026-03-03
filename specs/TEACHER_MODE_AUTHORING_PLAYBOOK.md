# Teacher Mode Authoring Playbook

## Content team workflow for Teacher Mode V4 books

**Authority:** [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md) — dev spec.  
**Audience:** Content leads, teacher onboarding, writers who add or approve teacher-scoped atoms.

---

## 0. Why this exists

Teacher Mode books use a **real teacher's teachings** as the source of truth. The pipeline does not invent or summarize the teacher at runtime; it **assembles** from teacher-scoped atoms that were either:

- **Manually authored** (you write them from the teacher's materials), or  
- **Gap-filled offline** (the gap-fill tool generates candidates from the teacher KB; you approve or reject).

This playbook is the content-team sequence so that Teacher Mode stays governable and auditable.

---

## 1. Onboard a teacher (one-time)

Before any Teacher Mode book can be compiled for a teacher:

### 1.1 Add teacher to registry

A dev or content lead adds an entry to `config/teachers/teacher_registry.yaml`:

- `display_name`, `kb_id`, `doctrine_profile`
- `allowed_topics`, `disallowed_topics`
- `allowed_engines`, `allowed_resolution_types`, `identity_shift_allowed`
- `teacher_mode_defaults`: e.g. `require_teacher_story: true`, `require_teacher_exercise: true`

Without this, the system will not accept the teacher for compilation.

### 1.2 Create teacher bank directory

Under `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/` create:

- `raw/` — place the teacher's source files (pdf, md, txt, docx, transcripts). **Never** used at runtime; only for KB build and gap-fill.
- `doctrine/` — add `doctrine.yaml` with: forbidden claims, tone boundaries, glossary/canonical phrases, prohibited outcomes, exercise safety notes (especially for trauma-related material).
- `candidate_atoms/` and `approved_atoms/` (with subdirs HOOK, SCENE, STORY, EXERCISE, INTEGRATION as needed) — may be empty at first.
- `artifacts/` — for mining_runs, gap_reports, approval_logs.

### 1.3 Build the knowledge base

Run:

```bash
python3 tools/teacher_mining/build_kb.py --teacher <teacher_id>
```

This indexes `raw/` so the gap-fill tool can retrieve supporting passages. No book compile uses the KB directly; only offline tools do.

---

## 2. Plan a Teacher Mode book

Teacher Mode books use the same Stage 1/2/3 pipeline as regular V4 books, with a teacher scoped to the book.

- **Who assigns the teacher?** Either the catalog/planning process (e.g. `teacher_allocator.py`) or a human specifying `--teacher <teacher_id>` when running the pipeline. The catalog planner itself does not "choose" the teacher; something upstream must supply it.
- **Arc is still required.** No arc = no compile. The arc (persona, topic, engine, format) must be compatible with the teacher's `allowed_topics` and `allowed_engines`.

---

## 3. Check coverage and gaps

Before compile (or when you want to see what’s missing):

```bash
python3 phoenix_v4/qa/report_teacher_gaps.py \
  --plan artifacts/plan.json \
  --arc config/source_of_truth/master_arcs/...yaml \
  --teacher <teacher_id> \
  --out artifacts/gaps.json
```

The report lists:

- Missing STORY counts by band (e.g. band_3, band_4)
- Missing EXERCISE counts by type (e.g. somatic, reflection)

If there are no gaps, you can proceed to compile. If there are gaps, either:

- Add **manually authored** atoms into the teacher’s `approved_atoms/` (following the same atom schema and doctrine), or  
- Run the **gap-fill pipeline** to generate candidates, then approve (§4).

---

## 4. Fill gaps (offline only)

Gap-fill generates **candidate** atoms from the teacher KB. It does not write to approved_atoms.

### 4.1 Run gap-fill

```bash
python3 tools/teacher_mining/gap_fill.py \
  --teacher <teacher_id> \
  --gaps artifacts/gaps.json \
  --out SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/candidate_atoms
```

Output: candidate atoms under `candidate_atoms/` and a Gap-Fill Run Report in artifacts.

### 4.2 Approve or reject candidates

Use the approval tool with teacher scope:

```bash
python3 tools/approval/approve_atoms.py --teacher <teacher_id> list
python3 tools/approval/approve_atoms.py --teacher <teacher_id> approve <atom_id>
```

Approval moves atoms from candidate to approved and adds approval metadata. The tool never rewrites content.

- **Sensitive families:** Teacher doctrine (or global no-auto-promotion list) may forbid auto-promotion for certain topics (e.g. grief, trauma). Those atoms require human approval only.
- **Provenance:** Gap-filled atoms include `source_refs` (doc_id, span, quote_hash). Keep these for audit; do not strip them.

---

## 5. Compile the book

Once coverage exists (no gaps, or gaps filled and approved):

```bash
python3 scripts/run_pipeline.py \
  --topic <topic> --persona <persona> --structural-format <F00X> \
  --arc <path-to-arc.yaml> \
  --teacher <teacher_id> --teacher-mode \
  --out artifacts/teacher_mode.plan.json
```

If a required slot still has no atom, the compiler **fails** and emits a Gap Report. It does not generate content at runtime.

---

## 6. Content-team rules of thumb

| Do | Don’t |
|----|--------|
| Put only teacher-sourced or gap-filled-and-approved content in teacher approved_atoms | Put raw teacher text or ad-hoc “summaries” into runtime content |
| Keep doctrine.yaml updated when the teacher’s boundaries change | Let the system invent new doctrine or meaning at runtime |
| Use gap report → gap-fill → approve as the only way to add generated atoms | Expect the compiler to “fill in” missing slots |
| Treat approval as the gate for all candidate atoms | Auto-promote in sensitive families (unless policy explicitly allows) |

---

## 7. When something goes wrong

- **Compile fails with “gap” or “no atoms for slot”:** Run `report_teacher_gaps.py`; add manual atoms or run gap_fill and approve.
- **Candidate atoms fail lint/cadence/doctrine:** Fix is in the offline pipeline (repair loop or manual edit of candidates before re-submission). The spec allows max 2 repair attempts; after that, treat as manual authoring.
- **Teacher not found or not allowed for topic/engine:** Check `config/teachers/teacher_registry.yaml` (allowed_topics, allowed_engines) and the arc’s topic/engine.

---

## 8. Teacher Mode voice and structure

**Authority:** [TEACHER_MODE_STRUCTURAL_SPEC.md](./TEACHER_MODE_STRUCTURAL_SPEC.md)

### 8.1 Author voice

In Teacher Mode the author is **interpreter and applicator**, not originator. Use framing like "In [Teacher]'s work…", "What [Teacher] calls…", "Through the lens of [Teacher]…". Do **not** use "I discovered…", "My breakthrough was…", or "This method guarantees…". Tone: grounded, respectful, clear, applied — never devotional or mythologizing.

### 8.2 Pre-Intro chapter

Every Teacher Mode book must include a short **Pre-Intro** (e.g. "A Note on the Teachings", "Before We Begin") before Chapter 1 that: (1) clarifies you were not a direct student and encountered the work through books/talks; (2) states why this teacher matters for this topic; (3) states scope and boundary (application, not replacement); (4) invites the reader to go to the source. 900–1200 words max; no biography or authority claims.

### 8.3 Exercise attribution

- Direct from teacher: "Drawn from…"
- Adapted: "Inspired by…"
- Derived from pattern: "In the spirit of…"
- Never claim "This is exactly how [Teacher] taught it" unless verified.

### 8.4 Teacher Presence Score (TPS)

The system can report **TPS per chapter** (structural only: STORY/EXERCISE slot counts). Minimum TPS threshold is configurable; below-threshold chapters are flagged in the coverage report. See [TEACHER_MODE_STRUCTURAL_SPEC.md](./TEACHER_MODE_STRUCTURAL_SPEC.md) §3.

---

## 9. References

- **Dev spec:** [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md)  
- **Structural (voice, Pre-Intro, TPS):** [TEACHER_MODE_STRUCTURAL_SPEC.md](./TEACHER_MODE_STRUCTURAL_SPEC.md)  
- **Integrity (cross-series):** [TEACHER_INTEGRITY_SPEC.md](./TEACHER_INTEGRITY_SPEC.md)  
- **Portfolio (brand, anti-spam):** [TEACHER_PORTFOLIO_PLANNING_SPEC.md](./TEACHER_PORTFOLIO_PLANNING_SPEC.md)  
- **Arc-First (system authority):** [PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](./PHOENIX_ARC_FIRST_CANONICAL_SPEC.md)  
- **Stage contracts:** [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md)
