# AI LLM testing framework for books
_Exported on 3/5/2026 at 17:54:39 GMT+8 from Cursor (2.5.25)_

---

**User**

crate AI llm github cohisve bestseller tester to test 10k books from pearl prime cli and 10k teacher mode books all personas + topis and v2 EI to see what is 100% . test read all

---

**Cursor**


Exploring the codebase to understand the pearl prime CLI, teacher-mode books, personas, topics, and v2 EI so we can build an LLM-based bestseller tester for 10k books.



Checking how we enumerate teacher-mode books and the format selector for simulation:



Checking how to build the full teacher-mode matrix (personas × topics × engines) and whether a run_pipeline CLI exists:



Creating the cohesive bestseller tester: adding the main script and a README section.



Creating the cohesive bestseller tester script.



Summary of what was added:

## 1. **`scripts/ci/llm_cohesive_bestseller_tester.py`**

Single script that:

- **Test read all** (`--read-all`): Loads and prints config used for “test read all”:
  - `config/catalog_planning/canonical_personas.yaml`
  - `config/catalog_planning/canonical_topics.yaml`
  - `config/catalog_planning/teacher_persona_matrix.yaml` (teachers, allowed_personas, allowed_engines)
  - `config/format_selection/format_registry.yaml` (structural + runtime formats, tiers)
  - EI v2 config path and enabled modules

- **Pearl Prime 10k**: Reads `artifacts/simulation_10k.json` (or path via `--pearl-prime-input`), finds bestseller-tier and Tier A failures, and aggregates error reasons. Optional `--run-pearl-10k` runs `run_simulation_10k.py` first.

- **Teacher-mode matrix**: With `--teacher-matrix`, builds the full test set from teacher_persona_matrix: every **(teacher_id, persona_id, topic_id, engine)** allowed (personas × topics × teachers × engines), capped at 10k by default (`--teacher-matrix-cap`).

- **EI v2**: With `--ei-v2-report`, pulls in `artifacts/ei_v2/eval_rigorous_report.json` if present (quality scores, V1 vs V2 agreement, safety/dedup/TTS/arc).

- **LLM**: With `--llm`, sends a single prompt with config summary, Pearl 10k failure summary, teacher matrix size, and EI v2 summary, and asks for:
  - **What is 100%** (dimensions/segments that are fully passing)
  - **Bestseller cohesion gaps** (what would block bestseller-tier quality)
  - **Root causes and one-line recommendations**  
  Reply is parsed as JSON and stored in the report.

- **Output**: Writes `artifacts/reports/cohesive_bestseller_tester_report.json` and `cohesive_bestseller_tester_SUMMARY.txt`. With `--require-100`, exits 1 if there are any bestseller-tier failures in the Pearl 10k run.

## 2. **`scripts/ci/README.md`**

New section documents the cohesive bestseller tester: options (read-all, pearl input, teacher-matrix, ei-v2-report, run-pearl-10k, llm, require-100) and example commands.

**Example usage**

```bash
# Only read all config (personas, topics, teachers, formats, EI v2)
PYTHONPATH=. python scripts/ci/llm_cohesive_bestseller_tester.py --read-all

# Full run: 10k Pearl Prime + teacher matrix + EI v2 report + LLM
PYTHONPATH=. python scripts/ci/llm_cohesive_bestseller_tester.py \
  --pearl-prime-input artifacts/simulation_10k.json \
  --teacher-matrix --ei-v2-report --llm --out artifacts/reports

# Run 10k sim first, then test with 100% gate
PYTHONPATH=. python scripts/ci/llm_cohesive_bestseller_tester.py \
  --run-pearl-10k --teacher-matrix --ei-v2-report --llm --require-100
```

For strict 100% gating in CI, use this script with `--require-100` and/or run `analyze_pearl_prime_sim.py --min-pass-rate 1.0` on the same simulation artifact.

---

**User**

more robbust itellegent testing 

---

**Cursor**


Enhancing the cohesive bestseller tester with smarter logic, stronger validation, and more actionable reporting.



Adding dimension-aware analysis, baseline comparison, coverage intelligence, severity levels, and input validation.



Implementing robust, intelligent enhancements.



Verifying the script runs:



Summary of the **robust, intelligent testing** added to the cohesive bestseller tester:

## 1. **Validation & robustness**
- **Simulation JSON validation** – `validate_sim_structure()` checks for `results`, list shape, and `passed`/`format_id`. Validation errors are stored and reported.
- **Safe loading** – `load_pearl_prime_sim()` returns `(results, summary, validation_errors)` and handles read/JSON errors without crashing.
- **Subprocess timeout** – `--run-pearl-timeout` (default 600s) for `run_simulation_10k.py` to avoid hung runs.
- **LLM response validation** – `validate_llm_response()` ensures `what_is_100_percent`, `bestseller_gaps`, `root_causes` exist; optional retry (up to 2) with backoff if the response is invalid or the call fails.

