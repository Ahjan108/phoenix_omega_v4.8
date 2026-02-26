# Teacher Authoring Layer Spec

## Main Teaching Atoms, Story Helpers, Exercise Helpers, Signature Vibe, and LLM Intake Pass

**Status:** Canonical
**Subordinate to:** TEACHER_MODE_V4_CANONICAL_SPEC.md (Arc-First remains sole system architecture)
**Depends on:** TEACHER_MODE_MASTER_SPEC.md, TEACHER_MODE_STRUCTURAL_SPEC.md, TEACHER_MODE_NORMALIZATION_SPEC.md
**Audience:** Senior devs, content leads, LLM pipeline engineers

---

## 0. Problem

Teacher Mode books have governance, validation, and slot-filling infrastructure. What they lack is authoring guidance — the layer that ensures generated content actually sounds like it belongs to a specific teacher and centers that teacher's core ideas.

Current gap-fill produces generic therapeutic content tagged with a teacher_id. It does not know what the teacher's core ideas are, how change works in their framework, what stories about their teaching should sound like, or what exercises drawn from their lineage should feel like.

The result: books that mention the teacher but don't center the teacher. Stories that illustrate generic anxiety recovery instead of this teacher's specific explanation of why anxiety happens and what to do about it. Exercises that could belong to any teacher. No structural guarantee that the teacher's core intellectual contribution is the spine of the book.

This spec defines the authoring layer that fixes this.

---

## 1. Architecture Overview

### 1.1 New Assets Per Teacher

The LLM intake pass produces five doctrine-layer assets per teacher. All are YAML. All live in `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/`. All are generated once at intake, reviewed by a human, then frozen. None are used at runtime for generation — they are consumed by offline tools only (gap-fill, mining, normalization, coverage gate).

```
SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/
  doctrine.yaml                  # existing — glossary, forbidden language, tone
  main_teaching_atoms.yaml       # NEW — core ideas (the stars of the book)
  story_helpers.yaml             # NEW — how to write stories proving the teachings
  exercise_helpers.yaml          # NEW — how to write exercises practicing the teachings
  signature_vibe.yaml            # NEW — felt quality of all content for this teacher
  content_audit.yaml             # NEW — raw material classification and usability map
```

### 1.2 New Tool

```
tools/teacher_mining/intake_normalize.py
```

Single CLI entry point for the LLM intake pass. Reads `teacher_banks/<teacher_id>/raw/`, calls LLM, writes all five new assets plus updates `doctrine.yaml` if it doesn't exist.

### 1.3 Pipeline Position

```
Raw material in teacher_banks/<id>/raw/
        |
        v
intake_normalize.py  (NEW — LLM pass, produces doctrine assets)
        |
        v
Human review of doctrine package
        |
        v
build_kb.py  (existing — indexes raw/ for retrieval)
        |
        v
mine_kb_to_atoms.py  (existing — now uses story/exercise helpers for classification)
        |
        v
gap_fill.py  (existing stub — now uses all authoring layer assets)
        |
        v
normalize_story_atoms.py / normalize_exercise_atoms.py  (existing — now uses vibe profile)
        |
        v
Human approval
        |
        v
Arc-First compile (existing — now with teaching-atom-aware arc planning)
```

### 1.4 Invariant

The authoring layer is offline only. No LLM calls at compile time. No authoring layer assets are read by the slot resolver, book renderer, or any runtime module. They are consumed exclusively by: intake_normalize.py, mine_kb_to_atoms.py, gap_fill.py, normalize_story_atoms.py, normalize_exercise_atoms.py, report_teacher_gaps.py, check_teacher_readiness.py.

---

## 2. Main Teaching Atoms

### 2.1 Definition

A main teaching atom (MTA) is a core idea that defines a teacher's intellectual contribution. It is not a quote, not a story, not a practice. It is the load-bearing concept that books are organized around.

Each teacher has 5-20 MTAs. The number is constrained: too few and books repeat; too many and the concept becomes dilute. The LLM intake pass extracts them; the content lead reviews and caps at 20.

### 2.2 Schema

File: `doctrine/main_teaching_atoms.yaml`

```yaml
schema_version: "1.0"
teacher_id: "master_wu"
extraction_date: "2026-02-26"
reviewed_by: null  # content lead fills after review
review_date: null

main_teaching_atoms:
  - concept_id: "dragon_vein_flow"
    teaching_statement: "The land contains living energy pathways called Dragon Veins; when they flow, people and societies thrive; when blocked, stagnation follows."
    mechanism: "Land energy governs human vitality. Disrupted earth qi produces psychological and social instability. Restoration is precise and technical."
    counter_pattern: "Treating anxiety as purely internal — ignoring the relationship between the person and their physical environment and geography."
    story_seed: "Someone discovers that their chronic stuckness is connected to where they physically are — not just their mindset. They learn to read their environment through the teacher's framework and something shifts."
    exercise_seed: "A land observation or spatial awareness practice — noticing the ground, the orientation of the room, the relationship between body and place."
    band_affinity: [2, 3, 4]
    allowed_topics: [anxiety, self_worth, depression, overwhelm]
    tags: ["geomancy", "land_energy", "flow", "blockage"]
```

### 2.3 Field Definitions

