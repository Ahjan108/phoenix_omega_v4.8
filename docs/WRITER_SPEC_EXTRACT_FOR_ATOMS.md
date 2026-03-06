# Writer Spec Extract: STORY, Four Rules, TTS, Role Types

**Purpose:** Critical sections from [PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) and related specs so you can tag atoms and avoid TTS/rule violations when the full spec doesn’t load.  
**Full spec:** `specs/PHOENIX_V4_5_WRITER_SPEC.md`

---

## 1. STORY role types (for `role:` on atoms)

STORY atoms can be tagged with **role** for role-aware assembly. The five roles (from PHOENIX_V4_CANONICAL_SPEC / Omega spec) are:

| Role | Purpose | Must Include | Must NOT Include | Word range |
|------|---------|--------------|------------------|------------|
| **recognition** | Incident + validation, no body language | validation phrase, tension signal | body sensation, reassurance, solution | 60–90 |
| **embodiment** | Body sensation only | body lexeme (chest, jaw, hands, stomach, throat) | explanation, solution, cognitive framing | 60–80 |
| **pattern** | Repetition without relief or hope | repetition marker, temporal signal ("again," "every time") | hope, relief, progress, resolution | 60–90 |
| **mechanism_proof** | Explanation without solution | causal explanation of why the loop works | advice, fixing, cure, prescription | 60–120 |
| **agency_glimmer** | Choice without reassurance | choice verb, open ending | reassurance, outcome, triumph, celebration | 60–90 |

**Ordering (within a chapter):** recognition → embodiment → pattern → mechanism_proof → agency_glimmer. Order must not go backward; not all five are required per chapter.

**YAML:** Use `role: recognition | embodiment | pattern | mechanism_proof | agency_glimmer` on STORY atoms when you know the role. Schema (Canonical Spec): STORY “extra fields” include `role`; tag when known so assembly can use it. `emotional_intensity_band` (1–5) is **required** for every STORY atom; `role` is recommended where assembly is role-aware.

---

## 2. §4.3 STORY (from Writer Spec) — show, don’t teach

Named character. Specific moment. Third-person present tense. The story SHOWS the mechanism. No teaching. No labels. No resolution.

**TTS rules for stories:**
- Use dialogue. Robot TTS differentiates character voices tolerably through dialogue.
- One action per sentence.
- Max 15 words per sentence in emotional moments.
- White space for silence beats. TTS cannot pause. Write the pause as a held moment.

**Silence beats:** Write silence as a held moment:
- ✓ "She sat with it. Just sat. Thirty seconds became a minute. The panic did not leave. But something in her stopped fighting it."

**Consequence stories (misfire_tax):** Include action AND reaction. Action without visible reaction = incomplete.
- ✓ "Maya says never mind. The conversation moves on. But it moves on without her."
- ✗ "Maya says never mind. She feels bad." — No visible social reaction.

**Bridge sentences:** If two stories appear in sequence: one-sentence bridge between them. 8–15 words. First-person. "It does not always look like this."

**Emotional intensity band (required for every STORY):** Every STORY atom must have **emotional_intensity_band** set to an integer 1–5. The compiler uses it so books don’t all feel the same: at least 3 distinct bands per book, no more than 3 chapters in a row at the same band.

| Band | Emotional energy |
|------|------------------|
| 1 | mild discomfort |
| 2 | tension |
| 3 | strain |
| 4 | breaking point |
| 5 | crisis / rupture |

**QA Checklist — STORY:**
- [ ] Named character (not "she" / "he" generic)
- [ ] Third-person present tense
- [ ] **emotional_intensity_band (1–5) set and accurate for the moment**
- [ ] ≥ 1 visible consequence (if action present)
- [ ] No emotion labels ("felt anxious," "felt overwhelmed")
- [ ] ≤ 15 words per emotional beat
- [ ] Dialogue used for volatile/cost moments

---

## 3. §6 The Four Story Rules (exact definitions)

### 6.1 Misfire Tax
Alarm or avoidance causes **visible social cost**. Character does something BECAUSE of alarm. Environment responds. Cost must be **visible**. Not internal. Social environment changes.

### 6.2 Silence Beat
Social interaction **pauses**. Pause described in real time. Character experiences it **somatically**. **Ambiguous resolution**. Pause ≥ 2 sentences. Somatic detail.

### 6.3 Never-Know
Story ends with **permanent ambiguity**. Character cannot determine what the interaction meant. No follow-up. No retrospective clarity. No narrator aside revealing truth.

### 6.4 The Interrupt
**One per book.** Character performs avoided action **while alarm still fires**. Messy, imperfect, physically uncomfortable. **Not resolution.** Uses character who appeared earlier. Alarm fires DURING action. Nothing resolved.

---

## 4. §3 TTS Prose Law (Universal)

Applies to every atom type. No exceptions.

- **No rhetorical questions.** Robot makes them sound condescending. Convert every question to a statement. No "?" marks (except in dialogue).
- **No tentative language.** Forbidden: perhaps, you might, it's possible, maybe, could be, might be, you may want to, consider trying, sometimes it helps to, do whatever feels right.
- **Active verbs only.** No: was feeling, was sitting, was thinking, had been. Replace with active constructions.
- **Body anchors required.** Every emotional moment must be grounded in a concrete body state or sensory detail.
- **Sentence length caps:**

| Function | Max words |
|----------|-----------|
| Emotional beats | 15 |
| Teaching sentences | 12 |
| Instructions (EXERCISE) | 10 |
| Integration carry lines | 8 |