## 2. **Dimension-aware analysis**
- **Pearl Prime** – `analyze_pearl_dimensions()`: pass rate by format and tier, phase2/phase3 failure counts, worst formats/tiers, and phase2/phase3 summary.
- **EI v2** – `analyze_ei_v2_dimensions()`: all 10 dimensions (therapeutic_value, emotional_coherence, engagement, etc.) compared to `--ei-v2-threshold` (default 0.5); dimension-level fails and scores are in the report.
- **Coverage** – `coverage_from_pearl_results()` infers formats (and optionally persona/topic) from sim results for coverage reporting.

## 3. **Severity & health score**
- **Severity** – `classify_severity()`: **CRITICAL** (bestseller failures), **HIGH** (pearl/phase2/phase3 failures), **MEDIUM** (e.g. pass rate &lt; 95%), **LOW**.
- **Health score (0–100)** – `compute_health_score()` from: Pearl pass rate (40%), bestseller OK (30%), EI v2 composite (20%), teacher-matrix coverage (10%). Reported in the summary and JSON.
- **Require-100** – Exit 1 on any bestseller-tier failure or any CRITICAL severity.

## 4. **Baseline comparison**
- **`--baseline PATH`** – Loads a prior report and compares health score and Pearl pass rate; writes `baseline_comparison` with deltas and regression warnings.

## 5. **LLM**
- **Richer prompt** – Includes EI v2 dimension names, severity summary, health score, worst formats, and dimension-fail list.
- **Retries** – Up to 2 retries with sleep on invalid JSON or missing keys.
- **Validation** – If required keys are still missing after retries, the run continues and adds `llm_validation_warning` to the report.

## 6. **New CLI options**
- `--baseline` – Baseline report path for regression.
- `--ei-v2-threshold` – Dimension fail threshold (default 0.5).
- `--run-pearl-timeout` – Timeout in seconds for the 10k sim (default 600).

Example run (no LLM) produced **health score 61.1**, severity **HIGH** (pearl/phase2/phase3 failures) and **MEDIUM** (pass rate &lt; 95%), and **EI v2 dimensions below threshold**: engagement, cohesion, marketability, content_uniqueness, somatic_precision. The script and README are updated; run with `--llm` for full LLM analysis.

---

**User**

document everything use @docs/DOCS_INDEX.md 

---

**Cursor**


Adding cohesive bestseller tester and bestseller error report to DOCS_INDEX in the appropriate sections.



Noting the inventory already includes the new artifacts. Adding a cross-reference to the cohesive tester in the Rigorous section and updating the "Last updated" date:



Checking whether the video script we have open is documented:



Adding an explicit Video pipeline entry for the FLUX generator script.



Summary of updates to **docs/DOCS_INDEX.md**:

## 1. **Rigorous system test & simulation (document all)**

- **Scripts**
  - **Cohesive bestseller tester** — [scripts/ci/llm_cohesive_bestseller_tester.py](../scripts/ci/llm_cohesive_bestseller_tester.py): 10k Pearl Prime + teacher-mode matrix + EI v2, `--read-all`, dimension analysis, severity, health score, baseline, `--require-100`.
  - **Bestseller error report** — [scripts/ci/llm_bestseller_error_report.py](../scripts/ci/llm_bestseller_error_report.py): bestseller-tier failures from 10k sim, optional LLM, 100% gate.
- **Artifacts**
  - `artifacts/reports/cohesive_bestseller_tester_report.json` and `cohesive_bestseller_tester_SUMMARY.txt`
  - `artifacts/reports/bestseller_error_report.json` and `bestseller_error_report_SUMMARY.txt`
- **Intro** — Note that the section covers “cohesive bestseller testing” and a pointer to **scripts/ci/README.md** § AI/LLM cohesive bestseller tester.

## 2. **Scripts/CI — content quality gates**

- Rows for **llm_cohesive_bestseller_tester.py** and **llm_bestseller_error_report.py** and their purposes.

## 3. **Document all — complete inventory**

- **Scripts & code** — Both scripts listed with section “Simulation / Cohesive bestseller” and “Simulation / Bestseller QA”.
- **Root & other** — Cohesive and bestseller report artifacts were already present; no change.

## 4. **Video pipeline**

- **FLUX image generator** — [scripts/video/run_flux_generate.py](../scripts/video/run_flux_generate.py) with links to VIDEO_IMAGE_MASTER_PROMPT_SPEC.md and flux_shnell_research.rtf.

## 5. **Last updated**

- Set to **2026-03-05** with note “(cohesive bestseller tester + bestseller error report documented)”.

