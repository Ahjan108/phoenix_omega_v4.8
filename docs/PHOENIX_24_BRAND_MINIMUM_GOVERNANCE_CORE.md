# Phoenix 24-Brand Minimum Governance Core (12 Controls)

**Purpose:** Non-negotiable survival layer for 24-brand scale. Twelve controls in three phases; implementation order and acceptance criteria so dev can move without architecture drift.  
**Authority:** [PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md](PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md).  
**Last updated:** 2026-02-25

---

## Frozen control IDs

**GOV-01** through **GOV-12**. IDs are stable for audit and tooling; never renumber.

---

## Ownership roles (defined once)

| Role | Scope |
|------|--------|
| **Ops** | Release pipeline, gates, artifacts, dashboard, audit log |
| **Content QA** | Sampling policy, human review triggers, description/title uniqueness |
| **Platform** | KPI baselines, channel metrics, refund escalation, throttling |

Every **Owner** cell in this doc uses only these three roles.

---

## No duplicate gates rule

Before adding a new gate or script, **reference existing checks** and extend or reuse where possible. Existing entry points include:

- `scripts/ci/run_prepublish_gates.py` — structural entropy, platform similarity, wave density, similarity index update
- `scripts/ci/check_platform_similarity.py` — CTSS fingerprint, block/review thresholds
- `scripts/ci/check_structural_entropy.py` — min word counts, family dominance, emotional role sequence
- `scripts/ci/check_wave_density.py` — arc_id, band_seq, slot_sig, exercise placement, emotional_role_sig
- `scripts/ci/update_similarity_index.py` — append to `artifacts/catalog_similarity/index.jsonl`
- `scripts/release/prepare_wave_for_export.py` — release path; runs gates before export

Do not create a net-new gate that duplicates or overlaps these without documenting the extension.

---

## Rollout order by PR batches

- **Phase 1 only first** — One or more PRs for GOV-01 through GOV-06. No Phase 2 or 3 changes in the same batch.
- **Phase 2 next** — GOV-07 through GOV-10.
- **Phase 3 last** — GOV-11 through GOV-12.

No mixing phases in one rollout batch.

---

## Break-glass policy

- **Who can override:** Only the documented role (e.g. platform/ops lead) may override a failing governance gate for a specific release or wave.
- **Audit log requirement:** Every override must be **audit-logged** with: who, when, which control (GOV-xx), and reason. Log location and format to be defined (e.g. `artifacts/governance/override_log.jsonl` or ticketed with link).

---

## Glossary

| Term | Definition |
|------|------------|
| **wave** | A batch of books selected for release together (e.g. output of wave orchestrator or wave selection); subject to wave-level diversity and density gates. |
| **catalog similarity** | Measure of structural or metadata similarity across compiled plans in the catalog; used to block or flag near-duplicates (e.g. CTSS fingerprint, similarity index). |
| **brand collision** | Two or more brands shipping same or near-same persona + topic (and optionally similar structure) within a defined time window; leads to self-competition and algorithm clustering. |
| **refund escalation** | Automated response when refund rate or related KPI crosses threshold: e.g. increase QA sampling, freeze template/persona, or reduce release velocity. |

---

## Dashboard requirement

One **dashboard view** must show all 12 controls with:

- **Status** per control (Implemented / Partial / Planned)
- **Latest run timestamp** per control (when the gate or check last ran)

**Where it lives:** To be implemented (e.g. `artifacts/ops/governance_dashboard.json` or CI summary artifact). **Owner:** Ops. Maintained on each gate run or nightly.

---

## Control map table