These are hard caps. Split longer sentences.

- **Sentence rhythm variance:** Within any 10 consecutive sentences, shortest vs longest must differ by at least 12 words. Every chapter: at least one sentence of 3 words or fewer.
- **Paragraph breaks as breath.** In REFLECTION: paragraph break every 60–80 words.
- **Strategic repetition:** ✓ Structural repetition ("Same room. Same table. Same panic."). ✗ Same phrase four times in three sentences.
- **Sentence fragments:** ✓ Use for impact. Not as default.

---

## 5. §12 TTS Prose Requirements (formal gates)

### 12.1 Sentence length caps by type

| Section type | Max words | Why |
|--------------|-----------|-----|
| Teaching (Doctrine, Key Concepts) | 12 | Mechanism explanation needs compression |
| Sensory Scene (Opening Scene, Grounding) | 10 | One sensory detail per sentence |
| Emotional Moment (Story Injection) | 15 | TTS can't hold tension longer |
| Exercise Instructions | 8 | One step per sentence |
| Integration/Closing | 12 | Carry lines must land cleanly |

**Exception:** Opening hooks may use one 18–20 word sentence IF followed immediately by a 3–5 word sentence for rhythm.

### 12.4 TTS CI gates (T01–T07)

| Gate | Check | Fail condition |
|------|-------|----------------|
| T01 | Sentence length | Teaching/reflection > 12 words. **Hard fail.** |
| T02 | Rhetorical questions | "?" in non-exercise sections. Flag for rewrite. |
| T03 | Tentative language | perhaps, might, maybe, you may want. **Hard fail.** |
| T04 | Passive voice | was feeling, had been, is trying to. Warn if > 3/section. |
| T05 | Abstract without anchor | Abstract noun without body anchor in 2 sentences. Warn. |
| T06 | Exercise chunking | Exercise instructions > 8 words/sentence. **Hard fail.** |
| T07 | Paragraph density | Paragraph > 100 words without break. Warn. |

### Punctuation / TTS

- **No em-dashes in dialogue** (TTS breaks). Use commas or full stops.
- **No heavy punctuation clusters.** Keep sentences TTS-clean.
- Parentheses: avoid in dialogue; sparing elsewhere so the robot doesn’t sound confused.

---

## 6. Atom-level fields (STORY schema)

From Canonical Spec and Writer Spec:

- **Required for every STORY:** `emotional_intensity_band` (1–5). Lint rejects STORY atoms without it.
- **Recommended when assembly is role-aware:** `role` (recognition | embodiment | pattern | mechanism_proof | agency_glimmer).
- **Optional from STORY_TYPES_AND_STRUCTURES:** `story_origin` (true_story | composite), `story_type` (parable | direct_teaching | character_study | atmospheric | recognition_exchange).
- **Tags for Four Story Rules:** e.g. `misfire_tax: true`, `silence_beat: true`, `never_know: true` (and one interrupt per book). Documented in Writer Spec §16.8 and emotional governance.
- **`pivot` field (recommended for formats that use PIVOT slot):** 2–3 sentences that name what this story shows — without teaching it. Written alongside the story body. Assembly reads this field when filling a PIVOT slot that follows this STORY atom. Write in third-person or second-person present. Name the visible dynamic only; no mechanism explanation.

```yaml
# Example STORY atom with pivot field
atom_id: maya_story_001
story_type: character_study
emotional_intensity_band: 3
body: |
  Maya gets the feedback in writing. She reads it three times. She does not reply.
  She closes the laptop and does not open it again until morning.
pivot: |
  She did not go quiet because she agreed. She went quiet because the alarm fired
  and the only move that felt safe was stillness.
misfire_tax: true
never_know: false
```

**When to write a pivot field:** Any story where the mechanism is not immediately obvious — where the reader might see *what happened* but miss *what it means about the pattern*. Character_study and atmospheric types benefit most. Parable types often carry their own meaning implicitly.

---

## 7. New slot types (v2 — Pearl Prime structural upgrade)

These slots are in the pipeline as of 2026-03-06. Writers do not author atoms for TAKEAWAY or THREAD directly — those resolve from the arc. PIVOT content comes from the `pivot` field on STORY atoms. PERMISSION needs authored atoms.

| Slot | How it fills | Writer task |
|------|-------------|-------------|
| **PIVOT** | From `pivot` field on the preceding STORY atom | Write `pivot:` field on every STORY atom (see §6 above) |
| **TAKEAWAY** | From `chapter_thesis[ch]` in the arc YAML | None — arc generates it; see `docs/CHAPTER_THESIS_BANK.md` |
| **THREAD** | From `chapter_thread[ch]` in the arc YAML | None — arc generates it; see `docs/CHAPTER_THESIS_BANK.md` |
| **PERMISSION** | From `chapter_permission[ch]` in the arc YAML | None — arc generates it; see `docs/CHAPTER_THESIS_BANK.md` |

**PIVOT rules (for `pivot` field on STORY atoms):**
- 2–3 sentences maximum
- Names the visible dynamic only — not the mechanism
- Third-person or second-person present tense
- No "this shows us," "notice how," "here we see" — no transition language
- No teaching. PIVOT ends where REFLECTION begins.
- ≤ 12 words per sentence (TTS rule)

Full spec for all four slot types: `specs/PHOENIX_V4_5_WRITER_SPEC.md` §4.3a, §4.7, §4.7a, §4.8.

Use this extract when the full Writer Spec isn’t available. For everything else, use `specs/PHOENIX_V4_5_WRITER_SPEC.md`.
