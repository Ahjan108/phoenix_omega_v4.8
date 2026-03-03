# WRITER PRODUCTION ASSIGNMENT
# Burnout × gen_z_professional — Inventory Batch Brief
# Target: 60–80 confirmed STORY atoms
# Current inventory: 22 atoms (Wave 1 + Wave 2)
# Remaining to produce: ~40 atoms minimum
# Last updated: 2026-02-20

---

## YOUR SCOPE

You produce:
- STORY atoms
- EXERCISE atoms (later phase)
- Author assets
- Micro-stake research notes

You do NOT touch:
- Arc logic
- Slot selection
- Plan compiler
- Teacher Mode
- CI gates
- Emotional band rule definitions
- Any file in specs/ or config/

If a question touches those areas, escalate to content lead. Do not interpret.

---

## CURRENT INVENTORY STATUS

| Domain              | Atoms produced | Target | Gap |
|---------------------|---------------|--------|-----|
| Workplace visible   | 10            | 15     | 5   |
| Financial           | 3             | 10     | 7   |
| Body signals        | 3             | 10     | 7   |
| Social life bleed   | 3             | 10     | 7   |
| Identity / future   | 2             | 10     | 8   |
| Family expectation  | 1             | 5      | 4   |
| **Total**           | **22**        | **60** | **38** |

---

## BATCH ASSIGNMENTS

Complete batches in order. Do not mix domains within a batch submission.

---

### BATCH 3 — Financial Domain
**Target: 10 atoms**
**Bands required: at least one each of 1, 2, 3, 4**

Micro-stake sources (use research note: gen_z_professional_x_burnout.yaml):
- Rent increase absorbed without negotiation
- Student loan auto-payment date
- Savings buffer erosion (month over month, no crisis, just smaller)
- Compensation review language shift
- Healthcare benefits tied to job status
- Promotion freeze announcement (no individual conversation)
- Bonus structure change communicated by memo
- Side project abandoned due to bandwidth (lost income potential)
- Emergency fund too small to cover a realistic emergency
- Financial comparison to peer (not dramatic — a passing calculation)

Specificity targets for this batch:
- At least 3 atoms must reference specific dollar ranges or payment structures
  (e.g. "the $312 that comes out on the 14th", "a buffer that was $4,200 in October")
- At least 2 atoms must name a specific location anchor
  (subway card reload, the ATM on the corner of her block, the co-working day pass)

---

### BATCH 4 — Body Domain
**Target: 10 atoms**
**Bands required: at least one each of 1, 2, 3, 4**

Micro-stake sources:
- Shoulder height unnoticed for weeks
- 3pm headache (same headache, different Tuesday)
- Jaw clenched during video calls — discovered when the call ends
- Waking at 5:30am already calculating the day
- Food intake that is technically adequate and entirely joyless
- Sitting posture that drifts and is corrected and drifts again
- Weekend fatigue that does not lift by Sunday afternoon
- Eye strain from screen hours that exceed what anyone would admit to
- Hands that don't move toward the keyboard even when the mind is willing
- The specific tiredness of performing attention when attention is gone

Specificity targets for this batch:
- At least 2 atoms must name the office or home environment physically
  (the chair that needs adjusting, the monitor angle, the kitchen table as permanent desk)
- Body sensations must be observed from outside (third-person present), not labeled emotionally
  (e.g. "her shoulders are at a height they should not be" — not "she felt tense")

---

### BATCH 5 — Social Life Bleed Domain
**Target: 10 atoms**
**Bands required: at least one each of 2, 3, 4**

Micro-stake sources:
- Friday night cancellation (text drafted twice, sent once, guilt by Saturday morning)
- Group chat read but not answered (days, not hours)
- Dating app opened and closed without sending anything
- Friend's birthday acknowledged late (not forgotten — delayed by energy calculation)
- Relationship where both people are tired and neither says so
- The social plans that exist on a calendar and feel like obligations
- The friend who asks "are you okay" and the answer that is technically accurate
- The party that shows up in Instagram stories that she knew about and did not attend
- The person she used to call on the commute who she now texts when she remembers
- Leaving a gathering earlier than expected because the math stopped working

Specificity targets for this batch:
- At least 3 atoms must include a specific platform or communication mode
  (Instagram story, not social media; voice note, not message; the group chat named "girls 🌙")
- At least 2 atoms must include a specific location
  (the bar in Echo Park, the rooftop in Bushwick, the friend's apartment in Astoria)

---

### BATCH 6 — Identity / Future Domain
**Target: 10 atoms**
**Bands required: at least one each of 1, 2, 3, 4, 5**

Micro-stake sources:
- The version of herself at 27 that she planned for at 22
- The job she took because it was supposed to lead somewhere
- The side project still in a notes app, last edited four months ago
- Former self comparison (used to be curious about this; now it feels like maintenance)
- Title she has vs. meaning she doesn't
- The accomplishment that was real and landed nowhere emotionally
- LinkedIn profile she hasn't updated because updating it would require deciding something
- The thing she is good at that she no longer enjoys
- The future she is building toward that she hasn't examined recently
- The moment she realizes she is staying somewhere not because she wants to but because leaving requires energy she doesn't have

Specificity targets for this batch:
- The Band 5 atom must be identity dissociation — she is completing the motion of her life
  without being located inside it. Not a breakdown. Not tears. The motion continuing.
- At least 2 atoms must reference a specific age, year, or numeric milestone
  (27, six months from now, the promotion she expected by Q3)

---

## QUALITY REQUIREMENTS FOR ALL BATCHES

**Non-negotiables:**
- Third-person present. No exceptions.
- 60–150 words per atom.
- ≥ 1 micro-stake per atom (specific, not generic).
- ≥ 1 environmental cue per atom.
- Emotional band declared in metadata.
- persona_specificity_score declared (honest self-assessment).
- status: provisional_template on all submissions.

**Specificity floor:**
- All atoms in these batches: target 0.75+
- Hyper-specific location/salary/platform atoms: target 0.85+

**What 0.85+ looks like:**
- The atom names a subway line, a salary number, a specific app, a specific neighborhood, or an industry-specific artifact.
- A reader inside this persona's world would recognize the atom as describing their life, not a version of their life.

**Repetition check before submission:**
- Review your full batch against existing inventory (Waves 1 and 2).
- No micro-stake should appear twice in identical form.
- Same micro-stake category allowed maximum 2× across entire inventory.

---

## METADATA REQUIRED ON EVERY ATOM

```yaml
atom_id:                    # gzp_burn_story_NNN (continue from 023)
persona_id: gen_z_professional
topic_id: burnout
role: STORY
band:                       # 1–5
stake_present: true
peer_present:               # true / false
persona_specificity_score:  # 0.00–1.00
micro_stake_domain:         # financial / body / social / identity / family / workplace
status: provisional_template
```

---

## SUBMISSION FORMAT

One YAML file per batch.
Filename convention:
```
gen_z_professional_x_burnout_story_atoms_batch{N}.yaml
```

Submit batches in order. Do not combine.

---

## WHAT HAPPENS AFTER SUBMISSION

Content lead reviews each batch against:
1. Persona specificity score (self-assessed vs. reviewer assessment)
2. Repetition entropy across full inventory
3. Micro-stake domain balance
4. Band distribution

Atoms passing review are promoted:
```yaml
status: confirmed
```

Atoms returned for revision receive a specific note. No silent rejection.

---

## DO NOT START YET

Do not begin until content lead confirms this brief is received.
First submission: Batch 3 (Financial Domain).
