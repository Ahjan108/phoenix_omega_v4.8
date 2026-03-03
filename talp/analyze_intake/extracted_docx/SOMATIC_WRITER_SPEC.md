# SOMATIC WRITER SPEC (extracted from .docx)

Source: GOLDEN_PHOENIX_Writer_Spec_Somatic_V2.docx

---

🔥 GOLDEN PHOENIX

COMPLETE WRITER EXECUTION SPEC

Somatic Audiobook Template V2

12 Chapters × 10 Sections × 5 Variants = 600 Files

SpiritualTech Systems — SOURCE_OF_TRUTH

Version 1.0 — February 2026

NON-NEGOTIABLE — NO INTERPRETATION

TABLE OF CONTENTS

1. Architecture Overview

2. Chapter & Phase Map

3. Section-by-Section Writer Spec (All 10 Types)

   3.1  HOOK (section_01)

   3.2  SCENE — Opening (section_02)

   3.3  REFLECTION — Sensation Inquiry (section_03)

   3.4  EXERCISE — First Practice (section_04)

   3.5  SCENE — Middle (section_05)

   3.6  TEACHERDOCTRINE (section_06)

   3.7  REFLECTION — Deep Sensing (section_07)

   3.8  EXERCISE — Integration Practice (section_08)

   3.9  SCENE — Resolution (section_09)

   3.10 INTEGRATION (section_10)

4. Teacher-Specific Writing Rules

5. Doctrine Writer Spec

6. Exercise Bank Writer Spec

7. Persona Adaptation Rules

8. SDG Integration (Writer-Level)

9. Injection Point Hydration Spec

10. Validation & QA Checklist

11. Completion Definition

1. ARCHITECTURE OVERVIEW

This spec governs ALL content creation for the Somatic V2 therapeutic audiobook template. The template generates personalized audiobooks by assembling pre-written sections with teacher-specific injections (stories + exercises). Every file in this system must pass validation before a teacher is considered 100% ready.

1.1 System Dimensions

Dimension

Count

Details

Chapters

12

3 per phase (HARDSHIP, HELP, HEALING, HOPE)

Sections per chapter

10

HOOK → SCENE → REFLECTION → EXERCISE → SCENE → TEACHERDOCTRINE → REFLECTION → EXERCISE → SCENE → INTEGRATION

Variants per section

5

F1–F5 for persona/voice diversity

Total template files

601

600 YAML sections + 1 registry.yaml

Injection types

2

[STORY_INJECTION_POINT] and [EXERCISE_INJECTION_POINT]

Target audio per book

~8–12 hrs

At 150 WPM with injected content

1.2 File Structure

sections_somatic_v2/

  registry.yaml                              # Master index of all sections

  chapter_01/                                 # Ch 1: The Body Remembers (HARDSHIP)

    section_01_hook/f1.yaml ... f5.yaml       # 5 variants

    section_02_scene/f1.yaml ... f5.yaml      # Opening scene

    section_03_reflection/f1.yaml ... f5.yaml # Sensation inquiry

    section_04_exercise/f1.yaml ... f5.yaml   # First somatic practice

    section_05_scene/f1.yaml ... f5.yaml      # Middle scene

    section_06_teacherdoctrine/f1.yaml ...     # Body wisdom teachings

    section_07_reflection/f1.yaml ... f5.yaml # Deep sensing

    section_08_exercise/f1.yaml ... f5.yaml   # Integration practice

    section_09_scene/f1.yaml ... f5.yaml      # Resolution scene

    section_10_integration/f1.yaml ... f5.yaml# Somatic synthesis

  chapter_02/ ... chapter_12/                  # Same structure

1.3 YAML File Schema (Every Section)

variant_id: ch01_sec01_hook_f1

chapter: 1

section: 1

section_type: HOOK

purpose: 'Opening — somatic hardship recognition'

variant_family: F1

content: '<full prose content here>'

fingerprint:

  char_count: 1130

  paragraph_count: 9

  sentence_count: 23

metadata:

  persona: Adult Professional

  topic: Somatic healing

  section_type: HOOK

  scene_type: null

  location_tokens: []

