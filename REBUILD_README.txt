Perfect — here is the **Phoenix V4 Dev Onboarding Packet** you can hand directly to senior engineers.
This is written to **rebuild V4 from scratch**, without needing past chats.

---

# 🧭 Phoenix V4 — Developer Onboarding Packet

**Authoritative System Overview & Build Guide**

> **One-line mission:**
> Phoenix V4 scales *human-written therapeutic journeys* without letting machines invent, dilute, or resolve meaning.

---

## 1. What Phoenix V4 Is (Plain English)

Phoenix V4 is **not an AI writing system**.

It is a **content assembly system** that:

* takes **human-written truth**
* decomposes it into **safe, composable units**
* enforces **therapeutic + narrative rules**
* and **reassembles journeys at runtime**

💡 If a model is “writing prose,” you are building the wrong thing.

---

## 2. The Core Design Principle (Non-Negotiable)

> **Humans create meaning.
> Machines enforce structure.
> Runtime only assembles.**

Everything else follows from this.

---

## 3. High-Level Architecture

### Three Worlds (Never Mixed)

```
1. HUMAN WORLD (Offline, Read-Only)
2. SYSTEM WORLD (Approved Assets)
3. RUNTIME WORLD (Assembly Only)
```

If something crosses worlds incorrectly → **hard failure**.

---

## 4. HUMAN WORLD (Offline Authoring)

**Purpose:** Capture lived, culturally grounded truth.

### Inputs (Human-written only)

* Full self-help books
* Person-based stories with:

  * people
  * locations
  * peers
  * stakes
* Exercises with structure:

  * intro → practice → ah-ha → integration
* Cultural / local specificity

### Rules

* ❌ Runtime never reads these files
* ❌ Models never paraphrase them
* ✅ They are *source material only*

**Think:** research corpus, not content library.

---

## 5. SEED MINING (Offline Transformation)

This is where human truth becomes scalable.

### Pipeline

1. **Semantic segmentation**

   * incident
   * body
   * validation
   * pattern
   * mechanism
   * agency opening
2. **Role mapping**

   * recognition
   * embodiment
   * pattern
   * mechanism_proof
   * agency_glimmer
3. **Rewrite → micro-atoms**

   * 60–90 words
   * second person
   * present tense
   * unresolved
4. **Hard lint**

   * no reassurance
   * no resolution
   * role purity
   * cadence ordering
5. **Repair loop (bounded)**
6. **Human approval**

### Output

Only **approved assets** survive.

```
SOURCE_OF_TRUTH/
├── approved_atoms/
├── approved_scenes/
└── approved_exercises/
```

---

## 6. SYSTEM WORLD (Source of Truth)

This is the **only content runtime can see**.

### Asset Types

#### 1. Story Atoms

* Role-pure
* Emotionally incomplete
* Persona-agnostic
* Location injected later

#### 2. Scenes

* Person-based
* Have stakes
* Carry narrative tension
* Used to *support* ideas, not replace them

#### 3. Exercises

* Fixed structure
* Nervous-system aware
* Never motivational speeches

---

## 7. Exercise System (Critical)

Exercises are **functional**, not expressive.

### Canonical Exercise Types

```
00_breath_regulation.yaml
01_grounding_orientation.yaml
02_body_awareness_scan.yaml
03_somatic_release_discharge.yaml
04_nervous_system_downregulation.yaml
05_nervous_system_upregulation.yaml
06_vagal_stimulation_sound.yaml
07_self_contact_touch.yaml
08_emotional_processing_completion.yaml
09_embodied_intention_direction.yaml
10_integration_return_to_baseline.yaml
```

### Required Structure (Every Exercise)

1. Intro (why now)
2. Practice (what to do)
3. Ah-ha (what changed)
4. Integration (return to life)

❌ No advice
❌ No persuasion
❌ No fixing the reader

---

## 8. RUNTIME WORLD (Assembly Only)

Runtime **never generates prose**.

### Runtime Responsibilities

* Select approved assets
* Order them via a plan
* Inject:

  * persona variables
  * topic variables
  * location overlays
* Validate completeness

### Runtime Cannot:

* rewrite text
* “improve” content
* fill missing meaning

If something is missing → **no book ships**

---

## 9. Planning Layer (How Books Are Shaped)

Plans declare **requirements**, not text.

