# Phoenix Deep Research Integration Spec
# (Narrative Depth Layer — v1.0)

---

## 0. Purpose

This spec operationalizes five structural additions extracted from deep research analysis into the Phoenix ARC-FIRST system.

All additions are:

* Declarative and structural
* Non-scoring
* Validator-compatible
* Zero architectural risk to existing compile pipeline

Nothing in this spec reintroduces prose inspection, tone heuristics, or emotional entropy metrics.

---

## 1. Overview of Changes

| # | What | Scope | Type |
|---|------|-------|------|
| 1 | `invisible_script` HOOK subtype | Atom schema + coverage_report.py | Schema addition |
| 2 | `belief_flip` STORY atom pattern | Writer Spec doc | Documentation |
| 3 | SCENE = micro-failure moment requirement | Writer Spec doc | Documentation |
| 4 | `milestone_type` field on INTEGRATION atoms | Atom schema | Schema addition |
| 5 | "Chapter must earn its place" quality test | ARC_AUTHORING_PLAYBOOK.md | Documentation |

---

## 2. Change 1 — `invisible_script` HOOK Subtype

### What

Add `invisible_script` as a valid HOOK atom subtype alongside existing types.

### Current HOOK type list (from WRITER_DEV_SPEC_PHASE_2)

```
sensory_image
context_drop
direct_address
imagery_hook
recognition_beat
```

### Updated HOOK type list

```
sensory_image
context_drop
direct_address
imagery_hook
recognition_beat
invisible_script        ← NEW
```

### Definition

`invisible_script` — A hook that names the reader's hidden operating belief before the reader has consciously named it themselves.

Not an inspirational opener. Not a scene description. A precise statement of the assumption running the reader's life.

### Persona Examples (for writer reference)

* NYC Executive: "You've optimized everything except the part that's quietly costing you."
* Healthcare Worker: "You learned to carry everyone else's pain before you learned to carry your own."
* Gen Z / Young Adult: "You've spent so long performing okayness that you've lost track of what okay actually feels like."

### Dev Implementation

**Atom schema:** Add `invisible_script` to the HOOK `type` enum.

**coverage_report.py — HOOK Type Distribution table:** Add `invisible_script` row.

**Coverage flags:** Add flag if `invisible_script` count == 0 for a given persona × topic pool. (This subtype is high-value and should be present in every pool.)

**No validator enforcement required.** Coverage flag is sufficient.

---

## 3. Change 2 — `belief_flip` STORY Atom Pattern

### What

Document a named atom-writing pattern for mid-band STORY atoms. No schema change. No validator. Writer spec only.

### Where to Add

`specs/WRITER_DEV_SPEC_PHASE_2.md` — add new section after Section 2 (Writer Production Rules).

### Content to Add

**Section 2A — STORY Atom Patterns**

Writers producing STORY atoms at Band 3–4 (escalation phase) should use the `belief_flip` pattern where appropriate.

**belief_flip — Three-Part Structure:**

1. **Name the wrong-but-common belief** — State the internal model the persona is operating from. Must feel true to the reader, not straw-man.
2. **Show it failing in a specific lived moment** — A concrete, recognizable micro-failure. Not abstract. Not general. The reader must recognize their own day.
3. **Offer a counter-intuitive but credible reframe** — Attack the frame, not the reader. The model is broken. The person is not.

**Example (NYC Executive, self-worth, shame engine, Band 3):**

1. Belief: "If I slow down, I'll fall behind. Momentum is everything."
2. Failure: The third Sunday in a row where you said you'd rest and instead opened your laptop at 9pm because stillness felt more dangerous than work.
3. Reframe: The momentum isn't protecting your performance. It's protecting you from having to feel what's underneath it.

**Guidance:**

* Do not use belief_flip in Band 1–2 (too early; reader not ready).
* Do not use belief_flip in Band 5 (cost chapter; too confrontational for reframe).
* Belief must be recognizable to persona, not generic.
* Reframe must be earned, not inspirational.

---

## 4. Change 3 — SCENE Atom Micro-Failure Requirement

### What

Add explicit requirement that SCENE atoms represent specific micro-failure moments. Writer spec only. No schema change. No validator.

### Where to Add

`specs/WRITER_DEV_SPEC_PHASE_2.md` — add to Section 2 (Writer Production Rules) as a new row.

### Row to Add to Writer Production Rules Table

| Rule | Description |
|------|-------------|
| SCENE atoms must represent micro-failure moments | Scenes depict a specific, recognizable moment of the engine pattern failing in daily life. Not abstract emotional states. Not general description. A moment the reader recognizes as their own. |

### Clarification for Writers

**Correct:** "She refreshes her inbox three times before the presentation starts. Not because she's expecting something. Because stillness feels like falling."

**Incorrect:** "She often feels anxious before important meetings at work."

The first is a micro-failure moment. The second is exposition. SCENE slots require the first.

No compiler enforcement. Writer-governed.

---

## 5. Change 4 — `milestone_type` on INTEGRATION Atoms

### What

Add optional `milestone_type` metadata field to INTEGRATION atoms. Enables post-cost chapters to declare what kind of landing the chapter produces.

### Schema Addition

Add to INTEGRATION atom metadata:

```yaml
integration:
  mode: BODY-LANDED | COST-VISIBLE | QUESTION-OPEN | FMT | STILL-HERE | SOMEONE-ELSE
  milestone_type: micro_win | open_question | grounded_reframe | still_present   ← NEW FIELD
```

