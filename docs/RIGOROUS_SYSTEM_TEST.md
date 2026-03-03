# Rigorous System Test and Production 100%

**Purpose:** Single reference for (1) simulation-based rigorous testing (10k / 100k Pearl Prime knob coverage) and (2) **what is still required** for 100% production. Simulation is **excellent readiness tooling**; it is **not standalone production 100%**.

**See also:** [FEATURES_SCALE_AND_KNOBS.md](FEATURES_SCALE_AND_KNOBS.md) (all knobs), [SYSTEMS_V4.md](SYSTEMS_V4.md) (systems test), [DOCS_INDEX.md](DOCS_INDEX.md) (docs vs production 100%).

**Document all:** For a single index of every doc, script, config, and artifact for rigorous system test and simulation (10k/100k, analyzer, variation report, config, artifacts, CI), see [DOCS_INDEX.md § Rigorous system test & simulation (document all)](DOCS_INDEX.md#rigorous-system-test--simulation-document-all).

---

## 1. Simulation coverage (readiness tooling)

- **10k sim** — Format/structure at scale (topic × persona × format); Phase 1+2+3 synthetic validation; no real atoms. Runner: `scripts/ci/run_simulation_10k.py` (or `simulation/run_simulation.py --n 10000 --use-format-selector --phase2 --phase3`).
- **100k sim (full knobs)** — Same as above with **every knob** exercised: persona, topic, format, angle_id, book_structure_id, journey_shape_id, motif_id, reframe_profile_id, section_reorder_mode, chapter_order_mode. Runner: `scripts/ci/run_simulation_100k.py`; analysis: `scripts/ci/analyze_pearl_prime_sim.py`.

This is **synthetic validation**: mock pool, no real pipeline, no real atoms. It proves format/structure and variation knobs at scale and gives best/worst combo analysis. **Strong simulation coverage, but not 100% by itself.**

---

## 2. What is still required for 100% production

For full production confidence you still need all of the following. Until they are in place, treat simulation + analyzer as **readiness tooling**, not the sole definition of production-ready.

| # | Requirement | Purpose |
|---|-------------|--------|
| **1** | **Real pipeline canary runs** (not sim) on sampled **worst** and **best** combos from the analyzer | Prove that actual `run_pipeline.py` compile + render succeeds/fails as expected for those combos; catch resolver/atom/arc issues the sim cannot see. |
| **2** | **CI gate** wired to fail on **regression thresholds** from the analyzer (e.g. pass rate by dimension or overall below baseline) | Prevent `main` from regressing; analyzer output becomes the baseline to compare against. |
| **3** | **Evidence on `main`**: green workflow runs + **artifact links** (e.g. simulation_100k.json, pearl_prime_sim_analysis.json) | Auditable proof that the suite ran and what the current baseline is. |
| **4** | **Release-path smoke** with **rollback proof** (runbook, snapshots, rollback script exercised) | Before release, run smoke on the real path and confirm rollback works so production can be reverted if needed. |

---

## 3. Summary

- **Simulation (10k / 100k + full knobs + analyzer):** Excellent readiness tooling; proves format/structure and knob coverage at scale; yields best/worst combos and recommendations.
- **Production 100%:** Requires (1) real pipeline canaries on worst/best combos, (2) CI gate on analyzer regression thresholds, (3) evidence on main (green workflows + artifact links), (4) release-path smoke with rollback proof.

Document and implement (1)–(4) when moving from “readiness” to “production 100%.”