| Control ID | Gate/Script | Config | Artifact | Owner | Verification |
|------------|-------------|--------|----------|-------|---------------|
| GOV-01 | run_pipeline.py (writes plan); extend for full fingerprint | config/catalog_planning/atoms_model.yaml | Compiled plan JSON (plan_hash, atoms_model); future: meta.provenance | Ops | Compiled plan contains plan_hash + atoms_model; after extend: full provenance block present |
| GOV-02 | check_wave_density.py; update_similarity_index.py; extend for structural signature cap | config/gates or wave density thresholds | artifacts/catalog_similarity/index.jsonl; wave density report | Ops | Wave fails if structural clone % above threshold; index contains slot_sig/band_sig |
| GOV-03 | New or extend check_* for metadata similarity | TBD | TBD | Content QA | Report or gate: description opening uniqueness, keyword overlap below cap |
| GOV-04 | New: cross-brand topic collision check | TBD (e.g. cooling period days) | TBD | Platform | Gate fails if two brands ship same persona+topic within window without structural diff |
| GOV-05 | New: KPI sentinel + refund escalation | TBD (baselines, thresholds) | TBD | Platform | Refund spike triggers documented action (e.g. QA escalation, freeze); baseline matrix exists |
| GOV-06 | brand_teacher_matrix.yaml; brand_archetype_registry; extend with lockfile | config/catalog_planning/brand_teacher_matrix.yaml; config/catalog_planning/brand_archetype_registry.yaml | N/A | Platform | Brand matrix and archetype registry validated; no plan outside allowed persona/topic envelope |
| GOV-07 | New: adaptive throttle (reduce wave size / freeze on metrics) | TBD | TBD | Platform | When metric crosses threshold, release count or combo is reduced; configurable |
| GOV-08 | Extend wave density or new template saturation check | TBD | TBD | Ops | Wave fails if same template_id exceeds X% of wave or brand quarter cap |
| GOV-09 | New: keyword heatmap monitor | TBD | artifacts/ops/keyword_heatmap.json (or similar) | Content QA | Artifact shows keyword frequency/saturation; alert when threshold exceeded |
| GOV-10 | update_similarity_index.py; build_structural_drift_dashboard.py | artifacts/catalog_similarity/index.jsonl | artifacts/drift/summary.json; dashboard | Ops | Similarity index updated on plan write; dashboard shows similarity trend or risk score |
| GOV-11 | New: QA sampling policy (config-driven rates) | TBD (e.g. qa_sampling_policy.yaml) | TBD | Content QA | Sampling % applied by risk category (new template, new teacher, stable, refund alert) |
| GOV-12 | Extend check_author_positioning or new compliance gate | config (e.g. prohibited phrases, disclaimer template) | TBD | Ops | Prohibited phrases blocked; disclaimer present in listing/audio where required |

---

## Phase 1 — Survival (GOV-01..GOV-06)

### GOV-01 — Provenance fingerprint

| Field | Value |
|-------|--------|
| **Purpose** | Zero ambiguity on content origin for every compiled book. |
| **Implementation** | Embed in compiled plan (or meta): atoms_model, atoms_root_hash, teacher_version, persona_version, format_version, structural_signature, plan_hash. run_pipeline already writes plan_hash and atoms_model; extend with remaining fields. |
| **Layer** | 1 (Content Integrity) |
| **Status** | Partial |
| **Build type** | Extend |
| **Gate/Script** | scripts/run_pipeline.py; phoenix_v4/planning/assembly_compiler.py |
| **Config** | config/catalog_planning/atoms_model.yaml |
| **Artifact** | Compiled plan JSON (e.g. out/plan written by run_pipeline) |
| **Owner** | Ops |
| **Verification** | Compiled plan contains plan_hash and atoms_model; after full implementation, contains full provenance block (all listed fields). |
| **Acceptance criteria** | **Pass:** Every exported plan includes plan_hash + atoms_model; (future) meta.provenance with all fingerprint fields. **Fail:** Plan missing plan_hash or atoms_model. **Evidence:** Sample compiled plan JSON; CI assertion on run_pipeline output. |

---

### GOV-02 — Structural signature guard

| Field | Value |
|-------|--------|
| **Purpose** | Block excessive identical arc/band/slot/exercise structure across catalog and within waves. |
| **Implementation** | Hash per book (arc, band sequence, slot order, exercise families); store in similarity index; enforce wave-level and catalog-level caps (e.g. wave density FAIL if % identical structural signature above threshold). |
| **Layer** | 1 |
| **Status** | Partial |
| **Build type** | Extend |
| **Gate/Script** | scripts/ci/check_wave_density.py; scripts/ci/update_similarity_index.py |
| **Config** | Wave density thresholds (e.g. in script or config/gates) |
| **Artifact** | artifacts/catalog_similarity/index.jsonl; wave density report |
| **Owner** | Ops |
| **Verification** | Wave fails when structural clone % exceeds threshold; index contains slot_sig, band_sig (or equivalent). |
| **Acceptance criteria** | **Pass:** Wave density gate FAILs when ≥ defined % same slot_sig/band_seq; index updated on plan write. **Fail:** Wave with > threshold identical structure passes. **Evidence:** Gate exit code and report; index row sample. |

---

### GOV-03 — Metadata similarity scoring

