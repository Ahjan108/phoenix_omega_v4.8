# Phoenix 24-Brand Governance Architecture

**Purpose:** Single north-star document for governance at 24-brand scale. Prevents duplication flags, internal cannibalization, brand collapse, algorithm distrust, and scale entropy.  
**Audience:** Ops, Platform, Content QA, release, and engineering.  
**Last updated:** 2026-02-25

---

## Authority and precedence

This document is the **architectural overlay** for governance at scale. It does **not** supersede:

| Spec | Domain |
|------|--------|
| [specs/OMEGA_LAYER_CONTRACTS.md](../specs/OMEGA_LAYER_CONTRACTS.md) | Stage 1–3 handoffs (BookSpec, FormatPlan, CompiledBook) |
| [specs/DUPE_EVAL_SPEC.md](../specs/DUPE_EVAL_SPEC.md) | Duplication evaluation |
| [specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md](../specs/BRAND_ARCHETYPE_VALIDATOR_SPEC.md) | Brand registry validation |

Those specs remain canonical for their domains. This architecture describes how governance controls sit across layers and reference existing gates/specs where applicable.

---

## Catalog Health (north star metric)

**Definition:** Catalog Health = Structural entropy + Metadata diversity + Brand separation + KPI stability.

**Formula (normalized weights):**

```
CH = w1·E + w2·D + w3·S + w4·K
```

- **E** = Structural entropy (e.g. band/slot/template diversity; 0–1 normalized)
- **D** = Metadata diversity (e.g. title/description/keyword divergence; 0–1)
- **S** = Brand separation (e.g. cross-brand topic/structure collision score inverted; 0–1)
- **K** = KPI stability (e.g. refund/completion/CTR vs baseline; 0–1)

**Weights:** Default `w1 = w2 = w3 = w4 = 0.25`. Weights are configurable (e.g. in governance config) so teams do not interpret the metric differently. Used consistently in [PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md](PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md).

---

## Non-Goals

Governance does **not** aim to:

- Increase content volume
- Replace editorial judgment
- Optimize conversion
- Add new templates

Governance is **protective, not generative**. It guards signal, credibility, and platform trust at scale.

---

## Failure scenarios

**Algorithmic duplication collapse** — The platform flags the catalog as duplicate or farm-like. Ranking and distribution suffer; new titles fail to surface. Recovery is slow and may require throttling or structural changes.

**Refund cascade** — Quality or fit issues compound. Refund spikes trigger account or category penalties; platform limits or suspends distribution. Revenue and reputation drop before the cause is fully visible.

**Brand cannibalization** — Own brands compete on the same persona/topic with similar structure. The algorithm clusters them; revenue and identity blur; no single brand gains clear positioning.

---

## Three-layer stack

| Layer | Name | Focus |
|-------|------|--------|
| **Layer 1** | Content Integrity | What is written and assembled: provenance, structure, saturation, determinism |
| **Layer 2** | Brand & Identity | What the book represents: positioning, collision, metadata, narrator, visual separation |
| **Layer 3** | Release & Performance | How it behaves in the wild: KPI sentinels, throttle, A/B, LTV:CAC, localization, compliance, QA sampling |

**Cross-layer:** Wave composition governor; catalog similarity index; provenance audit registry; model mix dashboard.

---

## Layer 1 — Content Integrity

1. **Atom provenance system** — Every compiled book carries atoms_model, atoms_root_hash, teacher/persona/format versions, structural_signature, plan_hash.
2. **Structural signature engine** — Hash arc shape + band sequence + slot order + exercise families per book; index and enforce diversity.
3. **Template saturation controls** — Cap % same template per wave and per brand per quarter.
4. **Exercise rotation guard** — Limit repetition of exercise families and identical intros/flows.
5. **Regeneration drift detector** — If a plan regenerates differently under same inputs → alert.

---

## Layer 2 — Brand & Identity

6. **Brand positioning matrix** — Each brand locked to persona clusters, topic envelope, tone band, runtime range, narrator profile.
7. **Cross-brand topic collision detector** — Block same persona + same topic + similar structure across brands within a defined window (or require structural differentiation).
8. **Metadata uniqueness engine** — Unique title patterns, unique opening description sentence, keyword overlap caps, category density caps.
9. **Keyword heatmap monitor** — Track keyword frequency and saturation across catalog; alert on thresholds.
10. **Cover / visual diversity heuristic** — Auto-check dominant color, typography, layout similarity.
11. **Narrator identity mapping** — Each brand tied to narrator archetype, vocal pacing band, emotional range.

---

## Layer 3 — Release & Performance

12. **KPI baseline sentinel** — Monitor CTR, sample-to-buy, completion, refund rate, review velocity vs template × persona baseline; auto-trigger corrective action.
13. **Adaptive release throttle** — Reduce wave size or freeze template/persona when quality metrics decline.
14. **A/B test registry** — Centralized experiment log; one variable at a time; minimum sample sizes; delta thresholds.
15. **Channel LTV:CAC optimizer** — Compute LTV:CAC per channel; routing bias per template.
16. **Localization tier gate** — City tier qualification; cue sheet; local reviewers; density cap.
17. **Compliance enforcement layer** — Hard-block medical claims, cure language; auto-insert required disclaimers.
18. **QA sampling policy** — 100% new template, 25% new teacher, 5% stable brand, 100% if refund alert; config-driven.

---

## Cross-layer controls

19. **Wave composition governor** — Each wave must satisfy persona, topic, template, structural, and brand diversity.
20. **Catalog similarity index** — Similarity scores across entire corpus; alert if duplication risk increases.
21. **Provenance audit registry** — Searchable index: who built, with what config, when, under which atoms model.
22. **Model mix dashboard** — Track legacy vs cluster %; per brand and per wave; prevent silent drift.

---

## What this achieves

- Structural uniqueness  
- Market separation  
- Algorithm safety  
- Compliance resilience  
- Controlled velocity  
- Performance optimization  
- Brand independence  
- Scale without entropy  

---

## What happens without it

- Cannibalization  
- Metadata clustering  
- Duplication flags  
- Refund cascades  
- Predictable catalog  
- Blurred brands  
- Flattened revenue  

---

## Reality

At 24 brands, content generation is easy. Collision prevention is hard. **Governance is the moat.**

---

## Change control

- **Who can modify:** Governance architecture and minimum core docs are modified by the platform/ops lead (or documented role in your org). Changes should be reviewed and traceable.
- **Version history:** Git history for `docs/` is the source of truth. Optionally reference [docs/SCHEMA_CHANGELOG.md](SCHEMA_CHANGELOG.md) or a dedicated governance changelog if added for high-level change notes.

---

## Appendix

- **Full 80-item hardening blueprint:** [GOVERNANCE_HARDENING_BLUEPRINT.md](GOVERNANCE_HARDENING_BLUEPRINT.md). That blueprint is **reference only, non-authoritative** (no implementation precedence). It avoids documentation drift; this doc and the minimum core remain the authoritative governance sources.
- **12-control minimum core (implementation order, control map, acceptance criteria):** [PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md](PHOENIX_24_BRAND_MINIMUM_GOVERNANCE_CORE.md).