Example:

* Persona: Gen-Z student
* Topic: Anxiety
* Stakes: social exposure
* Required:

  * 3 recognition atoms
  * 2 scenes with peers
  * 1 downregulation exercise
  * 1 integration exercise

Plans are **contracts**.

---

## 10. Validation Gates (Why Quality Holds)

A book fails if:

* narrative arc incomplete
* no stakes
* exercises missing
* cadence broken
* persona violated

There is **no fallback content**.

Fail fast > degrade silently.

---

## 11. Why This Does NOT Become “Therapeutic Bullet Points”

Your concern is valid — here’s why it doesn’t happen:

### What prevents bullet-point books

* Scenes with people + stakes are mandatory
* Atoms are incomplete on purpose → must be chained
* Exercises regulate pacing, not content
* Plans enforce narrative arcs
* Runtime cannot summarize or compress meaning

Result:

> The reader experiences a **journey**, not tips.

---

## 12. What Devs Need From You (Action List)

### Required

1. **Human-written source material** (even partial)
2. **Exercise files** (old V4 is perfect input)
3. **Persona definitions**
4. **Topic taxonomy**
5. **Story examples with stakes**

### Optional (Nice to have)

* Old template families (as analysis, not runtime)
* Old atom libraries (for comparison)

### Do NOT give devs

* 100+ chat logs
* partially evolved specs without context

This packet **replaces** that history.

---

## 13. Rebuild Order (Recommended)

**Week 1**

* Set up repo structure
* Enforce world separation
* Add CI guards

**Week 2**

* Seed mining + lint
* Approval tooling

**Week 3**

* Runtime planning + assembly
* Exercise slotting

**Week 4**

* Validation gates
* End-to-end test book

---

## 14. One Sentence Dev Test

Ask any dev:

> “Can runtime create a new sentence?”

If the answer is **yes**, V4 is broken.

---

## Final Note (Important)

Phoenix V4 is **opinionated on purpose**.
It trades:

* flexibility ❌
  for
* trust, safety, and depth ✅

That’s why it works.

---

If you want next, I can:

* turn this into a **PDF onboarding doc**
* write a **technical task breakdown per engineer**
* or generate a **repo skeleton with README files**

Just say the word.

Got it. Here are **both**, clean, canonical, and ready to hand to devs or leadership.

---

# 🧭 Phoenix V4 — Single Visual Flow Diagram (Authoritative)

You can paste this directly into docs or turn it into a diagram later.
This is the **mental model everyone must share**.

```
┌────────────────────────────┐
│   HUMAN AUTHORING (OFFLINE)│
│                            │
│ • Handwritten books        │
│ • Person-based scenes      │
│ • Exercises (structured)   │
│ • Cultural & local truth   │
│ • Author authority rules   │
│                            │
│  ❌ NEVER used at runtime  │
└─────────────┬──────────────┘
              │  (read-only, human truth)
              ▼
┌────────────────────────────┐
│ SEED MINING & DECOMPOSITION│
│        (OFFLINE)           │
│                            │
│ • Semantic segmentation    │
│ • Role extraction          │
│ • Rewrite → micro-atoms    │
│ • Lint + cadence gates     │
│ • Repair loop (bounded)    │
│ • Human approval required  │
│                            │
│ Output: APPROVED ASSETS    │
└─────────────┬──────────────┘
              │  (sealed, immutable)
              ▼
┌────────────────────────────┐
│     SOURCE OF TRUTH        │
│                            │
│ • approved_atoms/          │
│ • approved_scenes/         │
│ • approved_exercises/      │
│                            │
│ ✅ Only thing runtime sees │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│        PLANNING LAYER      │
│        (RUNTIME)           │
│                            │
│ • Persona                  │
│ • Topic                    │
│ • Stakes                   │
│ • Narrative arc            │
│ • Required story roles     │
│ • Exercise functions       │
│                            │
│ ❌ No prose generation     │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│       ASSEMBLY LAYER       │
│        (RUNTIME)           │
│                            │
│ • Select approved assets   │
│ • Order by plan            │
│ • Inject scenes            │
│ • Insert exercises         │
│ • Hydrate variables        │
│                            │
│ ❌ No rewriting            │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│      VALIDATION GATES      │
│        (RUNTIME)           │
│                            │
│ • Safety                   │
│ • Cadence                  │
│ • Narrative completeness  │
│ • Persona integrity        │
│                            │
│ FAIL = NO BOOK             │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│     FINISHED BOOK OUTPUT   │
│                            │
│ • Journey-based            │
│ • Human-feeling            │
│ • Therapeutically safe     │
│ • Scalable                 │
└────────────────────────────┘
```

