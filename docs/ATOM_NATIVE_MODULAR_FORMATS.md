# Atom-Native Modular Formats (No Long-Form Cohesion Required)

Purpose: define high-value output formats that fit the current atom corpus as it exists today, without depending on multi-chapter narrative flow.

## 1) What The Current Atoms Support Well

Based on current files under `atoms/*/<topic>/`:

- Strong: `HOOK`, `SCENE`, `EXERCISE`, mechanism story families (`shame`, `spiral`, `false_alarm`, `comparison`, `watcher`, `overwhelm`, `grief`), `INTEGRATION` (when hydrated).
- Usable but repetitive: `REFLECTION` (good for teaching blocks, requires dedupe/rotation).
- Inconsistent in some topics: `COMPRESSION` (some files are metadata-heavy or partially empty). Treat as optional until fully hydrated.

Implication: prioritize formats built from short independent units (practice, checklist, card, FAQ, protocol), not chapter-journey books.

## 2) Shared Delivery Rules (All Formats)

Before output:

1. Strip metadata lines (`family:`, `voice_mode:`, `mechanism_emphasis:`, `mode:`, `carry_line:`, etc.).
2. Strip markdown artifacts (`---`, section markers).
3. Resolve placeholders (`{weather_detail}`, `{street_name}`, `{transit_line}`) with global fallbacks.
4. Fail build if braces or metadata labels remain.
5. Enforce stem dedupe in same asset (avoid repeated openers like "What I've noticed...").

## 3) Canonical Building Blocks

Use these block IDs in all format specs:

- `B1_HOOK` = one `HOOK` atom (25-55 words)
- `B2_SCENE` = one `SCENE` atom (60-120 words)
- `B3_MECH` = one mechanism-story atom from `shame|spiral|false_alarm|comparison|watcher|overwhelm|grief`
- `B4_REFLECT` = one `REFLECTION` atom excerpt (trim to target length)
- `B5_EXERCISE` = one `EXERCISE` atom (80-180 words)
- `B6_CLOSE` = one `INTEGRATION` atom
- `B7_COMPRESS` = one `COMPRESSION` atom (optional only)

## 4) Format Structures (Atom-First)

### A. 5-Minute Practice (1 skill, 1 cue, 1 rep)

Best for audio practice and app sessions.

- Structure: `B1_HOOK (short)` -> `B5_EXERCISE` -> `B6_CLOSE (short)`
- Word target: 350-650
- Story required: No
- Reflection required: No
- Notes: this should be your default scalable unit.

### B. Pocket Guide (10-20 entries, non-linear)

Best for EPUB, app cards, PDF quick reference.

- Entry structure (each): `B1_HOOK` -> `B5_EXERCISE` -> `B6_CLOSE`
- Entries per guide: 10-20
- Word target per entry: 180-420
- Story required: No
- Notes: no cross-entry sequencing required; random-access friendly.

### C. "10 Things To Do For X" (ranked checklist)

Best for conversion content and practical listener utility.

- Item structure: `#rank line` -> `B2_SCENE (1-2 lines)` -> `B5_EXERCISE (single actionable step)` -> `B6_CLOSE (1 line)`
- Items: exactly 10
- Word target per item: 120-260
- Story required: No
- Notes: keep each item independent; do not force emotional arc.

### D. Symptom-to-Action Atlas ("If you feel X, do Y in 60s")

Best for crisis utility and repeat consumption.

- Card structure: `If symptom...` -> `Why it happens (B4_REFLECT short or B3_MECH short)` -> `60-second action (B5_EXERCISE trimmed)` -> `check line (B6_CLOSE short)`
- Cards: 20-60 per atlas
- Word target per card: 90-220
- Story required: No
- Notes: highest utility for current atom design.

### E. Daily Text + Audio Companion (one idea/day)

Best for subscriptions and retention loops.

- Daily unit: `B1_HOOK` -> `B5_EXERCISE` -> `B6_CLOSE`
- Optional add-on: `B2_SCENE` once every 3-4 days
- Word target: 140-320 text, 45-120 sec audio
- Story required: No
- Notes: "day cards," not chapters.

### F. Crisis Cards (before/during/after scripts)

Best for acute state support.

- Card set per trigger:
  - `BEFORE`: `B1_HOOK` + prevention step from `B5_EXERCISE`
  - `DURING`: stripped-down `B5_EXERCISE` (fast imperative)
  - `AFTER`: `B6_CLOSE` + one restore step from `B5_EXERCISE`
- Word target per card: 90-200
- Story required: No
- Notes: use `overwhelm`, `false_alarm`, `spiral` as primary mechanism families.

### G. Weekly Challenge Pack (7 episodes, one behavior loop)

Best for habit programs.

- Day 1: `B1_HOOK + B2_SCENE + B5_EXERCISE + B6_CLOSE`
- Days 2-6: `B1_HOOK + B5_EXERCISE + B6_CLOSE`
- Day 7: `B1_HOOK + B4_REFLECT short + B6_CLOSE`
- Word target: 180-480/day
- Story required: Optional (Day 1 only)
- Notes: this gives progression without needing narrative chapter continuity.

### H. FAQ Audiobooks ("Why do I ___?")

Best for searchable audio and YouTube/podcast exports.

- Answer unit: `Question title` -> `B4_REFLECT short` or `B3_MECH` -> `B5_EXERCISE` -> `B6_CLOSE`
- Duration per answer: 2-4 min
- Word target: 320-700
- Story required: Optional
- Notes: one FAQ = one independent mechanism.

### I. Myth vs Mechanism Series

Best for reframing and social clips.

- Episode structure: `Myth line` -> `B3_MECH` (proof paragraph) -> `B4_REFLECT short` (actual mechanism) -> `B5_EXERCISE` -> `B6_CLOSE`
- Duration: 3-6 min
- Word target: 450-900
- Story required: Yes (one mechanism-story block)
- Notes: this is the best place to use your story-family atoms.

### J. Protocol Library (searchable drills by trigger)

Best for productized "use when" catalog.

- Protocol structure: `Trigger` -> `State check` -> `B5_EXERCISE` -> `Failure fallback step` -> `B6_CLOSE`
- Word target: 120-280
- Story required: No
- Notes: index by trigger tags (`meeting panic`, `sleep spike`, `social replay`, `money dread`).

## 5) No-Story Profiles (when you want pure utility)

Use these profiles where narrative adds little value:

- `UTILITY_MIN`: `B1_HOOK -> B5_EXERCISE -> B6_CLOSE`
- `UTILITY_MICRO`: `B5_EXERCISE -> B6_CLOSE`
- `UTILITY_CARD`: `symptom line -> B5_EXERCISE (trim) -> check line`

Applicable formats: A, B, C, D, E, F, J.

## 6) Story-Optional Profiles (when story helps but is not required)

- `PROOF_LITE`: `B1_HOOK -> B3_MECH -> B5_EXERCISE -> B6_CLOSE`
- `FAQ_PROOF`: `question -> B3_MECH -> B4_REFLECT short -> B5_EXERCISE -> B6_CLOSE`

Applicable formats: G, H, I.

## 7) Production Priority (Ship Order)

If you want immediate value with existing atoms:

1. Symptom-to-Action Atlas
2. 5-Minute Practice
3. Crisis Cards
4. Pocket Guide
5. Protocol Library
6. Weekly Challenge Packs
7. FAQ Audiobooks
8. Myth vs Mechanism
9. "10 Things To Do For X"
10. Daily Text + Audio Companion

Rationale: this order minimizes dependency on weak/variable long-form cohesion and maximizes immediate utility per atom.

