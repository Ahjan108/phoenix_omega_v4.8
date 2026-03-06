# Content and metadata analysis in repository
_Exported on 3/5/2026 at 17:58:14 GMT+8 from Cursor (2.5.25)_

---

**User**

lookat @docs/DOCS_INDEX.md do full analysis and status of contnet and metadata in whole repo. tell me if there is anything needed, missing, expected , etc

see if there's an existing .py for this. if there do anlysis to make sure it's doing it right

---

**Cursor**


Reading DOCS_INDEX in chunks and searching for scripts that analyze docs or metadata.



Reading the docs governance script and more of DOCS_INDEX to map its structure and extract linked paths.



Running the governance script and scanning DOCS_INDEX for "not present" and path patterns:



Running the script with python3 and verifying link resolution:



Checking for absolute-path links and whether the script should resolve from repo root:



Checking whether scripts and configs referenced as missing in the index actually exist:



Checking whether the config files and tier0_trend exist:



Checking observability script paths referenced in the index:



Here’s the analysis and status.

---

## 1. DOCS_INDEX.md — Role and structure

- **Purpose:** Canonical index for doc authority and navigation. Only existing files are linked; planned/missing items are backlog (plain text or path with ⚠️ *file not present*).
- **Last updated:** 2026-03-05 (present and current).
- **Structure:** Control plane bundle, canonical authority, core system docs, then domain “(document all)” sections (Rigorous system test, Pearl News, Marketing, Church & payout, EI, Teacher Mode, etc.), plus a **Document all — complete inventory** at the end with ✓/⚠️.

---

## 2. Existing Python tool: `scripts/ci/check_docs_governance.py`

**What it does:**

1. **Link integrity** — Finds markdown links `[text](path)`, resolves paths relative to `docs/` (repo root for `../`), and **fails** if the target file does not exist.
2. **Last updated** — Requires a line matching `**Last updated:** YYYY-MM-DD`; fails if missing or invalid.
3. **Staleness (optional)** — With `--check-staleness`, warns if that date is older than 30 days (does not fail).

**Behavior:**

- Correctly skips external URLs, `#anchor`-only, and `{{ ... }}`.
- Strips `#anchor` before resolving; only the file path is checked.
- Relative links like `./X.md` and `../scripts/foo.py` are resolved from `docs/` so they match repo layout.
- Backlog items are usually in **backticks** (e.g. `` `scripts/ci/run_simulation_100k.py` ``), not `[text](path)`, so they are **not** validated by this script. That matches the stated policy: “only existing files are linked.”

**Edge case:** If the index ever used a link like `[x](/specs/foo.md)` (leading slash), the script would treat it as filesystem-absolute, not repo-relative. There are no such links in the current index, so this is only a future caveat.

**Verdict:** The script is doing the right thing for the current index and policy. No code change is required for normal use.

---

## 3. Governance run result

```text
DOCS_INDEX governance check PASSED
  Checked: docs/DOCS_INDEX.md
  Link integrity: OK
  Last updated: 2026-03-05
```

So: every **linked** target exists, and the required metadata is present and current.

---

## 4. Content and metadata status

### 4.1 Stale “file not present” (files exist but index says missing)

These are listed in DOCS_INDEX as ⚠️ *file not present* even though the files exist. The index should be updated (replace with links and remove ⚠️, and/or fix the complete inventory):

| Item | Actual status |
|------|----------------|
| `config/quality/tier0_book_output_contract.yaml` | **Exists** |
| `scripts/ci/check_book_output_tier0_contract.py` | **Exists** |
| `scripts/ci/run_canary_100_books.py` | **Exists** |
| `tests/test_ei_v2_hybrid.py` | **Exists** |

### 4.2 Complete inventory — wrong ✓

| Doc | Issue |
|-----|--------|
| `EI_V2_ROLLOUT_PROOF_CHECKLIST.md` | Marked ✓ in inventory but **file not found** (should be ⚠️ or backlog). |

### 4.3 Correctly missing (backlog / ⚠️)

