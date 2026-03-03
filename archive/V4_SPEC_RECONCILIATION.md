# Phoenix Omega V4.4 — Spec Reconciliation & Authority

**Hand this to the developer first, before anything else.**

**Version:** 1.0  
**Date:** February 2026  
**Purpose:** Single authority for document precedence, what changed in V4.4, and what remains valid. Resolves conflicts between older specs and the Format Portfolio / 6-type taxonomy.

---

## Section 1 — The Rule

**If any document contradicts a higher-layer document, the higher layer wins. No exceptions.**

When you see conflicting statements about atom taxonomy, chapter structure, format definitions, or slot types, resolve them by layer (Section 2). Lower layers remain valid only where they do not contradict a higher layer.

---

## Section 2 — Document Hierarchy

Four layers. Lower numbers override higher numbers on conflict.

| Layer | Documents | Scope | When they govern |
|-------|-----------|--------|-------------------|
| **0** | **This reconciliation doc** | Precedence rule, hierarchy, migration table, reading order, conflict cheat sheet | Always. Start here. |
| **1** | **Beat Map Spec V2** + **Format Portfolio Spec** | Atom taxonomy (6 section types), chapter structure (beat maps), format definitions (F001–F015, Tier A/B/C), slot remaps, K-tables per format, release waves | **CANONICAL** for: atom types, slot semantics, format list, beat map library, micro vs full atoms. |
| **2** | **Complete Spec** + **Systems Doc** | Plan compiler, duplication simulation, governance, approval workflows, catalog planning, CI gates, pipeline, directory layout | **VALID** for infrastructure. **SUPERSEDED** for: atom categories, chapter_arc, format definitions. Use Layer 2 for how to build and run the system; use Layer 1 for what an atom is and how chapters are structured. |
| **3** | **Source material** | Canonical books, master scripts in `content/`, V3 section maps, existing atom pools | Content to **mine** and validate against. Not specs to build against. |

**Layer 1 document locations (canonical):**

- **Format Portfolio Spec:** `PHOENIX_V4_FORMAT_PORTFOLIO_SPEC.docx` (or exported equivalent). Contains 15 formats, 6 section types, Tier A/B/C, beat map assignments, slot remaps (3-type → 6-type), K-table expansion, CI gate additions, brand × section type mapping, release waves.
- **Beat Map Spec V2:** If published as a separate document, it must align with Format Portfolio §1–4 (three-tier architecture, full vs micro beat maps, fixed sequences). Until then, beat map definitions are **inside** the Format Portfolio Spec.

**Layer 2 document locations:**

- **Complete Spec:** `PHOENIX_OMEGA_V4_COMPLETE_SPEC (1).md`
- **Systems Doc:** `SYSTEMS_DOCUMENTATION (3).md`

---

## Section 3 — What Changed (Old → V4.4)

Ten-row mapping. For each row, the **V4.4 replacement** is governed by **Layer 1** (Format Portfolio Spec / Beat Map Spec V2).

| # | Old concept (Layer 2 or earlier) | V4.4 replacement | Governing V4.4 doc |
|---|----------------------------------|------------------|---------------------|
| 1 | **3 atom categories** (story, exercise, scene) | **6 section types** (HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION) | Format Portfolio §1, §2.2–2.3 |
| 2 | **One fixed 10-slot chapter_arc** (slot_01_entry … slot_10_transition) | **12 full beat maps + 8 micro beat maps + fixed sequences** per format; plan compiler selects per chapter | Format Portfolio §1, §2.1 |
| 3 | **scene / closing** | **INTEGRATION** (closing synthesis; author voice, not sensory scene) | Format Portfolio §2.2 |
| 4 | **story / mechanism_proof** (teaching prose) | **REFLECTION** (mechanism_explanation, reframe, pattern_naming, core_thesis) | Format Portfolio §2.2 |
| 5 | **story / recognition** or archetype intro (author-voice opening) | **HOOK** (author-voice chapter opening) | Format Portfolio §2.2 |
| 6 | **5 format policy names** (standard_book, short_form, deep_dive, etc.) | **15 formats** F001–F015 in **3 tiers** (A: full beat maps, B: micro beat maps, C: fixed sequences) | Format Portfolio §2.1, §3, §4 |
| 7 | **Single K-table** (e.g. standard_book) | **K-table per format**; K-tables cover full and micro atom pools; format_id in structural fingerprint | Format Portfolio §5, §10 |
| 8 | **atom_category: story \| exercise \| scene** | **atom_category** = one of 6 types; **atom_size**: full \| micro; micro variants (e.g. MICRO_HOOK, MICRO_REFLECTION) | Format Portfolio §1, §3.1, §7 (this doc) |
| 9 | **One duplication threshold** | **Format-specific duplication thresholds**; cross-format sharing rules (word count ranges, namespace) | Format Portfolio §6, §10 |
| 10 | **One voice profile** | **Brand × section type mapping** (HOOK/REFLECTION/INTEGRATION voice per brand); brand affinity governs author-voice atoms | Format Portfolio §8 |