| Field | Type | Required | Description |
|---|---|---|---|
| concept_id | string | yes | System-usable identifier. Snake_case. Unique within teacher. |
| teaching_statement | string | yes | The idea in 1-2 sentences, in the teacher's framing. Not a quote — a distillation. |
| mechanism | string | yes | How this teaching says change works. The causal logic. |
| counter_pattern | string | yes | What this teaching corrects — the wrong belief or approach it replaces. |
| story_seed | string | yes | What a story proving this teaching looks like. The transformation arc in 2-3 sentences. |
| exercise_seed | string | yes | What a practice applying this teaching looks like. The experiential form in 1-2 sentences. |
| band_affinity | list[int] | yes | Which emotional bands (1-5) this teaching naturally serves. |
| allowed_topics | list[string] | yes | Which book topics this teaching applies to. Must be subset of teacher's allowed_topics in registry. |
| tags | list[string] | no | Freeform tags for retrieval and classification. |

### 2.4 Constraints

- Minimum 5 MTAs per teacher. Below this, the teacher lacks enough conceptual range for multi-book production.
- Maximum 20 MTAs per teacher. Above this, concepts are likely overlapping or too granular.
- Every MTA must map to at least one topic in the teacher's `allowed_topics` (from teacher_registry.yaml).
- concept_id must be unique within teacher; globally prefixed by teacher_id when referenced cross-system (e.g., `master_wu.dragon_vein_flow`).

---

## 3. Story Helpers

See spec for full YAML example. Key fields: narrator_position, narrator_voice, transformation_patterns (pattern_id, description, serves_mta, typical_arc), persona_scenarios (persona_id -> list of scenario strings), band_templates (band_1_2, band_3, band_4_5: shape, resolution), forbidden_moves (list of strings).

---

## 4. Exercise Helpers

See spec for full YAML example. Key fields: supported_families (family_id, description, example_prompt, frequency), unsupported_families, adaptation_wrappers (intro_templates, close_templates), safety (max_intensity, notes, forbidden_exercise_types), mta_mapping (concept_id -> list of family_ids).

---

## 5. Signature Vibe

Key fields: voice_instruction (multiline), sentence_constraints (preferred_length_range, max_sentence_length, preferred_paragraph_length, allowed_opening_words, forbidden_sentence_patterns), vocabulary (preferred_words, forbidden_words, tone_words, anti_tone_words), emotional_register (allowed, forbidden).

---

## 6. Content Audit

Key fields: files[] (filename, usability, atom_types, mta_coverage, notes, extraction_warnings), unusable_content[] (description, reason).

---

## 7. LLM Intake Pass

Tool: `tools/teacher_mining/intake_normalize.py`. CLI: `--teacher`, `--raw-dir`, `--out-dir`, `[--model]`, `[--dry-run]`. Behavior: read raw/, load or generate doctrine.yaml, 3-5 LLM calls (Core Concept, Story Helper, Exercise Helper, Signature Vibe, Content Audit), write 5 YAMLs + intake_manifest.json, validation with intake_validation_errors.json on failure.

---

## 8. Downstream Integration

- Arc: optional chapter_mta_assignments (chapter -> primary_mta, intent). Fallback: round-robin MTA by topic.
- report_teacher_gaps.py: new mta_coverage section (per concept_id: required_stories, available_stories, gap_stories, required_exercises, available_exercises, gap_exercises). Atoms tagged with serves_mta (concept_id).
- gap_fill.py: prompts include MTA, story/exercise helpers, signature vibe.
- mine_kb_to_atoms.py: use content_audit (skip low/unusable), tag serves_mta.
- normalize_*.py: use signature_vibe for lint (sentence length, forbidden vocab, adaptation_wrappers).
- check_teacher_readiness.py: --min-mta-story-coverage, --min-mta-exercise-coverage.

---

## 9. Human Review Gate

All assets have reviewed_by: null until content lead sets reviewed_by and review_date. Downstream tools warn and fall back to doctrine-only if reviewed_by is null.

---

## 10. CI / QA Gates

MTA-A: MTA coverage per book (every assigned MTA has ≥1 STORY and ≥1 EXERCISE). MTA-B: no MTA >50% of STORY. MTA-C: every STORY has serves_mta (warning if >20% lack). VIBE-A: forbidden_words in bodies = fail. VIBE-B: >20% sentences over max_sentence_length = warning.

---

## 11. Implementation Plan

Phase 1: Schemas, intake_normalize.py, serves_mta field, report_teacher_gaps MTA section. Phase 2: gap_fill/mine/normalize integration, chapter_mta_assignments. Phase 3: CI gates, check_teacher_readiness MTA mins, intake for all teachers.

---

## 12. File Locations Summary

| Asset | Path |
|---|---|
| Main Teaching Atoms | doctrine/main_teaching_atoms.yaml |
| Story Helpers | doctrine/story_helpers.yaml |
| Exercise Helpers | doctrine/exercise_helpers.yaml |
| Signature Vibe | doctrine/signature_vibe.yaml |
| Content Audit | doctrine/content_audit.yaml |
| Intake Manifest | doctrine/intake_manifest.json |
| Validation Errors | doctrine/intake_validation_errors.json |
| Tool | tools/teacher_mining/intake_normalize.py |

---

## 13. Non-Goals

No runtime LLM. No prose scoring. No Arc-First replacement. No auto-publish. No change to teacher_registry schema. Optional atom field serves_mta only.

---

## 14. References

TEACHER_MODE_V4_CANONICAL_SPEC.md, TEACHER_MODE_MASTER_SPEC.md, TEACHER_MODE_STRUCTURAL_SPEC.md, TEACHER_MODE_NORMALIZATION_SPEC.md, TEACHER_MODE_INVARIANTS.md, TEACHER_INTEGRITY_SPEC.md, TEACHER_PORTFOLIO_PLANNING_SPEC.md, TEACHER_MODE_AUTHORING_PLAYBOOK.md.