| Field | Value |
|-------|--------|
| **Purpose** | Avoid algorithm clustering via metadata uniqueness and keyword overlap caps. |
| **Implementation** | Uniqueness checks (e.g. opening sentence of description, title pattern); keyword overlap cap across catalog; cosine or similar similarity across listings. |
| **Layer** | 2 (Brand & Identity) |
| **Status** | Planned |
| **Build type** | New build |
| **Gate/Script** | TBD (new or extend existing CI) |
| **Config** | TBD (overlap cap %, uniqueness rules) |
| **Artifact** | TBD (report or gate output) |
| **Owner** | Content QA |
| **Verification** | Report or gate shows description opening uniqueness and keyword overlap below cap; FAIL when exceeded. |
| **Acceptance criteria** | **Pass:** No two listings share same first sentence; keyword overlap below configured cap. **Fail:** Duplicate opening or overlap above cap. **Evidence:** Gate output or artifact. |

---

### GOV-04 — Cross-brand topic collision gate

| Field | Value |
|-------|--------|
| **Purpose** | Prevent two brands from shipping same persona + topic within a defined window unless structurally differentiated. |
| **Implementation** | Check release/wave data: if two brands have same persona+topic in window, require structural differentiation (e.g. template_id, structural signature) or block. |
| **Layer** | 2 |
| **Status** | Planned |
| **Build type** | New build |
| **Gate/Script** | TBD (e.g. in release path or check_release_wave) |
| **Config** | Cooling period (days); structural diff rules |
| **Artifact** | TBD |
| **Owner** | Platform |
| **Verification** | Gate fails when two brands ship same persona+topic within window without structural diff. |
| **Acceptance criteria** | **Pass:** No two brands release same persona+topic within window without structural differentiation. **Fail:** Collision detected and not differentiated. **Evidence:** Gate report. |

---

### GOV-05 — KPI sentinel + refund escalation

| Field | Value |
|-------|--------|
| **Purpose** | Auto-trigger corrective action when metrics (refund rate, completion, etc.) cross thresholds. |
| **Implementation** | Baseline matrix per template × persona; compare actual to baseline; on refund spike (or other threshold), escalate QA sampling or freeze template/persona. |
| **Layer** | 3 (Release & Performance) |
| **Status** | Planned |
| **Build type** | New build |
| **Gate/Script** | TBD |
| **Config** | Baselines, thresholds, escalation actions |
| **Artifact** | TBD (alert, log, dashboard) |
| **Owner** | Platform |
| **Verification** | Refund spike triggers documented action; baseline matrix exists and is used. |
| **Acceptance criteria** | **Pass:** When refund rate exceeds threshold, escalation protocol runs (e.g. QA %, freeze); baselines defined. **Fail:** Spike with no action or no baselines. **Evidence:** Runbook + artifact. |

---

### GOV-06 — Brand positioning lockfile

| Field | Value |
|-------|--------|
| **Purpose** | No brand drift without explicit override; each brand locked to allowed persona/topic/tone/runtime/narrator envelope. |
| **Implementation** | Enforce at plan or export: brand_teacher_matrix + brand_archetype_registry define allowed envelope; reject or flag plans outside envelope. |
| **Layer** | 2 |
| **Status** | Partial |
| **Build type** | Extend |
| **Gate/Script** | phoenix_v4/qa/validate_brand_archetype_registry.py; config load in generate_full_catalog / release path |
| **Config** | config/catalog_planning/brand_teacher_matrix.yaml; config/catalog_planning/brand_archetype_registry.yaml |
| **Artifact** | N/A (validation at plan/export time) |
| **Owner** | Platform |
| **Verification** | Brand matrix and archetype registry validated; no plan outside allowed persona/topic envelope is released. |
| **Acceptance criteria** | **Pass:** Every plan’s brand has defined envelope; validation runs before export. **Fail:** Plan for brand outside envelope or missing validation. **Evidence:** CI/prepublish gate. |

---

## Phase 2 — Stability (GOV-07..GOV-10)

### GOV-07 — Adaptive release throttle

| Field | Value |
|-------|--------|
| **Purpose** | Protect account trust by reducing output when quality metrics decline. |
| **Implementation** | When refund/rating/completion crosses threshold, reduce wave size or freeze specific template/persona combination; configurable. |
| **Layer** | 3 |
| **Status** | Planned |
| **Build type** | New build |
| **Gate/Script** | TBD |
| **Config** | TBD (thresholds, throttle rules) |
| **Artifact** | TBD |
| **Owner** | Platform |
| **Verification** | When metric crosses threshold, release count or combo is reduced; configurable. |
| **Acceptance criteria** | **Pass:** Throttle activates on threshold; wave size or combo reduced. **Fail:** Metric breach with no throttle. **Evidence:** Config + run log. |

---

### GOV-08 — Template saturation cap