---

## Section 4 — What's Still Valid (Unchanged)

These systems from the old specs remain in force. Use **Layer 2** (Complete Spec, Systems Doc) for their details.

| # | System | Where defined (Layer 2) |
|---|--------|-------------------------|
| 1 | **Plan compiler pipeline** (inputs, capability check, achievable chapter count, plan output) | Systems Doc §19.4, §20; Complete Spec §compile_format_plan |
| 2 | **Duplication simulation** (variant threshold, no reuse within book, structural fingerprint) | Systems Doc §19.3, §20; Format Portfolio §6 extends with format_id in fingerprint |
| 3 | **Governance layers** (candidate vs approved, human approval, CI enforcement) | Systems Doc §14, §23; Complete Spec coverage/approval |
| 4 | **Approval workflows** (approve_cli, status: confirmed \| provisional, V4_STRICT) | Systems Doc; Complete Spec §10, §11 |
| 5 | **Catalog planning** (domain → series → angle, teacher, persona, topic) | Systems Doc; plan compiler inputs |
| 6 | **Cultural overlays** (persona, topic, location variables) | Systems Doc; persona_topic_variables, overlays |
| 7 | **Brand registry** (24 brands; Format Portfolio §8 adds brand × section type mapping on top) | Systems Doc; Format Portfolio §8 |
| 8 | **Story atom schema** (ids, persona, topic, teacher, body, word_count, approval, provenance) — **extended** by V4.4 fields in Section 7 below, not replaced | Systems Doc §8, §9, §10; Complete Spec §5, §14 |
| 9 | **Build manifests** (artifacts, CI gates, coverage reports) | Systems Doc; Complete Spec |
| 10 | **QA campaigns** (golden Phoenix, semantic uniqueness, cadence, doctrine compliance) | Systems Doc §12, §23; Complete Spec |
| 11 | **Forbidden resolution lexemes / open ending / no medical advice** (applies to all atom types) | Systems Doc §10; unchanged in V4.4 |

---

## Section 5 — Developer Reading Order

| Step | Document / action | Time |
|------|-------------------|------|
| 1 | **This reconciliation doc** (Sections 1–7) | ~5 min |
| 2 | **Beat Map Spec** (or Format Portfolio §1–4: three-tier architecture, full/micro/fixed beat maps, slot types per tier) | ~30 min |
| 3 | **Format Portfolio Spec** (full read: 15 formats, 6-type remaps, K-tables, release waves, CI gates, brand mapping) | ~30 min |
| 4 | **Complete Spec** — infrastructure only: plan compiler usage, coverage checker, directory layout, approval, story_atoms paths. **Skip** sections that define atom categories or single chapter_arc as canonical. | ~45 min |
| 5 | **Systems Doc** — orchestration only: pipelines, governance, validation stack, catalog. **Skip** sections that define atom taxonomy or format list as only standard_book/short_form/deep_dive. | ~30 min |

Total: ~2.5 hours to be spec-aligned.

---

## Section 6 — Conflict Resolution Cheat Sheet

When you see **X** in an old spec, treat it as **Y** (and use the cited doc/section).

| If you see X (old) | Replace with Y (V4.4) | Document + section |
|--------------------|----------------------|---------------------|
| `atom_category: story \| exercise \| scene` | `atom_category`: one of `hook`, `scene`, `story`, `reflection`, `exercise`, `integration`; plus `atom_size: full \| micro` where applicable | Format Portfolio §1, §3.1; this doc §7 |
| Single `chapter_arc` with 10 fixed slots (slot_01_entry … slot_10_transition) | Beat map selection per chapter (12 full / 8 micro / fixed per format); slot semantics come from the beat map, not one global arc | Format Portfolio §1, §2.1 |
| `scene_type: closing` | Type is **INTEGRATION**; closing synthesis, not sensory scene | Format Portfolio §2.2 |
| `story` slot labeled mechanism explanation or “why it works” | **REFLECTION** (subtype: mechanism_explanation) | Format Portfolio §2.2 |
| `story` slot for chapter opening / “recognizing state” / archetype intro (author voice) | **HOOK** | Format Portfolio §2.2 |
| Only formats: standard_book, short_form, deep_dive, guided_session, micro_collection | 15 formats F001–F015; Tier A (full), Tier B (micro), Tier C (fixed) — see Format Portfolio §2.1, §3, §4 | Format Portfolio §2.1, §4 |
| One K-table for standard_book | K-table per format; micro and full pools; `format_id` in fingerprint | Format Portfolio §5, §6, §10 |
| Story roles only: recognition, embodiment, pattern, mechanism_proof, agency_glimmer | **STORY** atoms keep 5 roles for character-driven vignettes; **REFLECTION** and **HOOK** are separate types (author voice). Roles still apply to STORY only. | Format Portfolio §2.2 |
| No atom_size or micro variants | `atom_size: full \| micro`; MICRO_HOOK, MICRO_SCENE, MICRO_STORY, MICRO_REFLECTION, MICRO_INTEGRATION with word count ranges per Format Portfolio §3.1 | Format Portfolio §3.1; this doc §7 |
| Single duplication threshold | Format-specific thresholds; cross-format sharing rules (word count, namespace) | Format Portfolio §6, §10 |