- **Simulation:** `scripts/ci/run_simulation_100k.py`
- **Config:** `config/source_of_truth/chapter_order_modes.yaml`, `config/quality/canary_config.yaml`, `config/source_of_truth/enlightened_intelligence_registry.yaml`
- **Scripts:** `scripts/ci/tier0_trend.py`
- **Docs:** `docs/PEARL_NEWS_WRITER_SPEC.md`, `docs/norcal_dharma.yaml`, `docs/EI_V2_ROLLOUT_PROOF_CHECKLIST.md`, `docs/ei_v2_branch_protection_evidence.png`
- **Locale docs:** `LOCALE_PROSE_AND_PROMPTING.md`, `MULTILINGUAL_ARCHITECTURE.md`, `KOREA_MARKET_AND_PROSE.md`, `JAPANESE_MARKET_SELFHELP_GUIDE.md`
- **Payout:** `specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md`, `config/payouts/*`, payout package files — all noted as not present in repo

### 4.4 Optional improvement for the governance script

The script only validates **links** `[text](path)`. It does **not**:

- Validate backtick paths (e.g. `` `path/to/file` ``) that appear in the “complete inventory” with ✓.
- Detect when the inventory says ✓ but the file is missing (like `EI_V2_ROLLOUT_PROOF_CHECKLIST.md`).

If you want the index to be machine-checkable for that, you could add an optional mode that parses the inventory table and checks that every path marked ✓ exists and every path marked ⚠️ is either missing or explicitly backlog. That would require parsing the inventory table format and is not required for the current “link integrity + Last updated” contract.

---

## 5. Summary

| Area | Status |
|------|--------|
| **DOCS_INDEX governance script** | Correct; no change needed for current behavior. |
| **Link integrity** | All linked targets exist; check passes. |
| **Last updated** | Present and current (2026-03-05). |
| **Stale “not present”** | 4 items (tier0 config, tier0 checker, canary script, EI V2 hybrid test) exist but are still marked missing — update DOCS_INDEX. |
| **Wrong ✓ in inventory** | `EI_V2_ROLLOUT_PROOF_CHECKLIST.md` — file missing; change to ⚠️ or backlog. |
| **Truly missing** | Backlog list is consistent with repo (canary_config, tier0_trend, 100k sim, Pearl News writer spec, church/payout/locale docs, etc.). |

**Recommended next steps:**

1. In DOCS_INDEX, for the four items in §4.1: add proper links and remove the ⚠️ *file not present* (and set ✓ in the complete inventory where applicable).
2. In the complete inventory: set `EI_V2_ROLLOUT_PROOF_CHECKLIST.md` to ⚠️ (or list it as backlog) and add `docs/ei_v2_branch_protection_evidence.png` as ⚠️ if it’s still not in repo.
3. Optionally: extend `check_docs_governance.py` to validate the “Document all — complete inventory” table (✓ vs ⚠️ vs actual file existence) so these mismatches are caught automatically.

---

**User**

do: Three things, in order of value:

**1. Fix the index (5 minutes, do it now).** Four files exist but are still marked `⚠️ file not present` — just swap them for real links. One file is marked `✓` but is actually missing — flip it to `⚠️`. The index is the source of truth; right now it's lying in 5 places.

**2. Extend the governance script (30 minutes, high value).** Right now the script only catches broken links. It doesn't catch what just broke — a `✓` in the inventory table pointing to a file that doesn't exist. Add one optional mode that parses the inventory table and checks `✓ = file exists, ⚠️ = file missing`. Then these mismatches get caught in CI automatically and never drift again.

**3. Leave the backlog alone.** Everything correctly marked as missing/backlog is accurate. Don't touch it — that list is doing its job.

