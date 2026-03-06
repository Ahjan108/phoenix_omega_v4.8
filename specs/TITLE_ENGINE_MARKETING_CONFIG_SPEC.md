# Title Engine Marketing Config Spec

**Status:** Canonical (authority for config layer and title engine sourcing). **Implementation: complete** (2026-03-04).  
**Subordinate to:** [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](./PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) for invisible_script HOOK subtype and narrative depth.  
**Audience:** Dev, content/marketing, CI.

---

## Implementation status (writer complete)

The following are **implemented and live**:

- **Config:** `config/marketing/consumer_language_by_topic.yaml` (14 topics, full schema); `config/marketing/invisible_scripts_by_persona_topic.yaml` (140 entries, 10×14, 2 scripts each).
- **Loader:** `MarketingConfigLoader` in `phoenix_title_engine_v4.py` loads both YAMLs on init; config-first, fallback to hardcoded blocks when absent.
- **Compliance:** `check_compliance()` uses config-driven banned clinical terms (plus existing GLOBAL_FLAGGED / COMPLIANCE_FILTER).
- **Invisible script:** `generate_invisible_script()` uses persona×topic lookup with seeded-deterministic selection; fallback to TOPIC_VOCABULARY when config absent.
- **CI:** `scripts/ci/check_marketing_config.py` validates both files (referential integrity, required fields, minimum content, cross-file consistency, brand×clinical cross-check). `.github/workflows/marketing-config-gate.yml` runs on PRs touching `config/marketing/**`; strict mode on main.

**Current parallel:** `COMPLIANCE_FILTER` and `consumer_language_by_topic.yaml` both supply banned/flagged terms; the engine checks config first then fallback. Deprecation path: remove COMPLIANCE_FILTER once config coverage is validated complete (see §9).

---

## 0. Purpose

Unify the title engine’s compliance and invisible-script behavior behind a **config-driven layer** so that:

1. **Consumer language** (banned terms, bridge language, search clusters, platform risk terms) and **invisible scripts** (persona×topic) live in YAML, not in hardcoded Python.
2. **One config replaces two hardcoded structures:** `consumer_language_by_topic.yaml` replaces both `COMPLIANCE_FILTER` and the topic-level vocabulary (search/bridge/flagged) that was in `TOPIC_VOCABULARY`; `invisible_scripts_by_persona_topic.yaml` replaces `TOPIC_VOCABULARY.invisible_scripts`.
3. **Persona×topic invisible scripts** are the primary source for `generate_invisible_script()`; the previous behavior (modular arithmetic on `persona_id` length over topic-level scripts) is deprecated and used only as fallback when config is missing.
4. **Loader** is config-first with a **clear fallback**: if a config file is absent or invalid, the engine falls back to the existing hardcoded blocks and SHOULD log or surface that fallback so it can be removed once config is fully adopted.

---

## 1. Config Files

| File | Purpose | Replaces (in code) |
|------|---------|--------------------|
| `config/marketing/consumer_language_by_topic.yaml` | Per-topic consumer phrases, banned clinical terms, bridge language, search clusters, persona subtitle patterns, platform risk terms, culture-specific phrases. | `COMPLIANCE_FILTER` (flagged/banned per topic); topic-level search/bridge/forbidden data previously in `TOPIC_VOCABULARY`. |
| `config/marketing/invisible_scripts_by_persona_topic.yaml` | 10 personas × 14 topics = 140 entries; each entry has 2 persona-specific invisible scripts (first-person, raw, specific). | `TOPIC_VOCABULARY[topic_id]["invisible_scripts"]` (topic-only scripts); removes reliance on modular arithmetic on `persona_id` for “persona-specific” pick. |

**Canonical topic IDs** (must match `config/catalog_planning/canonical_topics.yaml`):  
anxiety, burnout, overthinking, imposter_syndrome, sleep_anxiety, financial_stress, grief, boundaries, somatic_healing, depression, compassion_fatigue, courage, self_worth, social_anxiety.

**Canonical persona IDs** (must match `config/catalog_planning/canonical_personas.yaml`):  
millennial_women_professionals, tech_finance_burnout, entrepreneurs, working_parents, gen_x_sandwich, corporate_managers, gen_z_professionals, healthcare_rns, gen_alpha_students, first_responders.

---

## 2. Consumer Language Schema (consumer_language_by_topic.yaml)

Each topic entry SHALL include:

- **topic_id** — Exactly one of the canonical topic IDs above.
- **consumer_phrases** — 8–10 phrases (how real people search/talk; raw, colloquial).
- **banned_clinical_terms** — 5–8 terms that MUST NOT appear in consumer-facing titles (platform/compliance).
- **culture_specific_phrases** — 3–5 current cultural phrases (internet-native, workplace-native, generational).
- **bridge_language** — 5–7 phrases (consumer-friendly, therapeutically accurate “translation” layer).
- **search_clusters** — 3–5 actual search-query patterns (e.g. Google/Spotify).
- **persona_subtitle_patterns** — 2–3 subtitle patterns that signal persona without naming.
- **platform_risk_terms** — 3–5 monitor-tier terms (borderline/platform-flagged; not full bans).

Authority and scaffold: `marketing_deep_research/` scaffold 03. File header MUST state version and last updated; DO NOT EDIT canonical topic IDs in place (add new topics via controlled process).

