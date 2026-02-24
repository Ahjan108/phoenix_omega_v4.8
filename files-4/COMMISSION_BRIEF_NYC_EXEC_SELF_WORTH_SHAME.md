# COMMISSION BRIEF — ATOM GAP ORDER
# Pool: nyc_executives / self_worth / shame
# Purpose: Gold Master Book_001 — V4 system validation
# Date: February 2026

---

## BEFORE YOU WRITE: RUN THE VALIDATOR FIRST

```
python scripts/validate_book_001_readiness.py \
  --persona nyc_executives \
  --topic self_worth \
  --engine shame \
  --chapters 8
```

Print the band distribution table from the output.
Commission only what the validator says is missing or underrepresented.
Do not write atoms the pool already has.

---

## LOCKED PARAMETERS

| Field | Value |
|-------|-------|
| Persona | nyc_executives |
| Topic | self_worth |
| Engine | shame |
| Locale | NYC |
| Target chapters | 8 |
| Target band arc | 1 → 2 → 3 → 4 → 5 → 4 → 3 → 2 |
| Runtime format | standard_book |
| Structural format | F006 (or confirm from format registry) |

These do not change mid-commission.

---

## WHAT YOU ARE DELIVERING

You are not writing a book.
You are stocking a pool.
The system assembles the book from your atoms.
Your job: produce emotionally precise, structurally clean, individually self-contained atoms.

---

## PART 1 — STORY ATOMS

### Target count: 20 minimum (5 per role)

Deliver to:
```
get_these/nyc_executives/self_worth/shame/CANONICAL.txt
```

### Role distribution

| Role | Count | What it does |
|------|-------|--------------|
| RECOGNITION | 5 | Character inside the collapse, wanting to disappear. No exit. Still shrinking. |
| MECHANISM_PROOF | 5 | Same collapse, different moments. Demonstrates the pattern is reliable. |
| TURNING_POINT | 5 | Something cracks the collapse. Not cure. Crack. |
| EMBODIMENT | 5 | Small protective action taken. No confidence. No triumph. |

### BAND distribution target

Produce atoms across the full range. No clustering at BAND 3.

| BAND | Count | Meaning |
|------|-------|---------|
| 1 | 2 | Quiet exposure. Almost nothing. The body still fires. |
| 2 | 4 | Subtle social downgrade. Implied not explicit. |
| 3 | 6 | Clear public correction. Visible to the room. |
| 4 | 5 | Noticeable displacement. Witnessed. Unresolvable. |
| 5 | 3 | Rupture. Irreversible. Permanent record or identity-level. |

Total: 20. Adjust per validator output — only commission bands that are underrepresented.

### NYC Executive exposure surfaces

Use these. Not generic "office."

Each atom gets ONE anchor. Do not stack.

| Surface | Band range |
|---------|-----------|
| Board presentation slide skipped by CEO mid-sentence | 4–5 |
| Google Doc comment correction visible to full team | 3 |
| Calendar invite removed while online indicator shows active | 4 |
| LinkedIn deal announcement — junior partner tagged, not them | 2–3 |
| Midtown client dinner — introduced by wrong title | 3–4 |
| Zoom grid — camera off when theirs is the only one on | 2 |
| Slack thread — their question left unanswered, next message answers it | 3 |
| Conference room glass — heads turn away mid-presentation | 4 |
| 6 train door closes on them mid-sentence during a walking meeting | 2 |
| Annual review language: "demonstrates potential" not "delivers results" | 5 |
| Team photo circulated — they are cropped or absent | 2–3 |
| Partner introduces their project without saying their name | 4 |
| Voicemail to client played back on speakerphone unexpectedly | 5 |

Rotate. Every atom needs a different surface.

### STORY atom rules (non-negotiable)

1. One irreversible social moment. Not a pattern. Not a summary. One moment.
2. Audience present — named person, named group, or implied (post, recording, document).
3. Body anchor present — face heat, chest drop, shoulders in, jaw closing, hands flat, stillness.
4. Ends unresolved — stillness, non-response, cursor blinking, hand not moving.
5. Third-person present tense. Always.
6. No rhetorical questions.
7. No: embarrassed, humiliated, ashamed, self-esteem, owned it, no one cares.
8. No anxiety bleed — no "what if I get fired," no future spirals, no job loss fear.
9. BAND assigned intentionally. Not default.

### STORY atom format

```
## RECOGNITION v04
---
path: nyc_executives/self_worth/shame
BAND: 3
---

[prose — 200–800 words]

```

Blank line between atoms. No chapter headings. No beat maps. No commentary.

---

## PART 2 — REFLECTION ATOMS

### Target count: 8–12

Deliver to same CANONICAL.txt or separate file — confirm with dev.

### What reflections do

- Name what happened in the body (mechanism, not metaphor)
- Explain why the body responded that way
- Clarify the difference between the event and its interpretation
- De-escalate the threat register without resolving the story

### Reflection temperature bands needed

