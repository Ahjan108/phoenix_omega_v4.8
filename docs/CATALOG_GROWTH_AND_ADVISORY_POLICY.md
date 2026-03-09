# Catalog Growth and Advisory Policy

**Purpose:** Conservative growth curve as **advisory + human override**. One **hard block** only for legal/compliance. All other signals (rejection rate, engagement, metadata similarity) produce **advisory issues**; books ship unless a human pauses the wave.

**Related:** [docs/CATALOG_ARCHITECTURE_AT_SCALE.md](./CATALOG_ARCHITECTURE_AT_SCALE.md), [docs/RELEASE_VELOCITY_AND_SCHEDULE.md](./RELEASE_VELOCITY_AND_SCHEDULE.md), [config/governance/advisory_policy.yaml](../config/governance/advisory_policy.yaml).

---

## 1. Growth curve (advisory)

Realistic, conservative path so platforms see **stable quality and engagement** before rapid expansion:

| Phase   | Titles/year | Per month | Focus |
|---------|-------------|-----------|--------|
| Year 1  | 20–60       | 2–5       | Establish credibility, gather reviews |
| Year 2  | 80–150      | 7–12      | Moderate expansion, series + topic diversity |
| Year 3  | 200–400     | 15–35     | Full publishing program, multiple programs |
| Year 4+ | 500+        | 40+       | Large-scale catalog, many programs |

**Rule of thumb:** `monthly_growth_rate ≤ 25–35%` keeps expansion predictable. Start small → demonstrate quality → expand gradually → build series and programs.

Config: [config/release_velocity/growth_curve_advisory.yaml](../config/release_velocity/growth_curve_advisory.yaml) (target bands by phase). Used for **planning and UI display only**; no automatic gate that blocks release.

---

## 2. No hard gates (except legal/compliance)

**Do not hard-block** on:

- Rejection/flag rate (platform)
- Completion/read-through (engagement)
- Refund/takedown rate
- Metadata similarity (see §3)
- Anti-homogeneity score (wave diversity)
- Engagement or trust signals (see §4)

**Hard block only:** Legal/compliance (e.g. copyright, policy violation, mandatory takedown). When a legal/compliance block exists, export must not proceed until resolved.

Config: `config/governance/advisory_policy.yaml` → `no_hard_gates` list; `block_only_legal_compliance: true`.

---

## 3. Advisory issues (UI)

Instead of failing the pipeline, emit **AdvisoryIssue** for human review.

**Severity:**

- **info** — Watch; no action required immediately.
- **warn** — Needs review soon.
- **critical** — Manual decision required; still ship by default unless human pauses.

**Books ship** unless a legal/compliance block exists or a human uses the **manual pause** in the UI to stop a wave.

Schema: `schemas/advisory_issue_v1.schema.json`. Fields: `issue_id`, `severity`, `reason`, `source` (e.g. `metadata_similarity`, `wave_diversity`, `catalog_fingerprint` for fingerprint-risk heuristics), `plan_id` / `wave_id`, `nearest_neighbors` (for similarity), `created_at`. Catalog fingerprint risk (near-duplicates, series continuity, release shape) can surface as advisory alerts; see [docs/CATALOG_ARCHITECTURE_AT_SCALE.md](./CATALOG_ARCHITECTURE_AT_SCALE.md) §10.

---

## 4. Metadata similarity → advisory, not block

- **Keep** the similarity check in assembly/review (e.g. `check_platform_similarity.py`, CTSS).
- **Change behavior** when advisory policy is enabled:
  - Similarity high (e.g. ≥ block threshold) → emit **warn** or **critical** AdvisoryIssue with **reason** and **nearest_neighbors** (book_id, similarity score).
  - **Ship allowed by default**; no exit code that blocks export.
- **Manual pause** in UI if operator decides to stop the wave.

Config: [config/governance/advisory_policy.yaml](../config/governance/advisory_policy.yaml) → `metadata_similarity_behavior: emit_advisory`, `block_on_similarity: false`. When `block_on_similarity` is false, prepublish/similarity scripts should emit an AdvisoryIssue (e.g. into the report or `advisory_issues` array) and **not** exit 2; implementation can read this config in `run_prepublish_gates.py` / `check_platform_similarity.py`.

---

## 5. Trust Signal Score (boost, don’t auto-throttle)

Build a **Trust Signal Score** from:

- Engagement (read-through, completion)
- Low policy friction (few flags/takedowns)
- Positive feedback trend

**Planner use:**

- **Strong score** → increase wave size (e.g. multiplier &gt; 1).
- **Weak score** → keep baseline; **do not** auto-throttle unless operator explicitly chooses.
- Score is advisory input to planning; not a gate that blocks release.

Config: `config/governance/advisory_policy.yaml` → `trust_signal` (weights, multiplier bounds). Implementation: planner or scheduler reads score and applies optional wave-size multiplier when configured.

---

## 6. Series-heavy strategy (Teacher Mode)

- **Default** Teacher Mode to **series-first**.
- **Target mix (Google Play / Findaway industry-informed):**
  - 65–75% of output in series (ideal 70%); 25–35% standalone.
  - Of series: **40%** micro (3–4 books), **40%** mid (5–7 books), **20%** flagship (8–12 books). Avoid 1–2; complete series clusters.
- Keeps catalog natural and avoids uniform “all standalone” or “all same length.”

Config: [config/catalog_planning/series_mix_targets.yaml](../config/catalog_planning/series_mix_targets.yaml) (operational source); [config/governance/advisory_policy.yaml](../config/governance/advisory_policy.yaml) → `series_mix`. Planning/portfolio use when allocating. Target: 65–75% series (ideal 70%); of series 40% micro (3–4), 40% mid (5–7), 20% flagship (8–12); avoid 1–2; complete series clusters. Rationale: industry-informed for Google Play / Findaway (read-through data; not a single study).

---

## 7. Safeguards (not weird)

- Stagger release days across brands/programs (`release_scheduler.yaml`).
- Mix series and standalone in each wave.
- Avoid all teachers launching identical series lengths at once.
- Keep title grammar families varied by program/worldview.

These remain structural/process controls; no new hard gates.

---

## 8. Summary

| Item | Policy |
|------|--------|
| Growth curve | Advisory only; no gate. Config: growth_curve_advisory.yaml. |
| Hard blocks | Legal/compliance only. |
| Rejection/engagement/refund | No hard gates; optional AdvisoryIssue (info/warn/critical). |
| Metadata similarity | Emit AdvisoryIssue (warn/critical) + nearest_neighbors; ship by default; manual pause in UI. |
| Trust Signal Score | Boost wave size when strong; baseline when weak; no auto-throttle. |
| Series mix | 65–75% series (ideal 70%); 40% micro (3–4), 40% mid (5–7), 20% flagship (8–12). Config: series_mix_targets.yaml, advisory_policy series_mix. |
| UI | AdvisoryIssue list; manual pause per wave. |
