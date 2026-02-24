# Writer Comms: What To Write So the System Runs 100%

**One-page brief for content writers.** If these are done, pipeline and CI pass. If any are missing, builds or gates fail.

---

## 1. Atoms (Core Content)

- **Path:** `atoms/<persona_id>/<topic_id>/<engine_id>/` (and `SOURCE_OF_TRUTH/...` where used). Delivered to `get_these/` for ingestion; then moved to canonical paths.
- **Six types:** HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION. Write to the rules in **Writer Spec §§4–8** (sentence caps, no questions, body anchors, TTS-safe).
- **STORY:** Every STORY atom **must** have **`emotional_intensity_band`** (1–5) in metadata. Without it the atom fails lint and assembly. Use the band that matches the moment (1 = mild discomfort … 5 = crisis/rupture).
- **Tags when applicable:** `misfire_tax: true`, `silence_beat: true`, `never_know: true` on STORY; `integration_mode: still_here | cost_visible | body_landed | question_open | someone_else` on INTEGRATION. Required counts per format are in emotional_governance_rules; missing tags can cause CI or assembly to fail.
- **Persona/topic/engine:** Only write for **persona × topic × engine** combinations that exist in **config/topic_engine_bindings.yaml**. No prohibited terms from **config/topic_skins.yaml**.
- **SCENE:** Only use location placeholders from the allowed list (§18): e.g. `{transit_line}`, `{street_name}`, `{weather_detail}`. No other variables in body.

---

## 2. Compression Atoms (When the Format Has COMPRESSION)

- **When:** Formats that include slot_08_compression (e.g. F006) need one COMPRESSION atom per chapter. If you are writing for such a format, you must supply compression atoms.
- **Path:** `SOURCE_OF_TRUTH/compression_atoms/approved/<persona_id>/<topic_id>/` (or candidate then approved).
- **Rules:** 40–120 words. 2–6 sentences. **One insight only:** no steps, no lists, no “first, second, third,” no “here are,” no more than one colon, no more than two pivot markers (“but also,” “and also”). No lecturing. TTS-safe (no em dashes; short sentences). Persona cues minimal (1–2 max). See **Writer Spec §25**.

---

## 3. Arcs (If You Author or Edit Arcs)

- **Path:** `config/source_of_truth/master_arcs/`. Filename pattern: `persona__topic__engine__format.yaml` (e.g. `nyc_executives__self_worth__shame__F006.yaml`).
- **Required:** `emotional_role_sequence` — **one role per chapter**, length exactly **chapter_count**. Allowed roles: `recognition`, `destabilization`, `reframe`, `stabilization`, `integration`.
- **Rules:** First chapter = `recognition` (unless arc has `opening_override: true`). Last chapter = `integration`. No more than 2 consecutive chapters with the same role. For chapter_count ≥ 6 use at least 4 of the 5 roles; for 4–5 chapters use at least 3. See **ARC_AUTHORING_PLAYBOOK.md** and arc_loader validation.
- **Other required fields:** arc_id, persona, topic, engine, format, chapter_count, emotional_curve (length = chapter_count), emotional_temperature_curve, chapter_intent, reflection_strategy_sequence, cost_chapter_index, resolution_type, motif.

---

## 4. Author-Bound Books (Pen-Name Authors)

- **Registry:** Author must exist in **config/author_registry.yaml** with `persona_ids`, `topic_ids`, and **`positioning_profile`** (must exist in **config/authoring/author_positioning_profiles.yaml**).
- **Author assets (when required):** bio, why_this_book, authority_position, audiobook_pre_intro at `assets/authors/<author_id>/` (or path in registry). Word ranges: bio 120–180; why_this_book 150–250; authority_position 100–150; audiobook_pre_intro 500–900. No runtime-generated content; human-written only.
- **Positioning:** Write to the profile’s **allowed_language** and **forbidden_language**. CI (check_author_positioning) fails if e.g. first_person_reflection exceeds the band for research_guide, or command_language exceeds threshold for somatic_companion. See **Writer Spec §24**.

---

## 5. What Makes the System Pass 100%

| Area | What writers must do |
|------|----------------------|
| **Atoms** | All six types per brief; STORY has emotional_intensity_band (1–5); tags (misfire_tax, silence_beat, never_know, integration_mode) where required; persona/topic/engine in config; no prohibited terms. |
| **Compression** | If format has COMPRESSION slot: supply 40–120 word, one-insight-only atoms; no steps/lists; TTS-safe. |
| **Arcs** | emotional_role_sequence length = chapter_count; first = recognition, last = integration; max 2 consecutive same role; role diversity per playbook. |
| **Authors** | Every pen-name author in author_registry with positioning_profile; author assets present and within word ranges when author-bound books are built. |
| **Voice / CI** | No "?" outside dialogue; no tentative language; sentence caps (teaching ≤12, emotional ≤15, instructions ≤10, carry ≤8); cognitive/body ratio ≤5; action → reaction; TTS rhythm and governance rules per Writer Spec §16. |

---

## 6. Single Source of Truth

- **How to write:** [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) — voice, atom types, TTS rules, gates, §23–§25.
- **Arcs:** [specs/ARC_AUTHORING_PLAYBOOK.md](../specs/ARC_AUTHORING_PLAYBOOK.md).
- **Config that constrains you:** config/topic_engine_bindings.yaml (engines per topic), config/topic_skins.yaml (prohibited terms), config/format_selection/ (formats and slots).

If you deliver the above, the pipeline and production gates can run to 100%. If something is missing, the failure message (pipeline exit, CI gate, or systems test report) will point to the rule or file.