2. CHAPTER & PHASE MAP

Every chapter belongs to exactly one of four therapeutic phases. The phase determines the emotional arc, the type of somatic awareness cultivated, and the intensity of exercises. Writers MUST match tone, content, and instruction depth to the phase.

Ch

Title

Phase

Somatic Focus

01

The Body Remembers

HARDSHIP

Recognition of disconnection, stored tension, body signals ignored

02

Where Tension Lives

HARDSHIP

Mapping held tension, jaw/shoulder/gut patterns, chronic bracing

03

The Weight We Carry

HARDSHIP

Accumulated somatic burden, emotional weight in tissue

04

Reading Your Nervous System

HELP

Polyvagal awareness, window of tolerance, state identification

05

The Wisdom of Sensation

HELP

Sensation vocabulary, interoception, body as information source

06

Tools for Regulation

HELP

Breath, grounding, containment, co-regulation, vagal toning

07

Releasing What's Held

HEALING

Softening, tremor, spontaneous movement, pain as message

08

The Practice of Presence

HEALING

Embodied presence, tracking sensation, staying with discomfort

09

Building New Pathways

HEALING

Neuroplasticity, new patterns, expanded window of tolerance

10

The Body Opening

HOPE

Capacity for pleasure, aliveness, felt sense of possibility

11

Embodied Wholeness

HOPE

Integration of all parts, wholeness as felt experience

12

Moving Forward in Your Body

HOPE

Embodied agency, ongoing practice, body as home

2.1 Phase Writing Rules

HARDSHIP (Ch 1–3): Tone is compassionate recognition. The listener is being seen, possibly for the first time. Do NOT rush to solutions. Exercises are gentle (body scan, grounding, breath awareness). Scenes show characters disconnected from their bodies. Doctrine acknowledges that the body keeps the score.

HELP (Ch 4–6): Tone shifts to education and empowerment. The listener is learning new frameworks. Exercises introduce regulation tools. Scenes show characters discovering body literacy. Doctrine introduces nervous system science (polyvagal, vagus nerve, window of tolerance).

HEALING (Ch 7–9): Tone becomes permission-giving and tender. The listener is ready to feel and release. Exercises become more intensive (movement, sound, deeper breath). Scenes show characters in active release. Doctrine frames healing as a body-led process.

HOPE (Ch 10–12): Tone is expansive and forward-looking. The listener is integrating and embodying new capacities. Exercises focus on aliveness and agency. Scenes show characters living differently in their bodies. Doctrine frames the body as home.

3. SECTION-BY-SECTION WRITER SPEC

Each chapter has exactly 10 sections in fixed order. This section defines MANDATORY requirements for every section type. No exceptions. No interpretation.

3.1 HOOK (section_01)

Attribute

Specification

Position

Always section 1 of every chapter

Purpose

Somatic {phase} recognition — bring the listener INTO their body immediately

Target length

~180–250 words per variant

Variants required

5 (F1–F5)

Injection points

NONE

Tone

Direct, intimate, second-person (you/your)

Writing Rules for HOOK

Every hook MUST open with a somatic instruction (not a concept). The very first sentence puts the listener in contact with their body. Examples: 'Put your hand on your chest right now.' / 'Feel your feet on the floor.' / 'Notice your breathing without changing it.'

The hook then names the somatic reality of the phase. In HARDSHIP, it names tension, numbness, disconnection. In HELP, it names the possibility of reading body signals. In HEALING, it names softening and release. In HOPE, it names aliveness and integration.

HARD FAIL: Hooks that begin with abstract concepts, quotes, or intellectual framing. The listener must feel something in the first 10 seconds.

HARD FAIL: Hooks that exceed 300 words. This is a somatic opening, not a lecture.

3.2 SCENE — Opening (section_02)

Attribute

Specification

Position

Always section 2 — first scene slot

Purpose

Body story — {phase} in the flesh

Scene type

opening — introduces the character's somatic reality

Target length

~100–150 words (frame around injection point)

Injection point

[STORY_INJECTION_POINT] — REQUIRED, exactly one per variant

Characters

Named characters with specific somatic patterns (Elena, Marcus, etc.)