| Field | Value |
|-------|--------|
| **Purpose** | Prevent monotony and "factory" detection; cap how often same template appears in wave and per brand per quarter. |
| **Implementation** | Cap % same template_id per wave; cap per brand per quarter; extend wave density or add dedicated check. |
| **Layer** | 1 |
| **Status** | Planned |
| **Build type** | Extend |
| **Gate/Script** | TBD (extend check_wave_density or new) |
| **Config** | TBD (X% per wave, Y% per brand per quarter) |
| **Artifact** | TBD |
| **Owner** | Ops |
| **Verification** | Wave fails if same template_id exceeds X% of wave or brand quarter cap. |
| **Acceptance criteria** | **Pass:** Template concentration within cap. **Fail:** Wave exceeds template saturation cap. **Evidence:** Gate report. |

---

### GOV-09 — Keyword heatmap monitor

| Field | Value |
|-------|--------|
| **Purpose** | Prevent internal niche crowding; track keyword frequency and saturation. |
| **Implementation** | Track keyword frequency across catalog; saturation thresholds; alert when exceeded. |
| **Layer** | 2 |
| **Status** | Planned |
| **Build type** | New build |
| **Gate/Script** | TBD |
| **Config** | TBD (thresholds) |
| **Artifact** | artifacts/ops/keyword_heatmap.json (or similar) |
| **Owner** | Content QA |
| **Verification** | Artifact shows keyword frequency/saturation; alert when threshold exceeded. |
| **Acceptance criteria** | **Pass:** Heatmap artifact exists; alerts configured. **Fail:** No heatmap or no alert. **Evidence:** Artifact + alert config. |

---

### GOV-10 — Catalog similarity index dashboard

| Field | Value |
|-------|--------|
| **Purpose** | Audit duplication risk; single view of similarity across corpus. |
| **Implementation** | Similarity index (existing); dashboard or summary showing similarity trend / risk score; updated on plan write. |
| **Layer** | Cross-layer |
| **Status** | Partial |
| **Build type** | Extend |
| **Gate/Script** | scripts/ci/update_similarity_index.py; scripts/obs/build_structural_drift_dashboard.py |
| **Config** | N/A |
| **Artifact** | artifacts/catalog_similarity/index.jsonl; artifacts/drift/summary.json |
| **Owner** | Ops |
| **Verification** | Similarity index updated on plan write; dashboard or summary shows trend/risk. |
| **Acceptance criteria** | **Pass:** Index updated; dashboard/summary available with at least one similarity metric. **Fail:** Index not updated or no dashboard. **Evidence:** Index row count; summary.json. |

---

## Phase 3 — Reinforcement (GOV-11..GOV-12)

### GOV-11 — QA sampling protocol tied to metrics

| Field | Value |
|-------|--------|
| **Purpose** | Human oversight at scale; sampling % by risk category. |
| **Implementation** | 100% new template; 25% new teacher; 5% stable brand; 100% if refund alert; config-driven (e.g. qa_sampling_policy.yaml). |
| **Layer** | 3 |
| **Status** | Planned |
| **Build type** | New build |
| **Gate/Script** | TBD |
| **Config** | TBD (e.g. qa_sampling_policy.yaml) |
| **Artifact** | TBD |
| **Owner** | Content QA |
| **Verification** | Sampling % applied by risk category (new template, new teacher, stable, refund alert). |
| **Acceptance criteria** | **Pass:** Policy defines and applies sampling rates by category. **Fail:** No policy or rates not applied. **Evidence:** Config + sampling log. |

---

### GOV-12 — Compliance enforcement automation

| Field | Value |
|-------|--------|
| **Purpose** | Protect account; hard-block prohibited claims; auto-insert disclaimers. |
| **Implementation** | Prohibited phrase scanner; topic-sensitive wording map; mandatory disclaimer injection (in-audio and description). |
| **Layer** | 3 |
| **Status** | Partial |
| **Build type** | Extend |
| **Gate/Script** | scripts/ci/check_author_positioning.py (language); TBD for disclaimers/prohibited phrases |
| **Config** | TBD (prohibited phrases, disclaimer template) |
| **Artifact** | TBD |
| **Owner** | Ops |
| **Verification** | Prohibited phrases blocked; disclaimer present in listing/audio where required. |
| **Acceptance criteria** | **Pass:** Prohibited phrases cause FAIL; disclaimer present where required. **Fail:** Prohibited phrase in output or missing disclaimer. **Evidence:** Gate output; sample listing. |

---

## Reference

- **Architecture and Catalog Health:** [PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md](PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md)
- **Existing gates:** scripts/ci/run_prepublish_gates.py, [scripts/ci/PREPUBLISH_CHECKLIST.md](../scripts/ci/PREPUBLISH_CHECKLIST.md)