| Temp | Count | Focus |
|------|-------|-------|
| cool | 2 | Exposure as geometry. Why visibility triggers the alarm. |
| warm | 3 | Accumulation. Why small moments compound. Why silence confirms. |
| hot | 2 | Irreversibility. Why the body can't let go when a record exists. |
| descent | 2 | Crack-insufficient. Why fractional relief doesn't satisfy. |

### Reflection rules

- Second-person direct voice. No "we."
- No rhetorical questions.
- No therapy clichés: "sit with your feelings," "practice self-compassion."
- No generic advice: "try to remember," "it's okay to feel this way."
- No empowerment hype.
- Sentence caps: teaching sentences ≤ 12 words.
- Paragraph break every 60–80 words.

### Reflection format

```
## REFLECTION_cool_v01
---
path: nyc_executives/self_worth/shame
temp: cool
---

[prose — 150–400 words]

```

---

## PART 3 — EXERCISE ATOMS

### Target count: 4–6 unique exercises

### Rules

- Somatic only. No journaling. No affirmations.
- Targets body zones where shame compresses: face, jaw, throat, chest, shoulders.
- Under 2 minutes each.
- Shame-specific framing — not generic breathwork rebranded.
- Max 3 uses per book (system enforces). Write them so each could stand alone at any chapter position.

### Exercises needed (do not duplicate existing)

| Exercise | Body target | Duration | When to use |
|----------|-------------|----------|-------------|
| Jaw Release | Face and throat | 75 sec | After hot exposure — recorded, broadcast, witnessed |
| Weight Drop | Shoulders | 90 sec | After correction or public downgrade |
| [NEEDED] Chest Expansion | Chest and sternum | 90 sec | After chest-drop collapse at warm band |
| [NEEDED] Eye-Line Reset | Eyes and upper face | 60 sec | After being watched or assessed |
| [NEEDED] Ground Contact | Feet, legs, base of spine | 120 sec | After identity-level rupture — cool-down |

Write the three marked NEEDED. Do not rewrite Jaw Release or Weight Drop unless improving them.

### Exercise format

```
## EXERCISE_chest_expansion_v01
---
path: nyc_executives/self_worth/shame
body_target: chest and sternum
duration_seconds: 90
---

{EXERCISE: [Name] — [descriptor]. Level 1, [X] seconds. [One sentence on why this exercise targets this specific shame response.]}

[Step-by-step somatic instructions]

```

---

## PART 4 — INTEGRATION ATOMS

### Target count: 8–12

### Integration modes needed

| Mode | Count | Function |
|------|-------|----------|
| BODY-LANDED | 2 | Grounds listener in present body after story |
| COST-VISIBLE | 2 | Names what the moment cost without resolving it |
| QUESTION-OPEN | 2 | Leaves identity tension unresolved, forward-facing |
| FMT | 4 | Forward Momentum Trigger — open loop, next room |
| STILL-HERE | 1 | Final chapter only. One per book. Do not produce more than one. |
| SOMEONE-ELSE | 1 | Reframes — the other person in the moment was also afraid |

### Integration rules

- Do not summarize the chapter story.
- Do not repeat the reflection mechanism.
- Do not resolve the exposure event.
- Must hold dual reality: moment happened AND body is here now.
- FMT carry line: one sentence, forward-facing, unresolved. "That room hasn't opened yet." "You don't know what you'll remember afterward." Not: "You'll be okay." Not: "That's enough."
- STILL-HERE: present tense, body anchor, no prediction, no lesson. End on a stone.

### Integration format

```
## INTEGRATION_fmt_v01
---
path: nyc_executives/self_worth/shame
mode: FMT
---

[prose — 80–200 words]

[Final carry line — 1 sentence maximum]

```

---

## DELIVERY CHECKLIST

Before submitting atoms to get_these/:

- [ ] Every STORY has explicit BAND (not defaulting to 3)
- [ ] Every STORY ends on stillness or non-response
- [ ] No STORY contains a rhetorical question
- [ ] No STORY contains banned terms
- [ ] No STORY contains anxiety-bleed language
- [ ] Every STORY has a body anchor
- [ ] Every STORY has an audience (real or implied)
- [ ] BAND distribution covers 1–5 (no gap bands)
- [ ] No two STORY atoms use the same exposure surface
- [ ] Exercises target distinct body zones
- [ ] STILL-HERE integration: exactly one produced

If 2 or more boxes fail, do not submit. Fix and recheck.

---

## WHAT HAPPENS AFTER DELIVERY

1. Dev runs readiness validator on ingested pool.
2. If pass: pipeline compiles 8-chapter plan.
3. Markdown render produced.
4. Editorial reads in one sitting.
5. Flinch audit: minimum 5 involuntary body responses for standard book.
6. If flinch audit passes: TTS render.
7. Listen end-to-end.
8. QA document filed.

You will not see the assembled book before step 4. The system assembles, not you.

---

## ONE-LINE REMINDER

Write emotionally precise atoms.
The system builds the book.
Your job ends at delivery.