Writing Rules for SCENE (All Positions)

Scenes are frames around injected teacher-specific stories. The frame text introduces a character, establishes their somatic situation, places the [STORY_INJECTION_POINT] marker, then asks the listener to connect to their own body experience.

Characters MUST have: (a) a named identity, (b) a specific body pattern (not generic 'stress'), (c) sensory detail (where in the body, what sensation).

Opening scenes (section_02): Introduce the character's disconnection/problem. End with a reflective question that connects to the listener.

Middle scenes (section_05): Show the messy middle. The character's body is changing but it's uncomfortable. Healing looks like breaking.

Resolution scenes (section_09): Show embodied change. Not dramatic transformation—a new normal. A baseline that used to be impossible.

HARD FAIL: Scenes without [STORY_INJECTION_POINT].

HARD FAIL: Scenes with more than one [STORY_INJECTION_POINT].

HARD FAIL: Scenes that tell rather than show the body experience.

3.3 REFLECTION — Sensation Inquiry (section_03)

Attribute

Specification

Position

Section 3 — first reflection slot

Purpose

Sensation inquiry — feeling {phase}

Target length

~150–220 words

Injection points

NONE

Tone

Gentle, inquiring, permission-giving

Writing Rules for REFLECTION (Both Positions)

Reflections guide the listener into direct somatic inquiry. They ask the listener to scan, sense, track, or inquire into body experience. They do NOT teach or explain—they guide attention.

Section 03 (Sensation Inquiry): Early-chapter reflection. Body scan, noticing what's present, naming sensations. More surface-level, establishing baseline awareness.

Section 07 (Deep Sensing): Late-chapter reflection. Deeper layers. Felt sense, body intelligence, the knowing beneath thought. More contemplative and integrative.

Every reflection MUST include at least one direct somatic question: 'What do you notice?' / 'Where in your body do you feel that?' / 'What's the quality of the sensation—sharp, dull, warm, cold, heavy, light?'

HARD FAIL: Reflections that stay in the cognitive/intellectual domain without directing attention to the body.

3.4 EXERCISE — First Practice (section_04)

Attribute

Specification

Position

Section 4 — first exercise slot

Purpose

Somatic practice — {phase} in body

Target length

~80–130 words (frame around injection point)

Injection point

[EXERCISE_INJECTION_POINT] — REQUIRED, exactly one per variant

Frame structure

Setup (why this practice) → injection → debrief (what to notice)

Writing Rules for EXERCISE (Both Positions)

Exercises are frames around injected teacher-specific somatic practices. The frame provides context before the injection and integration after it.

Section 04 (First Practice): Foundational exercise for the chapter's phase. Simpler, more accessible. Establishes the somatic skill being built.

Section 08 (Integration Practice): Deeper/more advanced exercise. Builds on section 04. May combine multiple modalities (breath + movement, sound + sensation).

The frame MUST include: (a) a 2–3 sentence setup explaining what we're about to do and why, (b) the [EXERCISE_INJECTION_POINT] marker, (c) a 2–3 sentence debrief inviting the listener to notice what shifted.

HARD FAIL: Exercise frames without [EXERCISE_INJECTION_POINT].

HARD FAIL: Frames that give actual exercise instructions (the injected content does that).

HARD FAIL: Debriefs that prescribe what the listener should have felt (e.g., 'You should feel calmer now').

3.5 SCENE — Middle (section_05)

Same rules as section_02 SCENE, with scene_type = 'middle'. See 3.2 for full spec.

Key difference: Middle scenes show the messy process. The character is IN the work. Healing looks uncomfortable. The body is speaking louder. Progress doesn't feel like progress.

3.6 TEACHERDOCTRINE (section_06)

Attribute

Specification

Position

Section 6 — the doctrine slot (center of the chapter)

Purpose

Body wisdom — {phase} teachings

Target length

~250–350 words per variant

Injection points

NONE (but content MUST be teacher-hydration-ready)

Current content

Generic somatic science (polyvagal, van der Kolk, vagus nerve)

Required evolution

Must become teacher-specific doctrine when hydrated

