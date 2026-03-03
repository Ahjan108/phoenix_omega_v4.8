# Phoenix Protocol — Email Sequences for Freebie Landing Pages

**Capture first:** Use **Formspree** (no MailerLite needed). One form ID in `config/freebies/exercises_landing.json` → all 27 pages work. See [FORMSPREE_SETUP.md](./FORMSPREE_SETUP.md).

**Automations later:** Use these sequences in **MailerLite** (or any ESP) when you connect Formspree → MailerLite via Zapier, or when you switch the generator to MailerLite. Trigger: **Subscriber joins group** or **Subscriber tagged** with the exercise tag (e.g. `cyclic_sighing`, `box_breathing`).

- **Master sequence:** [5-email-welcome-sequence.md](./5-email-welcome-sequence.md) — copy into MailerLite; replace `{{exercise_name}}`, `{{exercise_benefit}}`, `{{tool_link}}` per automation.
- **Persona variants:** [persona-variants.md](./persona-variants.md) — swap in for Executive / Gen Z / Healthcare.
- **Per-exercise copy:** [exercise-one-liners.md](./exercise-one-liners.md) — subject lines and opening lines for all 27 exercises; use when building one automation per exercise.

## Quick setup

1. MailerLite → Automations → Create workflow.
2. Trigger: **Subscriber added to group** (e.g. "Phoenix — Cyclic Sighing") or **Subscriber tagged** `cyclic_sighing`.
3. Add 5 emails; delay: 0, 24h, 72h, 72h, 168h (see sequence doc).
4. Paste body from 5-email-welcome-sequence.md; replace placeholders.
5. For persona-specific tone, use blocks from persona-variants.md in Email 1 and 3.

## Tags (match exercises_landing.json ml_tag)

Use these exactly for segmentation: `cyclic_sighing`, `sigh_of_relief`, `bee_breath`, `triangle_breathing`, `box_breathing`, `478_breathing`, `five_senses_grounding`, `loving_kindness_breathing`, `hrv_coherence`, `coherence_5bpm`, `equal_breathing`, `rectangle_breathing`, `body_scan`, `extended_exhale`, `resonance_6bpm`, `three_part_breath`, `breath_walking`, `lions_breath`, `liberation_laughter`, `ujjayi_ocean`, `kapalabhati`, `tonglen`, `intention_breathing`, `alternate_nostril`, `buteyko`, `phoenix_breath`, `moon_breath`.