**One sentence summary for devs:**

> *Humans create truth, tools distill it, runtime assembles it, and nothing writes prose.*

---

# 🔟 Phoenix V4 — “In 10 Rules” Manifesto

This is the **north star**.
If any rule is violated, the system is no longer V4.

---

### **Rule 1 — Humans write lived experience**

All real stories, people, locations, and emotional truth are **human-authored**.

No exceptions.

---

### **Rule 2 — Runtime never invents prose**

V4 **does not write**.
It selects, orders, and hydrates.

If it writes, it’s broken.

---

### **Rule 3 — Meaning scales, prose does not**

Human prose is **decomposed into meaning** (atoms, scenes, exercises), not reused or paraphrased.

---

### **Rule 4 — All runtime content is pre-approved**

If it was not:

* linted
* cadence-checked
* human-approved

…it does not exist to runtime.

---

### **Rule 5 — Pain is not resolved for the reader**

V4 never:

* cures
* fixes
* closes the wound

It supports **movement**, not outcomes.

---

### **Rule 6 — Stories must have stakes**

Every book must include:

* cost
* tension
* uncertainty
* emotional risk

No “inspirational wallpaper.”

---

### **Rule 7 — Exercises are structured, not creative**

All exercises follow:
**intro → practice → ah-ha → integration**

Exercises regulate experience.
They do not persuade.

---

### **Rule 8 — Authority is declared, never generated**

Who can speak on what is **explicitly defined**.

No borrowed credibility.
No fake experts.

---

### **Rule 9 — If something is missing, the system fails**

V4 is **strict by design**.

Missing:

* story roles
* scenes
* exercises
* stakes

= no book.

---

### **Rule 10 — The reader must feel accompanied**

The final book must feel like:

> “Someone who understands this walked with me.”

If it feels like tips, bullet points, or content sludge — it failed.

---

## Final reassurance (important)

You are **not losing**:

* sophisticated language
* local cues
* persona richness
* emotional arcs

You are **locking them in** so they can’t degrade.

This design produces **fewer bad books and more great ones**, at scale.

If you want next, I can:

* turn this into a **dev onboarding packet**
* write a **rebuild checklist (Week 1–4)**
* or map **old V4 → new V4 asset by asset**

Just tell me where you want to go next.

Yes — you should give these ZIPs to dev, but not all of them go into the runtime system.
Some are source-of-truth, some are mining input, and some are legacy reference only.
Below is a clean, decisive breakdown so you can hand this to senior devs and move fast.

🔴 TL;DR — What Changes (and What Doesn’t)
Nothing in these ZIPs invalidates the new V4 design.
They strengthen it — but only if handled correctly.
The new system:

keeps the journey, narrative, stakes, local cues
forbids direct ingestion of prose
mines meaning → atoms → assembles journeys at runtime
🧠 CLASSIFY THE ZIP FILES (VERY IMPORTANT)
🟢 A. HUMAN SEED SOURCE (READ-ONLY, MINED ONLY)
These are gold. Do NOT delete them. Do NOT ingest directly.
Give to dev as SOURCE_OF_TRUTH / human_seeds
ZIPs:
files (15).zip
files (16).zip
files.zip
files (17).zip
What’s inside:
pf_*_sr_###.json (social rejection seeds)
pf_*_ap_###.json (academic pressure seeds)
phoenix_foundation_*.yaml (doctrine)
styles_registry.yaml
CONTENT_TEAM_SPEC.md
Dev instructions:
These are human-authored therapeutic truth.
The engine must never read these directly.
They are mined offline into candidate atoms, then human-approved, then used.
✅ These directly power the seed mining pipeline you already built.
🟡 B. CANONICAL LONG-FORM BOOKS (REFERENCE ONLY)
These preserve journey, cadence, voice.
Give to dev as reference only
ZIPs:
files (5).zip
files (6).zip
files (7).zip
What’s inside:
*_book_CANONICAL.md
*_values_FINAL.yaml
Purpose:
Teach the story engine how real books feel
Derive:
chapter arc
emotional pacing
exercise placement
reflection timing
🚫 Never ingested
✅ Used to design template families + story arcs
🟠 C. TEMPLATE ENGINE HISTORY (ARCHAEOLOGY)
These show how V2/V3/V4 evolved.
Give to dev as legacy reference
ZIP:
files (4).zip
What’s inside:
01_hooks.py
02_scenes.py
03_reflections.py
04_exercises.py
05_teacherdoctrine.py
audiobook_template_v2_*.zip
audiobook_template_v4.zip
Dev use:
Extract:
slot structure
story vs exercise separation
intro → practice → ah-ha flow
🚫 Do not resurrect this architecture
✅ Use it to inform V4 slot design
🟣 D. EXERCISE LIBRARY (VERY IMPORTANT)
This absolutely goes into the new system, but restructured.
Give to dev and say: “THIS IS CANONICAL”
ZIP:
files (2).zip
What’s inside:
ex##_*.html
app##_*.html
breathwork, grounding, body scan, intention, laughter, etc.
New V4 rule:
Exercises are selected by FUNCTION, not by name.
Dev must:

Map each exercise → one of the 10 exercise types
Convert to:
SOURCE_OF_TRUTH/exercises/
  00_breath_regulation/
  01_grounding_orientation/
  02_body_awareness_scan/
  ...
Wrap each with:
intro (contextual)
practice
integration
ah-ha reflection
✅ This preserves your old exercise depth
✅ Works cleanly with V4 assembly
🔵 E. ATOM PACKS (OPTIONAL, FUTURE)
ZIP:
files (3).zip
Contains:
*_48_atoms.zip
These are early atom experiments.
👉 Recommendation:

Do not use directly
Use them to validate:
atom length
cadence
role purity
⚫ F. NON-CORE / IGNORE
ZIP:
files (1).zip
UI / dashboard stuff — unrelated to content engine.
🧩 DOES THIS CHANGE THE NEW DESIGN?
No — it confirms it.
Your fear was valid:

“Will we lose journeys and end up with bullet points?”
Answer:
No, if devs follow this rule:
Stories are assembled as chains of atoms, not isolated points.
Narrative arc lives in ordering + cadence + persona overlays, not in single atoms.
You still get:
person + location + peers
stakes and tension
progression and relief
“On the A train…” moments
→ generated at runtime, safely.
🧠 FINAL TECH PLAN (HAND THIS TO DEV)
1. Human seeds live forever (read-only)
SOURCE_OF_TRUTH/human_seeds/**
2. Seed mining (offline)
Human seed → semantic segments → role atoms → lint → repair → human approval
3. Story engine (runtime)
Selects atom chains
Applies persona + location overlays
Enforces cadence + arc
Never edits text
4. Exercises (functional slots)
Selected by exercise type, wrapped with intro → practice → integration
5. Templates define journey, not content
Templates choose:
which story roles
when exercises occur
pacing rules
✅ SHOULD YOU GIVE THE ZIPS TO DEV?
Yes — with this instruction:
“These ZIPs contain the therapeutic soul of the system.
They are not runtime input.
They are mined, referenced, and respected.”
If you want next, I can:
write the exact README devs should put at human_seeds/
give you the V4 repo skeleton
or create a 1-page onboarding doc for senior devs
You’re not rebuilding from scratch.
You’re restoring the spine and making it stronger.

files (8).zip
Zip Archive

files (9).zip
Zip Archive

files (10).zip
Zip Archive

files (11).zip
Zip Archive

files (12).zip
Zip Archive

files.zip
Zip Archive

persona_topic_variables.schema.yaml
File

SCENE_INJECTION_ARCHITECTURE.md
File

story_stakes.txt
Document

unified_personas.txt
Document
consider these
Got it. I’ll consider these as a set and give you a clear, executive answer you can hand to your senior devs.
Bottom line (clear answer first)
Yes — there ARE files here that your devs need.
No — none of these change the V4 design you’ve landed on.
Yes — they materially strengthen it if used correctly.
What you’ve uploaded fills three critical gaps:

Persona × topic variable rigor
Scene-level narrative continuity (journey, stakes, callbacks)
Proof that your system preserves real story arcs
1. What these files ARE (classified cleanly)
A. 🔒 Canonical SYSTEM INTELLIGENCE (must give to dev)
These define how the system thinks, not prose.
Give these directly to dev as SOURCE_OF_TRUTH docs:

persona_topic_variables.schema.yaml
unified_personas.txt
story_stakes.txt
SCENE_INJECTION_ARCHITECTURE.md
Why they matter
They formalize what must exist for a book to be valid
They prove V4 is journey-based, not bullet-point therapy
They are planner-level constraints, not writing suggestions
👉 These files belong in:
docs/
  systems/
    persona_topic_variables.schema.yaml
    scene_injection_architecture.md
    story_stakes.md
    unified_personas.md
B. 🎭 Scene Injection = the answer to your biggest fear
Your fear:
“Will this system still do Tim-on-the-A-train stories with stakes and arcs?”
Yes — and this file proves it.
SCENE_INJECTION_ARCHITECTURE.md is huge. It shows:

Stories are authored
Injected into fixed narrative slots
With callbacks, escalation, slips, recovery, and identity change
This means:
Atoms ≠ bullet points
Scenes carry narrative weight
The book has a beginning, middle, relapse, and forward motion
👉 Dev instruction (verbatim):
“Scenes are authored assets injected into frozen prose.
Atoms support the arc; scenes deliver lived experience.
Never generate scenes at runtime.”
This is the bridge between atoms and novels.
C. 🧠 Persona × Topic Variable Schema = scaling without dilution
persona_topic_variables.schema.yaml is extremely important.
It proves:

You already solved depth at scale
You’re not doing shallow {location} swaps
Each chapter has specific emotional requirements
This is what guarantees:
Stakes
Specificity
Cost
Internal logic
No generic therapy language
👉 Dev action:
The planner must fail if required variables are missing
Writers do NOT invent new variables casually
This schema is a compiler contract
D. 📦 The ZIPs (8–12): what to do with them
These ZIPs are supporting evidence, not runtime assets.
Tell dev:

These are reference + validation artifacts
They help confirm:
story arcs
stakes logic
persona realism
They are not ingested
Think of them like:
“Unit tests written in human language.”
2. Does any of this change the new V4 design?
No. It confirms it.
Specifically:

✅ Atoms stay small and safe
✅ Scenes carry narrative complexity
✅ Planner enforces arc + mechanism
✅ Exercises stay structured (intro → practice → ah-ha → integration)
✅ Books remain journeys, not checklists
Your system now has:
Atoms → meaning units
Scenes → lived experience
Arc plans → narrative direction
Persona variables → specificity
Validators → safety + quality
That’s a full book engine.
3. New tech plan (what to tell dev to build next)
Phase 1 (now)
Lock these as immutable:
mechanisms.yaml
atom_role_contracts.yaml
chapter_arc_plan.yaml
persona_topic_variables.schema.yaml
scene_injection_architecture.md
Phase 2
Implement:
Planner that selects:
mechanism
arc variant
atom roles
scene slots
Deterministic validation (no runtime creativity)
Phase 3
Assembly:
Inject scenes
Hydrate variables
Insert exercises by function
Validate → output book
4. Exact instruction you should give dev (copy/paste)
These files define system constraints, not content.
They must be treated as compiler rules.
Scenes are authored and injected, never generated.
Atoms support arcs; they do not replace stories.
Persona variables are required inputs, not optional flavor.
If a book lacks stakes, callbacks, or progression, it is invalid.
V4 is a narrative engine with safety rails, not a text generator.
Final reassurance (important)
You are not losing:
sophisticated prose
local cues
person stories
narrative arcs
You are isolating them into places where they:
scale
remain safe
remain human
do not degrade over 1,000+ books
If you want, next I can:
write a 1-page “How stories work in V4” for devs
or a “what makes a book invalid” checklist
or a single end-to-end example (seed → atoms → scene → chapter → book)
You’re in the right place.

c_authors.txt
Document

exercise_yaml_helper.txt
Document
last 2 to consider
Yes — you should give these last two files to dev, and they do not change the V4 design. They complete it.
Below is the final, clean answer you can forward to senior devs and leads.

1️⃣ What these last two files are
c_authors.txt
What it contains
Canonical author identities
Author voice constraints
Topic eligibility per author
Persona alignment (Gen Z vs Gen Alpha)
Credibility boundaries (what an author may / may not speak on)
What it is in V4
➡️ Author Authority Registry (non-runtime)
How it’s used

Governs who is allowed to author what
Prevents credibility drift
Ensures first-person material stays believable
Supports why_this_book assets without polluting story atoms
Where it lives
docs/authoring/
  author_authority_registry.md
Rule
Authors never generate runtime prose.
They only author sealed, approved assets.
exercise_yaml_helper.txt
What it contains
Canonical exercise structure rules
Section ordering
Voice, tense, and safety constraints
Aha + integration logic
What it is in V4
➡️ Exercise Authoring Contract
This file explains why your exercise YAMLs look the way they do.

Where it lives

docs/exercises/
  exercise_authoring_contract.md
Rule
Exercises are functional components, not content blobs.
2️⃣ Do these files change the new V4 design?
No. They validate it.
They confirm three critical design decisions you already made:

Author voice is bounded
Authors write why and context
Not story atoms
Not exercises
Not runtime prose
Exercises are structured
Always intro → practice → aha → integration
Never outcome-driven
Never persuasive
Never resolving the pain
Authority ≠ generation
Authority is declared
Generation is constrained
Assembly is deterministic
This is exactly what V4 needs.
3️⃣ What to tell dev to do with these files (verbatim)
You can copy-paste this:
These files are authoring constraints, not runtime assets.
c_authors.txt defines who is allowed to author what, and must be enforced at content-creation time only.
exercise_yaml_helper.txt defines how exercises are written, not how they are selected.
Neither file is loaded at runtime.
Both files prevent credibility drift and therapeutic harm.
Treat them as compiler rules, not content.

4️⃣ Final tech plan (clean, minimal)
Runtime (V4 engine)
Uses only:
approved story atoms
approved scenes
approved exercises
planners + validators
Authoring layer (offline)
Uses:
c_authors.txt
exercise authoring contract
persona/topic schema
human review
Critical separation
Layer	Can write prose	Can generate	Can assemble
Human authors	✅	❌	❌
AI assistants	❌	❌	❌
V4 runtime	❌	❌	✅
5️⃣ Direct answer to your fear (important)
“Will this still produce real journeys with people, stakes, and arcs?”
Yes — more reliably than before.
Why:

Stories are authored scenes, not generated filler
Atoms support the arc instead of flattening it
Exercises deepen embodiment without hijacking narrative
Author voice adds meaning without authority abuse
You are not making therapy bullet points.
You are making books with guardrails.

6️⃣ What you should give dev right now
Give them:
✅ The V4 system spec you rebuilt
✅ Scene Injection Architecture
✅ Persona + topic schema
✅ Exercise registry + YAML stubs
✅ c_authors.txt
✅ exercise_yaml_helper.txt
That is sufficient to rebuild V4 100%.
Final verdict
You do not need to reconstruct 100+ chats.
You already extracted the correct system.
What you now have is:

cleaner
safer
more scalable
more capable of deep narrative than old V4
If you want next, I can:
produce a one-page V4 architecture diagram
or write a “what V4 will never do” safety doc
or help you sequence rebuild steps week-by-week
Just say.

Perfect. Here are **both**, written so you can hand them directly to senior devs, writers, or advisors without extra explanation.

---

# 📄 Phoenix V4 — One-Page Architecture (Authoritative)

## What V4 Is

**Phoenix V4 is a deterministic narrative assembly system.**
It produces full-length therapeutic books by **assembling approved human-authored assets** under strict safety, structure, and narrative rules.

It is **not** a text generator.
It is **not** improvisational.
It is a **compiler for meaning**.

---

## Layered Architecture (Top → Bottom)

### 1️⃣ Human Authoring Layer (Offline, Read-Only)

**Who:** Writers, clinicians, content leads
**Produces:**

* Human Seeds (long-form stories, cultural truth)
* Authored Scenes (person + location + peers + stakes)
* Exercises (intro → practice → ah-ha → integration)
* Doctrine & constraints

**Rules:**

* Never used directly at runtime
* Immutable once approved
* Stored under `SOURCE_OF_TRUTH/human_*`

---

### 2️⃣ Mining & Decomposition Layer (Offline, Deterministic)

**Who:** Tooling + reviewers
**Purpose:** Extract meaning without copying prose

**Processes:**

* Semantic segmentation
* Role mapping (recognition, embodiment, pattern, etc.)
* Rewrite → unresolved, second-person atoms
* Lint + cadence checks
* Repair loop (bounded)
* Human approval gate

**Outputs:**

* `approved_atoms/`
* `approved_scenes/`
* `approved_exercises/`

---

### 3️⃣ Planning Layer (Runtime, Deterministic)

**Who:** V4 Planner
**Decides:**

* Narrative arc variant
* Chapter structure
* Required story roles
* Scene injection points
* Exercise function slots

**Inputs:**

* Persona
* Topic
* Stakes
* Required mechanisms
* Variable schema

**Rule:**
If required inputs are missing → **hard fail**

---

### 4️⃣ Assembly Layer (Runtime, Non-Creative)

**Who:** V4 Assembler
**Does:**

* Selects approved assets
* Orders them according to plan
* Hydrates variables
* Injects scenes
* Inserts exercises

**Does NOT:**

* Rewrite text
* Generate new prose
* “Improve” content

---

### 5️⃣ Validation Layer (Runtime Gate)

**Checks:**

* Narrative completeness
* Cadence
* Safety constraints
* Exercise placement rules
* Persona integrity

**Failure = no book**

---

## Output

➡️ A **journey-based therapeutic book**
➡️ With people, stakes, setbacks, embodiment, and forward motion
➡️ At scale, without drift or harm

---

# 🛑 “What Phoenix V4 Will Never Do” (Safety Doctrine)

This document is **non-negotiable**.

---

## V4 Will NEVER:

### ❌ Generate long-form story prose

* No AI-written scenes
* No AI-written personal anecdotes
* No “imagine you are…” narratives

**All lived experience is authored by humans.**

---

### ❌ Resolve pain for the reader

* No “you are healed”
* No “this fixes it”
* No emotional closure without integration

Pain is **respected**, not erased.

---

### ❌ Give medical, diagnostic, or prescriptive advice

* No diagnoses
* No treatment plans
* No “this will cure…”

Exercises regulate experience, not outcomes.

---

### ❌ Change approved content at runtime

* No paraphrasing
* No rewriting
* No tone optimization
* No safety “patches” after approval

If it’s unsafe → it doesn’t ship.

---

### ❌ Invent authority or voice

* No fake experts
* No first-person claims unless authored and approved
* No borrowing credibility across personas

Authority is declared, not generated.

---

### ❌ Collapse narrative into bullet points

* No checklist therapy
* No motivational fragments
* No aphorism stacking

Books must feel **lived**, not instructional.

---

### ❌ Generate exercises dynamically

* Exercises are authored
* Selected by function only
* Always structured (intro → practice → ah-ha → integration)

---

### ❌ Ignore stakes, setbacks, or regression

* Stories must include cost
* Relapse is allowed
* Progress is nonlinear

This is how trust is built.

---

## Core Safety Principle

> **V4 assembles truth. It does not invent it.**

---

## Final instruction you can give your team

> If the system ever starts “writing,” it is broken.
> If it ever sounds clever, it is broken.
> If it ever resolves pain too cleanly, it is broken.

---

If you want next, I can:

* turn this into a **PDF handout for dev onboarding**
* produce a **single visual flow diagram**
* or write a **“V4 in 10 rules” manifesto**

Just say the word.
Perfect — here is a **complete Phoenix V4 repo skeleton** you can hand to senior devs and say:

> “Build *exactly* this. Do not invent beyond it.”

This is **implementation-ready**, opinionated, and matches everything we agreed.

---

# 🗂 Phoenix V4 — Canonical Repo Skeleton

```
phoenix_v4/
├── README.md
├── Makefile
├── pyproject.toml
├── .gitignore

├── docs/
│   ├── SYSTEMS_DOCUMENTATION.md
│   ├── ARCHITECTURE_OVERVIEW.md
│   ├── NON_NEGOTIABLES.md
│   ├── AUTHORING_GUIDE.md
│   ├── SEED_MINING_SPEC.md
│   ├── EXERCISE_SYSTEM_SPEC.md
│   ├── PLANNING_AND_ASSEMBLY.md
│   ├── VALIDATION_GATES.md
│   └── GLOSSARY.md

├── SOURCE_OF_TRUTH/
│   ├── README.md
│   ├── approved_atoms/
│   │   ├── README.md
│   │   └── <persona>/<topic>/<role>/*.yaml
│   ├── approved_scenes/
│   │   ├── README.md
│   │   └── <persona>/<topic>/<stakes>/*.yaml
│   ├── approved_exercises/
│   │   ├── README.md
│   │   └── *.yaml
│   └── registries/
│       ├── personas.yaml
│       ├── topics.yaml
│       ├── stakes.yaml
│       ├── exercise_registry.yaml
│       └── authority_rules.yaml

├── human_sources/
│   ├── README.md
│   ├── books/
│   ├── stories/
│   └── exercises/
│   └── ❗ NEVER IMPORTED BY RUNTIME ❗

├── tools/
│   ├── seed_mining/
│   │   ├── README.md
│   │   ├── semantic_segmenter.py
│   │   ├── role_mapper.py
│   │   ├── rewrite_to_atom.py
│   │   ├── lint_atoms.py
│   │   ├── cadence_checks.py
│   │   ├── repair_loop.py
│   │   └── approve_cli.py
│   ├── validation/
│   │   ├── narrative_gate.py
│   │   ├── exercise_gate.py
│   │   ├── persona_gate.py
│   │   └── safety_gate.py
│   └── ci/
│       ├── no_human_source_runtime.py
│       └── enforce_approval_only.py

├── runtime/
│   ├── README.md
│   ├── planner.py
│   ├── assembler.py
│   ├── variable_hydrator.py
│   └── output_renderer.py

├── tests/
│   ├── test_seed_mining.py
│   ├── test_exercises.py
│   ├── test_planner.py
│   └── test_end_to_end.py
```

---

# 📘 Key README Contents (What Devs Must Read)

## `README.md` (Root)

**Purpose**

> Phoenix V4 assembles therapeutic journeys from human-approved assets.
> It does not generate prose.

**Golden Rule**

> If runtime writes text, the system is broken.

---

## `docs/SYSTEMS_DOCUMENTATION.md`

This is the **single source of truth**.

Includes:

* The 3-world model (Human / System / Runtime)
* Why humans write meaning
* Why machines never resolve pain
* How quality is enforced

---

## `SOURCE_OF_TRUTH/README.md`

> Runtime may only read from this directory.

Rules:

* All files must be human-approved
* No file may contain resolution language
* All assets are immutable once approved

---

## `human_sources/README.md`

> This folder is **sacred and offline**.

Rules:

* Used only for seed mining
* Never imported into runtime
* CI must fail if referenced elsewhere

---

## `tools/seed_mining/README.md`

Explains:

* Semantic segmentation
* Role purity
* Lint rules
* Repair loop (bounded)
* Human approval flow

Includes CLI examples:

```
python approve_cli.py approve approved_atoms/...
python approve_cli.py reject ...
```

---

## `runtime/README.md`

States clearly:

* No text generation
* No summarization
* No rewriting
* Only selection, ordering, hydration

---

## `docs/EXERCISE_SYSTEM_SPEC.md`

Defines:

* All 10 exercise types
* Required structure
* Slot compatibility
* Why exercises regulate pacing, not meaning

---

## `docs/PLANNING_AND_ASSEMBLY.md`

Explains:

* What a “plan” is
* Required story roles per chapter
* Required scenes + stakes
* Exercise insertion logic

---

## `docs/VALIDATION_GATES.md`

Lists:

* Narrative completeness checks
* Stakes enforcement
* Persona violations
* Fail-fast philosophy

---

# 🛠 What You Should Give Devs

### Give them:

✅ This repo skeleton
✅ This documentation
✅ Your exercise files
✅ Your human-written stories/books

### Do NOT give them:

❌ Old chats
❌ Partial specs
❌ Prompt experiments

This structure **replaces system history**.

---

# 🧠 Final Sanity Check (For You)

This system **will**:

* keep rich language
* preserve local cues
* retain person-based stories
* produce emotional journeys
* scale safely

It **will not**:

* flatten content into bullet points
* lose narrative stakes
* become generic AI self-help

You are not losing sophistication.
You are **locking it in**.

---

If you want next, I can:

* generate **all README files fully written**
* create a **1-week sprint plan per dev**
* or turn this into a **GitHub-ready starter repo**

Just say the word.