So: fix the index first (it's wrong right now), then wire up the script to make sure it can never go wrong silently again. Want me to do both?

---

**Cursor**


Fixing the index first, then extending the governance script.



Applying index fixes.



Index fixes complete. Extending the governance script: reading the script and inventory table format.



Checking more inventory rows for path patterns (links vs backticks):



Implementing inventory parsing and validation in the governance script.



Fixing status parsing and adding inventory check to the report.



Skipping table separator rows and fixing path resolution for link-only first cells:



Fixing separator detection: we used first_cell before assignment.



Making path-relative display safe for paths outside repo_root:



Running the script with and without --check-inventory:



Checking whether those paths exist or are parsing errors:



Confirming the script is correct: it's flagging 11 additional inventory rows marked ✓ whose files are missing (pre-existing index drift). Default run still passes; --check-inventory is optional so we can add it to CI after fixing those rows. Verifying default (no --check-inventory) and completing the todo.



Summary of what was done:

---

## 1. Index fixes (DOCS_INDEX.md)

**Replaced 4 “file not present” entries with real links** (files exist):

- **Tier 0 contract config** — `config/quality/tier0_book_output_contract.yaml` → proper link  
- **Tier 0 checker** — `scripts/ci/check_book_output_tier0_contract.py` → proper link  
- **Canary script** — `scripts/ci/run_canary_100_books.py` → proper link  
- **test_ei_v2_hybrid.py** — updated in all 4 places (EI Tests row, EI V2 gates description, test file inventory table, complete inventory) to use the link and ✓  

**Corrected 1 wrong ✓:**

- **EI_V2_ROLLOUT_PROOF_CHECKLIST.md** — complete inventory status changed from ✓ to ⚠️ missing (file is not in repo).

Backlog entries (e.g. canary_config.yaml, tier0_trend.py, run_simulation_100k.py, PEARL_NEWS_WRITER_SPEC.md, payout/locale docs) were left as-is.

---

## 2. Governance script extension (check_docs_governance.py)

**New optional mode: `--check-inventory`**

- Parses the **“Document all — complete inventory”** section (all tables with a Status column).
- For each row: reads first column (link target or backtick path) and last status column.
- **✓** → file must exist (fail if missing).  
- **⚠️ / missing** → file must not exist (fail if present, so index can be updated).
- Resolves paths: link targets from `docs/`, backtick paths with `/` from repo root, bare filenames from `docs/`.
- On mismatch: prints line number, path, and whether the problem is “✓ but file missing” or “⚠️ but file exists”.

**Behavior:**

- **Without `--check-inventory`:** unchanged; link integrity + Last updated only (still passes).
- **With `--check-inventory`:** also runs inventory checks. Currently **11** extra mismatches are reported (rows marked ✓ for files that don’t exist: e.g. `config/localization/quality_contracts/README.md`, `.github/workflows/translate-atoms-qwen-matrix.yml`, several EI V2 and translation scripts). Those are existing index/repo drift, not bugs in the script.

**CI:** Keep running the script without `--check-inventory` so current CI stays green. After you fix or correct those 11 rows in the index (or add the files), add `--check-inventory` to the governance job so future drift is caught automatically.

---

## 3. Files touched

- **docs/DOCS_INDEX.md** — 9 edits (4 stale ⚠️→links, 1 ✓→⚠️, 4 test_ei_v2_hybrid updates).  
- **scripts/ci/check_docs_governance.py** — docstring updated, `BACKTICK_PATH_RE` added, `_parse_inventory_tables`, `_check_inventory`, `--check-inventory` flag, and inventory failure reporting in `check_docs_index`.

---

**User**

fix: **The workflow going forward:** fix those 11 rows → add `--check-inventory` to the CI job → the index can never drift silently again.

Clean and concrete. **12 rows** marked `✓` in the index but the files don't exist. Three clusters:

**Localization / CI workflows (3 rows)** — `config/localization/quality_contracts/README.md`, and two GitHub Actions workflows (`translate-atoms-qwen-matrix.yml`, `locale-gate.yml`). These are future multilingual infrastructure — not built yet.

**EI V2 core files (4 rows)** — `hybrid_selector.py`, `learner.py`, `dimension_gates.py`, and `run_ei_v2_catalog_calibration.py`. The EI V2 system isn't fully built out yet — these are planned files.

**Translation scripts (5 rows)** — `translate_atoms_all_locales_cloud.py`, `validate_translations.py`, `merge_translation_shards.py`, `check_golden_translation.py`, `native_prompts_eval_learn.py`. All translation pipeline scripts, none exist.

**The fix is simple:** for all 12, change `✓` to `⚠️` in the inventory table. These are backlog, not done. Once that's done, you add `--check-inventory` to CI and the index is fully honest and machine-enforced.



---

**Cursor**


Fixing the 12 inventory rows (✓ → ⚠️ missing) and adding `--check-inventory` to the CI job.



Applying all 12 inventory fixes and updating the CI workflow.



Verifying governance check with --check-inventory:



Summary of changes:

**1. DOCS_INDEX.md — 12 rows updated (✓ → ⚠️ missing)**

- **Localization / CI (3):** `config/localization/quality_contracts/README.md`, `.github/workflows/translate-atoms-qwen-matrix.yml`, `.github/workflows/locale-gate.yml`
- **EI V2 (4):** `phoenix_v4/quality/ei_v2/hybrid_selector.py`, `learner.py`, `dimension_gates.py`, `scripts/ci/run_ei_v2_catalog_calibration.py`
- **Translation scripts (5):** `scripts/translate_atoms_all_locales_cloud.py`, `validate_translations.py`, `merge_translation_shards.py`, `check_golden_translation.py`, `native_prompts_eval_learn.py`

**2. CI — docs job now runs with inventory check**

- **.github/workflows/docs-ci.yml:** The docs governance step now runs `check_docs_governance.py --check-inventory` (step name updated to “links + freshness + inventory + authority”).

**Verification**

- `python3 scripts/ci/check_docs_governance.py --check-inventory` exits 0 and reports “Inventory table: OK”.

The index now matches the backlog for these 12 items, and CI will fail if the inventory table drifts (✓ for missing files or ⚠️ for existing ones).

---

**User**

does this tell me if there is any content missing. i mean book prose -anything that can be assembled in a book. if not that's what to do next

---

**Cursor**


Checking what the current setup covers and how book-assemblable content is tracked:



**Short answer: no.** The docs index and governance script only care about **docs, specs, scripts, configs, and workflows**. They do **not** tell you if any **book prose** or other assemblable content is missing (atoms, stories, exercises, etc.).

**What they do cover:**
- Link integrity and “Document all — complete inventory” (✓/⚠️) for *files* in the index
- No notion of persona/topic/role, slot coverage, or “can we assemble this book?”

**What already exists for *content* coverage (separate from DOCS_INDEX):**
- **`tests/test_atoms_coverage_100_percent.py`** — 450/450 atom pool: all persona × topic × pool combos have CANONICAL.txt (marked `slow` in CI).
- **`scripts/ci/check_teacher_readiness.py`** — Teacher atom pool readiness (min EXERCISE/STORY counts).
- **`phoenix_v4/planning/coverage_checker.py`** — Plan-time coverage when compiling (can fail if atoms are below `min_atoms_per_role`).
- **`scripts/fill_non_story_coverage_gaps.py`** — Fills missing HOOK/SCENE/REFLECTION/INTEGRATION/EXERCISE CANONICAL.txt.
- **`scripts/generate_teacher_gap_atoms.py`** — Generates candidate atoms for teachers with pool gaps.
- **DOCS_INDEX** § Atom coverage / Teacher Mode references things like `artifacts/teacher_coverage_report.json`, `TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC`, and the atoms coverage test.

So “is any content missing?” is answered by **content coverage** tooling (atoms, teacher readiness, coverage checker), not by the docs index.

**What to do next (concrete):**
1. **Use existing content checks**  
   Run the atoms coverage test and teacher readiness check (and any coverage report scripts you have). Their output is what tells you “this persona/topic/role or teacher is missing prose” — not DOCS_INDEX.
2. **Single “content missing” view (if you want it)**  
   Add a small **content-coverage report or script** that:
   - Calls or reuses the same logic as the atoms coverage test + teacher readiness + coverage checker (and any gap scripts),
   - Outputs a single summary: e.g. “Missing: persona × topic × role list, teacher gap list, and/or plan-level coverage failures,”
   - Optionally writes something like `artifacts/content_coverage_report.json` and/or a one-page summary (e.g. markdown or a script that prints “missing book content” only).
3. **Optional: tie into CI or docs**  
   - Run that content report in CI (e.g. a job that fails or warns when coverage is below threshold), and/or  
   - Add a short section in DOCS_INDEX that points to “how to check for missing book content” (this script/report + the existing tests), without making the docs checker itself content-aware.

So: the index does **not** tell you if book prose is missing; that’s the role of the content-coverage tools above. The next step is to rely on those and, if you want one place to look, add a content-coverage report (and optionally CI + a pointer in the index).

---

**User**

analyze that this is doing it properly and compltely : [What already exists for content coverage (separate from DOCS_INDEX):
tests/test_atoms_coverage_100_percent.py — 450/450 atom pool: all persona × topic × pool combos have CANONICAL.txt (marked slow in CI).
scripts/ci/check_teacher_readiness.py — Teacher atom pool readiness (min EXERCISE/STORY counts).
phoenix_v4/planning/coverage_checker.py — Plan-time coverage when compiling (can fail if atoms are below min_atoms_per_role).
scripts/fill_non_story_coverage_gaps.py — Fills missing HOOK/SCENE/REFLECTION/INTEGRATION/EXERCISE CANONICAL.txt.
scripts/generate_teacher_gap_atoms.py — Generates candidate atoms for teachers with pool gaps.
DOCS_INDEX § Atom coverage / Teacher Mode references things like artifacts/teacher_coverage_report.json, TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC, and the atoms coverage test.
So “is any content missing?” is answered by content coverage tooling (atoms, teacher readiness, coverage checker), not by the docs index.
]. then Use existing content checks
Run the atoms coverage test and teacher readiness check (and any coverage report scripts you have). Their output is what tells you “this persona/topic/role or teacher is missing prose” — not DOCS_INDEX.
Single “content missing” view (if you want it)
Add a small content-coverage report or script that:
Calls or reuses the same logic as the atoms coverage test + teacher readiness + coverage checker (and any gap scripts),
Outputs a single summary: e.g. “Missing: persona × topic × role list, teacher gap list, and/or plan-level coverage failures,”
Optionally writes something like artifacts/content_coverage_report.json and/or a one-page summary (e.g. markdown or a script that prints “missing book content” only).
Optional: tie into CI or docs
Run that content report in CI (e.g. a job that fails or warns when coverage is below threshold), and/or
Add a short section in DOCS_INDEX that points to “how to check for missing book content” (this script/report + the existing tests), without making the docs checker itself content-aware.
So: the index does not tell you if book prose is missing; that’s the role of the content-coverage tools above. The next step is to rely on those and, if you want one place to look, add a content-coverage report (and optionally CI + a pointer in the index).


---

**Cursor**


Analyzing existing content-coverage tooling, running the checks, and adding a single content-coverage report plus DOCS_INDEX/CI wiring.



Checking config paths and how to invoke the tests programmatically:



Creating the analysis doc and content-coverage report script.



Implementing the content-coverage report script:



Running the content coverage report (atoms + plan; skipping teachers for speed):



Report ran. Adding the DOCS_INDEX section and locating where to insert it:



Adding the new script and doc to the Document all — complete inventory so they're tracked.



Running the full report with teachers to verify the script end-to-end:



Summary of what was done:

---

## 1. Analysis: existing content coverage (proper & complete)

**docs/CONTENT_COVERAGE_ANALYSIS.md** records:

- **test_atoms_coverage_100_percent.py** — Correct and complete for the unified catalog: STORY (persona×topic×engine) and non-STORY (persona×topic × HOOK/SCENE/REFLECTION/EXERCISE/INTEGRATION). Uses config; exposes `run_sim_test()` and `run_non_story_sim_test()`.
- **check_teacher_readiness.py** — Correct per teacher (min pool counts). No aggregated “all teachers” report; run_teacher_production_gates loops and fails on first failure.
- **coverage_checker.py** — Correct for plan-time K-table + pool sizes, but only for (persona, topic) pairs that already exist under `atoms/`; it does not require full catalog coverage.
- **fill_non_story_coverage_gaps.py** / **generate_teacher_gap_atoms.py** — Remediation only; they don’t produce a single “what’s missing” report.
- **Gap:** No one place that combines atoms + plan coverage + teacher readiness into a single “content missing?” view.

---

## 2. Existing content checks run

- **Atoms STORY:** 100% (450 tuples).
- **Atoms non-STORY:** 100% (150 pairs × 5 slot types).
- **Plan coverage (coverage_checker):** FAIL — many persona/topic pairs have pool sizes below F006’s 12-chapter requirement (e.g. “required 12 unique atoms, pool has 0/3/4/7”). So “content missing” for assembly is currently from the plan coverage check (pool depth), not from the atoms existence test.
- **Teacher readiness:** Run with full script (with teachers); in this run all teachers passed.

---

## 3. Single content-coverage report

**scripts/ci/content_coverage_report.py**

- Calls the same logic as: atoms (STORY + non-STORY) via `run_sim_test()` / `run_non_story_sim_test()`, plan coverage via `coverage_checker.run_coverage_check()`, and teacher readiness via `check_teacher_readiness` for each teacher in the registry.
- Writes **artifacts/content_coverage_report.json** with: `story_coverage_ok`, `non_story_coverage_ok`, `plan_coverage_ok`, `plan_coverage_errors[]`, `teacher_readiness{ teacher_id: { ok, detail } }`, `teachers_failed`, `summary_ok`.
- Prints a one-page summary to stdout (missing STORY/non-STORY, plan errors, teachers with gaps). Exits 1 if any check fails.

Usage: `python scripts/ci/content_coverage_report.py [--out FILE] [--no-teachers]`.

---

## 4. DOCS_INDEX and inventory

- New section **“How to check for missing book content”** after Atom coverage: describes the single report script, the atoms test, plan coverage_check, teacher readiness, and the new analysis doc.
- **CONTENT_COVERAGE_ANALYSIS.md** and **scripts/ci/content_coverage_report.py** are linked from that section and added to the “Document all — complete inventory” (Docs and Scripts).

---

**Summary:** The existing tooling is analyzed and documented; the atoms test is the authority for “does this combo have a pool?”. Plan coverage (capability_check) is the one that currently reports “missing” content for building books (pool too small for 12 chapters). The new script gives one command and one JSON/summary for “is any book content missing?” and DOCS_INDEX now points to it and to the analysis doc. CI was not changed; you can add a job that runs `content_coverage_report.py` (e.g. nightly or on demand) if you want.

---

**User**

Yes and add restuls to UIl

do: That's the finish line for this piece. The index is honest, the script validates it, and CI enforces it going forward. Nothing left to fix here.
The only remaining work in this area is building the actual backlog files — EI V2 core, the translation pipeline scripts, the localization CI workflows. But those are features, not doc debt. The doc system will automatically flip them from ⚠️ to ✓ the moment someone creates the file, and CI will fail if the index isn't updated to match. The governance loop is closed.

---

**Cursor**


Searching the repo for where governance or report results are shown in the UI so we can add the content-coverage report (and optionally docs governance).



Adding report models, ArtifactReader load methods, and DocsConfigView updates to show governance and content-coverage results.



Checking whether the system governance script accepts arguments:



Adding the new Swift files to the Xcode project.



Summary of what was implemented:

---

## 1. Governance and content results in the UI (PhoenixControl)

**Models**
- **GovernanceReport.swift** — `SystemGovernanceReport`, `GovernanceCheck`, `GovernanceSummary` for `artifacts/governance/system_governance_report.json`.
- **ContentCoverageReport.swift** — `ContentCoverageReport`, `TeacherReadinessDetail` for `artifacts/content_coverage_report.json`.

**ArtifactReader**
- `loadSystemGovernanceReport(repoPath:)` — loads system governance JSON.
- `loadContentCoverageReport(repoPath:)` — loads content coverage JSON.

**Docs & Config tab (DocsConfigView)**
- **Governance & content status** card:
  - **Governance:** From `system_governance_report.json`: overall pass/fail, passed/total, and each check (docs_governance, github_local, production_gates, teacher_gates, etc.) with a pass/fail badge.
  - **Content coverage:** From `content_coverage_report.json`: overall pass/fail, then Atoms STORY, Atoms non-STORY, Plan coverage, Teacher readiness, plus a short note when there are many plan errors or teacher failures.
- **Actions:** “Run check_docs_governance” (with `--check-inventory`), “Run system governance”, “Run content coverage report”. Each run refreshes the card from the updated JSON.
- Reports are loaded on appear, when repo path changes, and when the global refresh trigger fires (e.g. Cmd+R).

**Xcode**
- `GovernanceReport.swift` and `ContentCoverageReport.swift` are in the PhoenixControl target and the Models group.

---

## 2. Finish line (no further doc debt here)

- **Index:** DOCS_INDEX is the source of truth; backlog items are marked ⚠️; we fixed the five incorrect rows.
- **Validation:** `check_docs_governance.py --check-inventory` enforces ✓ = file exists, ⚠️ = file missing.
- **CI:** Docs CI runs that check so the index can’t drift without failing CI.
- **Remaining work** is implementing the backlog (EI V2 core, translation scripts, localization workflows). When those files exist, updating the index to ✓ and adding links will satisfy the script and CI. The governance loop is closed; no extra doc debt in this area.

---

**User**

document everything use @docs/DOCS_INDEX.md 

---

**Cursor**


Checking DOCS_INDEX for missing entries and required updates so everything we added is documented.



Checking where the control plane tabs and artifacts are listed so we can add the Docs tab and content-coverage artifact.



Adding DOCS_INDEX entries for the PhoenixControl Docs tab and the content-coverage artifact.



Checking the video pipeline section and other areas for missing entries:



Adding a task-table row for "Check for missing book content" and updating the "Last updated" line.



Adding the video FLUX script to the pipeline scripts list for completeness.



Adding a note that docs governance is run with `--check-inventory` in CI and in the UI:



Summary of what was added to **DOCS_INDEX.md** using it as the single source:

### 1. **“How to use this index” table**
- New row: **Check for missing book content** → links to [How to check for missing book content](#how-to-check-for-missing-book-content), with a short note on the single report script and the PhoenixControl Docs & Config tab.

### 2. **Control plane & operator UI — full doc bundle**
- New paragraph: **PhoenixControl Docs & Config tab** — Describes that it shows Governance & content status from `system_governance_report.json` and `content_coverage_report.json`, the three run buttons (check_docs_governance with `--check-inventory`, check_system_governance_status, content_coverage_report), and that results refresh after each run, with a link to the “How to check for missing book content” section.

### 3. **How to check for missing book content**
- New **UI** line: PhoenixControl Docs & Config tab shows both reports, run buttons for the three scripts, and live log output; artifacts are linked.

### 4. **Document all — complete inventory (Root & other)**
- New artifact row: **artifacts/content_coverage_report.json** — Content coverage report (from content_coverage_report.py); atoms + plan + teacher readiness — ✓

### 5. **Video pipeline**
- **Pipeline scripts** row: Added an explicit link to `run_flux_generate.py` (FLUX image bank generation) in the list.

### 6. **Governance / Scripts/CI**
- **check_docs_governance.py**: Text updated to mention inventory checking (`--check-inventory`), that CI and the PhoenixControl Docs tab use it, and the “Link integrity & inventory” bullet under Document all — usage.

### 7. **Last updated**
- Set to **2026-03-05** (removed the long parenthetical note).

All of this stays within the index’s existing structure: task table, control-plane bundle, “How to check for missing book content,” complete inventory, video pipeline, and governance/usage. The Docs & Config tab, the content coverage artifact, and the docs governance `--check-inventory` behavior are now documented in DOCS_INDEX.