CRITICAL: Teacher Doctrine Hydration

The current template contains generic body wisdom content in section_06. When the assembler hydrates a book for a specific teacher, the TEACHERDOCTRINE content must be replaced or augmented with that teacher's specific doctrine for the chapter's topic.

This means writers must produce TWO layers:

Layer 1 — Base Template (already written): Generic somatic science that works for any teacher. This is the fallback content.

Layer 2 — Teacher Doctrine Override (NEW — writers must produce): Teacher-specific doctrine files that replace the base when that teacher is active. See Section 5 for the full doctrine writer spec.

The doctrine section is the heart of what makes each teacher unique. Without it, all books sound the same.

NON-NEGOTIABLE: Every teacher MUST have doctrine overrides for every topic/phase. If doctrine is missing, the teacher is NOT 100%.

3.7 REFLECTION — Deep Sensing (section_07)

Same rules as section_03 REFLECTION, but deeper. See 3.3 for full spec.

Key difference: Section 07 goes beneath surface sensation into felt sense, body intelligence, and the knowing beneath thought. It assumes the listener has already done the earlier scan (section_03) and the first exercise (section_04). The reflection here is more contemplative, more willing to sit in ambiguity.

3.8 EXERCISE — Integration Practice (section_08)

Same rules as section_04 EXERCISE. See 3.4 for full spec.

Key difference: Section 08 exercises are more advanced. They may use movement, sound, or deeper breath work. They build on the foundation laid in section_04. The debrief emphasizes capacity building: 'Notice how much more is available now.'

3.9 SCENE — Resolution (section_09)

Same rules as section_02 SCENE, with scene_type = 'resolution'. See 3.2 for full spec.

Key difference: Resolution scenes show embodied change landing. Not fireworks—a quiet new normal. The character's body has shifted in a way that's now default. 'Elena's shoulders finally dropped—not temporarily, fundamentally.'

3.10 INTEGRATION (section_10)

Attribute

Specification

Position

Section 10 — final section of every chapter

Purpose

Somatic synthesis — {phase} complete

Target length

~200–280 words

Injection points

NONE

Tone

Gathering, synthesizing, grounding, forward-looking

Writing Rules for INTEGRATION

The integration section gathers the entire chapter experience and lands it in the body. It names what happened (without lecturing), acknowledges what shifted, and points forward to what's next.

