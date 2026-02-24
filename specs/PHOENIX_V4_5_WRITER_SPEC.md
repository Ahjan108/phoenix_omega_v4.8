# PHOENIX V4.5 — COMPLETE WRITER SPECIFICATION (TTS-LOCKED)

**Single source of truth for writers.** Voice · Prose · Six Atom Types · TTS Rules · Phase 3 · Tests · Governance

SpiritualTech Systems — February 2026 — Version 2.0

---

## Contents

1. [The Production Reality](#1-the-production-reality)
2. [Voice](#2-voice)
3. [TTS Prose Law (Universal)](#3-tts-prose-law-universal)
4. [The Six Atom Types](#4-the-six-atom-types)
5. [Emotional Temperature](#5-emotional-temperature)
6. [The Four Story Rules](#6-the-four-story-rules)
7. [Reflections: Teaching for Robot Ears](#7-reflections-teaching-for-robot-ears)
8. [Integrations: Landing the Chapter](#8-integrations-landing-the-chapter)
9. [Pacing Profiles](#9-pacing-profiles)
10. [Phase 3 Requirements (Your Responsibility)](#10-phase-3-requirements-your-responsibility)
11. [What We Never Do](#11-what-we-never-do)
12. [TTS Prose Requirements (Formal Gates)](#12-tts-prose-requirements-formal-gates)
13. [Catalog QA & Drift Control](#13-catalog-qa--drift-control)
14. [Emotional Force Thresholds](#14-emotional-force-thresholds)
15. [Spiritual Authenticity Gates](#15-spiritual-authenticity-gates)
16. [Emotional QA & Drift Governance (CI-Enforced)](#16-emotional-qa--drift-governance-ci-enforced)
17. [Personas](#17-personas)
18. [Location Overlays](#18-location-overlays)
19. [The Tests](#19-the-tests)
20. [Config, Registry & Atom Layout (Reference)](#20-config-registry--atom-layout-reference)
21. [Appendix A: Shame Engine (Writer Onboarding)](#21-appendix-a-shame-engine-writer-onboarding)
22. [Example Chapter Shapes](#22-example-chapter-shapes)
23. [Identity & Audiobook Governance Layer](#23-identity--audiobook-governance-layer)
24. [Author Positioning Compliance](#24-author-positioning-compliance)
25. [Appendix B: Compression Atoms (slot_08_compression)](#25-appendix-b-compression-atoms-slot_08_compression)
26. [Appendix C: T01 Rewrite Patterns](#26-appendix-c-t01-rewrite-patterns)

---

# 1. The Production Reality

Your prose will be read by a robot. Google Play auto-narration. Zero vocal performance control. No warmth. No emphasis. No dramatic pauses. A flat synthetic voice reading your text exactly as written.

**This means:** 100% of the emotional weight comes from how you write. Sentence structure creates pacing. Paragraph breaks create breath. Word choice creates feeling. The robot contributes nothing. The text must do everything.

Every rule in this document exists because of this reality. Write for a flat robot voice reading at 150 words per minute to a person who is on a train, in bed, or walking to class. They hear each sentence once. The robot will not help you. **The text itself must breathe.**

---

# 2. Voice

**Who speaks:** The author. Not a guru. Not a therapist. Not a friend. An author whose authority comes from precision, not credentials.

**Person and tense:**

| Type | Person / Tense | Example |
|------|----------------|---------|
| HOOK | First-person author or second-person direct | "The question hangs in the air. Your throat tightens." |
| SCENE | Second-person present always | "You are on the N-Judah." |
| STORY | Third-person present | "Maya hears her name." Never past. Never first-person. |
| REFLECTION | First-person author to second-person listener | "Your nervous system does not distinguish threats." |
| EXERCISE | Second-person imperative | "Place your hand on your chest. Feel it rise." |
| INTEGRATION | First-person author. Quiet. Concrete. | "Still here. Feet on floor." |

**What the voice is NOT:**

- ✗ Inspirational. No "you can do this." No affirmations.
- ✗ Clinical. No DSM language.
- ✗ Guru. No "let me share my wisdom."
- ✗ Peer. No "we all feel this way."
- ✗ Tentative. No "perhaps" or "you might" or "it's possible." Direct statements only.

**Never use "we."** The author observes, names, and respects. "We" implies shared experience the author cannot guarantee.

---

# 3. TTS Prose Law (Universal)

These rules apply to every atom type. No exceptions.

### No rhetorical questions

Robot voice makes them sound condescending or preachy. Every question must be converted to a statement.

- ✗ "Why do we freeze?" — Sounds preachy in TTS.
- ✓ "You freeze because the alarm fires." — Direct statement. Lands in any voice.

**Stated-question strategy:** State what the listener is wondering, then answer. No "?" marks.

### No tentative language

Forbidden: perhaps, you might, it's possible, maybe, could be, might be, you may want to, consider trying, sometimes it helps to, do whatever feels right.

### Active verbs only

- ✗ "She was feeling overwhelmed by the situation." — Passive. Dead in TTS.
- ✓ "The situation crushed her. She could not breathe." — Active. Concrete.

Scan for: was feeling, was sitting, was thinking, were looking, had been. Replace with active constructions.

### Body anchors required

Every emotional moment must be grounded in a concrete body state or sensory detail. Abstract emotional states without physical anchors vanish in TTS.

### Sentence length caps

| Function | Max words |
|----------|-----------|
| Emotional beats | 15 |
| Teaching sentences | 12 |
| Instructions (EXERCISE) | 10 |
| Integration carry lines | 8 |

These are hard caps. If your teaching sentence hits 18 words, split it.

### Sentence rhythm variance

Within any 10 consecutive sentences, the range between shortest and longest must be at least 12 words. Every chapter: at least one sentence of 3 words or fewer.

### Paragraph breaks as breath

Your only pacing tool. In REFLECTION: paragraph break every 60–80 words. In STORY: tight paragraphs for tension, spacious for processing.

### Strategic repetition

✓ Structural repetition creates resonance: "Same room. Same table. Same panic."
✗ Stuck phrase: "Your nervous system" four times in three sentences.

### Sentence fragments

✓ "Not okay. Not even close. But still breathing." — Use fragments for impact. Not as default.

---

# 4. The Six Atom Types

## 4.1 HOOK (grab)

The first thing the listener hears. Job: make the listener think "this is about me" as fast as the format allows.

**TTS structure for short-format hooks:**
- Sentence 1: Pure concrete image. Max 12 words. No context.
- Sentence 2: Body state or immediate action. Max 10 words.
- Sentence 3 (optional): Single-clause recognition.

**Example:**

- ✗ "You know that feeling when you are in a meeting and someone asks you a question, and suddenly your mind goes blank..." — 42 words. One sentence. Dead in TTS.
- ✓ "The question hangs in the air. Your throat tightens. Every face turned toward you, waiting." — Three sentences. Concrete. Present tense.

**QA Checklist — HOOK:**

- [ ] ≤ 3 sentences (short-format)
- [ ] No "?" marks
- [ ] First line ≤ 12 words
- [ ] Body anchor included
- [ ] Survives monotone reading

---

## 4.2 SCENE (ground)

Sensory immersion. Second-person, present tense, always. One sensory detail per sentence. Max 10 words per sensory beat.

- ✗ "Sarah sat in the conference room feeling increasingly uncomfortable..." — Abstract. Vague.
- ✓ "Sarah's palms sweat against the table. Her breath shallow. The presenter's voice fading to background noise." — Body states. Concrete.

**Never:** "She could feel..." **Always:** "Her hands shook."

**SCENE illustrates; it does not teach.** A SCENE shows lived experience. It does not explain the pattern, name the mechanism, or deliver insight. If a SCENE explains something, it is doing REFLECTION's job. Teaching is the book's job; SCENE grounds the listener in a moment.

**No variables except location overlays.** Aside from the allowed location tokens (§18 — e.g. `{transit_line}`, `{street_name}`), no placeholders or templating in SCENE body. Scene text is authored whole. End with action or sensory moment, not with insight or realization ("That's when I realized...").

No two SCENE atoms in the same book can open with the same syntactic pattern. Vary: body state, sensory detail, environment, ambient sound.

**QA Checklist — SCENE:**

- [ ] 2–5 location tokens (where applicable)
- [ ] One sensory detail per sentence
- [ ] No internal emotional labeling ("felt," "felt like")
- [ ] Max 10 words per sensory beat
- [ ] Second-person present tense only
- [ ] Illustrates only; no teaching or explanation
- [ ] No variables/placeholders except §18 location tokens
- [ ] Ends with action or sensory moment, not insight

---

## 4.3 STORY (show)

Named character. Specific moment. Third-person present tense. The story SHOWS the mechanism. No teaching. No labels. No resolution.

**TTS rules for stories:**
- Use dialogue. Robot TTS differentiates character voices tolerably through dialogue.
- One action per sentence.
- Max 15 words per sentence in emotional moments.
- White space for silence beats. TTS cannot pause. Write the pause as a held moment.

**Silence beats:** Write silence as a held moment:
✓ "She sat with it. Just sat. Thirty seconds became a minute. The panic did not leave. But something in her stopped fighting it."

**Consequence stories (misfire_tax):** Include action AND reaction. Action without visible reaction = incomplete.

✓ "Maya says never mind. The conversation moves on. But it moves on without her."
✗ "Maya says never mind. She feels bad." — No visible social reaction.

**Bridge sentences:** If two stories appear in sequence: one-sentence bridge between them. 8–15 words. First-person. "It does not always look like this."

**Emotional intensity band (required for every STORY):** Every STORY atom must have **emotional_intensity_band** set to an integer 1–5. This is metadata you (or the mining pipeline) assign; lint rejects STORY atoms without it. The compiler uses it so books don’t all feel the same: at least 3 distinct bands per book, and no more than 3 chapters in a row at the same band. Choose the band that matches the emotional energy of the moment:

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

## 4.4 REFLECTION (teach)

Mechanism explanation. This is where most TTS audiobooks die. Your ceiling is lower. Your chunks are smaller. Your statements are sharper.

**TTS reflection ceilings:**

| Tier | Max words | Post-impact |
|------|-----------|-------------|
| S | 220 | 180 |
| A | 200 | 160 |
| B | 180 | 140 |
| C | 120 | — |
| D | 80 | — |

*Post-impact* = reflection follows a story with misfire_tax, silence_beat, or never_know. That story was intense. Name the mechanism. Connect it. Get out.

**Statement-based teaching only.** No rhetorical questions. Convert every question to a statement.

**Chunk every 60–80 words.** Paragraph break. Then next burst. Max 12 words per teaching sentence. Max 2 mechanism terms per reflection. One metaphor image per reflection. Max two sentences to establish it.

**The reflective beat:** Every reflection needs 1 sentence, max 25 words, in the first third, that directs the listener to their own experience. Second-person. Invites noticing a specific sensation or memory.

**Dual-voice pattern (required):** REFLECTION can combine first-person authority with second-person reflective direction in the same block.

Example (first-person authority + second-person reflective beat):

`Your system learned speed as safety. I have seen this pattern repeatedly in high-pressure performers. Notice what happens in your chest when you delay one response by ten seconds.`

**QA Checklist — REFLECTION:**

- [ ] ≤ Tier ceiling (words)
- [ ] ≤ 2 mechanism terms
- [ ] ≤ 12 words per teaching sentence
- [ ] 1 reflective beat present (directs to listener experience)
- [ ] Post-impact rule: if after intense story, use post-impact ceiling
- [ ] Chunk every 60–80 words with paragraph break

---

## 4.5 EXERCISE (guide)

Imperatives only. One instruction per sentence. No options. No "you might." Body-based.

- ✗ "You might want to try noticing your breath, and if it feels comfortable, perhaps place one hand on your chest..."
- ✓ "Place your hand on your chest. Feel it rise and fall. Breathe in for four counts. Out for six. Stay with the rhythm."

Timed instructions: explicit. "Count to four." Not "for about four seconds." Max 10 words per instruction sentence.

**QA Checklist — EXERCISE:**

- [ ] Imperatives only
- [ ] ≤ 10 words per sentence
- [ ] No options ("you might," "if comfortable")
- [ ] Explicit count if timed ("Count to four," not "about four seconds")
- [ ] One step per sentence
- [ ] Body-based (concrete sensation)

**Where EXERCISE content comes from:** (1) **Canonical:** `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` (block file). (2) **Teacher Mode:** `teacher_banks/<teacher_id>/approved_atoms/EXERCISE/*.yaml`. (3) **Backstop:** When canonical is missing or empty, assembly fills EXERCISE slots from the **practice library** (`SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl`) — 9×34 library_34 types (sensory_grounding, meditations, affirmations, etc.) plus optional ab_tady_37. Selection is deterministic (config: `config/practice/selection_rules.yaml`). Schema and pipeline: [PRACTICE_ITEM_SCHEMA.md](./PRACTICE_ITEM_SCHEMA.md); teacher fallback (wrapper): [../docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md](../docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md).

**Book-size full exercise quotas (writer-facing):**

| Book size | Full EXERCISE chapters max | Typical full-book expectation |
|-----------|----------------------------|-------------------------------|
| short (1–6 chapters) | 1 | 0–1 full, rest none/micro |
| medium (7–10 chapters) | 3 | 1–3 full, rest none/micro |
| long (11+ chapters) | 5 | 2–5 full, rest none/micro |

Planner/CI enforce these caps. Write micro variants so chapters can carry practice intent without forcing a full workbook cadence.

---

## 4.6 INTEGRATION (land)

Not a summary. A landing. Concrete body state. The listener's feet touch ground. They carry one thing into silence.

**Word count by weight:** light 150–200, standard 120–160, heavy 80–130, interrupt_landing 80–120.

**Every integration needs:** one reframe, one mode, one carry line (final sentence, max 8 words).

No "you're okay" or "you've got this" or "you're safe." Use concrete body states instead.

- ✓ "Feet on floor. Breath steady. Still here."
- ✗ "You're going to be okay. You've got this. Trust the process."

**QA Checklist — INTEGRATION:**

- [ ] 1 reframe (new information)
- [ ] 1 carry line ≤ 8 words
- [ ] No reassurance phrases
- [ ] Concrete body state
- [ ] Not a summary — a landing

---

# 5. Emotional Temperature

Every chapter is assigned a temperature: **cool**, **warm**, **hot**, or **land**.

| Temperature | Distance | Example |
|-------------|----------|---------|
| **Cool** | At the lectern. Reflective, mechanism. | "Here is what is happening when the alarm fires. Your amygdala has identified the social situation as a potential threat." |
| **Warm** | Across the table. Mild emotional tension. | "Think about what that costs. Not the dramatic cost. The quiet one." |
| **Hot** | Leaning forward. Visible consequence, volatile moment. | "You stop raising your hand. Then you stop going to the table at lunch. Then the invitations slow. Then one day you are sitting in your room and the quiet is not peace. It is the sound of a world that got smaller." |
| **Land** | Grounded embodied containment. Final chapters. | "Feet on floor. Breath steady. Still here." |

Every atom in a chapter matches the chapter's temperature.

**Per-format curves:** Each format has a defined sequence (e.g. cool → warm → hot → land). Your brief specifies the curve. See `simulation/config/emotional_temperature_curves.yaml` for format-specific sequences and requirements (volatility spikes, rupture, action-despite-pattern, landing).

**Volatility quotas by tier (what you must include):**

| Tier | Volatility scenes | Visible consequence | Action-despite-pattern | Silence beats |
|------|-------------------|---------------------|------------------------|---------------|
| S | ≥ 3 | ≥ 1 | ≥ 1 | ≥ 2 |
| A | ≥ 2 | ≥ 1 | ≥ 1 | ≥ 1 |
| B | ≥ 1 | — | ≥ 1 | — |
| C | — | — | optional | — |
| D | — | — | — | — |
| E | — | — | — | — |

*Ref:* `simulation/config/validation_matrix.yaml` (volatility quotas).

---

# 6. The Four Story Rules

## 6.1 Misfire Tax

Alarm or avoidance causes visible social cost. Character does something BECAUSE of alarm. Environment responds. Cost must be visible. Not internal. Social environment changes.

## 6.2 Silence Beat

Social interaction pauses. Pause described in real time. Character experiences it somatically. Ambiguous resolution. Pause ≥ 2 sentences. Somatic detail.

## 6.3 Never-Know

Story ends with permanent ambiguity. Character cannot determine what interaction meant. No follow-up. No retrospective clarity. No narrator aside revealing truth.

## 6.4 The Interrupt

One per book. Character performs avoided action while alarm still fires. Messy, imperfect, physically uncomfortable. Not resolution. Uses character who appeared earlier. Alarm fires DURING action. Nothing resolved.

---

# 7. Reflections: Teaching for Robot Ears

**The post-impact rule:** If the story before your reflection carried misfire_tax, silence_beat, or never_know: the story was intense. Your reflection is SHORTER. Name the mechanism. Connect it. Get out.

**Maximum 2 mechanism terms.** If you name amygdala, cortisol, and prefrontal cortex in one reflection, you are lecturing. Pick two.

**Never start two reflections the same way.** Vary: social observation, listener's experience, character continuation, mechanism naming.

---

# 8. Integrations: Landing the Chapter

**The five modes:** STILL-HERE, COST-VISIBLE, BODY-LANDED, QUESTION-OPEN, SOMEONE-ELSE.

**The five reframe types:** OTHER-PERSON, COST-UNCOUNTED, BODY-FACT, QUESTION-REFRAME, TIME-SHIFT.

**The carry line:** Final sentence, max 8 words. The line the listener remembers. Stone in still water.

- ✓ "Still here." "One corner at a time." "Nobody talks about it."
- ✗ "And so the alarm continues but you are learning to live alongside it." — Not a carry line. A paragraph ending.

**Interrupt landing:** After interrupt story: 120 words max. No mechanism language. No summary. One reframe. Carry line max 8 words. Quietest thing in the book.

**Stack momentum (book-ending only):** Final integration: adjacent opening. 1–3 sentences, max 40 words. Names connected mechanism book did not explore.

**Forward Momentum Trigger (FMT) — full books only:** Every full book (standard_book and longer; short/micro with narrative arc) must end with one of: *unresolved adjacent mechanism*, *identity tension*, *social cliff edge*, or *curiosity hook*. The FMT is the last beat before silence — the line the listener carries, and the hook the next book can pick up. Must not promise resolution. See [V4_6_BINGE_OPTIMIZATION_LAYER.md](./V4_6_BINGE_OPTIMIZATION_LAYER.md).

---

# 9. Pacing Profiles

| Profile | Character | Best for |
|---------|-----------|----------|
| VELOCITY | Fast, cognitive, tight. Avg 10–14 words. | Loops, rumination, overthinking |
| IMMERSION | Slow, sensory, heavy. Avg 14–20 words. | Dissociation, numbness, fog |
| SPIKE | Calm interrupted by bursts. Variable chapter length. | Social anxiety, phone anxiety |
| DESCENT | Progressively deepening. Sentence length increases. | Shame, grief, identity |

Your brief tells you the profile. Write to it.

---

# 10. Phase 3 Requirements (Your Responsibility)

The system scans assembled chapters. If your atoms do not contain specific word classes, the chapter fails validation.

**Hot chapters need escalation:**
- ≥ 3 escalation verbs: snap, slam, cry, send, delete, confront, hit, leave, lock, shout, freeze, shake, walk out, throw, break, scream
- ≥ 2 sensory stress words: jaw, breath, throat, chest, heat, silence, stare, shaking, sweat, pulse, stomach, hands
- ≥ 1 reaction marker: paused, looked, didn't reply, walked away, door, seen, turned, left, stopped, froze, went quiet, said nothing, stared

**All chapters: cognitive/body balance.** Ratio of cognitive to body words. Above 5 → fail. Above 3 → warn. Ground teaching in the body.

**Action requires reaction.** If a chapter contains action verbs (send, say, leave, confront, post), it must contain ≥ 1 reaction marker.

**Reassurance phrases to vary.** No phrase may appear in more than 40% of books: "You are not broken," "Still here," "You are enough," "You've got this," "Trust the process," "You're safe." Vary. Write specific carry lines.

**STORY atoms: emotional_intensity_band required.** Every STORY atom must include `emotional_intensity_band` (1–5). The compiler enforces emotional curve diversity: at least 3 distinct bands per book, no more than 3 consecutive chapters with the same dominant band. If you omit the band, the atom fails lint and cannot be approved. See §4.3 for the band scale.

---

# 11. What We Never Do

Absolute prohibitions. If any appear, the atom is rejected.

| Prohibition | Rule |
|-------------|------|
| RESOLVE | No character overcomes fear. No pattern breaks. No "it gets better." Coexistence, not recovery. |
| DIAGNOSE | No DSM language. No "social anxiety disorder." Describe mechanisms, not labels. |
| PRESCRIBE | No "talk to a therapist." No "consider medication." Exercises offered, not prescribed. |
| INSPIRE | No "you are stronger than you think." No "every storm passes." Precision, not encouragement. |
| FAKE EMPATHY | No "I know how hard this is." Credibility from precision, not performed solidarity. |
| BREAK FOURTH WALL | No "in this chapter we will explore." The listener is inside the experience. |
| LABEL EMOTIONS | No "Maya felt anxious." Show body. Show behavior. Let listener name it. |
| ASK QUESTIONS | No "?" marks outside of dialogue. Statement-based system. |
| HEDGE | No "perhaps" / "you might" / "maybe" / "it's possible." Direct statements only. |
| PASSIVE VOICE | No "was feeling" / "was thinking" / "had been." Active verbs. |

---

# 12. TTS Prose Requirements (Formal Gates)

Formal sentence caps by section type. CI gates T01–T07.

## 12.1 Sentence Length Caps by Type

| Section Type | Max Words | Why |
|--------------|-----------|-----|
| Teaching (Doctrine, Key Concepts) | 12 | Mechanism explanation needs compression |
| Sensory Scene (Opening Scene, Grounding) | 10 | One sensory detail per sentence |
| Emotional Moment (Story Injection) | 15 | TTS can't hold tension longer |
| Exercise Instructions | 8 | One step per sentence |
| Integration/Closing | 12 | Carry lines must land cleanly |

**Exception:** Opening hooks may use one 18–20 word sentence IF followed immediately by 3–5 word sentence for rhythm.

## 12.2 Reflection Ceiling by Tier

| Chapter Type | Max Words | Chunk Size |
|--------------|-----------|------------|
| HARDSHIP (intense) | 180 | 60–80 word bursts with breaks |
| HELP (teaching) | 220 | 80–100 word bursts |
| HEALING (practice) | 200 | 70–90 word bursts |
| HOPE (integration) | 140 | 50–70 word bursts |

**Rule:** After any high-emotion story injection, cut the following reflection by 20%. The story did the work.

## 12.2b TTS reflection ceilings (by format tier)

For TTS-optimized builds, use lower reflection ceilings so teaching does not become long monotone blocks. Break teaching into smaller chunks; more white space, more story, less exposition.

| Format tier | Max reflection words | Post-impact max |
|-------------|----------------------|-----------------|
| Tier S (Deep) | 220 | 180 |
| Tier A (Extended) | 200 | 160 |
| Tier B (Standard/Short) | 180 | 140 |
| Tier C (Micro) | 120 | — |
| Tier D (Capsules) | 80 | — |
| Tier E (Resets) | No reflections | — |

Source: PHOENIX_V4_5_TTS_PROSE_GUIDE (extracted). The §12.2 table (HARDSHIP/HELP/HEALING/HOPE) remains for legacy tier mapping where used.

## 12.3 Dialogue in Stories

Dialogue differentiates well in TTS. Use it strategically. The shift to quoted speech changes TTS cadence enough to hold attention.

## 12.4 TTS CI Gates (T01–T07)

| Gate | Check | Fail Condition |
|------|-------|----------------|
| T01 | Sentence length | Teaching/reflection > 12 words. Hard fail. |
| T02 | Rhetorical questions | "?" in non-exercise sections. Flag for rewrite. |
| T03 | Tentative language | perhaps, might, maybe, you may want. Hard fail. |
| T04 | Passive voice | was feeling, had been, is trying to. Warn if > 3/section. |
| T05 | Abstract without anchor | Abstract noun without body anchor in 2 sentences. Warn. |
| T06 | Exercise chunking | Exercise instructions > 8 words/sentence. Hard fail. |
| T07 | Paragraph density | Paragraph > 100 words without break. Warn. |

See [Appendix C](#26-appendix-c-t01-rewrite-patterns) for compliant rewrite examples for T01.

---

# 13. Catalog QA & Drift Control

At scale (100 teachers × 12 books = 1,200 books), without drift control: teachers converge on same metaphors, closing lines repeat, hooks feel samey. This section prevents that.

## 13.1 Metaphor Registry (Teacher Ownership)

Each teacher owns 3–5 metaphor image terms. No two teachers may share terms.

```yaml
metaphor_registry:
  teacher_001:
    owned_terms: [lotus, unfold, bloom, light body, golden thread]
    forbidden_terms: [all terms owned by other teachers]
```

**Gate D01 (Metaphor Collision):** Teacher uses another teacher's owned term → hard fail.
**Gate D02 (Metaphor Consistency):** Teacher uses owned terms in ≥ 6 of 12 chapters. Warn if absent.
**Gate D03 (Metaphor Overuse):** Single term > 20 times across 12 chapters → flag.

## 13.2 Reassurance Phrase Cap

No phrase may appear in > 40% of books. Monitored: "You are held," "You are not broken," "Your body knows," "Trust the process," "You are enough," "You are exactly where you need to be."

**Gate D04:** Phrase in > 40% of catalog → hard fail.
**Gate D05:** Teacher A's signature phrase in Teacher B's book → flag (contamination).

## 13.3 Hook Diversity

No two books may open with the same structural pattern. Scan first 2 sentences for structure, length, opening word.

**Gate D06:** Hook fingerprint similarity > 70% across catalog → hard fail.
**Gate D07:** Teacher's 12 books all use same Opening Scene variant → flag. Require rotation.

## 13.4 Carry Line Uniqueness

Final sentence of Chapter 12 = carry line. No two books may share the same carry line.

**Gate D08:** Exact duplicate → hard fail.
**Gate D09:** ≥ 50% 6-gram overlap → flag for review.

## 13.5 Emotional Waveform Entropy

Each book has an intensity curve across 12 chapters. Curves should vary at catalog scale.

**Gate D10:** No two books share exact same intensity sequence → flag.
**Gate D11:** Intensity variance < 1.5 (too flat) → warn.

---

# 14. Emotional Force Thresholds

Structural validation ensures correct build. Emotional force validation ensures the book moves the listener.

## 14.1 Chapter Temperature Classification

| Phase | Temperature | Intensity | Requirements |
|-------|-------------|-----------|--------------|
| HARDSHIP | Hot | 4–5 | Grounding verbs, body states, visible consequence |
| HELP | Warm | 2–3 | Teaching clarity, mechanism naming |
| HEALING | Warm-Hot | 3–4 | Emergence verbs, sensory present, no resolution |
| HOPE | Cool | 1–2 | Integration, quiet, synthesis |

## 14.2 HARDSHIP Chapter Requirements (Hot)

**Grounding verbs (≥ 2):** collapse, shatter, fragment, dissolve, abandon, crumble, unravel, break, fall, lose.

**Body state words (≥ 2):** tight, numb, hollow, frozen, raw, clenched, heavy, empty, small, trapped.

**Visible consequence required.** HARDSHIP chapters cannot end with "and everything was okay." Something must change, break, or stop.

**Gate E01:** Grounding verbs < 2 → hard fail.
**Gate E02:** Body state words < 2 → warn.
**Gate E03:** Ending feels resolved → flag for rewrite.

## 14.3 HEALING Chapter Requirements (Warm-Hot)

**Emergence verbs (≥ 2):** soften, open, return, notice, allow, settle, land, release, breathe, feel.

**Sensory present words (≥ 3):** breath, skin, ground, warmth, weight, texture, contact, sound, pulse, surface.

**No resolution allowed.** HEALING chapters cannot end with transformation complete.

**Gate E04:** Emergence verbs < 2 → warn.
**Gate E05:** Sensory words < 3 → hard fail.
**Gate E06:** Chapter ending implies cure → flag.

## 14.4 Cognitive/Body Ratio

**Formula:** cognitive_count / body_count

- > 5 → hard fail
- > 3 → warn
- < 2 → ideal

## 14.5 Action → Reaction Pairing

If story contains action verbs, it must contain reaction markers. Action without visible reaction feels incomplete.

**Gate E08:** Action present, no reaction → hard fail.

---

# 15. Spiritual Authenticity Gates

Protection against spiritual clichés, abstract drift, and voice contamination.

## 15.1 Cliché Density Threshold

No chapter may contain > 2 monitored cliché phrases.

**Monitored:** "Everything happens for a reason," "Trust the universe," "Divine timing," "Holding space," "Sacred container," "Come into alignment," "Do the work," "Sit with" (overused), "Embodiment" (> 3x/chapter), "Nervous system" (> 4x/chapter without fresh context).

**Gate S01:** > 2 phrases per chapter → hard fail.
**Gate S02:** Phrase in > 30% of catalog → warn.

**Exception:** Cliché allowed if immediately followed by grounding/specificity, or if doctrine-locked for that teacher.

**Scope policy (legacy migration):** S01/S02 are enforced as hard gates for new submissions and modified atoms. Legacy canonical atoms are migrated under a separate cleanup campaign; they are not auto-rejected retroactively unless explicitly reapproved in the current intake batch.

## 15.2 Abstract Noun Ceiling

Max 8 abstract nouns per 200 words. Monitored: consciousness, awareness, presence, energy, frequency, vibration, alignment, wholeness, integration, embodiment, authenticity.

**Gate S03:** > 8 per 200 words → warn. > 12 → hard fail.

## 15.3 Teacher Voice Bleed Detection

If Teacher A's signature phrase appears in Teacher B's book → contamination.

**Gate S04:** Signature phrase from another teacher → hard fail.

## 15.4 Specificity Requirement

Every teacher must demonstrate specific knowledge. Generic ("The body holds wisdom") fails. Specific ("The psoas muscle holds the memory of running. When you freeze, it contracts...") passes.

**Gate S05:** Human review. Generic/vague teaching without grounding → flag.

---

# 16. Emotional QA & Drift Governance (CI-Enforced)

Sections 1–15 define how content is written. Section 16 defines how content is validated at production scale. All rules are CI-enforced. No soft overrides in production mode.

**Machine-readable rules:** See `phoenix_v4/qa/emotional_governance_rules.yaml`

## 16.1 Chapter-Level Emotional Force

- ≥ 1 chapter flagged HIGH temperature
- That chapter: escalation_verbs ≥ 3, sensory_words ≥ 2, reaction_markers ≥ 1
- If any threshold fails → HARD FAIL

## 16.2 Cognitive/Body Ratio (Explicit)

```
cognitive_count / body_count > 5 → FAIL
cognitive_count / body_count > 3 → WARN
```

## 16.3 Action → Reaction

If ≥ 2 action verbs in chapter → ≥ 1 reaction marker required. Missing → FAIL.

## 16.4 TTS Rhythm Governance

- ≥ 30% sentences ≤ 10 words; ≥ 20% at 11–15; ≤ 20% > 18 words
- > 30% exceed 18 words → FAIL
- Question marks per chapter: ≤ 2. ≥ 3 → FAIL

## 16.5 Drift Detection (Book-Level)

- **Emotional flattening:** 3 consecutive chapters, same temperature, 0 escalation verbs, 0 visible consequences → FAIL
- **Reassurance cap:** Phrase in > 40% chapters → WARN. > 60% → FAIL
- **Carry line collision:** Exact duplicate → FAIL. ≥ 80% similarity → WARN
- **Metaphor family saturation:** No family > 40% in rolling 10-book window → FAIL

## 16.6 Catalog-Level

- Structural similarity > 20% → FAIL
- Story-body overlap > 15% → FAIL
- Waveform entropy: ≥ 3 distinct intensity curves in 10-book window. Else → FAIL
- Reflection density: No more than 2 consecutive books same tier. Else → FAIL

## 16.7 Failure Protocol

| Level | Action |
|-------|--------|
| Atom | Quarantine |
| Chapter | Block assembly |
| Book | Block export |
| Catalog | Freeze release batch |

---

## CI Governance Summary Table

| Layer | Rule | Threshold | Fail Condition |
|-------|------|-----------|----------------|
| Chapter | Escalation verbs | ≥ 3 (high temp) | < 3 |
| Chapter | Sensory words | ≥ 2 (high temp) | < 2 |
| Chapter | Reaction markers | ≥ 1 (if ≥ 2 actions) | Missing |
| Chapter | Cognitive/Body | > 5 | Fail |
| TTS | Long sentences | > 30% > 18 words | Fail |
| TTS | Questions | > 2 per chapter | Fail |
| Book | Emotional flattening | 3 same-temp run | Fail |
| Book | Reassurance phrase | > 60% chapters | Fail |
| Book | Metaphor family | > 40% stack | Fail |
| Catalog | Structural overlap | > 20% | Fail |
| Catalog | Waveform entropy | < 3 distinct curves | Fail |

## 16.8 Emotional impact patterns (misfire tax, silence beat, never-know, integration modes)

These patterns are required so books have emotional voltage and visible consequence; they are enforceable via atom tags and minimum counts. Full definitions and examples: `talp/analyze_intake/extracted_docx/EMOTIONAL_IMPACT_SPEC.md`.

**Misfire tax:** At least one STORY atom (standard_book: ≥2; micro_book: ≥1) where the alarm or avoidance causes a visible social cost. Tag: `misfire_tax: true`. QA: Something different afterward that would not have been different if the alarm had not fired.

**Silence beat:** At least one moment (standard_book: ≥2; micro_book: ≥1) where a social pause is described in real time, the character experiences it somatically, resolution is ambiguous. Tag: `silence_beat: true`.

**Never-know:** At least one STORY atom (standard_book: ≥2; micro_book: ≥1) that ends with the character (and listener) unable to determine what the social moment meant. No resolution. Tag: `never_know: true`.

**Integration modes:** Five modes — STILL-HERE, COST-VISIBLE, BODY-LANDED, QUESTION-OPEN, SOMEONE-ELSE. Standard_book: use ≥3 modes; micro_book: ≥2. No two consecutive chapters same mode. STILL-HERE only once per book (final chapter). Tag: `integration_mode: still_here | cost_visible | body_landed | question_open | someone_else`.

**Flinch audit:** Human reader reads full book at 150 WPM and marks involuntary body responses. Standard_book: ≥5 flinch points; micro_book: ≥2. Not automatable; required before approval.

Machine-enforceable minima (tags and counts) are in `phoenix_v4/qa/emotional_governance_rules.yaml` where implemented.

---

# 17. Personas

- **Gen Alpha (10–15):** School, social media, identity. Hallways, cafeterias, group chats. Language: contemporary, not slang-heavy.
- **Healthcare RN (25–45):** Hospital, shift work, compassion fatigue. Break rooms, nurses' stations, parking garages at 3AM.
- **Gen Z Professional (22–30):** Workplace, career anxiety. Open offices, Slack, Zoom, all-hands.

Persona boundaries are hard. If writing Gen Alpha and "quarterly" appears → auto-rejected.

---

# 18. Location Overlays

SCENE atoms contain tokens in curly braces: `{transit_line}`, `{street_name}`, `{weather_detail}`. System fills with locale-specific details.

- ✓ "You are on the {transit_line} and the windows are fogged and {weather_detail} is pressing against the glass."
- ✗ "You are in {city_name}, on the {transit_line}, near {landmark_name}." — Three in a row. Reads like a form.

Min 2 tokens per SCENE. Max 5. Scatter through prose.

---

# 19. The Tests

**The Monotone Test:** Read your atom aloud in a flat, expressionless voice. No emphasis. No pauses except at paragraph breaks. Does every sentence land? Does the prose create rhythm through LENGTH variation? At the end, do you feel something in your body? Can you identify the ONE thing this atom does? If heard in isolation, does it make sense?

**The Question Scan:** Search for "?" outside dialogue. If found → convert to statement. Zero tolerance.

**The Tentative Scan:** Search for perhaps, you might, maybe, it's possible, could be, consider trying. If found → rewrite.

**The Body Count:** Highlight every emotional moment. Is there a concrete body anchor? If not, add one.

**The Sentence Length Audit:** Emotional max 15. Teaching max 12. Instructions max 10. Carry lines max 8.

**The Flinch Audit:** Human reads full book in monotone. Marks every involuntary body response. Minimum: 5 per standard book. 2 per micro. 1 per capsule.

**The Prediction Test (integrations):** Read chapter without integration. Predict what it says. If you were right, it is a summary. Rewrite until it surprises.

**The Stone Test (carry lines):** Read the final sentence. Does it land like a stone in still water? Could another sentence follow? If yes, it is not final enough.

---

# 20. Config, Registry & Atom Layout (Reference)

Where topic gates, vocabulary, section packs, and canonical atoms live. Your brief is constrained by these; delivery may target staging or the canonical layout.

**Topic gates & vocabulary (repo root):**

- **config/topic_engine_bindings.yaml** — Which engines and roles are allowed per topic. Unified 12 (per [unified_personas.md](../unified_personas.md) Part 2): overthinking, burnout, boundaries, self_worth, social_anxiety, financial_anxiety, imposter_syndrome, sleep_anxiety, depression, grief, compassion_fatigue, somatic_healing; legacy keys (anxiety, courage, financial_stress) may also exist. Your topic determines which engines you can use; do not write for forbidden engines. **Engine onboarding guides do not override config/topic_engine_bindings.yaml.** Writers may only write engines permitted by the topic binding for that topic.
- **config/topic_skins.yaml** — Prohibited terms (global and per-topic), role suffixes (≤30 words), and topic overrides. Vocabulary steering is enforced from this file. No prohibited terms; use topic-appropriate language.

**Section packs:**

- **registry/** — Section variant packs (e.g. **registry/registry_grief.yaml** for grief). The pipeline uses these for section selection. If you are writing section variants for a pack, they are registered here.

**Canonical story atoms:**

- **atoms/\<persona\>/\<topic\>/\<engine\>/CANONICAL.txt** — Canonical story atoms live under this path by persona, topic, and engine. Used for assembly and coverage. You may deliver new atoms to **get_these/** for ingestion; they are then moved into **atoms/** (see **get_these/README.md** and Canonical Spec Part 5).

**Practice library (EXERCISE backstop):**

- **SOURCE_OF_TRUTH/practice_library/** — inbox/ (raw `*_library_34.json`, optional ab_tady_37), tmp/ (raw JSONL), store/practice_items.jsonl (validated). **config/practice/selection_rules.yaml**, **config/practice/validation.yaml**. Scripts: **scripts/practice/ingest_practice_libraries.py**, **normalize_practice_items.py**, **validate_practice_store.py**, **extract_libraries_from_rtf.py** (specs/34_exercises.rtf → inbox). When EXERCISE canonical is missing, assembly fills from store; prose resolved by Stage 6 from store for atom_ids like lib34_*, ab37_*. Schema: [PRACTICE_ITEM_SCHEMA.md](./PRACTICE_ITEM_SCHEMA.md). Teacher fallback: [../docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md](../docs/PRACTICE_LIBRARY_TEACHER_FALLBACK.md). Safety lint: phoenix_v4/qa/practice_safety_lint.py.

*Ref:* [PHOENIX_V4_CANONICAL_SPEC.md](./PHOENIX_V4_CANONICAL_SPEC.md) Part 5; REPO_FILES.md; get_these/README.md.

---

# 21. Appendix A: Shame Engine (Writer Onboarding)

Use this as the **template for engine-specific onboarding** (anxiety, grief, comparison, overwhelm, watcher, spiral, false_alarm). Full one-page onboarding: `talp/analyze_intake/WRITER_ONBOARDING_SHAME_ENGINE.md`.

**Shame in one line:** Exposure + contraction. Someone saw something; the self feels smaller, wrong, wanting to disappear. Not fear, not thoughts, not loss — **exposure.**

**Pattern:** (1) Moment of being seen (real or perceived). (2) Internal collapse ("something is wrong with *me*"). (3) Urge to hide, shrink, disappear.

**Required:** Specific exposure moment; witness (real or implied); body signals from shame lexicon (face heat, chest drop, shoulders curling — NOT racing heart/sweating palms, that's FALSE_ALARM). **Role constraints:** Recognition (no exit, still shrinking); Mechanism Proof (collapse is reliable); Turning Point (crack not cure); Embodiment (protective action only, no triumph). **Language bans:** embarrassed, humiliated, ashamed, self-esteem, owned it, no one noticed. **One-line test:** If the character could feel this alone in an empty room, it's not shame.

**Template for other engines:** Core definition; pattern (3 steps); triggers (rotate); body signals (engine-specific); role constraints; turning point mechanisms; embodiment actions; engine differential (vs. spiral, watcher, overwhelm, comparison, grief); language bans; failure modes; self-check; one-line test. Write once per engine; reuse structure across personas/topics.

---

# 22. Example Chapter Shapes

**Standard / long-form (relationship_anxiety, Gen Z, LA):** Chapter shape: STORY → REFLECTION → EXERCISE (placeholder) → INTEGRATION. Use tagging (e.g. `[Tagged: never_know: true]`) and Integration Mode (e.g. BODY-LANDED). Exercise placeholder: `{EXERCISE: description}` with level/duration. Reference: `talp/analyze_intake/relationship_anxiety_la_gen_z.md`.

**Short format (the_quiet_in_the_crowd):** Beat map: ground_first. Emotional temperature: cool (Ch1). Section types per chapter: HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION with word counts. Engines: false_alarm, spiral, watcher. Format: 3 chapters × 6 section types; ~12 min audio. Reference: `talp/analyze_intake/the_quiet_in_the_crowd.md`.

**Forward reference (planner-controlled archetypes):** chapter shape is increasingly planner-driven via archetype policies. Writers should expect these fields in future intake manifests:
- `arc_role` (`introduce|deepen|challenge|resolve`)
- `exercise_mode` (`none|micro|full`)
- `reflection_weight` (`light|standard|heavy`)
- `story_depth` (`micro|standard|deep`)

Until the archetype intake schema is fully published, continue writing section atoms per this spec; planner applies chapter-level distribution and transitions at assembly time.

**Integration modes and tagging:** Document integration modes (e.g. BODY-LANDED) and story tagging (e.g. never_know, misfire_tax) as optional but recommended so assembly and QA can use them. Standardize **{EXERCISE: description}** (and level/duration) in writer-facing instructions so mining and assembly stay aligned.

---

**This document is everything you need.** The system tells you what to write. This document tells you how to write it for a robot that will read it flat. Write for the robot. Write for the ear. Write one atom at a time. **The constraint creates the quality. The text itself must breathe.**

---

**Still to do (whole system):** What remains to finish the whole V4 system is in the canonical systems doc and planning status: [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md) § Remaining to finish whole system, [../docs/PLANNING_STATUS.md](../docs/PLANNING_STATUS.md). For a concise brief to writers on what to deliver so the system runs 100%, see [../docs/WRITER_COMMS_SYSTEMS_100.md](../docs/WRITER_COMMS_SYSTEMS_100.md).

---

# 23. Identity & Audiobook Governance Layer

## 23.0 Purpose

This section introduces governance for pen-name authors, brand-bound narrators, and audiobook front-matter assembly. It does not alter any existing canonical rule.

## 23.1 Scope Clarification

**Applies to:**
- Pen-name authors
- Brand-bound authors
- Audiobook narrator front matter

**Does NOT apply to or modify:**
- Teacher Mode Pre-Intro (governed by TEACHER_MODE_V4_CANONICAL_SPEC; 900–1200 words, 4 paragraphs, "I was not a direct student…" structure)
- STORY tense (third-person present remains canonical and unchanged)
- EXERCISE, REFLECTION, INTEGRATION, or other atom types
- Arc rules and emotional band definitions
- Six Atom Types
- TTS constraints (§3–§9)
- Persona definitions (§17)

If any rule in this section conflicts with §1–22 of this spec, §1–22 governs.

## 23.2 Author Registry Requirement (Pen-Name Authors Only)

All non-teacher pen-name authors must be registered in:

```
config/author_registry.yaml
```

Each author entry must define: `author_id` (key), `pen_name`, `brand_id`, `persona_ids`, `topic_ids`, `positioning_profile` (mandatory; must exist in `config/authoring/author_positioning_profiles.yaml`), `assets_path` (optional). Optional: `status` (draft | approved) when enforced.

**Compile fails if:** Author ID not found; author topic not in `topic_ids`; author persona not in `persona_ids`; author `positioning_profile` missing or not in author_positioning_profiles. No silent fallback. No default author. Brand default author may be resolved via `config/brand_author_assignments.yaml`.

## 23.3 Author Asset Contract

Each pen-name author must supply all four assets before compile is permitted. Assets live at:

```
assets/authors/{author_id}/
    bio.yaml
    why_this_book.yaml
    authority_position.yaml
    audiobook_pre_intro.yaml
```

**No asset may be runtime-generated.** All assets must be human-written and approved before `status: approved` is set in the registry.

Asset word ranges: bio.yaml 120–180; why_this_book.yaml 150–250; authority_position.yaml 100–150; audiobook_pre_intro.yaml 500–900 (narrator-read framing).

## 23.4 Audiobook Pre-Intro Layer (Narrator Front Matter)

**Separate from Teacher Mode Pre-Intro.** Applies to pen-name books only.

The narrator reads the following blocks in order before Chapter 1: `narrator_intro`, `book_title_line`, `series_line` (omit if no series), `author_intro`, `author_background`, `why_this_book`, `transition_line`.

**Content rules:** No marketing language; no transformation promises; no invented credentials; no first-person emotional appeals beyond lived context; must be persona-aware in `author_background` and `why_this_book`.

**Assembly:** Identity Binding (e.g. Stage 2.5), before arc compile. See OMEGA_LAYER_CONTRACTS for schema extension.

## 23.5 Narrator Registry

Narrators must exist in `config/narrators/narrator_registry.yaml` with: `narrator_id`, `display_name`, `brand_compatibility`, `persona_alignment`, `pacing_profile`, `voice_engine_id`, `disallowed_topics` (optional), `status` (draft | approved).

**Compile fails if:** Narrator not found; narrator `brand_compatibility` does not include current `brand_id`; narrator `status` is not `approved`; narrator `disallowed_topics` overlaps current topic.

## 23.6 Brand Registry Extension

The brand registry must include for identity binding: `allowed_authors`, `default_narrators`, `tone_constraints`, `audio_pacing_profile`. These fields are additive. Config location: see [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md) and [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md).

## 23.7 Persona Specificity Enforcement (Additive)

Applies to all STORY and SCENE atoms. Does not change existing emotional band or TTS rules.

Every STORY and SCENE atom must contain: **≥ 1 micro-stake** (small, socially meaningful consequence specific to the persona); **≥ 1 environmental cue** (physical location, sound, artifact, or social hierarchy signal); **Persona-realistic stressor**.

**STORY tense remains third-person present. Unchanged.**

Atoms failing persona specificity may not be promoted to `status: confirmed`. They remain `status: provisional_template` until upgraded. See [../docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md](../docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md).

## 23.8 Atom Promotion State (Operational Metadata Only)

Atoms may carry optional metadata: `status: provisional_template | confirmed`.

**Rules:** This field is not evaluated at runtime assembly; it is enforced at content approval only. `provisional_template` may be used in development; `confirmed` only in production. Teacher Mode approval flow is unchanged.

**Promotion requires:** Persona overlay applied; micro-stake present and persona-specific; environmental cue present; repetition entropy acceptable (Golden Phoenix guide); human reviewer sets `status: confirmed`. No automated promotion.

## 23.9 Identity Binding Fail Conditions

Build fails (no silent fallback) if: Author not in registry or topic/persona/status invalid; any required asset missing; narrator not in registry or brand incompatible or status not approved; brand missing `allowed_authors` or `default_narrators`; author not in brand's `allowed_authors`.

**Implementation (pipeline):** `scripts/run_pipeline.py` uses `config/author_registry.yaml` (author_id, positioning_profile, optional assets_path). When author_id is set, `phoenix_v4/planning/author_asset_loader.py` loads the four assets from `assets/authors/{author_id}/` or from the registry's `assets_path` (directory or single multi-doc YAML). If any required asset is missing, the pipeline exits with failure (no silent fallback). Author may be resolved from brand via `config/brand_author_assignments.yaml` and `phoenix_v4/planning/author_brand_resolver.py` when `--author` is not supplied. Compiled plan output includes `author_assets`; freebie templates may use placeholders `{{author_bio}}`, `{{author_why_this_book}}`, `{{author_pen_name}}`, `{{author_audiobook_pre_intro}}`. See [OMEGA_LAYER_CONTRACTS.md](./OMEGA_LAYER_CONTRACTS.md) and [../docs/SYSTEMS_V4.md](../docs/SYSTEMS_V4.md).

## 23.10 What This Section Does Not Do

Does not add a new atom type; does not change STORY to second person; does not change emotional band definitions or arc structure; does not override Teacher Mode Pre-Intro; does not grant runtime prose generation rights.

---

# 24. Author Positioning Compliance

## 24.0 Purpose

Each compiled book carries a **trust posture signature** (Layer 2 Identity). The Author Positioning Profile governs tone constraints, narrative stance, allowed/forbidden phrasing bands, vulnerability exposure, and experience framing style. This section does not alter Layer 1 content integrity; it enforces voice, authority posture, and trust alignment.

**Config:** `config/authoring/author_positioning_profiles.yaml` defines profiles (e.g. somatic_companion, research_guide, elder_stabilizer). Each author in `config/author_registry.yaml` has a mandatory `positioning_profile`. BookSpec carries `author_positioning_profile`; when `author_id` is present it is resolved from the registry and must match.

## 24.1 Per-Chapter Compliance

Each compiled chapter must comply with:

- **trust_anchor_style** (companion | analyst | elder) — narrative stance and distance.
- **vulnerability_band** — how much first-person or confessional tone is allowed.
- **forbidden_language** — no use of the profile’s forbidden language list (e.g. academic_citation, command_language, slang, emotional_confession as defined per profile).

## 24.2 Vulnerability Band Enforcement

| Band     | Constraint |
|----------|------------|
| low      | No personal confessional tone. |
| moderate | Limited first-person experience allowed. |
| high     | Personal narrative allowed but must not exceed 30% of chapter word count. |

CI (e.g. `scripts/ci/check_author_positioning.py`) enforces these bands. Exceeding the band → FAIL.

## 24.3 Allowed vs Forbidden Language

Profiles define `allowed_language` and `forbidden_language` tags. Prose must stay within allowed bands and must not use forbidden patterns. Detection is pattern-based (first-person density, command density, academic markers, slang, mystical absolutism). Writer Spec §§1–23 unchanged; this section adds a compliance layer validated in CI.

## 24.4 What This Section Does Not Do

Does not change atom schema; does not modify STORY/REFLECTION/EXERCISE structure; does not override TTS or emotional governance rules.

---

# 26. Appendix C: T01 Rewrite Patterns

These examples show how to pass T01 (`teaching sentence > 12 words` = hard fail) without losing meaning.

1. Before: `Your nervous system interprets uncertainty as social danger and starts preparing you to hide.`
   After: `Your system reads uncertainty as danger. It prepares you to hide.`

2. Before: `When you delay your response, your body can learn that urgency is not safety.`
   After: `Delay the response. Let your body learn urgency is not safety.`

3. Before: `This pattern survives because avoidance brings relief quickly, even when it shrinks your life.`
   After: `Avoidance relieves you quickly. It also shrinks your life.`

4. Before: `The alarm is not proof of danger; it is proof of prediction.`
   After: `The alarm is not danger. It is prediction.`

---

# 25. Appendix B: Compression Atoms (slot_08_compression)

When a format includes the **COMPRESSION** slot (e.g. F006), each chapter gets one short, high-recall distillation (memory anchor + snippet/shareability). Structural only; no change to meaning or doctrine.

## 25.1 Requirements

- **Length:** 40–120 words (strict). CI fails outside this range.
- **Sentences:** 2–6.
- **One insight only:** No steps, no lists, no citations. No “first, second, third,” “here are,” or numbered lists. No more than one colon (avoids multi-idea enumeration). No more than two pivot markers (“but also,” “and also,” “another thing”) per atom.
- **Tone:** No lecturing. Present tense allowed. One reframe only.
- **TTS-safe:** No em dashes; avoid long semicolons. Short sentences; clean punctuation.
- **Persona:** Persona-specific cues allowed but minimal (1–2 max).

## 25.2 Where They Live

Approved atoms: `SOURCE_OF_TRUTH/compression_atoms/approved/<persona_id>/<topic_id>/*.yaml`. Each file: `atom_id`, `word_count` (40–120), optional `compression_family` (C1…C5 for diversity), `body`. Stage 3 selects deterministically from this pool. CI enforces word count and one-insight structure.