---

## Section 7 — The Atom (V4.4 Schema)

Complete atom schema for V4.4. All atoms share the universal fields; type-specific fields apply as indicated. **Layer 1** (Format Portfolio) governs the allowed values.

### Universal fields (all atoms)

```yaml
atom_id: "<type_prefix>_<persona_topic_slug>_<seq>"
atom_category: hook | scene | story | reflection | exercise | integration
atom_size: full | micro
version: 1
deprecated: false
persona: <persona_id>
topic: <topic_id>
teacher_id: "<teacher_id>"
body: |
  <prose or guided instruction>
word_count: <integer>
approval:
  status: approved | provisional
  approved_by: <human>
  approved_at: <UTC ISO 8601>
  promotion_reason: manual | auto_confident
provenance:
  source_seed: "<id>"
  teacher_doctrine: "<id>"
  mined_at: <UTC ISO 8601>
```

### Type-specific fields

**HOOK**

- `hook_type` or variant family (F1–F5 per Format Portfolio; e.g. provocative, invitation, pattern_naming).
- **Full:** 150–350 words. **Micro:** 40–100 words.
- Author-voice chapter opening; no character story.

**SCENE**

- `scene_type: entry | transition | closing` (sensory/context only; “closing” as final scene of a sequence is still scene_type; if it’s synthesis/author wrap-up → INTEGRATION).
- **Full:** 150–300 words. **Micro:** 40–80 words.

**STORY** (character-driven vignette)

- `role: recognition | embodiment | pattern | mechanism_proof | agency_glimmer`
- `arc_type`, `stake_domain` (per existing story atom registry).
- **Full:** 60–150 words per role. **Micro:** 30–80 words.
- STORY is only for character-driven beats; teaching prose → REFLECTION.

**REFLECTION**

- `reflection_type: mechanism_explanation | reframe | pattern_naming | core_thesis`
- **Full:** 200–500 words. **Micro:** 60–150 words.
- Author-voice teaching; no character.

**EXERCISE**

- `exercise_type`: breathwork | somatic | integration | stillness | movement (per registry).
- `exercise_tier`: 1 | 2 | 3 (e.g. awareness / regulation or release / integration) for placement.
- `cadence_role`: grounding | activation | release | integration (unchanged from Layer 2).
- **Full:** 100–300 words. **Micro:** 60–120 words; optional `micro_body` when full atom is used in Tier B.

**INTEGRATION**

- Closing synthesis; author voice; no resolution promise.
- **Full:** 100–200 words. **Micro:** 30–60 words.

### Variants (F1–F5)

HOOK and other author-voice types may use **variant families** F1–F5 for selection/affinity (see Format Portfolio). Include in atom metadata when defined:

```yaml
variant_family: F1  # optional; per format/brand affinity
```

### Word count and lint

- **Full** vs **micro** word ranges per Format Portfolio §3.1 and per type above.
- All atoms: open ending, no resolution lexemes, no medical advice (unchanged from Layer 2).
- **atom_size** must pass format-specific lint: Tier A → full only; Tier B/C → micro where required.

### Governing document

- **Format Portfolio Spec** (§1 Three-Tier Architecture, §2.2–2.3 Slot Remaps, §3.1 Micro Atom Variants, §5 K-Table, §7 CI / schema implications).

---

## Summary

| Question | Answer |
|----------|--------|
| What is canonical for atom types and chapter structure? | Layer 1: Beat Map Spec V2 + Format Portfolio Spec (6 section types, beat maps, 15 formats). |
| What is still valid for implementation? | Layer 2: Plan compiler, governance, approval, catalog, pipelines, directory layout — except where they assume 3 categories or one 10-slot arc. |
| What if Complete Spec or Systems Doc disagrees with Format Portfolio? | Format Portfolio wins. |
| Where do I get the full atom schema? | This doc §7 (V4.4); Format Portfolio for K-tables, CI gates, and format-specific rules. |

**Runtime assembles. Humans govern. The system never degrades.**