---

## 3. Invisible Scripts Schema (invisible_scripts_by_persona_topic.yaml)

Each entry SHALL include:

- **persona_id** — Exactly one of the canonical persona IDs above.
- **topic_id** — Exactly one of the canonical topic IDs above.
- **scripts** — List of 2 persona×topic invisible scripts.

**Script rules:**

- First person (“I…”).
- Raw, specific; NOT generic affirmation.
- Names the hidden belief, fear, or rule the person lives by but rarely says aloud.
- Persona-specific (this life context, this role).
- 1–2 sentences max; conversational; no jargon.
- Should feel like a 2am thought, not a therapy intake form.

Authority and scaffold: `marketing_deep_research/` scaffold 04. This file is the **highest-value content** in the marketing config layer; quality bar is high.

---

## 4. Loader Behavior (MarketingConfigLoader)

**Implementation:** `phoenix_title_engine_v4.py` — `MarketingConfigLoader`.

- **Config directory:** `config/marketing/` (or override via constructor).
- **Load order:** On init, load `consumer_language_by_topic.yaml` then `invisible_scripts_by_persona_topic.yaml`. If a file is missing or invalid, do not raise; leave in-memory structures empty for that file and rely on fallback in callers.
- **Fallback:** Callers (compliance check, `generate_invisible_script()`, title generation) MUST use config-first, then fall back to hardcoded `COMPLIANCE_FILTER` and `TOPIC_VOCABULARY` when config data is absent. Fallback MUST be documented in code and, where feasible, logged so that removal of hardcoded blocks can be tracked.
- **Deprecation:** The hardcoded `COMPLIANCE_FILTER` and `TOPIC_VOCABULARY` blocks in the title engine are **deprecated**. New behavior and CI SHALL assume config is present; fallback exists only for backward compatibility and migration.

---

## 5. generate_invisible_script() Contract

**Signature:** `generate_invisible_script(brand_id: str, topic_id: str, persona_id: str) -> str`

**Behavior:**

1. **Primary:** Call `MarketingConfigLoader.get_invisible_scripts(persona_id, topic_id)`. If the returned list is non-empty, choose one script deterministically (e.g. seeded random from `brand_id:topic_id:persona_id`) and return it.
2. **Fallback 1:** If config returns empty, use `TOPIC_VOCABULARY.get(topic_id, {}).get("invisible_scripts", [])`. If non-empty, select by deterministic seed (e.g. persona_id/topic_id modular arithmetic) and return. This preserves legacy behavior when config is not yet populated.
3. **Fallback 2:** If still empty, return a generic phrase, e.g. `f"the hidden cost of {topic_id.replace('_', ' ')}"`.

**Quality note:** Persona×topic scripts fix the main quality gap: the previous “persona-specific” selection was effectively random (modular arithmetic on `persona_id` length), not meaningfully persona-specific. Config-driven persona×topic scripts are the intended source.

---

## 6. Compliance Check (Banned / Platform Risk Terms)

Title engine compliance logic SHALL:

1. **Primary:** Use `MarketingConfigLoader.get_banned_clinical_terms(topic_id)` and `MarketingConfigLoader.get_platform_risk_terms(topic_id)` for checks and flags.
2. **Fallback:** If config is not loaded or topic missing, use `COMPLIANCE_FILTER.get(topic_id, {}).get("flagged", [])` (and any analogous “banned” list) for the same checks.

Unified compliance gate: a single code path SHOULD use config when available and fall back to `COMPLIANCE_FILTER` so that one day the hardcoded dict can be removed.

---

## 7. CI and Validation

- **Marketing config gate:** `scripts/ci/check_marketing_config.py` validates both YAML files: referential integrity (topics/personas match canonical), required fields, minimum content, cross-file consistency (e.g. every topic in invisible_scripts exists in consumer_language). Exit 1 on ERROR; `--strict` promotes WARNs to ERRORs.
- **Workflow:** `.github/workflows/marketing-config-gate.yml` runs the gate on PRs touching `config/marketing/**`; uses `--strict` on main branch pushes when applicable.

---

## 8. Downstream Consumers

| Consumer | Use |
|----------|-----|
| Title engine v4 | Compliance filter, search/bridge language, `generate_invisible_script()` |
| HOOK atom seeds | Invisible-script ideas from `invisible_scripts_by_persona_topic.yaml` for authoring |
| Deep research ingestion | Outputs from marketing deep research prompts land in these two files (see docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md) |

---

## 9. Still to Do

- **Deprecate COMPLIANCE_FILTER:** Today the title engine has two parallel structures for compliance — hardcoded `COMPLIANCE_FILTER` and `consumer_language_by_topic.yaml` (banned_clinical_terms, platform_risk_terms). The loader is already config-first; the next step is to validate that config coverage is complete for all topics, then remove the hardcoded dict so the YAML is the single source of truth.
- **Deprecate TOPIC_VOCABULARY.invisible_scripts:** Once all call paths use config persona×topic scripts (and fallback is no longer needed), remove the hardcoded invisible_scripts from TOPIC_VOCABULARY.
- Optional: experiment-loop logging (which source was used: config vs fallback) for monitoring and deprecation proof.