Structure: (a) Acknowledge the journey of the chapter ('Let's gather what just happened in your body'), (b) Name the key somatic shift, (c) Invite the listener to notice where they are now, (d) Bridge to next chapter.

The final integration (Ch 12, section_10) is the book's closing. It should feel like a complete arrival—not an ending but a beginning of embodied living.

HARD FAIL: Integrations that introduce new concepts (this is synthesis, not new material).

HARD FAIL: Integrations that skip the body and go intellectual ('Today we learned about...').

4. TEACHER-SPECIFIC WRITING RULES

Each teacher in the system has a unique somatic lineage and must be written with strict fidelity to their tradition. The following are MANDATORY writing rules per teacher. When in doubt: if it could be said by any teacher, it's too generic.

4.1 Master Wu — Taoist Geomantic Healing

Opening Attunement (NO EXCEPTIONS)

Every Master Wu exercise MUST begin with:

1. Attuning to the Dragon's Meridian (spine as internal dragon vein)

2. Geomantic awareness (connection to land/earth)

3. Embodied sensing (not visualization alone—felt sensation)

Required Elements (ALL)

Visualization of COLOR: gold, jade green, deep earth red, sky blue. Sensation of VIBRATION/current/flow. Connection to: spine = internal dragon vein, land = external dragon veins. Clear Taoist structure: grounding → circulation → settling → return.

FORBIDDEN: Mindfulness-only language. Western therapy framing. Generic 'focus on your breath' without Taoist context. Any exercise that could belong to a different teacher.

Master Wu Doctrine Voice

Master Wu speaks through nature metaphors and energetic geography. His doctrine references: the Five Elements, dragon vein theory, dantian cultivation, Wei Wu Wei (effortless action), and seasonal/celestial cycles. He never uses clinical language (no 'nervous system,' no 'polyvagal'). Instead: 'When the jade current rises through the lower gate...'

4.2 [Additional Teachers]

This section must be extended with equivalent depth for EVERY teacher in the system. Each teacher entry requires: Opening protocol, Required elements, Forbidden elements, Doctrine voice. No teacher may ship without this section being complete.

Writers: If you are assigned a teacher not yet documented here, STOP and request the teacher's lineage brief before writing any content.

5. DOCTRINE WRITER SPEC

Doctrine defines teacher uniqueness. Without doctrine, exercises are invalid. Without doctrine, all books sound the same. Doctrine is the MOST CRITICAL artifact a writer produces.

5.1 File Location

SOURCE_OF_TRUTH/data/teachers/<teacher_id>/doctrine/<topic>.yaml

5.2 Required Fields (ALL MANDATORY)

topic: <topic>

teacher_id: <teacher_id>

 

signature_move:

  name: '<unique named move>'

  description: '<what makes THIS teacher different for THIS topic>'

 

reframe:

  core_belief_shift: '<old belief> → <new belief>'

  explanation: '<teacher-specific explanation>'

 

identity_shift:

  from: '<identity before>'

  to: '<identity after>'

 

closing_orientation:

  how_the_listener_leaves: '<felt state + worldview>'

 

language:

  preferred_terms: [list]

  avoided_terms: [list]

 

sdg_alignment:

  primary_sdgs: [SDG numbers]

  rationale: '<how this teaching contributes to those SDGs>'

5.3 Doctrine Hard Rules

❌ No generic spirituality. If a passage could come from any teacher, it fails.

❌ No cross-teacher reuse. Each doctrine must be wholly unique.

❌ No copy/paste doctrine. If two teacher doctrines share >20% similar phrasing, both fail.

✅ Must feel inevitable for that teacher. Reading the doctrine, you should think: 'Of course. Only this teacher would say it this way.'

5.4 Somatic Doctrine Mapping

For the somatic template specifically, each teacher's doctrine must address the body through their unique lens:

Phase

Doctrine Must Address

Through Teacher's Lens

HARDSHIP

Why the body stores pain / how disconnection serves protection

Teacher's tradition-specific explanation

HELP

How to read the body's signals / what the body is communicating

Teacher's specific framework for body literacy

HEALING

How the body releases and reorganizes / what permits letting go

Teacher's specific release methodology

HOPE

What embodied wholeness feels like / the body as home

Teacher's vision of full embodiment

6. EXERCISE BANK WRITER SPEC

Exercises are what listeners DO in their bodies. They are injected at [EXERCISE_INJECTION_POINT] markers. Each teacher needs a full bank of exercises that the assembler can draw from.

6.1 File Location

SOURCE_OF_TRUTH/data/teacher_banks/<teacher_id>/exercises/<teacher>_<topic>_eXX.json

6.2 Minimum Exercise Counts (Per Topic)

Intensity

Minimum Per Topic

When Used

Low

3

HARDSHIP chapters (section_04 first practice), early HELP

Medium

3

Mid-book chapters (HELP section_08, HEALING section_04)

High

2

Late HEALING, HOPE chapters (section_08 integration practices)

That's a minimum of 8 exercises per teacher per topic. With the somatic template covering 12 chapters across 4 phases, a fully realized teacher needs sufficient exercises to populate 24 injection points (2 per chapter × 12 chapters) without repetition across the 5 variant paths.

6.3 Exercise JSON Schema (REQUIRED)

{

  "exercise_id": "master_wu_anxiety_e01",

  "teacher_id": "master_wu",

  "topic": "anxiety",

  "name": "Internal Dragon Vein Attunement",

  "intensity": "medium",

  "duration_seconds": 180,

  "persona_tags": ["gen_z", "gen_alpha", "adults"],

  "somatic_modality": "breath_and_visualization",

  "framing": {

    "short": "...",

    "standard": "...",

    "long": "..."

  },

  "instructions": [

    "Step 1: Bring attention to the spine as the internal dragon vein...",

    "Step 2: Visualize a warm golden current rising...",

    "Step 3: Feel the subtle vibration as the current enters..."

  ],

  "integration_bridge": "Notice how the meridian continues to pulse..."

}

6.4 Somatic Modalities (Tag Required)

Modality Tag

Description

Example

breath

Breathing practices

Vagal toning breath, extended exhale

body_scan

Systematic awareness

Full body scan, targeted area scan

grounding

Connection to ground/support

Feet-floor contact, seated grounding

movement

Somatic movement

Shaking, pendulation, micro-movements

sound

Vocal/auditory

Humming, toning, sighing

visualization

Imagery combined with sensation

Color/light in body, energy flow

breath_and_visualization

Combined modality

Breathing with energetic imagery

containment

Boundary/regulation

Imaginal container, hands-on-body holds

touch

Self-touch practices

Hand on heart, bilateral tapping

7. PERSONA ADAPTATION RULES

The current somatic template defaults all metadata to 'Adult Professional.' For full coverage, each teacher's exercises must include persona_tags that map to the system's persona registry. The template frame content (sections 01–10) uses language accessible to all personas, but injected content (stories + exercises) must be persona-aware.

7.1 Persona-Specific Language Rules

Persona

Language Adaptation

Exercise Framing

NYC Executive

Direct, time-conscious, ROI-aware. Body as high-performance asset.

Frame as performance optimization. 'This practice takes 90 seconds and changes your nervous system state.'

Healthcare Worker

Compassion fatigue aware, familiar with clinical terms. Body as both tool and burden.

Frame as self-care that enables care of others. Acknowledge somatic cost of caregiving.

Gen Z

Authentic, non-performative, meme-literate. Body positivity aware.

Frame as embodiment practice. Avoid clinical coldness. 'Your body is not a project to fix.'

Gen Alpha

Digital native, shorter attention spans, sensory-rich.

Shorter exercises, more vivid imagery, gamified elements where appropriate.

Trauma Survivor

Trauma-informed, choice-based, never directive.

Always offer opt-outs. 'If this feels like too much, you can...' Titration over intensity.

CRITICAL: Persona tags in exercises determine which exercises the assembler selects. If an exercise has no persona_tags, it's orphaned and will never be used. Every exercise MUST have at least one persona tag.

8. SDG INTEGRATION (Writer-Level)

Writers do NOT write SDG sections directly. The assembler surfaces SDG alignment from doctrine. However, writers must embed SDG logic into their doctrine and exercise design so the system can detect it.

8.1 SDG Mapping for Somatic Content

SDG

Somatic Connection

Writer Action

SDG 3: Good Health

Direct: somatic practices improve physical + mental health

Ensure exercises target measurable health outcomes (stress reduction, sleep, pain)

SDG 4: Quality Education

Body literacy is education; interoceptive awareness is a learnable skill

Frame teachings as skill-building, not just experience

SDG 5: Gender Equality

Somatic agency empowers all bodies; trauma-informed care disproportionately helps women

Include diverse body experiences; avoid gendered body assumptions

SDG 10: Reduced Inequalities

Somatic healing accessible to all, not just privileged

Exercises require no equipment, no special space, no cost

SDG 16: Peace & Justice

Regulated nervous systems reduce interpersonal violence

Frame regulation as contribution to collective peace

Writers must ensure exercises support: emotional regulation, resilience, agency, and social harmony. Make the SDG linkage obvious to the system by including relevant terms in doctrine rationale fields.

9. INJECTION POINT HYDRATION SPEC

The assembler replaces injection point markers with teacher-specific content at build time. This section defines exactly what content fills each injection type.

9.1 [STORY_INJECTION_POINT]

Attribute

Specification

Appears in

SCENE sections only (section_02, section_05, section_09)

Count per section

Exactly 1

Replaced with

Teacher-specific story content (~300–800 words)

Content source

Teacher story banks matched by topic + phase + scene_type

Frame text remains

YES — the frame text before and after the marker stays

9.2 [EXERCISE_INJECTION_POINT]

Attribute

Specification

Appears in

EXERCISE sections only (section_04, section_08)

Count per section

Exactly 1

Replaced with

Teacher-specific somatic exercise instructions (~200–800 words)

Content source

Teacher exercise banks matched by topic + intensity + persona

Frame text remains

YES — setup before and debrief after the marker stays

Framing selection

short/standard/long based on audiobook length target

9.3 Hydration Order

1. Assembler selects variant family (F1–F5) based on persona and path diversity.

2. For each SCENE section: match teacher story bank → inject at [STORY_INJECTION_POINT].

3. For each EXERCISE section: match teacher exercise bank by intensity + persona → inject at [EXERCISE_INJECTION_POINT].

4. For TEACHERDOCTRINE (section_06): if teacher doctrine override exists, replace base content entirely. If not, use base (and flag teacher as incomplete).

5. All other sections (HOOK, REFLECTION, INTEGRATION) use template content as-is.

10. VALIDATION & QA CHECKLIST

Reviewers enforce the following checks. Any failure = content is rejected and returned to writer.

10.1 Section-Level Validation

Check

Section Types

Failure Mode

Injection point present and correct

SCENE (must have [STORY_INJECTION_POINT]), EXERCISE (must have [EXERCISE_INJECTION_POINT])

HARD FAIL — section is broken without it

No injection point in wrong section

HOOK, REFLECTION, TEACHERDOCTRINE, INTEGRATION must have ZERO injection points

HARD FAIL — assembler will break

Word count within range

All sections

WARN if >20% outside target range

Phase tone match

All sections

HARD FAIL if HARDSHIP content sounds hopeful or HOPE content sounds despairing

5 variants exist

All sections

HARD FAIL if any variant missing

Variant distinctiveness

All sections

HARD FAIL if >30% textual overlap between variants of same section

10.2 Teacher-Level Validation

Check

What's Checked

Failure Mode

Doctrine exists for all phases

4 doctrine files (HARDSHIP, HELP, HEALING, HOPE)

HARD FAIL — teacher is not 100%

Signature move detectable

Must appear in exercise framing or instructions

HARD FAIL — exercises not anchored to teacher

Language matches doctrine

preferred_terms used, avoided_terms absent

HARD FAIL — teacher voice broken

Exercise count meets minimum

8+ exercises per topic (3 low, 3 med, 2 high)

HARD FAIL — assembler can't fill all slots

Persona tags present

Every exercise has at least 1 persona tag

HARD FAIL — exercise is orphaned

No cross-teacher content

Doctrine and exercises unique to this teacher

HARD FAIL — breaks teacher identity

10.3 Registry Validation

After all content is written, the registry.yaml must be regenerated and pass these automated checks:

1. Every chapter (01–12) has exactly 10 sections.

2. Every section has exactly 5 variants (F1–F5).

3. Fingerprints (char_count, paragraph_count, sentence_count) are recalculated and match actual content.

4. No variant_id collisions.

5. All scene_type values are correct (opening/middle/resolution/null).

11. COMPLETION DEFINITION

A teacher is 100% READY only when ALL of the following are true:

Requirement

Verification Method

Status

Doctrine exists for EVERY phase (HARDSHIP, HELP, HEALING, HOPE)

File check: 4 doctrine YAML files exist

☐

Exercises exist at required counts for EVERY topic

Count check: ≥8 per topic (3 low + 3 med + 2 high)

☐

All exercises pass doctrine anchoring validation

Automated: signature_move appears in framing or instructions

☐

Persona compatibility covers all target personas

Tag check: persona_tags span full registry

☐

Teacher-specific writing rules documented (Section 4)

Human review: opening protocol, required/forbidden elements

☐

SDG alignment embedded in doctrine

Field check: sdg_alignment present with rationale

☐

CI coverage check passes with ZERO warnings

Automated: full validation suite green

☐

Anything less = UNFINISHED.

11.1 What This Solves

After this spec is followed, there is NO difference between 'template exists' and 'teacher supported.' Somatic, bestseller, contrarian, and SDG formats all work. No silent fallback. No partial teachers. No special cases.

Templates become interchangeable. Teachers become complete.

11.2 The Final Truth

This spec transforms the system from:

  'We can generate books'

Into:

  'We are structurally incapable of generating incomplete ones.'