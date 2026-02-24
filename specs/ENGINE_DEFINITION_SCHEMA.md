# ENGINE DEFINITION SCHEMA

# (Prevents Future Resolution Conflicts)

---

## 0. WHY THIS EXISTS

Past conflict:

General spec required resolution.
Engine required open loops.
System contradicted itself.

This schema eliminates that permanently.

---

# 1. ENGINE FILE STRUCTURE

Each engine must define:

```yaml
engine_id:
description:
core_pattern:
allowed_resolution_types:
identity_shift_allowed: true|false
open_loop_allowed: true|false
peak_intensity_limit:
tone_constraints:
prohibited_outcomes:
motif_preferences:
```

No prose essays.
Clear constraints only.

---

# 2. REQUIRED FIELDS EXPLAINED

### core_pattern

4-line description of psychological movement.

Example (Shame):

* Social exposure
* Freeze or shrink
* Self-surveillance
* Social narrowing

---

### allowed_resolution_types

Explicit list.

Example (Shame):

* open_loop
* internal_shift_only

Not allowed:

* identity_shift

---

### identity_shift_allowed

Boolean. Redundant but explicit. Prevents accidental arc mismatch.

---

### peak_intensity_limit

Maximum BAND allowed.

Example: Burnout may cap at 4. Shame may allow 5.

Prevents melodrama creep.

---

### tone_constraints

Short list.

Example (Shame):

* No triumphant speeches
* No public victory moments
* No empowerment monologues

---

### prohibited_outcomes

Explicit disallowed endings.

Example:

* "You are enough exactly as you are."
* Public confrontation success.
* Apology from antagonist.

---

### motif_preferences

Optional emotional anchors.

Example: Glass, mirrors, silence, echo.

---

# 3. ENGINE–ARC COMPATIBILITY CHECK

Compiler verifies:

* Arc resolution_type ∈ engine.allowed_resolution_types
* Arc peak ≤ engine.peak_intensity_limit
* Ending Integration does not violate identity_shift_allowed
* No cost chapter outside emotional peak window

No prose inspection required.

Pure structural alignment.

---

# 4. ENGINE SCALE STRATEGY

You do not need 50 engines.

You likely need:

* Shame
* Anxiety
* Burnout
* Grief
* Control
* Loneliness
* Self-worth
* People-pleasing
* Trauma-lite
* Ambition-conflict

Engines must remain clean.

If engine grows messy: Split it.

---

# 5. ENGINE FAILURE MODES

Watch for:

* Engine bleed (shame turning into anxiety mid-book)
* Resolution inflation
* Identity rewrite in non-identity engine
* Peak escalation arms race

Engine purity > emotional intensity.

---

# FINAL SYSTEM STABILITY MAP

Arc = emotional pacing authority
Engine = behavioral guardrail
Atoms = human emotional content
Compiler = structural verifier
Validators = structural only

Nothing else.