`milestone_type` is optional. No compile failure if absent.

### Allowed Values

| Value | Meaning |
|-------|---------|
| `micro_win` | Reader gains small, felt sense of movement or relief. Post-cost descent chapters. |
| `open_question` | Reader is left with a question they will sit with. Escalation chapters. |
| `grounded_reframe` | Reader's frame shifts without triumphant resolution. Pre-final chapters. |
| `still_present` | Reader is affirmed in simply continuing to face the pattern. Use sparingly. |

### Arc Schema Addition (Optional)

Arc may declare expected `milestone_type` per chapter in `chapter_intent`.

Example:

```yaml
chapter_intent:
  6:
    milestone_type: micro_win
  7:
    milestone_type: grounded_reframe
  8:
    milestone_type: open_question
```

Arc declares intent. Compiler does not enforce. Structural declaration only.

### coverage_report.py Addition

Add `milestone_type` distribution to INTEGRATION Mode Distribution output. Flag if `micro_win` count == 0 (post-cost chapters need this).

---

## 6. Change 5 — Arc Quality Test Addition

### What

Add one line to the arc quality test in ARC_AUTHORING_PLAYBOOK.md.

### Where

Section 4 — ARC QUALITY TEST.

### Current content

> Ask: If prose were perfect, would this curve feel psychologically believable? If answer is no: Redesign.

### Updated content

> Ask: If prose were perfect, would this curve feel psychologically believable? If answer is no: Redesign.
>
> Then ask: If a chapter were removed, would the emotional journey break? If the answer is no: That chapter is not earning its place. Redesign.

No compiler enforcement. Arc author discipline.

---

## 7. Dev Deliverables Summary

| Deliverable | File | Action |
|-------------|------|--------|
| Add `invisible_script` to HOOK type enum | Atom schema | Code change |
| Add `invisible_script` to coverage_report.py HOOK table | scripts/coverage_report.py | Code change |
| Add invisible_script == 0 coverage flag | scripts/coverage_report.py | Code change |
| Add `milestone_type` to INTEGRATION atom schema | Atom schema | Code change |
| Add `milestone_type` to coverage_report.py INTEGRATION table | scripts/coverage_report.py | Code change |
| Add `micro_win == 0` coverage flag | scripts/coverage_report.py | Code change |
| Add `milestone_type` to arc `chapter_intent` (optional field) | Arc schema | Schema addition |
| Add `belief_flip` pattern section | specs/WRITER_DEV_SPEC_PHASE_2.md | Doc update |
| Add SCENE micro-failure rule | specs/WRITER_DEV_SPEC_PHASE_2.md | Doc update |
| Add chapter-must-earn-its-place quality test | specs/ARC_AUTHORING_PLAYBOOK.md | Doc update |

---

## 8. What This Does NOT Change

* Compiler logic (no new enforcement)
* Validator logic (no new prose checks)
* Engine YAML schema
* Arc emotional_curve or resolution_type handling
* Slot resolver band filtering
* Any deprecated validator behavior

Structural purity is maintained.

---

## 9. Migration

No existing arcs or atoms require updates.

New fields are additive and optional at compile time. Coverage flags are advisory (print warnings, not compile failures).

Writers begin using `belief_flip` pattern and `invisible_script` hooks when producing new atoms.

Existing atoms remain valid.

---

## 10. Architectural Guardrail — Narrative Depth Layer Constraints

The additions defined in this spec (`invisible_script`, `belief_flip`, SCENE micro-failure clarification, `milestone_type`, and arc quality test expansion) are:

* Descriptive
* Declarative
* Observational
* Writer-facing
* Coverage-visible

They are **not** compile-time governance rules.

### 10.1 Non-Enforcement Principle

None of the following are permitted:

* Compile failure based on HOOK subtype distribution
* Compile failure based on `milestone_type`
* Arc–atom cross-checking for `milestone_type`
* Story phase validation based on `belief_flip`
* Prose inspection to confirm belief visibility
* Scene abstraction detection logic
* Intensity or rhetorical scoring of `invisible_script` hooks

These additions must remain outside the validator layer.

### 10.2 Structural Purity Rule

The following remain the only structural enforcement layers:

* Arc presence
* Arc alignment (BAND, cost index, reflection sequence)
* Engine resolution compatibility
* Slot completeness
* Token resolution
* K-table minimums
* Duplicate prevention

No new validation categories may be introduced under the Narrative Depth Layer.

### 10.3 Future Evolution Constraint

If a future proposal attempts to:

* Enforce narrative quality via metadata
* Score belief depth
* Require milestone matching
* Introduce cognitive distortion tagging
* Analyze prose for structural compliance

It must be rejected unless the Canonical Spec (PHOENIX_ARC_FIRST_CANONICAL_SPEC) is formally revised.

This layer is additive and advisory only.

### 10.4 Intent

The purpose of this spec is to:

* Increase narrative sharpness
* Improve emotional tension
* Support writer clarity
* Enhance marketing leverage

It is not to:

* Increase system complexity
* Simulate psychological correctness
* Replace arc design judgment
* Create new failure states in the pipeline

Structural determinism remains untouched.

---

*This spec is subordinate to PHOENIX_ARC_FIRST_CANONICAL_SPEC v1.1. If any addition conflicts with that document, the canonical spec wins.*
