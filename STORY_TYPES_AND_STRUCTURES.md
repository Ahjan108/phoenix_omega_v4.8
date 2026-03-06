# Story Types and Structures

**Path:** docs/STORY_TYPES_AND_STRUCTURES.md  
**Status:** Canonical (content authority for story type definitions, structures, and origin rules)  
**Audience:** Writers, content leads, atom authors, gap-fill reviewers  
**Subordinate to:** [PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) (§4.3 STORY, §6 Four Story Rules) and [PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md).  
**Related:** [HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md](./HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md), [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md), [TEACHER_MODE_AUTHORING_PLAYBOOK.md](../specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md)

---

## 0. Why this doc exists

Two source documents — `story_types.rtf` and `story_structures.rtf` — were referenced as authoritative but were never committed to the repo. This document replaces them as the single canonical source for:

- What story types exist and when to use each
- What structure each type follows (minimal template per type)
- The origin rule: true story vs composite, and what each permits
- The principle-teacher rule (e.g. Ma'at, cosmic teachers): no human appearance, ever
- How these apply to both Teacher Mode and regular (non-teacher) STORY atoms

Writers producing STORY atoms should read this doc alongside the Writer Spec and the Story Atom Upgrade Rubric. It does not replace those docs; it extends them with structure and type clarity.

---

## 1. Story origin: true vs composite (Rule #1)

This is the most important rule in this document. Get it wrong and the book breaks trust.

### 1.1 Definitions

**True story** — A real incident: one person, one event, documented or directly recalled. The author was present, or it comes from a real client/student interaction that can be honestly framed as such.

**Composite story** — Synthesized from doctrine, combined experiences, or "someone like X." It is not a single real event. It is built from pattern, not memory.

### 1.2 The rule

> **If a story is composite, the teacher never appears in the story.**

In a composite, the teacher cannot walk into a scene and speak, because the scene did not happen. The author frames it as: "I shared this teaching with Jack, and when he…" — and then only Jack's story follows. Jack is the story. The teacher is not in the room.

In a true story, the teacher may appear in scene only if they actually were there.

### 1.3 Author framing for composites

Use one of these frames (adapt as needed):

- "I was working with someone — I'll call her Maya — who…"
- "I shared this teaching with a client, and what she said back stopped me."
- "Someone I worked with for three years described it like this…"
- "A physician I know — not a patient, a colleague — told me once that…"

The frame tells the reader: this is real pattern, not a single event. It is honest. It is not weaker than a true story — it is a different kind of truth.

### 1.4 Schema

Add to STORY atom metadata:

```yaml
story_origin: true_story | composite
```

- **Required** for all Teacher Mode STORY atoms.
- **Optional but recommended** for regular STORY atoms.
- Default assumption when absent: treat as composite (conservative).

### 1.5 Composite constraint on story types

When `story_origin: composite`, the allowed story types are:

`parable` | `direct_teaching` | `character_study` | `atmospheric`

**Not allowed:** `recognition_exchange` — because that type requires the teacher to be physically present in a scene, which composite origin does not permit.

---

## 2. Principle teachers: the Ma'at rule

Some teachers in the system are not human teachers in the conventional sense — they represent cosmic principles, archetypes, or lineage wisdom (e.g. Ma'at as divine principle, not as a person who sat across from the author and spoke).

### 2.1 The rule

> **Principle teachers never appear in stories as characters. They may only appear as wisdom voice, ceremonial address, or as the subject of a parable.**

"Ma'at appeared in my office and said…" is not a valid construction. Ever.

Principle teachers operate through the world, through pattern, through the reader's experience — not through direct speech in a scene.

### 2.2 Registry flag

In `config/teachers/teacher_registry.yaml`, principle teachers carry:

```yaml
teacher_as_principle: true
```

When this flag is set:
- All stories for that teacher are treated as composite-style regardless of `story_origin`.
- Allowed story types: `parable`, `atmospheric`, `direct_teaching` (wisdom voice only).
- `character_study` is allowed only if the teacher is referenced as background context, not as a character.
- `recognition_exchange` is never allowed.

### 2.3 Voice for principle teachers

The author may invoke the teacher's principles as:

- A parable drawn from the teacher's tradition ("In the Egyptian conception of Ma'at…")
- A ceremonial or second-person address ("What this principle asks of you is…")
- A wisdom-voice framing ("The teaching here is not about…")

Never as scene, never as dialogue, never as character.

---

## 3. Story types: definitions and when to use

Five types. Four are standard across Teacher Mode and regular books. One (`recognition_exchange`) is restricted to true stories and should be used sparingly.

---

### Type 1 — Parable

**What it is:** A metaphor, historical tale, or teaching story with no modern named character. Often begins "In the tradition of…" or "There is a story about…" or names a historical/mythological figure. The lesson is implied, not stated.

**Teacher appears?** No — or only as narrator/voice, never as a character in scene.

**When to use:**
- When the teaching is ancient or lineage-based and benefits from that framing
- When a modern character would feel contrived
- When you want maximum distance between the reader and the "this is about you" pressure
- Band 1–3 (recognition, early escalation); also works for integration

**Does not work when:**
- The reader needs to see themselves directly (use character_study or atmospheric instead)
- The teaching is very contemporary or somatic (parable can feel abstract)

**Structure template:**

```
1. Setup — time, place, or "In the tradition of…" (1–2 sentences; no modern character)
2. Event or metaphor — the thing that happens or the image that holds the teaching
3. Implied lesson — either stated briefly at the end, or left for the reader
   (Do not explain the parable. Trust the image.)
```

**Example shape:**
> In the Zen tradition, there is a story of a student who spent three years asking his teacher the same question. Each time, the teacher poured tea until it overflowed. The student finally stopped asking. The cup, the teacher said nothing, was already full.

---

### Type 2 — Direct Teaching

**What it is:** First- or second-person; the author or teacher speaking directly to the reader. Short, pointed, mechanism-focused. This is not a story about someone else — it is a direct transmission.

**Teacher appears?** As voice, not as a character in scene. The author is the voice; they may invoke the teacher's framework, but the teacher does not walk into the room.

**When to use:**
- When the mechanism needs to be stated plainly before the reader can use it
- When a story would be slower than the insight deserves
- Band 2–4; also works as a short beat inside longer atoms
- When the persona is high-cognitive (executives, clinicians) and wants directness

**Does not work when:**
- The reader needs to feel recognized first (use character_study or atmospheric before this)
- The teaching is subtle and indirect delivery would be more powerful

**Structure template:**

```
1. "You" or "we" or "I" — establish the perspective directly
2. Name the mechanism — what is actually happening (not what the reader thinks is happening)
3. One concrete move — what to do, or what to notice; specific, not inspirational
   (No third-person story. No other character. Just the reader and the idea.)
```

**Example shape:**
> When you reach for your phone at 11pm, you are not looking for information. You are managing a nervous system that does not yet trust rest. The phone is not the problem. The distrust of stillness is. You can put the phone down. What you cannot do — yet — is sit with what the phone is covering.

---

### Type 3 — Character Study

**What it is:** A named character; a specific situation and inner life; no neat resolution. The story ends in ambiguity, cost, or open question — not in fix. The character is recognizable to the persona. Junko and Miki-style: no rescue, no tidy arc.

**Teacher appears?** No — or only as a distant catalyst, never as sage or fixer. The character's insight (if any) comes from their own reckoning, not from a teacher walking in with the answer.

**When to use:**
- When you want the reader to recognize themselves without being told "this is you"
- Band 3–4 (escalation, cost-adjacent); also Band 5 cost chapter if the cost is visceral enough
- When the teaching is about what it costs to keep the pattern going
- When `belief_flip` pattern is in use (see PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md §3)

**Does not work when:**
- The reader needs a direct instruction (use direct_teaching)
- The book is in early Band 1–2 and the reader has not yet been oriented to the pattern

**Structure template:**

```
1. Named character + specific moment (not "a woman" — give her a name; not "one day" — give it a time)
2. Inner life or cost — what this is costing them, or what they are holding
3. No resolution — end in ambiguity, open question, or the moment just before the thing they cannot yet do
   (Do not fix it. Do not explain what they should have done. Leave the door open.)
```

**Composite framing when needed:**
> "I was working with a woman I'll call Naomi. She was a senior editor at a publisher. The day she called me was a Tuesday, which she mentioned three times, as if the day of the week explained something."

**Example shape (Junko-style):**
> Yumi had been running the department for eight months when her manager asked if she wanted to lead the restructuring. She said yes before she finished hearing the question. That night she sat in her car outside the subway entrance for forty minutes. She wasn't crying. She wasn't thinking. She was just sitting there, engine off, watching people walk past, none of them looking up.

---

### Type 4 — Atmospheric

**What it is:** A brief, precise moment — place, body sensation, shift in quality of attention. Minimal plot. No dialogue. Almost no character. The moment itself is the story.

**Teacher appears?** No.

**When to use:**
- When a full story would overexplain what a single image can hold
- Band 1–2 (recognition, early orientation) and Band 4–5 (cost, stillness)
- When the reader needs to be placed somewhere before they can hear the teaching
- As an opener or closer within a longer atom, or as a standalone SCENE-adjacent beat

**Does not work when:**
- The reader needs a character to identify with
- The teaching requires narrative arc or cost to land

**Structure template:**

```
1. Sensory anchor — place or body (one specific detail; not "a quiet room" — where exactly, what texture)
2. Held moment — what is happening in the stillness or in the movement; no dialogue
3. Shift in quality — something changes: attention sharpens, the body registers something, the quality of the room changes
   (No explanation. No lesson stated. The moment is the lesson.)
```

**Example shape (Miki-style):**
> The rain had been falling for an hour before she noticed it. She was at the kitchen table, both hands around a cup that had gone cold. Outside, the neighbor's dog was sitting under the eaves, not moving, just watching the water fall. She stayed there longer than she planned. Nothing was solved. The cup stayed cold. She stayed anyway.

---

### Type 5 — Recognition Exchange

**What it is:** Teacher and character in the same scene; a brief exchange (2–4 lines of dialogue or interaction); a pivot line that reframes something. The classic "teacher in the doorway" form.

**Teacher appears?** Yes — but only in true stories, and only when the teacher actually was there.

**Restrictions:**
- `story_origin: true_story` required. Composite origin is not allowed for this type.
- Principle teachers (`teacher_as_principle: true`) may never use this type.
- Cap per book: no more than 1–2 recognition_exchange atoms per compiled book. Use sparingly; overuse collapses into formula.

**When to use:**
- When a real exchange actually happened and the teacher's presence is part of what made it land
- Band 3–4; occasionally Band 2 if the exchange is gentle rather than confrontational
- When the pivot line is genuinely the teacher's and genuinely memorable

**Does not work when:**
- The story is composite (do not use)
- The "exchange" is reconstructed or probable rather than actual
- The book already has one recognition_exchange and this would be the second (consider a different type)

**Structure template:**

```
1. Character in a specific moment — where they are, what they are doing or avoiding
2. Teacher enters or is already present — no build-up; just present
3. Exchange — 2–4 lines maximum; no speeches; the teacher says less than you think they should
4. Pivot — one line that reframes; the character (or reader) sits with it; no explanation follows
```

**Example shape:**
> She had been sitting outside the interview room for twenty minutes when Rinpoche walked past. He stopped. "You look like you are preparing for a battle," he said. She said she was nervous. He looked at her for a moment. "Yes," he said, and walked on.

---

## 4. Story type and origin: quick reference

| Type | Origin allowed | Teacher in scene? | Resolution? | Best bands |
|------|---------------|-------------------|-------------|------------|
| `parable` | true_story, composite | No (or narrator voice only) | Implied, not stated | 1–3, integration |
| `direct_teaching` | true_story, composite | As voice only | Yes — direct move | 2–4 |
| `character_study` | true_story, composite | No (or distant catalyst) | No — open ending | 3–5 |
| `atmospheric` | true_story, composite | No | No — shift only | 1–2, 4–5 |
| `recognition_exchange` | **true_story only** | Yes | Pivot, not fix | 3–4 |

---

## 5. What makes a story work: the five-element check

Use this alongside the full [HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md](./HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md).

Every STORY atom — regardless of type — should contain at least three of these five. If fewer than three are present, rewrite before the atom enters the pool.

1. **Specificity trigger** — A place, a physical action, a sensory cue, or a real sentence someone said. Not "she felt overwhelmed." The car outside the hospital. The cup gone cold.

2. **Cost moment** — What did it cost? Sleep, identity, a relationship, self-respect. Without cost, there is no tension and no reason to keep reading.

3. **Internal conflict** — Two forces in the same person: "I should…" and "but I can't…" or "but I won't…". Without conflict, the story is flat.

4. **Insight pivot** — A moment where the frame shifts. Not "she realized she needed rest." Instead: "If I collapse, no one benefits." The pivot is felt, not concluded.

5. **Residual echo** — After reading, something lingers. Would someone underline a line? If not, the story has not earned its place.

**Pass / fail rule:** Missing 2 or more of the five → rewrite before scaling.

---

## 6. Story types and the `belief_flip` pattern

The `belief_flip` pattern (see [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md §3](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md)) applies most naturally to Band 3–4 STORY atoms and works well inside **character_study** and **direct_teaching** types:

- **Character study + belief_flip:** The character's wrong-but-common belief is shown failing in the specific moment (the cost). No tidy reframe — leave it open or land it ambiguously.
- **Direct teaching + belief_flip:** Name the belief directly to the reader, show it failing in a recognizable moment, offer the counter-intuitive reframe. More explicit than character study; use when the persona is ready for directness.

Do not use belief_flip in Band 1–2 (too early) or in Band 5 cost chapter (too confrontational for reframe at that point).

---

## 7. Story type schema additions

### 7.1 Teacher Mode STORY atoms

Add to atom metadata YAML:

```yaml
story_origin: true_story | composite   # required for teacher-mode STORY
story_type: parable | direct_teaching | character_study | atmospheric | recognition_exchange
```

Rules enforced at authoring/approval (not compile-time):
- If `story_origin: composite` → `story_type` must not be `recognition_exchange`
- If teacher has `teacher_as_principle: true` → `story_type` must be `parable`, `atmospheric`, or `direct_teaching`

### 7.2 Regular (non-teacher) STORY atoms

`story_type` is optional for regular STORY atoms. Add where schema/format supports it. Coverage reporting can flag story_type distribution when present; no hard enforcement.

Minimum variety target (advisory, not compile failure): at least 2–3 distinct story_type values per book.

---

## 8. Reshaping existing mined stories (Ahjan and similar)

When mined atoms are raw KB extracts with no narrative shape:

1. **Set origin first.** Is this a single documented incident? → `true_story`. Built from doctrine or combined experiences? → `composite`.
2. **Choose a story type** based on the content and origin:
   - Doctrine / lineage language → `parable` (wrap in "In the tradition…" or metaphor frame)
   - Direct mechanism → `direct_teaching` (first/second person; no character)
   - Named character scenario → `character_study` (give them a name; specific moment; no resolution)
   - Single image or sensation → `atmospheric` (place + body + shift; no dialogue)
   - Composite → never `recognition_exchange`
3. **Rewrite to structure.** Use the template for the chosen type (§3 above). Preserve the teacher's conceptual depth and lineage language. Do not flatten into generic self-help.
4. **Approve via standard flow.** Human approval required; no auto-publish.

Reference: `SOURCE_OF_TRUTH/teacher_banks/ahjan/doctrine/story_helpers.yaml` (transformation_patterns, band_templates) for Ahjan-specific patterns.

---

## 9. Variety and distribution

Across a compiled book, story variety matters for engagement. A book with eight character_study atoms in a row is monotonous regardless of quality.

**Target distribution (advisory):**

| Type | Suggested per 8-chapter book |
|------|------------------------------|
| `parable` | 1–2 |
| `direct_teaching` | 1–2 |
| `character_study` | 2–3 |
| `atmospheric` | 1–2 |
| `recognition_exchange` | 0–1 (true_story only; use sparingly) |

Coverage reporting (`scripts/coverage_report.py`) should flag story_type distribution when `story_type` metadata is present. A warning (not a compile failure) if fewer than 2 distinct types appear across a book's STORY atoms.

---

## 10. What this doc does NOT cover

- Atom band targets or emotional curve governance → [PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md)
- STORY role taxonomy (recognition, embodiment, pattern, mechanism_proof, agency_glimmer) → Writer Spec §4.3
- Teacher Mode gap-fill and approval process → [TEACHER_MODE_AUTHORING_PLAYBOOK.md](../specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md)
- Doctrine constraints per teacher → teacher doctrine YAML per teacher bank
- `structure_family` (NARRATIVE, CASE_STUDY, PARABLE, DIALOGUE) assigned by hash for entropy → unchanged; `story_type` is the content-facing lever; both can coexist

---

## 11. Files to update after adopting this doc

| Action | File |
|--------|------|
| Add `story_origin` and `story_type` to teacher STORY atom schema | Atom schema |
| Document composite rule and principle-teacher rule | `specs/TEACHER_MODE_NORMALIZATION_SPEC.md` |
| Add composite rule and story-type guidance | `specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md` §9 and new §10 |
| Add `teacher_as_principle: true` for Ma'at and similar | `config/teachers/teacher_registry.yaml` per teacher |
| Add story_type distribution to coverage report | `scripts/coverage_report.py` |
| Add link under content/writer section | `docs/DOCS_INDEX.md` |
| Reshape Ahjan mined atoms to type + origin | `SOURCE_OF_TRUTH/teacher_banks/ahjan/candidate_atoms/` → approve via existing flow |
