# First 10 Books Evaluation Protocol

You do **not** evaluate one book. You evaluate **10**.  
Because systems scale patterns.

---

## Step 1 — Compile 10 Books

- **One brand only.**
- No wave filtering.
- No optimizer.

```bash
python3 scripts/generate_full_catalog.py --max-books 10 --brand <brand_id> --skip-wave-selection
```

Example: `--brand stillness_press`

---

## Step 2 — Blind Listening

Listen to **20 minutes** of each book:

- Beginning  
- Midpoint  
- Final chapter  

**Don't read the script.** Listen like a user.

---

## Step 3 — Rate on 5 Axes (1–5 scale)

| Axis            | What it measures                          |
|-----------------|--------------------------------------------|
| Emotional Pull  | Did I feel something?                     |
| Clarity         | Was it easy to follow?                    |
| Memorability    | Any standout lines?                      |
| Practicality    | Would someone apply it?                  |
| Identity Shift  | Does it reframe the listener's self-image? |

Score each book.

---

## Step 4 — Pattern Analysis

- **If 7/10 books score below 3 on Emotional Pull:**  
  Arc/story layer is weak.

- **If Practicality is low:**  
  Exercises need work.

- **If Memorability is low:**  
  Voice and insight density need work.

**Do not modify governance yet.** Fix upstream content quality (see [High-Impact Story Atom Upgrade Rubric](HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md), [Narrative Tension Validator](NARRATIVE_TENSION_VALIDATOR.md), [Insight Density Analyzer](INSIGHT_DENSITY_ANALYZER.md)).

---

## Critical Truth

The system guarantees:

- No duplication  
- Emotional distribution  
- Brand separation  
- Release safety  
- Entropy diversity  

It does **not** guarantee:

- Insight density  
- Story authenticity  
- Emotional resonance  
- Transformation  

Those must be measured manually at first.

---

*See also: [Creative Quality Validation Checklist](CREATIVE_QUALITY_VALIDATION_CHECKLIST.md), [Simplified Emotional Impact Scoring](SIMPLIFIED_EMOTIONAL_IMPACT_SCORING.md).*
