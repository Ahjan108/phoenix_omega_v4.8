# Teacher Mode Structural Spec

## Identity Design: Pre-Intro, Voice, and Teacher Presence

**Status:** Canonical (structural authority for Teacher Mode identity)  
**Subordinate to:** [TEACHER_MODE_V4_CANONICAL_SPEC.md](./TEACHER_MODE_V4_CANONICAL_SPEC.md)  
**Audience:** Content leads, writers, QA

This spec defines **how the teacher is elevated** and **how author voice shifts** in Teacher Mode — without prose scoring, tone AI, or runtime improvisation. Structure only.

---

## 1. Pre-Intro Chapter (Non-Arc)

A Teacher Mode book MUST include a short framing chapter **before** Arc Chapter 1. It is **not** part of the emotional arc.

### 1.1 Section name options

- "A Note on the Teachings"
- "Before We Begin"
- "How I Met This Work"
- "On Learning From [Teacher]"

### 1.2 Structural template (4 paragraphs)

**Paragraph 1 — Relationship clarity**

- State: "I was not a direct student of [Teacher]."
- State: "I encountered their work through books, talks, and publicly available teachings."
- State: "What follows is not an official interpretation — it is an application."

*Purpose:* Prevent false lineage; remove implied authority confusion; establish honesty.

**Paragraph 2 — Why this teacher matters for this topic**

- State how [Teacher]'s understanding of [core concept] reshaped the way you see [topic].

*Purpose:* Anchor topic to teacher lens; establish thematic authority.

**Paragraph 3 — Scope and boundary**

- "This book applies these teachings to [persona + topic context]."
- "It does not replace the teacher's original work."

*Purpose:* Clear boundary; no appropriation.

**Paragraph 4 — Invitation**

- "If something resonates here, I encourage you to go to the source."

*Purpose:* Elevate teacher; reduce ego centrality.

### 1.3 Structural rules

- **Length:** 900–1200 words max.
- **Must NOT include:** Biography section, mythologizing, personal struggle narrative, authority claims.
- **Placement:** Above the arc; not part of chapter_slot_sequence. Implemented as a dedicated front-matter section or "Chapter 0" in format/omega layer.
- This is a **framing device**, not an arc chapter.

---

## 2. Author Voice in Teacher Mode

In Teacher Mode the author is **interpreter + applicator**, not originator. Teacher = source of wisdom; author = bridge.

### 2.1 Voice positioning by role

| Slot / role   | Author position   |
|--------------|-------------------|
| Recognition  | Interpreter       |
| Mechanism    | Translator of teacher lens |
| Pattern      | Applicator to reader context |
| Exercise     | Adapter of teacher practice |
| Integration  | Bridge back to teacher frame |

Author is **never:** originator of doctrine, spiritual authority, emotional confessor, replacement for teacher.

### 2.2 Sentence framing — allowed

- "In [Teacher]'s work…"
- "What [Teacher] calls…"
- "A framework often emphasized by [Teacher]…"
- "Through the lens of [Teacher]…"

### 2.3 Sentence framing — not allowed

- "I discovered…"
- "My breakthrough was…"
- "What changed my life was…"
- "This method guarantees…"

### 2.4 Tone

Grounded. Respectful. Clear. Applied.  
**Not:** devotional, biographical, mythologizing, apologetic, or pretending to be a lineage holder.

### 2.5 Concept anchoring requirement

Each arc chapter MUST contain:

- ≥1 explicit teacher concept reference, OR  
- ≥1 teacher-derived STORY atom  

This ensures teacher presence without overuse. Enforced structurally (e.g. TPS) not by prose inspection.

### 2.6 Exercise attribution rules

| Type              | Attribution wording        |
|-------------------|----------------------------|
| Direct from teacher | "Drawn from…"            |
| Adapted           | "Inspired by…"             |
| Derived from pattern | "In the spirit of…"     |

**Never:** "This is exactly how [Teacher] taught it" unless verified and approved.

---

## 3. Teacher Presence Score (TPS)

**Purpose:** Ensure the teacher is meaningfully present in every chapter — **structural only**, no prose scoring.

### 3.1 Definition

For each chapter, TPS is computed from **metadata and slot counts only** (no NLP, no sentiment).

| Component              | Structural check                    | Weight |
|-------------------------|-------------------------------------|--------|
| Teacher STORY atoms     | Count of STORY slots in chapter     | 2      |
| Teacher EXERCISE atoms  | Count of EXERCISE slots in chapter  | 2      |
| Mechanism from teacher | 1 if chapter has STORY (mechanism_proof implied by arc/format) | 2 (optional; see note) |
| Teacher concept ref     | Flag in atom metadata (optional)    | 1      |

**Note:** When format does not expose mechanism_proof at slot level, TPS can use:  
**TPS = 2 × (STORY count in chapter) + 2 × (EXERCISE count in chapter)**  
Optional: +2 if chapter index matches a "mechanism" chapter in arc; +1 per atom with `teacher_concept_anchor: true` when that field exists.

### 3.2 Example

Chapter with 2 STORY slots and 1 EXERCISE slot:

- TPS = (2×2) + (1×2) = 6

### 3.3 Thresholds

- **Minimum TPS per chapter:** 4 (configurable).
- **Recommended:** 6+.
- **If TPS &lt; threshold:** Emit compile/report **warning** (not hard failure); flag in coverage report.

### 3.4 Teacher dominance mode (optional)

In BookSpec or teacher_mode_defaults:

```yaml
teacher_dominance: light | balanced | strong
```

- **light** → TPS threshold = 3  
- **balanced** → TPS threshold = 5  
- **strong** → TPS threshold = 7  

Allows brand differentiation.

### 3.5 Implementation

- **Report:** `phoenix_v4/qa/teacher_presence_report.py` — given compiled plan + teacher_mode, output TPS per chapter and overall.
- **No prose inspection.** Only slot_type counts and optional metadata flags.

---

## 4. Optional: Closing "Return to the Teacher" Section

After the arc, a short section (e.g. "Where to Go Deeper", "Returning to the Source") can:

- Encourage reading original works
- Point to talks or direct engagement
- Reinforce that the book is an **application layer**, not a replacement

Implemented as optional back-matter in format/omega layer.

---

## 5. What This Spec Does NOT Do

- No prose scoring  
- No vibe detection  
- No tone AI  
- No runtime content generation  
- No modification of Arc-First structure  

Only **structural** clarity and governance.
