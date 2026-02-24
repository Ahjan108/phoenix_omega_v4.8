# Teacher Integrity Spec

## Guardrails Across Series and Across Books

**Status:** Canonical  
**Subordinate to:** [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md)  
**Audience:** Devs, content governance, release gates

Prevent **drift** across multiple books and series: vocabulary, resolution type, exercise identity, teacher presence. Structural monitoring only — no prose scoring, no sentiment.

---

## 1. Problem: Drift Happens Quietly

Across many books, drift can occur:

- Vocabulary slowly shifts away from teacher's terms
- Teacher concepts get diluted
- Exercises become generic
- Author voice dominates
- Resolution type creeps toward triumph
- Engine severity escalates beyond teacher doctrine
- Topic coverage expands beyond teacher's authentic domain

Drift is slow and structural. So we need **cross-book** enforcement, not just per-book checks.

---

## 2. Guardrail Layers

Conceptually:

- **Layer 0:** Teacher Doctrine (allowed_topics, allowed_engines, resolution_types, doctrine.yaml)
- **Layer 1:** Arc-First structure
- **Layer 2:** Omega / business orchestration
- **Layer 3:** Teacher Integrity Monitoring (cross-series)

Layer 3 does **not** modify runtime content. It monitors aggregate patterns and reports (or fails CI).

---

## 3. Guardrail Categories

We enforce integrity across five domains:

1. Doctrine boundaries (resolution, engine, topic)
2. Vocabulary stability (core_terms, forbidden_terms)
3. Resolution temperature (peak band)
4. Exercise identity (% from teacher pool, type distribution)
5. Teacher presence distribution (TPS average across books)

---

## 4. Doctrine Boundary Guardrail

From `config/teachers/teacher_registry.yaml`:

- `allowed_resolution_types`
- `identity_shift_allowed`
- `allowed_engines`
- `allowed_topics` / `disallowed_topics`

**Across all teacher books (when we have a book registry or plan artifacts):**

- % of books violating preferred resolution?
- Any identity_shift when disallowed?
- Any engine outside allowed_engines?
- Any topic outside allowed_topics or in disallowed_topics?

**Tool:** `scripts/teacher_integrity_report.py` — per-teacher report.  
**Tool:** `scripts/teacher_integrity_dashboard.py` — aggregate summary; can consume multiple reports or scan teacher_banks + registry.

---

## 5. Vocabulary Stability Guardrail

Doctrine can define (add to doctrine.yaml or teacher registry):

```yaml
core_terms: [resistance, awareness, subtle grasping]
forbidden_terms: [manifestation, vibration, guaranteed outcome]
```

**Checks (structural string presence only; no NLP):**

- Core term frequency in approved atom bodies (per book or per bank)
- Forbidden term detection in any approved atom → hard fail

If core term usage drops below a threshold across series, or forbidden term appears → flag or fail.

---

## 6. Resolution Temperature Guardrail

Across books:

- Check average peak intensity band (from arc or compiled plan).
- If teacher prefers e.g. `peak_intensity_limit: 4` and many books have peak band 5 → drift toward melodrama.
- Alert threshold: e.g. >10% of books with band 5 → review.

---

## 7. Exercise Identity Guardrail

Teacher Mode books should feel like the teacher's practice lineage.

- Track: % of EXERCISE atoms from teacher pool (when teacher_mode, 100% by definition; useful when comparing to non-teacher books).
- Exercise type distribution (if atoms are tagged): e.g. breath_awareness, somatic_scan, journaling.
- If "generic" exercise share creeps up across releases → teacher dilution flag.

---

## 8. Teacher Presence Distribution (Across Series)

- TPS average per book (from `teacher_presence_report.py`).
- If average TPS across a wave < target → flag brand-level review.

---

## 9. Topic Expansion Guardrail

- If teacher has `allowed_topics: [anxiety, shame]` and a plan requests topic `productivity_hacks` → **hard block** at planner stage.
- No "marketing expansion drift."

---

## 10. Implementation

### 10.1 Per-teacher report

`scripts/teacher_integrity_report.py --teacher <id> [--out report.json]`

- Load teacher registry + doctrine (allowed_*, core_terms, forbidden_terms).
- Scan `SOURCE_OF_TRUTH/teacher_banks/<id>/approved_atoms/` for term counts, atom counts by slot type.
- Output: resolution/engine summary (from registry only; book-level requires plan registry), vocabulary stats, exercise counts, any violations.

### 10.2 Dashboard

`scripts/teacher_integrity_dashboard.py [--reports dir] [--out summary.json]`

- Run or load per-teacher reports; aggregate.
- Output: TEACHER INTEGRITY SUMMARY, doctrine violations, vocabulary stability, TPS averages, overall drift risk (LOW / MEDIUM / HIGH).

### 10.3 CI

Before publishing a teacher wave:

- Run `teacher_integrity_dashboard`.
- Archive report in `artifacts/`.
- No report → no release (policy).

---

## 11. What This Does NOT Do

- Does not score prose
- Does not analyze sentiment
- Does not alter compile
- Does not add runtime checks
- Does not add emotional entropy metrics

Only **structural metadata and distribution** monitoring.
