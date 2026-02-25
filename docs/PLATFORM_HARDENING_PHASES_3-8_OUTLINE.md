# Platform Hardening — Phases 3–8 Operational Outline

**Context:** Publishing control surface; platform hardening program. Phases 1–2, 2.5, 5, and 6 are implemented. This document provides operational clarity for remaining phases.

---

## Phase 2.5 — Coverage health JSON dashboard schema ✅ Implemented

**Intent:** Stable contract for ops dashboards: heatmaps, aging alerts, pool velocity, deficit triage.

**Implemented:** `coverage_health_weekly_{date}.json` now has `schema_version: "1.0"`, `generated_at_utc`, `report_date`, `repo` (root + git commit), `config_snapshot`, `summary` (risk_counts, top_deficit_codes, aging, velocity), `tuples[]` (tuple_id, binding{}, arc{}, story_pool{}, bands{}, deficit_codes, risk), and `indices` (by_risk, by_persona, by_topic). Velocity uses previous week’s report when available.

---

## Phase 3 — Planner-time band-aware scoring

**Intent:** When selecting STORY atoms per chapter, add a small band-diversity term so the planner prefers variety and discourages same-band runs.

**Formula (keep small; do not let it dominate structure):**
- `score = structural_score + novelty_score + band_diversity_bonus`
- `band_diversity_bonus = +0.2` if candidate atom’s band is not yet represented in the book
- `band_diversity_bonus = -0.3` if candidate’s band has already been used 3+ times

**Where to implement:** The component that **scores or selects STORY candidates** (e.g. `slot_resolver.resolve_slot` for STORY, or the assembly compiler’s resolution loop). Today STORY is filtered by `required_band_by_chapter` then chosen via deterministic index; extend to:
1. Track per-band usage count across chapters already resolved.
2. When multiple STORY candidates satisfy the required band for the chapter, score them with the above bonus/penalty (or apply a tie-break that prefers under-represented bands and penalizes over-used bands).
3. Post-compile band guardrail remains the hard-fail (no change).

**Files to touch:** `phoenix_v4/planning/slot_resolver.py` and/or `phoenix_v4/planning/assembly_compiler.py` (where STORY slot resolution and used_atom_ids/used bands are known).

**Acceptance:** Same arc produces more band-diverse STORY sequences where pool allows; no regression on arc-required bands.

---

## Phase 4 — Entropy wrapper exclusion

**Intent:** Avoid normalization collision in entropy hashing by hashing only the semantic body, not teacher/wrapper/header boilerplate.

**Change:** In the **entropy hashing logic** (e.g. `scripts/ci/check_structural_entropy.py` or wherever structural fingerprint / entropy hash is computed):

Before fingerprint:
- Strip from the text (or exclude from the hashed content):
  - `teacher_intro`
  - `teacher_outro`
  - Wrapper prefix
  - Compression header
  - Style IDs

Hash only the **semantic body**.

**Files to touch:** Locate where entropy hash/fingerprint is built (e.g. `check_structural_entropy.py`, or a shared hashing helper). Add a normalization step that removes the listed wrappers/headers before hashing.

**Acceptance:** Two plans that differ only in teacher_intro/outro or style IDs produce the same entropy hash where semantic body is identical.

---

## Phase 5 — Brand emotional range ✅ Implemented

**Intent:** Arc required bands must fall within the brand’s allowed emotional range; reject at preflight. Do not clip bands—fail early.

**Implemented:** `config/catalog_planning/brand_emotional_range.yaml` (default + per-brand `min_band`/`max_band`). Tuple viability gate (and pipeline) loads range for `brand_id`; if any arc required band is outside [min_band, max_band], adds error `ARC_OUTSIDE_BRAND_EMOTIONAL_RANGE`. Pipeline passes `brand_id` into the gate (from teacher/brand resolution).

**Config:** `default` and `brands.<brand_id>` with `min_band`, `max_band`. Unlisted brands use default (1–5).

**Acceptance:** Arcs requiring band 1 or 5 when brand allows only 2–4 are rejected before Stage 1.

---

## Phase 6 — Batch release controls ✅ Implemented

