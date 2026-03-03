# exercises_v4 — V4 Somatic & Therapeutic Exercise Registry

**Authority:** [exercise_yaml_helper.txt](../../exercise_yaml_helper.txt), [REBUILD_README.txt](../../REBUILD_README.txt) §7.

Exercises are selected by **function (type)**, not by topic or prose. Runtime may only load from `approved/`.

## Layout

```
exercises_v4/
├── registry.yaml                    # Canonical registry: 11 types, slot policies, aha_noticing rules
├── persona_overlays.yaml            # Optional lexical overlays per persona (deterministic)
├── aha_noticing_phoenix_standard.yaml # Canonical 27 aha_noticing blocks; hydrate from here
├── integration_phoenix_standard.yaml   # Canonical integration blocks (same keys as AHA); optional
├── README.md                        # This file
├── candidate/                       # Work-in-progress; not used at runtime
│   └── _stubs/                      # Minimal stubs for all 11 exercise types
└── approved/                        # Human-approved exercises only; runtime source
```

## 11 exercise types

| Type | Cadence role | Description |
|------|--------------|-------------|
| `00_breath_regulation` | grounding | Breath-based regulation |
| `01_grounding_orientation` | grounding | Sensory orientation (e.g. 5 senses) |
| `02_body_awareness_scan` | grounding | Body scan / interoceptive awareness |
| `03_somatic_release_discharge` | release | Movement / discharge |
| `04_nervous_system_downregulation` | grounding | Parasympathetic settling |
| `05_nervous_system_upregulation` | activation | Activation / mobilization |
| `06_vagal_stimulation_sound` | grounding | Sound / vibration (e.g. humming) |
| `07_self_contact_touch` | grounding | Touch / self-contact (e.g. hand on heart) |
| `08_emotional_processing_completion` | release | Emotion / completion |
| `09_embodied_intention_direction` | integration | Intention / orientation |
| `10_integration_return_to_baseline` | integration | Integration / return to baseline |

## Required structure (every exercise)

1. **intro** — Why now
2. **guided_practice** — What to do
3. **aha_noticing** — Consolidation moment (see below)
4. **integration** — Return to life

No advice, no promises, no outcome claims. Second person, present tense.

## aha_noticing — Phoenix standard

The **aha_noticing** section is the nervous-system interpretation layer. It is not generic sensation commentary.

It must:

- **Anchor sensation** — Reference a physical sensation or rhythm change.
- **Name a pattern** — Connect that sensation to a common stress pattern (without diagnosing).
- **Reinforce non-dramatic capacity** — Regulation, not transformation.

Constraints:

- 60–120 words preferred (40 minimum).
- Second person, present tense.
- No outcome claims, no identity transformation, no emotional climax.
- Start with a clear callout (e.g. "Now, pause and consider…"; never just "Notice").
- Structure: sensation → pattern → capacity.
- Observational, not persuasive.

**Enforcement (registry):** Callout is enforced via `section_requirements.aha_noticing.must_start_with_one_of` in `registry.yaml` (e.g. "Now, I want you", "Now, pause", "Now, let's"). Validation level: `warn` (soft). Lint must also require "notice" or "might notice" and at least one body-reference word.

**Source of truth:** [aha_noticing_phoenix_standard.yaml](./aha_noticing_phoenix_standard.yaml) is the canonical library of 27 aha_noticing blocks. Exercise YAMLs should be **hydrated from it at compile** (e.g. by reference), not manually copied. Writers must not edit the library and individual exercise files independently, or drift occurs.

**Copy-ready blocks:** For one-off use, copy from the library into `content.aha_noticing: |` in exercise YAMLs. Prefer `aha_noticing_ref: <key>` + hydration where the assembler supports it.

## Persona overlays (aha_noticing)

Same nervous-system logic for all personas; only **lexical surface** varies so listeners feel seen without breaking determinism.

- **Canonical AHA** = persona-neutral (aha_noticing_phoenix_standard.yaml).
- **Overlay** = controlled phrase substitution per persona (see [persona_overlays.yaml](./persona_overlays.yaml)).
- Structure, word count, and callout never change. Assembler applies substitutions after resolving the exercise.

**Variation axes:** vocabulary density, environmental reference, stress framing, cognitive abstraction. **Do not:** rewrite full blocks per persona, change structure, or add identity/motivational framing.

**Overlay guardrails (registry / CI):** Enforce these so overlays do not introduce semantic distortion or tone drift:

```yaml
overlay_constraints:
  - substitutions must preserve grammatical role
  - no substitution may introduce future-oriented language
  - no substitution may increase emotional intensity
  - overlays may not modify callout sentence
```

- Substitutions must preserve grammatical role (no semantic distortion; e.g. "stress pattern may be chemical" → "performance pressure may be chemical" is invalid).
- No substitution may introduce future-oriented language or increase emotional intensity.
- **Overlays may not modify the callout sentence.** The opening (e.g. "Now, I want you to…") must remain universal and identical; it is never persona-substituted. Callout is validated post-overlay via `must_start_with_one_of`; if overlay corrupts it, validation fails.

**Stronger long-term strategy:** Prefer **tag-based substitution** in canonical copy (e.g. `{STRESS_PATTERN}`) and inject per persona in overlay YAML. That avoids accidental partial replacement, grammar corruption, and overlapping phrase issues. Assembler can support token-based injection first, with phrase substitution as legacy fallback.

## integration — Phoenix standard

**Purpose:** Close the practice with grounded carry-forward behaviour *without promises*.

Render order unchanged: `intro → guided_practice → aha_noticing → integration`.

**Constraints:**

- Second person, present tense.
- No outcome claims, no "you will", no "this will fix", no "healed".
- No identity transformation, no emotional climax, no new teaching (integration is carry-forward + boundary, not a lesson).

**Word counts:** min 40, preferred 60–120, max 150.

**Required opener (callout):** One of: "Now, before you move on,", "Now, as you return,", "Now, for the next few minutes,", "Now, as you go back to your day,", "Now, keep it simple,".

**Content pattern:**

- **Carry-forward cue:** One micro-action that fits the exercise (e.g. one longer exhale, soften jaw once, feel feet at red lights).
- **Boundary clause:** e.g. "Nothing has to change." / "No need to force it." / "If it's not there today, that's fine."
- **Re-entry:** How to rejoin the environment (screen, hallway, meeting) without "reset fantasy".

**Enforcement:** See `section_requirements.integration` in `registry.yaml`. Do **not** extend persona overlays to integration until this standard is fully adopted and integration blocks are canonical.

## Workflow

1. Author or adapt exercises in `candidate/` (use `_stubs/` as templates).
2. Lint and cadence checks per registry `global_rules` and `auto_promotion.eligibility_rules`.
3. Human review; set `approval.status: approved`.
4. Copy to `approved/` (layout per persona/topic or per registry).
5. Assembler/resolver reads `registry.yaml`, selects from `approved/` only.

## Legacy mapping

See exercise_yaml_helper.txt “DELIVERABLE 2” for mapping legacy exercise names (e.g. box breathing → `00_breath_regulation`, 5 senses → `01_grounding_orientation`, full body scan → `02_body_awareness_scan`) to these types.