**Intent:** Enforce caps per release wave and anti-homogeneity to prevent platform suppression.

**Implemented:** `phoenix_v4/ops/check_release_wave.py` + `config/release_wave_controls.yaml` + `tests/test_release_wave_controls.py`.

**Features:**
- Weekly caps: topic, persona, topic×persona, arc, engine, brand, band_sig, slot_sig, variation_sig, wave_fingerprint, teacher_id / teacher_mode
- Exact fingerprint clusters (arc|slot_sig|band_sig|variation); fail if cluster size > cap
- Near clusters (Jaccard on token set); configurable threshold and min cluster size
- Anti-homogeneity score (normalized entropy); fail if score < min_score
- Sliding-window share caps when `--history-index` provided (JSONL with release_week or publish_date)
- Report: JSON + MD with violations, top clusters, remediation hints

**CLI:** `--plans-dir`, `--calendar-week`, `--history-index`, `--out-dir`, `--config`, `--warn-only`. Exit 0 PASS, 1 FAIL, 2 WARN.

---

## Phase 7 — Teacher mode firewall (two additions)

### 7.1 — KB excerpt similarity check

**Intent:** Before approving a teacher atom derived from KB, ensure it is not a near-duplicate of an existing atom.

**Logic:**
- Hash KB-derived body (semantic content only, after stripping wrappers).
- Compare cosine similarity (or other defined metric) to existing approved atoms.
- Reject if similarity &gt; 0.85 to any existing atom.

**Where:** In the flow that approves/submits teacher atoms (e.g. validation or staging step before writing to `approved_atoms`). May live in `phoenix_v4/teacher/` or a validation script.

**Acceptance:** Duplicate KB reuse is blocked before approval.

### 7.2 — Normalization family rotation

**Intent:** Prevent structural homogenization at scale by rotating normalization “family” per atom.

**Config:** Add `normalization_family: {A, B, C}` (or similar) to teacher/schema config.

**Logic:**  
`family = hash(atom_id) % 3` → assign family A/B/C per atom. Downstream normalization or rendering uses the family to vary structure (e.g. intro/outro templates, style IDs).

**Where:** Teacher atom metadata or the component that applies normalization when rendering teacher content.

**Acceptance:** At scale, teacher books show rotated normalization families rather than a single pattern.

---

## Phase 8 — Governance simplification (no code change)

**Intent:** Keep governance boundaries clear; do not merge emotional governance into the planner.

**Decisions:**
- **OMEGA_LAYER_CONTRACTS** remain the sole contract authority for BookSpec → FormatPlan → CompiledBook.
- Emotional governance (e.g. band guardrails, brand emotional range) stays separate from planner logic; it guards different failure surfaces.
- Teacher Mode stays consolidated in the MASTER spec; no merge of emotional governance into planner.

**Action:** None beyond documentation and ensuring new gates (e.g. Phase 5 brand emotional range) are implemented as separate checks, not inside the planner core.

---

## Summary

| Phase | Deliverable | Owner | Status |
|-------|-------------|--------|--------|
| 2.5 | Coverage health JSON dashboard schema | Ops | **Implemented** |
| 3 | Band-aware scoring in STORY selection | Planning | Outline |
| 4 | Entropy hash excludes wrapper/header/style | CI / hashing | Outline |
| 5 | Brand emotional range validation at preflight | Gates / pipeline | **Implemented** |
| 6 | `check_release_wave.py` + rules | Ops | **Implemented** |
| 7.1 | KB similarity check before teacher approval | Teacher / validation | Outline |
| 7.2 | Normalization family rotation by atom_id | Teacher / rendering | Outline |
| 8 | Governance boundaries documented; no merge | Docs / process | Outline |
| **13-C** | **Deterministic Constraint Solver Wave Optimizer (DWO-CS)** | Ops | **Implemented** |

Implementing Phases 1 (tuple viability) and 2 (weekly coverage health) reduces most future instability; Phases 3–8 are scale and governance refinements. **Phase 13-C** provides deterministic wave selection (hard constraints + objective, no randomness); see [docs/PHASE_13_C_WAVE_OPTIMIZER.md](./PHASE_13_C_WAVE_OPTIMIZER.md).
